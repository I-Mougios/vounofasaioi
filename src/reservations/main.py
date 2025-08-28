# src/reservations/main.py
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database.schema import AdminORM, UserORM
from models.responses import TokenResponse

from .dependencies import open_session
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
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(open_session)
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
    user: Optional[UserORM] = session.query(UserORM).filter_by(email=form_data.username).first()
    if not user:
        admin: Optional[AdminORM] = (
            session.query(AdminORM).filter_by(email=form_data.username).first()
        )
        user = admin if admin else None

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    # Create JWT
    access_token = create_access_token(data={"sub": user.email})

    return TokenResponse(access_token=access_token, token_type="bearer")
