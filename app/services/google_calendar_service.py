from datetime import date, datetime, timedelta
from typing import Any

import requests

from app.config import Settings
from app.models.calendar_event import CalendarEvent
from app.models.free_block import FreeBlock
from app.utils.datetime_utils import combine_date_and_hhmm, start_and_end_of_day


class GoogleCalendarService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def is_configured(self) -> bool:
        if self.settings.use_mock_data:
            return False
        return all(
            [
                self.settings.google_client_id,
                self.settings.google_client_secret,
                self.settings.google_refresh_token,
            ]
        )

    def get_today_events(self, target_date: date | None = None) -> list[CalendarEvent]:
        target_date = target_date or datetime.now().astimezone().date()
        if self.settings.use_mock_data:
            return []
        if not self.is_configured():
            return []
        time_min, time_max = start_and_end_of_day(target_date, self.settings.timezone)
        access_token = self._get_access_token()

        response = requests.get(
            f"https://www.googleapis.com/calendar/v3/calendars/{self.settings.google_calendar_id}/events",
            headers={"Authorization": f"Bearer {access_token}"},
            params={
                "timeMin": time_min.isoformat(),
                "timeMax": time_max.isoformat(),
                "singleEvents": "true",
                "orderBy": "startTime",
            },
            timeout=30,
        )
        response.raise_for_status()

        events = []
        for item in response.json().get("items", []):
            start_value = item.get("start", {}).get("dateTime") or item.get("start", {}).get("date")
            end_value = item.get("end", {}).get("dateTime") or item.get("end", {}).get("date")
            if not start_value or not end_value:
                continue
            start = self._parse_google_datetime(start_value)
            end = self._parse_google_datetime(end_value, is_end_date=True)
            events.append(
                CalendarEvent(
                    title=item.get("summary", "Untitled Event"),
                    start=start,
                    end=end,
                )
            )
        return sorted(events, key=lambda event: event.start)

    def calculate_free_blocks(
        self,
        events: list[CalendarEvent],
        target_date: date | None = None,
    ) -> list[FreeBlock]:
        target_date = target_date or datetime.now().astimezone().date()
        day_start = combine_date_and_hhmm(target_date, self.settings.day_start, self.settings.timezone)
        day_end = combine_date_and_hhmm(target_date, self.settings.day_end, self.settings.timezone)
        buffer_delta = timedelta(minutes=self.settings.buffer_minutes)

        adjusted_events = []
        for event in sorted(events, key=lambda item: item.start):
            buffered_start = max(day_start, event.start - buffer_delta)
            buffered_end = min(day_end, event.end + buffer_delta)
            if buffered_end <= day_start or buffered_start >= day_end:
                continue
            adjusted_events.append((buffered_start, buffered_end))

        merged_events: list[tuple[datetime, datetime]] = []
        for start, end in adjusted_events:
            if not merged_events or start > merged_events[-1][1]:
                merged_events.append((start, end))
            else:
                merged_events[-1] = (merged_events[-1][0], max(merged_events[-1][1], end))

        free_blocks: list[FreeBlock] = []
        cursor = day_start
        for start, end in merged_events:
            if start > cursor:
                minutes = int((start - cursor).total_seconds() // 60)
                if minutes >= self.settings.min_block_minutes:
                    free_blocks.append(FreeBlock(start=cursor, end=start, minutes=minutes))
            cursor = max(cursor, end)

        if cursor < day_end:
            minutes = int((day_end - cursor).total_seconds() // 60)
            if minutes >= self.settings.min_block_minutes:
                free_blocks.append(FreeBlock(start=cursor, end=day_end, minutes=minutes))

        return free_blocks

    def _get_access_token(self) -> str:
        response = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": self.settings.google_client_id,
                "client_secret": self.settings.google_client_secret,
                "refresh_token": self.settings.google_refresh_token,
                "grant_type": "refresh_token",
            },
            timeout=30,
        )
        response.raise_for_status()
        token = response.json().get("access_token")
        if not token:
            raise ValueError("Google OAuth token response did not contain access_token")
        return token

    @staticmethod
    def _parse_google_datetime(value: str, is_end_date: bool = False) -> datetime:
        if "T" in value:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))

        parsed = datetime.fromisoformat(f"{value}T00:00:00+00:00")
        if is_end_date:
            return parsed
        return parsed
