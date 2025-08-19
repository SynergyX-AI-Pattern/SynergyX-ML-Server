from fastapi import APIRouter
from app.api.v1.endpoints import emotion_diary

router = APIRouter()

router.include_router(emotion_diary.router, prefix="/diaries", tags=["Emotion Diary"])