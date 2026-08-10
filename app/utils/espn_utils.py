def safe_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

def pick_logo(logos, rel_key):
    for logo in logos or []:
        if rel_key in (logo.get("rel") or []):
            return logo
    return (logos or [None])[0]

def extract_record_stats_team(team):
    items = (team.get("record") or {}).get("items", [])
    total = next((i for i in items if i.get("type") == "total"), None) or (items[0] if items else None)
    stats = {s.get("name"): s.get("value") for s in (total or {}).get("stats", [])}
    return total, stats

def extract_next_event_team(team_id, team):
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