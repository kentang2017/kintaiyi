# 排盤 SVG 語意層：由 pan() 斷事生成扇區 tooltip（P0）

from __future__ import annotations

import math
import re

from . import config
from .taiyidict import su_dist

# 與 chart.gen_chart 十六宮扇區順序一致（起巳順行）
_SIXTEEN_BRANCHES = ("巳", "午", "未", "坤", "申", "酉", "戌", "乾", "亥", "子", "丑", "艮", "寅", "卯", "辰", "巽")
_TWELVE_BRANCHES = ("巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑", "寅", "卯", "辰")
_EIGHT_DOOR_ORDER = ("休", "生", "傷", "杜", "景", "死", "驚", "開")
_GOOD_DOORS = frozenset({"休", "生", "開", "景"})
_PLANET_RING_BRANCHES = ("午", "未", "申", "酉", "戌", "亥", "子", "丑", "寅", "卯", "辰", "巳")
_PLANET_TOKENS = ("日\u3000", "月\u3000", "辰星", "太白", "熒惑", "歲星", "填星", "月孛", "羅睺", "計都")
_PLANET_TOKENS_LIFE = ("日", "月", "辰星", "太白", "熒惑", "歲星", "填星", "月孛", "羅睺", "計都")
_LR_GENERAL_KEYS = "巳午未坤申酉戌乾亥子丑艮寅卯辰巽"
_LR_GENERAL_MAP = dict(
    zip(
        list("貴蛇雀合勾龍空虎常玄陰后"),
        re.findall("..", "貴人螣蛇朱雀六合勾陳青龍天空白虎太常玄武太陰天后"),
    )
)

_PALACE_TEMPLATE = {
    "巳": ("大神", "楚"), "午": ("大威", "荊州"), "未": ("天道", "秦"), "坤": ("大武", "梁州"),
    "申": ("武德", "晉"), "酉": ("太簇", "趙雍"), "戌": ("陰主", "魯"), "乾": ("陰德", "冀州"),
    "亥": ("大義", "衛"), "子": ("地主", "齊兗"), "丑": ("陽德", "吳"), "艮": ("和德", "青州"),
    "寅": ("呂申", "燕"), "卯": ("高叢", "徐州"), "辰": ("太陽", "鄭"), "巽": ("大炅", "揚州"),
}
_BAGUA_BY_GONG_NUM = {
    1: "乾", 2: "離", 3: "艮", 4: "震", 5: "中", 6: "兌", 7: "坤", 8: "坎", 9: "巽",
}
_TE_GONG_BRANCH = {"絳宮": "巳", "明堂": "丑", "玉堂": "卯"}
_SANQI_KEYS = ("太歲青龍旗", "太陰黑旗", "害氣赤旗")
_FEIFU_LABELS = ("飛符", "災殺", "鬼殺", "月殺", "天賊殺", "天史殺")
_MAX_PALACE_LINES = 10
_ROTATION_ANGLE = 248.0
_GEJU_LABEL_FONT_SIZE = 9
_GEJU_LABEL_STROKE_WIDTH = 1.8
_GEJU_SHORT_COLORS: dict[str, tuple[str, str, str]] = {
    "掩": ("#7A1530", "#E8A4B4", "#FFF5F7"),
    "迫": ("#B91C3C", "#F8C0CC", "#FFFFFF"),
    "關": ("#A16207", "#F5D565", "#1C1400"),
    "囚": ("#92400E", "#F0C27A", "#FFFAF0"),
    "擊": ("#881337", "#FDA4AF", "#FFF1F3"),
    "格": ("#581C87", "#D8B4FE", "#FAF5FF"),
    "對": ("#1E4D7B", "#93C5FD", "#EFF6FF"),
    "提": ("#166534", "#86EFAC", "#F0FDF4"),
    "執": ("#3F3F8A", "#C7C9F5", "#F5F6FF"),
    "四": ("#3F4E5C", "#A8BCC8", "#F8FAFC"),
}
_GEJU_TONE_COLORS: dict[str, tuple[str, str, str]] = {
    "danger": ("#B91C3C", "#F8C0CC", "#FFFFFF"),
    "warn": ("#A16207", "#F5D565", "#1C1400"),
    "caution": ("#1E4D7B", "#93C5FD", "#EFF6FF"),
    "info": ("#3F4E5C", "#A8BCC8", "#F8FAFC"),
}


def _clip(text: str, n: int = 72) -> str:
    s = (text or "").strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def _sector_entry(title: str, lines: list[str]) -> dict:
    clean = [str(x).strip() for x in lines if x and str(x).strip()]
    return {"title": title, "lines": clean}


def _geju_lines(geju: dict, *, limit: int = 4) -> list[str]:
    if not geju:
        return []
    lines = []
    for k, v in geju.items():
        if k == "無格局":
            continue
        if isinstance(v, str) and v.strip():
            lines.append(f"{k}：{_clip(v, 48)}")
        elif v:
            lines.append(str(k))
    return lines[:limit]


