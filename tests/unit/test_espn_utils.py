from app.utils.espn_utils import (
    extract_next_event_team,
    extract_record_stats_team,
    pick_logo,
    safe_float,
    safe_int,
)


def test_safe_int():
    assert safe_int("123") == 123
    assert safe_int(456) == 456
    assert safe_int("abc") is None
    assert safe_int(None) is None


def test_safe_float():
    assert safe_float("12.34") == 12.34
    assert safe_float(50) == 50.0
    assert safe_float("invalid") is None
    assert safe_float(None) is None


def test_pick_logo():
    logos = [
        {"href": "logo_default.png", "rel": ["default"]},
        {"href": "logo_dark.png", "rel": ["dark", "scoreboard"]},
    ]
    assert pick_logo(logos, "dark") == logos[1]
    assert pick_logo(logos, "nonexistent") == logos[0]
    assert pick_logo([], "dark") is None
    assert pick_logo(None, "dark") is None


def test_extract_record_stats_team():
    team_data = {
        "record": {
            "items": [
                {
                    "type": "total",
                    "stats": [
                        {"name": "wins", "value": 10},
                        {"name": "losses", "value": 2},
                    ],
                }
            ]
        }
    }
    total, stats = extract_record_stats_team(team_data)
    assert total is not None
    assert stats == {"wins": 10, "losses": 2}


def test_extract_record_stats_team_empty():
    total, stats = extract_record_stats_team({})
    assert total is None
    assert stats == {}


def test_extract_next_event_team_empty():
    assert extract_next_event_team(10, {}) == {}
    assert extract_next_event_team(10, {"nextEvent": []}) == {}
    assert extract_next_event_team(10, {"nextEvent": [{}]}) == {}


def test_extract_next_event_team_success():
    raw_team = {
        "nextEvent": [
            {
                "id": "1001",
                "date": "2026-10-10T20:00:00Z",
                "name": "Team A vs Team B",
                "shortName": "A vs B",
                "competitions": [
                    {
                        "venue": {
                            "fullName": "Main Stadium",
                            "address": {"city": "Madrid", "country": "Spain"},
                        },
                        "status": {"type": {"state": "pre", "detail": "Scheduled"}},
                        "competitors": [
                            {"id": "10", "homeAway": "home"},
                            {
                                "id": "20",
                                "homeAway": "away",
                                "team": {"id": "20", "displayName": "Team B"},
                            },
                        ],
                    }
                ],
            }
        ]
    }
    parsed = extract_next_event_team(10, raw_team)
    assert parsed["next_event_id"] == 1001
    assert parsed["next_event_name"] == "Team A vs Team B"
    assert parsed["next_event_home_away"] == "home"
    assert parsed["next_event_opponent_id"] == 20
    assert parsed["next_event_opponent_name"] == "Team B"
    assert parsed["next_event_venue_name"] == "Main Stadium"
    assert parsed["next_event_city"] == "Madrid"
    assert parsed["next_event_country"] == "Spain"
    assert parsed["next_event_status_state"] == "pre"
