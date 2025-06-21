from enum import Enum
from starlette import status


class SuccessStatus(Enum):
    SUCCESS = ("SUCCESS", "요청 성공.", status.HTTP_200_OK)
    STOCK_FOUND = ("STOCK_FOUND", "종목 조회 성공", status.HTTP_200_OK)
    PREDICTION_COMPLETE = ("PREDICTION_COMPLETE", "예측 완료", status.HTTP_200_OK)

    def __init__(self, code, message, http_status):
        self.code = code
        self.message = message
        self.http_status = http_status
