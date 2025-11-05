from fastapi import BackgroundTasks
from starlette.datastructures import URL

from src.database.url_repository import UrlRepository
from src.exceptions.url_exceptions import URLNotFoundError, DisabledURLError
from src.models.url_models import URLShortenRequest, UrlInfo, URLShortenResponse
from src.utilities.code_utils import generate_code_and_secret_key


class UrlHandler:
	def __init__(self, urls: UrlRepository):
		self.urls = urls

	async def create_shortened_url(self, request: URLShortenRequest, root_url: URL) -> URLShortenResponse:
		short_code, secret_key = await generate_code_and_secret_key(4, self.urls)		#passing the db to ensure a unique code
		short_url = str(root_url) + short_code

		new_info = UrlInfo(
				short_code=short_code, secret_key=secret_key, short_url=short_url, original_url=request.original_url.encoded_string()
		)
		await self.urls.add_url_info(new_info)
		return URLShortenResponse(short_url=short_url, secret_key=secret_key)

	async def get_original_url(self, short_code: str, background_task: BackgroundTasks) -> str:
		if result:= await self.urls.find_url_info(short_code):
			if not result.active:
				raise DisabledURLError("URL not active")
			background_task.add_task(self.urls.update_url_info_clicks, secret_key=result.secret_key)
			return result.original_url
		raise URLNotFoundError("URL not found")

	async def get_url_info(self, secret_key: str) -> UrlInfo:
		if result := await self.urls.find_url_info_via_secret(secret_key):
			if not result.active:
				raise DisabledURLError("URL not active")
			return result
		raise URLNotFoundError("URL not found")

	async def disable_shortened_url(self, secret_key: str) -> None:
		await self.urls.toggle_url_status(secret_key, True)

	async def enable_shortened_url(self, secret_key: str) -> None:
		await self.urls.toggle_url_status(secret_key, False)