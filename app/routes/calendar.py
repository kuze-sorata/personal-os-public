from datetime import datetime

from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.services.google_calendar_service import GoogleCalendarService


router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("/today")
def get_today_calendar(settings: Settings = Depends(get_settings)) -> dict[str, object]:
    today = datetime.now().astimezone().date()
    calendar_service = GoogleCalendarService(settings)
    events = calendar_service.get_today_events(today)
    free_blocks = calendar_service.calculate_free_blocks(events, today)
    return {
        "events": [event.model_dump() for event in events],
        "free_blocks": [block.model_dump() for block in free_blocks],
    }

