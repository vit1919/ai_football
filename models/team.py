from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from .favourite_team import FavouriteTeam

class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    espn_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    uid: Mapped[str | None] = mapped_column(String)
    slug: Mapped[str | None] = mapped_column(String, index=True)

    name: Mapped[str] = mapped_column(String)
    display_name: Mapped[str | None] = mapped_column(String)
    short_display_name: Mapped[str | None] = mapped_column(String)
    abbreviation: Mapped[str | None] = mapped_column(String(10))
    location: Mapped[str | None] = mapped_column(String)
    nickname: Mapped[str | None] = mapped_column(String)
    is_active: Mapped[bool | None] = mapped_column(Boolean, default=True)

    color: Mapped[str | None] = mapped_column(String(10))
    alternate_color: Mapped[str | None] = mapped_column(String(10))
    logo_url: Mapped[str | None] = mapped_column(String)
    logo_dark_url: Mapped[str | None] = mapped_column(String)
    logo_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    league_id: Mapped[int | None] = mapped_column(Integer, index=True)
    league_slug: Mapped[str | None] = mapped_column(String)
    league_abbrev: Mapped[str | None] = mapped_column(String)
    league_name: Mapped[str | None] = mapped_column(String)

    record_summary: Mapped[str | None] = mapped_column(String)
    games_played: Mapped[int | None] = mapped_column(Integer)
    wins: Mapped[int | None] = mapped_column(Integer)
    losses: Mapped[int | None] = mapped_column(Integer)
    ties: Mapped[int | None] = mapped_column(Integer)
    points: Mapped[int | None] = mapped_column(Integer)
    rank: Mapped[int | None] = mapped_column(Integer)
    streak: Mapped[int | None] = mapped_column(Integer)
    points_for: Mapped[int | None] = mapped_column(Integer)
    points_against: Mapped[int | None] = mapped_column(Integer)
    point_diff: Mapped[int | None] = mapped_column(Integer)
    standing_summary: Mapped[str | None] = mapped_column(String)

    next_event_id: Mapped[int | None] = mapped_column(Integer, index=True)
    next_event_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    next_event_name: Mapped[str | None] = mapped_column(String)
    next_event_short_name: Mapped[str | None] = mapped_column(String)
    next_event_home_away: Mapped[str | None] = mapped_column(String(10))
    next_event_opponent_id: Mapped[int | None] = mapped_column(Integer)
    next_event_opponent_name: Mapped[str | None] = mapped_column(String)
    next_event_venue_name: Mapped[str | None] = mapped_column(String)
    next_event_city: Mapped[str | None] = mapped_column(String)
    next_event_country: Mapped[str | None] = mapped_column(String)

    next_event_status_state: Mapped[str | None] = mapped_column(String)
    next_event_status_detail: Mapped[str | None] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC)
    )

    favourite_teams: Mapped[list["FavouriteTeam"]] = relationship(
        back_populates="team",
        cascade="all, delete-orphan",
    )
