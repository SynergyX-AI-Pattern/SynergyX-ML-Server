from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from app.schemas.base_response import BaseResponse
from app.api_payload.code.status_code import SuccessStatus
from app.core.response import success_response
from app.db.session import get_db
from app.services.stock_service import StockService

router = APIRouter()


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
    [API] 종목 ID 기반 단건 조회

    - Service 계층에서 비즈니스 로직 처리
    - 표준 응답 포맷(BaseResponse)으로 래핑
    """
    result = StockService.get_stock_detail(stock_id, db)

    return success_response(
        data=result,
        status=SuccessStatus.STOCK_FOUND
    )
