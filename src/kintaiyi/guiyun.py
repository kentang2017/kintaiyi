# 《太乙統宗寶鑑》卷九：大遊小遊軌運入卦、重卦策數、陽九百六限數

from __future__ import annotations

from . import config
from .tongyun_extras import _bits_from_code, _gua_code, _split_trigrams

# 大遊內卦起坤七宮順行；外卦同序每十年一易
_DAYOU_BAGUA = ("坤", "坎", "巽", "乾", "離", "艮", "震", "兌")
# 小遊內外卦起乾離艮震兌坤坎巽
_XIAOYOU_BAGUA = ("乾", "離", "艮", "震", "兌", "坤", "坎", "巽")

# 四象之策（卷九）
_CE_CE = {
    "乾": ("老陽", 36),
    "坤": ("老陰", 24),
    "震": ("少陽", 28),
    "坎": ("少陽", 28),
    "艮": ("少陽", 28),
    "巽": ("少陰", 32),
    "離": ("少陰", 32),
    "兌": ("少陰", 32),
}

_YAO_GAN_FENYE = {
    "甲": "東兵·齊", "乙": "東夷·宋", "丙": "南楚·吳", "丁": "蠻夷",
    "戊": "中原", "己": "豫州", "庚": "正西·秦", "辛": "梁益·西戎",
    "壬": "燕冀", "癸": "北狄",
}
_YAO_ZHI_FENYE = {
    "子": "齊", "丑": "吳", "寅": "燕", "卯": "宋", "辰": "鄭", "巳": "楚",
    "午": "周", "未": "秦", "申": "晉", "酉": "趙", "戌": "魯", "亥": "衛",
}


def _bagua_at(order: tuple[str, ...], quotient: int, remainder: int,
              cycle_years: int) -> tuple[str, int, int]:
    idx = quotient if quotient else len(order)
    years = remainder or cycle_years
    return order[idx - 1], idx, years


_TRIGRAM_BITS = {
    "乾": (True, True, True), "兌": (True, True, False),
    "離": (True, False, True), "震": (True, False, False),
    "巽": (False, True, True), "坎": (False, True, False),
    "艮": (False, False, True), "坤": (False, False, False),
}


def _compose_gua(inner: str, outer: str) -> str:
    lower = _TRIGRAM_BITS[inner]
    upper = _TRIGRAM_BITS[outer]
    code = "".join("7" if b else "8" for b in (*lower, *upper))
    return config.multi_key_dict_get(config.sixtyfourgua, code) or f"{outer}{inner}"


def dayou_nei_gua(taiyi_acumyear: int) -> dict:
    """大遊軌運入內卦（三十六歲一宮）。"""
    rem = (taiyi_acumyear + 34) % 2880 % 288
    q, r = divmod(rem, 36)
    gua, idx, years = _bagua_at(_DAYOU_BAGUA, q, r, 36)
    yao = (years - 1) // 6 + 1
    yang = _bits_from_code(_gua_code(gua))[yao - 1] if gua in config._KING_WEN_64 else True
    yao_name = (config._YAO_NAMES_YANG if yang else config._YAO_NAMES_YIN)[yao - 1]
    ce, ce_num = _CE_CE[gua]
    return {
        "內卦": gua,
        "卦序": idx,
        "入卦年數": years,
        "動爻": yao,
        "爻名": yao_name,
        "四象": ce,
        "策數": ce_num,
        "滿宮": years == 36,
        "要訣": "三十六年行一內卦，六年行一爻",
    }


