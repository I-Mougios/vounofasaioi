from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from backend.dependencies import open_session
from database.schema import AddressORM, UserORM
from models.schema import UserModel

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserModel])
def users(session=Depends(open_session)):
    users_orm = session.query(UserORM).limit(100).all()
    return users_orm


@router.post("/", response_model=UserModel)
def insert_user(user: UserModel, session=Depends(open_session)):
    try:
        user_orm = UserORM.from_attributes(user, include=["password"])
        session.add(user_orm)
        session.flush()  # get user_orm.id

        if user.address:
            address_orm = AddressORM.from_attributes(user.address)
            address_orm.user_id = user_orm.id_
            session.add(address_orm)
            session.flush()

        session.commit()

    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error during user insertion: {str(e)}",
        )

    return UserModel.model_validate(user_orm)
