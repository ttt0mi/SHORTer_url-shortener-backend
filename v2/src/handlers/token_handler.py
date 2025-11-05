import uuid
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import jwt
from jwt.exceptions import PyJWTError, ExpiredSignatureError

from src.database.token_blacklist import TokenBlacklistProtocol
from src.configuration.settings import get_settings
from src.exceptions.user_errors import UnauthorisedTokenAccessError, MissingTokenError, TokenBlacklistedError

SECRET_KEY = get_settings().TOKEN_KEY

class TokenHandler:
	def __init__(self, token_blacklist: TokenBlacklistProtocol):
		self.token_blacklist = token_blacklist
		self.ALGORITHM = "HS256"
		"""i am only putting this here to stop the 'this method may be static' error in 'generate_jwt_token_for()'"""

	async def blacklist_token(self, token_identity: str):
		await self.token_blacklist.add_token_to_blacklist(token_identity)

	async def is_token_blacklisted(self, token_identity: str) -> bool:
		return await self.token_blacklist.is_token_in_blacklist(token_identity)

	async def generate_jwt_token_for(self, data: dict, expiry_in_minutes: int, refresh: bool = False) -> str:
		payload_to_encode = data.copy()
		payload_to_encode["jti"] = str(uuid.uuid4())
		payload_to_encode["exp"] = datetime.now(ZoneInfo('UTC')) + timedelta(minutes=expiry_in_minutes)
		payload_to_encode["type"] = "refresh_token" if refresh else "access_token"
		return jwt.encode(payload=payload_to_encode, key=SECRET_KEY, algorithm=self.ALGORITHM)

	async def verify_jwt_token(self, token: str, refresh: bool = False):
		try:
			payload: dict = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[self.ALGORITHM])
		except (ExpiredSignatureError, PyJWTError):
			raise UnauthorisedTokenAccessError("Invalid token.", headers={"WWW-Authenticate": "Bearer"})

		if refresh and payload["type"] != "refresh_token":
			raise MissingTokenError("Refresh token missing")

		if not payload.get("jti"):
			raise MissingTokenError("Token missing")

		if await self.is_token_blacklisted(token_identity=payload["jti"]):
			raise TokenBlacklistedError("Token has been revoked.")

		return payload