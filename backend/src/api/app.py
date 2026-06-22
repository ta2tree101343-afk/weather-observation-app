"""閲覧API Lambda（本実装）
HTTP API から呼ばれ、パスに応じて2種類の応答を返す。
  GET /wards                     … 23区の一覧（画面のセレクタ用）
  GET /observations?ward=13109   … 指定区の観測データ（新しい順）
DynamoDBの数値は Decimal で返るため、JSONにする際 float へ戻す（保存時の逆処理）。
"""
import json
import os
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key

from wards import WARDS

TABLE_NAME = os.environ["TABLE_NAME"]
DEFAULT_LIMIT = 48

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

WARD_NAMES = {code: name for code, name in WARDS}


def _decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def _response(status, body):
    """共通のレスポンス組み立て。CORSヘッダーはAPI Gateway側が付与する。"""
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, ensure_ascii=False, default=_decimal_default),
    }


def handle_wards():
    """23区の一覧を返す"""
    wards = [{"code": code, "name": name} for code, name in WARDS]
    return _response(200, {"wards": wards})


def handle_observations(params):
    """指定区の観測データを新しい順で返す"""
    ward = (params or {}).get("ward")
    if not ward:
        return _response(400, {"error": "query parameter 'ward' is required"})
    if ward not in WARD_NAMES:
        return _response(404, {"error": f"unknown ward: {ward}"})

    try:
        limit = int((params or {}).get("limit", DEFAULT_LIMIT))
    except (TypeError, ValueError):
        limit = DEFAULT_LIMIT

    result = table.query(
        KeyConditionExpression=Key("ward").eq(ward),
        ScanIndexForward=False,
        Limit=limit,
    )
    items = result.get("Items", [])
    return _response(200, {
        "ward": ward,
        "ward_name": WARD_NAMES[ward],
        "count": len(items),
        "items": items,
    })


def lambda_handler(event, context):
    path = event.get("rawPath", "")
    params = event.get("queryStringParameters") or {}

    if path == "/wards":
        return handle_wards()
    if path == "/observations":
        return handle_observations(params)
    return _response(404, {"error": f"not found: {path}"})