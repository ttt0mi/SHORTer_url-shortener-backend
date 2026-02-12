from datetime import datetime, UTC

from pydantic import BaseModel, ConfigDict, AnyUrl


class URLShortenRequest(BaseModel):
	original_url: AnyUrl

class URLShortenResponse(BaseModel):
	short_url: str
	secret_key: str

class UrlInfo(BaseModel):
	model_config = ConfigDict(
			json_encoders={datetime: lambda v: v.isoformat(sep=" ", timespec="seconds")}
	)

	short_code: str
	secret_key: str
	short_url: str
	original_url: str
	active: bool = True
	clicks: int = 0
	created_at: datetime|str = datetime.now(UTC)
	last_used_at: datetime|str = "Not used"



#AnyUrl: any scheme allowed, top-level domain (TLD) not required, host required.
#AnyHttpUrl: scheme http or https, TLD not required, host required.
#HttpUrl: scheme http or https, TLD required, host required, max length 2083.