import os
from functools import lru_cache

from dotenv import find_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
env_file_map = {"development": ".env.dev", "production": ".env.prod",}
env_path = find_dotenv(filename=env_file_map.get(ENVIRONMENT, ".env.dev"))

class Settings(BaseSettings):
	model_config = SettingsConfigDict(
		env_file=env_path, env_file_encoding="utf-8",
		extra="ignore", env_ignore_empty=True
	)
	
	database_uri: str = Field(..., alias="DATABASE_URI")
	token_key: str = Field(..., alias="TOKEN_KEY")
	
	allowed_hosts: list[str] = Field(default_factory=lambda: ["*"], alias="ALLOWED_HOSTS")
	allowed_origins: list[str] = Field(default_factory=lambda: ["*"], alias="ALLOWED_ORIGINS")
	
	environment: str = Field(default="development", alias="ENVIRONMENT")


@lru_cache
def get_settings() -> Settings:
	settings = Settings()
	return settings