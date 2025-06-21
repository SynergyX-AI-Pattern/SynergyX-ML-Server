from pydantic import BaseModel, Field
from typing import Any, Optional


class BaseResponse(BaseModel):
    is_success: bool = Field(..., description="요청 성공 여부")
    message: Optional[str] = Field(None, description="응답 메시지")
    code: Optional[str] = Field(None, description="응답 코드")
    data: Optional[Any] = Field(None, description="실제 데이터")

    model_config = {
        "json_schema_extra": {
            "example": {
                "is_success": True,
                "code": "SUCCESS",
                "message": "종목 정보 조회 성공.",
                "data": {
                    "id": 101,
                    "symbol": "005930",
                    "name": "삼성전자",
                    "image_url": "https://images/005930.png"
                }
            }
        }
    }
