from datetime import datetime, timedelta, timezone

import requests
from bs4 import BeautifulSoup

JST = timezone(timedelta(hours=9))

BASE_URL = "https://weathernews.jp/onebox/tenki/tokyo/{code}/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ja,en;q=0.9",
}


def fetch_html(code, timeout=15):
    url = BASE_URL.format(code=code)
    res = requests.get(url, headers=HEADERS, timeout=timeout)
    res.raise_for_status()
    return res.text


def to_float(text):
    text = (text or "").strip()
    if text in ("", "-", "--", "―", "−"):
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_observation_table(html, base_date=None):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one("table.dataTable")
    if table is None:
        raise ValueError("observation table not found: HTML structure may have changed")

    rows = table.select("tbody tr")
    if base_date is None:
        base_date = datetime.now(JST)
    current_date = base_date.date()

    records = []
    prev_hour = None
    first = True

    for tr in rows:
        cells = [td.get_text(strip=True) for td in tr.find_all("td")]
        if len(cells) < 5:
            continue

        digits = "".join(ch for ch in cells[0] if ch.isdigit())
        if not digits:
            continue
        hour = int(digits)
        if hour == 24:
            hour = 0

        if first:
            if hour > base_date.hour:
                current_date -= timedelta(days=1)
            first = False
        elif prev_hour is not None and hour > prev_hour:
            current_date -= timedelta(days=1)
        prev_hour = hour

        dt = datetime(
            current_date.year, current_date.month, current_date.day, hour, 0, 0, tzinfo=JST
        )

        records.append(
            {
                "datetime": dt.isoformat(),
                "temperature": to_float(cells[1]),
                "wind_speed": to_float(cells[2]),
                "wind_direction": cells[3] or None,
                "precipitation": to_float(cells[4]),
            }
        )

    return records


def scrape_ward(code, base_date=None):
    html = fetch_html(code)
    return parse_observation_table(html, base_date=base_date)
