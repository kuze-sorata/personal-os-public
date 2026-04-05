# Personal Operating System for Daily Focus

Google Calendar と Notion を使って、その日の予定と未完了タスクから「今日やるべき3つ」を選び、Telegram に通知する FastAPI バックエンドです。

## Features

- Google Calendar から当日の予定を取得
- イベント前後にバッファを加味して空き時間を算出
- Notion Tasks DB から未完了タスクを取得
- 優先度、締切、所要時間、空き時間適合でスコアリング
- カテゴリ分散を意識して最大 3 件を選定
- 朝通知と夜の未完了通知を実行
- 手動実行用の FastAPI エンドポイントを提供

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
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

1. Python 3.11 以上を用意します。
2. 仮想環境を作成して依存関係を入れます。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. `.env.example` を `.env` にコピーして各 API キーを設定します。

```bash
cp .env.example .env
```

4. 開発サーバーを起動します。

```bash
uvicorn app.main:app --reload
```

## Environment Variables

```env
NOTION_API_KEY=
NOTION_TASK_DB_ID=
NOTION_IDEA_DB_ID=
NOTION_DAILY_LOG_DB_ID=

GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REFRESH_TOKEN=
GOOGLE_CALENDAR_ID=primary

TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

DAY_START=08:00
DAY_END=22:00
MIN_BLOCK_MINUTES=20
BUFFER_MINUTES=15
TIMEZONE=Asia/Tokyo
```

## API Endpoints

- `GET /health`
- `POST /jobs/morning`
- `POST /jobs/night`
- `GET /tasks/today`
- `GET /calendar/today`

## Cron Examples

- 毎朝 08:00 に朝ジョブを呼ぶ
- 毎晩 21:00 に夜ジョブを呼ぶ

GitHub Actions、Railway Cron、Vercel Cron、またはサーバー上の `cron` で `POST /jobs/morning` と `POST /jobs/night` を叩く構成を想定しています。

## GitHub Actions Automation

ローカルでサーバーを立てっぱなしにしなくても、GitHub Actions で朝夜ジョブを自動実行できます。設定ファイルは [.github/workflows/scheduled-jobs.yml](/home/sora/dev/personal-os/.github/workflows/scheduled-jobs.yml) です。

やること:

1. このプロジェクトを GitHub リポジトリに置く
2. GitHub の `Settings > Secrets and variables > Actions` を開く
3. 以下の Repository Secrets を追加する

- `NOTION_API_KEY`
- `NOTION_TASK_DB_ID`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `DAY_START`
- `DAY_END`
- `MIN_BLOCK_MINUTES`
- `BUFFER_MINUTES`
- `TIMEZONE`

Google Calendar をあとで使う場合は追加で以下も入れます。

- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REFRESH_TOKEN`
- `GOOGLE_CALENDAR_ID`

このワークフローは日本時間で次の時刻に動くように設定しています。

- 毎朝 08:00 JST
- 毎晩 21:00 JST

手動実行もできます。GitHub の `Actions` タブから `Personal OS Scheduled Jobs` を開き、`Run workflow` で `morning` または `night` を選んで実行してください。

## Testing

```bash
pytest
```

## Notion Tasks DB Setup

`Tasks` データベースを作ったあと、`.env` に `NOTION_API_KEY` と `NOTION_TASK_DB_ID` を入れれば、次のコマンドで必要なプロパティを一括追加できます。

```bash
.venv/bin/python scripts/setup_notion_tasks_db.py
```

`Name` タイトル列は Notion 側で最初から存在する前提です。

## Notes

- Google Calendar は Refresh Token から Access Token を取得して API を呼びます。
- Google 認証情報が未設定の間は、予定なしとして扱い、`DAY_START` から `DAY_END` までを空き時間として朝ジョブを動かせます。
- Notion の `TodayCandidate` は朝ジョブで選ばれたタスクのマークにも使います。
- Night Job は `TodayCandidate = true` かつ `Status != Done` のタスクを通知します。
