# src/reservations/routers/__init__.py

from .users import router as users_router

routers = [users_router]

__all__ = ["users_router", "routers"]
