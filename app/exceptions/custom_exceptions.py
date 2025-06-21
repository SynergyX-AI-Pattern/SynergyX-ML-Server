from app.exceptions.base import APIException
from app.api_payload.code.status_code import ErrorStatus


class NotFoundException(APIException):
    def __init__(self):
        super().__init__(ErrorStatus.NOT_FOUND)


class ModelErrorException(APIException):
    def __init__(self):
        super().__init__(ErrorStatus.MODEL_ERROR)