def _branch_bagua(branch: str) -> str | None:
    if branch in _BAGUA_BY_GONG_NUM.values():
        return branch
    num = config.gong2.get(branch)
    return _BAGUA_BY_GONG_NUM.get(num) if num else None


def _branch_stars(ttext: dict, branch: str) -> list[str]:
    sg = ttext.get("十六宮分佈") or {}
    items = sg.get(branch, [])
    if isinstance(items, list):
        return [str(x) for x in items if x]
    if items:
        return [str(items)]
    return []


def _wuyun_lines(ttext: dict) -> list[str]:
    wl = ttext.get("五運六氣") or {}
    if not wl:
        v10 = ttext.get("卷十") or {}
        wl = v10.get("五運六氣") or {}
    if not wl:
        return []
    lines = []
    yun = wl.get("五運", "")
    buji = wl.get("太過不及", "")
    if yun:
        lines.append(f"五運·{yun}{'·' + buji if buji else ''}")
    sitian = wl.get("司天", "")
    zaiquan = wl.get("在泉", "")
    if sitian or zaiquan:
        lines.append(
            f"司天{sitian}{wl.get('司天化', '')} / 在泉{zaiquan}{wl.get('在泉化', '')}".strip(" /")
        )
    if wl.get("主氣"):
        lines.append(f"主氣·{wl['主氣']}")
    if wl.get("客氣"):
        lines.append(f"客氣·{wl['客氣']}")
    for hit in (wl.get("歲會天符") or [])[:2]:
        lines.append(_clip(str(hit), 56))
    return lines[:4]


def _wuyin_lines(ttext: dict) -> list[str]:
    wy = ttext.get("五音之數") or {}
    if not wy:
        return []
    lines = []
    yuan = wy.get("五音之元")
    if yuan:
        lines.append(_clip(str(yuan), 56))
    for label, key in (
        ("主算", "主算五音"),
        ("客算", "客算五音"),
        ("定算", "定算五音"),
        ("太乙宮", "太乙五音"),
    ):
        block = wy.get(key)
        if isinstance(block, dict) and block.get("五音"):
            lines.append(f"{label}·{block['五音']}")
    return lines[:4]


def _sanqi_lines(ttext: dict, *, branch: str | None = None) -> list[str]:
    sq = ttext.get("三旗行宮") or {}
    if not sq:
        return []
    lines = []
    if branch:
        for name in _SANQI_KEYS:
            if sq.get(name) == branch:
                lines.append(f"{name}在此")
        return lines
    flags = " / ".join(f"{k[-2:] if len(k) > 2 else k}{v}" for k, v in sq.items() if k in _SANQI_KEYS)
    if flags:
        lines.append(f"三旗·{flags}")
    if sq.get("會合"):
        lines.append(_clip(str(sq["會合"]), 56))
    return lines


def _noble_god_lines(ttext: dict, *, branch: str | None = None, bagua: str | None = None) -> list[str]:
    ng = ttext.get("九宮貴神") or {}
    v10 = ttext.get("卷十") or {}
    if not ng:
        ng = v10.get("九宮貴神") or {}
    if not ng:
        return []
    lines = []
    if branch is None:
        if ng.get("直事貴神"):
            lines.append(f"直事貴神·{ng['直事貴神']}")
        for item in (v10.get("歲會天符") or [])[:2]:
            if "貴神" in str(item):
                lines.append(_clip(str(item), 56))
        return lines[:3]
    dist = ng.get("九宮貴神分布") or {}
    god = dist.get(bagua) if bagua else None
    if god:
        lines.append(f"貴神·{god}")
        if ng.get("直事貴神") == god:
            lines.append("直事貴神臨此")
    return lines


def _nine_star_lines(ttext: dict, bagua: str | None) -> list[str]:
    if not bagua:
        return []
    lines = []
    ts = ttext.get("太乙九星") or {}
    dist = ts.get("九星分布") or {}
    star = dist.get(bagua)
    if star:
        lines.append(f"太乙九星·{star}")
        if ts.get("直符九星") == star:
            lines.append(_clip(str(ts.get("直符所主", "")), 56))
    ws = ttext.get("文昌九星") or {}
    wdist = ws.get("文昌九星分布") or {}
    wstar = wdist.get(bagua)
    if wstar:
        lines.append(f"文昌九星·{wstar}")
        if ws.get("直事文昌星") == wstar:
            lines.append(_clip(str(ws.get("臨宮分野", "")), 48))
    return lines


def _te_gong_lines(branch: str, ttext: dict) -> list[str]:
    te = (ttext.get("卷八") or {}).get("絳宮明堂玉堂") or {}
    if not te:
        return []
    lines = []
    for name, zhi in _TE_GONG_BRANCH.items():
        if branch != zhi or name not in te:
            continue
        info = te[name]
        lines.append(f"{name}·{info.get('分野', '')}")
        if info.get("要訣"):
            lines.append(_clip(str(info["要訣"]), 56))
    return lines


