from datetime import datetime, timedelta, timezone
import httpx
from schemas.match_schema import MatchSchema
import asyncio
from app.utils import safe_int, safe_float

async def get_matches_today(league_list: list[str]) -> list[MatchSchema]:
    today = datetime.now(timezone.utc)
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)

    dates = [
        yesterday.strftime("%Y%m%d"),
        today.strftime("%Y%m%d"),
        tomorrow.strftime("%Y%m%d"),
    ]

    matches: list[MatchSchema] = []
    seen_event_ids: set[int] = set()

    async with httpx.AsyncClient(timeout=60.0) as client:
        for league in league_list:
            url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league}/scoreboard"

            for date in dates:
                try:
                    response = await client.get(url, params={"dates": date})
                    if response.status_code != 200:
                        continue

                    data = response.json()
                    if "events" not in data:
                        continue

                    for match in extract_matches(data):
                        if match.event_id in seen_event_ids:
                            continue
                        seen_event_ids.add(match.event_id)
                        matches.append(match)
                        
                except httpx.RequestError as e:
                    print(f"Ошибка сети при парсинге {league} за {date}: {e}")
                    continue
                except Exception as e:
                    print(f"Критическая ошибка при обработке {league}: {e}")
                    continue

                await asyncio.sleep(0.5)

    return matches


def extract_leader(team):
    try:
        leader = team["leaders"][0]["leaders"][0]["athlete"]
        return leader.get("id"), leader.get("displayName")
    except Exception:
        return None, None

