# backend

AWS SAM で構成するバックエンド。Lambda 2 本（収集・閲覧）+ DynamoDB + API Gateway + S3/CloudFront。

## ローカルセットアップ

```bash
uv sync      # .venv を作成し全依存をインストール
make test    # 全テストが passed であることを確認
```

### よく使うコマンド

```bash
make test      # テスト実行
make sync      # 依存の再インストール
make compile   # pyproject.toml 変更後に requirements.txt を再生成
```

### ローカルで Lambda を動かす

```bash
sam build

# 閲覧 API をローカル起動（http://localhost:3000）
sam local start-api

# 収集 Lambda を 1 回だけ手動実行
sam local invoke CollectorFunction
```

## デプロイ（バックエンド）

```bash
sam build
sam deploy
```

## ディレクトリ構成

```text
backend/
├── src/
│   ├── api/            # 閲覧 Lambda（GET /wards, GET /observations）
│   │   ├── app.py          # lambda_handler（エントリポイント）
│   │   ├── routers/        # ルーティング・レスポンス組み立て
│   │   ├── repositories/   # DynamoDB アクセス
│   │   └── tests/
│   ├── collector/      # 収集 Lambda（毎時スクレイピング → DynamoDB）
│   │   ├── app.py
│   │   ├── scraper.py      # weathernews.jp をスクレイピング
│   │   └── tests/
│   └── layers/
│       └── common/     # 両 Lambda が共有するコード
│           └── python/
│               ├── wards.py    # 23区コード↔名前のマッピング
│               └── schemas.py  # データクラス定義（Observation, Ward）
├── template.yaml       # SAM テンプレート（インフラ定義）
├── samconfig.toml      # デプロイ設定（スタック名・リージョン等）
├── pyproject.toml      # 依存管理（uv）
└── Makefile
```

### 閲覧 Lambda の層構造

```text
lambda_handler (app.py)
    └── Router (routers/weather.py)   # パス振り分け・バリデーション・レスポンス組み立て
            └── Repository (repositories/weather_repository.py)  # DynamoDB クエリ
```
