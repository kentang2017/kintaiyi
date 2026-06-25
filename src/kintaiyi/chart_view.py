# 排盤 SVG 語意層：由 pan() 斷事生成扇區 tooltip（P0）

from __future__ import annotations

import math
import re

from . import config
from .chart import ornament_outer_radius
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
_EIGHT_ORDER = [1, 2, 3, 4, 6, 7, 8, 9]
_GEJU_OPP = {1: 9, 9: 1, 2: 8, 8: 2, 3: 7, 7: 3, 4: 6, 6: 4}
_TE_GONG_BRANCH = {"絳宮": "巳", "明堂": "丑", "玉堂": "卯"}
_SANQI_KEYS = ("太歲青龍旗", "太陰黑旗", "害氣赤旗")
_FEIFU_LABELS = ("飛符", "災殺", "鬼殺", "月殺", "天賊殺", "天史殺")
_MAX_PALACE_LINES = 10
_ROTATION_ANGLE = 248.0
_GEJU_LABEL_FONT_SIZE = 9
_GEJU_LABEL_STROKE_WIDTH = 1.8
_GEJU_SHORT_COLORS: dict[str, tuple[str, str, str]] = {
    "掩": ("#7A1530", "#E8A4B4", "#FF8FAB"),
    "迫": ("#B91C3C", "#F8C0CC", "#FF4466"),
    "關": ("#A16207", "#F5D565", "#FFD54F"),
    "囚": ("#92400E", "#F0C27A", "#FF9E40"),
    "擊": ("#881337", "#FDA4AF", "#FF6B9D"),
    "格": ("#581C87", "#D8B4FE", "#C084FC"),
    "對": ("#1E4D7B", "#93C5FD", "#60A5FA"),
    "提": ("#166534", "#86EFAC", "#4ADE80"),
    "執": ("#3F3F8A", "#C7C9F5", "#A78BFA"),
    "四": ("#3F4E5C", "#A8BCC8", "#94A3B8"),
}
_GEJU_LABEL_SEP_COLOR = "#8A9BB0"
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
    from .guiyun_display import guiyun_summary_lines  # noqa: PLC0415
    from .tongyun_display import tongyun_summary_lines  # noqa: PLC0415

    lines.extend(tongyun_summary_lines(ttext, limit=2))
    lines.extend(guiyun_summary_lines(ttext.get("卷九"), limit=2))
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
    vol20 = life_pan.get("卷二十") or {}
    fly = vol20.get("飛祿飛馬") or {}
    cur = fly.get("當前") or {}
    if cur.get("飛祿宮") or cur.get("飛馬宮"):
        period = f"（{cur['期間']}）" if cur.get("期間") else ""
        lines.append(
            f"祿{cur.get('飛祿宮', '—')}馬{cur.get('飛馬宮', '—')}{period}"
        )
    return lines


def _vol20_palace_lines(palace: str, branch: str, life_pan: dict | None) -> list[str]:
    life_pan = life_pan or {}
    vol20 = life_pan.get("卷二十") or life_pan
    lines: list[str] = []
    fly = vol20.get("飛祿飛馬") or {}
    cur = fly.get("當前") or {}
    if cur.get("飛祿宮") == branch:
        lines.append(f"飛祿·{branch}")
    if cur.get("飛馬宮") == branch:
        lines.append(f"飛馬·{branch}")
    san = vol20.get("命宮三合") or {}
    if branch and branch in (san.get("三合") or ""):
        lines.append(f"三合·{san.get('三合', '')}")
    she = vol20.get("十干合") or {}
    if palace == "命宮" and she.get("合干"):
        lines.append(f"十干合·{she.get('年干', '')}{she.get('合干', '')}合")
    wang = vol20.get("十二宮旺衰絕空刑") or {}
    pinfo = wang.get(palace) or {}
    if pinfo.get("狀態"):
        lines.append(f"宮位·{pinfo['狀態']}")
    return lines


