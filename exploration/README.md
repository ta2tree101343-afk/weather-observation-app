# スクレイピング検証（スパイク）

weathernews.jp から品川区の過去1時間データを取得できるか検証した記録。

## 結論

- HTTP 200・データはHTMLに直書き（JS描画不要）→ `requests` + `BeautifulSoup` で取得可能
- 取得元は `class="dataTable"`（実況天気・観測値）= 過去の観測値
- 時刻欄に日付が無いため、行の並びから日付を復元（24時→0:00、繰り下げ処理）

## スクリプト

- `check_weathernews.py` … 取得可否の診断
- `explore_tables.py`    … テーブル構造の調査
- `parse_weather.py`     … 時刻・気温・風速・降水量の抽出（日付復元込み）