def _feifu_lines(branch: str, ttext: dict) -> list[str]:
    ff = (ttext.get("卷十一") or {}).get("飛符四殺") or {}
    if not ff:
        return []
    lines = []
    for label in _FEIFU_LABELS:
        if ff.get(label) == branch:
            lines.append(f"飛符四殺·{label}")
    xing = ff.get("城名刑殺") or {}
    for label, zhi in (
        ("劫殺", xing.get("劫殺")),
        ("災殺", xing.get("災殺")),
        ("天殺", xing.get("天殺")),
        ("地殺", xing.get("地殺")),
    ):
        if zhi == branch:
            lines.append(f"城名刑殺·{label}")
    if ff.get("飛符") == branch and ff.get("飛符併災殺"):
        lines.append(_clip(str(ff.get("斷語", "")), 56))
    return lines[:3]


def _geju_for_branch(branch: str, ttext: dict) -> list[str]:
    geju = ttext.get("釋格局") or {}
    if not geju:
        return []
    stars = _branch_stars(ttext, branch)
    lines = []
    for key, val in geju.items():
        if key == "無格局":
            continue
        text = str(val)
        hit = branch in text or any(s and s in key for s in stars)
        if hit:
            lines.append(f"{key}：{_clip(text, 44)}")
    return lines[:3]


def _jueyi_for_branch(branch: str, ttext: dict) -> list[str]:
    block = (ttext.get("神將所主") or {}).get("陰陽絕易") or {}
    lines = []
    for item in block.get("臨宮") or []:
        palaces = item.get("宮位") or []
        if branch not in palaces and _branch_bagua(branch) not in palaces:
            continue
        kind = item.get("類型", "")
        gods = "、".join(str(x) for x in (item.get("臨神") or []))
        duan = item.get("斷語", "")
        lines.append(f"{kind}·{gods}：{_clip(str(duan), 48)}" if gods else _clip(str(duan), 56))
    return lines[:2]


def _tongbian_for_branch(branch: str, ttext: dict) -> list[str]:
    tongbian = (ttext.get("神將所主") or {}).get("八門所主", {}).get("通變") or []
    bagua = _branch_bagua(branch) or branch
    lines = []
    for item in tongbian:
        text = str(item)
        if branch in text or bagua in text:
            lines.append(_clip(text, 64))
    return lines[:2]


def _split_planets(cell: str, tokens: tuple[str, ...]) -> list[str]:
    if not cell or cell == " ":
        return []
    result: list[str] = []
    remaining = cell
    while remaining:
        matched = False
        for token in tokens:
            if remaining.startswith(token):
                result.append(token.replace("\u3000", "").strip() or token.strip())
                remaining = remaining[len(token):]
                matched = True
                break
        if not matched:
            break
    return result


def _planet_ring(year: int, month: int, day: int, hour: int, minute: int, *, life: bool = False) -> list[tuple[str, list[str]]]:
    from .kintaiyi import find_stars  # noqa: PLC0415 — 避免模組載入循環

    tokens = _PLANET_TOKENS_LIFE if life else _PLANET_TOKENS
    stars = find_stars(year, month, day, hour, minute)
    cells = {branch: " " for branch in _PLANET_RING_BRANCHES}
    for planet, zhi in stars.items():
        if zhi not in cells:
            continue
        label = planet.replace("\u3000", "") if life else planet
        if cells[zhi] == " ":
            cells[zhi] = label
        else:
            cells[zhi] += label
    return [
        (branch, _split_planets(cells[branch], tokens))
        for branch in _PLANET_RING_BRANCHES
    ]


def _planet_ring_lines(branch: str, planets: list[str]) -> list[str]:
    lines = [f"地支·{branch}"]
    if planets:
        lines.append("七曜：" + "、".join(planets))
    else:
        lines.append("七曜：本宮無行星")
    return lines


def _su_lines(star: str, ttext: dict) -> list[str]:
    lines = []
    desc = su_dist.get(star)
    if desc:
        lines.append(_clip(desc, 64))
    if star == ttext.get("太歲二十八宿"):
        yc = ttext.get("太歲值宿斷事")
        if yc:
            lines.append(f"太歲值宿·{_clip(str(yc), 56)}")
    if star == ttext.get("始擊二十八宿"):
        sc = ttext.get("始擊值宿斷事")
        if sc:
            lines.append(f"始擊值宿·{_clip(str(sc), 56)}")
    daily = ttext.get("二十八宿值日")
    if daily and star == daily:
        lines.append("值日宿")
    return lines


def _day_golden_lines(trigram: str, star: str, door: str, ttext: dict) -> list[str]:
    lines = [f"{trigram}宮"]
    if star and str(star).strip():
        lines.append(f"九星·{star}")
    if door and str(door).strip():
        door_key = str(door).replace("門", "")
        lines.append(str(door))
        lines.extend(_door_lines(door_key, ttext)[:2])
    return lines


