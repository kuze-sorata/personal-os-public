from datetime import datetime

from pydantic import BaseModel


class Task(BaseModel):
    id: str
    name: str
    deadline: datetime | None = None
    status: str = "Not Started"
    today_candidate: bool = False
    score: int | None = None
