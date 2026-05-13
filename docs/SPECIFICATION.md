# 実装仕様書

## プロジェクト名

Personal Operating System for Daily Focus

## 1. 目的

このシステムは以下を実現する。

- Google Calendar から当日の予定を取得する
- Notion の Task DB から未完了タスクを取得する
- 締切と `TodayCandidate` をもとにその日やるべきタスクを最大3件選ぶ
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
- 起動手順は [docs/STARTUP_GUIDE.md](/home/sora/dev/personal-os-public-demo/docs/STARTUP_GUIDE.md) を優先する
- 公開版では live secret や private workspace 依存の説明を入れない

## 3. 技術スタック

推奨構成

- Backend: Python + FastAPI
- Scheduler: 手動実行または public GitHub Actions の `workflow_dispatch`
- Data store: Notion Database をそのまま利用
- Calendar: Google Calendar API
- Notification: Telegram Bot API
- Config: `.env`
- Runtime: `USE_MOCK_DATA=true`

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
- free block は算出するが、選定スコアと朝通知本文には使わない

## 7. 朝通知仕様

- 朝通知は「今日の予定」と「今日の3つ」のみ表示する
- 空き時間は内部計算/API レスポンスには含めるが、通知本文には表示しない

## 8. 夜通知仕様

- 未完了タスクだけでなく完了タスクも表示する
- 翌日の予定を Google Calendar から取得し、夜通知に含める
- mock mode では `mock_data/calendar_events.json` の翌日データを使う

## 9. 成功条件

- 毎朝、その日の予定が取得できる
- 未完了タスクから妥当な3タスクが選ばれる
- Telegram に自然な形式で通知できる
- 夜に未完了整理ができる

## 10. 起動と確認

公開版は、実サービスの認証情報なしで起動できる。

基本手順:

1. 仮想環境を作る
2. `USE_MOCK_DATA=true` を有効にする
3. `uvicorn app.main:app --reload` を起動する

確認先:

- `GET /health`
- `POST /jobs/morning`
- `POST /jobs/night`

参照:

- [起動手順](/home/sora/dev/personal-os-public-demo/docs/STARTUP_GUIDE.md)
