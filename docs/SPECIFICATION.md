# 実装仕様書

## プロジェクト名

Personal Operating System for Daily Focus

## 1. 目的

このシステムは以下を実現する。

- Google Calendar から当日の予定を取得する
- Notion の Task DB から未完了タスクを取得する
- 空き時間を確認しつつ、締切と `TodayCandidate` をもとにその日やるべきタスクを最大3件選ぶ
- 朝に通知する
- 夜に未完了タスクを整理し、次日に持ち越せるようにする

## 2. スコープ

### Version 1

最低限ここまで実装する。

- Google Calendar 連携
- Notion Task DB 連携
- 今日の予定取得
- 今日の空き時間の算出
- 未完了タスク取得
- 優先順位スコアリング
- 今日の3つを選定
- 朝通知
- 夜の未完了整理

補足:

- public demo は `USE_MOCK_DATA=true` を前提に動作する
- demo 用の予定とタスクは `mock_data/` のサンプルデータを使う

## 3. 技術スタック

推奨構成

- Backend: Python + FastAPI
- Scheduler: 手動実行または public GitHub Actions の `workflow_dispatch`
- Data store: Notion Database をそのまま利用
- Calendar: Google Calendar API
- Notification: Telegram Bot API
- Config: `.env`

## 4. システム構成

```text
Google Calendar API
        ↓
   Schedule Fetcher
        ↓
Notion API (Task DB)
        ↓
 Priority Engine
        ↓
 Telegram Notifier
        ↓
 User
```

## 5. データベース設計

### Task Data

- `Name`
- `Deadline`
- `Status`
- `TodayCandidate`

## 6. 優先順位エンジン仕様

- Deadline today `+5`
- Deadline tomorrow `+4`
- Deadline within 3 days `+3`
- `TodayCandidate=true` `+2`
- free block は通知表示に使うが、選定スコアには使わない

## 7. 夜通知仕様

- 未完了タスクだけでなく完了タスクも表示する
- 翌日の予定を Google Calendar から取得し、夜通知に含める
- mock mode では `mock_data/calendar_events.json` の翌日データを使う

## 8. 成功条件

- 毎朝、その日の予定が取得できる
- 未完了タスクから妥当な3タスクが選ばれる
- Telegram に自然な形式で通知できる
- 夜に未完了整理ができる
