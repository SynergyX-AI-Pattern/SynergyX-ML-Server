from enum import Enum
from starlette import status


class ErrorStatus(Enum):
    NOT_FOUND = ("NOT_FOUND", "해당 리소스를 찾을 수 없습니다.", status.HTTP_404_NOT_FOUND)
    VALIDATION_ERROR = ("VALIDATION_ERROR", "유효성 검사 실패", status.HTTP_400_BAD_REQUEST)
    MODEL_ERROR = ("MODEL_ERROR", "모델 예측 중 오류 발생", status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 종목
    STOCK_NOT_FOUND = ("STOCK_NOT_FOUND", "해당 종목을 찾을 수 없습니다.", status.HTTP_404_NOT_FOUND)

    def __init__(self, code, message, http_status):
        self.code = code
        self.message = message
        self.http_status = http_status