def _hour_general_lines(branch: str, general: str, earth: str, ttext: dict) -> list[str]:
    lines = []
    if general and str(general).strip():
        lines.append(f"天將·{general}")
    if earth and str(earth).strip():
        lines.append(f"天盤·{earth}")
    god = config.sixteen_god_zhu(branch)
    if god.get("神"):
        lines.append(f"間神·{god['神']}")
        if god.get("所主"):
            lines.append(_clip(god["所主"], 64))
    sj = ttext.get("神將所主") or {}
    ng = sj.get("九宮所主") or {}
    if ng.get("摘要"):
        lines.append(_clip(str(ng["摘要"]), 56))
    return lines


def _palace_branch_lines(branch: str, ttext: dict) -> list[str]:
    lines = []
    tmpl = _PALACE_TEMPLATE.get(branch)
    if tmpl:
        lines.append(f"神將·{tmpl[0]}　分野·{tmpl[1]}")
    stars = _branch_stars(ttext, branch)
    if stars:
        lines.append("臨宮：" + "、".join(stars))
    vol8 = ttext.get("卷八") or {}
    fy = vol8.get("十二分野表") or []
    for row in fy:
        if row.get("地支") == branch:
            lines.append(f"{row.get('國', '')}分·{row.get('州', '')}")
            break
    vol11 = ttext.get("卷十一") or {}
    zy = vol11.get("州國災變月數") or {}
    for hit in (zy.get("災月") or []):
        if hit.get("月建") == branch:
            lines.append(_clip(hit.get("斷語", ""), 56))
            break
    god = config.sixteen_god_zhu(branch)
    if god.get("所主"):
        lines.append(f"間神·{god.get('神', '')}：{_clip(god['所主'], 48)}")
    bagua = _branch_bagua(branch)
    lines.extend(_noble_god_lines(ttext, branch=branch, bagua=bagua))
    lines.extend(_nine_star_lines(ttext, bagua))
    lines.extend(_sanqi_lines(ttext, branch=branch))
    lines.extend(_te_gong_lines(branch, ttext))
    lines.extend(_feifu_lines(branch, ttext))
    lines.extend(_geju_for_branch(branch, ttext))
    lines.extend(_jueyi_for_branch(branch, ttext))
    lines.extend(_tongbian_for_branch(branch, ttext))
    return lines[:_MAX_PALACE_LINES]


def _door_lines(door: str, ttext: dict) -> list[str]:
    lines = []
    doors = ttext.get("八門分佈") or {}
    wang = ttext.get("八宮旺衰") or {}
    for gong, name in doors.items():
        d = str(name).replace("門", "")
        if d == door or door in str(name):
            gname = config.num2gong(gong) if isinstance(gong, int) else str(gong)
            wx = wang.get(gname, "")
            ji = "吉" if d in _GOOD_DOORS else "凶"
            lines.append(f"臨{gname}宮·{name}（{ji}{'·' + wx if wx else ''}）")
    sj = ttext.get("神將所主") or {}
    bm = sj.get("八門所主") or {}
    for item in bm.get("八門分布") or []:
        if door in str(item.get("門", "")):
            if item.get("所主"):
                lines.append(_clip(item["所主"], 64))
            if item.get("旺衰"):
                lines.append(f"旺衰：{item['旺衰']}")
            break
    if bm.get("太乙所臨門") and door in str(bm.get("太乙所臨門", "")):
        if bm.get("太乙門所主"):
            lines.append(f"太乙門·{_clip(bm['太乙門所主'], 48)}")
    for label, text in (bm.get("門具") or {}).items():
        blob = f"{label}{text}"
        if door in blob or door.replace("門", "") in blob:
            lines.append(_clip(f"{label}·{text}", 64))
    for item in (bm.get("通變") or []):
        if door in str(item):
            lines.append(_clip(str(item), 64))
    jueyi = (ttext.get("神將所主") or {}).get("陰陽絕易") or {}
    if jueyi.get("斷語") and door in str(bm.get("太乙所臨門", "")):
        lines.append(_clip(str(jueyi["斷語"]), 56))
    return lines[:8]


def _center_lines(ttext: dict) -> list[str]:
    lines = []
    ty = ttext.get("太乙")
    if ty is not None:
        lines.append(f"太乙落{config.num2gong(ty)}宮")
    wc = ttext.get("文昌")
    if isinstance(wc, list) and wc:
        lines.append(f"天目文昌·{wc[0]}")
    if ttext.get("始擊"):
        lines.append(f"始擊·{ttext['始擊']}")
    hc = ttext.get("主算")
    ac = ttext.get("客算")
    sc = ttext.get("定算")
    if hc:
        lines.append(f"主算 {hc[0] if isinstance(hc, list) else hc}")
    if ac:
        lines.append(f"客算 {ac[0] if isinstance(ac, list) else ac}")
    if sc:
        lines.append(f"定算 {sc[0] if isinstance(sc, list) else sc}")
    lines.extend(_geju_lines(ttext.get("釋格局") or {}, limit=3))
    lines.extend(_sanqi_lines(ttext))
    lines.extend(_noble_god_lines(ttext))
    lines.extend(_wuyun_lines(ttext))
    lines.extend(_wuyin_lines(ttext))
    v10 = ttext.get("卷十") or {}
    for item in (v10.get("天目合會") or [])[:1]:
        lines.append(_clip(str(item), 56))
    if v10.get("要訣"):
        lines.append(_clip(str(v10["要訣"]), 56))
    v12 = ttext.get("卷十二") or {}
    rg = v12.get("統運入卦") or {}
    if rg.get("卦"):
        lines.append(f"統運·{rg.get('運', '')}{rg.get('卦', '')}{rg.get('爻名', '')}")
    return lines[:14]


