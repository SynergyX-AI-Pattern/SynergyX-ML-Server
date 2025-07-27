from datetime import datetime, timedelta, UTC
from sqlalchemy.orm import Session
from app.models.prediction import Prediction
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def create_prediction_objects(stock_id: int, predicted: list[float]) -> list[Prediction]:
    """
    예측 결과 리스트를 Prediction 객체 리스트로 변환합니다.
    주말 제외: bdate_range()로 미래 15 영업일 기준
    """
    today = datetime.now(UTC).date()

    # 주말 제외된 15 영업일 생성
    biz_days = pd.bdate_range(start=today + pd.Timedelta(days=1), periods=len(predicted)).date

    predictions = []
    for i, price in enumerate(predicted):
        prediction = Prediction(
            stock_id=stock_id,
            target_date=biz_days[i],
            predicted_close=price,
            predicted_high=price * 1.02,
            predicted_low=price * 0.98,
            recommended_sell=price * 1.01,
            recommended_buy=price * 0.99,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )
        predictions.append(prediction)

    return predictions


def save_predictions(db: Session, predictions: list[Prediction]) -> None:
    """
    Prediction 객체 리스트를 DB에 저장합니다.
    """
    db.bulk_save_objects(predictions)
    db.flush()
    db.commit()
    logger.debug(f"[{predictions[0].stock_id}] 예측 결과 {len(predictions)}건 저장 완료")
