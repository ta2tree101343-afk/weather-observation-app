"""
weathernews.jp 観測値パーサー
==============================
class="dataTable"（実況天気・観測値）から
「日時・気温・風速・降水量（＋風向）」を構造化データとして抽出する。

ポイント:
  - このテーブルは予報ではなく「観測済みの過去1時間ごとの値」=課題の「過去データ」。
  - 時刻欄は「12時」「24時」のように"時"しか無く日付が無いので、
    新しい行→古い行の並びを使って日付を復元する（時が増えたら前日に繰り下げる）。
  - 「24時」は 0:00 として扱う。
"""

import json
import sys
from datetime import datetime, timedelta, timezone

from bs4 import BeautifulSoup

JST = timezone(timedelta(hours=9))


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
        return []

    rows = table.select("tbody tr")
    if base_date is None:
        base_date = datetime.now(JST)
    current_date = base_date.date()

    records = []
    prev_hour = None

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

        # 新しい→古い順なので、時が前の行より大きくなったら日付を前日へ
        if prev_hour is not None and hour > prev_hour:
            current_date -= timedelta(days=1)
        prev_hour = hour

        dt = datetime(current_date.year, current_date.month, current_date.day,
                      hour, 0, 0, tzinfo=JST)

        records.append({
            "datetime": dt.isoformat(),           # 例: 2026-06-20T12:00:00+09:00
            "temperature": to_float(cells[1]),    # 気温(℃)
            "wind_speed": to_float(cells[2]),     # 風速(m/s)
            "wind_direction": cells[3] or None,   # 風向（おまけ）
            "precipitation": to_float(cells[4]),  # 降水量(mm/h)
        })

    return records


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "debug_page.html"
    try:
        with open(path, encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError:
        print(f"✗ {path} が見つかりません。先に check_weathernews.py を実行してください。")
        return

    records = parse_observation_table(html)
    if not records:
        print("✗ 観測値テーブル(table.dataTable)が見つかりませんでした。")
        return

    print(f"✓ {len(records)} 件の観測データを抽出しました。\n")
    print(f"{'日時':<27} {'気温':>6} {'風速':>6} {'風向':>5} {'降水':>6}")
    print("-" * 54)
    for r in records:
        temp = "-" if r["temperature"] is None else f"{r['temperature']:.1f}"
        wind = "-" if r["wind_speed"] is None else f"{r['wind_speed']:.0f}"
        prec = "-" if r["precipitation"] is None else f"{r['precipitation']:.0f}"
        print(f"{r['datetime']:<27} {temp:>6} {wind:>6} {r['wind_direction'] or '-':>5} {prec:>6}")

    with open("observation.json", "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print("\n→ observation.json に保存しました（DynamoDB保存処理の入力に使えます）。")


if __name__ == "__main__":
    main()
