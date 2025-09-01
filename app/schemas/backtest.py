from typing import Optional
from pydantic import BaseModel
from datetime import date, datetime

class BacktestRequest(BaseModel):
    startDate: date
    endDate: date

    model_config = {
        "json_schema_extra": {
            "example": {
                "startDate": "2025-06-13",
                "endDate": "2025-06-26"
            }
        }
    }

class HighlightRange(BaseModel):
    fromDate: datetime
    toDate: datetime

    model_config = {
        "json_schema_extra": {
            "example": {
                "fromDate": "2024-02-01T09:00:00",
                "toDate": "2024-03-15T15:00:00"
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
    highlightRange: Optional[HighlightRange] = None

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
                "lastMatchedReturn": 9.3,
                "highlightRange": {
                    "fromDate": "2024-02-01T09:00:00",
                    "toDate": "2024-03-15T15:00:00"
                }
            }
        }
    }