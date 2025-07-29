from typing import Dict, Type

from app.models.stock_ohlcv_1h import StockOhlcv1h
from app.models.stock_ohlcv_1d import StockOhlcv1d

UNIT_TO_TABLE: Dict[str, Type] = {
    "HOUR": StockOhlcv1h,
    "DAY": StockOhlcv1d,
}