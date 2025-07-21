from datetime import UTC, date, datetime
from typing import Annotated
from zoneinfo import ZoneInfo

from dateutil import parser
from pydantic import AfterValidator, BeforeValidator


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


def to_date(datetime: datetime) -> date:
    return datetime.date()


AthensDateTime = Annotated[
    datetime, BeforeValidator(parse_datetime), AfterValidator(to_athens_zoneinfo)
]

CustomDate = Annotated[date, BeforeValidator(parse_datetime)]
