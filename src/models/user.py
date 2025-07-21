from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import date

from .custom_types import AthensDateTime


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id_: int | None = Field(alias="id", default=None)
    first_name: str
    last_name: str
    password: str
    date_of_birth: date
    email: EmailStr
    phone: str
    created_at: AthensDateTime
    updated_at: AthensDateTime
