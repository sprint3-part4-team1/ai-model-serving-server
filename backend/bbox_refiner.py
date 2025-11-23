"""
Bounding Box Refinement Algorithm
자동으로 박스 위치를 보정하여 정확도를 높임
"""

import numpy as np
import cv2
from typing import List, Dict, Tuple
import json
from pathlib import Path


class BBoxRefiner:
    """
    OCR 박스 위치를 정제하는 알고리즘
    """

    def __init__(self, image):
        """
        Args:
            image: OpenCV image (BGR format)
        """
        self.image = image
        self.gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self.height, self.width = image.shape[:2]

    def refine_text_boxes(self, text_boxes: List[Dict], method='edge_based') -> List[Dict]:
        """
        텍스트 박스들을 정제

        Args:
            text_boxes: OCR에서 추출한 텍스트 박스 리스트
            method: 'edge_based', 'contour_based', 'adaptive'

        Returns:
            정제된 텍스트 박스 리스트
        """
        refined_boxes = []

        for box in text_boxes:
            if method == 'edge_based':
                refined = self._refine_edge_based(box)
            elif method == 'contour_based':
                refined = self._refine_contour_based(box)
            elif method == 'adaptive':
                refined = self._refine_adaptive(box)
            else:
                refined = box

            refined_boxes.append(refined)

        return refined_boxes

    def _refine_edge_based(self, box: Dict) -> Dict:
        """
        엣지 검출 기반 박스 정제
        박스 주변의 실제 텍스트 경계를 찾아 조정
        """
        bbox = box['bbox']
        x1, y1, x2, y2 = [int(coord) for coord in bbox]

        # 박스 주변에 여유 공간 추가
        margin = 10
        x1_exp = max(0, x1 - margin)
        y1_exp = max(0, y1 - margin)
        x2_exp = min(self.width, x2 + margin)
        y2_exp = min(self.height, y2 + margin)

        # 해당 영역 추출
        roi = self.gray[y1_exp:y2_exp, x1_exp:x2_exp]

        if roi.size == 0:
            return box

        # Otsu 이진화
        _, binary = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # 모폴로지 연산으로 텍스트 연결
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

        # 수평/수직 투영으로 실제 텍스트 영역 찾기
        h_proj = np.sum(binary, axis=1)
        v_proj = np.sum(binary, axis=0)

        # 임계값 이상인 영역 찾기
        h_thresh = np.max(h_proj) * 0.1
        v_thresh = np.max(v_proj) * 0.1

        h_mask = h_proj > h_thresh
        v_mask = v_proj > v_thresh

        if not np.any(h_mask) or not np.any(v_mask):
            return box

        # 실제 텍스트 영역의 경계 찾기
        h_indices = np.where(h_mask)[0]
        v_indices = np.where(v_mask)[0]

        new_y1 = y1_exp + h_indices[0]
        new_y2 = y1_exp + h_indices[-1]
        new_x1 = x1_exp + v_indices[0]
        new_x2 = x1_exp + v_indices[-1]

        # 업데이트
        refined_box = box.copy()
        refined_box['bbox'] = [new_x1, new_y1, new_x2, new_y2]
        refined_box['bbox_normalized'] = [
            new_x1 / self.width,
            new_y1 / self.height,
            new_x2 / self.width,
            new_y2 / self.height
        ]
        refined_box['refinement_method'] = 'edge_based'

        return refined_box

    def _refine_contour_based(self, box: Dict) -> Dict:
        """
        윤곽선 검출 기반 박스 정제
        """
        bbox = box['bbox']
        x1, y1, x2, y2 = [int(coord) for coord in bbox]

        # 박스 확장
        margin = 15
        x1_exp = max(0, x1 - margin)
        y1_exp = max(0, y1 - margin)
        x2_exp = min(self.width, x2 + margin)
        y2_exp = min(self.height, y2 + margin)

        roi = self.gray[y1_exp:y2_exp, x1_exp:x2_exp]

        if roi.size == 0:
            return box

        # 적응형 이진화
        binary = cv2.adaptiveThreshold(
            roi, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )

        # 윤곽선 찾기
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return box

        # 가장 큰 윤곽선들 결합
        all_points = np.vstack([c.reshape(-1, 2) for c in contours])
        rect = cv2.boundingRect(all_points)

        new_x1 = x1_exp + rect[0]
        new_y1 = y1_exp + rect[1]
        new_x2 = new_x1 + rect[2]
        new_y2 = new_y1 + rect[3]

        refined_box = box.copy()
        refined_box['bbox'] = [new_x1, new_y1, new_x2, new_y2]
        refined_box['bbox_normalized'] = [
            new_x1 / self.width,
            new_y1 / self.height,
            new_x2 / self.width,
            new_y2 / self.height
        ]
        refined_box['refinement_method'] = 'contour_based'

        return refined_box

    def _refine_adaptive(self, box: Dict) -> Dict:
        """
        적응형 박스 정제
        텍스트 크기와 confidence에 따라 다른 전략 사용
        """
        bbox = box['bbox']
        confidence = box.get('confidence', 1.0)

        # 박스 크기 계산
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        area = width * height

        # confidence가 높으면 원본 유지
        if confidence > 0.95:
            return box

        # 작은 텍스트는 edge_based, 큰 텍스트는 contour_based
        if area < 5000:
            return self._refine_edge_based(box)
        else:
            return self._refine_contour_based(box)

    def align_boxes_to_grid(self, text_boxes: List[Dict], tolerance=10) -> List[Dict]:
        """
        박스들을 그리드에 정렬
        같은 행/열에 있는 박스들의 y/x 좌표를 맞춤

        Args:
            text_boxes: 텍스트 박스 리스트
            tolerance: 같은 행/열로 간주할 픽셀 허용 오차

        Returns:
            정렬된 박스 리스트
        """
        if not text_boxes:
            return text_boxes

        # Y 좌표 클러스터링 (같은 행)
        y_coords = [(box['bbox'][1], i) for i, box in enumerate(text_boxes)]
        y_coords.sort()

        y_clusters = []
        current_cluster = [y_coords[0]]

        for i in range(1, len(y_coords)):
            if abs(y_coords[i][0] - current_cluster[-1][0]) <= tolerance:
                current_cluster.append(y_coords[i])
            else:
                y_clusters.append(current_cluster)
                current_cluster = [y_coords[i]]
        y_clusters.append(current_cluster)

        # 각 클러스터의 평균 Y 좌표로 정렬
        aligned_boxes = [box.copy() for box in text_boxes]

        for cluster in y_clusters:
            avg_y = np.mean([y for y, _ in cluster])
            for _, idx in cluster:
                bbox = aligned_boxes[idx]['bbox']
                height = bbox[3] - bbox[1]
                aligned_boxes[idx]['bbox'][1] = int(avg_y)
                aligned_boxes[idx]['bbox'][3] = int(avg_y + height)

                # Normalized 좌표도 업데이트
                aligned_boxes[idx]['bbox_normalized'][1] = avg_y / self.height
                aligned_boxes[idx]['bbox_normalized'][3] = (avg_y + height) / self.height

        # X 좌표 정렬 (같은 열)
        x_coords = [(box['bbox'][0], i) for i, box in enumerate(aligned_boxes)]
        x_coords.sort()

        x_clusters = []
        current_cluster = [x_coords[0]]

        for i in range(1, len(x_coords)):
            if abs(x_coords[i][0] - current_cluster[-1][0]) <= tolerance:
                current_cluster.append(x_coords[i])
            else:
                x_clusters.append(current_cluster)
                current_cluster = [x_coords[i]]
        x_clusters.append(current_cluster)

        for cluster in x_clusters:
            avg_x = np.mean([x for x, _ in cluster])
            for _, idx in cluster:
                bbox = aligned_boxes[idx]['bbox']
                width = bbox[2] - bbox[0]
                aligned_boxes[idx]['bbox'][0] = int(avg_x)
                aligned_boxes[idx]['bbox'][2] = int(avg_x + width)

                aligned_boxes[idx]['bbox_normalized'][0] = avg_x / self.width
                aligned_boxes[idx]['bbox_normalized'][2] = (avg_x + width) / self.width

        return aligned_boxes


