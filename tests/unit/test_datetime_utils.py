from datetime import UTC, datetime, timedelta, timezone

from app.utils.datetime_utils import ensure_utc, get_now_utc, get_today_range_utc


def test_get_today_range_utc():
    start, end = get_today_range_utc()
    assert start.tzinfo == UTC
    assert end.tzinfo == UTC
    assert (
        start.hour == 0
        and start.minute == 0
        and start.second == 0
        and start.microsecond == 0
    )
    assert end - start == timedelta(days=1)


def test_get_now_utc():
    now = get_now_utc()
    assert now.tzinfo == UTC
    assert (datetime.now(UTC) - now).total_seconds() < 2


def test_ensure_utc_naive():
    dt_naive = datetime(2026, 6, 15, 12, 0, 0)
    dt_utc = ensure_utc(dt_naive)
    assert dt_utc.tzinfo == UTC
    assert dt_utc.year == 2026
    assert dt_utc.month == 6
    assert dt_utc.day == 15
    assert dt_utc.hour == 12


def test_ensure_utc_aware():
    tz_plus_3 = timezone(timedelta(hours=3))
    dt_aware = datetime(2026, 6, 15, 15, 0, 0, tzinfo=tz_plus_3)
    dt_utc = ensure_utc(dt_aware)
    assert dt_utc.tzinfo == UTC
    assert dt_utc.hour == 12
