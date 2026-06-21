"""
debug_page.html 表構造 調査スクリプト
=====================================
check_weathernews.py が保存した debug_page.html を読み込み、
5つの <table> の中身を要約する。どのテーブルが「1時間ごとデータ」で、
気温/風速/降水量がどの行・どの列にあるかを特定するのが目的。
"""

import sys
from bs4 import BeautifulSoup

PATH = sys.argv[1] if len(sys.argv) > 1 else "debug_page.html"
KEYWORDS = ["気温", "風速", "降水", "℃", "m/s", "mm", "時"]


def summarize_table(index, table):
    print("=" * 60)
    print(f"[table {index}]")

    print(f"  class: {table.get('class')}")

    heading = table.find_previous(["h1", "h2", "h3", "h4", "caption"])
    if heading:
        print(f"  近くの見出し: {heading.get_text(strip=True)[:50]}")

    rows = table.find_all("tr")
    print(f"  行数(tr): {len(rows)}")

    text = table.get_text(" ", strip=True)
    hits = [k for k in KEYWORDS if k in text]
    print(f"  含まれるキーワード: {hits}")

    print("  --- 中身（先頭6行・各行先頭12セル）---")
    for r, tr in enumerate(rows[:6]):
        cells = [c.get_text(strip=True) for c in tr.find_all(["th", "td"])]
        print(f"    行{r} ({len(cells)}列): {cells[:12]}")
    print()


def main():
    try:
        with open(PATH, encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError:
        print(f"✗ {PATH} が見つかりません。")
        print("  先に check_weathernews.py を実行して debug_page.html を作ってください。")
        return

    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")
    print(f"テーブル数: {len(tables)}\n")

    for i, table in enumerate(tables):
        summarize_table(i, table)

    print("=" * 60)
    print("[補足] ℃ を3個以上含む要素（テーブル外に時系列がある場合の手がかり）:")
    found = 0
    for tag in soup.find_all(True):
        # 直接の子テキストだけを見て、深い入れ子を二重カウントしない
        direct_text = "".join(
            c for c in tag.find_all(string=True, recursive=False)
        )
        if direct_text.count("℃") >= 3:
            print(f"    <{tag.name} class={tag.get('class')}>: "
                  f"{direct_text.strip()[:60]}")
            found += 1
            if found >= 5:
                break
    if not found:
        print("    （該当なし。データはテーブル内にある可能性が高い）")
    print("=" * 60)


if __name__ == "__main__":
    main()