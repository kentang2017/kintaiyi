# 《太乙統宗寶鑑》卷十二補：災厄首尾、入運變卦納甲、觀象期、歲本建子為正

from __future__ import annotations

from . import config

# 八卦方位（卷十二變卦觀象）
_BAGUA_FANG = {
    "乾": "西北", "坤": "西南", "震": "正東", "巽": "東南",
    "坎": "正北", "離": "正南", "艮": "東北", "兌": "正西",
}
# 納甲地支分野（卷十二）
_ZHI_FENYE = {
    "子": "齊·青州", "丑": "吳越·揚州", "寅": "燕·幽州", "卯": "宋·豫州",
    "辰": "鄭·兗州", "巳": "楚·荆州", "午": "周·三河", "未": "秦·雍州",
    "申": "晉·益州", "酉": "趙·冀州", "戌": "魯·徐州", "亥": "衛·并州",
}
# 納甲天干分野（卷十二）
_GAN_FENYE = {
    "甲": "東兵·齊", "乙": "東夷", "丙": "吳楚", "丁": "蠻夷海奧",
    "庚": "正西·秦", "辛": "梁益·西戎", "壬": "正北·燕冀", "癸": "北夷",
    "戊": "中原·豫州三河", "己": "中原·豫州三河",
}
# 京房納甲（內卦三爻、外卦三爻）
_NAJIA_INNER = {
    "乾": ("甲子", "甲寅", "甲辰"), "坤": ("乙未", "乙巳", "乙卯"),
    "震": ("庚子", "庚寅", "庚辰"), "巽": ("辛丑", "辛亥", "辛酉"),
    "坎": ("戊寅", "戊辰", "戊午"), "離": ("己卯", "己丑", "己亥"),
    "艮": ("丙辰", "丙午", "丙戌"), "兌": ("丁巳", "丁卯", "丁丑"),
}
_NAJIA_OUTER = {
    "乾": ("壬午", "壬申", "壬戌"), "坤": ("癸丑", "癸亥", "癸酉"),
    "震": ("庚午", "庚申", "庚戌"), "巽": ("辛未", "辛巳", "辛卯"),
    "坎": ("戊申", "戊戌", "戊子"), "離": ("己酉", "己未", "己巳"),
    "艮": ("丙戌", "丙子", "丙寅"), "兌": ("丁亥", "丁酉", "丁未"),
}
# 變卦象（卷十二遷幸方）
_BIAN_GUA_XIANG = {
    "乾": "大河", "坎": "陰阻", "艮": "山陵", "震": "關梁",
    "巽": "林壑", "離": "湖漳", "坤": "大川", "兌": "泊澤",
}
_YAO_NAMES = ("初", "二", "三", "四", "五", "上")
_MONTH_ZHI = list(config.di_zhi)


def _gua_code(gua_name: str) -> str:
    for code, name in config.sixtyfourgua.items():
        if name == gua_name:
            bits = code if isinstance(code, tuple) else (code,)
            for b in bits:
                if len(b) == 6:
                    return b.replace("9", "7").replace("6", "8")
    return "777777"


def _flip_yao(code: str, yao_idx: int) -> str:
    g = list(code)
    i = yao_idx - 1
    g[i] = "8" if g[i] == "7" else "7"
    return "".join(g)


def _bits_from_code(code: str) -> list[bool]:
    return [c in config._YANG_GUA_LINE for c in code]


def _trigram_name(bits3: tuple[bool, bool, bool]) -> str:
    table = {
        (True, True, True): "乾", (True, True, False): "兌",
        (True, False, True): "離", (True, False, False): "震",
        (False, True, True): "巽", (False, True, False): "坎",
        (False, False, True): "艮", (False, False, False): "坤",
    }
    return table[bits3]


def _split_trigrams(gua_name: str) -> tuple[str, str]:
    bits = _bits_from_code(_gua_code(gua_name))
    lower = tuple(bits[:3])
    upper = tuple(bits[3:])
    return _trigram_name(lower), _trigram_name(upper)


def najia_for_yao(gua_name: str, yao_idx: int) -> dict:
    """京房納甲：取卦中某一爻之干支。"""
    inner, outer = _split_trigrams(gua_name)
    if yao_idx <= 3:
        gz = _NAJIA_INNER[inner][yao_idx - 1]
        scope = "內卦"
        bagua = inner
    else:
        gz = _NAJIA_OUTER[outer][yao_idx - 4]
        scope = "外卦"
        bagua = outer
    gan, zhi = gz[0], gz[1]
    return {
        "納甲": gz,
        "天干": gan,
        "地支": zhi,
        "內外": scope,
        "八卦": bagua,
        "方位": _BAGUA_FANG.get(bagua, ""),
        "地支分野": _ZHI_FENYE.get(zhi, ""),
        "天干分野": _GAN_FENYE.get(gan, ""),
    }


def tongyun_bian_gua(year: int) -> dict:
    """入運行爻變卦納甲（卷十二）。"""
    rugua = config.tongyun_rugua(year)
    gua = rugua["卦"]
    yao = rugua["爻"]
    code = _gua_code(gua)
    new_code = _flip_yao(code, yao)
    bian = config.multi_key_dict_get(config.sixtyfourgua, new_code) or gua
    najia = najia_for_yao(gua, yao)
    inner, outer = _split_trigrams(bian)
    return {
        "公元年": year,
        "本卦": gua,
        "動爻": yao,
        "爻名": rugua["爻名"],
        "變卦": bian,
        "內卦": inner,
        "外卦": outer,
        "內卦象": _BIAN_GUA_XIANG.get(inner, ""),
        "外卦象": _BIAN_GUA_XIANG.get(outer, ""),
        "納甲": najia,
        "要訣": (
            f"內卦主事生於內，外卦起於外藩；"
            f"{najia['納甲']}在{najia['方位']}（{najia['地支分野']}）"
        ),
    }


