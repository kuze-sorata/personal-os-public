from datetime import date, datetime

from app.config import Settings
from app.models.calendar_event import CalendarEvent
from app.services.google_calendar_service import GoogleCalendarService


def test_calculate_free_blocks_applies_buffers_and_min_block() -> None:
    settings = Settings(
        use_mock_data=True,
        day_start="08:00",
        day_end="22:00",
        min_block_minutes=20,
        buffer_minutes=15,
        timezone="Asia/Tokyo",
    )
    service = GoogleCalendarService(settings)
    target_date = date(2026, 4, 5)
    events = [
        CalendarEvent(
            title="Morning Meeting",
            start=datetime.fromisoformat("2026-04-05T10:00:00+09:00"),
            end=datetime.fromisoformat("2026-04-05T11:00:00+09:00"),
        ),
        CalendarEvent(
            title="Dinner",
            start=datetime.fromisoformat("2026-04-05T18:30:00+09:00"),
            end=datetime.fromisoformat("2026-04-05T20:00:00+09:00"),
        ),
    ]

    blocks = service.calculate_free_blocks(events, target_date)

    assert [(block.start.strftime("%H:%M"), block.end.strftime("%H:%M"), block.minutes) for block in blocks] == [
        ("08:00", "09:45", 105),
        ("11:15", "18:15", 420),
        ("20:15", "22:00", 105),
    ]


def test_overlapping_buffered_events_are_merged() -> None:
    settings = Settings(
        use_mock_data=True,
        day_start="08:00",
        day_end="12:00",
        min_block_minutes=20,
        buffer_minutes=15,
        timezone="Asia/Tokyo",
    )
    service = GoogleCalendarService(settings)
    target_date = date(2026, 4, 5)
    events = [
        CalendarEvent(
            title="A",
            start=datetime.fromisoformat("2026-04-05T09:00:00+09:00"),
            end=datetime.fromisoformat("2026-04-05T09:30:00+09:00"),
        ),
        CalendarEvent(
            title="B",
            start=datetime.fromisoformat("2026-04-05T09:35:00+09:00"),
            end=datetime.fromisoformat("2026-04-05T10:00:00+09:00"),
        ),
    ]

    blocks = service.calculate_free_blocks(events, target_date)

    assert [(block.start.strftime("%H:%M"), block.end.strftime("%H:%M")) for block in blocks] == [
        ("08:00", "08:45"),
        ("10:15", "12:00"),
    ]


def test_get_today_events_returns_empty_when_google_is_not_configured() -> None:
    settings = Settings(
        use_mock_data=True,
        google_client_id="",
        google_client_secret="",
        google_refresh_token="",
        timezone="Asia/Tokyo",
    )
    service = GoogleCalendarService(settings)

    events = service.get_today_events(date(2026, 4, 5))

    assert events == []
