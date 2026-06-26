# 気象データ管理システム

東京都 23 区の気温・風速・降水量を 1 時間ごとに自動収集し、区ごとに一覧表示する Web アプリ。

**公開 URL:** <https://d17h67joyzv011.cloudfront.net>

## アーキテクチャ

```text
【データ収集（毎時）】
EventBridge ──→ CollectorLambda ──→ DynamoDB
                    │                  ▲
                    └──→ CloudWatch Alarm (FailedWardsCount > 0 で発火)
【閲覧 API】                            │
ブラウザ ──→ API Gateway ──→ APILambda ─┘
  ▲          (GET /wards, GET /observations)
  │
【静的配信】
CloudFront + S3 ──→ ブラウザ (HTML/JS)
```

## 技術スタック

| 層 | 技術 |
| --- | --- |
| フロントエンド | React 19 / TypeScript / Vite / Tailwind CSS v4 |
| バックエンド | Python 3.13 / AWS Lambda / API Gateway |
| データベース | Amazon DynamoDB |
| スケジューラ | Amazon EventBridge Scheduler (1 時間ごと) |
| インフラ定義 | AWS SAM (CloudFormation) |
| 静的配信 | Amazon S3 + CloudFront (OAC) |

## 前提ツール

| ツール | バージョン | 用途 |
| --- | --- | --- |
| Node.js | 20 以上 | フロントエンドのビルド |
| Python | 3.13 | バックエンド Lambda のランタイム |
| [uv](https://docs.astral.sh/uv/) | 最新 | Python 依存管理 |
| AWS CLI | v2 | S3 同期・CloudFront 操作 |
| [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html) | 最新 | Lambda/インフラのデプロイ |
| GNU Make | 3.81 以上 | `make test` / `make sync` の実行 |

## クイックスタート

```bash
git clone <repo-url>
cd weather-observation-app

# バックエンドのテスト
cd backend && uv sync && make test

# フロントエンドの開発サーバー起動
cd ../frontend && npm install
cp .env.example .env   # VITE_API_URL を設定してから起動
npm run dev            # → http://localhost:5173
```

詳細は各 README を参照:

- **バックエンド（Lambda / SAM）** → [`backend/README.md`](backend/README.md)
- **フロントエンド（React / Vite）** → [`frontend/README.md`](frontend/README.md)
