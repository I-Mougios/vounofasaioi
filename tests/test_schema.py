# tests/test_schema.py
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from database.engine import engine
from database.schema import AddressORM, UserORM
from models.schema import AddressModel, UserModel
from src.enumerations import Gender


def test_basic_fields_validation(users):
    user1, _ = users
    m1 = UserModel.model_validate(user1)
    assert isinstance(m1.date_of_birth, date)
    assert m1.date_of_birth == date(1992, 5, 17)
    assert isinstance(m1.address, AddressModel)
    assert m1.address.city == "Thessaloniki"
    assert m1.gender == Gender.FEMALE
    assert m1.gender.value == "F"
    assert isinstance(m1.gender, Gender)


def test_enum_and_custom_date_assignment(users):
    user1, _ = users
    m1 = UserModel.model_validate(user1)
    m1.gender = "F"
    m1.date_of_birth = "July 27, 1995"
    assert m1.date_of_birth.year == 1995
    assert m1.date_of_birth.month == 7


def test_dayfirst_date_parsing(users):
    user1, _ = users
    m1 = UserModel.model_validate(user1)
    m1.date_of_birth = "07/06/1995"  # dd/mm/yyyy
    assert m1.date_of_birth.day == 7


def test_athens_datetime_conversion_from_naive(users):
    user1, _ = users
    m1 = UserModel.model_validate(user1)
    naive_now = datetime.now()
    m1.updated_at = naive_now
    assert m1.updated_at.tzinfo == ZoneInfo("Europe/Athens")
    assert m1.updated_at.hour == (naive_now + timedelta(hours=3)).hour


def test_athens_datetime_accepts_aware_datetime(users):
    user1, _ = users
    m1 = UserModel.model_validate(user1)
    aware_now = datetime.now(tz=ZoneInfo("Europe/Athens"))
    m1.updated_at = aware_now
    assert m1.updated_at.hour == aware_now.hour


def test_str_str_whitespace_strip(users):
    user1, _ = users
    m1 = UserModel.model_validate(user1)
    m1.first_name = " John\t"
    assert m1.first_name == "John"


# ==========Test Database schema and relationships========


def test_add_addresses_via_users(users):
    user1, user2 = users
    m1 = UserModel.model_validate(user1)
    m2 = UserModel.model_validate(user2)
    # Create the ORMs instances from Pydantic Models
    u1 = UserORM.from_attributes(m1)
    u2 = UserORM.from_attributes(m2)
    a1 = AddressORM.from_attributes(m1.address)
    a2 = AddressORM.from_attributes(m2.address)

    # Insert addresses via the user
    with Session(bind=engine) as session:
        u1.address = a1
        u2.address = a2
        session.add(u1)
        session.add(u2)
        session.flush()
        now = datetime.now()
        addresses = list(session.query(AddressORM).all())
        assert len(addresses) == 2
        assert addresses[0].city == m1.address.city
        assert u1.created_at.minute == now.minute


def test_add_users_via_addresses(users):
    user1, user2 = users
    m1 = UserModel.model_validate(user1)
    m2 = UserModel.model_validate(user2)
    # Create the ORMs instances from Pydantic Models
    u1 = UserORM.from_attributes(m1)
    u2 = UserORM.from_attributes(m2)
    a1 = AddressORM.from_attributes(m1.address)
    a2 = AddressORM.from_attributes(m2.address)
    # Let's insert the users through the addresses instances
    with Session(bind=engine) as session:
        a1.user = u1
        a2.user = u2
        session.add(a1)
        session.add(a2)
        session.flush()
        users_result = list(session.query(UserORM).all())
        assert len(users_result) == 2
        assert users_result[0].first_name == m1.first_name


def test_users_address_on_delete_cascade(users):
    user1, user2 = users
    m1 = UserModel.model_validate(user1)
    m2 = UserModel.model_validate(user2)
    # Create the ORMs instances from Pydantic Models
    u1 = UserORM.from_attributes(m1)
    u2 = UserORM.from_attributes(m2)
    a1 = AddressORM.from_attributes(m1.address)
    a2 = AddressORM.from_attributes(m2.address)
    # Let's insert the users through the addresses instances
    # Insert addresses via the user
    with Session(bind=engine, expire_on_commit=True) as session:
        u1.address = a1
        u2.address = a2
        session.add(u1)
        session.add(u2)
        session.commit()

        session.delete(u1)  # it executes before deletion select statement due to expire on commit
        result = list(session.query(AddressORM).all())
        assert len(result) == 1
        session.delete(u2)
        session.commit()
