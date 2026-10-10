from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from models.match import Match


async def seed_upcoming_match(db: AsyncSession) -> Match:
    future_date = datetime.now(UTC) + timedelta(hours=2)
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
async def test_create_and_get_prediction(
    async_client: AsyncClient, db_session: AsyncSession
):
    match = await seed_upcoming_match(db_session)

    await async_client.post(
        "/auth/register",
        json={
            "username": "predictor",
            "email": "pred@example.com",
            "password": "Password123",
        },
    )
    login_res = await async_client.post(
        "/auth/login", data={"username": "pred@example.com", "password": "Password123"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    pred_payload = {
        "match_id": match.id,
        "score_home": 2,
        "score_away": 1,
        "selected_model": "gemini-3.5-flash-lite",
    }
    pred_res = await async_client.post(
        "/predictions", json=pred_payload, headers=headers
    )
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
async def test_duplicate_prediction_forbidden(
    async_client: AsyncClient, db_session: AsyncSession
):
    match = await seed_upcoming_match(db_session)

    await async_client.post(
        "/auth/register",
        json={
            "username": "dup_predictor",
            "email": "dup_pred@example.com",
            "password": "Password123",
        },
    )
    login_res = await async_client.post(
        "/auth/login",
        data={"username": "dup_pred@example.com", "password": "Password123"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    pred_payload = {"match_id": match.id, "score_home": 1, "score_away": 0}

    res1 = await async_client.post("/predictions", json=pred_payload, headers=headers)
    assert res1.status_code == 200

    res2 = await async_client.post("/predictions", json=pred_payload, headers=headers)
    assert res2.status_code == 400


@pytest.mark.asyncio
async def test_create_prediction_match_not_found(async_client: AsyncClient):
    await async_client.post(
        "/auth/register",
        json={
            "username": "not_found_user",
            "email": "not_found@example.com",
            "password": "Password123",
        },
    )
    login_res = await async_client.post(
        "/auth/login",
        data={"username": "not_found@example.com", "password": "Password123"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = await async_client.post(
        "/predictions",
        json={"match_id": 99999999, "score_home": 1, "score_away": 0},
        headers=headers,
    )
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_create_prediction_match_already_started(
    async_client: AsyncClient, db_session: AsyncSession
):
    past_date = datetime.now(UTC) - timedelta(hours=2)
    match = Match(
        league_id=1,
        league_slug="test_league",
        year=2026,
        event_id=888888,
        date=past_date,
        state="post",
        completed=True,
        home_team_id=101,
        home_team_name="Real Madrid",
        away_team_id=102,
        away_team_name="Barcelona",
    )
    db_session.add(match)
    await db_session.commit()
    await db_session.refresh(match)

    await async_client.post(
        "/auth/register",
        json={
            "username": "past_predictor",
            "email": "past_pred@example.com",
            "password": "Password123",
        },
    )
    login_res = await async_client.post(
        "/auth/login",
        data={"username": "past_pred@example.com", "password": "Password123"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = await async_client.post(
        "/predictions",
        json={"match_id": match.id, "score_home": 1, "score_away": 0},
        headers=headers,
    )
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_update_and_delete_prediction_success(
    async_client: AsyncClient, db_session: AsyncSession
):
    match = await seed_upcoming_match(db_session)

    await async_client.post(
        "/auth/register",
        json={
            "username": "crud_predictor",
            "email": "crud_pred@example.com",
            "password": "Password123",
        },
    )
    login_res = await async_client.post(
        "/auth/login",
        data={"username": "crud_pred@example.com", "password": "Password123"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_res = await async_client.post(
        "/predictions",
        json={"match_id": match.id, "score_home": 1, "score_away": 0},
        headers=headers,
    )
    assert create_res.status_code == 200
    prediction_id = create_res.json()["id"]

    patch_res = await async_client.patch(
        f"/predictions/{prediction_id}",
        json={"score_home": 3, "score_away": 2},
        headers=headers,
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["score_home"] == 3
    assert patch_res.json()["score_away"] == 2

    delete_res = await async_client.delete(
        f"/predictions/{prediction_id}", headers=headers
    )
    assert delete_res.status_code == 204
