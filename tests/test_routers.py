from urllib.parse import quote

import pytest
import pytest_asyncio


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


@pytest_asyncio.fixture(scope="function")
async def admin_token(client):
    email = "i.mougios.tech@gmail.com"
    # Try to get existing admin token
    response = await client.post(
        "/login",
        data={
            "username": "i.mougios.tech@gmail.com",
            "password": "password",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if response.status_code == 200:
        return response.json()["access_token"]

    # Admin does not exist → register
    response = await client.post(
        "/admins/register",
        json={
            "first_name": "ioannis",
            "last_name": "mougios",
            "email": email,
            "password": "password",
        },
    )

    assert response.status_code == 201
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def event_one(events):
    return events[0]


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


@pytest.mark.asyncio
async def test_insert_event(client, admin_token, event_one):
    response = await client.post(
        "/events/register", headers={"Authorization": f"Bearer {admin_token}"}, json=event_one
    )
    assert response.status_code == 201
    event_name = response.json()["name"]
    event_name_encoded = quote(event_name)

    response = await client.delete(
        f"/events/delete?event_name={event_name_encoded}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 204
