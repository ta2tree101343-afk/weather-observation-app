"""weathernews.jp 観測値スクレイパー
指定した区コードのページから、class="dataTable"（実況天気・観測値）を取得し、
「日時・気温・風速・降水量（＋風向）」の構造化データに変換する。

検証スクリプト parse_weather.py の心臓部（観測値テーブルの抽出と日付復元）を
そのまま移植したもの。日付復元の考え方:
  - 観測値テーブルは時刻欄に日付が無く "12時" "24時" のように時だけが入る。
  - 行は新しい順なので、時が前の行より大きくなったら日付を前日へ繰り下げる。
  - "24時" は 0:00 として扱う。
"""

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
    """区コードのページHTMLを取得する。失敗時は例外を送出。"""
    url = BASE_URL.format(code=code)
    res = requests.get(url, headers=HEADERS, timeout=timeout)
    res.raise_for_status()
    return res.text


def to_float(text):
    """数値文字列をfloatに。'-' '--' 空欄などは None。"""
    text = (text or "").strip()
    if text in ("", "-", "--", "―", "−"):
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_observation_table(html, base_date=None):
    """観測値テーブルを解析して辞書のリストを返す（新しい順）。"""
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
        if hour == 24:  # 24時 = 0:00
            hour = 0

        if first:
            # 最新行の時刻が base_date の現在時刻より後なら、その行はまだ来ていない
            # = 起点は前日（例: 00:30 に最新行が "23時" → 昨日23:00）
            if hour > base_date.hour:
                current_date -= timedelta(days=1)
            first = False
        elif prev_hour is not None and hour > prev_hour:
            # 新しい→古い順なので、時が前の行より大きくなったら日付を前日へ
            current_date -= timedelta(days=1)
        prev_hour = hour

        dt = datetime(
            current_date.year, current_date.month, current_date.day, hour, 0, 0, tzinfo=JST
        )

        records.append(
            {
                "datetime": dt.isoformat(),  # 例: 2026-06-20T12:00:00+09:00
                "temperature": to_float(cells[1]),  # 気温(℃)
                "wind_speed": to_float(cells[2]),  # 風速(m/s)
                "wind_direction": cells[3] or None,  # 風向
                "precipitation": to_float(cells[4]),  # 降水量(mm/h)
            }
        )

    return records


def scrape_ward(code, base_date=None):
    """区コードを渡すと、その区の観測データ（新しい順）を返す。"""
    html = fetch_html(code)
    return parse_observation_table(html, base_date=base_date)
