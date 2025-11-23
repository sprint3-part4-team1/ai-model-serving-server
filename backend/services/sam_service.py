"""
SAM (Segment Anything Model) 서비스
정밀한 객체 세그멘테이션 제공
"""
import torch
import numpy as np
from PIL import Image
from typing import Optional, Tuple, List
from loguru import logger
import cv2

try:
    from segment_anything import sam_model_registry, SamPredictor
    SAM_AVAILABLE = True
except ImportError:
    SAM_AVAILABLE = False
    logger.warning("SAM not installed. Install with: pip install segment-anything")


class SAMSegmenter:
    """SAM 기반 객체 세그멘테이션"""

    def __init__(self, model_type: str = "vit_h", checkpoint_path: Optional[str] = None):
        """
        Args:
            model_type: 'vit_h', 'vit_l', 'vit_b'
            checkpoint_path: SAM 체크포인트 경로 (sam_vit_h_4b8939.pth)
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_type = model_type
        self.checkpoint_path = checkpoint_path or "sam_vit_h_4b8939.pth"
        self.predictor = None

        if SAM_AVAILABLE:
            logger.info(f"SAM Segmenter initialized (model: {model_type}, device: {self.device})")
        else:
            logger.error("SAM not available!")

    def _load_model(self):
        """SAM 모델 로딩 (Lazy Loading)"""
        if self.predictor is not None:
            return

        if not SAM_AVAILABLE:
            raise RuntimeError("SAM is not installed")

        try:
            logger.info(f"Loading SAM model from {self.checkpoint_path}...")
            sam = sam_model_registry[self.model_type](checkpoint=self.checkpoint_path)
            sam.to(device=self.device)
            self.predictor = SamPredictor(sam)
            logger.info("SAM model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load SAM model: {e}")
            raise

    def segment_object(
        self,
        image: Image.Image,
        point_coords: Optional[List[Tuple[int, int]]] = None,
        point_labels: Optional[List[int]] = None,
        box: Optional[Tuple[int, int, int, int]] = None,
        multimask: bool = False
    ) -> Tuple[np.ndarray, Image.Image]:
        """
        객체 세그멘테이션

        Args:
            image: 입력 이미지
            point_coords: 클릭 좌표 [(x1, y1), (x2, y2), ...]
            point_labels: 점 레이블 [1, 1, 0, ...] (1=foreground, 0=background)
            box: 바운딩 박스 (x1, y1, x2, y2)
            multimask: 여러 마스크 생성 여부

        Returns:
            (mask, mask_image): 마스크 배열, 마스크 이미지
        """
        self._load_model()

        # PIL → numpy
        image_np = np.array(image.convert("RGB"))

        # SAM 이미지 설정
        self.predictor.set_image(image_np)

        # 프롬프트 준비
        point_coords_np = np.array(point_coords) if point_coords else None
        point_labels_np = np.array(point_labels) if point_labels else None
        box_np = np.array(box) if box else None

        # 세그멘테이션 실행
        masks, scores, logits = self.predictor.predict(
            point_coords=point_coords_np,
            point_labels=point_labels_np,
            box=box_np,
            multimask_output=multimask,
        )

        # 최고 점수 마스크 선택
        if len(masks.shape) == 3:
            best_idx = np.argmax(scores)
            mask = masks[best_idx]
        else:
            mask = masks

        # 마스크를 PIL Image로 변환
        mask_image = Image.fromarray((mask * 255).astype(np.uint8))

        logger.info(f"Segmentation completed (score: {scores.max():.3f})")
        return mask, mask_image

    def auto_segment(self, image: Image.Image) -> Tuple[np.ndarray, Image.Image]:
        """
        자동 객체 감지 및 세그멘테이션 (중앙 객체 선택)

        Args:
            image: 입력 이미지

        Returns:
            (mask, mask_image): 마스크 배열, 마스크 이미지
        """
        # 이미지 중앙을 foreground로 가정
        w, h = image.size
        center_point = [(w // 2, h // 2)]
        center_label = [1]

        logger.info(f"Auto-segmenting with center point: {center_point}")
        return self.segment_object(
            image=image,
            point_coords=center_point,
            point_labels=center_label,
            multimask=True
        )

    def create_inverse_mask(self, mask: np.ndarray) -> np.ndarray:
        """
        역마스크 생성 (배경 영역)

        Args:
            mask: 원본 마스크 (객체 영역 = 1)

        Returns:
            역마스크 (배경 영역 = 1)
        """
        return ~mask


# 싱글톤 인스턴스
_sam_instance = None


def get_sam_segmenter(checkpoint_path: Optional[str] = None) -> SAMSegmenter:
    """SAM Segmenter 싱글톤 반환"""
    global _sam_instance
    if _sam_instance is None:
        _sam_instance = SAMSegmenter(checkpoint_path=checkpoint_path)
    return _sam_instance
