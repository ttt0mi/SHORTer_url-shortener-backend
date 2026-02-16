from functools import lru_cache

from dotenv import find_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = find_dotenv()

class Settings(BaseSettings):
	model_config = SettingsConfigDict(
		env_file=env_path, env_file_encoding="utf-8",
		extra="ignore", env_ignore_empty=True
	)
	
	database_uri: str = Field(..., alias="DATABASE_URI")
	token_key: str = Field(..., alias="TOKEN_KEY")
	allowed_hosts: list[str] = Field(default=["*"], alias="ALLOWED_HOSTS")
	allowed_origins: list[str]= Field(default=["*"], alias="ALLOWED_ORIGINS")


@lru_cache
def get_settings() -> Settings:
	settings = Settings()
	return settings