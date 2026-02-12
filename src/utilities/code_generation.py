import secrets
from src.database.url_repository import UrlRepository


async def generate_url_code(length: int, urls: UrlRepository) -> str:
	while await urls.exists(code := secrets.token_urlsafe(length)):
		pass
	return code