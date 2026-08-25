import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User


@pytest.mark.asyncio
async def test_leaderboard_sorting(async_client: AsyncClient, db_session: AsyncSession):
    u1 = User(username="user_top", email="top@test.com", hashed_password="pass", total_points=15)
    u2 = User(username="user_mid", email="mid@test.com", hashed_password="pass", total_points=8)
    u3 = User(username="user_low", email="low@test.com", hashed_password="pass", total_points=2)

    db_session.add_all([u1, u2, u3])
    await db_session.commit()

    response = await async_client.get("/leaderboard")
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 3
    assert data[0]["username"] == "user_top"
    assert data[0]["total_points"] == 15
    assert data[0]["rank"] == 1

    assert data[1]["username"] == "user_mid"
    assert data[1]["rank"] == 2

    assert data[2]["username"] == "user_low"
    assert data[2]["rank"] == 3