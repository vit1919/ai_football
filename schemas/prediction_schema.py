from pydantic import BaseModel, Field, computed_field
from datetime import datetime, timezone
from app.utils import get_now_utc
from models.prediction import Result, PredictionSource
from schemas.match_schema import MatchSchemaIndexPage

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
            locked_at = locked_at.replace(tzinfo=timezone.utc)
        return locked_at <= get_now_utc()

class PredictionUpdate(BaseModel):
    score_home: int | None = Field(default=None, ge=0)
    score_away: int | None = Field(default=None, ge=0)
    confidence: float | None = None
    predicted_mvp: str | None = None

class PredictionWithMatchRead(PredictionRead):
    match: MatchSchemaIndexPage