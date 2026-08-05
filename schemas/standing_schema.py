from datetime import datetime, timezone
from pydantic import BaseModel


class StandingSchema(BaseModel):
    league_slug: str
    season: int
    group_name: str | None = None
    team_espn_id: int
    team_name: str
    abbreviation: str | None = None
    logo_url: str | None = None
    rank: int | None = None
    games_played: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    goals_for: int = 0
    goals_against: int = 0
    goal_difference: int = 0
    points: int = 0
    deductions: int = 0


class StandingRead(StandingSchema):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LeagueStandingResponse(BaseModel):
    league_slug: str
    group_name: str | None = None
    season: int
    entries: list[StandingRead]
