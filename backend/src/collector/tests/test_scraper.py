import pytest
from datetime import datetime, timedelta, timezone
from scraper import parse_observation_table

JST = timezone(timedelta(hours=9))


def test_parse_raises_when_table_not_found():
    html = "<html><body><p>no table here</p></body></html>"
    with pytest.raises(ValueError, match="observation table not found"):
        parse_observation_table(html)


def test_parse_returns_records_for_valid_table():
    html = """<html><body>
    <table class="dataTable">
    <tbody>
    <tr><td>12時</td><td>25.5</td><td>3.2</td><td>北</td><td>0.0</td></tr>
    </tbody>
    </table>
    </body></html>"""
    records = parse_observation_table(html)
    assert len(records) == 1
    assert records[0]["temperature"] == 25.5
    assert records[0]["wind_speed"] == 3.2
    assert records[0]["wind_direction"] == "北"
    assert records[0]["precipitation"] == 0.0


def _make_table_html(*rows):
    trs = "".join(f"<tr>{''.join(f'<td>{c}</td>' for c in row)}</tr>" for row in rows)
    return f'<html><body><table class="dataTable"><tbody>{trs}</tbody></table></body></html>'


def test_parse_future_hour_rolls_back_to_previous_day():
    """00:30 JST 時点で最新行が "23時" → 昨日 23:00 として保存されるべき。"""
    base = datetime(2026, 6, 25, 0, 30, 0, tzinfo=JST)
    html = _make_table_html(
        ("23時", "20.0", "2.0", "南", "0.0"),
        ("22時", "19.5", "1.5", "南", "0.0"),
    )
    records = parse_observation_table(html, base_date=base)
    assert records[0]["datetime"] == "2026-06-24T23:00:00+09:00"
    assert records[1]["datetime"] == "2026-06-24T22:00:00+09:00"


def test_parse_current_hour_stays_on_base_date():
    """14:30 JST 時点で最新行が "14時" → 今日 14:00 として保存されるべき。"""
    base = datetime(2026, 6, 25, 14, 30, 0, tzinfo=JST)
    html = _make_table_html(
        ("14時", "28.0", "3.0", "東", "0.0"),
        ("13時", "27.5", "2.5", "東", "0.0"),
    )
    records = parse_observation_table(html, base_date=base)
    assert records[0]["datetime"] == "2026-06-25T14:00:00+09:00"
    assert records[1]["datetime"] == "2026-06-25T13:00:00+09:00"


def test_parse_handles_missing_numeric_as_none():
    html = """<html><body>
    <table class="dataTable">
    <tbody>
    <tr><td>10時</td><td>-</td><td>--</td><td>静穏</td><td>-</td></tr>
    </tbody>
    </table>
    </body></html>"""
    records = parse_observation_table(html)
    assert records[0]["temperature"] is None
    assert records[0]["wind_speed"] is None
    assert records[0]["precipitation"] is None
