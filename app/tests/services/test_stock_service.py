import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
dotenv_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path)

# print(".env 위치:", dotenv_path)
# print("DATABASE_URL 값:", os.getenv("DATABASE_URL"))

from app.services.stock_service import StockService
from app.db.session import SessionLocal
from app.exceptions.base import APIException
from app.api_payload.code.status_code import ErrorStatus


def test_get_stock_detail_success_real_db():
    """
    [성공] ID=1 종목이 존재할 경우 정상 조회되어야 함.
    """
    db = SessionLocal()
    result = StockService.get_stock_detail(stock_id=1, db=db)

    assert result.name == "삼성전자"
    assert result.symbol == "005930"


def test_get_stock_detail_not_found_real_db():
    """
    [실패] 존재하지 않는 종목 ID 조회 시 APIException 발생해야 함.
    """
    db = SessionLocal()

    try:
        StockService.get_stock_detail(stock_id=999999, db=db)
        assert False, "예외가 발생하지 않았습니다"
    except APIException as e:
        assert e.status == ErrorStatus.STOCK_NOT_FOUND
