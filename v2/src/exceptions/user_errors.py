from fastapi import HTTPException
from starlette.status import (
	HTTP_404_NOT_FOUND, HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
)


class UserNotFoundError(HTTPException):
	def __init__(self, message: str, status_code: int=HTTP_404_NOT_FOUND, headers: dict=None):
		super().__init__(status_code, message, headers or {})


class UserAlreadyExistsError(HTTPException):
	def __init__(self, message: str, status_code: int=HTTP_400_BAD_REQUEST, headers: dict=None):
		super().__init__(status_code, message, headers or {})


class InvalidCredentialsError(HTTPException):
	def __init__(self, message: str, status_code: int=HTTP_403_FORBIDDEN, headers: dict=None):
		super().__init__(status_code, message, headers or {})


class UnauthorisedTokenAccessError(HTTPException):
	def __init__(self, message: str, status_code: int=HTTP_401_UNAUTHORIZED, headers: dict=None):
		super().__init__(status_code, message, headers or {})

class TokenBlacklistedError(HTTPException):
	def __init__(self, message: str, status_code: int=HTTP_403_FORBIDDEN, headers: dict=None):
		super().__init__(status_code, message, headers or {})

class MissingTokenError(HTTPException):
	def __init__(self, message: str, status_code: int=HTTP_404_NOT_FOUND, headers: dict=None):
		super().__init__(status_code, message, headers or {})