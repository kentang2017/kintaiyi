# 《太乙統宗寶鑑》卷十八：十精所主、十精太乙雲氣所主

from __future__ import annotations

from . import config

# 十精合會雲氣斷語（卷十八詩訣摘要）
_JING_HEHUI = {
    "天皇": {
        "合太乙陽宮": "日暈晝昏，風遍天下",
        "合太乙陰宮": "月暈夜昏",
        "合東方": "日暈大風",
        "合南方": "日暈有雲氣",
        "合北方": "日色大暈",
        "合天目": "大陰雨",
    },
    "地符": {
        "合太乙": "日暈",
        "陽宮": "晴",
        "陰宮": "雨",
        "旺相": "小雨小陰雲、疾風猝起",
        "合天目": "小陰疾風",
    },
    "太尊": {
        "合太乙旺相": "陰雨",
        "八宮": "陰雨",
        "六宮": "日暈",
        "二宮": "陰暗",
        "四宮": "陰寒",
        "合天目": "陰雨大昏",
        "合飛鳥三風五風": "陰雨大昏",
    },
    "飛鳥": {
        "合太乙旺相": "天星有變、大風",
        "合天時": "陰風",
        "九六宮": "日暈",
        "合三風五風": "大風",
    },
    "五行": {
        "合太乙": "暴風寒、雲氣昏沉",
        "合風神": "吹沙拔木",
    },
    "五風": {
        "合太乙旺相": "日月有變、連陰暴雨",
        "合太乙": "小陰雨",
        "合飛鳥": "疾風",
        "合天符": "大風雨",
        "合天目": "大陰小風",
    },
    "八風": {
        "合太乙旺相": "小雨兼風",
        "休囚": "寂然無風",
    },
    "三風": {
        "合太乙": "風起號令",
    },
}

# 雲氣色與變法時辰（卷十八子房風雨期）
_YUNQI_COLOR = {
    "青": {"數": (3, 4), "變時": "寅卯", "象": "風寒"},
    "赤": {"數": (9, 2), "變時": "巳午", "象": "風"},
    "白": {"數": (7, 6), "變時": "亥子", "象": "風寒"},
    "黃": {"數": (5,), "變時": "四季", "象": "暈"},
    "黑": {"數": (6,), "變時": "—", "象": "風雨"},
    "紅": {"數": (2, 7), "變時": "—", "象": "風"},
}

_YANG_GONG = frozenset({1, 2, 3, 4, 6, 9})
_YIN_GONG = frozenset({7, 8, 5})

_TEN_JING_FN = {
    "天皇": config.tian_wang,
    "地符": config.kingfu,
    "太尊": config.taijun,
    "飛鳥": config.flybird,
    "五行": config.wuxing,
    "五風": config.fivewind,
    "八風": config.eightwind,
    "三風": config.threewind,
    "天時": config.tian_shi,
    "太歲": lambda acc: config.num2gong((acc % 12) or 12),
}


def _palace_label(val) -> tuple[int | None, str]:
    if val is None:
        return None, ""
    if isinstance(val, int):
        return val, config.num2gong(val)
    if isinstance(val, str) and val.isdigit():
        n = int(val)
        return n, config.num2gong(n)
    g = config.gong.get(val)
    return g, val if g else str(val)


def shijing_luo(taiyi_acumyear: int) -> dict:
    """十精落宮。"""
    result = {}
    for name, fn in _TEN_JING_FN.items():
        raw = fn(taiyi_acumyear)
        num, label = _palace_label(raw)
        result[name] = {
            "落宮": label or str(raw),
            "宮數": num,
            "陰陽": "陽" if num in _YANG_GONG else ("陰" if num in _YIN_GONG else ""),
        }
    return result


def shijing_shu(taiyi_acumyear: int) -> dict:
    """十精太乙數（周紀三百六十、元法七十二）。"""
    rem = taiyi_acumyear % 360
    shu = rem % 72 or 72
    return {
        "周紀餘": rem,
        "十精數": shu,
        "斷語": _shu_duanyu(shu),
        "要訣": "數三十大風日暈，四十陰雨，五十與天目合則旺相",
    }


def _shu_duanyu(shu: int) -> str:
    if shu == 30:
        return "大風，日暈"
    if shu == 40:
        return "陰雨"
    if shu == 50:
        return "黃霧塵，與天目合則旺相"
    if shu == 10:
        return "天數，與計目合則大風"
    if shu == 5:
        return "地數"
    return f"十精數{shu}，視與太乙沖合而斷風雨"


def yunqi_hehui(jing_name: str, jing_gong: int | None, ty: int | None) -> list[str]:
    """單一十精與太乙合會雲氣斷語。"""
    rules = _JING_HEHUI.get(jing_name, {})
    if not rules or not ty or not jing_gong:
        return []
    hits = []
    if jing_gong == ty:
        hits.append(rules.get("合太乙", rules.get("合太乙旺相", f"{jing_name}與太乙同宮")))
    ty_yang = ty in _YANG_GONG
    jing_yang = jing_gong in _YANG_GONG
    if ty_yang and jing_yang:
        hits.append(rules.get("合太乙陽宮", rules.get("陽宮", "合陽位則晴")))
    if not ty_yang and not jing_yang:
        hits.append(rules.get("陰宮", "合陰位則雨"))
    return hits or [f"{jing_name}在{config.num2gong(jing_gong)}，與太乙{config.num2gong(ty)}無特殊合會"]


def yunqi_zongduan(taiyi_acumyear: int, ty: int) -> dict:
    """十精雲氣綜斷。"""
    luo = shijing_luo(taiyi_acumyear)
    shu = shijing_shu(taiyi_acumyear)
    hehui = {}
    for name, info in luo.items():
        g = info.get("宮數")
        if g:
            hehui[name] = yunqi_hehui(name, g, ty)
    # 子房總訣
    zifang = []
    for jing in ("地符", "太尊", "五風", "八風", "三風"):
        g = luo.get(jing, {}).get("宮數")
        if not g:
            continue
        if g in _YANG_GONG and g == ty:
            zifang.append(f"{jing}與太乙合陽宮為晴")
        elif g in _YIN_GONG and g == ty:
            zifang.append(f"{jing}與太乙合陰宮為雨")
    return {
        "十精落宮": luo,
        "十精數": shu,
        "合會斷語": hehui,
        "子房總訣": zifang or ["十精與太乙未全合會，視旺相消息而推"],
        "雲氣色法": _YUNQI_COLOR,
        "要訣": "陽占旱、陰占雨；旺相則變病雨而速，休囚則遲",
    }


def zonghe(taiyi_acumyear: int, ty: int) -> dict:
    """卷十八綜合：十精所主、雲氣合會。"""
    yq = yunqi_zongduan(taiyi_acumyear, ty)
    same = [n for n, i in yq["十精落宮"].items() if i.get("宮數") == ty]
    return {
        **yq,
        "與太乙同宮": same,
        "要訣": (
            f"十精同宮：{'、'.join(same) if same else '無'}；"
            f"十精數{yq['十精數']['十精數']}，"
            f"{yq['十精數']['斷語']}"
        ),
    }