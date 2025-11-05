from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from src.configuration.settings import get_settings

mongo_client: AsyncIOMotorClient | None = None
mongo_database: AsyncIOMotorDatabase | None = None

def connect():
	global mongo_client, mongo_database
	mongo_client = AsyncIOMotorClient(get_settings().DATABASE_URI)
	mongo_database = mongo_client.get_database("url_shortener_db_v1")
	if mongo_database is None: print("no connection could be established")
	else: print("connection established.")


def disconnect():
	global mongo_client, mongo_database
	mongo_client.close()
	print("connection closed.")


def get_database() -> AsyncIOMotorDatabase:
	if mongo_database is None:
		raise RuntimeError("database not configured.")
	return mongo_database