from datetime import datetime

from app.models.free_block import FreeBlock
from app.models.task import Task
from app.services.priority_engine import PriorityEngine


def make_task(
    task_id: str,
    *,
    priority: str = "Low",
    deadline: datetime | None = None,
    estimated_minutes: int = 30,
    category: str = "Work",
    today_candidate: bool = False,
) -> Task:
    return Task(
        id=task_id,
        name=task_id,
        category=category,
        priority=priority,
        deadline=deadline,
        estimated_minutes=estimated_minutes,
        status="Not Started",
        today_candidate=today_candidate,
        energy_level=None,
    )


def test_near_deadline_task_scores_higher() -> None:
    engine = PriorityEngine()
    today = datetime(2026, 4, 5).date()
    free_blocks = [FreeBlock(start=datetime(2026, 4, 5, 9), end=datetime(2026, 4, 5, 10), minutes=60)]
    urgent = make_task("urgent", priority="Medium", deadline=datetime(2026, 4, 5, 18), estimated_minutes=30)
    later = make_task("later", priority="Medium", deadline=datetime(2026, 4, 9, 18), estimated_minutes=30)

    assert engine.score_task(urgent, free_blocks, today) > engine.score_task(later, free_blocks, today)


def test_short_task_scores_higher_than_long_task() -> None:
    engine = PriorityEngine()
    today = datetime(2026, 4, 5).date()
    free_blocks = [FreeBlock(start=datetime(2026, 4, 5, 9), end=datetime(2026, 4, 5, 12), minutes=180)]
    short_task = make_task("short", priority="Low", estimated_minutes=20)
    long_task = make_task("long", priority="Low", estimated_minutes=120)

    assert engine.score_task(short_task, free_blocks, today) > engine.score_task(long_task, free_blocks, today)


def test_task_that_does_not_fit_block_is_penalized() -> None:
    engine = PriorityEngine()
    today = datetime(2026, 4, 5).date()
    free_blocks = [FreeBlock(start=datetime(2026, 4, 5, 9), end=datetime(2026, 4, 5, 9, 20), minutes=20)]
    fit_task = make_task("fit", estimated_minutes=20)
    oversized_task = make_task("oversized", estimated_minutes=45)

    assert engine.score_task(fit_task, free_blocks, today) > engine.score_task(oversized_task, free_blocks, today)


def test_selection_prefers_category_variety_when_scores_are_equal() -> None:
    engine = PriorityEngine()
    today = datetime(2026, 4, 5).date()
    free_blocks = [FreeBlock(start=datetime(2026, 4, 5, 9), end=datetime(2026, 4, 5, 12), minutes=180)]
    tasks = [
        make_task("work-a", priority="High", category="Work"),
        make_task("work-b", priority="High", category="Work"),
        make_task("study-a", priority="High", category="Study"),
        make_task("life-a", priority="High", category="Life"),
    ]

    selected = engine.select_top_tasks(tasks, free_blocks, today)
    categories = [task.category for task in selected]

    assert "Study" in categories
    assert "Life" in categories

