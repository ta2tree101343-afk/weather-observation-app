"""Collector Lambda（本実装）
EventBridge Scheduler から1時間ごとに起動され、東京23区の観測データを
weathernews.jp から取得して DynamoDB に保存する。

設計のポイント:
  - 1区が失敗しても全体を止めない（try/except で区ごとに処理）。
  - 相手サーバへの負荷を避けるため、区ごとに少し待つ（SLEEP_SECONDS）。
  - 同じ ward + datetime は上書きになるため、重複は自然に防げる。
"""

import os
import time
from decimal import Decimal

import boto3
from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.typing import LambdaContext
from scraper import scrape_ward
from wards import WARDS

logger = Logger(service="weather-collector")
tracer = Tracer(service="weather-collector")
metrics = Metrics(namespace="WeatherApp", service="weather-collector")

TABLE_NAME = os.environ["TABLE_NAME"]
SLEEP_SECONDS = 1.5

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)


def to_decimal(value):
    """DynamoDB の数値は Decimal で渡す必要がある（float は不可）。"""
    if value is None:
        return None
    return Decimal(str(value))


def build_item(ward_code, ward_name, record):
    """1レコードを DynamoDB の1アイテムに変換する。"""
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


@logger.inject_lambda_context
@tracer.capture_lambda_handler
@metrics.log_metrics
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    total_saved = 0
    failed = []

    with table.batch_writer(overwrite_by_pkeys=["ward", "datetime"]) as batch:
        for code, name in WARDS:
            try:
                records = scrape_ward(code)
                for r in records:
                    batch.put_item(Item=build_item(code, name, r))
                total_saved += len(records)
                logger.info("ward saved", ward_name=name, ward_code=code, count=len(records))
            except Exception as e:
                logger.exception("ward fetch failed", ward_name=name, ward_code=code, error=str(e))
                failed.append(code)
            time.sleep(SLEEP_SECONDS)

    result = {"saved": total_saved, "failed_wards": failed}
    metrics.add_metric(name="FailedWardsCount", unit=MetricUnit.Count, value=len(failed))

    if len(failed) == len(WARDS):
        logger.error("all wards failed", **result)
        raise RuntimeError(f"全区の取得に失敗しました: {failed}")

    if failed:
        logger.warning("collection complete with partial failures", **result)
    else:
        logger.info("collection complete", **result)
    return {"statusCode": 200, "body": result}
