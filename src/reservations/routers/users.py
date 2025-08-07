from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database.schema import AddressORM, UserORM
from models.schema import UserModel, UserUpdateModel
from reservations.dependencies import open_session

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/",
    response_model=UserModel,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="""
Insert a new user along with their optional address.

- If the address is provided, it will also be saved and linked to the user.
- On success, returns the created user (excluding the password).
- On failure, returns a 500 Internal Server Error.
 
 Constraint Violation:
 - e-mail unique constraint
 - all field apart from gender are required.

Example:

    {
      "first_name": "Maria",\n
      "last_name": "Papadopoulou",\n
      "password": "mN7bV8cX9zQ1",\n
      "date_of_birth": "1992-05-17",\n
      "gender": "F",\n
      "email": "maria@example.com",\n
      "phone": "6901234567",\n
      "address": {\n
        "street": "45 Thessaloniki Ave",\n
        "city": "Thessaloniki",\n
        "postal_code": "54622",\n
        "country": "Greece"\n
      }\n
    }
""",
    responses={
        status.HTTP_201_CREATED: {"description": "User created successfully"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Database error during user insertion"
        },
    },
)
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


@router.patch(
    "/{email}",
    response_model=UserModel,
    summary="Partially update a user by email, including changing email",
    description="""
Update one or more fields of a user.

Notes:
- The password cannot be updated through this endpoint.
- On success, returns the updated user (excluding the password field).

This endpoint may fail in the following cases:
- The provided email in the path parameter does not exist (404 Not Found).
- A new email is provided, but it conflicts with an existing user (409 Conflict).
- A database schema violation occurs during the update operation (500 Internal Server Error).
- The new email is not a valid email address.

Constraint Violations:
- The email field must be unique.
- All fields except for `gender` are required.
        
Example:\n
    {
      "first_name": "Maria",\n
      "last_name": "Papadopoulou",\n
      "date_of_birth": "1992-05-17",\n
      "gender": "F",\n
      "email": "maria@example.com",\n
      "phone": "6901234567"\n
    }
    """,
    responses={
        status.HTTP_200_OK: {"description": "User updated successfully"},
        status.HTTP_404_NOT_FOUND: {"description": "email address does not exist"},
        status.HTTP_409_CONFLICT: {"description": "New email address already exists"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Database error"},
    },
)
def patch_user_by_email(
    email: EmailStr,
    update_data: UserUpdateModel,
    session: Session = Depends(open_session),
):
    old_user_orm = session.query(UserORM).filter_by(email=email).first()
    if not old_user_orm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {email} not found",
        )
    # Check for email change and uniqueness
    new_fields = update_data.model_dump(exclude_unset=True)
    new_email = new_fields.get("email", None)
    if new_email and new_email != email:
        email_exists = session.query(UserORM).filter_by(email=new_email).first()
        if email_exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email {new_email} already exists",
            )
    try:
        for field, value in new_fields.items():
            setattr(old_user_orm, field, value)
            session.flush()
        session.commit()
        return UserModel.model_validate(old_user_orm)

    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user: {str(e)}",
        )


# ============= Endpoints mainly for development assistance ============


@router.get(
    "/",
    response_model=list[UserModel],
    summary="List users",
    description="Returns up to 100 users from the database. Intended for development/debugging.",
)
def list_users(session: Session = Depends(open_session)) -> list[UserModel]:
    users_orm = session.query(UserORM).limit(100).all()
    return users_orm


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete all users",
    description="Permanently deletes all users from the database. Use with caution.",
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "All users deleted successfully"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal database error"},
    },
)
def delete_all_users(session: Session = Depends(open_session)) -> None:
    try:
        session.query(UserORM).delete()
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting users: {str(e)}",
        )
