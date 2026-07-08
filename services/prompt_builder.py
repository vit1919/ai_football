from models.match import Match

def build_prediction_prompt(match: Match) -> str:
    odds_section = _build_odds_section(match)

    return f"""You are an expert football (soccer) match predictor.

Analyze the following match and predict the final score.

## Match Info
- Tournament: {match.league_name} ({match.league_slug})
- Date: {match.date.strftime('%Y-%m-%d %H:%M UTC')}
- Venue: {match.venue_name or 'Unknown'}

## Home Team: {match.home_team_name}
- Form: {match.home_team_form or 'N/A'}
- Record: {match.home_team_record or 'N/A'}
- Key player: {match.home_team_leader_name or 'N/A'}

## Away Team: {match.away_team_name}
- Form: {match.away_team_form or 'N/A'}
- Record: {match.away_team_record or 'N/A'}
- Key player: {match.away_team_leader_name or 'N/A'}

{odds_section}

## Instructions
Predict the exact final score (home goals, away goals).
Consider team form, head-to-head history, home advantage, and odds.

Respond ONLY with valid JSON in this exact format:
{{
  "score_home": <int>,
  "score_away": <int>,
  "confidence": <float between 0 and 1>,
  "reasoning": "<brief explanation in 1-2 sentences>"
}}"""


def _build_odds_section(match: Match) -> str:
    lines = ["## Odds"]

    if match.home_ml_close is not None:
        lines.append(f"- Moneyline: Home {match.home_ml_close} | Draw {match.draw_ml_close or 'N/A'} | Away {match.away_ml_close or 'N/A'}")

    if match.total_line is not None:
        lines.append(f"- Over/Under: {match.total_line} (Over {match.over_odds_close or 'N/A'} / Under {match.under_odds_close or 'N/A'})")

    if match.home_spread_line_close is not None:
        lines.append(f"- Spread: Home {match.home_spread_line_close} ({match.home_spread_odds_close or 'N/A'}) | Away {match.away_spread_line_close} ({match.away_spread_odds_close or 'N/A'})")

    if len(lines) == 1:
        return ""

    return "\n".join(lines)
