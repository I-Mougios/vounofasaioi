# src/models/responses.py
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from models.custom_types import AthensDateTime, CustomDate
from models.schema import AdminModel

default_configs = ConfigDict(
    from_attributes=True, serialize_by_alias=True, str_strip_whitespace=True
)


class UserResponse(BaseModel):
    id_: Optional[int] = Field(None, exclude=True)

    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    password: str = Field(..., max_length=128, exclude=True)
    date_of_birth: CustomDate
    email: EmailStr = Field(...)
    phone: str = Field(..., max_length=50)
    created_at: Optional[AthensDateTime] = None
    updated_at: Optional[AthensDateTime] = None

    model_config = default_configs


class TokenResponse(BaseModel):

    access_token: str
    token_type: str = "bearer"
    user: Optional[UserResponse] = None
    admin: Optional[AdminModel] = None

    model_config = default_configs
