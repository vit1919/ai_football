from datetime import datetime, timedelta, timezone
import httpx
import asyncio
from schemas.team_schema import TeamRead, TeamSchema
from app.utils import safe_int

def pick_logo(logos, rel_key):
    for logo in logos or []:
        if rel_key in (logo.get("rel") or []):
            return logo
    return (logos or [None])[0]

def extract_record_stats(team):
    items = (team.get("record") or {}).get("items", [])
    total = next((i for i in items if i.get("type") == "total"), None) or (items[0] if items else None)
    stats = {s.get("name"): s.get("value") for s in (total or {}).get("stats", [])}
    return total, stats

def extract_next_event(team_id, team):
    event = (team.get("nextEvent") or [None])[0]
    if not event:
        return {}

    comp = (event.get("competitions") or [None])[0]
    if not comp:
        return {}

    competitors = comp.get("competitors") or []
    me = next((c for c in competitors if safe_int(c.get("id")) == team_id), None)
    opp = next((c for c in competitors if c is not me), None)

    opp_team = (opp or {}).get("team", {})
    venue = comp.get("venue", {})
    addr = venue.get("address", {})
    status = comp.get("status", {}).get("type", {})

    return {
        "next_event_id": safe_int(event.get("id")),
        "next_event_date": event.get("date"),
        "next_event_name": event.get("name"),
        "next_event_short_name": event.get("shortName"),
        "next_event_home_away": (me or {}).get("homeAway"),
        "next_event_opponent_id": safe_int((opp or {}).get("id") or opp_team.get("id")),
        "next_event_opponent_name": opp_team.get("displayName"),
        "next_event_venue_name": venue.get("fullName"),
        "next_event_city": addr.get("city"),
        "next_event_country": addr.get("country"),
        "next_event_status_state": status.get("state"),
        "next_event_status_detail": status.get("detail"),
    }

def extract_team_info(payload: dict) -> TeamSchema | None:
    team = payload.get("team")
    if not team:
        return None

    team_id = safe_int(team.get("id"))
    logos = team.get("logos", [])
    logo = pick_logo(logos, "default")
    logo_dark = pick_logo(logos, "dark")

    total, stats = extract_record_stats(team)

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
        

        **extract_next_event(team_id, team),
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
            print(f"HTTP error occurred while fetching team info: {e}")
        except Exception as e:
            print(f"An error occurred while fetching team info: {e}")
    return None

