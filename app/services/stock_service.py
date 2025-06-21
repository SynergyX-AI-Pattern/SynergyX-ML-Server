import logging
from sqlalchemy.orm import Session
from app.crud.stock import get_stock_by_id
from app.schemas.stock import StockResponse
from app.exceptions.base import APIException
from app.api_payload.code.status_code import ErrorStatus

logger = logging.getLogger(__name__)


class StockService:
    """
    종목 관련 비즈니스 로직을 처리합니다.
    """

    @staticmethod
    def get_stock_detail(stock_id: int, db: Session) -> StockResponse:
        """
        종목 ID로 단건 조회합니다.

        Args:
            stock_id (int): 조회할 종목 ID
            db (Session): SQLAlchemy 세션

        Returns:
            StockResponse: 조회된 종목 데이터

        Raises:
            APIException: 종목이 존재하지 않을 경우
        """
        logger.debug(f"[Service] 종목 조회 시작 - stock_id: {stock_id}")
        stock = get_stock_by_id(db, stock_id)

        if not stock:
            logger.warning(f"[Service] 존재하지 않는 종목 ID: {stock_id}")
            raise APIException(ErrorStatus.STOCK_NOT_FOUND)

        logger.debug(f"[Service] 종목 조회 성공 - stock_id: {stock_id}")
        return StockResponse.from_orm(stock)
