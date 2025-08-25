from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from src.enumerations import Gender

from .custom_types import CustomDate
from .utils import to_snake_alias

default_configs = ConfigDict(
    from_attributes=True,
    alias_generator=to_snake_alias,
    populate_by_name=True,
    str_strip_whitespace=True,
    validate_assignment=True,
    serialize_by_alias=True,
)


class UserUpdateModel(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    date_of_birth: Optional[CustomDate] = None
    gender: Optional[Gender] = None

    model_config = default_configs


class UserLogin(BaseModel):
    email: EmailStr
    password: str
