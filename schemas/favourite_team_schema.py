from datetime import datetime

from pydantic import BaseModel

from schemas.team_schema import TeamRead


class FavouriteTeamBase(BaseModel):
    team_id: int


class FavouriteTeamRead(FavouriteTeamBase):
    id: int
    team: TeamRead
    created_at: datetime | None

    model_config = {"from_attributes": True}
