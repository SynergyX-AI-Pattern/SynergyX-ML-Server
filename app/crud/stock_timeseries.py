from sqlalchemy.orm import Session
from datetime import datetime, date
from app.models.stock_ohlcv import StockOhlcv

def get_stock_timeseries(
    db: Session,
    stock_id: int,
    start_date: date,
    end_date: date
) -> list[tuple[datetime, float]]:
    """
    주어진 구간의 timestamp와 종가 리스트를
    오름차순으로 반환합니다.
    """
    return (
        db.query(StockOhlcv.timestamp, StockOhlcv.close)
          .filter(StockOhlcv.stock_id == stock_id)
          .filter(StockOhlcv.timestamp >= start_date)
          .filter(StockOhlcv.timestamp <= end_date)
          .order_by(StockOhlcv.timestamp.asc())
          .all()
    )
