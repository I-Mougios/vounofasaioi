# src/reservations/routers/admins.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database.schema import AdminORM
from models.responses import TokenResponse
from models.schema import AdminModel
from reservations.dependencies import open_session
from reservations.security import create_access_token, hash_password

router = APIRouter(prefix="/admins", tags=["admins"])


@router.post(
    "/register",
    response_description="JWT token, token type and admin record from database",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new admin (development purposes only)",
    responses={
        status.HTTP_201_CREATED: {"description": "Admin created successfully"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Database error during user insertion"
        },
        status.HTTP_400_BAD_REQUEST: {"description": "Admin already exists"},
    },
    description="""
Example:
    
    {
     "first_name": "ioannis",\n
     "last_name": "mougios",\n
     "email": "i.mougios.tech@gmail.com",\n
     "password": "password"\n
    }
             """,
)
def register(admin: AdminModel, session: Session = Depends(open_session)) -> TokenResponse:
    existing_admin = session.query(AdminORM).filter_by(email=admin.email).first()
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email '{admin.email}' already exists.",
        )
    try:
        admin_orm = AdminORM.from_attributes(admin, include=["password"]).cast(
            attr="password", callable=hash_password
        )
        session.add(admin_orm)
        session.flush()
        session.commit()

        token = create_access_token({"sub": admin_orm.email})

    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error during admin insertion: {str(e)}",
        )

    return TokenResponse(
        access_token=token, token_type="bearer", admin=AdminModel.model_validate(admin_orm)
    )