def test_refinement():
    """박스 정제 테스트"""
    from paddleocr import PaddleOCR
    import numpy as np

    # OCR 초기화
    ocr = PaddleOCR(
        use_textline_orientation=True,
        lang='en',
        text_det_thresh=0.3,
        text_det_box_thresh=0.5,
        text_det_unclip_ratio=1.6,
        text_det_limit_side_len=1280
    )

    # 이미지 로드
    img_path = Path("목표 이미지.jpg")
    with open(img_path, 'rb') as f:
        file_bytes = np.frombuffer(f.read(), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    # OCR 실행
    result = ocr.predict(image)
    ocr_result = result[0]

    rec_texts = ocr_result.get('rec_texts', [])
    rec_scores = ocr_result.get('rec_scores', [])
    rec_polys = ocr_result.get('rec_polys', [])

    height, width = image.shape[:2]
    text_boxes = []

    for text, score, poly in zip(rec_texts, rec_scores, rec_polys):
        if not text:
            continue

        if hasattr(poly, 'tolist'):
            poly = poly.tolist()

        x_coords = [p[0] for p in poly]
        y_coords = [p[1] for p in poly]
        bbox = [min(x_coords), min(y_coords), max(x_coords), max(y_coords)]

        text_boxes.append({
            "text": text,
            "bbox": bbox,
            "bbox_normalized": [
                bbox[0] / width, bbox[1] / height,
                bbox[2] / width, bbox[3] / height
            ],
            "confidence": float(score),
            "polygon": poly
        })

    print(f"Original boxes: {len(text_boxes)}")

    # 박스 정제
    refiner = BBoxRefiner(image)

    print("\nTesting edge-based refinement...")
    refined_edge = refiner.refine_text_boxes(text_boxes, method='edge_based')

    print("Testing adaptive refinement...")
    refined_adaptive = refiner.refine_text_boxes(text_boxes, method='adaptive')

    print("Testing grid alignment...")
    aligned = refiner.align_boxes_to_grid(refined_adaptive, tolerance=15)

    # 결과 저장
    output_dir = Path("ocr_results")
    with open(output_dir / "refined_boxes.json", 'w', encoding='utf-8') as f:
        json.dump({
            "original": text_boxes[:5],  # 샘플만
            "refined_adaptive": refined_adaptive[:5],
            "aligned": aligned[:5]
        }, f, indent=2, ensure_ascii=False)

    print(f"\n[SUCCESS] Refinement complete!")
    print(f"   Original boxes: {len(text_boxes)}")
    print(f"   Refined boxes: {len(refined_adaptive)}")
    print(f"   Aligned boxes: {len(aligned)}")


if __name__ == "__main__":
    test_refinement()
