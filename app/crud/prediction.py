from datetime import datetime, timezone
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
    if not predicted:
        logger.warning(f"[{stock_id}] 빈 예측 리스트가 전달됨")
        return []

    today = datetime.now(timezone.utc).date()

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
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        predictions.append(prediction)

    return predictions


def save_predictions(db: Session, predictions: list[Prediction]) -> None:
    """
    Prediction 객체 리스트를 DB에 저장합니다.
    """
    if not predictions:
        logger.warning("저장할 예측 데이터가 없습니다.")
        return

    try:
        upsert_count = 0
        insert_count = 0

        for p in predictions:
            existing = db.query(Prediction).filter(
                Prediction.stock_id == p.stock_id,
                Prediction.target_date == p.target_date
            ).first()

            if existing:
                # UPDATE
                existing.predicted_close = p.predicted_close
                existing.predicted_high = p.predicted_high
                existing.predicted_low = p.predicted_low
                existing.recommended_sell = p.recommended_sell
                existing.recommended_buy = p.recommended_buy
                existing.updated_at = datetime.now(timezone.utc)
                upsert_count += 1
                logger.debug(f"[UPSERT] UPDATE → stock_id={p.stock_id}, date={p.target_date}")
            else:
                # INSERT
                db.add(p)
                insert_count += 1
                logger.debug(f"[UPSERT] INSERT → stock_id={p.stock_id}, date={p.target_date}")

        db.commit()
        logger.info(f"[{predictions[0].stock_id}] 예측 저장 완료: INSERT={insert_count}, UPDATE={upsert_count}")
    except Exception as e:
        db.rollback()
        logger.exception(f"[{predictions[0].stock_id}] 예측 저장 실패: {str(e)}")
        raise
