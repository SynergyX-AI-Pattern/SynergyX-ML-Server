from pydantic import BaseModel, Field
from typing import Any, Optional


class BaseResponse(BaseModel):
    is_success: bool = Field(..., description="요청 성공 여부")
    message: Optional[str] = Field(None, description="응답 메시지")
    code: Optional[str] = Field(None, description="응답 코드")
    data: Optional[Any] = Field(None, description="실제 데이터")
