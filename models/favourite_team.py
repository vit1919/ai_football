from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy import Integer
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .user import User
    from .team import Team


class FavouriteTeam(Base):
    __tablename__ = "favourite_teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship(back_populates="favourite_teams")
    team: Mapped["Team"] = relationship(back_populates="favourite_teams")

    __table_args__ = (UniqueConstraint("user_id", "team_id", name="uq_user_team_favorite"),)