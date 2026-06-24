# 《太乙統宗寶鑑》卷八：九宮分野疆界、十二分野、絳宮明堂玉堂

from __future__ import annotations

from . import config

# 十二辰次分野（卷八、卷九動爻分野）
_SHIER_FENYE = {
    "寅": ("燕", "幽州", "析木之次"),
    "卯": ("宋", "豫州", "太火之次"),
    "辰": ("鄭", "兗州", "壽星之次"),
    "巳": ("楚", "荆州", "鶉尾之次"),
    "午": ("周", "三河", "鶉火之次"),
    "未": ("秦", "雍州", "鶉首之次"),
    "申": ("晉", "益州", "實沈之次"),
    "酉": ("趙", "冀州", "大梁之次"),
    "戌": ("魯", "徐州", "降婁之次"),
    "亥": ("衛", "并州", "陬訾之次"),
    "子": ("齊", "青州", "星紀之次"),
    "丑": ("吳", "揚州", "玄枵之次"),
}

# 九宮正卦分野（卷八「明太乙經行九宮分野成名」）
_JIUGONG_FENYE = {
    1: ("冀州", "丁丑", "北方坎水"),
    2: ("荆州", "丁未", "正南離火"),
    3: ("青州", "癸丑", "東北艮土"),
    4: ("徐州", "甲辰", "正東震木"),
    5: ("豫州", "乙丑", "中央土"),
    6: ("雍州", "甲申", "正西兌金"),
    7: ("梁州", "戊戌", "西南坤土"),
    8: ("兗州", "乙未", "正北坎水"),
    9: ("揚州", "癸酉", "東南巽木"),
}

# 絳宮、明堂、玉堂（卷八附）
_TE_GONG = {
    "絳宮": {
        "干支": "己巳",
        "分野": "交州",
        "禹貢": "揚州之域（南越）",
        "宮名例": "合浦壬申",
        "要訣": "南越交趾，禹貢揚州南境",
    },
    "明堂": {
        "干支": "辛丑",
        "分野": "益州",
        "禹貢": "梁州之域",
        "宮名例": "成都嘉犍為",
        "要訣": "益州梁雍，參伐所主",
    },
    "玉堂": {
        "干支": "癸卯",
        "分野": "幽州",
        "禹貢": "冀州之域",
        "宮名例": "范陽燕國",
        "要訣": "幽州燕分，箕星所主",
    },
}


def shier_fenye(zhi: str | None = None) -> dict | list:
    """十二分野表；可單查一地支。"""
    if zhi:
        guo, zhou, ci = _SHIER_FENYE.get(zhi, ("", "", ""))
        return {
            "地支": zhi,
            "國": guo,
            "州": zhou,
            "次舍": ci,
            "斷語": f"{zhi}為{guo}分，于野為{zhou}",
        }
    return [
        {"地支": z, "國": v[0], "州": v[1], "次舍": v[2]}
        for z, v in _SHIER_FENYE.items()
    ]


def jiugong_fenye(gong: int | str | None = None) -> dict | list:
    """九宮分野；可單查一宮。"""
    if gong is not None:
        num = gong if isinstance(gong, int) else config.gong.get(gong)
        zhou, gz, wx = _JIUGONG_FENYE.get(num, ("", "", ""))
        name = config.num2gong(num) if num else ""
        return {
            "宮": num,
            "宮名": name,
            "州": zhou,
            "城名干支": gz,
            "五行象": wx,
            "斷語": f"太乙臨{name or num}宮，主{zhou}分野災祥",
        }
    return [
        {"宮": n, "宮名": config.num2gong(n), "州": v[0], "城名干支": v[1], "五行象": v[2]}
        for n, v in _JIUGONG_FENYE.items()
    ]


def tegong_fenye(name: str | None = None) -> dict:
    """絳宮、明堂、玉堂分野。"""
    if name and name in _TE_GONG:
        return {"宮名": name, **_TE_GONG[name]}
    return dict(_TE_GONG)


def _palace_num(ty: int | str) -> int | None:
    if isinstance(ty, int):
        return ty
    if isinstance(ty, str) and ty.isdigit():
        return int(ty)
    return config.gong.get(ty)


def fenye_for_palace(ty: int | str) -> dict:
    """依太乙所在宮推當年分野。"""
    num = _palace_num(ty)
    if num is None:
        return {"宮名": str(ty), "斷語": "宮位未明"}
    base = jiugong_fenye(num)
    if not isinstance(base, dict):
        base = {}
    cheng = config._NINE_GONG_CHENG.get(num)
    te = None
    if cheng:
        for tname, (zhou, gz) in config._EXTRA_GONG_CHENG.items():
            if gz == cheng[1]:
                te = {"宮名": tname, **_TE_GONG[tname]}
                break
    year_zhi = None
    if cheng:
        year_zhi = cheng[1][1] if len(cheng[1]) > 1 else None
    shier = shier_fenye(year_zhi) if year_zhi in _SHIER_FENYE else {}
    return {
        **base,
        "城名": cheng[0] if cheng else "",
        "城名干支": cheng[1] if cheng else "",
        "特宮": te,
        "十二分野": shier,
        "要訣": "九宮臨分野，遇開休生大吉，杜傷死大凶",
    }


def zonghe(ty: int | str, year_zhi: str | None = None) -> dict:
    """卷八綜合：九宮分野、十二分野、絳宮明堂玉堂。"""
    palace = fenye_for_palace(ty)
    shier = shier_fenye(year_zhi) if year_zhi else None
    return {
        "太乙分野": palace,
        "十二分野表": shier_fenye(),
        "九宮分野表": jiugong_fenye(),
        "絳宮明堂玉堂": tegong_fenye(),
        "歲建分野": shier,
        "要訣": (
            f"太乙在{palace.get('宮名', '')}宮，主{palace.get('州', '')}；"
            f"天有十二次，地有十二辰，王侯之所國"
        ),
    }