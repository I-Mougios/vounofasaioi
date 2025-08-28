# src/reservations/dependencies.py
from typing import Generator, Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, sessionmaker

from database.engine import engine
from database.schema import AdminORM, UserORM
from reservations.security import decode_access_token

# ======= Database ===========
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=True)


def open_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


# ======= Authentication =====
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), session: Session = Depends(open_session)
) -> UserORM:
    """
    Dependency that extracts and validates the current user from a JWT access token.

    Steps:
        1. Reads the JWT token from the `Authorization: Bearer <token>` header.
        2. Decodes the token and extracts the `sub` claim (expected to be the user's email).
        3. Queries the database for a user with the given email.
        4. Returns the user object if found.

    Raises:
        HTTPException (401):
            - If the token is missing, invalid, or expired.
            - If the `sub` claim is missing from the payload.
            - If no user exists with the decoded email.

    Returns:
        UserORM: The authenticated user record from the database.
    """
    try:
        payload = decode_access_token(token)
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: missing subject"
            )
    except jwt.PyJWTError as ex:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token error: {str(ex)}"
        )

    user: Optional[UserORM] = session.query(UserORM).filter_by(email=email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"No user found with email: {email}"
        )

    return user


def get_current_admin(
    token: str = Depends(oauth2_scheme), session: Session = Depends(open_session)
) -> UserORM:
    """
    Dependency that extracts and validates the current admin from a JWT access token.

    Steps:
        1. Reads the JWT token from the `Authorization: Bearer <token>` header.
        2. Decodes the token and extracts the `sub` claim (expected to be the user's email).
        3. Queries the database for a user with the given email.
        4. Returns the user object if found.

    Raises:
        HTTPException (401):
            - If the token is missing, invalid, or expired.
            - If the `sub` claim is missing from the payload.
            - If no user exists with the decoded email.

    Returns:
        UserORM: The authenticated user record from the database.
    """
    try:
        payload = decode_access_token(token)
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: missing subject"
            )
    except jwt.PyJWTError as ex:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token error: {str(ex)}"
        )

    admin: Optional[AdminORM] = session.query(AdminORM).filter_by(email=email).first()
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"No admin found with email: {email}"
        )

    return admin
