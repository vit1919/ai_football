import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_user_success(async_client: AsyncClient):
    payload = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "Password123"
    }
    response = await async_client.post("/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "id" in data

@pytest.mark.asyncio
async def test_register_duplicate_user(async_client: AsyncClient):
    payload = {
        "username": "dupuser",
        "email": "dup@example.com",
        "password": "Password123"
    }
    res1 = await async_client.post("/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = await async_client.post("/auth/register", json=payload)
    assert res2.status_code == 400


@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient):
    await async_client.post("/auth/register", json={
        "username": "loginuser",
        "email": "login@example.com",
        "password": "Password123"
    })

    login_data = {
        "username": "login@example.com", 
        "password": "Password123"
    }
    response = await async_client.post("/auth/login", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_get_me_authorized(async_client: AsyncClient):

    await async_client.post("/auth/register", json={
        "username": "meuser",
        "email": "me@example.com",
        "password": "Password123"
    })

    login_res = await async_client.post("/auth/login", data={
        "username": "me@example.com",
        "password": "Password123"
    })
    token = login_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    me_res = await async_client.get("/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["username"] == "meuser"

@pytest.mark.asyncio
async def test_get_me_unauthorized(async_client: AsyncClient):
    response = await async_client.get("/auth/me")
    assert response.status_code == 401