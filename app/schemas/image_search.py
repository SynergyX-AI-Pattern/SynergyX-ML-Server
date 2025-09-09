from enum import Enum

from pydantic import BaseModel
from typing import Optional

class StockStatus(str, Enum):
    LISTED = "LISTED" # KOSPI100 종목
    LISTED_OUTSIDE = "LISTED_OUTSIDE" # db에 없는 상장 기업
    UNLISTED = "UNLISTED" # 비상장 브랜드/기업
    UNKNOWN = "UNKNOWN" # 판단 불가

class ImageSearchResponse(BaseModel):
    id: Optional[int] = None
    name: str
    imageUrl: Optional[str] = None
    status: StockStatus

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"id": 1, "name": "삼성전자", "imageUrl": "https://pattern-catcher-stock-image.s3.ap-northeast-2.amazonaws.com/stock/samsung.png", "status": "LISTED"},
                {"id": None, "name": "Apple Inc. (AAPL)", "imageUrl": None, "status": "LISTED_OUTSIDE"},
                {"id": None, "name": "교보생명", "imageUrl": None, "status": "UNLISTED"},
                {"id": None, "name": "모름", "imageUrl": None, "status": "UNKNOWN"}
            ]
        }
    }