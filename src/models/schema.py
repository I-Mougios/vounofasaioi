# src/models/schema.py
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.enumerations import Gender

from .custom_types import AthensDateTime, CustomDate
from .utils import to_snake_alias

default_configs = ConfigDict(
    from_attributes=True, alias_generator=to_snake_alias, populate_by_name=True
)


class BookingModel(BaseModel):
    # TODO: fill actual fields
    pass


class CancellationModel(BaseModel):
    # TODO: fill actual fields
    pass


class AddressModel(BaseModel):
    # TODO: fill actual fields
    pass


class UserModel(BaseModel):
    id_: Optional[int] = Field(None, exclude=True)

    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    password: str = Field(..., max_length=128)
    date_of_birth: CustomDate
    gender: Optional[Gender] = None
    email: EmailStr = Field(...)
    phone: str = Field(..., max_length=50)
    created_at: Optional[AthensDateTime] = None
    updated_at: Optional[AthensDateTime] = None

    user_bookings: Optional[List[BookingModel]] = None
    user_cancellations: Optional[List[CancellationModel]] = None
    address: Optional[AddressModel] = None

    model_config = default_configs
