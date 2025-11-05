from src.database.users_repository import UsersRepository
from src.exceptions.user_errors import UserNotFoundError, UserAlreadyExistsError, InvalidCredentialsError
from src.schemas.user_schemas import CreateUser
from src.utilities.security import hash_password, verify_password


class UsersHandler:
	def __init__(self, user_repository: UsersRepository):
		self.users = user_repository

	async def create_user_with(self, register_request: CreateUser):
		if await self.users.exists_by_email(register_request.email):
			raise UserAlreadyExistsError("This email has already been registered")
		user_data = register_request.model_dump()
		user_data["password"] = hash_password(register_request.password)
		return await self.users.add_user(user_data)

	async def authenticate_from(self, email: str, password: str):
		found_user_data = await self.users.find_user_by_email(email)
		if found_user_data is None:
			raise UserNotFoundError("Incorrect email, user not found")
		if not verify_password(
				request_password=password, hashed_password=found_user_data["password"]
		):
			raise InvalidCredentialsError("Incorrect password")
		return found_user_data

	async def retrieve_user_by(self, user_id: str):
		found_user_data = await self.users.find_user_by_id(user_id)
		if found_user_data is None:
			raise UserNotFoundError("User not found")
		return found_user_data