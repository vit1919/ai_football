from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from models.match import Match
from services.jobs_service import score_predictions


@pytest.mark.asyncio
async def test_full_user_and_prediction_lifecycle(async_client: AsyncClient, db_session: AsyncSession):
    await async_client.post("/auth/register", json={
        "username": "e2e_hero",
        "email": "e2e@test.com",
        "password": "Password123"
    })
    login_res = await async_client.post("/auth/login", data={
        "username": "e2e@test.com",
        "password": "Password123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    match = Match(
        league_id=1, league_slug="e2e_league", year=2026, event_id=555111,
        date=datetime.now(UTC) + timedelta(hours=2),
        state="pre", completed=False,
        home_team_id=1, home_team_name="Real",
        away_team_id=2, away_team_name="Barca"
    )
    db_session.add(match)
    await db_session.commit()

    pred_res = await async_client.post("/predictions", json={
        "match_id": match.id,
        "score_home": 2,
        "score_away": 1
    }, headers=headers)
    assert pred_res.status_code == 200

    match.completed = True
    match.state = "post"
    match.home_score = 2
    match.away_score = 1
    match.winner = "home"
    await db_session.commit()

    score_res = await score_predictions(db_session)
    assert score_res["matches_scored"] == 1

    lb_res = await async_client.get("/leaderboard")
    assert lb_res.status_code == 200
    lb_data = lb_res.json()
    
    hero_stat = next(u for u in lb_data if u["username"] == "e2e_hero")
    assert hero_stat["total_points"] == 6  