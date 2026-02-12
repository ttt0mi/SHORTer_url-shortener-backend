from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, AnyUrl, Field, FutureDatetime


class URLShortenRequest(BaseModel):
	original_url: AnyUrl
	expires_at: Optional[FutureDatetime] = None

	model_config = ConfigDict(
			json_schema_extra={
					"example": {
						"original_url": "https://example.com/",
						"expires_at": (datetime.now(ZoneInfo('UTC')) + timedelta(days=1)).isoformat(),
					}
			}
	)


class URLShortenResponse(BaseModel):
	short_code: str
	short_url: str


class UrlInfo(BaseModel):
	model_config = ConfigDict(
			json_encoders={datetime: lambda v: v.strftime("%c")}
	)

	user_id: str
	short_code: str
	short_url: str
	original_url: str
	active: bool = True
	clicks: int = 0
	created_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo('UTC')))
	last_used_at: datetime|str = "Not used"
	expires_at: Optional[datetime] = None


#AnyUrl: any scheme allowed, top-level domain (TLD) not required, host required.
#AnyHttpUrl: scheme http or https, TLD not required, host required.
#HttpUrl: scheme http or https, TLD required, host required, max length 2083.