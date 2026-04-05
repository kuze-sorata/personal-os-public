from datetime import datetime

from pydantic import BaseModel


class Task(BaseModel):
    id: str
    name: str
    category: str = "Unknown"
    priority: str = "Low"
    deadline: datetime | None = None
    estimated_minutes: int = 0
    status: str = "Not Started"
    today_candidate: bool = False
    energy_level: str | None = None
    score: int | None = None

