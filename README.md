# Personal OS (Public Demo)

[![CI](https://github.com/kuze-sorata/personal-os-public/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/kuze-sorata/personal-os-public/actions/workflows/ci.yml)

A mock-safe backend that recommends **Top 3 tasks for today** from task + calendar inputs.

## What It Does

- ranks open tasks with simple, explainable rules (`Deadline` + `TodayCandidate`)
- generates a morning summary (schedule, top tasks)
- generates a night review (done/incomplete tasks, tomorrow schedule)
- runs fully in `USE_MOCK_DATA=true` for safe public review

## System Overview

<img src="docs/assets/system-overview.png" alt="System Overview" width="760" />

## Mock-Safe Boundary

<img src="docs/assets/mock-safe-boundary.png" alt="Mock-Safe Boundary" width="760" />

Public demo uses only:

- [mock_data/tasks.json](mock_data/tasks.json)
- [mock_data/calendar_events.json](mock_data/calendar_events.json)

No live credentials or real API calls are required.

## Telegram Output Sample

<img src="docs/assets/telegram-output.jpg" alt="Telegram Output" width="420" />

## Quick Start

For a step-by-step guide, see [docs/STARTUP_GUIDE.md](docs/STARTUP_GUIDE.md).

If you want the shortest possible setup, run:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
USE_MOCK_DATA=true uvicorn app.main:app --reload
```

## Demo Endpoints

- `GET /health`
- `POST /jobs/morning`
- `POST /jobs/night`

## Local Setup

### 1. Create the environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 2. Enable mock mode

Public demo should run with mock data only.

```bash
export USE_MOCK_DATA=true
```

You can also prefix the command directly:

```bash
USE_MOCK_DATA=true uvicorn app.main:app --reload
```

### 3. Start the app

```bash
uvicorn app.main:app --reload
```

### 4. Open the demo

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/jobs/morning`
- `http://127.0.0.1:8000/jobs/night`

## What You See

- the morning job selects the top 3 tasks
- the night job summarizes completed and incomplete items
- mock data keeps the demo safe and self-contained

## Test

```bash
./.venv/bin/pytest -q
```

## Stack

- Python
- FastAPI
- pytest
