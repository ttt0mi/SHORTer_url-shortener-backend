from fastapi import APIRouter, Depends, BackgroundTasks, Path
from starlette.requests import Request
from starlette.responses import RedirectResponse, StreamingResponse, HTMLResponse
from starlette.status import (
	HTTP_423_LOCKED, HTTP_201_CREATED, HTTP_204_NO_CONTENT
)

from src.handlers.urls_handler import UrlsHandler
from src.routes.authentication_router import retrieve_current_user
from src.schemas.user_schemas import CurrentUser
from src.configuration.dependencies import get_urls_handler
from src.schemas.url_schemas import *

router = APIRouter(prefix="/api/sh", tags=["URL Shortener Routes"])


@router.post("/", response_model=URLShortenResponse, status_code=HTTP_201_CREATED)
async def shorten_url(
		request: URLShortenRequest, raw_request: Request,
		current_user: CurrentUser = Depends(retrieve_current_user),
		handler: UrlsHandler = Depends(get_urls_handler)
):
	"""reconsider this route, "shortened url" is starting to look a bit long"""
	return await handler.create_shortened_url(
			current_user_id=current_user.id,
			request=request, root_url=raw_request.url,
	)


@router.get("/qr/{short_code}", dependencies=[Depends(retrieve_current_user)])
async def shorten_qrcode(
		short_code: str = Path(..., description="Short code to create QR Code with corresponding original url"),
		handler: UrlsHandler = Depends(get_urls_handler)
):
	"""
	unable to track clicks due to lack of an actual domain.
	due to localhost does not work on any other device aside from this one
	"""
	qrcode_buffer = await handler.create_url_qr_code(short_code=short_code)

	return StreamingResponse(
			content=qrcode_buffer, media_type="image/png", status_code=HTTP_201_CREATED
	)


@router.get("/{short_code}")
async def redirect(
		bt: BackgroundTasks,
		short_code: str = Path(..., description="Short code to redirect to original url"),
		handler: UrlsHandler = Depends(get_urls_handler)
):
	original_url = await handler.get_original_url(short_code=short_code, background_task=bt)
	if original_url.get("status"):
		return RedirectResponse(url=original_url.get("original_url"))

	error_html = f"""
	<!DOCTYPE html>
	<html>
		<head>
	        <title>Error 404</title>
	    </head>
	    <body style="font-family: monospace; text-align: center; padding: 100px;">
	        <h1 style=font-size: 40px; color: red;>Error 423 - Page Not Available on this URL</h1>
	    </body>
	</html>"""
	return HTMLResponse(content=error_html, status_code=HTTP_423_LOCKED)


@router.get("/{short_code}/info", response_model=UrlInfo, response_model_exclude_none=True,
			dependencies=[Depends(retrieve_current_user)])
async def get_info(
		short_code: str = Path(..., description="short code used to view all info about the shortened url"),
		handler: UrlsHandler = Depends(get_urls_handler)
):
	return await handler.get_url_info(short_code=short_code)


@router.get("/info/all", response_model=list[UrlInfo], response_model_exclude_none=True)
async def get_infos(
		current_user: CurrentUser = Depends(retrieve_current_user),
		handler: UrlsHandler = Depends(get_urls_handler)
):
	return await handler.get_users_url_infos(current_user_id=current_user.id)


@router.patch("/disable/{short_code}", status_code=HTTP_204_NO_CONTENT,
			  dependencies=[Depends(retrieve_current_user)])
async def disable_url(
		short_code: str = Path(..., description="short code used to disable the shortened url"),
		handler: UrlsHandler = Depends(get_urls_handler)
):
	await handler.disable_shortened_url(short_code=short_code)


@router.patch("/enable/{short_code}", status_code=HTTP_204_NO_CONTENT,
			  dependencies=[Depends(retrieve_current_user)])
async def enable_url(
		short_code: str = Path(..., description="short code used to enable the shortened url"),
		handler: UrlsHandler = Depends(get_urls_handler)
):
	await handler.enable_shortened_url(short_code=short_code)