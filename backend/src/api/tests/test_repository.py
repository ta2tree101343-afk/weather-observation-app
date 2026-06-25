from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError
from repositories.weather_repository import WeatherRepository


def make_mock_table(items):
    mock_table = MagicMock()
    mock_table.query.return_value = {"Items": items}
    return mock_table


def test_get_observations_converts_decimal_to_float():
    table = make_mock_table(
        [
            {
                "ward": "13101",
                "datetime": "2026-06-22T10:00:00",
                "ward_name": "千代田区",
                "temperature": Decimal("25.5"),
                "wind_speed": Decimal("3.2"),
            }
        ]
    )
    repo = WeatherRepository(table)
    result = repo.get_observations("13101", 10)

    assert len(result) == 1
    assert result[0].temperature == 25.5
    assert isinstance(result[0].temperature, float)
    assert result[0].wind_speed == 3.2


def test_get_observations_handles_missing_optional_fields():
    table = make_mock_table(
        [{"ward": "13101", "datetime": "2026-06-22T10:00:00", "ward_name": "千代田区"}]
    )
    repo = WeatherRepository(table)
    result = repo.get_observations("13101", 10)

    assert result[0].temperature is None
    assert result[0].wind_speed is None
    assert result[0].wind_direction is None
    assert result[0].precipitation is None


def test_get_observations_passes_limit_to_query():
    table = make_mock_table([])
    repo = WeatherRepository(table)
    repo.get_observations("13101", 5)

    table.query.assert_called_once()
    call_kwargs = table.query.call_args.kwargs
    assert call_kwargs["Limit"] == 5
    assert call_kwargs["ScanIndexForward"] is False


def test_get_observations_reraises_client_error():
    mock_table = MagicMock()
    mock_table.query.side_effect = ClientError(
        {"Error": {"Code": "ProvisionedThroughputExceededException", "Message": "exceeded"}},
        "Query",
    )
    repo = WeatherRepository(mock_table)
    with pytest.raises(ClientError):
        repo.get_observations("13101", 10)


def test_get_observations_raises_on_missing_required_field():
    table = make_mock_table([{"ward": "13101", "ward_name": "千代田区"}])  # missing "datetime"
    repo = WeatherRepository(table)
    with pytest.raises(KeyError):
        repo.get_observations("13101", 10)


def test_get_observations_raises_on_invalid_float_field():
    table = make_mock_table(
        [
            {
                "ward": "13101",
                "datetime": "2026-06-22T10:00:00",
                "ward_name": "千代田区",
                "temperature": "N/A",
            }
        ]
    )
    repo = WeatherRepository(table)
    with pytest.raises((ValueError, TypeError)):
        repo.get_observations("13101", 10)
