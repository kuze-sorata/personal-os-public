# Personal OS

Decision-support and workflow-automation backend for daily focus.

This project turns a task list and calendar availability into a short execution plan: what to do today, when it fits, and what to carry over at night.

This public repository is a `mock-safe demo`. It runs only with sample data, requires `USE_MOCK_DATA=true`, and does not use real Notion, Google Calendar, or Telegram credentials.

## What This Repo Shows

- decision-support logic for ranking and selecting the top tasks for the day
- simplified scoring based on deadline pressure and `TodayCandidate`
- workflow automation for morning and night summary generation
- night summaries that include tomorrow's schedule
- a public-safe presentation of the same product idea used in the private production version

## Why It Stands Out

This is not a generic todo app.

The interesting part is the decision layer:

- reduces daily decision friction into a small recommendation loop
- keeps the automation explainable through explicit scoring rules
- shows the same product idea in a safe demo form without exposing personal services

## Public Demo Boundary

- sample tasks are loaded from [mock_data/tasks.json](mock_data/tasks.json)
- sample calendar events are loaded from [mock_data/calendar_events.json](mock_data/calendar_events.json)
- no live API calls are made to Notion, Google Calendar, or Telegram
- generated messages are printed locally in demo mode
- the app refuses to start if `USE_MOCK_DATA` is disabled

## Local Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Example Endpoints

- `GET /health`
- `GET /tasks/today`
- `GET /calendar/today`
- `POST /jobs/morning`
- `POST /jobs/night`

## Stack

- Python
- FastAPI
- pytest

## Notes

The public GitHub Actions workflow is manual-only and always runs with mock settings. It does not read production secrets.

The private production version connects the same workflow to real services and scheduled execution. This public version exists so the decision-support architecture and automation design can be reviewed safely.
