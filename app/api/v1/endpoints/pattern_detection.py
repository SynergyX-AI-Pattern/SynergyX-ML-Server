from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.base_response import BaseResponse
from app.core.response import success_response
from app.api_payload.code.status_code import SuccessStatus
from app.db.session import get_db
from app.services.pattern_detection_service import PatternDetectionService

router = APIRouter()

@router.post(
    "",
    response_model=BaseResponse,
    summary="패턴 감지 실행",
    description="실시간 패턴 감지를 수행하고, 감지 성공 시 알림을 전송합니다.",
    tags=["Pattern Detection"]
)
def run_pattern_detection(db: Session = Depends(get_db)):
    results = PatternDetectionService.detect(db)
    return success_response(
        data=results,
        status=SuccessStatus.PATTERN_DETECTION_EXECUTED
    )
