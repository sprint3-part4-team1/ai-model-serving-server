"""
메뉴판 템플릿 재활용 완전 파이프라인
기존 메뉴판 구조를 학습하여 새로운 메뉴판 생성

작성자: 당신 팀
목표: 준영님이 시도한 DeepseekOCR 방식을 PaddleOCR로 더 효율적으로 달성
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import json
from paddleocr import PaddleOCR
from typing import List, Dict, Tuple
import copy


class MenuTemplatePipeline:
    """
    기존 메뉴판을 분석하고 새 메뉴 정보로 재생성하는 파이프라인
    """

    def __init__(self):
        """Initialize OCR and processing components"""
        print("Initializing Menu Template Pipeline...")

        # PaddleOCR with optimal settings
        self.ocr = PaddleOCR(
            use_textline_orientation=True,
            lang='en',
            text_det_thresh=0.3,
            text_det_box_thresh=0.5,
            text_det_unclip_ratio=1.6,
            text_det_limit_side_len=1280
        )

        print("Pipeline ready!")

    def analyze_template(self, template_path: str) -> Dict:
        """
        STEP 1: 기존 메뉴판 분석
        - 텍스트 위치, 크기, 스타일 추출
        - 이미지 영역 감지
        - 레이아웃 구조 파악

        Returns:
            template_data: 템플릿 메타데이터
        """
        print(f"\n[STEP 1] Analyzing template: {template_path}")

        # Load image
        with open(template_path, 'rb') as f:
            file_bytes = np.frombuffer(f.read(), dtype=np.uint8)
            image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        height, width = image.shape[:2]

        # Run OCR
        result = self.ocr.predict(image)
        ocr_result = result[0]

        rec_texts = ocr_result.get('rec_texts', [])
        rec_scores = ocr_result.get('rec_scores', [])
        rec_polys = ocr_result.get('rec_polys', [])

        # Extract text boxes with metadata
        text_boxes = []
        for text, score, poly in zip(rec_texts, rec_scores, rec_polys):
            if not text:
                continue

            if hasattr(poly, 'tolist'):
                poly = poly.tolist()

            x_coords = [p[0] for p in poly]
            y_coords = [p[1] for p in poly]
            bbox = [min(x_coords), min(y_coords), max(x_coords), max(y_coords)]

            # Calculate text properties
            box_width = bbox[2] - bbox[0]
            box_height = bbox[3] - bbox[1]

            # Classify text type
            text_type = self._classify_text_type(text, box_width, box_height)

            text_boxes.append({
                "text": text,
                "bbox": bbox,
                "bbox_normalized": [
                    bbox[0] / width, bbox[1] / height,
                    bbox[2] / width, bbox[3] / height
                ],
                "confidence": float(score),
                "polygon": poly,
                "width": box_width,
                "height": box_height,
                "type": text_type  # title, section, menu_name, description, price
            })

        # Detect image regions
        image_regions = self._detect_image_regions(image, text_boxes, width, height)

        # Analyze layout structure
        layout = self._analyze_layout_structure(text_boxes, width, height)

        template_data = {
            "image_size": {"width": width, "height": height},
            "text_boxes": text_boxes,
            "image_regions": image_regions,
            "layout": layout,
            "total_texts": len(text_boxes),
            "total_images": len(image_regions)
        }

        print(f"  Detected {len(text_boxes)} text boxes")
        print(f"  Detected {len(image_regions)} image regions")
        print(f"  Layout: {layout['type']}")

        return template_data, image

    def _classify_text_type(self, text: str, width: float, height: float) -> str:
        """텍스트 유형 분류"""
        text_lower = text.lower().strip()

        # Price pattern
        if '$' in text or '€' in text or '₩' in text:
            return 'price'

        # Section headers
        section_keywords = ['starters', 'main', 'beverages', 'vegan', 'special', 'dessert']
        if any(kw in text_lower for kw in section_keywords):
            return 'section_header'

        # Title (large text)
        if height > 40 or (width > 200 and height > 30):
            return 'title'

        # Long text = description
        if len(text) > 40:
            return 'description'

        # Default = menu name
        return 'menu_name'

    def _detect_image_regions(self, image, text_boxes, width, height):
        """이미지 영역 감지"""
        mask = np.zeros((height, width), dtype=np.uint8)

        for text_box in text_boxes:
            polygon = text_box["polygon"]
            pts = np.array(polygon, dtype=np.int32)
            cv2.fillPoly(mask, [pts], 255)

        non_text_mask = cv2.bitwise_not(mask)
        contours, _ = cv2.findContours(non_text_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        image_regions = []
        min_region_area = (width * height) * 0.02

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > min_region_area:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0

                if 0.5 < aspect_ratio < 2.5:
                    image_regions.append({
                        "type": "image_placeholder",
                        "bbox": [x, y, x + w, y + h],
                        "bbox_normalized": [
                            x / width, y / height,
                            (x + w) / width, (y + h) / height
                        ],
                        "area": area
                    })

        return image_regions

    def _analyze_layout_structure(self, text_boxes, width, height):
        """레이아웃 구조 분석"""
        if not text_boxes:
            return {"type": "empty", "columns": 0}

        x_centers = [(box["bbox"][0] + box["bbox"][2]) / 2 for box in text_boxes]
        x_centers_sorted = sorted(x_centers)

        # Column detection
        gaps = []
        for i in range(len(x_centers_sorted) - 1):
            gap = x_centers_sorted[i + 1] - x_centers_sorted[i]
            if gap > width * 0.15:
                gaps.append(gap)

        num_columns = len(gaps) + 1 if gaps else 1

        return {
            "type": "multi_column" if num_columns > 1 else "single_column",
            "columns": num_columns,
            "column_gaps": gaps
        }

    def create_editable_template(self, template_data: Dict, output_path: str):
        """
        STEP 2: 편집 가능한 템플릿 생성
        텍스트 영역을 비우고 위치 정보를 JSON으로 저장
        """
        print(f"\n[STEP 2] Creating editable template...")

        # TODO: Implement inpainting to remove text
        # For now, save template structure
        template_structure = {
            "layout": template_data["layout"],
            "image_size": template_data["image_size"],
            "editable_fields": []
        }

        for box in template_data["text_boxes"]:
            if box["type"] in ["menu_name", "description", "price"]:
                template_structure["editable_fields"].append({
                    "type": box["type"],
                    "bbox": box["bbox"],
                    "bbox_normalized": box["bbox_normalized"],
                    "original_text": box["text"],
                    "width": box["width"],
                    "height": box["height"]
                })

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(template_structure, f, indent=2, ensure_ascii=False)

        print(f"  Saved {len(template_structure['editable_fields'])} editable fields")
        return template_structure

    def generate_menu_from_template(
        self,
        template_image,
        template_data: Dict,
        new_menu_data: Dict,
        output_path: str
    ):
        """
        STEP 3: 새 메뉴 정보로 메뉴판 생성

        Args:
            template_image: 원본 템플릿 이미지
            template_data: 템플릿 메타데이터
            new_menu_data: 새로운 메뉴 정보
                {
                    "starters": [{"name": "...", "description": "...", "price": "..."}],
                    "main": [...],
                    ...
                }
            output_path: 출력 경로
        """
        print(f"\n[STEP 3] Generating new menu from template...")

        # Convert to PIL for text rendering
        image_rgb = cv2.cvtColor(template_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        draw = ImageDraw.Draw(pil_image)

        # TODO: Load appropriate fonts
        try:
            font_name = ImageFont.truetype("arial.ttf", 20)
            font_desc = ImageFont.truetype("arial.ttf", 14)
            font_price = ImageFont.truetype("arialbd.ttf", 18)
        except:
            font_name = ImageFont.load_default()
            font_desc = ImageFont.load_default()
            font_price = ImageFont.load_default()

        # Group text boxes by section
        sections = self._group_by_sections(template_data["text_boxes"])

        # Replace text for each section
        for section_name, new_items in new_menu_data.items():
            if section_name in sections:
                section_boxes = sections[section_name]
                # TODO: Match and replace text

        # Save result
        pil_image.save(output_path)
        print(f"  Saved new menu: {output_path}")

        return pil_image

    def _group_by_sections(self, text_boxes):
        """텍스트 박스를 섹션별로 그룹화"""
        sections = {}
        current_section = None

        for box in sorted(text_boxes, key=lambda b: b["bbox"][1]):  # Sort by Y
            if box["type"] == "section_header":
                current_section = box["text"].lower()
                sections[current_section] = []
            elif current_section and box["type"] in ["menu_name", "description", "price"]:
                sections[current_section].append(box)

        return sections


def main():
    """파이프라인 테스트"""
    pipeline = MenuTemplatePipeline()

    # Test template analysis
    template_path = "목표 이미지.jpg"
    template_data, template_image = pipeline.analyze_template(template_path)

    # Save analysis
    output_dir = Path("pipeline_output")
    output_dir.mkdir(exist_ok=True)

    with open(output_dir / "template_analysis.json", 'w', encoding='utf-8') as f:
        # Remove image from JSON (not serializable)
        data_to_save = copy.deepcopy(template_data)
        json.dump(data_to_save, f, indent=2, ensure_ascii=False)

    print(f"\n[SUCCESS] Analysis saved to pipeline_output/")

    # Create editable template
    template_structure = pipeline.create_editable_template(
        template_data,
        str(output_dir / "editable_template.json")
    )

    # Test with sample menu data
    new_menu_data = {
        "starters": [
            {"name": "Caesar Salad", "description": "Fresh romaine, parmesan, croutons", "price": "$12.00"},
            {"name": "Soup of the Day", "description": "Chef's special creation", "price": "$8.00"}
        ],
        "main": [
            {"name": "Grilled Salmon", "description": "With seasonal vegetables", "price": "$24.00"}
        ]
    }

    # Generate new menu
    # pipeline.generate_menu_from_template(
    #     template_image,
    #     template_data,
    #     new_menu_data,
    #     str(output_dir / "new_menu.jpg")
    # )

    print("\n" + "="*60)
    print("PIPELINE SUMMARY")
    print("="*60)
    print(f"Template analyzed: {template_path}")
    print(f"Total text elements: {template_data['total_texts']}")
    print(f"Editable fields: {len(template_structure['editable_fields'])}")
    print(f"Layout: {template_data['layout']['columns']} columns")
    print("="*60)


if __name__ == "__main__":
    main()
