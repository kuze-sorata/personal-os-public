from datetime import datetime

from app.config import Settings
from app.models.calendar_event import CalendarEvent
from app.models.free_block import FreeBlock
from app.models.task import Task
from app.routes.jobs import build_morning_message, run_morning_job, run_night_job


class DummyNotionService:
    def __init__(self, tasks: list[Task]) -> None:
        self.tasks = tasks
        self.synced_ids: set[str] | None = None

    def get_open_tasks(self) -> list[Task]:
        return self.tasks

    def sync_today_candidates(self, selected_task_ids: set[str], tasks: list[Task]) -> None:
        self.synced_ids = selected_task_ids

    def get_selected_open_tasks(self) -> list[Task]:
        return [task for task in self.tasks if task.today_candidate]


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
                deadline=None,
                status="Not Started",
                today_candidate=True,
            )
        ],
    )

    assert "今日の予定:" in message
    assert "空き時間:" in message
    assert "今日の3つ:" in message
    assert "1. SQL復習" in message


def test_run_morning_job_works_without_google_events() -> None:
    task = Task(
        id="1",
        name="SQL復習",
        deadline=None,
        status="Not Started",
        today_candidate=False,
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
        Settings(use_mock_data=True, timezone="Asia/Tokyo"),
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
    assert "Mock Client Call" in result["message"]


def test_run_night_job_includes_tomorrow_schedule() -> None:
    completed_task = Task(
        id="1",
        name="Landing page copyを整える",
        deadline=None,
        status="Done",
        today_candidate=True,
    )
    incomplete_task = Task(
        id="2",
        name="X投稿案を3本メモする",
        deadline=None,
        status="In Progress",
        today_candidate=True,
    )
    notion_service = DummyNotionService([completed_task, incomplete_task])
    telegram_service = DummyTelegramService()
    calendar_service = DummyCalendarService(
        events=[
            CalendarEvent(
                title="Morning Shift",
                start=datetime.fromisoformat("2026-04-06T09:00:00+09:00"),
                end=datetime.fromisoformat("2026-04-06T12:00:00+09:00"),
            )
        ],
        free_blocks=[],
    )

    result = run_night_job(
        Settings(use_mock_data=True, mock_today_date="2026-04-05", timezone="Asia/Tokyo"),
        notion_service=notion_service,
        calendar_service=calendar_service,
        telegram_service=telegram_service,
    )

    assert "今日完了したタスク:" in result["message"]
    assert "- Landing page copyを整える" in result["message"]
    assert "未完了タスク:" in result["message"]
    assert "- X投稿案を3本メモする" in result["message"]
    assert "明日の予定:" in result["message"]
    assert "- 09:00-12:00 Morning Shift" in result["message"]
