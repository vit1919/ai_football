import logging
from datetime import datetime, timedelta, timezone
import httpx
import asyncio
from schemas.team_schema import TeamRead, TeamSchema
from app.utils import safe_int, safe_float, pick_logo, extract_record_stats_team, extract_next_event_team

logger = logging.getLogger(__name__)

def extract_team_info(payload: dict) -> TeamSchema | None:
    team = payload.get("team")
    if not team:
        return None

    team_id = safe_int(team.get("id"))
    logos = team.get("logos", [])
    logo = pick_logo(logos, "default")
    logo_dark = pick_logo(logos, "dark")

    total, stats = extract_record_stats_team(team)

    data = {
        "espn_id": team_id,
        "uid": team.get("uid"),
        "slug": team.get("slug"),
        "name": team.get("name"),
        "display_name": team.get("displayName"),
        "short_display_name": team.get("shortDisplayName"),
        "abbreviation": team.get("abbreviation"),
        "location": team.get("location"),
        "nickname": team.get("nickname"),
        "is_active": team.get("isActive"),

        "color": team.get("color"),
        "alternate_color": team.get("alternateColor"),
        "logo_url": (logo or {}).get("href"),
        "logo_dark_url": (logo_dark or {}).get("href"),
        "logo_updated_at": (logo or {}).get("lastUpdated"),

        "league_id": safe_int(team.get("defaultLeague", {}).get("id")),
        "league_slug": team.get("defaultLeague", {}).get("slug"),
        "league_abbrev": team.get("leagueAbbrev"),
        "league_name": team.get("defaultLeague", {}).get("name"),

        "record_summary": (total or {}).get("summary"),
        "games_played": safe_int(stats.get("gamesPlayed")),
        "wins": safe_int(stats.get("wins")),
        "losses": safe_int(stats.get("losses")),
        "ties": safe_int(stats.get("ties")),
        "points": safe_int(stats.get("points")),
        "rank": safe_int(stats.get("rank")),
        "streak": safe_int(stats.get("streak")),
        "points_for": safe_int(stats.get("pointsFor")),
        "points_against": safe_int(stats.get("pointsAgainst")),
        "point_diff": safe_int(stats.get("pointDifferential")),
        "standing_summary": payload.get("standingSummary"),
        

        **extract_next_event_team(team_id, team),
    }
    return TeamSchema(**data)

async def get_team_info(league_slug: str, team_id: int) -> TeamRead | None:
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_slug}/teams/{team_id}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            return extract_team_info(data)
        
        except httpx.HTTPError as e:
            logger.error("HTTP error fetching team info: %s", e)
        except Exception as e:
            logger.error("Error fetching team info: %s", e, exc_info=True)
    return None

