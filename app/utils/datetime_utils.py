from datetime import UTC, datetime, timedelta


def get_today_range_utc() -> tuple[datetime, datetime]:
    now = datetime.now(UTC)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    
    return start, end

def get_now_utc() -> datetime:
    return datetime.now(UTC)

def ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)