from fastapi import Depends
from pymongo.asynchronous.database import AsyncDatabase

from src.database.token_blacklist import TokenBlacklistProtocol
from src.database.token_blacklist import TokenBlacklist
from src.handlers.token_handler import TokenHandler
from src.database.url_repository import UrlRepository
from src.database.users_repository import UsersRepository
from src.handlers.urls_handler import UrlsHandler
from src.handlers.users_handler import UsersHandler
from src.configuration.database_config import get_database


def get_url_repository(db: AsyncDatabase = Depends(get_database)):
	return UrlRepository(db)


def get_user_repository(db: AsyncDatabase = Depends(get_database)):
	return UsersRepository(db)


def get_token_blacklist(db: AsyncDatabase = Depends(get_database)):
	return TokenBlacklist(db)


def get_urls_handler(urls: UrlRepository = Depends(get_url_repository)):
	return UrlsHandler(urls)


def get_users_handler(users: UsersRepository = Depends(get_user_repository)):
	return UsersHandler(users)


def get_token_handler(token_blacklist: TokenBlacklistProtocol = Depends(get_token_blacklist)):
	return TokenHandler(token_blacklist)