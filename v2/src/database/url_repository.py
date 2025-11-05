from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import PyMongoError

from src.exceptions.url_errors import DatabaseError
from src.schemas.url_schemas import UrlInfo


class UrlRepository:
	def __init__(self, db: AsyncDatabase):
		self.db = db
		self.collection = self.db.get_collection("url_info_storage")
		self.init_index()

	async def init_index(self):
		"""a coroutine that cannot be awaited at __init__, will give a runtime warning for memory leaks"""
		await self.collection.create_index([("expires_at", 1)], expireAfterSeconds=0)

	async def add_url_info(self, info: UrlInfo):
		try:
			url_data = info.model_dump(exclude_none=True)
			await self.collection.insert_one(url_data)
		except PyMongoError as e:
			raise DatabaseError(str(e))

	async def update_url_info_clicks(self, code: str):
		try:
			await self.collection.update_one(
					{"short_code": code},
					{
							"$set": {"last_used_at": datetime.now(ZoneInfo('UTC'))},
							"$inc": {"clicks": 1}
					}
			)
		except PyMongoError as e:
			raise DatabaseError(str(e))

	async def find_url_info(self, code: str) -> Optional[dict]:
		try:
			return await self.collection.find_one({"short_code": code})
		except PyMongoError as e:
			raise DatabaseError(str(e))

	async def find_user_url_infos(self, user_id: str) -> list[dict]:
		try:
			return await self.collection.find({"user_id": user_id}).to_list()
		except PyMongoError as e:
			raise DatabaseError(str(e))

	async def toggle_url_status(self, code: str, disable: bool):
		try:
			await self.collection.update_one(
					{"short_code": code},
					{
							"$set": {"active": False if disable else True, "last_used_at": datetime.now(ZoneInfo('UTC'))}
					}
			)
		except PyMongoError as e:
			raise DatabaseError(str(e))

	async def exists(self, code: str) -> bool:
		try:
			return await self.collection.find_one({"short_code": code}) is not None
		except PyMongoError as e:
			raise DatabaseError(str(e))