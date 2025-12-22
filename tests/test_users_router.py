from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from reservations.main import app


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    try:
        yield client
    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_healthcheck(client):
    response = await client.get("http://localhost:8000")
    assert response.json() == {"message": "Welcome to Vounofasaious"}


@pytest.mark.asyncio
async def test_insert_user(client):
    response = await client.post(
        "users/register",
        json={
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
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
