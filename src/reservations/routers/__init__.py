# src/reservations/routers/__init__.py

from .admins import router as admins_router
from .users import router as users_router

routers = [users_router, admins_router]

__all__ = ["users_router", "admins_router", "routers"]
