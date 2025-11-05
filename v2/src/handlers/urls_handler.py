from io import BytesIO

import segno
from fastapi import BackgroundTasks
from starlette.datastructures import URL

from src.database.url_repository import UrlRepository
from src.exceptions.url_errors import URLNotFoundError, UrlQRCodeGenerationError
from src.schemas.url_schemas import UrlInfo, URLShortenRequest, URLShortenResponse
from src.utilities.code_generation import generate_url_code


class UrlsHandler:
	def __init__(self, url_repository: UrlRepository):
		self.urls = url_repository

	async def create_shortened_url(self, current_user_id: str, request: URLShortenRequest, root_url: URL) -> URLShortenResponse:
		new_info = await self.__build_url_info(current_user_id, request, root_url)
		await self.urls.add_url_info(new_info)
		return URLShortenResponse(short_code=new_info.short_code, short_url=new_info.short_url)

	async def create_url_qr_code(self, short_code: str) ->BytesIO :
		if result := await self.urls.find_url_info(code=short_code):
			try:
				img = segno.make_qr(content=result["original_url"], error="M")
				buffer = BytesIO()
				img.save(buffer, kind="png", scale=5)
				buffer.seek(0)
				return buffer
			except Exception as e:
				raise UrlQRCodeGenerationError(status_code=500, detail=f"error generating QR code: {e}")
		raise URLNotFoundError("URL not found")


	async def get_original_url(self, short_code: str, background_task: BackgroundTasks) -> dict:
		if result := await self.urls.find_url_info(code=short_code):
			"""snippet above uses the walrus op ':=' to check the condition. assigns the value to result if truthy, raises error if falsey"""
			if result["active"] is True:
				background_task.add_task(self.urls.update_url_info_clicks, code=short_code)
				#maybe add 2 types of clicks, active & inactive

			return {
					"original_url": result["original_url"],
					"status": result["active"],
			}
		raise URLNotFoundError("URL not found")

	async def get_url_info(self, short_code: str) -> UrlInfo:
		if result := await self.urls.find_url_info(code=short_code):
			return UrlInfo.model_construct(**result)
		raise URLNotFoundError("URL not found")

	async def get_users_url_infos(self, current_user_id: str) -> list[UrlInfo]:
		if results := await self.urls.find_user_url_infos(user_id=current_user_id):
			return [UrlInfo.model_construct(**result) for result in results]
		raise URLNotFoundError("No Urls found")

	async def disable_shortened_url(self, short_code: str) -> None:
		await self.urls.toggle_url_status(code=short_code, disable=True)

	async def enable_shortened_url(self, short_code: str) -> None:
		await self.urls.toggle_url_status(code=short_code, disable=False)

	async def __build_url_info(self, current_user_id: str, request: URLShortenRequest, root_url: URL) -> UrlInfo:
		short_code = await generate_url_code(4, self.urls)  #passing the repo to ensure a unique code
		short_url = str(root_url) + short_code
		return UrlInfo(
				user_id=current_user_id, short_code=short_code, short_url=short_url,
				original_url=request.original_url.encoded_string(), expires_at=request.expires_at,
		)