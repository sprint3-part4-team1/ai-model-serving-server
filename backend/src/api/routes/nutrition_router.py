# api/routes/nutrition_router.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import logging

from ...database import get_session
from ...models import Store, MenuItem, NutritionEstimate

from ...nutrition.nutrition_analyzer import NutritionAnalyzer

router = APIRouter() 
logger = logging.getLogger(__name__)

# ===== Response Models =====
class AnalyzeResponse(BaseModel):
    success: bool
    store_id: int
    message: str
    total_items: Optional[int] = None

class AnalyzeStatusResponse(BaseModel):
    status: str  # "processing", "completed", "failed"
    progress: Optional[float] = None  # 0.0 ~ 1.0
    message: Optional[str] = None

# ===== 동기 버전 (간단) =====
@router.post("/analyze/{store_id}", response_model=AnalyzeResponse)
def analyze_nutrition_sync(store_id: int, batch_size: int = 10):
    """
    매장 메뉴 영양 분석 (동기)
    
    - **store_id**: 매장 ID
    - **batch_size**: 배치 크기 (기본 10개)
    
    ⚠️ 주의: 메뉴가 많으면 시간이 오래 걸릴 수 있습니다 (10초+)
    """
    try:
        logger.info(f"매장 {store_id} 영양 분석 시작 (동기)")

        analyzer = NutritionAnalyzer(batch_size=batch_size)
        analyzer.analyze_store(store_id)

        logger.info(f"매장 {store_id} 영양 분석 완료")

        return AnalyzeResponse(
            success=True,
            store_id=store_id,
            message="영양 분석이 완료되었습니다."
        )
    
    except Exception as e:
        logger.error(f"매장 {store_id} 영양 분석 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"영양 분석 중 오류가 발생했습니다: {str(e)}"
        )

# ===== 비동기 버전 (권장) =====
def _analyze_background(store_id: int, batch_size: int):
    """백그라운드 작업으로 분석 실행"""
    try:
        logger.info(f"매장 {store_id} 백그라운드 분석 시작")

        analyzer = NutritionAnalyzer(batch_size=batch_size)
        analyzer.analyze_store(store_id)
        
        logger.info(f"매장 {store_id} 백그라운드 분석 완료")
        
        # TODO: 완료 상태를 Redis/DB에 저장 (선택사항)
        
    except Exception as e:
        logger.error(f"매장 {store_id} 백그라운드 분석 실패: {e}")
        # TODO: 실패 상태를 Redis/DB에 저장 (선택사항)


# ⭐ 권장
@router.post("/analyze/{store_id}/async", response_model=AnalyzeResponse)
def analyze_nutrition_async(
    store_id: int, 
    background_tasks: BackgroundTasks,
    batch_size: int = 10
):
    """
    매장 메뉴 영양 분석 (비동기)
    
    - **store_id**: 매장 ID
    - **batch_size**: 배치 크기 (기본 10개)
    
    💡 분석이 백그라운드에서 실행됩니다. 즉시 응답을 받습니다.
    """
    try:
        # 매장 존재 여부 체크 (빠른 검증)
        
        session = get_session()
        store = session.query(Store).filter_by(id=store_id).first()
        session.close()

        if not store:
            raise HTTPException(
                status_code=404,
                detail=f"매장 {store_id}을(를) 찾을 수 없습니다."
            )
        
        # 백그라운드 작업 추가
        background_tasks.add_task(_analyze_background, store_id, batch_size)

        logger.info(f"매장 {store_id} 백그라운드 분석 요청 완료")
        
        return AnalyzeResponse(
            success=True,
            store_id=store_id,
            message="영양 분석이 백그라운드에서 진행 중입니다."
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"매장 {store_id} 분석 요청 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"분석 요청 중 오류가 발생했습니다: {str(e)}"
        )

# ===== 상태 조회 (선택사항) =====
@router.get("/analyze/{store_id}/status", response_model=AnalyzeStatusResponse)
def get_analyze_status(store_id: int):
    """
    영양 분석 상태 조회
    
    - **store_id**: 매장 ID
    
    ⚠️ 주의: Redis/DB에 상태 저장 기능이 구현되어야 합니다.
    """
    # TODO: Redis/DB에서 상태 조회
    # 예시:
    # status = redis.get(f"nutrition_analysis:{store_id}")
    
    return AnalyzeStatusResponse(
        status="not_implemented",
        message="상태 조회 기능은 아직 구현되지 않았습니다."
    )

# ===== 재분석 (특정 confidence 이하만) =====
@router.post("/reanalyze/{store_id}", response_model=AnalyzeResponse)
def reanalyze_low_confidence(
    store_id: int,
    min_confidence: float = 0.7,
    batch_size: int = 10
):
    """
    낮은 신뢰도 메뉴만 재분석
    
    - **store_id**: 매장 ID
    - **min_confidence**: 최소 신뢰도 (기본 0.7)
    - **batch_size**: 배치 크기 (기본 10개)
    
    💡 신뢰도가 min_confidence 미만인 메뉴만 재분석합니다.
    """
    try:
        session = get_session()
        
        # 낮은 신뢰도 메뉴 찾기
        low_confidence_items = (
            session.query(MenuItem)
            .join(NutritionEstimate)
            .filter(
                MenuItem.menu.has(store_id=store_id),
                NutritionEstimate.confidence < min_confidence
            )
            .all()
        )
        
        session.close()
        
        if not low_confidence_items:
            return AnalyzeResponse(
                success=True,
                store_id=store_id,
                message=f"신뢰도 {min_confidence} 미만인 메뉴가 없습니다.",
                total_items=0
            )
        
        logger.info(f"매장 {store_id} 재분석 시작: {len(low_confidence_items)}개 메뉴")
        
        # TODO: 낮은 신뢰도 메뉴만 재분석하는 로직 추가
        # (현재는 전체 재분석)
        analyzer = NutritionAnalyzer(batch_size=batch_size)
        analyzer.analyze_store(store_id)
        
        return AnalyzeResponse(
            success=True,
            store_id=store_id,
            message=f"{len(low_confidence_items)}개 메뉴를 재분석했습니다.",
            total_items=len(low_confidence_items)
        )
    
    except Exception as e:
        logger.error(f"매장 {store_id} 재분석 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"재분석 중 오류가 발생했습니다: {str(e)}"
        )