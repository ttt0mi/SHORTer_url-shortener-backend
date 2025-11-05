from fastapi import APIRouter, Depends, BackgroundTasks, Path
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse

from src.configuration.dependencies import get_url_handler
from src.handlers.url_handler import UrlHandler
from src.models.url_models import *

router = APIRouter(prefix="/shorter", tags=["URL Shortener Routes"])


@router.post("/", response_model=URLShortenResponse, status_code=status.HTTP_201_CREATED)
async def shorten_url(
		request: URLShortenRequest, raw_request: Request,
		handler: UrlHandler = Depends(get_url_handler)
):
	return await handler.create_shortened_url(request, raw_request.url)


@router.get("/{short_code}")
async def redirect(
		bt: BackgroundTasks,
		short_code: str = Path(..., description="Short code to redirect to original url"),
		handler: UrlHandler = Depends(get_url_handler)
):
	original_url = await handler.get_original_url(short_code, background_task=bt)
	return RedirectResponse(original_url)


@router.get("/info/{secret_key}",
			response_model=UrlInfo, response_model_exclude={"short_code"})
async def get_info(
		secret_key: str = Path(..., description="secret key to view info about shortened url"),
		handler: UrlHandler = Depends(get_url_handler)
):
	return await handler.get_url_info(secret_key)


@router.patch("/disable/{secret_key}", status_code=status.HTTP_204_NO_CONTENT)
async def disable_url(
		secret_key: str = Path(..., description="secret key to disable shortened url"),
		handler: UrlHandler = Depends(get_url_handler)
):
	await handler.disable_shortened_url(secret_key)


@router.patch("/enable/{secret_key}", status_code=status.HTTP_204_NO_CONTENT)
async def enable_url(
		secret_key: str = Path(..., description="secret key to enable shortened url"),
		handler: UrlHandler = Depends(get_url_handler)
):
	await handler.enable_shortened_url(secret_key)