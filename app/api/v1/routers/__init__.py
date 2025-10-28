from fastapi import APIRouter
from app.api.v1.routers import stock_router, backtest_router, pattern_detection_router, emotion_diary_router, prediction_visual_router

router = APIRouter()

router.include_router(stock_router.router, prefix="/v1")
router.include_router(backtest_router.router, prefix="/v1")
router.include_router(pattern_detection_router.router, prefix="/v1")
router.include_router(emotion_diary_router.router, prefix="/v1")
router.include_router(prediction_visual_router.router, prefix="/v1", tags=["Prediction Visualization"])

# 아래에 추가 ex. router.include_router(user_router.router, prefix="/v1")
