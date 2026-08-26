from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.limiter import limiter
from models.match import Match


@pytest.fixture(autouse=True)
def manage_limiter_state():
    limiter.enabled = True
    limiter.reset()
    yield
    limiter.reset()
    limiter.enabled = False


@pytest.mark.asyncio
async def test_auth_login_rate_limit(async_client: AsyncClient):
    login_data = {
        "username": "ratelimit_login@test.com",
        "password": "Password123",
    }

    for _ in range(5):
        res = await async_client.post("/auth/login", data=login_data)
        assert res.status_code != 429

    blocked_res = await async_client.post("/auth/login", data=login_data)
    assert blocked_res.status_code == 429
    assert "Rate limit exceeded" in blocked_res.text


@pytest.mark.asyncio
async def test_auth_register_rate_limit(async_client: AsyncClient):
    for i in range(10):
        res = await async_client.post(
            "/auth/register",
            json={
                "username": f"user_limit_{i}",
                "email": f"limit_{i}@test.com",
                "password": "Password123",
            },
        )
        assert res.status_code != 429

    blocked_res = await async_client.post(
        "/auth/register",
        json={
            "username": "user_limit_blocked",
            "email": "blocked@test.com",
            "password": "Password123",
        },
    )
    assert blocked_res.status_code == 429


@pytest.mark.asyncio
async def test_predictions_create_rate_limit(
    async_client: AsyncClient, db_session: AsyncSession
):
    await async_client.post(
        "/auth/register",
        json={
            "username": "pred_limiter_user",
            "email": "pred_limit@test.com",
            "password": "Password123",
        },
    )
    login_res = await async_client.post(
        "/auth/login",
        data={"username": "pred_limit@test.com", "password": "Password123"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    match = Match(
        league_id=1,
        league_slug="test_league",
        year=2026,
        event_id=991199,
        date=datetime.now(UTC) + timedelta(hours=3),
        state="pre",
        completed=False,
        home_team_id=1,
        home_team_name="Team A",
        away_team_id=2,
        away_team_name="Team B",
    )
    db_session.add(match)
    await db_session.commit()
    await db_session.refresh(match)

    payload = {
        "match_id": match.id,
        "score_home": 1,
        "score_away": 0,
    }

    for _ in range(20):
        res = await async_client.post("/predictions", json=payload, headers=headers)
        assert res.status_code != 429

    blocked_res = await async_client.post("/predictions", json=payload, headers=headers)
    assert blocked_res.status_code == 429


@pytest.mark.asyncio
@patch("services.ai_prediction_service.call_llm")
async def test_llm_generation_rate_limit(
    mock_call_llm, async_client: AsyncClient, db_session: AsyncSession
):
    mock_call_llm.return_value = {
        "score_home": 2,
        "score_away": 1,
        "confidence": 0.8,
    }

    await async_client.post(
        "/auth/register",
        json={
            "username": "llm_limit_user",
            "email": "llm_limit@test.com",
            "password": "Password123",
        },
    )
    login_res = await async_client.post(
        "/auth/login",
        data={"username": "llm_limit@test.com", "password": "Password123"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    for _ in range(10):
        res = await async_client.post("/llm/generate/999999", headers=headers)
        assert res.status_code != 429

    blocked_res = await async_client.post("/llm/generate/999999", headers=headers)
    assert blocked_res.status_code == 429
