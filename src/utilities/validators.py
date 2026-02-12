import re

from pydantic_core import PydanticCustomError


name_pattern = re.compile(r"^([a-z]+)([-']?)([a-z]+)$", re.I)
password_pattern = re.compile(r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+")
email_pattern = re.compile(r"^([\w.-]+)@([a-z]+)\.([a-z.]+)$", re.I)


def validate_after_date(date_str: str) -> bool:
	pass
#maybe validate in frontend


def validate_name(name: str) -> str:
	if name_pattern.fullmatch(name) is None:
		raise PydanticCustomError(
				"ValueError",
				"invalid first name '{name}'",
				{"name": name}
		)
	return name


def validate_email(email: str) -> str:
	if len(email) < 10:
		raise PydanticCustomError(
				"ValueError",
				"invalid email length for '{email}'. email should be at least 10 characters long",
				{"email": email}
		)
	return email


def validate_password(password: str) -> str:
	if password_pattern.fullmatch(password) is None or len(password) < 8:
		raise PydanticCustomError(
				"ValueError",
				"invalid password '{password}'. \
password should have at least 1 uppercase letter, 1 lowercase letter, 1 number, and 1 special character",
				{"password": password}
		)
	return password