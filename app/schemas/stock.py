from pydantic import BaseModel, Field
from typing import Optional, List


class StockResponse(BaseModel):
    symbol: str
    name: str
    image_url: Optional[str] = None

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "symbol": "005930",
                "name": "삼성전자",
                "image_url": "https://example.com/samsung.png"
            }
        }
    }


class StockPredictionResponse(BaseModel):
    symbol: str
    predictions: List[float]
