from sqlalchemy.orm import Session
from app.models.stock import Stock


def get_stock_by_id(db: Session, stock_id: int) -> Stock | None:
    """
    stock_id 기준으로 종목 정보를 조회합니다.
    """
    return db.query(Stock).filter(Stock.id == stock_id).first()
