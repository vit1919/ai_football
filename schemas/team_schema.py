from datetime import datetime

from pydantic import BaseModel


class TeamBase(BaseModel):
    espn_id: int
    uid: str | None = None
    slug: str | None = None

    name: str
    display_name: str | None = None
    short_display_name: str | None = None
    abbreviation: str | None = None
    location: str | None = None
    nickname: str | None = None
    is_active: bool | None = True

    color: str | None = None
    alternate_color: str | None = None
    logo_url: str | None = None
    logo_dark_url: str | None = None
    logo_updated_at: datetime | None = None

    league_id: int | None = None
    league_slug: str | None = None
    league_abbrev: str | None = None
    league_name: str | None = None

    record_summary: str | None = None
    games_played: int | None = None
    wins: int | None = None
    losses: int | None = None
    ties: int | None = None
    points: int | None = None
    rank: int | None = None
    streak: int | None = None
    points_for: int | None = None
    points_against: int | None = None
    point_diff: int | None = None
    standing_summary: str | None = None


class TeamSchema(TeamBase):
    id: int | None = None


    next_event_id: int | None = None
    next_event_date: datetime | None = None
    next_event_name: str | None = None
    next_event_short_name: str | None = None
    next_event_home_away: str | None = None
    next_event_opponent_id: int | None = None
    next_event_opponent_name: str | None = None
    next_event_venue_name: str | None = None
    next_event_city: str | None = None
    next_event_country: str | None = None

    next_event_status_state: str | None = None
    next_event_status_detail: str | None = None

    model_config = {"from_attributes": True}


class TeamRead(TeamSchema):
    
    created_at: datetime
    updated_at: datetime

    


