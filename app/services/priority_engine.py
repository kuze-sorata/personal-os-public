from datetime import date

from app.models.free_block import FreeBlock
from app.models.task import Task
from app.utils.scoring import deadline_score


class PriorityEngine:
    def score_task(self, task: Task, free_blocks: list[FreeBlock], today_date: date) -> int:
        score = 0
        score += deadline_score(task.deadline.date() if task.deadline else None, today_date)
        if task.today_candidate:
            score += 2
        return score

    def select_top_tasks(
        self,
        tasks: list[Task],
        free_blocks: list[FreeBlock],
        today_date: date,
        limit: int = 3,
    ) -> list[Task]:
        scored_tasks = [
            task.model_copy(update={"score": self.score_task(task, free_blocks, today_date)})
            for task in tasks
        ]
        sorted_tasks = sorted(
            scored_tasks,
            key=lambda task: (
                -(task.score or 0),
                task.deadline.isoformat() if task.deadline else "9999-12-31T23:59:59",
                task.name.lower(),
            ),
        )
        return sorted_tasks[:limit]
