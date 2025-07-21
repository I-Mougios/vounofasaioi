from datetime import datetime, UTC
from zoneinfo import ZoneInfo
from typing import Annotated

from dateutil import parser
from pydantic import BeforeValidator, AfterValidator


def parse_datetime(value: str | datetime) -> datetime:
    if isinstance(value, str):
        try:
            return parser.parse(value, dayfirst=True)
        except Exception as ex:
            raise ValueError(ex)
    return value


def to_athens_zoneinfo(dt: datetime) -> datetime:
    # If datetime is naive, assume that the timezone if UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)

    athens_dt = dt.astimezone(ZoneInfo("Europe/Athens"))
    return athens_dt


AthensDateTime = Annotated[
    datetime, BeforeValidator(parse_datetime), AfterValidator(to_athens_zoneinfo)
]
