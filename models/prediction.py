from datetime import datetime, timezone
import enum
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from sqlalchemy import Enum
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .match import Match
    from .user import User

class Result(enum.Enum):
    HOME_WIN = "home_win"
    AWAY_WIN = "away_win"
    DRAW = "draw"

class PredictionSource(enum.Enum):
    LLM = "llm"
    USER = "user"
    

class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    match_id: Mapped[int] = mapped_column(Integer, ForeignKey("matches.id"), index=True, nullable=False)
    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), index=True, nullable=True)
    source: Mapped[PredictionSource] = mapped_column(Enum(PredictionSource), nullable=False)
    model_name: Mapped[str | None] = mapped_column(String)
    model_id: Mapped[int | None] = mapped_column(Integer)
    confidence: Mapped[float | None] = mapped_column(Float)

    predicted_result: Mapped[Result] = mapped_column(Enum(Result), nullable=False)
    score_home: Mapped[int] = mapped_column(Integer, nullable=False)
    score_away: Mapped[int] = mapped_column(Integer, nullable=False)
    predicted_mvp: Mapped[str | None] = mapped_column(String)


    points_awarded: Mapped[int | None] = mapped_column(Integer)
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    is_scored: Mapped[bool] = mapped_column(Boolean,default=False)
    scored_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


    match: Mapped["Match"] = relationship(back_populates="predictions")
    user: Mapped["User"] = relationship(back_populates="predictions")

    __table_args__ = (
    UniqueConstraint(
        "user_id",
        "match_id",
        name="uq_user_match_prediction"
    ),
)
