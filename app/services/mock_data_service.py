from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from app.config import Settings
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
                category=item.get("category", "Unknown"),
                priority=item.get("priority", "Low"),
                deadline=datetime.fromisoformat(item["deadline"]) if item.get("deadline") else None,
                estimated_minutes=item.get("estimated_minutes", 0),
                status=item.get("status", "Not Started"),
                today_candidate=item.get("today_candidate", False),
                energy_level=item.get("energy_level"),
            )
            for item in payload
        ]

    def _load_json(self, filename: str) -> Any:
        with (self.base_dir / filename).open("r", encoding="utf-8") as file:
            return json.load(file)
