# 卷二十：諸星照限游年歌、旺陷宮位（依《太乙統宗寶鑑》煙臺藏本整理）

from __future__ import annotations

from .zhao_you_songs_data import ZHAO_YOU_SONGS

# 諸星旺宮（卷二十「諸星上中下三等」旺地摘要）
STAR_WANG_ZHI: dict[str, frozenset[str]] = {
    "五福": frozenset("丑辰申亥"),
    "君基": frozenset("丑辰午未戌"),
    "臣基": frozenset("丑辰未戌"),
    "民基": frozenset("子辰申亥"),
    "文昌": frozenset("丑辰申亥"),
    "計神": frozenset("辰戌丑未"),
    "小游": frozenset("亥卯未寅"),
    "主大": frozenset("巳酉丑申"),
    "客大": frozenset("申子辰亥"),
    "始擊": frozenset("寅午戌巳"),
    "飛符": frozenset("寅午戌巳"),
    "四神": frozenset("申子辰亥"),
    "天乙": frozenset("巳酉丑申"),
    "地乙": frozenset("辰戌丑未"),
    "主參": frozenset("申子辰亥"),  # 主泰將
    "客參": frozenset("亥卯未辰"),  # 客泰將
}

STAR_XIAN_ZHI: dict[str, frozenset[str]] = {
    "五福": frozenset("寅卯"),
    "君基": frozenset("亥寅卯酉"),
    "文昌": frozenset("寅卯子"),
    "小游": frozenset("巳午申酉"),
    "始擊": frozenset("亥子卯酉申"),
    "天乙": frozenset("午寅"),
    "主大": frozenset("寅午戌亥"),
    "客大": frozenset("巳午卯戌"),
}

# 陽九入三限斷語（卷二十）
SAN_XIAN_DUAN = {
    "初限": {
        "吉": "陽九入初限吉星之宮：黑頭富貴，早年發達。",
        "凶": "陽九入初限關囚掩擊之宮：幼年破祖身孤，飘荡；入命身更逢惡星，主幼年徒刑。",
    },
    "中限": {
        "吉": "陽九入中限吉星之宮：中年富貴榮顯，祿位亨通。",
        "凶": "陽九入中限格對迫擊之宮：中年多傷婚嗣，進退多憂。",
    },
    "末限": {
        "吉": "陽九入末限吉星之宮：晚年富貴雍容，享福高壽。",
        "凶": "陽九入末限關囚掩擊迫絕之宮：晚年刑禍破蕩身孤，難得善終。",
    },
}

_STAR_NAMES = (
    "主參", "客參", "主大", "客大", "始擊", "文昌", "計神", "小游",
    "君基", "臣基", "民基", "五福", "飛符", "四神", "天乙", "地乙",
)

_JI_STARS = frozenset({"五福", "君基", "臣基", "民基", "文昌", "計神"})
_XIONG_STARS = frozenset({"始擊", "飛符", "天乙"})


def _extract_star_names(star_tokens: list[str]) -> set[str]:
    found: set[str] = set()
    blob = "".join(star_tokens)
    for n in _STAR_NAMES:
        if n in blob:
            found.add(n)
    return found


def _star_wang_xian(star: str, zhi: str) -> str:
    if zhi in STAR_WANG_ZHI.get(star, ()):
        return "旺"
    if zhi in STAR_XIAN_ZHI.get(star, ()):
        return "陷"
    return "平"


def match_zhao_you_songs(
    zhao_stars: list[str],
    you_stars: list[str],
    zhao_zhi: str,
    you_zhi: str,
) -> list[dict]:
    """依照限／游年宮星匹配歌訣（卷二十全文）。"""
    zhao_set = _extract_star_names(zhao_stars)
    you_set = _extract_star_names(you_stars)
    hits: list[dict] = []
    seen: set[str] = set()
    for rule in ZHAO_YOU_SONGS:
        need = set(rule["stars"])
        in_zhao = need <= zhao_set
        in_you = need <= you_set
        if not (in_zhao or in_you):
            continue
        zhi = zhao_zhi if in_zhao else you_zhi
        stars_here = zhao_set if in_zhao else you_set
        if rule.get("need_wang"):
            if not any(_star_wang_xian(s, zhi) == "旺" for s in need & stars_here):
                continue
        if rule.get("need_xian"):
            if not any(_star_wang_xian(s, zhi) == "陷" for s in need & stars_here):
                continue
        text = "".join(rule["lines"])
        if text in seen:
            continue
        seen.add(text)
        hits.append({
            "星": "、".join(rule["stars"]),
            "照限": in_zhao,
            "游年": in_you,
            "歌訣": text,
        })
    return hits


def zhao_you_song_coverage() -> dict[str, int]:
    """各星照限游年歌條目數（供測試／文檔）。"""
    counts: dict[str, int] = {}
    for rule in ZHAO_YOU_SONGS:
        for star in rule["stars"]:
            counts[star] = counts.get(star, 0) + 1
    return counts


def classify_san_xian_ji_xiong(star_names: set[str]) -> str:
    if star_names & _JI_STARS and not (star_names & _XIONG_STARS):
        return "吉"
    if star_names & _XIONG_STARS:
        return "凶"
    return "平"