from dataclasses import asdict

import wards
from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
    InternalServerError,
    NotFoundError,
    ServiceUnavailableError,
)
from botocore.exceptions import ClientError
from repositories.weather_repository import WeatherRepository

logger = Logger(service="weather-api", child=True)

LIMIT = 60
_ITEM_EXCLUDE = {"ward", "ward_name"}
_TRANSIENT_ERROR_CODES = frozenset(
    {
        "ProvisionedThroughputExceededException",
        "ThrottlingException",
        "RequestLimitExceeded",
        "InternalServerError",
        "ServiceUnavailable",
    }
)


def register(app: APIGatewayHttpResolver, repository: WeatherRepository) -> None:
    @app.get("/wards")
    def get_wards():
        return {"wards": [asdict(w) for w in wards.list_all()]}

    @app.get("/observations")
    def get_observations():
        ward = app.current_event.get_query_string_value("ward")
        if not ward:
            raise BadRequestError("query parameter 'ward' is required")
        if not wards.is_valid(ward):
            raise NotFoundError(f"unknown ward: {ward}")

        try:
            observations = repository.get_observations(ward, LIMIT)
        except ClientError as e:
            code = e.response["Error"]["Code"]
            if code in _TRANSIENT_ERROR_CODES:
                raise ServiceUnavailableError(
                    "観測データの取得に失敗しました。しばらくしてから再度お試しください。"
                )
            raise InternalServerError("観測データの取得に失敗しました。")
        except (KeyError, ValueError, TypeError) as e:
            logger.error("Malformed observation data", ward=ward, error=str(e))
            raise InternalServerError("観測データの処理中にエラーが発生しました。")

        return {
            "ward": ward,
            "ward_name": wards.get_name(ward),
            "count": len(observations),
            "items": [
                {
                    ("datetime" if k == "observed_at" else k): v
                    for k, v in asdict(o).items()
                    if v is not None and k not in _ITEM_EXCLUDE
                }
                for o in observations
            ],
        }
