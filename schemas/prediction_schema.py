from datetime import UTC, datetime

from pydantic import BaseModel, Field, computed_field, model_validator

from app.utils import get_now_utc
from models.prediction import PredictionSource, Result


class PredictionBase(BaseModel):
    match_id: int
    score_home: int = Field(ge=0)
    score_away: int = Field(ge=0)
    predicted_mvp: str | None = None

class PredictionCreateLLM(PredictionBase):
    model_name: str
    model_id: int | None = None

class PredictionCreateUser(PredictionBase):
    selected_model: str | None = None
    model_name: str | None = None

    @model_validator(mode="before")
    def sync_model_fields(cls, values):
        if isinstance(values, dict):
            if not values.get("selected_model") and values.get("model_name"):
                values["selected_model"] = values["model_name"]
        return values

class PredictionRead(PredictionBase):
    id: int
    user_id: int | None = None
    predicted_result: Result
    source: PredictionSource
    model_name: str | None = None
    model_id: int | None = None
    confidence: float | None = None
    locked_at: datetime | None = None
    user_vs_llm_result: str | None = None
    llm_compared_points: int | None = None
    points_awarded: int | None = None
    is_scored: bool = False
    scored_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


    model_config = {"from_attributes": True, "use_enum_values": True}

    @computed_field(return_type=bool)
    @property
    def is_locked(self) -> bool:
        if self.locked_at is None:
            return False
        locked_at = self.locked_at
        if locked_at.tzinfo is None:
            locked_at = locked_at.replace(tzinfo=UTC)
        return locked_at <= get_now_utc()

class PredictionUpdate(BaseModel):
    score_home: int | None = Field(default=None, ge=0)
    score_away: int | None = Field(default=None, ge=0)
    confidence: float | None = None
    predicted_mvp: str | None = None


class PredictionMatchRead(BaseModel):
    league_id: int
    league_name: str | None = None
    league_slug: str
    year: int

    event_id: int
    date: datetime
    state: str
    completed: bool

    home_team_id: int
    home_team_name: str

    home_team_form: str | None = None
    home_team_record: str | None = None
    home_team_logo: str | None = None

    away_team_id: int
    away_team_name: str

    away_team_form: str | None = None
    away_team_record: str | None = None
    away_team_logo: str | None = None

    venue_id: int | None = None
    venue_name: str | None = None

    winner: str | None = None
    home_score: int | None = None
    away_score: int | None = None

    model_config = {
        "from_attributes": True,
    }

class PredictionWithMatchRead(PredictionRead):
    match: PredictionMatchRead


