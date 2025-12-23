from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from reservations.main import app
from database.engine import engine


@pytest.fixture(scope="function")
def user_one():
    return {
        "first_name": "Maria",
        "last_name": "Papadopoulou",
        "password": "mN7bV8cX9zQ1",
        "date_of_birth": "1992-05-17",
        "gender": "F",
        "email": "maria@example.com",
        "phone": "6901234567",
        "address": {
            "street": "45 Thessaloniki Ave",
            "city": "Thessaloniki",
            "postal_code": "54622",
            "country": "Greece",
        },
    }


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    client = AsyncClient(base_url="http://test", transport=transport)
    try:
        yield client
    finally:
        await client.aclose()
        await engine.dispose()


@pytest.mark.asyncio
async def test_healthcheck(client):
    response = await client.get("/")
    assert response.json() == {"message": "Welcome to Vounofasaious"}


@pytest.mark.asyncio
async def test_insert_and_delete_user(client, user_one):
    response = await client.post("users/register", json=user_one)

    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    access_token = data["access_token"]

    response = await client.delete(
        "/users/delete_me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 204
    assert response.text == f"User with email {user_one["email"]} deleted successfully"


@pytest.mark.asyncio
async def test_insert_existing_user_raise_error(client, user_one):
    response = await client.post(
        "users/register",
        json=user_one,
    )
    data = response.json()

    user_one_copy = user_one.copy()
    user_one_copy["password"] = "<PASSWORD>"
    user_one_copy["first_name"] = "<FIRST_NAME>"
    response = await client.post("users/register", json=user_one_copy)
    assert response.status_code == 400
    assert response.json()["detail"] == f"User with email '{user_one["email"]}' already exists."

    access_token = data["access_token"]

    await client.delete("/users/delete_me", headers={"Authorization": f"Bearer {access_token}"})
