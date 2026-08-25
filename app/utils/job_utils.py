from models import Match, Prediction
from models.prediction import Result


def calc_result(home_score: int, away_score: int) -> Result:
    if home_score > away_score:
        return Result.HOME_WIN
    elif home_score < away_score:
        return Result.AWAY_WIN
    else:
        return Result.DRAW

def calculate_prediction_points(prediction: Prediction, match: Match) -> int:
    if match.home_score is None or match.away_score is None:
        return 0

    actual_result = calc_result(match.home_score, match.away_score)
    points = 0

    if prediction.predicted_result == actual_result:
        points += 3

    predicted_goal_diff = prediction.score_home - prediction.score_away
    actual_goal_diff = match.home_score - match.away_score

    if predicted_goal_diff == actual_goal_diff:
        points += 1

    if prediction.score_home == match.home_score and prediction.score_away == match.away_score:
        points += 2

    return points
