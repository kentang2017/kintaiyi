"""卷二十照限游年歌全文匹配測試。"""

from kintaiyi.kintaiyi import Taiyi
from kintaiyi.mingfa_songs import (
    ZHAO_YOU_SONGS,
    match_zhao_you_songs,
    zhao_you_song_coverage,
)


def test_zhao_you_songs_full_coverage_per_star():
    coverage = zhao_you_song_coverage()
    for star in (
        "五福", "君基", "臣基", "民基", "文昌", "小游", "主大", "客大",
        "計神", "始擊", "四神", "天乙", "地乙", "飛符", "主參", "客參",
    ):
        assert coverage.get(star, 0) >= 1, star
    assert len(ZHAO_YOU_SONGS) >= 50


def test_match_zhao_you_songs_dedupes_identical_text():
    hits = match_zhao_you_songs(
        ["五福", "君基"], ["五福"],
        "丑", "辰",
    )
    texts = [h["歌訣"] for h in hits]
    assert len(texts) == len(set(texts))


def test_mingfa_vol20_zhao_you_returns_songs():
    ty = Taiyi(1990, 5, 15, 8, 30)
    life = ty.taiyi_life("男", plate_ji=3)
    zy = life["卷二十"]["照限游年"]
    assert zy["星歌"]
    assert zy["星歌"][0]["歌訣"]
    assert len(zy["星歌"][0]["歌訣"]) > 12
    assert "照限" in zy or "游年" in zy