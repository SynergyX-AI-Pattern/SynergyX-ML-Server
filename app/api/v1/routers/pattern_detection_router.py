from fastapi import APIRouter
from app.api.v1.endpoints import pattern_detection

router = APIRouter()
router.include_router(pattern_detection.router, prefix="/pattern-detections", tags=["Pattern Detection"])
