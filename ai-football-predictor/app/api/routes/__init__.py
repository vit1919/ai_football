from .mathes import router as today_matches_router, sync_matches, list_matches, list_all_matches, list_matches_today, get_detailed_match
from .auth import router as auth, get_me, register, login

__all__ = ["today_matches_router", "sync_matches", "list_matches", "list_all_matches", "list_matches_today", "get_detailed_match", "auth", "get_me", "register", "login"]

