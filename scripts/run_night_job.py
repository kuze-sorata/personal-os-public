from __future__ import annotations

import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config import get_settings
from app.routes.jobs import run_night_job


def main() -> None:
    result = run_night_job(get_settings())
    task_names = [task["name"] for task in result["incomplete_tasks"]]
    print("Night job completed.")
    print("Incomplete tasks:", ", ".join(task_names) if task_names else "none")


if __name__ == "__main__":
    main()
