from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.schemas.backtest import BacktestRequest, BacktestResponse
from app.schemas.base_response import BaseResponse
from app.core.response import success_response
from app.api_payload.code.status_code import SuccessStatus
from app.db.session import get_db
from app.services.backtest_service import BacktestService

router = APIRouter()

@router.post(
    "",
    response_model=BaseResponse,
    summary="백테스트 실행",
    description=(
        "stock_id, pattern_id, 날짜 범위를 기반으로 백테스트를 실행합니다.<br><br>"
    ),
    tags=["Backtest"]
)
def run_backtest(
    stock_id: int = Query(..., alias="stockId", description="종목 ID"),
    pattern_id: int = Query(..., alias="patternId", description="패턴 ID"),
    request: BacktestRequest = ...,
    db: Session = Depends(get_db)
):
    result: BacktestResponse = BacktestService.execute_backtest(
        stock_id=stock_id,
        pattern_id=pattern_id,
        request=request,
        db=db
    )
    return success_response(
        data=result,
        status=SuccessStatus.BACKTEST_EXECUTED
    )
