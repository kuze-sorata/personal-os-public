from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

from app.config import Settings
from app.models.calendar_event import CalendarEvent
from app.models.task import Task


class MockDataService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.base_dir = Path(settings.mock_data_dir)

    def load_tasks(self) -> list[Task]:
        payload = self._load_json("tasks.json")
        return [
            Task(
                id=item["id"],
                name=item["name"],
                deadline=datetime.fromisoformat(item["deadline"]) if item.get("deadline") else None,
                status=item.get("status", "Not Started"),
                today_candidate=item.get("today_candidate", False),
            )
            for item in payload
        ]

    def load_calendar_events(self, target_date: date) -> list[CalendarEvent]:
        payload = self._load_json("calendar_events.json")
        return [
            CalendarEvent(
                title=item["title"],
                start=datetime.fromisoformat(item["start"]),
                end=datetime.fromisoformat(item["end"]),
            )
            for item in payload
            if datetime.fromisoformat(item["start"]).date() == target_date
        ]

    def _load_json(self, filename: str) -> Any:
        with (self.base_dir / filename).open("r", encoding="utf-8") as file:
            return json.load(file)
