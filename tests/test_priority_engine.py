from datetime import datetime

from app.models.free_block import FreeBlock
from app.models.task import Task
from app.services.priority_engine import PriorityEngine


def make_task(
    task_id: str,
    *,
    deadline: datetime | None = None,
    today_candidate: bool = False,
) -> Task:
    return Task(
        id=task_id,
        name=task_id,
        deadline=deadline,
        status="Not Started",
        today_candidate=today_candidate,
    )


def test_near_deadline_task_scores_higher() -> None:
    engine = PriorityEngine()
    today = datetime(2026, 4, 5).date()
    free_blocks = [FreeBlock(start=datetime(2026, 4, 5, 9), end=datetime(2026, 4, 5, 10), minutes=60)]
    urgent = make_task("urgent", deadline=datetime(2026, 4, 5, 18))
    later = make_task("later", deadline=datetime(2026, 4, 9, 18))

    assert engine.score_task(urgent, free_blocks, today) > engine.score_task(later, free_blocks, today)


def test_today_candidate_scores_higher_than_non_candidate() -> None:
    engine = PriorityEngine()
    today = datetime(2026, 4, 5).date()
    free_blocks = [FreeBlock(start=datetime(2026, 4, 5, 9), end=datetime(2026, 4, 5, 12), minutes=180)]
    preferred = make_task("preferred", today_candidate=True)
    normal = make_task("normal")

    assert engine.score_task(preferred, free_blocks, today) > engine.score_task(normal, free_blocks, today)


def test_selection_prefers_earlier_deadline() -> None:
    engine = PriorityEngine()
    today = datetime(2026, 4, 5).date()
    free_blocks = [FreeBlock(start=datetime(2026, 4, 5, 9), end=datetime(2026, 4, 5, 9, 20), minutes=20)]
    tasks = [
        make_task("later", deadline=datetime(2026, 4, 10, 9)),
        make_task("urgent", deadline=datetime(2026, 4, 5, 9)),
    ]

    selected = engine.select_top_tasks(tasks, free_blocks, today)
    assert selected[0].name == "urgent"
