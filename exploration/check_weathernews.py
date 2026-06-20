"""
weathernews.jp データ取得 検証スクリプト
=========================================
目的: 品川区の天気データが「requests だけ」で取れるかを診断する。
     （ヘッドレスブラウザが必要かどうかを、インフラを組む前に見極める）

このスクリプトは「データを保存する」ものではなく、「取れるか調べる」ものです。
判定の流れ:
  [1] ページにアクセスできるか（ステータスコード）
  [2] HTMLに気温などの数値が直接埋まっているか（サーバー描画 or JS描画の判定）
  [3] __NEXT_DATA__ 等の埋め込みJSONがあるか（あれば requests だけでいける＝最短）
  [4] 上記から「次に何をすべきか」を案内

使い方:
  pip install requests beautifulsoup4
  python check_weathernews.py
  # 別のURLで試す場合（DevToolsで見つけた本物のURLを貼る）:
  python check_weathernews.py "https://weathernews.jp/onebox/..."
"""

import json
import sys

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# 設定
# ---------------------------------------------------------------------------
# 品川区のピンポイント天気ページ（候補）。
# ★重要★ このURLは確実ではありません。ブラウザで品川区の天気ページを開き、
#         アドレスバーのURLをここに貼り替えるか、コマンドライン引数で渡してください。
DEFAULT_URL = "https://weathernews.jp/onebox/tenki/tokyo/13109/"

# ブラウザのふりをするためのヘッダ（これが無いとブロックされるサイトが多い）
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ja,en;q=0.9",
}

# HTML内に「天気データらしさ」があるか判定するキーワード
KEYWORDS = ["気温", "風速", "降水", "℃", "m/s", "mm"]

# 埋め込みJSONの中から「気温/風速/降水/時刻」っぽいキーを探すためのヒント
JSON_KEY_HINTS = [
    "temp", "気温", "wind", "風", "rain", "precip", "降水",
    "weather", "hour", "time", "時", "forecast",
]


# ---------------------------------------------------------------------------
# ユーティリティ
# ---------------------------------------------------------------------------
def find_interesting_keys(obj, path="", hits=None, depth=0, max_depth=8):
    """埋め込みJSONを再帰的に歩いて、天気っぽいキーの場所を列挙する。"""
    if hits is None:
        hits = []
    if depth > max_depth or len(hits) > 60:
        return hits

    if isinstance(obj, dict):
        for key, value in obj.items():
            key_path = f"{path}.{key}"
            if any(hint in str(key).lower() for hint in JSON_KEY_HINTS):
                if isinstance(value, (dict, list)):
                    preview = f"<{type(value).__name__} len={len(value)}>"
                else:
                    preview = repr(value)[:60]
                hits.append((key_path, preview))
            find_interesting_keys(value, key_path, hits, depth + 1, max_depth)
    elif isinstance(obj, list):
        # リストは先頭の数件だけ覗く（全部見ると爆発するため）
        for i, value in enumerate(obj[:3]):
            find_interesting_keys(value, f"{path}[{i}]", hits, depth + 1, max_depth)

    return hits


# ---------------------------------------------------------------------------
# メイン
# ---------------------------------------------------------------------------
def main():
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL

    print("=" * 64)
    print(" weathernews.jp 取得可否 診断")
    print("=" * 64)
    print(f"[1] アクセス先:\n    {url}\n")

    # --- アクセス ---
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
    except requests.RequestException as e:
        print(f"  ✗ リクエスト失敗: {e}")
        print("    → URLが正しいか、ネットワーク接続を確認してください。")
        return

    print(f"[2] ステータスコード: {res.status_code}")
    print(f"    HTMLサイズ: {len(res.text):,} 文字\n")

    if res.status_code != 200:
        print("  ✗ 200以外が返りました。")
        print("    → URLが違う / アクセス拒否(403) / ページ無し(404) の可能性。")
        print("    → ブラウザでそのURLが開けるか確認してください。")
        return

    html = res.text
    # あとで目視確認できるよう、生HTMLをファイルに保存しておく
    with open("debug_page.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("    （生HTMLを debug_page.html に保存しました）\n")

    soup = BeautifulSoup(html, "html.parser")

    # --- [3] キーワードがHTMLに直接あるか ---
    print("[3] HTMLに天気っぽいキーワードが直接含まれるか:")
    keyword_found = {kw: (kw in html) for kw in KEYWORDS}
    for kw, ok in keyword_found.items():
        print(f"    {'○' if ok else '×'} {kw}")
    print()

    # --- [4] テーブルの数 ---
    tables = soup.find_all("table")
    print(f"[4] <table> タグの数: {len(tables)}")
    if tables:
        print("    → 表形式で埋まっている可能性。debug_page.html を確認。")
    print()

    # --- [5] 埋め込みJSONを探す（最重要）---
    print("[5] 埋め込みJSON (__NEXT_DATA__ 等) の有無:")
    embedded = None
    source_label = None

    next_data = soup.find("script", id="__NEXT_DATA__")
    if next_data and next_data.string:
        embedded, source_label = next_data.string, "__NEXT_DATA__"
    else:
        # 他の埋め込みパターン（__NUXT__ / __INITIAL_STATE__ 等）も軽く探す
        for script in soup.find_all("script"):
            text = script.string or ""
            if any(token in text for token in ("__NUXT__", "__INITIAL_STATE__", "application/json")):
                embedded, source_label = text, "その他の埋め込みJSON"
                break

    if embedded:
        print(f"    ○ {source_label} を発見！")
        try:
            data = json.loads(embedded.strip().lstrip("window.__NUXT__=").rstrip(";"))
            with open("embedded_data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("    → 中身を embedded_data.json に保存しました。")
            print("    → 天気っぽいキーの候補（path: 値）:")
            hits = find_interesting_keys(data)
            if hits:
                for key_path, preview in hits[:25]:
                    print(f"        {key_path} = {preview}")
            else:
                print("        （自動では見つからず。embedded_data.json を目視確認）")
        except json.JSONDecodeError:
            print("    △ JSONのパースに失敗。embedded_data.json は作れませんでした。")
            print("       debug_page.html を開いて手動で確認してください。")
    else:
        print("    × 埋め込みJSONは見つかりませんでした。")
    print()

    # --- 総合判定 ---
    print("=" * 64)
    print(" 判定")
    print("=" * 64)
    any_keyword = any(keyword_found.values())
    if embedded:
        print(" ◎ 埋め込みJSONあり → requests だけで取得できる見込み大。")
        print("   ヘッドレスブラウザ不要。embedded_data.json から気温等のパスを特定し、")
        print("   そのパスを毎時 Lambda で読む実装に進めます。")
    elif any_keyword and tables:
        print(" ○ HTMLに数値が直接あり → BeautifulSoup でテーブルをパースできそう。")
        print("   debug_page.html のテーブル構造を見て select() を書いてください。")
    else:
        print(" △ HTMLに数値が見当たらない → JavaScript描画の可能性が高い。")
        print("   次の手順で「裏で叩かれているJSON API」を探してください:")
        print("     1. ブラウザで品川区の天気ページを開く")
        print("     2. F12 でDevToolsを開き [Network] タブ → [Fetch/XHR] で絞り込み")
        print("     3. ページを再読み込みし、気温の数値を含むレスポンスを探す")
        print("     4. そのAPIのURLを、このスクリプトの引数に渡して再実行する")
        print("        例: python check_weathernews.py \"https://api...../...\"")
    print("=" * 64)


if __name__ == "__main__":
    main()