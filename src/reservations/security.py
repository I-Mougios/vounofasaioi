# src/reservations/security.py
from passlib.hash import argon2

def hash_password(password: str) -> str:
    return argon2.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return argon2.verify(plain_password, hashed_password)

if __name__ == "__main__":
    print(len(hash_password("1234")))