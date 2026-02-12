from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import PyMongoError

from src.exceptions.url_exceptions import URLNotFoundError
from src.exceptions.url_exceptions import DatabaseError
from src.models.url_models import UrlInfo


class UrlRepository:
	def __init__(self, db: AsyncIOMotorDatabase):
		self.db = db
		self.collection = self.db.get_collection("url_info_storage")

	async def exists(self, code: str) -> bool:
		try:
			return await self.collection.find_one({"short_code": code}) is not None
		except PyMongoError as e:
			raise DatabaseError(str(e))

	async def add_url_info(self, info: UrlInfo):
		try:
			data = info.model_copy().model_dump()
			await self.collection.insert_one(data)
		except PyMongoError as e:
			raise DatabaseError(str(e))

	async def update_url_info_clicks(self, secret_key: str):
		try:
			await self.collection.update_one(
					{"secret_key": secret_key},
					{"$set": {"last_used_at": datetime.now()}, "$inc": {"clicks": 1}}
			)
		except PyMongoError as e:
			raise DatabaseError(str(e))

	async def find_url_info(self, code: str) -> UrlInfo:
		try:
			result = await self.collection.find_one({"short_code": code})
			if result is None:
				raise URLNotFoundError("URL not found")
			return UrlInfo.model_construct(**result)
		except PyMongoError as e:
			raise DatabaseError(str(e))

	async def find_url_info_via_secret(self, secret_key: str) -> UrlInfo:
		try:
			result = await self.collection.find_one({"secret_key": secret_key})
			if result is None:
				raise URLNotFoundError("URL not found")
			return UrlInfo.model_construct(**result)
		except PyMongoError as e:
			raise DatabaseError(str(e))

	async def toggle_url_status(self, secret_key: str, disable: bool):
		try:
			if disable:
				await self.collection.update_one(
						{"secret_key": secret_key},
						{"$set": {"active": False, "last_used_at": datetime.now()}}
				)
			else:
				await self.collection.update_one(
						{"secret_key": secret_key},
						{"$set": {"active": True, "last_used_at": datetime.now()}}
				)
		except DatabaseError as e:
			raise DatabaseError(str(e))