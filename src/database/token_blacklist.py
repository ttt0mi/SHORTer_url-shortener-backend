from datetime import datetime
from typing import Protocol
from zoneinfo import ZoneInfo

from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import PyMongoError

from src.exceptions.url_errors import DatabaseError


class TokenBlacklistProtocol(Protocol):
	async def add_token_to_blacklist(self, jti: str) -> None: ...

	async def is_token_in_blacklist(self, jti: str) -> bool: ...


class TokenBlacklist:
	def __init__(self, db: AsyncDatabase):
		self.db = db
		self.blacklisted_tokens = self.db.get_collection("blacklisted_tokens")
		self.init_index()

	async def init_index(self):
		"""a coroutine that cannot be awaited at __init__, will give a runtime warning for memory leaks"""
		await self.blacklisted_tokens.create_index(
				[("added_at", 1)], expireAfterSeconds=60 * 60 * 24
		)

	async def add_token_to_blacklist(self, jti: str) -> None:
		try:
			await self.blacklisted_tokens.insert_one({
					"token_identity": jti,
					"added_at": datetime.now(ZoneInfo('UTC'))
			})
		except PyMongoError as e:
			raise DatabaseError(str(e))

	async def is_token_in_blacklist(self, jti: str) -> bool:
		try:
			return await self.blacklisted_tokens.find_one({"token_identity": jti}) is not None
		except PyMongoError as e:
			raise DatabaseError(str(e))