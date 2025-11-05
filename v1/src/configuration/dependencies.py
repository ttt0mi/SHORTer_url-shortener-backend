from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.configuration.database_config import get_database
from src.handlers.url_handler import UrlHandler
from src.database.url_repository import UrlRepository


def get_url_repository(db: AsyncIOMotorDatabase = Depends(get_database)):
	return UrlRepository(db)


def get_url_handler(urls: UrlRepository = Depends(get_url_repository)):
	return UrlHandler(urls)