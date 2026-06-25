from aws_lambda_powertools import Logger
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from schemas import Observation

logger = Logger(service="weather-api", child=True)


class WeatherRepository:
    def __init__(self, table):
        self._table = table

    def get_observations(self, ward: str, limit: int) -> list[Observation]:
        try:
            result = self._table.query(
                KeyConditionExpression=Key("ward").eq(ward),
                ScanIndexForward=False,
                Limit=limit,
            )
        except ClientError as e:
            logger.error(
                "DynamoDB query failed",
                ward=ward,
                limit=limit,
                error_code=e.response["Error"]["Code"],
            )
            raise
        return [self._to_observation(item) for item in result.get("Items", [])]

    def _to_observation(self, item: dict) -> Observation:
        def to_float(key: str) -> float | None:
            v = item.get(key)
            return float(v) if v is not None else None

        try:
            return Observation(
                ward=item["ward"],
                observed_at=item["datetime"],
                ward_name=item["ward_name"],
                temperature=to_float("temperature"),
                wind_speed=to_float("wind_speed"),
                wind_direction=item.get("wind_direction"),
                precipitation=to_float("precipitation"),
            )
        except (KeyError, ValueError, TypeError) as e:
            logger.error("Malformed DynamoDB item", error=str(e), item_keys=list(item.keys()))
            raise
