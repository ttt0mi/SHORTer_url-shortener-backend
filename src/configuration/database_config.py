from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from src.configuration.settings import get_settings

mongo_client: AsyncMongoClient | None = None
mongo_database: AsyncDatabase | None = None


async def connect():
	global mongo_client, mongo_database
	try:
		mongo_client = AsyncMongoClient(
			get_settings().database_uri,
			maxPoolSize=10,
			maxIdletimeMS=45000,
		)
		mongo_database = mongo_client.get_default_database()
		if mongo_database is None:
			print("no connection could be established")
		else:
			print("connection established.")
			#these index creations will be moved
			# await mongo_database["blacklisted_tokens"].create_index(
			# 		[("added_at", 1)], expireAfterSeconds=60 * 60 * 24
			# )
			# await mongo_database["url_info_storage"].create_index(
			# 		[("expires_at", 1)], expireAfterSeconds=0
			# )
	except Exception as e:
		#this exception type will change
		raise RuntimeError(str(e))


async def disconnect():
	global mongo_client, mongo_database
	await mongo_client.close()
	print("connection closed.")


def get_database() -> AsyncDatabase:
	if mongo_database is None:
		#this exception type will change
		raise RuntimeError("database server not configured.")
	return mongo_database