def _life_center_lines(ttext: dict, life_pan: dict | None) -> list[str]:
    life_pan = life_pan or {}
    lines = []
    if life_pan.get("安命宮"):
        lines.append(f"命宮·{life_pan['安命宮']}")
    if life_pan.get("安身宮"):
        lines.append(f"身宮·{life_pan['安身宮']}")
    if life_pan.get("性別"):
        lines.append(str(life_pan["性別"]))
    ty = life_pan.get("太乙落宮") or ttext.get("太乙")
    if ty is not None:
        lines.append(f"太乙落{config.num2gong(ty)}宮")
    hc = life_pan.get("主算") or ttext.get("主算")
    if hc:
        lines.append(f"主算 {hc[0] if isinstance(hc, list) else hc}")
    jinfu = life_pan.get("十提金賦") or {}
    for entry in (jinfu.get("匹配賦") or [])[:2]:
        lines.append(f"金賦·{entry.get('賦名', '')}")
    return lines


def _life_palace_lines(palace: str, branch: str, life1: dict | None, ttext: dict) -> list[str]:
    lines = [f"地支·{branch}"]
    if palace and str(palace).strip():
        lines.append(f"十二宮·{palace}")
    for text in (life1 or {}).get(palace, [])[:3]:
        lines.append(_clip(str(text), 64))
    stars = _branch_stars(ttext, branch)
    if stars:
        lines.append("臨星：" + "、".join(stars))
    return lines[:_MAX_PALACE_LINES]


def _fill_planet_ring(sectors: dict[str, dict], layer: int, ring: list[tuple[str, list[str]]]) -> None:
    for i, (branch, planets) in enumerate(ring):
        title = "、".join(planets) if planets else branch
        sectors[f"layer{layer}:{i}"] = _sector_entry(title, _planet_ring_lines(branch, planets))


def _fill_star28_ring(sectors: dict[str, dict], layer: int, stars: list[str], ttext: dict) -> None:
    for i, star in enumerate(stars):
        sectors[f"layer{layer}:{i}"] = _sector_entry(star, _su_lines(star, ttext))


def _hour_general_ring(ty) -> list[tuple[str, str, str]]:
    earth_sky = ty.lr().sky_n_earth_list()
    general = ty.lr().result(0).get("地轉天將") or {}
    values = list(general.values())
    keys = list(general.keys())
    mapped = [_LR_GENERAL_MAP.get(v, v) for v in values]
    general_by_branch = dict(zip(keys, mapped))
    earth_by_branch = dict(zip(_LR_GENERAL_KEYS, earth_sky))
    return [
        (branch, general_by_branch.get(branch, ""), earth_by_branch.get(branch, ""))
        for branch in _SIXTEEN_BRANCHES
    ]


