from datetime import datetime

from app.config import Settings
from app.models.calendar_event import CalendarEvent
from app.models.free_block import FreeBlock
from app.models.task import Task
from app.routes.jobs import build_morning_message, run_morning_job


class DummyNotionService:
    def __init__(self, tasks: list[Task]) -> None:
        self.tasks = tasks
        self.synced_ids: set[str] | None = None

    def get_open_tasks(self) -> list[Task]:
        return self.tasks

    def sync_today_candidates(self, selected_task_ids: set[str], tasks: list[Task]) -> None:
        self.synced_ids = selected_task_ids


class DummyTelegramService:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def send_message(self, text: str) -> None:
        self.messages.append(text)


class DummyCalendarService:
    def __init__(self, events: list[CalendarEvent], free_blocks: list[FreeBlock]) -> None:
        self._events = events
        self._free_blocks = free_blocks

    def get_today_events(self, target_date=None) -> list[CalendarEvent]:
        return self._events

    def calculate_free_blocks(self, events, target_date=None) -> list[FreeBlock]:
        return self._free_blocks


def test_build_morning_message_contains_sections() -> None:
    message = build_morning_message(
        events=[
            CalendarEvent(
                title="バイト",
                start=datetime.fromisoformat("2026-04-05T10:00:00+09:00"),
                end=datetime.fromisoformat("2026-04-05T16:00:00+09:00"),
            )
        ],
        free_blocks=[
            FreeBlock(
                start=datetime.fromisoformat("2026-04-05T08:00:00+09:00"),
                end=datetime.fromisoformat("2026-04-05T09:30:00+09:00"),
                minutes=90,
            )
        ],
        tasks=[
            Task(
                id="1",
                name="SQL復習",
                category="Study",
                priority="High",
                deadline=None,
                estimated_minutes=45,
                status="Not Started",
                today_candidate=True,
                energy_level="Medium",
            )
        ],
    )

    assert "今日の予定:" in message
    assert "空き時間:" in message
    assert "今日の3つ:" in message
    assert "SQL復習 (45分)" in message


def test_run_morning_job_works_without_google_events() -> None:
    task = Task(
        id="1",
        name="SQL復習",
        category="Study",
        priority="High",
        deadline=None,
        estimated_minutes=45,
        status="Not Started",
        today_candidate=False,
        energy_level="Medium",
    )
    notion_service = DummyNotionService([task])
    telegram_service = DummyTelegramService()
    calendar_service = DummyCalendarService(
        events=[],
        free_blocks=[
            FreeBlock(
                start=datetime.fromisoformat("2026-04-05T08:00:00+09:00"),
                end=datetime.fromisoformat("2026-04-05T22:00:00+09:00"),
                minutes=840,
            )
        ],
    )

    result = run_morning_job(
        Settings(timezone="Asia/Tokyo"),
        notion_service=notion_service,
        calendar_service=calendar_service,
        telegram_service=telegram_service,
    )

    assert result["selected_tasks"][0]["name"] == "SQL復習"
    assert "予定はありません" in result["message"]
    assert telegram_service.messages
    assert notion_service.synced_ids == {"1"}


def test_run_morning_job_works_in_mock_mode() -> None:
    settings = Settings(use_mock_data=True, mock_data_dir="mock_data", timezone="Asia/Tokyo")

    result = run_morning_job(settings)

    assert len(result["selected_tasks"]) == 3
    assert "今日の3つ:" in result["message"]
    assert "予定はありません" in result["message"]
