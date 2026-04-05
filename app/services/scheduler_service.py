from croniter import croniter


class SchedulerService:
    @staticmethod
    def is_valid_cron(expression: str) -> bool:
        return croniter.is_valid(expression)

