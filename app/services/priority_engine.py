from collections import Counter
from datetime import date

from app.models.free_block import FreeBlock
from app.models.task import Task
from app.utils.scoring import deadline_score, estimated_minutes_score


class PriorityEngine:
    PRIORITY_SCORES = {
        "High": 5,
        "Medium": 3,
        "Low": 1,
    }

    def score_task(self, task: Task, free_blocks: list[FreeBlock], today_date: date) -> int:
        score = 0
        score += self.PRIORITY_SCORES.get(task.priority, 0)
        score += deadline_score(task.deadline.date() if task.deadline else None, today_date)
        score += estimated_minutes_score(task.estimated_minutes)
        if task.today_candidate:
            score += 2
        score += 3 if self._fits_any_block(task, free_blocks) else -3
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
                not self._fits_any_block(task, free_blocks),
                -(task.score or 0),
                task.estimated_minutes,
                task.name.lower(),
            ),
        )

        selected: list[Task] = []
        category_counts: Counter[str] = Counter()
        remaining = sorted_tasks[:]

        while remaining and len(selected) < limit:
            candidate = self._pick_next_task(remaining, category_counts, free_blocks)
            selected.append(candidate)
            category_counts[candidate.category] += 1
            remaining = [task for task in remaining if task.id != candidate.id]

        return selected

    def _pick_next_task(
        self,
        tasks: list[Task],
        category_counts: Counter[str],
        free_blocks: list[FreeBlock],
    ) -> Task:
        lowest_count = min((category_counts.get(task.category, 0) for task in tasks), default=0)
        diversified = [task for task in tasks if category_counts.get(task.category, 0) == lowest_count]
        candidates = diversified or tasks
        return sorted(
            candidates,
            key=lambda task: (
                not self._fits_any_block(task, free_blocks),
                -(task.score or 0),
                category_counts.get(task.category, 0),
                task.estimated_minutes,
                task.name.lower(),
            ),
        )[0]

    @staticmethod
    def _fits_any_block(task: Task, free_blocks: list[FreeBlock]) -> bool:
        return any(block.minutes >= task.estimated_minutes for block in free_blocks)

