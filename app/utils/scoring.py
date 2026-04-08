from datetime import date


def deadline_score(deadline_date: date | None, today_date: date) -> int:
    if deadline_date is None:
        return 0

    delta_days = (deadline_date - today_date).days
    if delta_days <= 0:
        return 5
    if delta_days == 1:
        return 4
    if delta_days <= 3:
        return 3
    return 0
