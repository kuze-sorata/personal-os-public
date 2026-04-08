from datetime import datetime
from typing import Any

import requests

from app.config import Settings
from app.services.mock_data_service import MockDataService
from app.models.task import Task


class NotionService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {settings.notion_api_key}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        }

    def get_open_tasks(self) -> list[Task]:
        if self.settings.use_mock_data:
            return [
                task
                for task in MockDataService(self.settings).load_tasks()
                if task.status != "Done"
            ]
        payload = {
            "filter": {
                "and": [{"property": "Status", "select": {"does_not_equal": "Done"}}]
            }
        }
        response = requests.post(
            f"{self.base_url}/databases/{self.settings.notion_task_db_id}/query",
            headers=self.headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return [self._map_task(page) for page in data.get("results", [])]

    def get_selected_open_tasks(self) -> list[Task]:
        tasks = self.get_open_tasks()
        return [task for task in tasks if task.today_candidate]

    def update_task_status(self, task_id: str, status: str) -> None:
        if self.settings.use_mock_data:
            return
        self._update_page_properties(task_id, {"Status": {"select": {"name": status}}})

    def mark_task_today_candidate(self, task_id: str, value: bool) -> None:
        if self.settings.use_mock_data:
            return
        self._update_page_properties(task_id, {"TodayCandidate": {"checkbox": value}})

    def sync_today_candidates(self, selected_task_ids: set[str], tasks: list[Task]) -> None:
        for task in tasks:
            self.mark_task_today_candidate(task.id, task.id in selected_task_ids)

    def _update_page_properties(self, task_id: str, properties: dict[str, Any]) -> None:
        response = requests.patch(
            f"{self.base_url}/pages/{task_id}",
            headers=self.headers,
            json={"properties": properties},
            timeout=30,
        )
        response.raise_for_status()

    def _map_task(self, page: dict[str, Any]) -> Task:
        properties = page.get("properties", {})
        return Task(
            id=page["id"],
            name=self._title(properties.get("Name")),
            deadline=self._parse_datetime(self._date_start(properties.get("Deadline"))),
            status=self._select_name(properties.get("Status"), default="Not Started"),
            today_candidate=self._checkbox(properties.get("TodayCandidate")),
        )

    @staticmethod
    def _title(prop: dict[str, Any] | None) -> str:
        items = (prop or {}).get("title", [])
        return "".join(item.get("plain_text", "") for item in items).strip()

    @staticmethod
    def _select_name(prop: dict[str, Any] | None, default: str | None = None) -> str | None:
        value = (prop or {}).get("select")
        if value is None:
            return default
        return value.get("name", default)

    @staticmethod
    def _date_start(prop: dict[str, Any] | None) -> str | None:
        value = (prop or {}).get("date")
        if value is None:
            return None
        return value.get("start")

    @staticmethod
    def _checkbox(prop: dict[str, Any] | None) -> bool:
        return bool((prop or {}).get("checkbox", False))

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        if not value:
            return None
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
