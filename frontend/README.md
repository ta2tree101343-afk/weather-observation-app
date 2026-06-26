# frontend

React + TypeScript + Vite で構築したフロントエンド。CloudFront + S3 で配信。

## ローカルセットアップ

```bash
npm install

# .env を作成して API の向き先を設定
cp .env.example .env
# VITE_API_URL=https://<your-api-id>.execute-api.ap-northeast-1.amazonaws.com

npm run dev    # → http://localhost:5173
```

## コマンド一覧

```bash
npm run dev      # 開発サーバー起動
npm run build    # dist/ を生成（デプロイ用）
npm run preview  # dist/ をローカルでプレビュー（本番ビルドの確認）
npm run lint     # ESLint
npm run format   # Prettier
```

## 環境変数

| 変数名 | 説明 | 例 |
| --- | --- | --- |
| `VITE_API_URL` | バックエンド API のベース URL | `https://xxx.execute-api.ap-northeast-1.amazonaws.com` |

## デプロイ（S3 + CloudFront）

```bash
# 1. ビルド
npm run build

# 2. S3 に同期
BUCKET=$(aws cloudformation describe-stacks \
  --stack-name weather-observation-app \
  --query "Stacks[0].Outputs[?OutputKey=='WebBucketName'].OutputValue" \
  --output text)

aws s3 sync dist "s3://${BUCKET}" --delete

# 3. CloudFront キャッシュを無効化（反映に必要）
DIST_ID=$(aws cloudformation describe-stacks \
  --stack-name weather-observation-app \
  --query "Stacks[0].Outputs[?OutputKey=='WebDistributionId'].OutputValue" \
  --output text)

aws cloudfront create-invalidation --distribution-id "${DIST_ID}" --paths "/*"
```

## 技術スタック

| Category | Technology |
| --- | --- |
| **Framework / Language** | React 19 + TypeScript |
| **Build Tool** | Vite |
| **Styling** | Tailwind CSS v4 |
| **Data Fetching** | SWR |
| **Validation** | Zod |