def build_chart_view_model(
    ttext: dict | None,
    *,
    chart_style: int = 0,
    is_life: bool = False,
    life_disc: dict | None = None,  # noqa: ARG001 — 保留舊介面
    life1: dict | None = None,
    life_pan: dict | None = None,
    sex: str | None = None,
    ty=None,
    tn: int = 0,
) -> dict:
    """由 pan() 文本建扇區 tooltip 索引（key = layerN:index）。"""
    ttext = ttext or {}
    sectors: dict[str, dict] = {}

    if is_life or chart_style in (5, 6):
        ty_obj = ty
        life_pan = life_pan or {}
        palace_map = life_pan.get("十二命宮排列") or {}
        if palace_map:
            palace_order = [palace_map.get(branch, "") for branch in _TWELVE_BRANCHES]
        elif ty_obj is not None and sex:
            palace_order = list(ty_obj._twelve_palace_map(sex).values())
        else:
            palace_order = []

        ty_gong = life_pan.get("太乙") or ttext.get("太乙")
        sectors["layer1:0"] = _sector_entry(
            f"命盤·{config.num2gong(ty_gong) if ty_gong is not None else '中宮'}",
            _life_center_lines(ttext, life_pan),
        )

        for i, branch in enumerate(_TWELVE_BRANCHES):
            palace = palace_order[i] if i < len(palace_order) else branch
            sectors[f"layer2:{i}"] = _sector_entry(
                str(palace),
                _life_palace_lines(str(palace), branch, life1, ttext),
            )
            sectors[f"layer3:{i}"] = _sector_entry(branch, _palace_branch_lines(branch, ttext) or [branch])
            sectors[f"layer4:{i}"] = _sector_entry(
                branch,
                _palace_branch_lines(branch, ttext) or [branch],
            )

        if ty_obj is not None:
            ring = _planet_ring(
                ty_obj.year, ty_obj.month, ty_obj.day, ty_obj.hour, ty_obj.minute, life=True,
            )
            _fill_planet_ring(sectors, 5, ring)

        return {"sectors": sectors, "is_life": True, "chart_style": chart_style}

    ty_obj = ty
    style = chart_style
    acc_style = style if style in (3, 4) else style
    if style in (5, 6):
        acc_style = 3

    ty_val = ttext.get("太乙")
    sectors["layer1:0"] = _sector_entry(
        f"太乙·{config.num2gong(ty_val)}" if ty_val else "中宮",
        _center_lines(ttext),
    )

    door_items = (ttext.get("神將所主") or {}).get("八門所主", {}).get("八門分布") or []
    for i, door in enumerate(_EIGHT_DOOR_ORDER):
        title = f"{door}門"
        lines = _door_lines(door, ttext)
        if i < len(door_items) and not lines:
            item = door_items[i]
            title = str(item.get("門", title))
            if item.get("所主"):
                lines.append(_clip(item["所主"], 64))
        sectors[f"layer2:{i}"] = _sector_entry(title, lines)

    palace_branches = _SIXTEEN_BRANCHES
    for i, br in enumerate(palace_branches):
        tmpl = _PALACE_TEMPLATE.get(br, ("", ""))
        sectors[f"layer3:{i}"] = _sector_entry(
            br,
            [f"神將·{tmpl[0]}", f"分野·{tmpl[1]}"] if tmpl[0] else [br],
        )

    for i, br in enumerate(palace_branches):
        sectors[f"layer4:{i}"] = _sector_entry(br, _palace_branch_lines(br, ttext))

    if ty_obj is not None:
        ring = _planet_ring(
            ty_obj.year, ty_obj.month, ty_obj.day, ty_obj.hour, ty_obj.minute,
        )

        if style in (0, 1):
            _fill_planet_ring(sectors, 5, ring)
        elif style == 2:
            _, golden_rows = config.gpan1(
                ty_obj.year, ty_obj.month, ty_obj.day, ty_obj.hour, ty_obj.minute,
            )
            for i, row in enumerate(golden_rows[:8]):
                trigram, star, door = row[0], row[1], row[2]
                sectors[f"layer3:{i}"] = _sector_entry(
                    f"{trigram}·{star}",
                    _day_golden_lines(trigram, star, door, ttext),
                )
            _fill_planet_ring(sectors, 6, ring)
        elif style in (3, 4):
            for i, (branch, general, earth) in enumerate(_hour_general_ring(ty_obj)):
                sectors[f"layer3:{i}"] = _sector_entry(
                    general or branch,
                    _hour_general_lines(branch, general, earth, ttext),
                )
            stars28 = ty_obj.twenty_eightstar(acc_style, tn)
            _fill_star28_ring(sectors, 6, stars28, ttext)
            _fill_planet_ring(sectors, 7, ring)

    return {"sectors": sectors, "is_life": False, "chart_style": chart_style}


def _gong_to_chart_branches(gong_num: int) -> list[str]:
    return [b for b in _SIXTEEN_BRANCHES if config.gong2.get(b) == gong_num]


def _resolve_ty_gong(ttext: dict) -> int | None:
    ty = ttext.get("太乙落宮")
    if isinstance(ty, int) and 1 <= ty <= 9:
        return ty
    name = str(ttext.get("太乙") or "")
    for i in range(1, 10):
        if config.num2gong(i) in name:
            return i
    return None


def _chart_entity_positions(ttext: dict) -> dict[str, list[str]]:
    pos: dict[str, list[str]] = {}
    ty_g = _resolve_ty_gong(ttext)
    if ty_g is not None:
        pos["太乙"] = _gong_to_chart_branches(ty_g)

    for field, label in (("始擊", "始擊"), ("定目", "定目")):
        ch = ttext.get(field)
        if isinstance(ch, str) and ch in _SIXTEEN_BRANCHES:
            pos[label] = [ch]

    wc = ttext.get("文昌")
    if isinstance(wc, list) and wc:
        ch = str(wc[0])
        if ch in _SIXTEEN_BRANCHES:
            pos["文昌"] = [ch]

    for field, label in (
        ("主將", "主大"),
        ("主參", "主參"),
        ("客將", "客大"),
        ("客參", "客參"),
    ):
        g = ttext.get(field)
        if isinstance(g, int):
            pos[label] = _gong_to_chart_branches(g)

    doors = ttext.get("八門分佈") or {}
    for gong, door in doors.items():
        gnum = gong if isinstance(gong, int) else None
        if gnum is None and isinstance(gong, str) and gong.isdigit():
            gnum = int(gong)
        if gnum is None:
            continue
        dn = str(door).replace("門", "")
        if dn == "開":
            pos.setdefault("開門", []).extend(_gong_to_chart_branches(gnum))
        if dn == "生":
            pos.setdefault("生門", []).extend(_gong_to_chart_branches(gnum))
    return pos


