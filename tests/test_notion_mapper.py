from app.config import Settings
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
