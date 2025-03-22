from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

class RoleEnum(str, Enum):
    supervisor = 'supervisor'
    admin = 'admin'
    user = 'user'

class IsActiveEnum(int, Enum):
    active = 1
    deactivated = 0

class UserCreateModel(BaseModel):
    user_name: str = Field(min_length=3, max_length=50)
    cpf: str = Field(min_length=11, max_length=14)
    email: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: IsActiveEnum
    role: RoleEnum

class UserInDBModel(UserCreateModel):
    password: str = Field(min_length=6, max_length=60)

class UserModel(BaseModel):
    user_id: int
    user_name: str = Field(min_length=3, max_length=50)
    cpf: str = Field(min_length=11, max_length=14)
    email: str
    password: str = Field(min_length=6, max_length=60)
    created_at: datetime
    updated_at: datetime
    is_active: IsActiveEnum
    role: RoleEnum