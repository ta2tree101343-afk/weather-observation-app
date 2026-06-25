"""東京23区（特別区）の区コードと名前の対応表。
区コードは weathernews.jp のURL（/onebox/tenki/tokyo/{code}/）に使う。
画面表示用の名前もここで一元管理する。
"""
from schemas import Ward

WARDS = [
    ("13101", "千代田区"),
    ("13102", "中央区"),
    ("13103", "港区"),
    ("13104", "新宿区"),
    ("13105", "文京区"),
    ("13106", "台東区"),
    ("13107", "墨田区"),
    ("13108", "江東区"),
    ("13109", "品川区"),
    ("13110", "目黒区"),
    ("13111", "大田区"),
    ("13112", "世田谷区"),
    ("13113", "渋谷区"),
    ("13114", "中野区"),
    ("13115", "杉並区"),
    ("13116", "豊島区"),
    ("13117", "北区"),
    ("13118", "荒川区"),
    ("13119", "板橋区"),
    ("13120", "練馬区"),
    ("13121", "足立区"),
    ("13122", "葛飾区"),
    ("13123", "江戸川区"),
]

_WARD_MAP: dict[str, str] = {code: name for code, name in WARDS}


def is_valid(ward: str) -> bool:
    return ward in _WARD_MAP


def get_name(ward: str) -> str:
    name = _WARD_MAP.get(ward)
    if name is None:
        raise KeyError(f"Unknown ward code: {ward!r}")
    return name


def list_all() -> list[Ward]:
    return [Ward(code=code, name=name) for code, name in WARDS]
