import pytest  # noqa: F401
from icecream import ic
from sqlalchemy.orm import Session

from database.engine import engine
from database.schema import UserORM
from models.schema import UserModel


def test_add_users(users):
    user_models = (UserModel.model_validate(user) for user in users)
    with Session(engine, expire_on_commit=True, autoflush=False) as session:
        session.add_all((UserORM.from_attributes(user_model) for user_model in user_models))
        session.flush()

        result = list(session.query(UserORM).all())
        ic(result)
        assert len(result) == len(users)
