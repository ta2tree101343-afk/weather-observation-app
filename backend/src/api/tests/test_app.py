import json
from decimal import Decimal
from unittest.mock import MagicMock, patch


def make_event(path, query_params=None):
    """HTTP API v2 形式の最小イベントを組み立てる。"""
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


@patch("app.table")
def test_get_wards_returns_all_23_wards(_mock_table):
    from app import lambda_handler

    res = lambda_handler(make_event("/wards"), MagicMock())

    assert res["statusCode"] == 200
    body = json.loads(res["body"])
    assert "wards" in body
    assert len(body["wards"]) == 23
    assert body["wards"][0] == {"code": "13101", "name": "千代田区"}


@patch("app.table")
def test_get_observations_returns_400_when_ward_missing(_mock_table):
    from app import lambda_handler

    res = lambda_handler(make_event("/observations"), MagicMock())

    assert res["statusCode"] == 400


@patch("app.table")
def test_get_observations_returns_404_for_unknown_ward(_mock_table):
    from app import lambda_handler

    res = lambda_handler(make_event("/observations", {"ward": "99999"}), MagicMock())

    assert res["statusCode"] == 404


@patch("app.table")
def test_get_observations_returns_items_with_floats(mock_table):
    from app import lambda_handler

    mock_table.query.return_value = {
        "Items": [
            {
                "ward": "13101",
                "datetime": "2026-06-22T10:00:00",
                "temperature": Decimal("25.5"),
                "wind_speed": Decimal("3.2"),
                "wind_direction": "北",
                "precipitation": Decimal("0.0"),
            }
        ]
    }

    res = lambda_handler(make_event("/observations", {"ward": "13101"}), MagicMock())

    assert res["statusCode"] == 200
    body = json.loads(res["body"])
    assert body["ward"] == "13101"
    assert body["ward_name"] == "千代田区"
    assert body["count"] == 1
    assert body["items"][0]["temperature"] == 25.5
    assert body["items"][0]["wind_speed"] == 3.2


@patch("app.table")
def test_get_observations_uses_custom_limit(mock_table):
    from app import lambda_handler

    mock_table.query.return_value = {"Items": []}

    lambda_handler(make_event("/observations", {"ward": "13101", "limit": "10"}), MagicMock())

    call_kwargs = mock_table.query.call_args.kwargs
    assert call_kwargs["Limit"] == 10


@patch("app.table")
def test_unknown_path_returns_404(mock_table):
    from app import lambda_handler

    res = lambda_handler(make_event("/unknown"), MagicMock())

    assert res["statusCode"] == 404
