# src/reservations/dependencies.py
from typing import AsyncGenerator, Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import SessionLocal
from database.schema import AdminORM, UserORM
from reservations.security import decode_access_token


async def open_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


# ======= Authentication =====
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(open_async_session)
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

    result = await session.execute(select(UserORM).filter_by(email=email))
    user: Optional[UserORM] = result.scalars().first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"No user found with email: {email}"
        )

    return user


async def get_current_admin(
    token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(open_async_session)
) -> AdminORM:
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

    result = await session.execute(select(AdminORM).filter_by(email=email))
    admin: Optional[AdminORM] = result.scalar_one_or_none()
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"No admin found with email: {email}"
        )

    return admin
