from fastapi import FastAPI
import logging
import sys
import os
from dotenv import load_dotenv
from app.core.logging_config import setup_logging
from app.exceptions.base import APIException
from app.exceptions.exception_handlers import api_exception_handler
from app.api.v1 import routers
from app.api_payload.code.status_code import SuccessStatus
from app.core.response import success_response
from app.schemas.base_response import BaseResponse
from app.exceptions.exception_handlers import validation_exception_handler, http_exception_handler
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

load_dotenv()
setup_logging()

logger = logging.getLogger(__name__)

# === FastAPI 애플리케이션 인스턴스 생성 ===
app = FastAPI(
    title="ML Prediction API",
    description="GRU 예측, 백테스트 결과를 반환하는 API 서버입니다.",
    version="1.0.0",
    docs_url="/docs",  # Swagger 문서 경로
)

# === 예외 핸들러 등록 ===
# 커스텀 예외
app.add_exception_handler(APIException, api_exception_handler)


# Pydantic validation 예외 처리
@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(request, exc):
    logger.debug(f"[ValidationError] {request.method} {request.url} | {exc.errors()}")  # 상세 로그
    return await validation_exception_handler(request, exc)


# 기본 HTTP 예외 처리 (404, 405 등)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)

# === 라우터 등록 ===
app.include_router(routers.router, prefix="/api")


# === 헬스 체크 ===
@app.get(
    "/",
    response_model=BaseResponse,
    summary="서버 헬스 체크",
    description="FastAPI 서버가 정상적으로 동작 중인지 확인합니다.",
    tags=["Health"]
)
def root() -> BaseResponse:
    return success_response(
        data={"status": "ok"},
        status=SuccessStatus.SUCCESS
    )
