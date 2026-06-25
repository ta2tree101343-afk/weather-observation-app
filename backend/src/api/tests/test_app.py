import json
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError
from schemas import Observation


def make_event(path, query_params=None):
    return {
        "version": "2.0",
        "rawPath": path,
        "requestContext": {
            "http": {"method": "GET", "path": path},
            "requestId": "test-req-id",
            "stage": "$default",
        },
        "headers": {},
        "queryStringParameters": query_params or {},
    }


def test_get_wards_returns_all_23_wards():
    from app import lambda_handler

    res = lambda_handler(make_event("/wards"), MagicMock())

    assert res["statusCode"] == 200
    body = json.loads(res["body"])
    assert "wards" in body
    assert len(body["wards"]) == 23
    assert body["wards"][0] == {"code": "13101", "name": "千代田区"}


def test_get_observations_returns_400_when_ward_missing():
    from app import lambda_handler

    res = lambda_handler(make_event("/observations"), MagicMock())

    assert res["statusCode"] == 400


def test_get_observations_returns_404_for_unknown_ward():
    from app import lambda_handler

    res = lambda_handler(make_event("/observations", {"ward": "99999"}), MagicMock())

    assert res["statusCode"] == 404


def test_unknown_path_returns_404():
    from app import lambda_handler

    res = lambda_handler(make_event("/unknown"), MagicMock())

    assert res["statusCode"] == 404


@patch("app._repository.get_observations")
def test_get_observations_returns_items_with_floats(mock_get_obs):
    from app import lambda_handler

    mock_get_obs.return_value = [
        Observation(
            ward="13101",
            observed_at="2026-06-22T10:00:00",
            ward_name="千代田区",
            temperature=25.5,
            wind_speed=3.2,
        )
    ]

    res = lambda_handler(make_event("/observations", {"ward": "13101"}), MagicMock())

    assert res["statusCode"] == 200
    body = json.loads(res["body"])
    assert body["ward"] == "13101"
    assert body["ward_name"] == "千代田区"
    assert body["count"] == 1
    assert body["items"][0]["datetime"] == "2026-06-22T10:00:00"
    assert "observed_at" not in body["items"][0]
    assert "ward" not in body["items"][0]
    assert "ward_name" not in body["items"][0]
    assert body["items"][0]["temperature"] == 25.5
    assert body["items"][0]["wind_speed"] == 3.2


@patch("app._repository.get_observations")
def test_get_observations_returns_503_on_throttling(mock_get_obs):
    from app import lambda_handler

    mock_get_obs.side_effect = ClientError(
        {"Error": {"Code": "ProvisionedThroughputExceededException", "Message": "exceeded"}},
        "Query",
    )

    res = lambda_handler(make_event("/observations", {"ward": "13101"}), MagicMock())

    assert res["statusCode"] == 503


@patch("app._repository.get_observations")
def test_get_observations_returns_500_on_permanent_client_error(mock_get_obs):
    from app import lambda_handler

    mock_get_obs.side_effect = ClientError(
        {"Error": {"Code": "AccessDeniedException", "Message": "not authorized"}},
        "Query",
    )

    res = lambda_handler(make_event("/observations", {"ward": "13101"}), MagicMock())

    assert res["statusCode"] == 500


@patch("app._repository.get_observations")
def test_get_observations_returns_500_on_malformed_data(mock_get_obs):
    from app import lambda_handler

    mock_get_obs.side_effect = KeyError("datetime")

    res = lambda_handler(make_event("/observations", {"ward": "13101"}), MagicMock())

    assert res["statusCode"] == 500


@patch("app._repository.get_observations")
def test_get_observations_omits_none_fields(mock_get_obs):
    from app import lambda_handler

    mock_get_obs.return_value = [
        Observation(ward="13101", observed_at="2026-06-22T10:00:00", ward_name="千代田区")
    ]

    res = lambda_handler(make_event("/observations", {"ward": "13101"}), MagicMock())

    body = json.loads(res["body"])
    item = body["items"][0]
    assert "temperature" not in item
    assert "wind_speed" not in item
