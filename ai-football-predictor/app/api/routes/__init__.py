from .mathes import router as today_matches_router, sync_matches, list_matches, list_all_matches, list_matches_today, get_detailed_match
from .auth import router as auth, get_me, register, login
from .predictions import router as predictions, prediction_from_user, get_user_prediction, update_prediction, delete_prediction

__all__ = ["today_matches_router", "sync_matches", "list_matches", "list_all_matches", "list_matches_today", "get_detailed_match", "auth", "get_me", "register", "login", "predictions", "prediction_from_user", "get_user_prediction", "update_prediction", "delete_prediction"]

