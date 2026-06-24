"""閲覧API Lambda
HTTP API から呼ばれ、パスに応じて2種類の応答を返す。
  GET /wards                     … 23区の一覧
  GET /observations?ward=13109   … 指定区の観測データ（新しい順）
"""
import json
import os
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver
from aws_lambda_powertools.event_handler.exceptions import BadRequestError, NotFoundError
from aws_lambda_powertools.utilities.typing import LambdaContext

from wards import WARDS

TABLE_NAME = os.environ["TABLE_NAME"]
DEFAULT_LIMIT = 48

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)
logger = Logger(service="weather-api")
tracer = Tracer(service="weather-api")

WARD_NAMES = {code: name for code, name in WARDS}


def _decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


app = APIGatewayHttpResolver(
    serializer=lambda x: json.dumps(x, default=_decimal_default, ensure_ascii=False)
)


@app.get("/wards")
def get_wards():
    wards = [{"code": code, "name": name} for code, name in WARDS]
    logger.info("wards list returned", count=len(wards))
    return {"wards": wards}


@app.get("/observations")
def get_observations():
    ward = app.current_event.get_query_string_value("ward")
    if not ward:
        raise BadRequestError("query parameter 'ward' is required")
    if ward not in WARD_NAMES:
        raise NotFoundError(f"unknown ward: {ward}")

    try:
        limit = int(app.current_event.get_query_string_value("limit") or DEFAULT_LIMIT)
    except (TypeError, ValueError):
        limit = DEFAULT_LIMIT

    result = table.query(
        KeyConditionExpression=Key("ward").eq(ward),
        ScanIndexForward=False,
        Limit=limit,
    )
    items = result.get("Items", [])
    logger.info("observations returned", ward=ward, count=len(items))
    return {
        "ward": ward,
        "ward_name": WARD_NAMES[ward],
        "count": len(items),
        "items": items,
    }


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
