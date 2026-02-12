from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


hasher = PasswordHasher(memory_cost=2 ** 12, time_cost=3, parallelism=4)

def hash_password(password: str) -> str:
	return hasher.hash(password)

def verify_password(request_password: str, hashed_password: str) -> bool:
	try:
		return hasher.verify(password=request_password, hash=hashed_password)
	except VerifyMismatchError:
		return False