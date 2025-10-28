from fastapi import APIRouter
from app.api.v1.endpoints import prediction_visual

router = APIRouter()
router.include_router(prediction_visual.router, prefix="/predict", tags=["Prediction Visualization"])
