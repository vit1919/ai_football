from datetime import datetime, timedelta, timezone
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from models.match import Match


async def seed_upcoming_match(db: AsyncSession) -> Match:
    future_date = datetime.now(timezone.utc) + timedelta(hours=2)
    match = Match(
        league_id=1,
        league_slug="test_league",
        year=2026,
        event_id=999999,
        date=future_date,
        state="pre",
        completed=False,
        home_team_id=101,
        home_team_name="Real Madrid",
        away_team_id=102,
        away_team_name="Barcelona",
    )
    db.add(match)
    await db.commit()
    await db.refresh(match)
    return match


@pytest.mark.asyncio
async def test_create_and_get_prediction(async_client: AsyncClient, db_session: AsyncSession):
    match = await seed_upcoming_match(db_session)

    await async_client.post("/auth/register", json={
        "username": "predictor",
        "email": "pred@example.com",
        "password": "Password123"
    })
    login_res = await async_client.post("/auth/login", data={
        "username": "pred@example.com",
        "password": "Password123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    pred_payload = {
        "match_id": match.id,
        "score_home": 2,
        "score_away": 1,
        "selected_model": "gemini-3.5-flash-lite"
    }
    pred_res = await async_client.post("/predictions", json=pred_payload, headers=headers)
    assert pred_res.status_code == 200
    pred_data = pred_res.json()
    assert pred_data["score_home"] == 2
    assert pred_data["score_away"] == 1
    assert pred_data["predicted_result"] == "home_win"

    me_preds_res = await async_client.get("/predictions/me", headers=headers)
    assert me_preds_res.status_code == 200
    me_preds_data = me_preds_res.json()
    
    assert len(me_preds_data) == 1
    assert me_preds_data[0]["match"]["home_team_name"] == "Real Madrid"
    assert me_preds_data[0]["match"]["away_team_name"] == "Barcelona"


@pytest.mark.asyncio
async def test_duplicate_prediction_forbidden(async_client: AsyncClient, db_session: AsyncSession):
    match = await seed_upcoming_match(db_session)

    await async_client.post("/auth/register", json={
        "username": "dup_predictor",
        "email": "dup_pred@example.com",
        "password": "Password123"
    })
    login_res = await async_client.post("/auth/login", data={
        "username": "dup_pred@example.com",
        "password": "Password123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    pred_payload = {
        "match_id": match.id,
        "score_home": 1,
        "score_away": 0
    }

    res1 = await async_client.post("/predictions", json=pred_payload, headers=headers)
    assert res1.status_code == 200

    res2 = await async_client.post("/predictions", json=pred_payload, headers=headers)
    assert res2.status_code == 400