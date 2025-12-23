# src/reservations/routers/users.py
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse
from pydantic import EmailStr
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database.schema import AddressORM, UserORM
from models.responses import TokenResponse
from models.schema import UserModel
from models.users import UserLogin, UserUpdateModel
from reservations.dependencies import get_current_user, open_session
from reservations.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/login",
    response_description="JWT access token, token type and the user record from the database",
    summary="Login with email and password (Json-compatible)",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Incorrect email or password"},
        status.HTTP_200_OK: {"description": "User successfully logged in and get the JWT"},
    },
    description="""
 Login with email and password (Json-compatible)
 
 Example:
 
    {
      "email": "maria@example.com",\n
      "password": "mN7bV8cX9zQ1"
    }
""",
)
def login(user: UserLogin, session: Session = Depends(open_session)):
    user_orm = session.query(UserORM).filter_by(email=user.email).first()
    if not user_orm or not verify_password(user.password, user_orm.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password"
        )

    token = create_access_token(data={"sub": user_orm.email})
    return TokenResponse(
        access_token=token, token_type="bearer", user=UserModel.model_validate(user_orm)
    )


@router.post(
    "/register",
    response_model=TokenResponse,
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
        status.HTTP_400_BAD_REQUEST: {"description": "User with email already exists"},
    },
)
def register(user: UserModel, session=Depends(open_session)) -> TokenResponse:
    # Check if email exists
    existing_user = session.query(UserORM).filter_by(email=user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email '{user.email}' already exists.",
        )
    try:
        user_orm = UserORM.from_attributes(user, include=["password"]).cast(
            attr="password", callable=hash_password
        )
        session.add(user_orm)
        session.flush()  # get user_orm.id

        if user.address:
            address_orm = AddressORM.from_attributes(user.address)
            address_orm.user_id = user_orm.id
            session.add(address_orm)
            session.flush()

        session.commit()
        # Step 4: Generate JWT token
        token = create_access_token({"sub": user_orm.email})

    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error during user insertion: {str(e)}",
        )

    return TokenResponse(
        access_token=token, token_type="bearer", user=UserModel.model_validate(user_orm)
    )


@router.patch(
    "/update_current_user",
    response_model=TokenResponse,
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
      "email": "maria_new_email@example.com",\n
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
def update_current_user(
    update_data: UserUpdateModel,
    current_user: UserORM = Depends(get_current_user),
    session: Session = Depends(open_session),
):
    # Check for email change and uniqueness
    new_fields = update_data.model_dump(exclude_unset=True)
    new_email = new_fields.get("email", None)
    if new_email and new_email != current_user.email:
        email_exists = session.query(UserORM).filter_by(email=new_email).first()
        if email_exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email {new_email} already exists",
            )
    try:
        for field, value in new_fields.items():
            setattr(current_user, field, value)

        session.commit()
        session.refresh(current_user)

        token = create_access_token({"sub": current_user.email})
        return TokenResponse(
            access_token=token, token_type="bearer", user=UserModel.model_validate(current_user)
        )

    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user: {str(e)}",
        )


@router.delete(
    "/delete_me",
    summary="Delete a user by email",
    description="Only authenticated users can delete their own account",
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "User deleted successfully"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Database error"},
    },
)
def delete_me(
    current_user: UserORM = Depends(get_current_user), session: Session = Depends(open_session)
):
    try:
        session.delete(current_user)
        session.commit()
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to delete user: {str(e)}",
        )

    return PlainTextResponse(
        f"User with email {current_user.email} deleted successfully",
        status_code=status.HTTP_204_NO_CONTENT,
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
    return [UserModel.model_validate(user) for user in users_orm]


@router.delete(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Delete all users",
    description="Permanently deletes all users from the database. Use with caution.",
    responses={
        status.HTTP_200_OK: {
            "description": "All users deleted successfully",
            "content": {"text/plain": {"example": "2 users deleted successfully"}},
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal database error"},
    },
)
def delete_all_users(session: Session = Depends(open_session)) -> PlainTextResponse:
    try:
        delete_count = session.query(UserORM).delete()
        session.commit()
        return PlainTextResponse(content=f"{delete_count} users deleted successfully")
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting users: {str(e)}",
        )


# ===================== Common Functionalities about users ===========
def get_user_by_email(email: EmailStr, session: Session = Depends(open_session)) -> UserORM:
    user: Optional[UserORM] = session.query(UserORM).filter_by(email=email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {email} not found",
        )
    return user