def dayou_wai_gua(taiyi_acumyear: int) -> dict:
    """大遊軌運入外卦（每十年一易，六百四十年一周）。"""
    rem = (taiyi_acumyear + 50) % 640 % 80
    q, r = divmod(rem, 10)
    gua, idx, years = _bagua_at(_DAYOU_BAGUA, q, r, 10)
    ce, ce_num = _CE_CE[gua]
    return {
        "外卦": gua,
        "卦序": idx,
        "入卦年數": years,
        "動爻": 6 if years == 10 else max(1, (years - 1) // 2 + 4),
        "四象": ce,
        "策數": ce_num,
        "滿卦": years == 10,
        "要訣": "每十年一易外卦，周六十四卦六百四十年",
    }


def dayou_chong_gua(taiyi_acumyear: int) -> dict:
    """大遊內外重卦。"""
    nei = dayou_nei_gua(taiyi_acumyear)
    wai = dayou_wai_gua(taiyi_acumyear)
    name = _compose_gua(nei["內卦"], wai["外卦"])
    total_ce = nei["策數"] + wai["策數"]
    return {
        "重卦": name,
        "內卦": nei["內卦"],
        "外卦": wai["外卦"],
        "內動爻": nei["動爻"],
        "內爻名": nei["爻名"],
        "外動爻": wai["動爻"],
        "內策": nei["策數"],
        "外策": wai["策數"],
        "總策": total_ce,
        "入內年數": nei["入卦年數"],
        "入外年數": wai["入卦年數"],
        "要訣": "內卦主創業之事，外卦主盛衰之數；內極三爻災輕，外極上爻災重",
    }


def xiaoyou_nei_gua(taiyi_acumyear: int) -> dict:
    """小遊軌運入內卦（二十四年一卦）。"""
    rem = taiyi_acumyear % 1920 % 192
    q, r = divmod(rem, 24)
    gua, idx, years = _bagua_at(_XIAOYOU_BAGUA, q, r, 24)
    yao = (years - 1) // 4 + 1
    yang = True
    if gua in config._KING_WEN_64:
        yang = _bits_from_code(_gua_code(gua))[yao - 1]
    yao_name = (config._YAO_NAMES_YANG if yang else config._YAO_NAMES_YIN)[yao - 1]
    ce, ce_num = _CE_CE[gua]
    return {
        "內卦": gua,
        "卦序": idx,
        "入卦年數": years,
        "動爻": yao,
        "爻名": yao_name,
        "四象": ce,
        "策數": ce_num,
        "滿卦": years == 24,
        "要訣": "二十四年行一內卦，四年行一爻",
    }


def xiaoyou_wai_gua(taiyi_acumyear: int) -> dict:
    """小遊軌運入外卦（三年一卦）。"""
    rem = taiyi_acumyear % 360 % 24
    q, r = divmod(rem, 3)
    gua, idx, years = _bagua_at(_XIAOYOU_BAGUA, q, r, 3)
    ce, ce_num = _CE_CE[gua]
    tian_li = ("理天", "理地", "理人")[years - 1]
    return {
        "外卦": gua,
        "卦序": idx,
        "入卦年數": years,
        "三才": tian_li,
        "四象": ce,
        "策數": ce_num,
        "滿卦": years == 3,
        "要訣": "三年行一外卦，一年理天、二年理地、三年理人",
    }


def xiaoyou_chong_gua(taiyi_acumyear: int) -> dict:
    """小遊內外重卦。"""
    nei = xiaoyou_nei_gua(taiyi_acumyear)
    wai = xiaoyou_wai_gua(taiyi_acumyear)
    name = _compose_gua(nei["內卦"], wai["外卦"])
    return {
        "重卦": name,
        "內卦": nei["內卦"],
        "外卦": wai["外卦"],
        "內動爻": nei["動爻"],
        "內爻名": nei["爻名"],
        "外三才": wai["三才"],
        "內策": nei["策數"],
        "外策": wai["策數"],
        "總策": nei["策數"] + wai["策數"],
        "入內年數": nei["入卦年數"],
        "入外年數": wai["入卦年數"],
        "要訣": "卦主其事，爻主其時；二五安平，內外極爻多凶",
    }


def yangjiu_xian(taiyi_acumyear: int) -> dict:
    """陽九災變大小限（4560／456）。"""
    rem_big = (taiyi_acumyear + 130) % 4560
    small_idx = rem_big // 456
    years_in = rem_big % 456 or 456
    at_end = years_in in (1, 456) or rem_big % 4560 in (0, 4559)
    return {
        "大限元數": 4560,
        "小限元數": 456,
        "入小限序": small_idx + 1 if rem_big % 456 else (rem_big // 456 or 10),
        "入限年數": years_in if rem_big % 456 else 456,
        "臨數終": at_end,
        "斷語": (
            "陽窮於九，極則災變；宜修政修禳、偃兵息民"
            if at_end else f"陽九小限第{small_idx + 1}元，入限{years_in}年"
        ),
        "要訣": "四千五百六十年為大限之極，四百五十六年為小限之極",
    }


def bailiu_xian(taiyi_acumyear: int) -> dict:
    """百六災變大小限（4320／288）。"""
    rem_big = (taiyi_acumyear + 2050) % 4320
    small_idx = rem_big // 288
    years_in = rem_big % 288 or 288
    at_end = years_in in (1, 288) or rem_big % 4320 in (0, 4319)
    return {
        "大限元數": 4320,
        "小限元數": 288,
        "入小限序": small_idx + 1 if rem_big % 288 else (rem_big // 288 or 15),
        "入限年數": years_in if rem_big % 288 else 288,
        "臨數終": at_end,
        "斷語": (
            "陰窮於六，厄會水旱；宜薄賦省刑、修德應天"
            if at_end else f"百六小限第{small_idx + 1}元，入限{years_in}年"
        ),
        "要訣": "四千三百二十年為大限之極，二百八十八年為小限之極",
    }


def xiaoyou_xingyao_zai(taiyi_acumyear: int) -> dict:
    """小遊統卦行爻所主災祥（納甲分野摘要）。"""
    chg = xiaoyou_chong_gua(taiyi_acumyear)
    gua = chg["重卦"]
    yao = chg["內動爻"]
    if gua in config._KING_WEN_64:
        inner, outer = _split_trigrams(gua)
        scope = "內" if yao <= 3 else "外"
        bagua = inner if yao <= 3 else outer
    else:
        scope, bagua = "內", chg["內卦"]
    najia = None
    if gua in config._KING_WEN_64:
        from .tongyun_extras import najia_for_yao  # noqa: PLC0415
        najia = najia_for_yao(gua, yao)
    gan_zhi = najia["納甲"] if najia else ""
    gan, zhi = (gan_zhi[0], gan_zhi[1]) if len(gan_zhi) >= 2 else ("", "")
    if yao in (2, 5):
        duan = "行於中道，安平之歲"
    elif yao in (1, 4):
        duan = "初四之爻，箕和有應則吉，忌關掩迫"
    else:
        duan = "內外極爻，事多凶變"
    return {
        "重卦": gua,
        "動爻": yao,
        "爻名": chg["內爻名"],
        "納甲": gan_zhi,
        "天干分野": _YAO_GAN_FENYE.get(gan, ""),
        "地支分野": _YAO_ZHI_FENYE.get(zhi, ""),
        "斷語": duan,
        "要訣": "甲乙風雷疾疫，丙丁大旱光怪，庚辛兵革，壬癸大水",
    }


def zonghe(taiyi_acumyear: int, year: int | None = None,
                month: int = 1, day: int = 15) -> dict:
    """卷九綜合：大小遊軌運、重卦策數、陽九百六限數。"""
    dayou = dayou_chong_gua(taiyi_acumyear)
    xiaoyou = xiaoyou_chong_gua(taiyi_acumyear)
    yj = yangjiu_xian(taiyi_acumyear)
    bl = bailiu_xian(taiyi_acumyear)
    xy_zai = xiaoyou_xingyao_zai(taiyi_acumyear)
    palace_big = config.bigyo(taiyi_acumyear)
    palace_small = config.smyo(taiyi_acumyear)
    extra = {}
    if year is not None:
        extra["歲計陽九支"] = config.yangjiu(year, month, day)
        extra["歲計百六支"] = config.baliu(year, month, day)
    return {
        "大遊軌運": dayou,
        "小遊軌運": xiaoyou,
        "大遊落宮": config.num2gong(palace_big) if palace_big else "",
        "小遊落宮": config.num2gong(palace_small) if palace_small else "",
        "行宮卦異": dayou["內卦"] != xiaoyou["內卦"],
        "陽九限數": yj,
        "百六限數": bl,
        "小遊行爻災祥": xy_zai,
        **extra,
        "要訣": (
            f"大遊{dayou['重卦']}{dayou['內爻名']}，"
            f"小遊{xiaoyou['重卦']}{xiaoyou['內爻名']}；"
            f"陽九入限{yj['入限年數']}年，百六入限{bl['入限年數']}年"
        ),
    }