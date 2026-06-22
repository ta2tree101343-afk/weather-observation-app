"""Collector Lambda（本実装）
EventBridge Scheduler から1時間ごとに起動され、東京23区の観測データを
weathernews.jp から取得して DynamoDB に保存する。

設計のポイント:
  - 1区が失敗しても全体を止めない（try/exceptで区ごとに握りつぶしてログに残す）。
  - 相手サーバへの負荷を避けるため、区ごとに少し待つ（SLEEP_SECONDS）。
  - 同じ ward + datetime は上書きになるため、重複は自然に防げる。
"""

import logging
import os
import time
from decimal import Decimal

import boto3

from scraper import scrape_ward
from wards import WARDS

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TABLE_NAME = os.environ["TABLE_NAME"]
SLEEP_SECONDS = 1.5

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)


def to_decimal(value):
    """DynamoDBの数値はDecimalで渡す必要がある（floatは不可）。"""
    if value is None:
        return None
    return Decimal(str(value))


def build_item(ward_code, ward_name, record):
    """1レコードをDynamoDBの1アイテムに変換する。"""
    item = {
        "ward": ward_code,
        "datetime": record["datetime"],
        "ward_name": ward_name,
    }

    for key in ("temperature", "wind_speed", "precipitation"):
        v = to_decimal(record.get(key))
        if v is not None:
            item[key] = v
    if record.get("wind_direction"):
        item["wind_direction"] = record["wind_direction"]
    return item


def lambda_handler(event, context):
    total_saved = 0
    failed = []

    with table.batch_writer() as batch:
        for code, name in WARDS:
            try:
                records = scrape_ward(code)
                for r in records:
                    batch.put_item(Item=build_item(code, name, r))
                total_saved += len(records)
                logger.info(f"{name}({code}): {len(records)}件 保存")
            except Exception as e:
                logger.exception(f"{name}({code}) 取得失敗: {e}")
                failed.append(code)
            time.sleep(SLEEP_SECONDS)

    result = {"saved": total_saved, "failed_wards": failed}
    logger.info(f"完了: {result}")
    return {"statusCode": 200, "body": result}