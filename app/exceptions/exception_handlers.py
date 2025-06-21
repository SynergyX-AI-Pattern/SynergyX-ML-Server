from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exceptions.base import APIException
from app.core.response import error_response
from app.api_payload.code.status_code import ErrorStatus


# 커스텀 API 예외 핸들러
async def api_exception_handler(request: Request, exc: APIException):
    return exc.to_response()


# FastAPI 내장 HTTP 예외 핸들러
# 존재하지 않는 경로(404), 메서드 오류(405) 등 기본적인 HTTP 에러에 대한 응답을 담당합니다.
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(ErrorStatus.COMMON_HTTP_ERROR).dict()
    )


# Validation 예외 핸들러
# 예: 필수 필드 누락, 타입 불일치 등 Pydantic validation 오류 처리
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=error_response(ErrorStatus.VALIDATION_ERROR).dict()
    )
