# 実装仕様書

## プロジェクト名

Personal Operating System for Daily Focus

## 1. 目的

このシステムは以下を実現する。

- Google Calendar から当日の予定を取得する
- Notion の Task DB から未完了タスクを取得する
- 空き時間、締切、優先度、所要時間をもとにその日やるべきタスクを最大3件選ぶ
- 朝に通知する
- 夜に未完了タスクを整理し、次日に持ち越せるようにする
- 発信ネタ管理用の Idea DB も保持する

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

### Version 2

あとから追加する。

- Idea DB 連携
- Instagram / X / note のネタ管理
- 投稿頻度不足の補助
- Daily Log DB 自動記録

## 3. 技術スタック

推奨構成

- Backend: Python + FastAPI
- Scheduler: cron / GitHub Actions / Railway cron / Vercel cron
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
Notion API (Task DB / Idea DB)
        ↓
 Priority Engine
        ↓
 Telegram Notifier
        ↓
 User
```

## 5. データベース設計

### Task DB (Notion)

- `Name` : Title
- `Category` : Select
- `Priority` : Select
- `Deadline` : Date
- `EstimatedMinutes` : Number
- `Status` : Select
- `TodayCandidate` : Checkbox
- `EnergyLevel` : Select
- `Recurring` : Checkbox
- `Notes` : Rich text

## 6. 優先順位エンジン仕様

- High priority `+5`
- Medium priority `+3`
- Low priority `+1`
- Deadline today `+5`
- Deadline tomorrow `+4`
- Deadline within 3 days `+3`
- Estimated minutes 15-30 `+3`
- Estimated minutes 31-60 `+2`
- Estimated minutes 61-90 `+1`
- `TodayCandidate=true` `+2`
- Fits any free block `+3`
- Does not fit any free block `-3`

## 7. 成功条件

- 毎朝、その日の予定が取得できる
- 未完了タスクから妥当な3タスクが選ばれる
- Telegram に自然な形式で通知できる
- 夜に未完了整理ができる