def _geju_short(key: str) -> str:
    for ch in "掩迫關囚擊格對提執四":
        if ch in key:
            return ch
    return key[:2] if key else ""


def _geju_tone(key: str) -> str:
    if any(x in key for x in ("擊", "迫", "掩", "格")):
        return "danger"
    if any(x in key for x in ("關", "囚")):
        return "warn"
    if any(x in key for x in ("對", "提", "執")):
        return "caution"
    return "info"


def _branches_for_geju_entry(key: str, val: str, pos: dict[str, list[str]], ttext: dict) -> list[str]:
    branches: set[str] = set()
    blob = f"{key}{val}"
    entity_aliases = (
        ("太乙", ("太乙",)),
        ("文昌", ("文昌", "天目")),
        ("始擊", ("始擊",)),
        ("定目", ("定目", "定計")),
        ("主大", ("主大", "主將")),
        ("主參", ("主參",)),
        ("客大", ("客大", "客將")),
        ("客參", ("客參",)),
        ("開門", ("開",)),
        ("生門", ("生",)),
    )
    for label, aliases in entity_aliases:
        if any(alias in key or alias in blob for alias in aliases):
            for br in pos.get(label, []):
                branches.add(br)
    for br in _SIXTEEN_BRANCHES:
        if br in blob:
            branches.add(br)
    if not branches:
        mini = {"釋格局": {key: val}, **ttext}
        for br in _SIXTEEN_BRANCHES:
            if _geju_for_branch(br, mini):
                branches.add(br)
    return [br for br in _SIXTEEN_BRANCHES if br in branches]


def _geju_palette(short: str, tone: str) -> tuple[str, str, str]:
    if short in _GEJU_SHORT_COLORS:
        return _GEJU_SHORT_COLORS[short]
    return _GEJU_TONE_COLORS.get(tone, _GEJU_TONE_COLORS["info"])


def _outer_ring_layout(chart_style: int, *, is_life: bool) -> dict:
    if is_life or chart_style in (5, 6):
        return {
            "layer_idx": 4,
            "inner_radius": 12.0,
            "layer_gap": 35.0,
            "sector_count": 12,
            "branch_order": _TWELVE_BRANCHES,
        }
    if chart_style in (0, 1):
        return {
            "layer_idx": 4,
            "inner_radius": 13.0,
            "layer_gap": 45.0,
            "sector_count": 12,
            "branch_order": _PLANET_RING_BRANCHES,
        }
    if chart_style == 2:
        return {
            "layer_idx": 5,
            "inner_radius": 3.0,
            "layer_gap": 31.5,
            "sector_count": 12,
            "branch_order": _PLANET_RING_BRANCHES,
        }
    return {
        "layer_idx": 6,
        "inner_radius": 3.0,
        "layer_gap": 31.5,
        "sector_count": 12,
        "branch_order": _PLANET_RING_BRANCHES,
    }


def _sector_angles_for_branch(branch: str, layout: dict) -> tuple[float, float]:
    order = layout["branch_order"]
    count = layout["sector_count"]
    if branch in order:
        idx = order.index(branch)
        start = (360.0 / count) * idx + _ROTATION_ANGLE
        end = (360.0 / count) * (idx + 1) + _ROTATION_ANGLE
        return start, end
    if branch in _SIXTEEN_BRANCHES:
        idx = _SIXTEEN_BRANCHES.index(branch)
        start = (360.0 / 16) * idx + _ROTATION_ANGLE
        end = (360.0 / 16) * (idx + 1) + _ROTATION_ANGLE
        return start, end
    return _ROTATION_ANGLE, _ROTATION_ANGLE


def _outer_label_radius(layout: dict, *, view_half: float = 250.0) -> float:
    """與 chart._add_ornament 外緣金環帶一致，標記置於最外可視環帶中央。"""
    outer_data = layout["inner_radius"] + (layout["layer_idx"] + 1) * layout["layer_gap"]
    band = max(view_half - outer_data, 1.0)
    r1 = outer_data + max(2.0, band * 0.30)
    r2 = outer_data + max(5.0, band * 0.62)
    return (r1 + r2) / 2.0


