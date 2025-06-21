from pydantic import BaseModel
from datetime import date

class BacktestRequest(BaseModel):
    startDate: date
    endDate: date

    model_config = {
        "json_schema_extra": {
            "example": {
                "startDate": "2023-01-01",
                "endDate": "2024-04-26"
            }
        }
    }

class BacktestResponse(BaseModel):
    matchedCount: int
    winRate: float
    averageReturn: float
    maxReturn: float
    maxReturnDate: date
    minReturn: float
    minReturnDate: date
    totalReturn: float
    lastMatchedDate: date
    lastMatchedReturn: float

    model_config = {
        "json_schema_extra": {
            "example": {
                "matchedCount": 8,
                "winRate": 65.2,
                "averageReturn": 12.5,
                "maxReturn": 25.4,
                "maxReturnDate": "2024-03-15",
                "minReturn": -7.8,
                "minReturnDate": "2024-02-10",
                "totalReturn": 88.3,
                "lastMatchedDate": "2024-04-20",
                "lastMatchedReturn": 9.3
            }
        }
    }