from enum import Enum
from starlette import status


class ErrorStatus(Enum):
    NOT_FOUND = ("NOT_FOUND", "해당 리소스를 찾을 수 없습니다.", status.HTTP_404_NOT_FOUND)
    VALIDATION_ERROR = ("VALIDATION_ERROR", "유효성 검사 실패", status.HTTP_400_BAD_REQUEST)
    MODEL_ERROR = ("MODEL_ERROR", "모델 예측 중 오류 발생", status.HTTP_500_INTERNAL_SERVER_ERROR)
    NOTIFICATION_SEND_FAILED = ("NOTIFICATION_SEND_FAILED", "알림 전송에 실패했습니다.", status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 종목
    STOCK_NOT_FOUND = ("STOCK_NOT_FOUND", "해당 종목을 찾을 수 없습니다.", status.HTTP_404_NOT_FOUND)
    STOCK_OHLCV_NOT_FOUND = ("STOCK_OHLCV_NOT_FOUND", "종목 데이터를 찾을 수 없습니다.", status.HTTP_404_NOT_FOUND)

    # 백테스팅
    NO_MATCHED_SECTION = ("NO_MATCHED_SECTION", "패턴과 유사한 구간이 없어 백테스트를 수행할 수 없습니다.", status.HTTP_400_BAD_REQUEST)
    INVALID_UNIT = ("INVALID_UNIT", "지원하지 않는 단위입니다.", status.HTTP_400_BAD_REQUEST)
    INVALID_UNIT_VALUE = ("INVALID_UNIT_VALUE", "단위 값이 유효하지 않습니다.", status.HTTP_400_BAD_REQUEST)
    INVALID_DATE_RANGE = ("INVALID_DATE_RANGE", "실행 기간이 유효하지 않습니다.", status.HTTP_400_BAD_REQUEST)
    NO_RESAMPLED_DATA = ("NO_RESAMPLED_DATA", "리샘플링 결과가 존재하지 않습니다.", status.HTTP_400_BAD_REQUEST)
    PATTERN_TOO_FLAT = ("PATTERN_TOO_FLAT", "패턴 값이 거의 일정하여 비교할 수 없습니다.", status.HTTP_400_BAD_REQUEST)
    NOT_ENOUGH_DATA = ("NOT_ENOUGH_DATA", "시계열 데이터가 패턴보다 짧아 비교할 수 없습니다.", status.HTTP_400_BAD_REQUEST)
    RETURN_CALCULATION_FAILED = ("RETURN_CALCULATION_FAILED", "수익률 계산에 실패했습니다.", status.HTTP_400_BAD_REQUEST)

    # 패턴
    PATTERN_NOT_FOUND = ("PATTERN_NOT_FOUND", "해당 패턴을 찾을 수 없습니다.", status.HTTP_404_NOT_FOUND)
    PATTERN_DETECTION_FAILED = ("PATTERN_DETECTION_FAILED", "실시간 패턴 감지 중 오류가 발생했습니다.", status.HTTP_500_INTERNAL_SERVER_ERROR)

    COMMON_HTTP_ERROR = ("COMMON_HTTP_ERROR", "HTTP 오류가 발생했습니다.", status.HTTP_500_INTERNAL_SERVER_ERROR)

    def __init__(self, code, message, http_status):
        self.code = code
        self.message = message
        self.http_status = http_status
