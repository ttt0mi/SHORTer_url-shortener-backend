from typing import Optional

from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import PyMongoError

from src.exceptions.url_errors import DatabaseError

class UsersRepository:
	def __init__(self, db: AsyncDatabase):
		self.db = db
		self.users = self.db.get_collection("url_shortener_users")

	async def add_user(self, user_data: dict):
		try:
			await self.users.insert_one(user_data)
			user_data["id"] = str(user_data.pop("_id"))
			user_data.pop("password")
			return user_data
		except PyMongoError as e:
			raise DatabaseError(str(e))

	async def find_user_by_id(self, user_id: str) -> Optional[dict]:
		try:
			result = await self.users.find_one({"_id": ObjectId(user_id)})
			if result is None:
				return None
			result["id"] = str(result.pop("_id"))
			return result
		except PyMongoError as e:
			raise DatabaseError(str(e))

	async def find_user_by_email(self, email: str) -> Optional[dict]:
		try:
			result = await self.users.find_one({"email": email})
			if result is None:
				return None
			result["id"] = str(result.pop("_id"))
			return result
		except PyMongoError as e:
			raise DatabaseError(str(e))

	async def exists_by_email(self, email) -> bool:
		try:
			return await self.users.find_one({"email": email}) is not None
		except PyMongoError as e:
			raise DatabaseError(str(e))