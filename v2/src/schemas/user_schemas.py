from typing import Annotated

from pydantic import BaseModel, EmailStr, AfterValidator, ConfigDict

from src.utilities.validators import validate_name, validate_email, validate_password


class CreateUser(BaseModel):
	first_name: Annotated[str, AfterValidator(validate_name)]
	last_name: Annotated[str, AfterValidator(validate_name)]
	email: Annotated[EmailStr, AfterValidator(validate_email)]
	password: Annotated[str, AfterValidator(validate_password)]

	model_config = ConfigDict(
			json_schema_extra={
					"example": {
							"first_name": "Tom",
							"last_name": "Jones",
							"email": "tj10@email.com",
							"password": "Tom12345@",
					}
			}
	)


class TokenResponse(BaseModel):
	access_token: str
	token_type: str


class CurrentUser(BaseModel):
	id: str
	first_name: str
	last_name: str
	email: EmailStr
	token_jti: str