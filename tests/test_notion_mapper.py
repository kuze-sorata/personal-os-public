from datetime import datetime

from app.config import Settings
from app.models.task import Task
from app.services.mock_data_service import MockDataService
from app.services.notion_service import NotionService


def test_notion_task_mapping() -> None:
    service = NotionService(Settings(use_mock_data=True))
    page = {
        "id": "task-123",
        "properties": {
            "Name": {"title": [{"plain_text": "Write SQL review"}]},
            "Deadline": {"date": {"start": "2026-04-05T12:00:00+09:00"}},
            "Status": {"select": {"name": "In Progress"}},
            "TodayCandidate": {"checkbox": True},
        },
    }

    task = service._map_task(page)

    assert task.id == "task-123"
    assert task.name == "Write SQL review"
    assert task.status == "In Progress"
    assert task.today_candidate is True


def test_get_selected_tasks_includes_done_tasks_when_today_candidate(monkeypatch) -> None:
    service = NotionService(Settings(use_mock_data=True))

    def fake_load_tasks(self) -> list[Task]:
        return [
            Task(
                id="done-selected",
                name="Done task",
                deadline=datetime.fromisoformat("2026-04-05T10:00:00+09:00"),
                status="Done",
                today_candidate=True,
            ),
            Task(
                id="open-selected",
                name="Open task",
                deadline=datetime.fromisoformat("2026-04-05T11:00:00+09:00"),
                status="In Progress",
                today_candidate=True,
            ),
            Task(
                id="open-not-selected",
                name="Not selected",
                deadline=datetime.fromisoformat("2026-04-05T12:00:00+09:00"),
                status="Not Started",
                today_candidate=False,
            ),
        ]

    monkeypatch.setattr(MockDataService, "load_tasks", fake_load_tasks)

    selected_tasks = service.get_selected_tasks()
    assert {task.id for task in selected_tasks} == {"done-selected", "open-selected"}
