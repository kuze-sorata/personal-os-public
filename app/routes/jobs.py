from datetime import datetime

from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.models.calendar_event import CalendarEvent
from app.models.free_block import FreeBlock
from app.models.task import Task
from app.services.google_calendar_service import GoogleCalendarService
from app.services.notion_service import NotionService
from app.services.priority_engine import PriorityEngine
from app.services.telegram_service import TelegramService
from app.utils.datetime_utils import format_time_range


router = APIRouter(prefix="/jobs", tags=["jobs"])


def build_morning_message(
    events: list[CalendarEvent],
    free_blocks: list[FreeBlock],
    tasks: list[Task],
) -> str:
    schedule_lines = [f"- {format_time_range(event.start, event.end)} {event.title}" for event in events] or ["- 予定はありません"]
    free_block_lines = [f"- {format_time_range(block.start, block.end)}" for block in free_blocks] or ["- 空き時間はありません"]
    task_lines = [f"{index}. {task.name} ({task.estimated_minutes}分)" for index, task in enumerate(tasks, start=1)] or ["- 選定できるタスクがありません"]
    return "\n".join(
        [
            "おはようございます。",
            "",
            "今日の予定:",
            *schedule_lines,
            "",
            "空き時間:",
            *free_block_lines,
            "",
            "今日の3つ:",
            *task_lines,
        ]
    )


def build_night_message(tasks: list[Task]) -> str:
    task_lines = [f"- {task.name}" for task in tasks] or ["- 未完了タスクはありません"]
    return "\n".join(
        [
            "今日の振り返りです。",
            "",
            "未完了タスク:",
            *task_lines,
            "",
            "明日に回すものを確認してください。",
        ]
    )


def run_morning_job(
    settings: Settings,
    notion_service: NotionService | None = None,
    calendar_service: GoogleCalendarService | None = None,
    priority_engine: PriorityEngine | None = None,
    telegram_service: TelegramService | None = None,
) -> dict[str, object]:
    notion_service = notion_service or NotionService(settings)
    calendar_service = calendar_service or GoogleCalendarService(settings)
    priority_engine = priority_engine or PriorityEngine()
    telegram_service = telegram_service or TelegramService(settings)

    today = datetime.now().astimezone().date()
    events = calendar_service.get_today_events(today)
    free_blocks = calendar_service.calculate_free_blocks(events, today)
    tasks = notion_service.get_open_tasks()
    selected_tasks = priority_engine.select_top_tasks(tasks, free_blocks, today, limit=3)
    notion_service.sync_today_candidates({task.id for task in selected_tasks}, tasks)
    message = build_morning_message(events, free_blocks, selected_tasks)
    telegram_service.send_message(message)

    return {
        "events": [event.model_dump() for event in events],
        "free_blocks": [block.model_dump() for block in free_blocks],
        "selected_tasks": [task.model_dump() for task in selected_tasks],
        "message": message,
    }


def run_night_job(
    settings: Settings,
    notion_service: NotionService | None = None,
    telegram_service: TelegramService | None = None,
) -> dict[str, object]:
    notion_service = notion_service or NotionService(settings)
    telegram_service = telegram_service or TelegramService(settings)

    tasks = notion_service.get_selected_open_tasks()
    message = build_night_message(tasks)
    telegram_service.send_message(message)
    return {
        "incomplete_tasks": [task.model_dump() for task in tasks],
        "message": message,
    }


@router.post("/morning")
def morning_job(settings: Settings = Depends(get_settings)) -> dict[str, object]:
    return run_morning_job(settings)


@router.post("/night")
def night_job(settings: Settings = Depends(get_settings)) -> dict[str, object]:
    return run_night_job(settings)

