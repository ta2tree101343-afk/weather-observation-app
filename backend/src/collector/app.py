"""Collector Lambda（フェーズ①のスタブ）
今はまだ収集処理を入れていない。インフラ（DynamoDB/Lambda/Scheduler）が
正しく立ち上がるかを確認するための最小ハンドラ。
次の段階で scraper.py を呼び、23区を取得して DynamoDB に保存する処理を入れる。
"""
import os


def lambda_handler(event, context):
    table_name = os.environ.get("TABLE_NAME")
    print(f"Collector起動。保存先テーブル: {table_name}")
    return {"statusCode": 200, "body": "ok (stub)"}