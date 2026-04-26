from datetime import datetime, timedelta, timezone
import httpx
from schemas.match_schema import MatchSchema


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

    async with httpx.AsyncClient(timeout=30) as client:
        for league in league_list:
            url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league}/scoreboard"

            for date in dates:
                response = await client.get(url, params={"dates": date})
                if response.status_code != 200:
                    continue

                data = response.json()
                for match in extract_matches(data):
                    if match.event_id in seen_event_ids:
                        continue
                    seen_event_ids.add(match.event_id)
                    matches.append(match)

    return matches


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
            home_team_leader_id = home_team["leaders"][0]["athlete"]["id"] if "leaders" in home_team and len(home_team["leaders"]) > 0 else None
            home_team_leader_name = home_team["leaders"][0]["athlete"]["displayName"] if "leaders" in home_team and len(home_team["leaders"]) > 0 else None  

            away_team = event["competitions"][0]["competitors"][1]
            away_team_id = away_team["id"]
            away_team_name = away_team["team"]["displayName"]
            away_team_form = away_team["form"] if "form" in away_team else None 
            away_team_record = away_team["records"][0]["summary"] if "records" in away_team and len(away_team["records"]) > 0 else None
            away_team_logo = away_team["team"]["logo"] if "logo" in away_team["team"] else None
            away_team_leader_id = away_team["leaders"][0]["athlete"]["id"] if "leaders" in away_team and len(away_team["leaders"]) > 0 else None
            away_team_leader_name = away_team["leaders"][0]["athlete"]["displayName"] if "leaders" in away_team and len(away_team["leaders"]) > 0 else None

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

            has_odds = "odds" in event["competitions"][0] and len(event["competitions"][0]["odds"]) > 0 and event["competitions"][0]["odds"][0] is not None

            odds_provider_id = int(event["competitions"][0]["odds"][0]["provider"]["id"]) if has_odds else None
            odds_provider_name = event["competitions"][0]["odds"][0]["provider"]["name"] if has_odds else None

            over_under = float(event["competitions"][0]["odds"][0]["overUnder"]) if has_odds else None

            home_ml_open = float(event["competitions"][0]["odds"][0]["moneyline"]["home"]["open"]["odds"]) if has_odds else None
            home_ml_close = float(event["competitions"][0]["odds"][0]["moneyline"]["home"]["close"]["odds"]) if has_odds else None
            away_ml_open = float(event["competitions"][0]["odds"][0]["moneyline"]["away"]["open"]["odds"]) if has_odds else None
            away_ml_close = float(event["competitions"][0]["odds"][0]["moneyline"]["away"]["close"]["odds"]) if has_odds else None
            draw_ml_open = float(event["competitions"][0]["odds"][0]["moneyline"]["draw"]["open"]["odds"]) if has_odds else None
            draw_ml_close = float(event["competitions"][0]["odds"][0]["moneyline"]["draw"]["close"]["odds"]) if has_odds else None

            total_line = float(event["competitions"][0]["odds"][0]["total"]["over"]["close"]["line"].replace("o", "").replace("u", "")) if has_odds else None
            over_odds_open = float(event["competitions"][0]["odds"][0]["total"]["over"]["open"]["odds"]) if has_odds else None
            over_odds_close = float(event["competitions"][0]["odds"][0]["total"]["over"]["close"]["odds"]) if has_odds else None
            under_odds_open = float(event["competitions"][0]["odds"][0]["total"]["under"]["open"]["odds"]) if has_odds else None
            under_odds_close = float(event["competitions"][0]["odds"][0]["total"]["under"]["close"]["odds"]) if has_odds else None

            home_spread_line_open = float(event["competitions"][0]["odds"][0]["pointSpread"]["home"]["open"]["line"]) if has_odds else None
            home_spread_line_close = float(event["competitions"][0]["odds"][0]["pointSpread"]["home"]["close"]["line"]) if has_odds else None
            home_spread_odds_open = float(event["competitions"][0]["odds"][0]["pointSpread"]["home"]["open"]["odds"]) if has_odds else None
            home_spread_odds_close = float(event["competitions"][0]["odds"][0]["pointSpread"]["home"]["close"]["odds"]) if has_odds else None

            away_spread_line_open = float(event["competitions"][0]["odds"][0]["pointSpread"]["away"]["open"]["line"]) if has_odds else None
            away_spread_line_close = float(event["competitions"][0]["odds"][0]["pointSpread"]["away"]["close"]["line"]) if has_odds else None
            away_spread_odds_open = float(event["competitions"][0]["odds"][0]["pointSpread"]["away"]["open"]["odds"]) if has_odds else None
            away_spread_odds_close = float(event["competitions"][0]["odds"][0]["pointSpread"]["away"]["close"]["odds"]) if has_odds else None

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
            print("ERROR:", e)
            continue

    return matches




