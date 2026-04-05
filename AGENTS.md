実装仕様書
プロジェクト名

Personal Operating System for Daily Focus

目的は、Google Calendar と Notion を連携して、
毎朝「今日やるべき3つ」を自動で決めて通知することです。

1. 目的

このシステムは以下を実現する。

Google Calendar から当日の予定を取得する
Notion の Task DB から未完了タスクを取得する
空き時間、締切、優先度、所要時間をもとに
その日やるべきタスクを最大3件選ぶ
朝に通知する
夜に未完了タスクを整理し、次日に持ち越せるようにする
発信ネタ管理用の Idea DB も保持する
2. スコープ
Version 1

最低限ここまで実装する。

Google Calendar 連携
Notion Task DB 連携
今日の予定取得
今日の空き時間の算出
未完了タスク取得
優先順位スコアリング
今日の3つを選定
朝通知
夜の未完了整理
Version 2

あとから追加する。

Idea DB 連携
Instagram / X / note のネタ管理
投稿頻度不足の補助
Daily Log DB 自動記録
3. 技術スタック
推奨構成
Backend: Python + FastAPI
Scheduler: cron / GitHub Actions / Railway cron / Vercel cron
Data store: Notion Database をそのまま利用
Calendar: Google Calendar API
Notification: Telegram Bot API
Config: .env

Python を推奨する理由:

API連携がシンプル
データ処理がやりやすい
将来的にAI処理を足しやすい
4. システム構成
Google Calendar API
        ↓
   Schedule Fetcher
        ↓
Notion API (Task DB / Idea DB)
        ↓
 Priority Engine
        ↓
 Telegram Notifier
        ↓
 User

Night Job
    ↓
- 未完了タスク整理
- Daily Log更新
- 翌日持ち越し候補作成
5. データベース設計
5.1 Task DB (Notion)

データベース名: Tasks

プロパティ
Name : Title
Category : Select
Life
Work
Study
Content
Admin
Priority : Select
High
Medium
Low
Deadline : Date
EstimatedMinutes : Number
Status : Select
Not Started
In Progress
Done
Deferred
TodayCandidate : Checkbox
EnergyLevel : Select
Low
Medium
High
Recurring : Checkbox
Notes : Rich text
用途
日々の実行タスク管理
朝の優先選定対象
5.2 Idea DB (Notion)

データベース名: Ideas

プロパティ
Title : Title
Platform : Multi-select
Instagram
X
note
Type : Select
Daily Life
Insight
Learning
Comparison
Draft
Content : Rich text
Priority : Select
High
Medium
Low
Status : Select
Inbox
Drafting
Published
CreatedAt : Date
用途
発信ネタのストック
将来的な投稿候補抽出
5.3 Daily Log DB (Version 2)

データベース名: Daily Logs

プロパティ
Date : Date
CompletedTasks : Rich text
IncompleteTasks : Rich text
Learnings : Rich text
IdeasCaptured : Rich text
TopTaskTomorrow : Rich text
6. Google Calendar 仕様

対象カレンダー:

Primary calendar
必要なら専用 calendar（例: Work Blocks）

取得対象:

当日 00:00 - 23:59 のイベント

取得項目:

title
start datetime
end datetime

除外条件:

free 扱いのイベントは除外しない
all-day event は予定ありとして扱うか、設定可能にする
7. 空き時間算出ロジック
入力
当日のイベント一覧
起床時刻 / 就寝時刻
バッファ時間
設定値
DAY_START = 08:00
DAY_END = 22:00
MIN_BLOCK_MINUTES = 20
BUFFER_MINUTES = 15
出力
空き時間ブロックの配列

例:

[
  { "start": "08:00", "end": "09:30", "minutes": 90 },
  { "start": "16:30", "end": "18:00", "minutes": 90 },
  { "start": "20:00", "end": "21:00", "minutes": 60 }
]
8. 優先順位エンジン仕様
目的

未完了タスクから、今日実行すべきタスクを最大3つ選ぶ。

対象条件
Status != Done
EstimatedMinutes > 0
空き時間に入るものを優先
スコアリングルール

各タスクにスコアを与える。

基本点
Priority = High → +5
Priority = Medium → +3
Priority = Low → +1
締切補正
Deadline が今日 → +5
Deadline が明日 → +4
Deadline が3日以内 → +3
Deadline 未設定 → +0
所要時間補正
15〜30分 → +3
31〜60分 → +2
61〜90分 → +1
91分以上 → +0
TodayCandidate 補正
True → +2
カテゴリ補正

初期値は補正なし。将来追加可能。

