from typing import Annotated

from fastapi import APIRouter, Depends, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from starlette.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from src.configuration.dependencies import get_users_handler, get_token_handler
from src.exceptions.user_errors import MissingTokenError
from src.handlers.users_handler import UsersHandler
from src.handlers.token_handler import TokenHandler
from src.schemas.user_schemas import CreateUser, TokenResponse, CurrentUser

router = APIRouter(prefix="/api/auth", tags=["Authentication", "Authorisation"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login/", refreshUrl="api/auth/refresh/")


@router.post("/register/", status_code=HTTP_201_CREATED, summary="register a new user")
async def register_user(
		create_user_request: CreateUser,
		user_handler: UsersHandler = Depends(get_users_handler)
) -> dict:
	return await user_handler.create_user_with(create_user_request)


@router.post("/login/", response_model=TokenResponse, summary="login an existing user")
async def login(
		login_form: Annotated[OAuth2PasswordRequestForm, Depends()],
		user_handler: UsersHandler = Depends(get_users_handler),
		token_handler: TokenHandler = Depends(get_token_handler),
		response: Response = None
) -> TokenResponse:
	found_user = await user_handler.authenticate_from(login_form.username, login_form.password)
	data_to_encode = {"sub": found_user["id"], "email": found_user["email"]}
	access_token = await token_handler.generate_jwt_token_for(data=data_to_encode, expiry_in_minutes=1)
	refresh_token = await token_handler.generate_jwt_token_for(data=data_to_encode, expiry_in_minutes=1440, refresh=True)

	response.set_cookie(
			key="refresh_token",
			value=refresh_token,
			httponly=True,
			samesite="lax",
			secure=False
	)
	return TokenResponse(access_token=access_token, token_type="bearer")


#this shouldn't be here, but I'm too tired to find where to put it
async def retrieve_current_user(
		token: Annotated[str, Depends(oauth2_scheme)],
		user_handler: UsersHandler = Depends(get_users_handler),
		token_handler: TokenHandler = Depends(get_token_handler)
) -> CurrentUser:
	payload = await token_handler.verify_jwt_token(token)
	user_id = payload["sub"]
	user_email = payload["email"]
	user_jti = payload["jti"]

	user_data = await user_handler.retrieve_user_by(user_id=user_id)
	return CurrentUser(
			id=user_id, first_name=user_data["first_name"],
			last_name=user_data["last_name"],
			email=user_email, token_jti=user_jti
	)


@router.post("/refresh/", response_model=TokenResponse, summary="refresh a user's access token")
async def refresh_access_token(
		refresh_token: str = Cookie(default=None, description="a cookie that contains the refresh token"),
		token_handler: TokenHandler = Depends(get_token_handler)
):
	if not refresh_token:
		raise MissingTokenError(message="Refresh token missing")

	payload = await token_handler.verify_jwt_token(token=refresh_token, refresh=True)
	data_to_encode = {"sub": payload["sub"], "email": payload["email"]}
	access_token = await token_handler.generate_jwt_token_for(data=data_to_encode, expiry_in_minutes=30)
	return TokenResponse(access_token=access_token, token_type="bearer")


@router.post("/logout/")
async def logout(
		current_user: CurrentUser = Depends(retrieve_current_user),
		token_handler: TokenHandler = Depends(get_token_handler),
		refresh_token=Cookie(default=None, description="a cookie that contains the refresh token"),
):
	jti = current_user.token_jti
	await token_handler.blacklist_token(token_identity=jti)

	if refresh_token:
		try:
			refresh_payload = await token_handler.verify_jwt_token(refresh_token, refresh=True)
			refresh_jti = refresh_payload["jti"]
			await token_handler.blacklist_token(token_identity=refresh_jti)
		except Exception as e:
			print(f"Failed to blacklist refresh token: {e}")

	response = JSONResponse({"message": "Successfully logged out"}, status_code=200)
	response.delete_cookie(
			"refresh_token",
			httponly=False,
			samesite="lax",
			secure=False
	)
	return response


@router.get("/current", status_code=HTTP_200_OK, response_model=CurrentUser)
async def me(current_user: CurrentUser = Depends(retrieve_current_user)):
	return current_user