# tests/test_schema.py
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from models.schema import AddressModel, UserModel
from src.enumerations import Gender


def test_model_configs(users):
    user1, user2 = users
    m1 = UserModel.model_validate(user1)
    # Basic field-testing
    assert isinstance(m1.date_of_birth, date) and m1.date_of_birth == date(1992, 5, 17)
    assert isinstance(m1.address, AddressModel) and m1.address.city == "Thessaloniki"
    assert m1.gender.value == "F" and m1.gender == Gender.FEMALE and isinstance(m1.gender, Gender)
    #  Validate assignments active
    m1.gender = "F"  # Check enum
    m1.date_of_birth = "July 27, 1995"  # Check Custom Date
    assert m1.date_of_birth.year == 1995 and m1.date_of_birth.month == 7
    # check dayfirst=True
    m1.date_of_birth = "07/06/1995"
    assert m1.date_of_birth.day == 7
    # Check AthensDateTime
    naive_now = datetime.now()
    m1.updated_at = datetime.now()
    assert m1.updated_at.tzinfo == ZoneInfo("Europe/Athens")
    assert (
        m1.updated_at.hour == (naive_now + timedelta(hours=3)).hour
    )  # It turns naive date to UTC and then add 3 hours
    aware_now = datetime.now(tz=ZoneInfo("Europe/Athens"))
    m1.updated_at = aware_now  # Nothing to do actually
    assert m1.updated_at.hour == aware_now.hour
    # Check str_str_whitespaces
    m1.first_name = " John\t"
    assert m1.first_name == "John"
