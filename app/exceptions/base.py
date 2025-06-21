from app.api_payload.code.status_code import ErrorStatus
from fastapi.responses import JSONResponse
from app.core.response import error_response


class APIException(Exception):
    def __init__(self, status: ErrorStatus):
        """
        커스텀 API 예외 클래스 (모든 비즈니스 예외는 이걸 상속받음)

        :param status: ErrorStatus enum 객체 (code, message, http_status 포함)
        """
        self.status = status
        self.status_code = status.http_status

    def __str__(self):
        return f"[{self.status.code}] {self.status.message}"

    def to_response(self) -> JSONResponse:
        return JSONResponse(
            status_code=self.status_code,
            content=error_response(self.status).__dict__
        )
