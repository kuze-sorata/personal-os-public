# 起動手順

この public demo は、`USE_MOCK_DATA=true` で動かす。

## まず結論

開発中もデモ確認も、次の3つで足りる。

1. 仮想環境を作る
2. mock mode を有効にする
3. FastAPI を起動する

## 手順

### 1. 仮想環境を作る

```bash
cd /home/sora/dev/personal-os-public-demo
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 2. mock mode を有効にする

このリポジトリは public demo なので、実サービスではなく mock data を使う。

```bash
export USE_MOCK_DATA=true
```

毎回コマンドに付けてもよい。

```bash
USE_MOCK_DATA=true uvicorn app.main:app --reload
```

### 3. FastAPI を起動する

```bash
uvicorn app.main:app --reload
```

### 4. ブラウザで開く

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/jobs/morning`
- `http://127.0.0.1:8000/jobs/night`

## 何が起きるか

- morning job は mock のタスクと予定を読み、今日の3つを選ぶ
- night job は mock の完了・未完了をまとめる
- 実サービスの認証情報は不要

## 注意

- `.env` に実運用の秘密情報は入れない
- mock mode 以外では動かさない
