# src/models/responses.py
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from models.custom_types import AthensDateTime, CustomDate
from models.schema import AdminModel

default_configs = ConfigDict(
    from_attributes=True, serialize_by_alias=True, str_strip_whitespace=True
)


class EventResponse(BaseModel):
    id_: Optional[int] = Field(None, exclude=True)
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    start_location: str = Field(..., max_length=50)
    destination: str = Field(..., max_length=50)
    departure_time_to: AthensDateTime
    arrival_time_to: AthensDateTime
    departure_time_return: AthensDateTime
    arrival_time_return: AthensDateTime
    event_start_date: CustomDate
    event_end_date: CustomDate
    reserved_seats: int = 0
    total_seats: int
    price_per_seat: Decimal
    created_at: Optional[AthensDateTime] = None
    updated_at: Optional[AthensDateTime] = None

    model_config = default_configs


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
