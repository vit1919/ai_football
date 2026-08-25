from .auth import get_me, login, register
from .auth import router as auth
from .matches import (
    get_detailed_match,
    list_all_matches,
    list_matches,
    list_matches_today,
    sync_matches,
)
from .matches import router as today_matches_router
from .predictions import (
    delete_prediction,
    get_user_prediction,
    prediction_from_user,
    update_prediction,
)
from .predictions import router as predictions
from .teams import router as teams

__all__ = [
    "auth",
    "delete_prediction",
    "get_detailed_match",
    "get_me",
    "get_user_prediction",
    "list_all_matches",
    "list_matches",
    "list_matches_today",
    "login",
    "prediction_from_user",
    "predictions",
    "register",
    "sync_matches",
    "today_matches_router",
    "update_prediction",
    "teams",
]
