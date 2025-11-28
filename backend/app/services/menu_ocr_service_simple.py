"""
메뉴판 OCR 서비스 (Simplified version)

실제 DeepSeek OCR 모델 통합은 환경 설정 후 진행
현재는 PaddleOCR과 기본 이미지 처리로 구현
"""
import os
import time
import uuid
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, List, Tuple
import json

from app.core.logging import app_logger as logger
from app.core.config import settings
from app.schemas.menu_ocr import (
    MenuOCRRequest,
    MenuOCRResponse,
    MenuRepaintRequest,
    MenuRepaintResponse,
    BoundingBox,
)

# PaddleOCR import (선택적)
try:
    from paddleocr import PaddleOCR
    PADDLE_OCR_AVAILABLE = True
    logger.info("PaddleOCR is available")
except ImportError:
    PADDLE_OCR_AVAILABLE = False
    logger.warning("PaddleOCR not available - using mock OCR")


class MenuOCRService:
    """메뉴판 OCR 서비스"""

    def __init__(self):
        self.ocr_results_dir = Path(settings.STATIC_DIR) / "ocr_results"
        self.ocr_results_dir.mkdir(parents=True, exist_ok=True)

        # PaddleOCR 초기화
        if PADDLE_OCR_AVAILABLE:
            try:
                self.paddle_ocr = PaddleOCR(use_angle_cls=True, lang='korean')
                logger.info("PaddleOCR initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize PaddleOCR: {e}")
                self.paddle_ocr = None
        else:
            self.paddle_ocr = None

    async def process_menu_ocr(
        self,
        image_path: str,
        request: MenuOCRRequest
    ) -> MenuOCRResponse:
        """
        메뉴판 이미지 OCR 처리

        Args:
            image_path: 입력 이미지 경로
            request: OCR 요청 정보

        Returns:
            MenuOCRResponse: OCR 결과
        """
        start_time = time.time()
        ocr_id = str(uuid.uuid4())[:8]

        try:
            logger.info(f"메뉴판 OCR 시작 - ID: {ocr_id}")

            # 결과 저장 디렉토리 생성
            result_dir = self.ocr_results_dir / ocr_id
            result_dir.mkdir(parents=True, exist_ok=True)
            (result_dir / "images").mkdir(exist_ok=True)

            # 이미지 로드
            image = Image.open(image_path).convert('RGB')

            # OCR 실행
            if self.paddle_ocr:
                ocr_results = self.paddle_ocr.ocr(image_path, cls=True)
                schema_content, bboxes = self._parse_paddle_results(ocr_results, image)
            else:
                # Mock OCR 결과
                schema_content, bboxes = self._generate_mock_ocr_result(image)

            # 바운딩 박스 그리기
            result_image_path = result_dir / "result_with_boxes.jpg"
            self._draw_bounding_boxes(image, bboxes, str(result_image_path))

            # 스키마 저장
            schema_path = result_dir / "schema.mmd"
            with open(schema_path, 'w', encoding='utf-8') as f:
                f.write(schema_content)

            # 메타데이터 저장
            metadata = {
                "ocr_id": ocr_id,
                "original_image": image_path,
                "schema_path": str(schema_path),
                "result_image_path": str(result_image_path),
                "created_at": time.time()
            }
            metadata_path = result_dir / "metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)

            processing_time = time.time() - start_time

            # 응답 생성
            response = MenuOCRResponse(
                ocr_id=ocr_id,
                schema_content=schema_content,
                result_image_url=f"/static/ocr_results/{ocr_id}/result_with_boxes.jpg",
                extracted_images=[],
                bounding_boxes=bboxes,
                processing_time=processing_time
            )

            logger.info(f"메뉴판 OCR 완료 - ID: {ocr_id}, 처리 시간: {processing_time:.2f}초")

            return response

        except Exception as e:
            logger.exception(f"메뉴판 OCR 실패: {str(e)}")
            raise

    async def process_menu_repaint(
        self,
        request: MenuRepaintRequest
    ) -> MenuRepaintResponse:
        """
        메뉴판 재생성

        Args:
            request: Repaint 요청 정보

        Returns:
            MenuRepaintResponse: Repaint 결과
        """
        start_time = time.time()
        repaint_id = str(uuid.uuid4())[:8]

        try:
            logger.info(f"메뉴판 Repaint 시작 - OCR ID: {request.ocr_id}")

            # OCR 결과 로드
            ocr_dir = self.ocr_results_dir / request.ocr_id
            if not ocr_dir.exists():
                raise ValueError(f"OCR 결과를 찾을 수 없습니다: {request.ocr_id}")

            # 메타데이터 로드
            metadata_path = ocr_dir / "metadata.json"
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            # 원본 이미지 로드
            original_image = Image.open(metadata["original_image"]).convert('RGB')

            # 스키마 사용 (수정된 것 또는 원본)
            if request.schema_content:
                schema_content = request.schema_content
            else:
                schema_path = Path(metadata["schema_path"])
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema_content = f.read()

            # Repaint 결과 디렉토리
            repaint_dir = self.ocr_results_dir / f"{request.ocr_id}_repaint_{repaint_id}"
            repaint_dir.mkdir(parents=True, exist_ok=True)

            # 스키마 파싱 및 이미지 재생성
            # TODO: 실제 Repaint 로직 구현
            # 현재는 원본 이미지를 복사
            result_image_path = repaint_dir / "result_repaint.jpg"
            original_image.save(result_image_path)

            processing_time = time.time() - start_time

            response = MenuRepaintResponse(
                repaint_id=repaint_id,
                result_image_url=f"/static/ocr_results/{request.ocr_id}_repaint_{repaint_id}/result_repaint.jpg",
                processing_time=processing_time
            )

            logger.info(f"메뉴판 Repaint 완료 - ID: {repaint_id}, 처리 시간: {processing_time:.2f}초")

            return response

        except Exception as e:
            logger.exception(f"메뉴판 Repaint 실패: {str(e)}")
            raise

    def _parse_paddle_results(self, ocr_results: List, image: Image.Image) -> Tuple[str, List[BoundingBox]]:
        """PaddleOCR 결과 파싱"""
        schema_lines = ["# 메뉴판 OCR 결과\n"]
        bboxes = []

        if not ocr_results or not ocr_results[0]:
            return "# 메뉴판\n(텍스트 없음)", []

        for line in ocr_results[0]:
            if not line:
                continue

            box = line[0]  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            text_info = line[1]  # (text, confidence)
            text = text_info[0]
            confidence = text_info[1]

            # 바운딩 박스 정보
            x_coords = [p[0] for p in box]
            y_coords = [p[1] for p in box]
            x = min(x_coords)
            y = min(y_coords)
            width = max(x_coords) - x
            height = max(y_coords) - y

            bboxes.append(BoundingBox(
                x=float(x),
                y=float(y),
                width=float(width),
                height=float(height),
                text=text
            ))

            schema_lines.append(f"- {text} (신뢰도: {confidence:.2f})\n")

        return "".join(schema_lines), bboxes

    def _generate_mock_ocr_result(self, image: Image.Image) -> Tuple[str, List[BoundingBox]]:
        """Mock OCR 결과 생성"""
        width, height = image.size

        # 샘플 메뉴 데이터
        mock_schema = """# 카페 메뉴

## 커피
- 아메리카노: 4,500원
- 카페라떼: 5,000원
- 바닐라라떼: 5,500원

## 디저트
- 초콜릿 케이크: 6,500원
- 치즈케이크: 6,000원
- 티라미수: 6,500원
"""

        # Mock 바운딩 박스
        mock_bboxes = [
            BoundingBox(x=width*0.1, y=height*0.1, width=width*0.3, height=height*0.05, text="카페 메뉴"),
            BoundingBox(x=width*0.1, y=height*0.2, width=width*0.2, height=height*0.04, text="커피"),
            BoundingBox(x=width*0.1, y=height*0.25, width=width*0.4, height=height*0.03, text="아메리카노: 4,500원"),
        ]

        return mock_schema, mock_bboxes

    def _draw_bounding_boxes(
        self,
        image: Image.Image,
        bboxes: List[BoundingBox],
        output_path: str
    ):
        """바운딩 박스 그리기"""
        draw_image = image.copy()
        draw = ImageDraw.Draw(draw_image)

        for bbox in bboxes:
            # 박스 그리기
            box = [
                bbox.x, bbox.y,
                bbox.x + bbox.width, bbox.y + bbox.height
            ]
            draw.rectangle(box, outline="red", width=2)

            # 텍스트 (선택적)
            # draw.text((bbox.x, bbox.y - 15), bbox.text[:20], fill="red")

        draw_image.save(output_path)


# 전역 서비스 인스턴스
menu_ocr_service = MenuOCRService()
