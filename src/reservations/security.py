# src/reservations/security.py
from datetime import UTC, datetime, timedelta

import jwt
from passlib.hash import argon2

# -------------------------------
# CONFIGURATION VARIABLES
# -------------------------------

# Secret key to sign JWT tokens (store in env vars in production)
SECRET_KEY = "your-very-long-random-secret-key"
# Algorithm used for JWT
ALGORITHM = "HS256"
# Token expiration in minutes
ACCESS_TOKEN_EXPIRE_MINUTES = 6


def hash_password(password: str) -> str:
    return argon2.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return argon2.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """
    Create JWT(Json Web Token) token

    Parameters:
        data (dict): dictionary with user info that used for JWT

    Returns:
        token (str): JWT token
    """
    to_encode = data.copy()
    expire = datetime.now(tz=UTC) + timedelta(seconds=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_access_token(token: str) -> dict:
    """
    Decode a JWT token and return the payload.
    Raises jwt.ExpiredSignatureError or jwt.InvalidTokenError if invalid.
    """
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload


if __name__ == "__main__":
    issubclass(jwt.ExpiredSignatureError, jwt.PyJWTError)
