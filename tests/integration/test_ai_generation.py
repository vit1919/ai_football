from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from models.match import Match
from models.prediction import PredictionSource
from services.ai_prediction_service import generate_for_upcoming_matches


@pytest.mark.asyncio
@patch("services.ai_prediction_service.call_llm")
async def test_generate_ai_predictions_job_success(mock_call_llm, db_session: AsyncSession):
    mock_call_llm.return_value = {
        "score_home": 2,
        "score_away": 0,
        "confidence": 0.85,
        "reasoning": "Home team in great form"
    }

    upcoming_match = Match(
        league_id=1,
        league_slug="test_league",
        year=2026,
        event_id=777111,
        date=datetime.now(UTC) + timedelta(minutes=10),
        state="pre",
        completed=False,
        home_team_id=1,
        home_team_name="Home FC",
        away_team_id=2,
        away_team_name="Away FC",
    )
    db_session.add(upcoming_match)
    await db_session.commit()

    predictions = await generate_for_upcoming_matches(db_session, model_name="gemini-3.5-flash-lite")

    assert len(predictions) == 1
    assert predictions[0].score_home == 2
    assert predictions[0].score_away == 0
    assert predictions[0].source == PredictionSource.LLM
    assert predictions[0].model_name == "gemini-3.5-flash-lite"

    mock_call_llm.assert_called_once()



#тест ручного роута
@pytest.mark.asyncio
@patch("services.ai_prediction_service.call_llm")
async def test_generate_ai_prediction_manual_api(mock_call_llm, async_client: AsyncClient, db_session: AsyncSession):
    mock_call_llm.return_value = {
        "score_home": 1,
        "score_away": 1,
        "confidence": 0.70
    }

    match = Match(
        league_id=1,
        league_slug="test_league",
        year=2026,
        event_id=777222,
        date=datetime.now(UTC) + timedelta(hours=5),
        state="pre",
        completed=False,
        home_team_id=1,
        home_team_name="Team A",
        away_team_id=2,
        away_team_name="Team B",
    )
    db_session.add(match)
    await db_session.commit()

    await async_client.post("/auth/register", json={
        "username": "llm_tester",
        "email": "llm@test.com",
        "password": "Password123"
    })
    login_res = await async_client.post("/auth/login", data={
        "username": "llm@test.com",
        "password": "Password123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = await async_client.post(f"/llm/generate/{match.event_id}", headers=headers)

    assert res.status_code == 200
    data = res.json()
    assert data["score_home"] == 1
    assert data["score_away"] == 1
    assert data["predicted_result"] == "draw"
