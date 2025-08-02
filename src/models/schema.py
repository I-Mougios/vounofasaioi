# src/models/schema.py
from __future__ import annotations

from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.enumerations import BookingStatus, EventStatus, Gender, PaymentMethod

from .custom_types import AthensDateTime, CustomDate
from .utils import to_snake_alias

default_configs = ConfigDict(
    from_attributes=True,
    alias_generator=to_snake_alias,
    populate_by_name=True,
    str_strip_whitespace=True,
    validate_assignment=True,
    serialize_by_alias=True,
)


class UserModel(BaseModel):
    id_: Optional[int] = Field(None, exclude=True)

    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    password: str = Field(..., max_length=128, exclude=True)
    date_of_birth: CustomDate
    gender: Optional[Gender] = None
    email: EmailStr = Field(...)
    phone: str = Field(..., max_length=50)
    created_at: Optional[AthensDateTime] = None
    updated_at: Optional[AthensDateTime] = None
    # Relationships
    user_bookings: Optional[List[BookingModel]] = None
    user_cancellations: Optional[List[CancellationModel]] = None
    address: Optional[AddressModel] = None

    model_config = default_configs


class UserUpdateModel(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    date_of_birth: Optional[CustomDate] = None
    gender: Optional[Gender] = None

    model_config = default_configs


class EventModel(BaseModel):
    id_: Optional[int] = Field(None, exclude=True)
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    status: EventStatus = EventStatus.ACTIVE
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
    # Relationship
    bookings: Optional[list[BookingModel]] = None

    model_config = default_configs


class BookingModel(BaseModel):
    id_: Optional[int] = Field(None, exclude=True)
    user_id: int
    event_id: int
    unit_price: Decimal = Field(..., max_digits=7, decimal_places=2)
    booking_time: Optional[AthensDateTime] = None
    seats: int
    status: BookingStatus = BookingStatus.ACTIVE
    refund_amount: Decimal = Field(default=Decimal("0.00"), max_digits=7, decimal_places=2)
    created_at: Optional[AthensDateTime] = None
    updated_at: Optional[AthensDateTime] = None

    # Relationships
    cancellation: Optional[CancellationModel] = None
    payment: Optional[PaymentModel] = None

    model_config = default_configs


class PaymentModel(BaseModel):
    id_: Optional[int] = Field(None, exclude=True)
    transaction_id: str = Field(..., max_length=255)
    booking_id: int
    amount_paid: Decimal = Field(..., max_digits=7, decimal_places=2)
    payment_method: PaymentMethod = PaymentMethod.CARD
    payment_time: Optional[AthensDateTime] = None  # Will be filled by DB if not supplied

    created_at: Optional[AthensDateTime] = None
    updated_at: Optional[AthensDateTime] = None

    model_config = default_configs


class CancellationModel(BaseModel):
    id_: Optional[int] = Field(None, exclude=True)
    user_id: int
    booking_id: int

    cancellation_time: Optional[AthensDateTime] = None
    refund_amount: Decimal = Decimal("0.00")
    reason: Optional[str] = Field(None, max_length=255)
    created_at: Optional[AthensDateTime] = None
    updated_at: Optional[AthensDateTime] = None

    model_config = default_configs


class AddressModel(BaseModel):
    id_: Optional[int] = Field(None, exclude=True)
    street: str = Field(..., max_length=100)
    city: str = Field(..., max_length=50)
    postal_code: str = Field(..., max_length=20)
    country: str = Field(..., max_length=50)
    user_id: Optional[int] = Field(default=None, exclude=True)

    model_config = default_configs
