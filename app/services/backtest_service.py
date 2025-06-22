import logging
from datetime import date
from sqlalchemy.orm import Session
from app.crud import stock, pattern
from app.schemas.backtest import BacktestRequest, BacktestResponse
from app.exceptions.base import APIException
from app.api_payload.code.status_code import ErrorStatus

logger = logging.getLogger(__name__)

class BacktestService:
    """
    백테스트 관련 비즈니스 로직을 처리합니다.
    """

    @staticmethod
    def execute_backtest(
        stock_id: int,
        pattern_id: int,
        request: BacktestRequest,
        db: Session
    ) -> BacktestResponse:
        """
        주어진 조건으로 백테스트를 실행합니다.

        Args:
            stock_id (int): 종목 ID
            pattern_id (int): 패턴 ID
            request (BacktestRequest): 시작일, 종료일
            db (Session): SQLAlchemy 세션

        Returns:
            BacktestResponse: 백테스트 결과 응답

        Raises:
            APIException: 유효하지 않은 종목/패턴 ID
        """
        logger.debug(f"[Service] 백테스팅 시작 - stock_id: {stock_id}, pattern_id: {pattern_id}, 기간: {request.startDate} ~ {request.endDate}")

        # TODO: 추후 실제 로직/DB 연동 구현
        try:
            stock_obj = stock.get_stock_by_id(db, stock_id)
            if not stock_obj:
                logger.warning(f"[Service] 존재하지 않는 종목 ID: {stock_id}")
                raise APIException(ErrorStatus.STOCK_NOT_FOUND)

            pattern_obj = pattern.get_pattern_by_id(db, pattern_id)
            if not pattern_obj:
                logger.warning(f"[Service] 존재하지 않는 패턴 ID: {pattern_id}")
                raise APIException(ErrorStatus.PATTERN_NOT_FOUND)

            # TODO: 추후 실제 DTW 계산 로직 삽입
            response = BacktestResponse(
                matchedCount=12,
                winRate=58.3,
                averageReturn=7.4,
                maxReturn=19.8,
                maxReturnDate=date(2024, 4, 15),
                minReturn=-6.2,
                minReturnDate=date(2024, 2, 5),
                totalReturn=88.1,
                lastMatchedDate=date(2024, 5, 30),
                lastMatchedReturn=5.6
            )

            logger.debug(f"[Service] 백테스팅 완료 - stock_id: {stock_id}, pattern_id: {pattern_id}")
            return response

        except Exception as e:
            logger.error(f"[Service] 백테스팅 실패 - {e}")
            raise APIException(ErrorStatus.BACKTEST_FAILED)

