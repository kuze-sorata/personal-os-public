from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo


def get_timezone(tz_name: str) -> ZoneInfo:
    return ZoneInfo(tz_name)


def combine_date_and_hhmm(target_date: date, hhmm: str, tz_name: str) -> datetime:
    hour, minute = map(int, hhmm.split(":"))
    return datetime.combine(target_date, time(hour=hour, minute=minute), tzinfo=get_timezone(tz_name))


def start_and_end_of_day(target_date: date, tz_name: str) -> tuple[datetime, datetime]:
    start = combine_date_and_hhmm(target_date, "00:00", tz_name)
    end = start + timedelta(days=1) - timedelta(microseconds=1)
    return start, end


def format_time_range(start: datetime, end: datetime) -> str:
    return f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}"

