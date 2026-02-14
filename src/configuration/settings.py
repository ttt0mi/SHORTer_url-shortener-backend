from functools import lru_cache

from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


env_path = find_dotenv()

class Settings(BaseSettings):
	model_config = SettingsConfigDict(
			env_file=env_path, env_file_encoding="utf-8", extra="ignore", env_ignore_empty=True
	)

	DATABASE_URI: str
	TOKEN_KEY: str


@lru_cache
def get_settings() -> Settings:
	settings = Settings()
	return settings