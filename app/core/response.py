from app.schemas.base_response import BaseResponse
from app.api_payload.code.status_code import SuccessStatus, ErrorStatus
from typing import Any


def success_response(data: Any = None, status: SuccessStatus = SuccessStatus.SUCCESS) -> BaseResponse:
    return BaseResponse(
        is_success=True,
        code=status.code,
        message=status.message,
        data=data
    )


def error_response(status: ErrorStatus, data: Any = None) -> BaseResponse:
    return BaseResponse(
        is_success=False,
        code=status.code,
        message=status.message,
        data=data
    )