def _life_palace_lines(
    palace: str,
    branch: str,
    life1: dict | None,
    ttext: dict,
    life_pan: dict | None = None,
) -> list[str]:
    lines = [f"地支·{branch}"]
    if palace and str(palace).strip():
        lines.append(f"十二宮·{palace}")
    lines.extend(_vol20_palace_lines(palace, branch, life_pan))
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
        center_lines = _life_center_lines(ttext, life_pan)
        if ty_obj is not None and sex:
            from .mingfa import life_chart_annotations  # noqa: PLC0415

            plate_ji = {5: 4, 6: 3}.get(chart_style, 3)
            ann = life_chart_annotations(ty_obj, sex, plate_ji=plate_ji)
            for line in ann.get("center_lines") or []:
                if line not in center_lines:
                    center_lines.insert(0, line)
        sectors["layer1:0"] = _sector_entry(
            f"命盤·{config.num2gong(ty_gong) if ty_gong is not None else '中宮'}",
            center_lines,
        )

        for i, branch in enumerate(_TWELVE_BRANCHES):
            palace = palace_order[i] if i < len(palace_order) else branch
            sectors[f"layer2:{i}"] = _sector_entry(
                str(palace),
                _life_palace_lines(str(palace), branch, life1, ttext, life_pan),
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

    doors = ttext.get("八門分佈") or {}
    ng = ttext.get("九宮貴神") or (ttext.get("卷十") or {}).get("九宮貴神") or {}
    god_dist = ng.get("九宮貴神分布") or {}
    door_items = (ttext.get("神將所主") or {}).get("八門所主", {}).get("八門分布") or []
    for i, gong in enumerate(_layer2_gong_order(ttext)):
        door = str(doors.get(gong, "")).replace("門", "")
        luoshu = config._LUOSHU_GONG.get(gong, "")
        god_full = god_dist.get(luoshu, "")
        gname = config.num2gong(gong)
        title = f"{gname}·{door}" if door else gname
        lines = _door_lines(door, ttext) if door else []
        if god_full:
            lines.insert(0, f"貴神·{god_full}")
            if ng.get("直事貴神") == god_full:
                lines.insert(1, "直事貴神臨此")
        if i < len(door_items) and not lines:
            item = door_items[i]
            item_door = str(item.get("門", door)).replace("門", "")
            title = f"{gname}·{item_door}" if item_door else title
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


def _geju_mishu_search_terms(key: str) -> list[str]:
    """《太乙秘書》局註中與釋格局 key 對應的檢索詞。"""
    terms: list[str] = []
    if "辰迫" in key:
        terms.append("辰迫")
    if "宮迫" in key:
        if "外" in key:
            terms.append("外迫")
        elif "內" in key:
            terms.append("內迫")
        else:
            terms.extend(["外迫", "內迫"])
    if key.startswith("擊"):
        if "辰" in key:
            terms.append("辰擊")
        if "宮" in key:
            terms.append("宮擊")
        terms.append("擊")
    if "提挾" in key:
        terms.extend(["提挾", "主挾", "客挾", "挾"])
    if "提格" in key:
        terms.append("提格")
    if "四郭" in key:
        terms.extend(["四郭", "四郭固"])
    if "關囚" in key:
        terms.extend(["關囚", "囚"])
    elif key.startswith("囚"):
        terms.append("囚")
    elif key.startswith("關"):
        terms.append("關")
    if key.startswith("格"):
        terms.append("格")
    if key == "掩" or "(掩" in key or "掩)" in key:
        terms.append("掩")
    if key == "對":
        terms.append("對")
    if "執" in key:
        terms.append("執")
    deduped: list[str] = []
    for t in terms:
        if t and t not in deduped:
            deduped.append(t)
    return deduped


def geju_mentioned_in_mishu(key: str, mishu_text: str | None) -> bool:
    """格局是否於《太乙秘書》局註文字中被提及。"""
    text = (mishu_text or "").strip()
    if not text:
        return False
    return any(term in text for term in _geju_mishu_search_terms(key))


def _entity_gong(label: str, ttext: dict) -> int | None:
    """格局實體名 → 八宮號（略過中宮 5）。"""
    int_fields = {
        "太乙": _resolve_ty_gong(ttext),
        "主大": ttext.get("主將"),
        "主參": ttext.get("主參"),
        "客大": ttext.get("客將"),
        "客參": ttext.get("客參"),
    }
    if label in int_fields:
        g = int_fields[label]
        return g if isinstance(g, int) and 1 <= g <= 9 and g != 5 else None

    branch = None
    if label in ("文昌", "天目"):
        wc = ttext.get("文昌")
        if isinstance(wc, list) and wc:
            branch = str(wc[0])
    elif label == "始擊":
        branch = ttext.get("始擊")
    elif label in ("定目", "定計"):
        branch = ttext.get("定目")
    if isinstance(branch, str) and branch in _SIXTEEN_BRANCHES:
        g = config.gong2.get(branch)
        return g if isinstance(g, int) and g != 5 else None

    if label in ("開", "開門", "生", "生門"):
        dn = "開" if "開" in label else "生"
        for gong, door in (ttext.get("八門分佈") or {}).items():
            gnum = gong if isinstance(gong, int) else int(gong) if str(gong).isdigit() else None
            if gnum and str(door).replace("門", "") == dn:
                return gnum if gnum != 5 else None
    return None


def _ty_neighbor_gongs(ttext: dict) -> tuple[int | None, int | None]:
    ty = _resolve_ty_gong(ttext)
    if ty is None or ty not in _EIGHT_ORDER:
        return None, None
    idx = _EIGHT_ORDER.index(ty)
    return _EIGHT_ORDER[(idx - 1) % 8], _EIGHT_ORDER[(idx + 1) % 8]


def _gongs_for_geju_entry(key: str, val: str, ttext: dict) -> list[int]:
    """釋格局條目 → 應標示之八宮號（與 shi_geju 宮位語意一致）。"""
    if key == "無格局":
        return []
    ty = _resolve_ty_gong(ttext)
    if ty is None:
        return []

    gongs: set[int] = set()
    prev_g, next_g = _ty_neighbor_gongs(ttext)
    opp = _GEJU_OPP.get(ty)
    blob = f"{key}{val}"

    if key == "掩":
        gongs.add(ty)
    elif "關囚" in key:
        gongs.add(ty)
    elif key.startswith("囚("):
        gongs.add(ty)
    elif key.startswith("關("):
        for ent in ("主大", "主參", "客大", "客參"):
            if ent in key:
                g = _entity_gong(ent, ttext)
                if g:
                    gongs.add(g)
    elif key.startswith("格("):
        if opp:
            gongs.add(opp)
    elif key == "對":
        wc_g = _entity_gong("文昌", ttext)
        if wc_g:
            gongs.add(wc_g)
    elif "宮迫" in key:
        if "外" in key and next_g:
            gongs.add(next_g)
        elif "內" in key and prev_g:
            gongs.add(prev_g)
        else:
            for ent in ("文昌", "始擊", "定目", "主大", "主參", "客大", "客參"):
                if ent in key:
                    g = _entity_gong(ent, ttext)
                    if g:
                        gongs.add(g)
    elif key.startswith("擊("):
        if "外宮" in key and next_g:
            gongs.add(next_g)
        elif "內宮" in key and prev_g:
            gongs.add(prev_g)
        else:
            g = _entity_gong("始擊", ttext)
            if g:
                gongs.add(g)
    elif "辰迫" in key:
        for ent in ("文昌", "始擊", "定目"):
            if ent in key:
                g = _entity_gong(ent, ttext)
                if g:
                    gongs.add(g)
    elif key == "提挾":
        gongs.add(ty)
    elif "執" in key:
        gongs.add(ty)
    elif "提格" in key and opp:
        gongs.add(opp)
    elif key == "四郭固":
        gongs.add(ty)
    else:
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
                g = _entity_gong(label, ttext)
                if g:
                    gongs.add(g)
        for i in _EIGHT_ORDER:
            if config.num2gong(i) in blob:
                gongs.add(i)

    return [g for g in _EIGHT_ORDER if g in gongs]


def _layer2_gong_order(ttext: dict) -> list[int]:
    """與盤面 layer2 八門扇區順序一致（起二宮旋轉）。"""
    doors = ttext.get("八門分佈") or {}
    keys = [k for k in doors if isinstance(k, int) and k != 5]
    if not keys:
        return list(_EIGHT_ORDER)
    return config.new_list(keys, 2)


def _eight_gong_ring_layout(chart_style: int, *, is_life: bool) -> dict | None:
    if is_life or chart_style in (5, 6):
        return None
    if chart_style in (0, 1):
        return {
            "layer_idx": 1,
            "inner_radius": 13.0,
            "layer_gap": 45.0,
            "sector_count": 8,
        }
    return {
        "layer_idx": 1,
        "inner_radius": 3.0,
        "layer_gap": 31.5,
        "sector_count": 8,
    }


def _sector_angles_for_gong(gong: int, ttext: dict, layout: dict) -> tuple[float, float]:
    order = _layer2_gong_order(ttext)
    if gong in order:
        idx = order.index(gong)
    elif gong in _EIGHT_ORDER:
        idx = _EIGHT_ORDER.index(gong)
    else:
        return _ROTATION_ANGLE, _ROTATION_ANGLE
    count = layout["sector_count"]
    start = (360.0 / count) * idx + _ROTATION_ANGLE
    end = (360.0 / count) * (idx + 1) + _ROTATION_ANGLE
    return start, end


def _eight_gong_label_radius(layout: dict) -> float:
    inner = layout["inner_radius"] + layout["layer_idx"] * layout["layer_gap"]
    outer = layout["inner_radius"] + (layout["layer_idx"] + 1) * layout["layer_gap"]
    return (inner + outer) / 2.0


def _geju_palette(short: str, tone: str) -> tuple[str, str, str]:
    if short in _GEJU_SHORT_COLORS:
        return _GEJU_SHORT_COLORS[short]
    return _GEJU_TONE_COLORS.get(tone, _GEJU_TONE_COLORS["info"])


def _geju_text_color(short: str, tone: str) -> str:
    return _geju_palette(short, tone)[2]


def _geju_label_tspans(entries: list[dict]) -> str:
    """多格局並列時，各字（掩／迫／關…）分色 tspan。"""
    parts: list[str] = []
    for i, ent in enumerate(entries[:3]):
        short = ent["short"]
        color = _geju_text_color(short, ent.get("tone", "info"))
        if i > 0:
            sep = _GEJU_LABEL_SEP_COLOR
            parts.append(
                f'<tspan fill="{sep}" style="fill:{sep} !important">·</tspan>'
            )
        parts.append(
            f'<tspan class="taiyi-geju-c-{short}" fill="{color}" '
            f'style="fill:{color} !important">{short}</tspan>'
        )
    return "".join(parts)


def geju_label_css() -> str:
    """釋格局外環標記分色 CSS（覆蓋主題統一文字色）。"""
    rules = [
        "    .taiyi-svg-root .taiyi-geju-label tspan { font-weight: 700 !important; }",
    ]
    for short, (_bg, _stroke, text) in _GEJU_SHORT_COLORS.items():
        rules.append(
            f"    .taiyi-svg-root .taiyi-geju-c-{short} "
            f"{{ fill: {text} !important; }}"
        )
    return "\n".join(rules)


_WENCHANG_SPOT_COLOR = "#4D8CFF"
_WENCHANG_SPOT_CLASS = "taiyi-wenchang-spot"


def wenchang_spot_chart_css(scope: str = ".taiyi-svg-root") -> str:
    """排盤內「文昌」：加粗、湖色藍（覆蓋主題統一文字色）。"""
    return (
        f"    {scope} .{_WENCHANG_SPOT_CLASS} {{\n"
        f"        fill: {_WENCHANG_SPOT_COLOR} !important;\n"
        "        font-weight: 700 !important;\n"
        "    }"
    )


def _append_svg_class(open_tag: str, class_name: str) -> str:
    if re.search(rf'\bclass="[^"]*\b{re.escape(class_name)}\b', open_tag):
        return open_tag
    if 'class="' in open_tag:
        return re.sub(
            r'class="([^"]*)"',
            lambda m: f'class="{m.group(1)} {class_name}"',
            open_tag,
            count=1,
        )
    return open_tag[:-1] + f' class="{class_name}">'


def mark_wenchang_spots_in_svg(svg_markup: str) -> str:
    """為排盤扇區內「文昌」字樣加上湖色藍加粗樣式類別。"""
    if "文昌" not in svg_markup:
        return svg_markup

    skip_tokens = ("taiyi-guxu", "taiyi-geju")

    def style_tspan(match: re.Match[str]) -> str:
        open_tag, content, close = match.group(1), match.group(2), match.group(3)
        if content.strip() != "文昌":
            return match.group(0)
        if any(token in open_tag for token in skip_tokens):
            return match.group(0)
        return f"{_append_svg_class(open_tag, _WENCHANG_SPOT_CLASS)}{content}{close}"

    styled = re.sub(
        r"(<tspan\b[^>]*>)([^<]*)(</tspan>)",
        style_tspan,
        svg_markup,
        flags=re.IGNORECASE,
    )

    def style_text(match: re.Match[str]) -> str:
        open_tag, inner, close = match.group(1), match.group(2), match.group(3)
        if any(token in open_tag for token in skip_tokens):
            return match.group(0)
        if re.search(r"<tspan\b", inner, flags=re.IGNORECASE):
            return match.group(0)
        if "文昌" not in inner:
            return match.group(0)
        return f"{_append_svg_class(open_tag, _WENCHANG_SPOT_CLASS)}{inner}{close}"

    return re.sub(
        r"(<text\b[^>]*>)(.*?)(</text>)",
        style_text,
        styled,
        flags=re.DOTALL | re.IGNORECASE,
    )


def wuxing_theme_chart_css(scope: str = ".taiyi-svg-root") -> str:
    """五行彩色排盤：依地支五行著色，調淡以契合深墨金主題。"""
    fills = {
        "blue": "rgba(53, 92, 140, 0.58)",
        "brown": "rgba(112, 84, 58, 0.62)",
        "green": "rgba(90, 140, 115, 0.55)",
        "red": "rgba(148, 38, 58, 0.58)",
        "gold": "rgba(186, 148, 52, 0.52)",
        "orange": "rgba(128, 88, 46, 0.55)",
        "silver": "rgba(118, 132, 152, 0.52)",
        "black": "rgba(16, 36, 54, 0.78)",
        "gray": "rgba(28, 52, 72, 0.72)",
        "white": "rgba(22, 48, 68, 0.65)",
    }
    rules = [
        f"    {scope} path,",
        f"    {scope} polygon,",
        f"    {scope} rect {{",
        "        stroke: rgba(215, 189, 111, 0.72) !important;",
        "        stroke-width: 1.15 !important;",
        "    }",
        f"    {scope} #layer1 path,",
        f"    {scope} #layer1 circle,",
        f"    {scope} #layer1 ellipse {{",
        "        fill: rgba(186, 148, 52, 0.82) !important;",
        "        stroke: rgba(245, 240, 225, 0.72) !important;",
        "    }",
        f"    {scope} text,",
        f"    {scope} tspan {{",
        "        fill: #ffffff !important;",
        "    }",
    ]
    for name, color in fills.items():
        rules.append(
            f"    {scope} path[fill='{name}'],"
            f"    {scope} polygon[fill='{name}'],"
            f"    {scope} rect[fill='{name}'] {{ fill: {color} !important; }}"
        )
    rules.append(wenchang_spot_chart_css(scope))
    return "\n".join(rules)


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


def _guxu_angle_reference_layout() -> dict:
    """孤虛框線角度基準：十六宮序（年／月／日計第 3／4／5 層同角對齊）。"""
    return {"branch_order": _SIXTEEN_BRANCHES, "sector_count": 16}


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


def _guxu_sector_angles_for_branch(branch: str) -> tuple[float, float]:
    """孤虛內／外框於第 3／4／5 層共用同一地支角度。"""
    return _sector_angles_for_branch(branch, _guxu_angle_reference_layout())


def _outer_label_radius(layout: dict, *, view_half: float = 250.0) -> float:
    """與 chart._add_ornament 外緣金環一致，標記置於最外可視環帶。"""
    outer_data = layout["inner_radius"] + (layout["layer_idx"] + 1) * layout["layer_gap"]
    return ornament_outer_radius(outer_data, view_half)


def build_geju_overlay_svg(
    ttext: dict | None,
    *,
    chart_style: int = 0,
    is_life: bool = False,
    view_half: float = 250.0,
    mishu_text: str | None = None,
) -> str:
    """於最外環金環帶顯示釋格局文字（角度對齊八宮扇區）。"""
    markers = build_geju_sector_markers(ttext, mishu_text=mishu_text)
    if not markers:
        return ""

    angle_layout = _eight_gong_ring_layout(chart_style, is_life=is_life)
    if not angle_layout:
        return ""

    ttext = ttext or {}
    ring_layout = _outer_ring_layout(chart_style, is_life=is_life)
    label_r = _outer_label_radius(ring_layout, view_half=view_half)
    parts = ['<g class="taiyi-geju-overlay" data-source="server">']

    for gong_key, items in markers.items():
        if not items:
            continue
        try:
            gong = int(gong_key)
        except (TypeError, ValueError):
            continue
        start, end = _sector_angles_for_gong(gong, ttext, angle_layout)
        mid_rad = math.radians((start + end) / 2.0)
        entries: list[dict] = []
        seen: set[str] = set()
        for item in items:
            short = str(item.get("short", "")).strip()
            if not short or short in seen:
                continue
            seen.add(short)
            entries.append({
                "short": short,
                "tone": item.get("tone", "info"),
            })
        if not entries:
            continue

        cx = label_r * math.cos(mid_rad)
        cy = label_r * math.sin(mid_rad)
        gong_name = config.num2gong(gong) or str(gong)
        tspans = _geju_label_tspans(entries)
        parts.append(
            f'<text class="taiyi-geju-label" data-gong="{gong}" data-gong-name="{gong_name}" '
            f'x="{cx:.2f}" y="{cy:.2f}" text-anchor="middle" dominant-baseline="middle" '
            f'font-size="{_GEJU_LABEL_FONT_SIZE}" font-weight="700" '
            f'font-family="Noto Serif SC, KaiTi, serif" '
            f'style="font-weight:700;paint-order:stroke;stroke:#141826;'
            f'stroke-width:{_GEJU_LABEL_STROKE_WIDTH}px;stroke-linejoin:round">'
            f"{tspans}</text>"
        )

    parts.append("</g>")
    return "".join(parts)


_GUXU_INNER_STROKE = "#4D8CFF"
_GUXU_OUTER_STROKE = "#FFBF00"
_GUXU_LABEL_INNER = _GUXU_INNER_STROKE
_GUXU_LABEL_OUTER = _GUXU_OUTER_STROKE
_GUXU_LABEL_SKY = "#FFFFFF"
_GUXU_LABEL_ATTACK = "#FFD54F"
_GUXU_ARROW_COLOR = "#FFB300"
_GUXU_LABEL_FONT = 10.5
_GUXU_LABEL_STROKE = 2.0
_GUXU_INNER_STROKE_WIDTH = 2.0
_GUXU_OUTER_STROKE_WIDTH = 2.0


def _guxu_text_style(fill: str) -> str:
    return (
        f"fill:{fill} !important;paint-order:stroke;"
        f"stroke:#141826;stroke-width:{_GUXU_LABEL_STROKE}px"
    )


def _guxu_short_char(guxu: str) -> str:
    if "虛" in guxu:
        return "虛"
    if "孤" in guxu:
        return "孤"
    return ""


_GUXU_ARROW_RING_FACTOR = 0.12


def _guxu_arrow_radii(chart_style: int, *, is_life: bool) -> tuple[float, float]:
    """宜攻箭頭：自中心圓緣略向外延伸，避免遮擋盤內文字。"""
    if is_life or chart_style in (5, 6):
        return 6.0, 28.0
    if chart_style in (0, 1):
        inner_base, gap = 13.0, 45.0
    else:
        inner_base, gap = 3.0, 31.5
    r0 = inner_base + 2.0
    ring_inner = inner_base + gap
    ring_outer = inner_base + 2 * gap
    r1 = ring_inner + (ring_outer - ring_inner) * _GUXU_ARROW_RING_FACTOR
    return r0, r1


def _guxu_sync_layer_layouts(chart_style: int, *, is_life: bool) -> list[dict]:
    """第 3／4／5 層扇區幾何（與 gen_chart / gen_chart_day / gen_chart_hour 一致）。"""
    if is_life or chart_style in (5, 6):
        return []
    if chart_style in (0, 1):
        inner_base, gap = 13.0, 45.0
        specs: dict[int, tuple[int, tuple[str, ...]]] = {
            3: (16, _SIXTEEN_BRANCHES),
            4: (16, _SIXTEEN_BRANCHES),
            5: (12, _PLANET_RING_BRANCHES),
        }
    else:
        inner_base, gap = 3.0, 31.5
        if chart_style == 2:
            specs = {
                3: (8, _SIXTEEN_BRANCHES),
                4: (16, _SIXTEEN_BRANCHES),
                5: (16, _SIXTEEN_BRANCHES),
            }
        else:
            specs = {
                3: (16, _SIXTEEN_BRANCHES),
                4: (16, _SIXTEEN_BRANCHES),
                5: (16, _SIXTEEN_BRANCHES),
            }
    layouts = []
    for layer_num in (3, 4, 5):
        count, order = specs[layer_num]
        idx = layer_num - 1
        layouts.append({
            "layer": f"layer{layer_num}",
            "layer_num": layer_num,
            "inner_radius": inner_base + idx * gap,
            "outer_radius": inner_base + layer_num * gap,
            "sector_count": count,
            "branch_order": order,
        })
    return layouts


def _append_guxu_sector_borders(
    parts: list[str],
    branches: list[str],
    *,
    kind: str,
    layout: dict,
) -> None:
    stroke = _GUXU_INNER_STROKE if kind == "inner" else _GUXU_OUTER_STROKE
    width = _GUXU_INNER_STROKE_WIDTH if kind == "inner" else _GUXU_OUTER_STROKE_WIDTH
    inner = layout["inner_radius"]
    outer = layout["outer_radius"]
    for br in branches:
        if not br:
            continue
        start, end = _guxu_sector_angles_for_branch(br)
        parts.append(
            f'<path class="taiyi-guxu-border taiyi-guxu-border-{kind}" '
            f'data-branch="{br}" data-layer="{layout["layer"]}" '
            f'd="{_guxu_wedge_path(start, end, inner, outer)}" fill="none" '
            f'stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round" '
            f'pointer-events="none" '
            f'style="fill:none !important;stroke:{stroke} !important;'
            f'stroke-width:{width}px !important"/>'
        )


def _guxu_wedge_path(start: float, end: float, inner: float, outer: float) -> str:
    sr, er = math.radians(start), math.radians(end)
    sox, soy = outer * math.cos(sr), outer * math.sin(sr)
    eox, eoy = outer * math.cos(er), outer * math.sin(er)
    six, siy = inner * math.cos(sr), inner * math.sin(sr)
    eix, eiy = inner * math.cos(er), inner * math.sin(er)
    return (
        f"M {six:.2f} {siy:.2f} L {sox:.2f} {soy:.2f} "
        f"A {outer:.2f} {outer:.2f} 0 0 1 {eox:.2f} {eoy:.2f} "
        f"L {eix:.2f} {eiy:.2f} "
        f"A {inner:.2f} {inner:.2f} 0 0 0 {six:.2f} {siy:.2f} Z"
    )


def _guxu_label_xy(
    branch: str,
    layout: dict,
    *,
    radius: float | None = None,
    tangential_offset: float = 0.0,
) -> tuple[float, float]:
    start, end = _sector_angles_for_branch(branch, layout)
    mid_rad = math.radians((start + end) / 2.0)
    inner = layout["inner_radius"]
    outer = layout["outer_radius"]
    r = radius if radius is not None else (inner + outer) / 2.0
    cx = r * math.cos(mid_rad)
    cy = r * math.sin(mid_rad)
    if tangential_offset:
        cx -= tangential_offset * math.sin(mid_rad)
        cy += tangential_offset * math.cos(mid_rad)
    return cx, cy


def build_guxu_chart_model(ttext: dict | None) -> dict | None:
    """由 pan 文句推算孤虛盤面模型。"""
    ttext = ttext or {}
    ty_g = _resolve_ty_gong(ttext)
    wc = ttext.get("文昌")
    sky = str(wc[0]) if isinstance(wc, list) and wc else None
    if ty_g is None or not sky or sky not in _SIXTEEN_BRANCHES:
        return None
    return config.guxu_sectors(ty_g, sky)


def build_guxu_sector_hints(model: dict | None) -> dict[str, str]:
    """地支 → 扇區面板孤虛提示（點選 layer4 時顯示）。"""
    if not model:
        return {}
    hints: dict[str, str] = {}
    guxu = model.get("孤虛", "—")
    attack = model.get("宜攻", "—")
    sky = model.get("天目辰", "")
    if sky:
        hints[sky] = f"孤虛對照：{guxu}（天目）·宜攻{attack}"
    for br in model.get("內辰") or []:
        hints.setdefault(br, f"內側·虛（宜攻{attack}）")
    for br in model.get("外辰") or []:
        hints.setdefault(br, f"外側·孤（宜攻{attack}）")
    for br in model.get("宜攻辰") or []:
        hints[br] = f"宜攻{attack}（{guxu}）"
    return hints


def build_guxu_overlay_svg(
    ttext: dict | None,
    *,
    chart_style: int = 0,
    is_life: bool = False,
    view_half: float = 250.0,
) -> str:
    """孤虛視覺化：內（虛）／外（孤）扇區細框線 + 外環字與宜攻箭頭。"""
    if is_life or chart_style in (5, 6):
        return ""
    model = build_guxu_chart_model(ttext)
    layer_layouts = _guxu_sync_layer_layouts(chart_style, is_life=is_life)
    if not model or not layer_layouts:
        return ""

    label_layout = next((ly for ly in layer_layouts if ly["layer_num"] == 4), layer_layouts[0])
    rotate_layers = chart_svg_layout(chart_style, is_life=is_life).get("rotate_layers") or []
    ring_layout = _outer_ring_layout(chart_style, is_life=is_life)
    outer_label_r = _outer_label_radius(ring_layout, view_half=view_half)
    inner_branches = model.get("內辰") or []
    outer_branches = model.get("外辰") or []
    arrow_r0, arrow_r1 = _guxu_arrow_radii(chart_style, is_life=is_life)

    parts = [
        '<g class="taiyi-guxu-overlay" data-source="server">',
        '<defs><marker id="guxu-arrowhead" markerWidth="3" markerHeight="3" '
        'refX="2.5" refY="1.5" orient="auto">',
        f'<path d="M0,0 L3,1.5 L0,3 Z" fill="{_GUXU_ARROW_COLOR}"/></marker></defs>',
    ]

    for layout in layer_layouts:
        lid = layout["layer"]
        rot_attr = f' data-rotate-layer="{lid}"' if lid in rotate_layers else ""
        parts.append(f'<g class="taiyi-guxu-ring" data-layer="{lid}"{rot_attr}>')
        _append_guxu_sector_borders(parts, inner_branches, kind="inner", layout=layout)
        _append_guxu_sector_borders(parts, outer_branches, kind="outer", layout=layout)
        parts.append("</g>")

    label_rot = ""
    if "layer4" in rotate_layers:
        label_rot = ' data-rotate-layer="layer4"'
    parts.append(f'<g class="taiyi-guxu-labels"{label_rot}>')
    label_drawn: set[str] = set()
    for br in inner_branches:
        if br in label_drawn:
            continue
        label_drawn.add(br)
        cx, cy = _guxu_label_xy(br, label_layout, radius=outer_label_r)
        parts.append(
            f'<text class="taiyi-guxu-label taiyi-guxu-label-inner" data-branch="{br}" '
            f'x="{cx:.2f}" y="{cy:.2f}" text-anchor="middle" dominant-baseline="middle" '
            f'fill="{_GUXU_LABEL_INNER}" font-size="{_GUXU_LABEL_FONT}" font-weight="700" '
            f'font-family="Noto Serif SC, KaiTi, serif" pointer-events="none" '
            f'style="{_guxu_text_style(_GUXU_LABEL_INNER)}">'
            f"虛</text>"
        )
    for br in outer_branches:
        if br in label_drawn:
            continue
        label_drawn.add(br)
        cx, cy = _guxu_label_xy(br, label_layout, radius=outer_label_r)
        parts.append(
            f'<text class="taiyi-guxu-label taiyi-guxu-label-outer" data-branch="{br}" '
            f'x="{cx:.2f}" y="{cy:.2f}" text-anchor="middle" dominant-baseline="middle" '
            f'fill="{_GUXU_LABEL_OUTER}" font-size="{_GUXU_LABEL_FONT}" font-weight="700" '
            f'font-family="Noto Serif SC, KaiTi, serif" pointer-events="none" '
            f'style="{_guxu_text_style(_GUXU_LABEL_OUTER)}">'
            f"孤</text>"
        )
    parts.append("</g>")

    attack_branches = model.get("宜攻辰") or []
    if attack_branches:
        br = attack_branches[0]
        arrow_rot = ' data-rotate-layer="layer4"' if "layer4" in rotate_layers else ""
        parts.append(f'<g class="taiyi-guxu-arrow-group"{arrow_rot}>')
        start, end = _sector_angles_for_branch(br, label_layout)
        mid = (start + end) / 2.0
        rad = math.radians(mid)
        r0, r1 = arrow_r0, arrow_r1
        x0, y0 = r0 * math.cos(rad), r0 * math.sin(rad)
        x1, y1 = r1 * math.cos(rad), r1 * math.sin(rad)
        parts.append(
            f'<line class="taiyi-guxu-arrow" x1="{x0:.2f}" y1="{y0:.2f}" '
            f'x2="{x1:.2f}" y2="{y1:.2f}" stroke="{_GUXU_ARROW_COLOR}" '
            f'stroke-width="1.4" marker-end="url(#guxu-arrowhead)" pointer-events="none"/>'
        )
        attack_offset = 14.0 if br in label_drawn else 0.0
        cx, cy = _guxu_label_xy(
            br, label_layout, radius=outer_label_r, tangential_offset=attack_offset,
        )
        parts.append(
            f'<text class="taiyi-guxu-label taiyi-guxu-label-attack" data-branch="{br}" '
            f'x="{cx:.2f}" y="{cy:.2f}" text-anchor="middle" dominant-baseline="middle" '
            f'fill="{_GUXU_LABEL_ATTACK}" font-size="{_GUXU_LABEL_FONT}" font-weight="700" '
            f'font-family="Noto Serif SC, KaiTi, serif" pointer-events="none" '
            f'style="paint-order:stroke;stroke:#141826;stroke-width:{_GUXU_LABEL_STROKE}px">'
            f"宜攻</text>"
        )
        parts.append("</g>")

    parts.append("</g>")
    return "".join(parts)


def build_geju_sector_markers(
    ttext: dict | None,
    *,
    mishu_text: str | None = None,
) -> dict[str, list[dict]]:
    """依釋格局將八宮對應的標記（key 為宮號字串 "1"–"9"）。

    僅納入《太乙秘書》局註文字中有提及的格局（mishu_text 為空則不顯示）。
    """
    ttext = ttext or {}
    geju = ttext.get("釋格局") or {}
    if not geju or (len(geju) == 1 and "無格局" in geju):
        return {}
    if not (mishu_text or "").strip():
        return {}

    markers: dict[str, list[dict]] = {}
    for key, val in geju.items():
        if key == "無格局":
            continue
        if not geju_mentioned_in_mishu(key, mishu_text):
            continue
        entry = {
            "key": key,
            "short": _geju_short(key),
            "tone": _geju_tone(key),
            "text": _clip(str(val), 56),
            "gong": None,
            "gong_name": "",
        }
        for gong in _gongs_for_geju_entry(key, str(val), ttext):
            entry = {
                **entry,
                "gong": gong,
                "gong_name": config.num2gong(gong) or "",
            }
            bucket = markers.setdefault(str(gong), [])
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


def guxu_rotate_layer(chart_style: int = 0, *, is_life: bool = False) -> str | None:
    """孤虛標記跟隨十六宮層（layer4）；僅當該層可轉時跟盤。"""
    if is_life or chart_style in (5, 6):
        return None
    layout = chart_svg_layout(chart_style, is_life=is_life)
    if "layer4" in (layout.get("rotate_layers") or []):
        return "layer4"
    return None


def geju_rotate_layer(chart_style: int = 0, *, is_life: bool = False) -> str | None:
    """釋格局標記置於八門層（layer2），該層不參與轉盤。"""
    if is_life or chart_style in (5, 6):
        return None
    return None


def chart_svg_layout(chart_style: int = 0, *, is_life: bool = False) -> dict:
    """各盤式 SVG 互動層配置（聯動著色、轉盤）。"""
    sync_layers = ["layer3", "layer4", "layer5"]
    if is_life or chart_style in (5, 6):
        return {
            "chart_style": 5,
            "sync_layers": sync_layers,
            "rotate_layers": [],
            "geju_rotate_layer": None,
        }
    return {
        "chart_style": chart_style,
        "sync_layers": sync_layers,
        "rotate_layers": list(sync_layers),
        "geju_rotate_layer": None,
    }


def build_palace_state_overlay_svg(life_pan: dict | None, *, is_life: bool = True) -> str:
    """命盤十二宮旺衰絕空刑角標（疊加於地支環）。"""
    if not is_life or not life_pan:
        return ""
    vol20 = life_pan.get("卷二十") or {}
    wang = vol20.get("十二宮旺衰絕空刑") or {}
    palace_map = life_pan.get("十二命宮排列") or {}
    branch_state: dict[str, str] = {}
    for br, palace in palace_map.items():
        state = (wang.get(palace) or {}).get("狀態")
        if state:
            branch_state[br] = state
    if not branch_state:
        return ""

    import math

    inner_radius = 12
    layer_gap = 35
    layer_idx = 2
    inner = inner_radius + layer_idx * layer_gap
    outer = inner_radius + (layer_idx + 1) * layer_gap
    mid_r = (inner + outer) / 2
    rotation = 248
    parts = [
        '<g class="taiyi-palace-state-overlay" pointer-events="none">',
    ]
    for i, branch in enumerate(_TWELVE_BRANCHES):
        state = branch_state.get(branch)
        if not state:
            continue
        ang = math.radians((360 / 12) * (i + 0.5) + rotation)
        x = mid_r * math.cos(ang) + 14 * math.cos(ang)
        y = mid_r * math.sin(ang) + 14 * math.sin(ang)
        parts.append(
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" '
            f'font-size="9" font-weight="700" fill="#e9cc88">{state}</text>'
        )
    parts.append("</g>")
    return "".join(parts)


def format_tooltip(entry: dict | None, fallback: str = "") -> str:
    """將 sector entry 格式化為 tooltip 多行文字。"""
    if not entry:
        return fallback
    parts = [entry.get("title", "")]
    parts.extend(entry.get("lines") or [])
    text = "\n".join(p for p in parts if p)
    return text or fallback