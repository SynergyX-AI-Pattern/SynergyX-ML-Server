from enum import Enum
from starlette import status


class ErrorStatus(Enum):
    NOT_FOUND = ("NOT_FOUND", "해당 리소스를 찾을 수 없습니다.", status.HTTP_404_NOT_FOUND)
    VALIDATION_ERROR = ("VALIDATION_ERROR", "유효성 검사 실패", status.HTTP_400_BAD_REQUEST)
    MODEL_ERROR = ("MODEL_ERROR", "모델 예측 중 오류 발생", status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 종목
    STOCK_NOT_FOUND = ("STOCK_NOT_FOUND", "해당 종목을 찾을 수 없습니다.", status.HTTP_404_NOT_FOUND)
    STOCK_OHLCV_NOT_FOUND = ("STOCK_OHLCV_NOT_FOUND", "종목 데이터를 찾을 수 없습니다.", status.HTTP_404_NOT_FOUND)

    # 백테스팅
    BACKTEST_FAILED = ("BACKTEST_FAILED", "백테스트 실행 중 오류가 발생했습니다.", status.HTTP_500_INTERNAL_SERVER_ERROR)
    INVALID_UNIT = ("INVALID_UNIT", "지원하지 않는 단위입니다.", status.HTTP_400_BAD_REQUEST)
    INVALID_UNIT_VALUE = ("INVALID_UNIT_VALUE", "단위 값이 유효하지 않습니다.", status.HTTP_400_BAD_REQUEST)
    INVALID_DATE_RANGE = ("INVALID_DATE_RANGE", "실행 기간이 유효하지 않습니다.", status.HTTP_400_BAD_REQUEST)

    # 패턴
    PATTERN_NOT_FOUND = ("PATTERN_NOT_FOUND", "해당 패턴을 찾을 수 없습니다.", status.HTTP_404_NOT_FOUND)

    COMMON_HTTP_ERROR = ("COMMON_HTTP_ERROR", "HTTP 오류가 발생했습니다.", status.HTTP_500_INTERNAL_SERVER_ERROR)

    def __init__(self, code, message, http_status):
        self.code = code
        self.message = message
        self.http_status = http_status
