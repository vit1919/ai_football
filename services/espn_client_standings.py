import logging
import httpx
from schemas.standing_schema import StandingSchema
from app.utils import safe_int

logger = logging.getLogger(__name__)

ESPN_STANDINGS_URL = "https://site.api.espn.com/apis/v2/sports/soccer/{league}/standings"

async def get_standings(league_slug: str) -> list[StandingSchema]:
    url = ESPN_STANDINGS_URL.format(league=league_slug)

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as e:
            logger.error("HTTP error fetching standings for %s: %s", league_slug, e)
            return []
        except Exception as e:
            logger.error("Error fetching standings for %s: %s", league_slug, e, exc_info=True)
            return []

    children = data.get("children") or []
    if not children:
        return []

    child = children[0]
    standings_data = child.get("standings") or {}
    season = standings_data.get("season", 0)
    group_name = child.get("name", league_slug)
    entries = standings_data.get("entries") or []

    result: list[StandingSchema] = []

    for entry in entries:
        try:
            team = entry.get("team", {})
            team_id = safe_int(team.get("id"))
            if team_id is None:
                continue

            logos = team.get("logos") or []
            logo_url = logos[0].get("href") if logos else None

            stats = {}
            for s in entry.get("stats") or []:
                name = s.get("name")
                val = s.get("value")
                if name and val is not None:
                    stats[name] = val

            result.append(StandingSchema(
                league_slug=league_slug,
                season=season,
                group_name=group_name,
                team_espn_id=team_id,
                team_name=team.get("displayName") or team.get("name", ""),
                abbreviation=team.get("abbreviation"),
                logo_url=logo_url,
                rank=stats.get("rank"),
                games_played=int(stats.get("gamesPlayed", 0)),
                wins=int(stats.get("wins", 0)),
                draws=int(stats.get("ties", 0)),
                losses=int(stats.get("losses", 0)),
                goals_for=int(stats.get("pointsFor", 0)),
                goals_against=int(stats.get("pointsAgainst", 0)),
                goal_difference=int(stats.get("pointDifferential", 0)),
                points=int(stats.get("points", 0)),
                deductions=int(stats.get("deductions", 0)),
            ))
        except Exception as e:
            logger.error("Error parsing standing entry: %s", e, exc_info=True)
            continue

    return result
