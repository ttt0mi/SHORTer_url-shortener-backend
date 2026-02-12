from secrets import token_urlsafe

from src.database.url_repository import UrlRepository


async def generate_code_and_secret_key(length: int, urls: UrlRepository) -> tuple[str, str]:
	short_code = token_urlsafe(length)
	while await urls.exists(short_code):
		short_code = token_urlsafe(length)
	return short_code, short_code + token_urlsafe(4)