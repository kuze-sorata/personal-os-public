# Project Agent Guide

このファイルは要点だけを置く。
詳細仕様や運用ルールは下記を参照する。

## 参照先

- 仕様書: [docs/SPECIFICATION.md](/home/sora/dev/personal-os/docs/SPECIFICATION.md)
- リポジトリ運用ルール: [REPOSITORY_POLICY.md](/home/sora/dev/personal-os/REPOSITORY_POLICY.md)

## このプロジェクトで重要な前提

- `main` は private production 用ブランチ
- `public-demo` は public portfolio 用ブランチ
- 公開向け変更では secrets や `.env` を扱わない
- 実運用の自動化は private 側で扱う
- 公開用 repo では mock mode を前提にする

## エージェント向け作業ルール

- 実運用に関わる変更は `main` を前提に扱う
- 公開用の説明、mock data、portfolio 向け README は `public-demo` を前提に扱う
- private/public の README を同じブランチ上で往復編集しない
- 仕様判断で迷ったら `docs/SPECIFICATION.md` を優先する
- ブランチ運用や公開範囲で迷ったら `REPOSITORY_POLICY.md` を優先する
