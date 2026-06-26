import json
import os

import boto3
import routers.weather as weather_router
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver
from aws_lambda_powertools.utilities.typing import LambdaContext
from repositories.weather_repository import WeatherRepository

logger = Logger(service="weather-api")
tracer = Tracer(service="weather-api")

app = APIGatewayHttpResolver(serializer=lambda x: json.dumps(x, ensure_ascii=False))

_table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])
_repository = WeatherRepository(_table)
weather_router.register(app, _repository)


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
