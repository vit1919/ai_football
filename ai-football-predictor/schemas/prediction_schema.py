from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Literal

class PredictionBase(BaseModel):
    match_id: int
    predicted_result: Literal["home_win", "away_win", "draw"]
    score_home: int | None = None
    score_away: int | None = None
    predicted_mvp: str | None = None

class PredictionCreateLLM(PredictionBase):
    model_name: str
    model_id: int | None = None
    
class PredictionRead(PredictionBase):
    id: int
    match_id: int
    user_id: int | None = None
    source: Literal["user", "llm"]
    model_name: str | None = None
    model_id: int | None = None
    is_correct: bool | None = None

    locked_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}