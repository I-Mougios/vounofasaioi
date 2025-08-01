from fastapi import APIRouter, Depends

from backend.dependencies import open_session
from database.schema import UserORM
from models.schema import UserModel

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserModel])
def users(session=Depends(open_session)):
    users_orm = session.query(UserORM).limit(100).all()
    return users_orm


@router.post("/", response_model=UserModel)
def insert_user(user: UserModel, session=Depends(open_session)):
    orm_user = UserORM.from_attributes(user, include=["password"])
    session.add(orm_user)
    session.commit()
    return user
