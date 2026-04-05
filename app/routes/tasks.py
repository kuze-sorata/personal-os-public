from datetime import datetime

from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.services.google_calendar_service import GoogleCalendarService
from app.services.notion_service import NotionService
from app.services.priority_engine import PriorityEngine


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/today")
def get_today_tasks(settings: Settings = Depends(get_settings)) -> dict[str, object]:
    today = datetime.now().astimezone().date()
    notion_service = NotionService(settings)
    calendar_service = GoogleCalendarService(settings)
    priority_engine = PriorityEngine()

    tasks = notion_service.get_open_tasks()
    events = calendar_service.get_today_events(today)
    free_blocks = calendar_service.calculate_free_blocks(events, today)
    selected = priority_engine.select_top_tasks(tasks, free_blocks, today)
    return {"tasks": [task.model_dump() for task in selected]}

