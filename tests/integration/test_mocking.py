from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.team import Team
from schemas.team_schema import TeamSchema


@pytest.mark.asyncio
@patch("app.api.routes.teams.get_team_info")
async def test_fallback_team_loading(mock_get_team_info, async_client: AsyncClient, db_session: AsyncSession):
    fake_team = TeamSchema(
        espn_id=999,
        name="Fake Team",
        display_name="Fake Team FC",
        abbreviation="FTFC",
        is_active=True,
    )
    mock_get_team_info.return_value = fake_team

    result = await db_session.execute(select(Team).where(Team.espn_id == 999))
    assert result.scalar_one_or_none() is None

    res = await async_client.get("/teams/eng.1/999")

    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "Fake Team"
    assert data["espn_id"] == 999

    result_after = await db_session.execute(select(Team).where(Team.espn_id == 999))
    saved_team = result_after.scalar_one_or_none()

    assert saved_team is not None
    assert saved_team.name == "Fake Team"

    mock_get_team_info.assert_called_once_with("eng.1", 999)


@pytest.mark.asyncio
@patch("app.api.routes.matches.get_matches_today")
async def test_sync_matches_external_api_error(mock_get_matches, async_client: AsyncClient, db_session: AsyncSession):
    mock_get_matches.side_effect = Exception("ESPN API is down")

    await async_client.post("/auth/register", json={
        "username": "error_tester",
        "email": "error@example.com",
        "password": "Password123"
    })
    login_res = await async_client.post("/auth/login", data={
        "username": "error@example.com",
        "password": "Password123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = await async_client.post("/sync_matches", headers=headers)

    assert res.status_code == 500
    assert "Internal Server Error" in res.text

    mock_get_matches.assert_called_once()
