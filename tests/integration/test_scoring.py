from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from models.match import Match
from models.prediction import Prediction, PredictionSource, Result
from models.user import User
from services.jobs_service import score_predictions


async def create_completed_match(db: AsyncSession, home_score: int = 2, away_score: int = 1) -> Match:
    match = Match(
        league_id=1,
        league_slug="test_league",
        year=2026,
        event_id=888888,
        date=datetime.now(UTC) - timedelta(hours=3),
        state="post",
        completed=True,
        home_team_id=101,
        home_team_name="Arsenal",
        away_team_id=102,
        away_team_name="Chelsea",
        home_score=home_score,
        away_score=away_score,
        winner="home",
        predictions_scored=False,
    )
    db.add(match)
    await db.commit()
    await db.refresh(match)
    return match


async def create_test_user(db: AsyncSession, username: str, email: str) -> User:
    user = User(
        username=username,
        email=email,
        hashed_password="hashed_pass_123",
        total_points=0,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.mark.asyncio
async def test_score_predictions_exact_and_partial(db_session: AsyncSession):
    match = await create_completed_match(db_session, home_score=2, away_score=1)

    user_exact = await create_test_user(db_session, "exact_guy", "exact@example.com")
    user_outcome = await create_test_user(db_session, "outcome_guy", "outcome@example.com")
    user_wrong = await create_test_user(db_session, "wrong_guy", "wrong@example.com")

    pred1 = Prediction(
        match_id=match.id,
        user_id=user_exact.id,
        source=PredictionSource.USER,
        score_home=2,
        score_away=1,
        predicted_result=Result.HOME_WIN,
    )
    pred2 = Prediction(
        match_id=match.id,
        user_id=user_outcome.id,
        source=PredictionSource.USER,
        score_home=3,
        score_away=0,
        predicted_result=Result.HOME_WIN,
    )
    pred3 = Prediction(
        match_id=match.id,
        user_id=user_wrong.id,
        source=PredictionSource.USER,
        score_home=0,
        score_away=1,
        predicted_result=Result.AWAY_WIN,
    )

    db_session.add_all([pred1, pred2, pred3])
    await db_session.commit()

    result = await score_predictions(db_session)

    assert result["matches_scored"] == 1
    assert result["predictions_scored"] == 3

    await db_session.refresh(user_exact)
    await db_session.refresh(user_outcome)
    await db_session.refresh(user_wrong)

    assert user_exact.total_points == 6
    assert user_outcome.total_points == 3
    assert user_wrong.total_points == 0

    await db_session.refresh(match)
    assert match.predictions_scored is True

@pytest.mark.asyncio
async def test_score_user_vs_llm_comparison(db_session: AsyncSession):
    match = await create_completed_match(db_session, home_score=2, away_score=1)
    user_winner = await create_test_user(db_session, "winner_guy", "win@test.com")
    user_loser = await create_test_user(db_session, "loser_guy", "lose@test.com")
    user_draw = await create_test_user(db_session, "draw_guy", "draw@test.com")

    llm_pred = Prediction(
        match_id=match.id,
        source=PredictionSource.LLM,
        model_name="gemini-3.5-flash-lite",
        score_home=1,
        score_away=0,
        predicted_result=Result.HOME_WIN,
    )
    user_pred_win = Prediction(
        match_id=match.id,
        user_id=user_winner.id,
        source=PredictionSource.USER,
        selected_model="gemini-3.5-flash-lite",
        score_home=2,
        score_away=1,
        predicted_result=Result.HOME_WIN,
    )
    user_pred_lose = Prediction(
        match_id=match.id,
        user_id=user_loser.id,
        source=PredictionSource.USER,
        selected_model="gemini-3.5-flash-lite",
        score_home=0,
        score_away=2,
        predicted_result=Result.AWAY_WIN,
    )
    user_pred_draw = Prediction(
        match_id=match.id,
        user_id=user_draw.id,
        source=PredictionSource.USER,
        selected_model="gemini-3.5-flash-lite",
        score_home=3,
        score_away=2,
        predicted_result=Result.HOME_WIN,
    )

    db_session.add_all([llm_pred, user_pred_win, user_pred_lose, user_pred_draw])
    await db_session.commit()

    result = await score_predictions(db_session)

    assert result["predictions_scored"] == 4
    await db_session.refresh(user_pred_win)
    await db_session.refresh(user_pred_lose)
    await db_session.refresh(user_pred_draw)

    assert user_pred_win.points_awarded == 6
    assert user_pred_win.llm_compared_points == 4
    assert user_pred_win.user_vs_llm_result == "user_win"

    assert user_pred_lose.points_awarded == 0
    assert user_pred_lose.llm_compared_points == 4
    assert user_pred_lose.user_vs_llm_result == "user_loss"

    assert user_pred_draw.points_awarded == 4
    assert user_pred_draw.llm_compared_points == 4
    assert user_pred_draw.user_vs_llm_result == "draw"
