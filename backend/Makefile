.PHONY: compile sync test

# pyproject.toml を変更したら make compile を実行する
compile:
	uv pip compile pyproject.toml --group collector -o src/collector/requirements.txt
	uv pip compile pyproject.toml --group api     -o src/api/requirements.txt

# 開発環境の仮想環境を更新する（uv.lock に従いインストール）
sync:
	uv sync --group dev --group collector --group api

test:
	uv run pytest src/api/tests/ src/collector/tests/ -v