空き時間適合補正
どこかの空き時間ブロックに入る → +3
入らない → -3
選定ルール
スコア順に並べる
空き時間に収まるものを優先
合計3件まで選ぶ
同カテゴリばかりにならないよう、可能なら分散する
9. 朝通知仕様
実行時刻
毎朝 08:00
内容
今日の予定一覧
今日の空き時間
今日の最重要3つ
送信例
おはようございます。

今日の予定:
- 10:00-16:00 バイト
- 18:30-20:00 友人と食事

空き時間:
- 08:00-09:30
- 16:15-18:15
- 20:15-22:00

今日の3つ:
1. X投稿ネタを1本作る（20分）
2. DS学習：SQL復習（45分）
3. インスタの次回リール構成メモ（30分）
10. 夜処理仕様
実行時刻
毎晩 21:00
処理内容
Status != Done の今日選定タスクを抽出
必要なら Deferred に変更しない
未完了一覧を通知
Version 2 では Daily Log DB に記録
送信例
今日の振り返りです。

未完了タスク:
- インスタの次回リール構成メモ
- DS学習：SQL復習

明日に回すものを確認してください。
11. API設計
11.1 Internal Endpoints
GET /health

稼働確認

レスポンス:

{ "status": "ok" }
POST /jobs/morning

朝処理を手動実行

処理:

今日の予定取得
空き時間算出
Task DB 取得
優先選定
Telegram送信
POST /jobs/night

夜処理を手動実行

処理:

未完了整理
Telegram送信
Daily Log更新（Version 2）
GET /tasks/today

今日選定されたタスク一覧を返す

GET /calendar/today

今日の予定一覧と空き時間を返す

12. ディレクトリ構成
personal-os/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── routes/
│   │   ├── health.py
│   │   └── jobs.py
│   ├── services/
│   │   ├── notion_service.py
│   │   ├── google_calendar_service.py
│   │   ├── telegram_service.py
│   │   ├── priority_engine.py
│   │   └── scheduler_service.py
│   ├── models/
│   │   ├── task.py
│   │   ├── calendar_event.py
│   │   └── free_block.py
│   └── utils/
│       ├── datetime_utils.py
│       └── scoring.py
├── tests/
│   ├── test_priority_engine.py
│   ├── test_free_block_calc.py
│   └── test_notion_mapper.py
├── requirements.txt
├── .env.example
└── README.md
13. 環境変数
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
14. 実装要件
14.1 notion_service.py

責務:

Notion DBからタスクを取得
レコードを内部 Task モデルに変換
必要ならタスク更新

必要メソッド:

get_open_tasks() -> list[Task]
get_idea_items() -> list[Idea]
update_task_status(task_id, status)
mark_task_today_candidate(task_id, value)
14.2 google_calendar_service.py

責務:

今日の予定を取得
空き時間を算出

必要メソッド:

get_today_events() -> list[CalendarEvent]
calculate_free_blocks(events) -> list[FreeBlock]
14.3 priority_engine.py

責務:

タスクにスコア付与
今日の3つを選定

必要メソッド:

score_task(task, free_blocks, today_date) -> int
select_top_tasks(tasks, free_blocks, limit=3) -> list[Task]
14.4 telegram_service.py

責務:

メッセージ送信

必要メソッド:

send_message(text: str)
14.5 jobs.py

責務:

朝処理
夜処理

関数:

run_morning_job()
run_night_job()
15. モデル設計
Task
class Task:
    id: str
    name: str
    category: str
    priority: str
    deadline: datetime | None
    estimated_minutes: int
    status: str
    today_candidate: bool
    energy_level: str | None
CalendarEvent
class CalendarEvent:
    title: str
    start: datetime
    end: datetime
FreeBlock
class FreeBlock:
    start: datetime
    end: datetime
    minutes: int
16. テスト要件

最低限、以下をテストする。

単体テスト
締切が近いタスクほどスコアが高くなる
短時間タスクが優先される
空き時間に入らないタスクはスコアが下がる
free block 算出が正しい
結合テスト
Notionから取得したタスクが Task モデルに正しく変換される
Morning Job 実行で Telegram に通知文が生成される
17. 開発ステップ
Step 1

FastAPI プロジェクト作成

Step 2

Notion Task DB 連携

Step 3

Google Calendar 連携

Step 4

free block 算出

Step 5

priority engine 実装

Step 6

Telegram 通知

Step 7

morning job 実装

Step 8

night job 実装

Step 9

テスト追加

Step 10

cron で自動実行

18. 成功条件

このシステムは以下を満たしたら成功。

毎朝、自動でその日の予定が取得できる
Notion の未完了タスクから、妥当な3タスクが選ばれる
Telegram に自然な形式で通知できる
夜に未完了整理ができる
ユーザーは
Google Calendar に予定を入れ、Notion にタスクを追加するだけで回る