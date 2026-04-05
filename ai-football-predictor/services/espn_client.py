from datetime import datetime
import httpx
from schemas.match_schema import MatchSchema


async def get_matches_today_top5():
    date = datetime.utcnow().strftime("%Y%m%d")

    matches = []
    top5 = ['eng.1', 'esp.1', 'ger.1', 'ita.1', 'fra.1']

    for league in top5:
        url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league}/scoreboard"
        
        params = {"dates": date}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)

        if response.status_code == 200: 
            data = response.json()
            league_mathes = extract_matches(data)
            matches.extend(league_mathes)

    return matches




def extract_matches(data: dict) -> list[MatchSchema]:

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
            home_team_record = home_team["record"] if "record" in home_team else None
            home_team_logo = home_team["team"]["logo"] if "logo" in home_team["team"] else None
            home_team_leader_id = home_team["leaders"][0]["athlete"]["id"] if "leaders" in home_team and len(home_team["leaders"]) > 0 else None
            home_team_leader_name = home_team["leaders"][0]["athlete"]["displayName"] if "leaders" in home_team and len(home_team["leaders"]) > 0 else None  

            away_team = event["competitions"][0]["competitors"][1]
            away_team_id = away_team["id"]
            away_team_name = away_team["team"]["displayName"]
            away_team_form = away_team["form"] if "form" in away_team else None 
            away_team_record = away_team["record"] if "record" in away_team else None
            away_team_logo = away_team["team"]["logo"] if "logo" in away_team else None
            away_team_leader_id = away_team["leaders"][0]["athlete"]["id"] if "leaders" in away_team and len(away_team["leaders"]) > 0 else None
            away_team_leader_name = away_team["leaders"][0]["athlete"]["displayName"] if "leaders" in away_team and len(away_team["leaders"]) > 0 else None

            if state == "post":
                winner = event["competitions"][0]["winner"]
                home_score = home_team["score"]
                away_score = away_team["score"]
            else:
                winner = None
                home_score = None
                away_score = None

            

            


        except Exception as e:
            continue
        

        