def build_geju_overlay_svg(
    ttext: dict | None,
    *,
    chart_style: int = 0,
    is_life: bool = False,
    view_half: float = 250.0,
) -> str:
    """於排盤最外環（金環裝飾帶）顯示釋格局文字標記。"""
    markers = build_geju_sector_markers(ttext)
    if not markers:
        return ""

    layout = _outer_ring_layout(chart_style, is_life=is_life)
    label_r = _outer_label_radius(layout, view_half=view_half)
    parts = ['<g class="taiyi-geju-overlay" data-source="server">']

    for branch, items in markers.items():
        if not items:
            continue
        start, end = _sector_angles_for_branch(branch, layout)
        mid_rad = math.radians((start + end) / 2.0)
        shorts: list[str] = []
        tone = "info"
        for item in items:
            short = str(item.get("short", "")).strip()
            if not short or short in shorts:
                continue
            shorts.append(short)
            if item.get("tone") == "danger":
                tone = "danger"
            elif item.get("tone") == "warn" and tone != "danger":
                tone = "warn"
        if not shorts:
            continue

        label = "·".join(shorts[:3])
        _fill, _stroke, text_color = _geju_palette(shorts[0], tone)
        cx = label_r * math.cos(mid_rad)
        cy = label_r * math.sin(mid_rad)
        parts.append(
            f'<text class="taiyi-geju-label" data-branch="{branch}" '
            f'x="{cx:.2f}" y="{cy:.2f}" text-anchor="middle" dominant-baseline="middle" '
            f'fill="{text_color}" font-size="{_GEJU_LABEL_FONT_SIZE}" font-weight="700" '
            f'font-family="Noto Serif SC, KaiTi, serif" '
            f'style="fill:{text_color} !important;'
            f'font-weight:700;paint-order:stroke;stroke:#141826;'
            f'stroke-width:{_GEJU_LABEL_STROKE_WIDTH}px;stroke-linejoin:round">'
            f"{label}</text>"
        )

    parts.append("</g>")
    return "".join(parts)


def build_geju_sector_markers(ttext: dict | None) -> dict[str, list[dict]]:
    """依釋格局將扇區地支對應的標記（供 SVG 外環標示）。"""
    ttext = ttext or {}
    geju = ttext.get("釋格局") or {}
    if not geju or (len(geju) == 1 and "無格局" in geju):
        return {}

    pos = _chart_entity_positions(ttext)
    markers: dict[str, list[dict]] = {}
    for key, val in geju.items():
        if key == "無格局":
            continue
        entry = {
            "key": key,
            "short": _geju_short(key),
            "tone": _geju_tone(key),
            "text": _clip(str(val), 56),
        }
        for branch in _branches_for_geju_entry(key, str(val), pos, ttext):
            bucket = markers.setdefault(branch, [])
            if not any(item["key"] == key for item in bucket):
                bucket.append(entry)
    return markers


def sector_panel_layer_labels(*, is_life: bool = False, chart_style: int = 0) -> dict[str, str]:
    """扇區點擊面板用之圖層中文標籤。"""
    if is_life or chart_style in (5, 6):
        return {
            "layer1": "命盤中宮",
            "layer2": "十二命宮",
            "layer3": "地支環",
            "layer4": "十六神環",
            "layer5": "行星環",
        }
    if chart_style == 2:
        return {
            "layer1": "中宮",
            "layer2": "八門",
            "layer3": "金函玉鏡",
            "layer4": "十六宮",
            "layer5": "六壬神將",
            "layer6": "行星環",
        }
    if chart_style in (3, 4):
        return {
            "layer1": "中宮",
            "layer2": "八門",
            "layer3": "地轉天將",
            "layer4": "十六宮",
            "layer6": "二十八宿",
            "layer7": "行星環",
        }
    return {
        "layer1": "中宮",
        "layer2": "八門",
        "layer3": "十六神將",
        "layer4": "十六宮",
        "layer5": "行星環",
    }


def chart_svg_layout(chart_style: int = 0, *, is_life: bool = False) -> dict:
    """各盤式 SVG 互動層配置（聯動著色、轉盤）。"""
    if is_life or chart_style in (5, 6):
        return {
            "chart_style": 5,
            "sync_layers": ["layer2", "layer3", "layer4"],
            "rotate_layers": [],
        }
    if chart_style in (0, 1):
        return {
            "chart_style": chart_style,
            "sync_layers": ["layer3", "layer4", "layer5"],
            "rotate_layers": ["layer4"],
        }
    if chart_style == 2:
        return {
            "chart_style": 2,
            "sync_layers": ["layer4", "layer5", "layer6"],
            "rotate_layers": ["layer5"],
        }
    if chart_style in (3, 4):
        return {
            "chart_style": chart_style,
            "sync_layers": ["layer3", "layer4", "layer5"],
            "rotate_layers": ["layer4", "layer6"],
        }
    return {
        "chart_style": chart_style,
        "sync_layers": ["layer3", "layer4", "layer5"],
        "rotate_layers": ["layer4"],
    }


def format_tooltip(entry: dict | None, fallback: str = "") -> str:
    """將 sector entry 格式化為 tooltip 多行文字。"""
    if not entry:
        return fallback
    parts = [entry.get("title", "")]
    parts.extend(entry.get("lines") or [])
    text = "\n".join(p for p in parts if p)
    return text or fallback