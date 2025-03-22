from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

class TokenTypeEnum(str, Enum):
    bearer = "bearer"

class TokenModel(BaseModel):
    access_token: str
    token_type: str = TokenTypeEnum.bearer

class TokenAuthCreateModel(BaseModel):
    user_id: int
    token_type: TokenTypeEnum
    access_token: str
    refresh_token: str
    expires_at: datetime
    created_at: datetime

class TokenAuthModel(BaseModel):
    token_id: int
    user_id: int
    token_type: TokenTypeEnum
    access_token: str
    refresh_token: str
    expires_at: datetime
    created_at: datetime

class TokenDataModel(BaseModel):
    username: str = Field(min_length=3, max_length=50)