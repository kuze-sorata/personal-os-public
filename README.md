# Personal OS

Personal OS is a personal productivity backend built with Python and FastAPI.
It selects the top 3 tasks for the day from a task list, estimates available time, and generates a morning summary message.

This public repository is a safe demo version. It runs in `mock mode` with sample task data and does not require real Notion, Google Calendar, or Telegram credentials.
`USE_MOCK_DATA=true` is required in this branch, and the app will refuse to start if mock mode is turned off.

## What It Does

- Loads open tasks from structured data
- Scores tasks by priority, deadline, estimated time, and time-block fit
- Selects up to 3 tasks for today with light category variety
- Builds morning and night summary messages
- Exposes FastAPI endpoints for health, calendar, tasks, and jobs

## Why This Exists

The original idea is to reduce daily decision fatigue.
Instead of manually checking a calendar, scanning a task list, and deciding what matters most, the system prepares a short focused plan automatically.

In the private production version, this flow is connected to real services and runs on a schedule.
In this public version, the same core logic is shown with mock data so the architecture and behavior can be reviewed safely.

## Demo Mode

This repo is locked to public demo mode through environment variables.

```env
USE_MOCK_DATA=true
MOCK_TODAY_DATE=2026-04-05
MOCK_DATA_DIR=mock_data
DAY_START=08:00
DAY_END=22:00
MIN_BLOCK_MINUTES=20
BUFFER_MINUTES=15
TIMEZONE=Asia/Tokyo
```

In mock mode:

- sample tasks are loaded from [mock_data/tasks.json](/home/sora/dev/personal-os/mock_data/tasks.json)
- no real Notion API calls are made
- no real Google Calendar API call is made
- no real Telegram message is sent
- the generated message is printed locally instead

## Tech Stack

- Python
- FastAPI
- requests
- pytest

## Project Structure

```text
personal-os/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── routes/
│   ├── services/
│   ├── models/
│   └── utils/
├── mock_data/
├── scripts/
├── tests/
├── requirements.txt
└── .env.example
```

## Local Setup

1. Create a virtual environment and install dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Create `.env` from the example file.

```bash
cp .env.example .env
```

3. Keep mock mode enabled in `.env`.

```env
USE_MOCK_DATA=true
MOCK_TODAY_DATE=2026-04-05
MOCK_DATA_DIR=mock_data
DAY_START=08:00
DAY_END=22:00
MIN_BLOCK_MINUTES=20
BUFFER_MINUTES=15
TIMEZONE=Asia/Tokyo
```

4. Start the API server.

```bash
uvicorn app.main:app --reload
```

## Example Endpoints

- `GET /health`
- `GET /calendar/today`
- `GET /tasks/today`
- `POST /jobs/morning`
- `POST /jobs/night`

## Running the Demo Jobs

Run the morning job locally:

```bash
python scripts/run_morning_job.py
```

Run the night job locally:

```bash
python scripts/run_night_job.py
```

The public GitHub Actions workflow is manual-only and always runs with mock settings. It does not read production secrets.

## Testing

```bash
pytest
```

## Architecture Notes

- `NotionService` maps external task records into internal `Task` models
- `GoogleCalendarService` calculates free blocks between `DAY_START` and `DAY_END`
- `PriorityEngine` scores and ranks candidate tasks
- `TelegramService` delivers the final message in production and prints it in mock mode

## Security Note

This public repo does not include real API keys, tokens, or personal workspace data.
Production credentials and real automations are kept in a separate private environment.
Do not add real credentials or GitHub Secrets to this public repository.
