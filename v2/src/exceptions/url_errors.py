from fastapi import HTTPException
from starlette.status import (
	HTTP_503_SERVICE_UNAVAILABLE, HTTP_423_LOCKED, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
)


class DatabaseError(HTTPException):
	def __init__(self, detail: str, status_code: int = HTTP_503_SERVICE_UNAVAILABLE):
		super().__init__(detail=detail, status_code=status_code)


class DisabledURLError(HTTPException):
	def __init__(self, detail: str, status_code: int = HTTP_423_LOCKED):
		super().__init__(detail=detail, status_code=status_code)


class URLNotFoundError(HTTPException):
	def __init__(self, detail: str, status_code: int = HTTP_404_NOT_FOUND):
		super().__init__(detail=detail, status_code=status_code)


class UrlQRCodeGenerationError(HTTPException):
	def __init__(self, detail: str, status_code: int = HTTP_500_INTERNAL_SERVER_ERROR):
		super().__init__(detail=detail, status_code=status_code)