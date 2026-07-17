from datetime import datetime, timezone
from sqlalchemy import BigInteger, Boolean, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .prediction import Prediction

class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    league_id: Mapped[int] = mapped_column(Integer, index=True)
    league_name: Mapped[str | None] = mapped_column(String)
    league_slug: Mapped[str] = mapped_column(String)
    year: Mapped[int] = mapped_column(Integer)

    event_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    state: Mapped[str] = mapped_column(String, nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)

    venue_id: Mapped[int | None] = mapped_column(Integer)
    venue_name: Mapped[str | None] = mapped_column(String)

    home_team_id: Mapped[int] = mapped_column(Integer, nullable=False)
    home_team_name: Mapped[str] = mapped_column(String, nullable=False)
    home_team_form: Mapped[str | None] = mapped_column(String)
    home_team_record: Mapped[str | None] = mapped_column(String)
    home_team_logo: Mapped[str | None] = mapped_column(String)
    home_team_leader_id: Mapped[int | None] = mapped_column(Integer)
    home_team_leader_name: Mapped[str | None] = mapped_column(String)

    away_team_id: Mapped[int] = mapped_column(Integer, nullable=False)
    away_team_name: Mapped[str] = mapped_column(String, nullable=False)
    away_team_form: Mapped[str | None] = mapped_column(String)
    away_team_record: Mapped[str | None] = mapped_column(String)
    away_team_logo: Mapped[str | None] = mapped_column(String)
    away_team_leader_id: Mapped[int | None] = mapped_column(Integer)
    away_team_leader_name: Mapped[str | None] = mapped_column(String)

    winner: Mapped[str | None] = mapped_column(String)
    home_score: Mapped[int | None] = mapped_column(Integer)
    away_score: Mapped[int | None] = mapped_column(Integer)
    home_possession: Mapped[float | None] = mapped_column(Float)
    away_possession: Mapped[float | None] = mapped_column(Float)
    home_shots: Mapped[int | None] = mapped_column(Integer)
    away_shots: Mapped[int | None] = mapped_column(Integer)
    home_shots_on_target: Mapped[int | None] = mapped_column(Integer)
    away_shots_on_target: Mapped[int | None] = mapped_column(Integer)

    odds_provider_id: Mapped[int | None] = mapped_column(Integer)
    odds_provider_name: Mapped[str | None] = mapped_column(String)
    over_under: Mapped[float | None] = mapped_column(Float)

    home_ml_open: Mapped[float | None] = mapped_column(Float)
    home_ml_close: Mapped[float | None] = mapped_column(Float)
    away_ml_open: Mapped[float | None] = mapped_column(Float)
    away_ml_close: Mapped[float | None] = mapped_column(Float)
    draw_ml_open: Mapped[float | None] = mapped_column(Float)
    draw_ml_close: Mapped[float | None] = mapped_column(Float)

    total_line: Mapped[float | None] = mapped_column(Float)
    over_odds_open: Mapped[float | None] = mapped_column(Float)
    over_odds_close: Mapped[float | None] = mapped_column(Float)
    under_odds_open: Mapped[float | None] = mapped_column(Float)
    under_odds_close: Mapped[float | None] = mapped_column(Float)

    home_spread_line_open: Mapped[float | None] = mapped_column(Float)
    home_spread_line_close: Mapped[float | None] = mapped_column(Float)
    home_spread_odds_open: Mapped[float | None] = mapped_column(Float)
    home_spread_odds_close: Mapped[float | None] = mapped_column(Float)

    away_spread_line_open: Mapped[float | None] = mapped_column(Float)
    away_spread_line_close: Mapped[float | None] = mapped_column(Float)
    away_spread_odds_open: Mapped[float | None] = mapped_column(Float)
    away_spread_odds_close: Mapped[float | None] = mapped_column(Float)

    match_url: Mapped[str | None] = mapped_column(String)
    stats_url: Mapped[str | None] = mapped_column(String)
    highlights_url: Mapped[str | None] = mapped_column(String)

    lineups_fetched: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_predictions_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    predictions_scored: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    predictions: Mapped[list["Prediction"]] = relationship(
    back_populates="match", cascade="all, delete-orphan"
    )
