from sqlalchemy.orm import Session
from datetime import datetime
from app.utils.unit_table_mapper import UNIT_TO_TABLE

def get_stock_timeseries_by_unit(
    db: Session,
    stock_id: int,
    start_datetime: datetime,
    end_datetime: datetime,
    unit: str
) -> list[tuple[datetime, float]]:
    """
    단위에 따라 테이블에서 (timestamp, close) 조회
    """
    model = UNIT_TO_TABLE.get(unit.upper())

    return (
        db.query(model.timestamp, model.close)
          .filter(model.stock_id == stock_id)
          .filter(model.timestamp >= start_datetime)
          .filter(model.timestamp <= end_datetime)
          .order_by(model.timestamp.asc())
          .all()
    )
