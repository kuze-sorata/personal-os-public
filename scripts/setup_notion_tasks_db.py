from __future__ import annotations

import argparse
import sys
from pathlib import Path

import requests

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config import get_settings


TASKS_PROPERTIES = {
    "Category": {
        "select": {
            "options": [
                {"name": "Life", "color": "blue"},
                {"name": "Work", "color": "green"},
                {"name": "Study", "color": "purple"},
                {"name": "Content", "color": "orange"},
                {"name": "Admin", "color": "gray"},
            ]
        }
    },
    "Priority": {
        "select": {
            "options": [
                {"name": "High", "color": "red"},
                {"name": "Medium", "color": "yellow"},
                {"name": "Low", "color": "blue"},
            ]
        }
    },
    "Deadline": {"date": {}},
    "EstimatedMinutes": {"number": {"format": "number"}},
    "Status": {
        "select": {
            "options": [
                {"name": "Not Started", "color": "default"},
                {"name": "In Progress", "color": "blue"},
                {"name": "Done", "color": "green"},
                {"name": "Deferred", "color": "gray"},
            ]
        }
    },
    "TodayCandidate": {"checkbox": {}},
    "EnergyLevel": {
        "select": {
            "options": [
                {"name": "Low", "color": "gray"},
                {"name": "Medium", "color": "yellow"},
                {"name": "High", "color": "red"},
            ]
        }
    },
    "Recurring": {"checkbox": {}},
    "Notes": {"rich_text": {}},
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Create/update the Notion Tasks DB schema.")
    parser.add_argument(
        "--database-id",
        help="Override NOTION_TASK_DB_ID from .env",
    )
    args = parser.parse_args()

    settings = get_settings()
    database_id = args.database_id or settings.notion_task_db_id
    if not settings.notion_api_key:
        raise SystemExit("NOTION_API_KEY is not set in .env")
    if not database_id:
        raise SystemExit("NOTION_TASK_DB_ID is not set in .env or --database-id")

    headers = {
        "Authorization": f"Bearer {settings.notion_api_key}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }

    response = requests.patch(
        f"https://api.notion.com/v1/databases/{database_id}",
        headers=headers,
        json={"properties": TASKS_PROPERTIES},
        timeout=30,
    )
    response.raise_for_status()

    print("Tasks database schema updated successfully.")


if __name__ == "__main__":
    main()
