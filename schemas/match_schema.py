from pydantic import BaseModel
from datetime import datetime, timezone
from pydantic import AwareDatetime
from .prediction_schema import PredictionRead

class MatchBase(BaseModel):
    league_id : int
    league_name : str | None = None
    league_slug : str
    year : int

    event_id : int
    date : datetime
    state : str
    completed : bool

    home_team_id : int
    home_team_name : str
   
    away_team_id : int
    away_team_name : str

    model_config = {"from_attributes": True}

  
class MatchSchema(MatchBase):
    id: int | None = None
    venue_id : int | None = None
    venue_name : str | None = None


    home_team_form : str | None = None
    home_team_record : str | None = None
    home_team_logo : str | None = None
    home_team_leader_id : int | None = None
    home_team_leader_name : str | None = None


    away_team_form : str | None = None
    away_team_record : str | None = None
    away_team_logo : str | None = None
    away_team_leader_id : int | None = None
    away_team_leader_name : str | None = None

    winner : str | None = None
    home_score: int | None = None
    away_score: int | None = None

    home_possession: float | None = None
    away_possession: float | None = None

    home_shots: int | None = None
    away_shots: int | None = None

    home_shots_on_target: int | None = None
    away_shots_on_target: int | None = None

    odds_provider_id : int | None = None
    odds_provider_name : str | None = None
    #open - starting odds, close - odds at match start
    over_under: float | None = None
    home_ml_open: float | None = None
    home_ml_close: float | None = None
    away_ml_open: float | None = None
    away_ml_close: float | None = None
    draw_ml_open: float | None = None
    draw_ml_close: float | None = None

    total_line: float | None = None
    over_odds_open: float | None = None
    over_odds_close: float | None = None
    under_odds_open: float | None = None
    under_odds_close: float | None = None

    home_spread_line_open: float | None = None
    home_spread_line_close: float | None = None
    home_spread_odds_open: float | None = None
    home_spread_odds_close: float | None = None

    away_spread_line_open: float | None = None
    away_spread_line_close: float | None = None
    away_spread_odds_open: float | None = None
    away_spread_odds_close: float | None = None

    match_url: str | None = None
    stats_url: str | None = None
    highlights_url: str | None = None

    llm_points_awarded: int | None = None
    llm_vs_user_result: str | None = None

class MatchDetailResponse(BaseModel):
    match: MatchSchema
    user_prediction: PredictionRead | None = None

class MatchSchemaIndexPage(MatchBase):
    id: int
    venue_id : int | None = None
    venue_name : str | None = None

    home_team_form : str | None = None
    home_team_record : str | None = None
    home_team_logo : str | None = None

    away_team_form : str | None = None
    away_team_record : str | None = None
    away_team_logo : str | None = None

    winner : str | None = None
    home_score: int | None = None
    away_score: int | None = None


class MatchComparisonResponse(BaseModel):
    match: MatchSchema
    user_prediction: PredictionRead | None = None
    llm_prediction: PredictionRead | None = None
    result: str | None = None
    actual_score: dict | None = None
    model_name: str | None = None

