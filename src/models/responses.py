# src/models/responses.py
from typing import Optional

from pydantic import BaseModel, ConfigDict

from models.schema import UserModel

default_config = ConfigDict(
    from_attributes=True, serialize_by_alias=True, str_strip_whitespace=True
)


class TokenResponse(BaseModel):

    access_token: str
    token_type: str = "bearer"
    user: Optional[UserModel] = None

    model_config = default_config
