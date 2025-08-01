# tests/test_users.py
import pytest
from icecream import ic
from sqlalchemy.exc import IntegrityError

from database.engine import DBConfig
from database.schema import AddressORM, UserORM

if DBConfig.globals.get("icecream_enabled", False):
    ic.enable()
else:
    ic.disable()


def test_insert_users_with_id_provided(session, users_orm):
    session.add_all(users_orm)
    session.flush()
    assert users_orm.pop(0).id == 1
    assert users_orm.pop(0).id == 2


def test_insert_users_autoincrement_id(session, users_models):
    users_orm = [UserORM.from_attributes(model, include=["password"]) for model in users_models]
    session.add_all(users_orm)
    session.flush()
    user1 = users_orm.pop(0)
    user2 = users_orm.pop(0)
    assert user1.id == user2.id - 1


def test_user_address_persistence(session, users_with_address_orm):
    session.add_all(users_with_address_orm)
    session.flush()
    first_user = users_with_address_orm.pop(0)
    user = session.get(UserORM, {"id_": first_user.id_})
    assert user.address is not None
    assert user.address.city == "Thessaloniki"


def test_address_inserted_via_user(session, users_with_address_orm):
    session.add_all(users_with_address_orm)
    session.flush()
    assert session.query(AddressORM).count() == session.query(UserORM).count()


def test_user_cascades_delete_to_address(session, users_with_address_orm):
    session.add_all(users_with_address_orm)
    session.flush()
    session.delete(users_with_address_orm[0])
    session.flush()

    assert session.query(AddressORM).count() == session.query(UserORM).count()


def test_update_user_address(session, users_with_address_orm):
    session.add_all(users_with_address_orm)
    session.flush()

    user = users_with_address_orm[0]
    user.address.city = "Patras"
    session.flush()

    refreshed_user = session.get(UserORM, user.id_)
    assert refreshed_user.address.city == "Patras"


def test_add_address_without_user_constraint(session, addresses_orm):
    with pytest.raises(IntegrityError):
        session.add_all(addresses_orm)
        session.flush()


def test_address_unique_constraint(session, users_with_address_orm, addresses_orm, users_orm):
    session.add_all(users_with_address_orm)
    session.flush()

    user = users_orm.pop(0)
    address = addresses_orm.pop(-1)
    inserted_user = users_with_address_orm.pop(0)
    assert user.id == inserted_user.id_
    assert inserted_user.address.city is not None
    assert inserted_user.address.id != address.id_
    # attach a different address to user whose address is not None
    with pytest.raises(IntegrityError):
        address.user_id = user.id
        session.add(address)
        session.flush()
