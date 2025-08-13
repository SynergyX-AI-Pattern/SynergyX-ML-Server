from enum import Enum
from starlette import status


class SuccessStatus(Enum):
    SUCCESS = ("SUCCESS", "요청 성공.", status.HTTP_200_OK)
    STOCK_FOUND = ("STOCK_FOUND", "종목 조회 성공", status.HTTP_200_OK)
    PREDICTION_COMPLETE = ("PREDICTION_COMPLETE", "예측 완료", status.HTTP_200_OK)
    BACKTEST_EXECUTED = ("BACKTEST_EXECUTED", "백테스팅 실행 성공", status.HTTP_200_OK)
    STOCK_PREDICTED = ("STOCK200", "15일 예측 성공", status.HTTP_200_OK)
    PATTERN_DETECTION_EXECUTED = ("PATTERN_DETECTION_EXECUTED", "패턴 감지 성공", status.HTTP_200_OK)
    IMAGE_SEARCH_SUCCESS = ("IMAGE_SEARCH_SUCCESS", "이미지로 종목 검색 성공", status.HTTP_200_OK)
    DIARY_ANALYSIS_SUCCESS = ("DIARY_ANALYSIS_SUCCESS", "감정 분석 성공", status.HTTP_200_OK)

    def __init__(self, code, message, http_status):
        self.code = code
        self.message = message
        self.http_status = http_status
