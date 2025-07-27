import logging
from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from app.schemas.base_response import BaseResponse
from app.api_payload.code.status_code import SuccessStatus
from app.core.response import success_response
from app.db.session import get_db
from app.services.stock_service import StockService
from app.services.prediction_service import PredictionService
from app.services.batch_service import BatchService
from app.schemas.stock import StockPredictionResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/predict/batch",
    response_model=BaseResponse,
    summary="전체 종목 예측 및 DB 저장",
    description="""
    스케줄러 테스트 용 -> 개별 실행 X\n
    stock_id 범위(1~100)에 대해
    GRU 모델 학습 및 15일 주가 예측을 수행하고,  
    그 결과를 prediction 테이블에 저장합니다.
    """,
    tags=["Stock"]
)
def batch_predict():
    """
    종목 일괄 예측 및 DB 저장 API (테스트/내부용)

    - stock_id 1~100에 대해 루프 실행
    - 각 종목의 심볼(symbol)을 조회하여 yfinance로 5년치 종가 수집
    - GRU 모델 기반으로 15일 예측 수행
    - prediction 테이블에 결과 저장
    """
    BatchService.batch_predict_and_save(start_id=1, end_id=100, max_workers=2)

    return success_response(
        data=None,
        status=SuccessStatus.STOCK_PREDICTED,
    )


@router.get(
    "/predict/{symbol}",
    response_model=BaseResponse,
    summary="15일 주가 예측 (테스트용)",
    description="""
    입력된 종목코드(symbol)에 대해 GRU 모델을 기반으로 
    향후 15일간의 주가를 예측합니다. 
    """,
    tags=["Stock"]
)
def predict_stock(
        symbol: str = Path(..., min_length=6, max_length=6, description="종목코드 (6자리, KOSPI 기준)"),
        db: Session = Depends(get_db)
):
    """
    단일 종목 15일 예측 + db 저장

    - yfinance 기반으로 종가 5년치 수집 후 전처리
    - GRU 모델 학습 및 예측
    - 예측 결과를 BaseResponse 포맷으로 반환
    """
    logger.debug(f"[Predict] /predict called with symbol={symbol}")

    # 예측 수행
    predictions = PredictionService.predict_and_save(symbol, db)

    logger.debug(f"[Predict] /predict result top-3: {predictions[:3]}")

    return success_response(
        data=StockPredictionResponse(symbol=symbol, predictions=predictions),
        status=SuccessStatus.STOCK_PREDICTED
    )


@router.get(
    "/{stock_id}",
    response_model=BaseResponse,
    summary="종목 Id로 정보 조회",
    description="stock Id로 종목 정보를 단건 조회합니다.",
    tags=["Stock"]
)
def get_stock(
        stock_id: int = Path(..., description="조회할 종목의 고유 ID"),
        db: Session = Depends(get_db)
):
    """
    종목 ID 기반 단건 조회

    - Service 계층에서 비즈니스 로직 처리
    - 표준 응답 포맷(BaseResponse)으로 래핑
    """
    result = StockService.get_stock_detail(stock_id, db)

    return success_response(
        data=result,
        status=SuccessStatus.STOCK_FOUND
    )
