from datetime import datetime

from pydantic import BaseModel


class CalendarEvent(BaseModel):
    title: str
    start: datetime
    end: datetime

