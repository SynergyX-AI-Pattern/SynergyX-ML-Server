import numpy as np
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from tensorflow.keras import Sequential, Input
from tensorflow.keras.layers import GRU, Dense
from tensorflow.keras.utils import set_random_seed
from typing import Tuple
import logging
import random
import tensorflow as tf
import os

logger = logging.getLogger(__name__)

# ======= Hyperparameters =======
TIME_STEP = 100
EPOCHS = 150
BATCH_SIZE = 64
SEED = 42
# ===============================


# 시드 고정 함수
def set_seed(seed: int = SEED):
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)
    set_random_seed(seed)


set_seed()  # 모듈 임포트 시 한 번 고정


def fetch_close_data(symbol: str):
    """
    yfinance로부터 과거 5년 종가 데이터 수집
    """
    try:
        df = yf.Ticker(f"{symbol}.KS").history(period="5y")[['Close']]
        df.dropna(inplace=True)
        if df.empty:
            logger.warning(f"[{symbol}] 수집된 종가 데이터가 없습니다.")
            return None
        return df
    except Exception as e:
        logger.error(f"[{symbol}] 데이터 수집 실패: {e}")
        return None


def preprocess(df) -> Tuple[np.ndarray, np.ndarray, MinMaxScaler]:
    """
    데이터 정규화 및 GRU 입력 형식으로 변환
    """
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df)

    X, y = [], []
    for i in range(TIME_STEP, len(scaled)):
        X.append(scaled[i - TIME_STEP:i])
        y.append(scaled[i, 0])

    return np.array(X), np.array(y), scaler


def build_gru_model(input_shape=(TIME_STEP, 1)) -> Sequential:
    """
    GRU 기반 예측 모델 정의 및 컴파일
    """
    model = Sequential([
        Input(shape=input_shape),
        GRU(50, return_sequences=True),
        GRU(50),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model


def predict_future_prices(
        model: Sequential,
        last_input: np.ndarray,
        scaler: MinMaxScaler,
        days: int = 15  # 15일 예측
) -> list[float]:
    """
    마지막 시점 입력을 기반으로 미래 `days`일 예측
    """
    temp_input = list(last_input.reshape(-1))
    predictions = []

    for _ in range(days):
        x_input = np.array(temp_input[-TIME_STEP:]).reshape(1, TIME_STEP, 1)
        yhat = model.predict(x_input, verbose=0)
        temp_input.append(yhat[0][0])
        predictions.append(yhat[0][0])

    return scaler.inverse_transform(np.array(predictions).reshape(-1, 1)).flatten().tolist()


def calculate_rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    테스트셋에 대한 RMSE 계산
    """
    return np.sqrt(mean_squared_error(y_true, y_pred))
