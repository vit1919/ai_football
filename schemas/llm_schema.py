from pydantic import BaseModel


class LLMModelRead(BaseModel):
    name: str
    provider: str


class AIPredictionResponse(BaseModel):
    match_id: int
    model_name: str
    score_home: int
    score_away: int
    predicted_result: str
    confidence: float | None = None
    reasoning: str | None = None

    model_config = {"from_attributes": True}


class LLMStatsResponse(BaseModel):
    total_predictions: int
    correct_results: int
    correct_goal_diff: int
    exact_scores: int
    avg_points: float
    wins: int
    draws: int
    losses: int


class LLMVsUserStatsResponse(BaseModel):
    wins: int
    draws: int
    losses: int
    total_compared: int
