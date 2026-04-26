from datetime import datetime, timedelta, timezone

def get_today_range_utc():
    now = datetime.now(timezone.utc)

    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)

    return start, end


def get_now_utc():
    return datetime.now(timezone.utc)