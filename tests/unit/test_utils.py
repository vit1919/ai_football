import pytest
from app.utils.job_utils import calc_result, calculate_prediction_points
from models.match import Match
from models.prediction import Prediction, Result

def test_calc_result():
    assert calc_result(3, 1) == Result.HOME_WIN
    assert calc_result(0, 2) == Result.AWAY_WIN
    assert calc_result(1, 1) == Result.DRAW

def test_calculate_prediction_points_exact_score():
    match = Match(home_score=2, away_score=1)
    prediction = Prediction(score_home=2, score_away=1, predicted_result=Result.HOME_WIN)
    points = calculate_prediction_points(prediction, match)
    assert points == 6

def test_calculate_prediction_points_goal_difference():
    match = Match(home_score=2, away_score=0)
    prediction = Prediction(score_home=3, score_away=1, predicted_result=Result.HOME_WIN)
    points = calculate_prediction_points(prediction, match)
    assert points == 4

def test_calculate_prediction_points_only_outcome():
    match = Match(home_score=3, away_score=1)
    prediction = Prediction(score_home=1, score_away=0, predicted_result=Result.HOME_WIN)
    points = calculate_prediction_points(prediction, match)
    assert points == 3

def test_calculate_prediction_points_wrong_prediction():
    match = Match(home_score=1, away_score=2)
    prediction = Prediction(score_home=2, score_away=0, predicted_result=Result.HOME_WIN)
    points = calculate_prediction_points(prediction, match)
    assert points == 0