def extract_matches(data: dict) -> list[MatchSchema]:

    matches: list[MatchSchema] = []

    league = data["leagues"]
    league_id = league[0]["id"]
    league_name = league[0]["name"]
    league_slug = league[0]["slug"]
    year = league[0]["season"]["year"]

    events = data["events"]
    for event in events:

        try:

            event_id = event["id"]
            date = event["date"]
            state = event["competitions"][0]["status"]["type"]["state"]
            completed = event["competitions"][0]["status"]["type"]["completed"]

            venue_id = event["competitions"][0]["venue"]["id"] if "venue" in event["competitions"][0] else None
            venue_name = event["competitions"][0]["venue"]["fullName"] if "venue" in event["competitions"][0] else None

            home_team = event["competitions"][0]["competitors"][0]
            home_team_id = home_team["id"]
            home_team_name = home_team["team"]["displayName"]
            home_team_form = home_team["form"] if "form" in home_team else None
            home_team_record = home_team["records"][0]["summary"] if "records" in home_team and len(home_team["records"]) > 0 else None
            home_team_logo = home_team["team"]["logo"] if "logo" in home_team["team"] else None
            home_team_leader_id, home_team_leader_name = extract_leader(home_team)  

            away_team = event["competitions"][0]["competitors"][1]
            away_team_id = away_team["id"]
            away_team_name = away_team["team"]["displayName"]
            away_team_form = away_team["form"] if "form" in away_team else None 
            away_team_record = away_team["records"][0]["summary"] if "records" in away_team and len(away_team["records"]) > 0 else None
            away_team_logo = away_team["team"]["logo"] if "logo" in away_team["team"] else None
            away_team_leader_id, away_team_leader_name = extract_leader(away_team)

            if state == "post":
                home_score = int(home_team["score"]) if "score" in home_team else None
                away_score = int(away_team["score"]) if "score" in away_team else None

                if "winner" in home_team and home_team["winner"]:
                    winner = "home"
                elif "winner" in away_team and away_team["winner"]:
                    winner = "away"
                elif home_score is not None and away_score is not None and home_score == away_score:
                    winner = "draw"
                else:
                    winner = None
            else:
                winner = None
                home_score = None
                away_score = None

            home_shots = next((int(s["displayValue"]) for s in home_team["statistics"] if s["name"] == "totalShots"), None) if "statistics" in home_team else None
            away_shots = next((int(s["displayValue"]) for s in away_team["statistics"] if s["name"] == "totalShots"), None) if "statistics" in away_team else None

            home_shots_on_target = next((int(s["displayValue"]) for s in home_team["statistics"] if s["name"] == "shotsOnTarget"), None) if "statistics" in home_team else None
            away_shots_on_target = next((int(s["displayValue"]) for s in away_team["statistics"] if s["name"] == "shotsOnTarget"), None) if "statistics" in away_team else None

            odds_data = None
            if "odds" in event["competitions"][0] and event["competitions"][0]["odds"]:
                odds_data = event["competitions"][0]["odds"][0]

            odds_provider_id = safe_int(odds_data.get("provider", {}).get("id")) if odds_data else None
            odds_provider_name = odds_data.get("provider", {}).get("name") if odds_data else None

            over_under = safe_float(odds_data.get("overUnder")) if odds_data else None

            ml = odds_data.get("moneyline", {}) if odds_data else {}

            home_ml_open = safe_float(ml.get("home", {}).get("open", {}).get("odds"))
            home_ml_close = safe_float(ml.get("home", {}).get("close", {}).get("odds"))
            away_ml_open = safe_float(ml.get("away", {}).get("open", {}).get("odds"))
            away_ml_close = safe_float(ml.get("away", {}).get("close", {}).get("odds"))
            draw_ml_open = safe_float(ml.get("draw", {}).get("open", {}).get("odds"))
            draw_ml_close = safe_float(ml.get("draw", {}).get("close", {}).get("odds"))

            total = odds_data.get("total", {}) if odds_data else {}

            line_raw = total.get("over", {}).get("close", {}).get("line")
            if line_raw:
                line_raw = line_raw.replace("o", "").replace("u", "")

            total_line = safe_float(line_raw)

            over_odds_open = safe_float(total.get("over", {}).get("open", {}).get("odds"))
            over_odds_close = safe_float(total.get("over", {}).get("close", {}).get("odds"))
            under_odds_open = safe_float(total.get("under", {}).get("open", {}).get("odds"))
            under_odds_close = safe_float(total.get("under", {}).get("close", {}).get("odds"))

            spread = odds_data.get("pointSpread", {}) if odds_data else {}

            home_spread_line_open = safe_float(spread.get("home", {}).get("open", {}).get("line"))
            home_spread_line_close = safe_float(spread.get("home", {}).get("close", {}).get("line"))
            home_spread_odds_open = safe_float(spread.get("home", {}).get("open", {}).get("odds"))
            home_spread_odds_close = safe_float(spread.get("home", {}).get("close", {}).get("odds"))

            away_spread_line_open = safe_float(spread.get("away", {}).get("open", {}).get("line"))
            away_spread_line_close = safe_float(spread.get("away", {}).get("close", {}).get("line"))
            away_spread_odds_open = safe_float(spread.get("away", {}).get("open", {}).get("odds"))
            away_spread_odds_close = safe_float(spread.get("away", {}).get("close", {}).get("odds"))

            match_url = event["links"][0]["href"] if "links" in event and len(event["links"]) > 0 else None
            stats_url = event["links"][1]["href"] if "links" in event and len(event["links"]) > 1 else None
            highlight_url = event["links"][2]["href"] if "links" in event and len(event["links"]) > 2 else None
            
            match = MatchSchema(
                league_id=league_id,
                league_name=league_name,
                league_slug=league_slug,
                year=year,

                event_id=event_id,
                date=date,
                state=state,
                completed=completed,

                venue_id=venue_id,
                venue_name=venue_name,

                home_team_id=home_team_id,
                home_team_name=home_team_name,
                home_team_form=home_team_form,
                home_team_record=home_team_record,
                home_team_logo=home_team_logo,
                home_team_leader_id=home_team_leader_id,
                home_team_leader_name=home_team_leader_name,

                away_team_id=away_team_id,
                away_team_name=away_team_name,
                away_team_form=away_team_form,
                away_team_record=away_team_record,
                away_team_logo=away_team_logo,
                away_team_leader_id=away_team_leader_id,
                away_team_leader_name=away_team_leader_name,

                winner=winner,
                home_score=home_score,
                away_score=away_score,

                home_shots=home_shots,
                away_shots=away_shots,

                home_shots_on_target=home_shots_on_target,
                away_shots_on_target=away_shots_on_target,

                odds_provider_id=odds_provider_id,
                odds_provider_name=odds_provider_name,

                over_under=over_under,
                home_ml_open=home_ml_open,
                home_ml_close=home_ml_close,
                away_ml_open=away_ml_open,
                away_ml_close=away_ml_close,
                draw_ml_open=draw_ml_open,
                draw_ml_close=draw_ml_close,

                total_line=total_line,
                over_odds_open=over_odds_open,
                over_odds_close=over_odds_close,
                under_odds_open=under_odds_open,
                under_odds_close=under_odds_close,

                home_spread_line_open=home_spread_line_open,
                home_spread_line_close=home_spread_line_close,
                home_spread_odds_open=home_spread_odds_open,
                home_spread_odds_close=home_spread_odds_close,

                away_spread_line_open=away_spread_line_open,
                away_spread_line_close=away_spread_line_close,
                away_spread_odds_open=away_spread_odds_open,
                away_spread_odds_close=away_spread_odds_close,

                match_url=match_url,
                stats_url=stats_url,
                highlights_url=highlight_url
            )
            matches.append(match)

        except Exception as e:
            print(f"ERROR: {e} EVENT: {event.get('id')}")
            continue

    return matches




