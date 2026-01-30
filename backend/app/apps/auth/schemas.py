import datetime as dt

from pydantic import BaseModel, Field


class LoginResponseShema(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"


class ForceLogoutSchema(BaseModel):
    use_token_since: dt.datetime = Field(default_factory=dt.datetime.now)
