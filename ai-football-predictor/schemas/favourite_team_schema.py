from pydantic import BaseModel
from datetime import datetime, timezone
from schemas import TeamRead

class FavouriteTeamBase(BaseModel):
    team_id : int

# class FavouriteTeamCreate(FavouriteTeamBase):
#     pass

class FavouriteTeamRead(FavouriteTeamBase):
    id: int
    team: TeamRead 
    created_at: datetime | None

    model_config = {"from_attributes": True}