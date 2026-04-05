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


def estimated_minutes_score(minutes: int) -> int:
    if 15 <= minutes <= 30:
        return 3
    if 31 <= minutes <= 60:
        return 2
    if 61 <= minutes <= 90:
        return 1
    return 0

