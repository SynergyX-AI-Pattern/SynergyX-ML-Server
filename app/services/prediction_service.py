import logging
from sqlalchemy.orm import Session
from app.models.stock import Stock
from app.exceptions.base import APIException
from app.api_payload.code.status_code import ErrorStatus
from app.services.predictors.gru_predictor import (
    fetch_close_data, preprocess,
    build_gru_model, predict_future_prices,
    calculate_rmse, set_seed,
    TIME_STEP
)
from app.crud.prediction import create_prediction_objects, save_predictions

logger = logging.getLogger(__name__)


class PredictionService:
    """
    예측 관련 비즈니스 로직을 처리합니다.
    """

    @staticmethod
    def predict_and_save(symbol: str, db: Session) -> list[float]:
        """
        (개별 테스트용) symbol로 예측 수행하고, DB에 저장한 뒤 결과 리스트 반환
        """
        # 종목 조회
        stock = db.query(Stock).filter(Stock.symbol == symbol).first()
        if not stock:
            logger.warning(f"[Service] 존재하지 않는 종목 symbol: {symbol}")
            raise APIException(ErrorStatus.STOCK_NOT_FOUND)

        stock_id = stock.id

        # 예측 수행
        predictions = PredictionService.predict_15_days(symbol)

        # DB 저장
        PredictionService.save_predictions_to_db(stock_id=stock_id, predicted=predictions, db=db)

        logger.info(f"[Service] 예측 완료 및 저장 - stock_id={stock_id}, count={len(predictions)}")

        return predictions

    @staticmethod
    def predict_15_days(symbol: str, epochs: int = 150, batch_size: int = 64) -> list[float]:
        """
        한 종목의 15일 주가를 예측합니다.
        """
        logger.info(f"[{symbol}] 예측 파이프라인 시작")

        # 시드 고정
        set_seed()
        logger.debug(f"[{symbol}] 시드 고정 완료")

        # 데이터 수집
        logger.debug(f"[{symbol}] yfinance 데이터 수집 시작")
        df = fetch_close_data(symbol)
        if df is None or df.empty:
            logger.warning(f"[{symbol}] 종가 데이터 없음 -> 예측 중단")
            raise APIException(ErrorStatus.STOCK_DATA_NOT_FOUND)

        logger.debug(f"[{symbol}] 수집된 데이터 수: {len(df)}")

        # 전처리
        X, y, scaler = preprocess(df)
        X = X.reshape(-1, TIME_STEP, 1)
        logger.debug(f"[{symbol}] 전처리 완료: X.shape={X.shape}, y.shape={y.shape}")

        # 훈련/테스트셋 분리
        train_size = int(len(X) * 0.7)
        X_train, y_train = X[:train_size], y[:train_size]
        X_test, y_test = X[train_size:], y[train_size:]
        logger.debug(f"[{symbol}] 데이터 분할: train={len(X_train)}, test={len(X_test)}")

        # 모델 생성 및 학습
        model = build_gru_model()
        logger.info(f"[{symbol}] GRU 모델 구조 생성 완료")

        # 학습 시작
        logger.info(f"[{symbol}] 모델 학습 시작 (epochs={epochs}, batch_size={batch_size})")
        model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, verbose=0)
        logger.info(f"[{symbol}] 모델 학습 완료")

        # RMSE 계산
        if len(X_test) > 0:
            y_pred = model.predict(X_test)
            y_pred_inv = scaler.inverse_transform(y_pred)
            y_test_inv = scaler.inverse_transform(y_test.reshape(-1, 1))
            rmse = calculate_rmse(y_test_inv, y_pred_inv)
            logger.info(f"[{symbol}] RMSE: {rmse:.2f}")
        else:
            logger.warning(f"[{symbol}] 테스트셋이 부족하여 RMSE 계산 생략")

        # 미래 15일 예측
        logger.info(f"[{symbol}] 미래 15일 예측 시작")
        predictions = predict_future_prices(model, X[-1], scaler, days=15)

        logger.info(f"[{symbol}] 예측 완료 → 상위 3개: {predictions[:3]}")
        return predictions

    @staticmethod
    def save_predictions_to_db(
            stock_id: int,
            predicted: list[float],
            db: Session
    ) -> None:
        """
        예측 결과를 prediction 테이블에 저장합니다.
        """
        predictions = create_prediction_objects(stock_id, predicted)
        save_predictions(db, predictions)
