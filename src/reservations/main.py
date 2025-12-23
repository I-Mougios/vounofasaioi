# src/reservations/main.py
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.schema import AdminORM, UserORM
from models.responses import TokenResponse

from .dependencies import open_async_session
from .routers import routers
from .security import create_access_token, verify_password

app = FastAPI()

for router in routers:
    app.include_router(router)


@app.get("/")
def root():
    return {"message": "Welcome to Vounofasaious"}


@app.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email and password (Swagger-compatible)",
    response_description="JWT access token, token type and the user record from the database",
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(open_async_session),
):
    """
    Authenticate a user using **email and password**.

    - **username**: email address of the user (sent as form field)
    - **password**: user password (sent as form field)

    This endpoint is designed to work with Swagger's **Authorize** button and the
    `OAuth2PasswordBearer` security scheme.
    On success, it returns a JWT token that must be included in the
    `Authorization: Bearer <token>` header for accessing protected endpoints.

    Raises:
    - **401 Unauthorized** if the email does not exist or the password is invalid.
    """

    # Swagger sends `username`, we treat it as `email`
    result: Optional[UserORM] = await session.execute(
        select(UserORM).filter_by(email=form_data.username)
    )
    user: Optional[UserORM] = result.scalar_one_or_none()
    if not user:
        result: Optional[AdminORM] = await session.execute(
            select(AdminORM).filter_by(email=form_data.username)
        )
        admin = result.scalar_one_or_none()
        user = admin if admin else None

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    # Create JWT
    access_token = create_access_token(data={"sub": user.email})

    return TokenResponse(access_token=access_token, token_type="bearer")