def _segment_for_gua(gua: str) -> dict:
    for seg in config._TONGYUN_SEGMENTS:
        if seg["卦"] == gua:
            return seg
    return config._TONGYUN_SEGMENTS[-1]


def tongyun_shouwei(year: int) -> dict:
    """入運災厄首尾（卷十二）。"""
    rugua = config.tongyun_rugua(year)
    seg = _segment_for_gua(rugua["卦"])
    gua_total = seg["年數"]
    gua_off = rugua["入卦年數"]
    yao = rugua["爻"]
    yang = rugua["陽爻"]
    jinian = rugua["統運積年"]

    is_gua_shou = gua_off == 1
    is_gua_wei = gua_off >= gua_total
    # 運首尾：本運第一卦首年、末卦末年
    yun_segs = [s for s in config._TONGYUN_SEGMENTS if s["運"] == seg["運"]]
    is_yun_first = seg["卦"] == yun_segs[0]["卦"] and is_gua_shou
    is_yun_last = seg["卦"] == yun_segs[-1]["卦"] and is_gua_wei

    ji_positions = (4, 5) if yang else (2, 6)
    is_ji_yao = yao in ji_positions
    is_nei_wai_ji = yao in (1, 3, 6)

    shouwei_flags = []
    if is_gua_shou:
        shouwei_flags.append("入卦首年")
    if is_gua_wei:
        shouwei_flags.append("入卦末年")
    if is_yun_first:
        shouwei_flags.append("入運首年")
    if is_yun_last:
        shouwei_flags.append("入運末年")
    if is_ji_yao:
        shouwei_flags.append("極爻災厄位")
    if is_nei_wai_ji:
        shouwei_flags.append("內外極爻")

    at_risk = bool(shouwei_flags) and (is_gua_shou or is_gua_wei or is_yun_first or is_yun_last)
    ji60 = jinian % 60

    disaster = []
    if at_risk and is_ji_yao:
        disaster.append("交運首尾，極爻主災")
    if at_risk and is_nei_wai_ji:
        disaster.append("內外極，災變較重" if yao == 6 else "內極，災變尚輕")
    if ji60 in (0, 59):
        disaster.append("紀法交首尾")

    return {
        "公元年": year,
        "卦": rugua["卦"],
        "爻": rugua["爻名"],
        "入卦年數": gua_off,
        "卦總年": gua_total,
        "首尾標記": shouwei_flags,
        "是否首尾": at_risk,
        "極爻災厄": is_ji_yao,
        "紀法餘": ji60,
        "斷語": "；".join(disaster) if disaster else (
            "非交運首尾" if not at_risk else "交際之年，宜修德慎守"
        ),
        "要訣": "陽爻四五、陰爻二六為極爻災厄；交運首尾忌陽九百六出入",
    }


def tongyun_guanxiang_qi(year: int) -> dict:
    """統運入卦觀象期：歲內十二月直事（卷十二咸→萃例）。"""
    rugua = config.tongyun_rugua(year)
    bian = tongyun_bian_gua(year)
    start = rugua["爻"] - 1
    months = []
    for m in range(1, 13):
        if m <= 6:
            gua = rugua["卦"]
            phase = "本卦"
        else:
            gua = bian["變卦"]
            phase = "變卦"
        yao_idx = (start + m - 1) % 6 + 1
        yang = _bits_from_code(_gua_code(gua))[yao_idx - 1]
        yao_name = (config._YAO_NAMES_YANG if yang else config._YAO_NAMES_YIN)[yao_idx - 1]
        months.append({
            "月序": m,
            "月建": _MONTH_ZHI[(m + 10) % 12],
            "階段": phase,
            "卦": gua,
            "爻": yao_idx,
            "爻名": yao_name,
        })
    return {
        "公元年": year,
        "本卦": rugua["卦"],
        "變卦": bian["變卦"],
        "起爻": rugua["爻名"],
        "十二月直事": months,
        "要訣": "上半年本卦、下半年變卦；自入爻起順推十二月",
    }


def suiben_jianzi_weizheng(year: int, month: int = 1, day: int = 15) -> dict:
    """歲本建子為正（卷十二）：太乙歲本與夏正歲首對照。"""
    gz = config.gangzhi(year, month, day, 12, 0)
    lunar = config.lunar_date_d(year, month, day)
    lunar_month = int(lunar.get("月", month))
    # 太乙天道以子為歲首：農曆十一月起算新歲
    taiyi_sui = year if lunar_month >= 11 else year - 1
    return {
        "公元年": year,
        "農曆": f"{lunar.get('年', year)}年{lunar.get('農曆月', '')}",
        "年干支": f"{gz[0][0]}{gz[0][1]}",
        "夏正歲首": "建寅（時王正）",
        "太乙歲本": "建子（天道正）",
        "太乙歲": taiyi_sui,
        "時王歲": year,
        "要訣": "演紀推元以子始終於亥；人事建寅，天道建子",
    }


def vol12_extended(year: int, year_gan=None, year_zhi=None, month=1, day=15) -> dict:
    """卷十二擴充：首尾、變卦納甲、觀象期、歲本建子。"""
    return {
        "災厄首尾": tongyun_shouwei(year),
        "變卦納甲": tongyun_bian_gua(year),
        "觀象期": tongyun_guanxiang_qi(year),
        "歲本建子": suiben_jianzi_weizheng(year, month, day),
    }