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


# 卷九「陰陽九厄水旱災期」九會分期（OCR line 5010-5036）
# 出處：《太乙統宗寶鑑》卷九「明陰陽厄會水旱災期術」
_YINYANG_JIU_E = (
    # (序, 名稱, 曆終年, 災類, 災年數, 水旱)
    (1, "一陽九災", 106, "陽九", 9, "旱"),
    (2, "二陰九災", 374, "陰九", 9, "水"),
    (3, "三陽九災", 480, "陽九", 9, "旱"),
    (4, "四陰七災", 720, "陰七", 7, "水"),
    (5, "五陽七災", 720, "陽七", 7, "旱"),
    (6, "六陰五災", 600, "陰五", 5, "水"),
    (7, "七陽五災", 600, "陽五", 5, "旱"),
    (8, "八陰三災", 480, "陰三", 3, "水"),
    (9, "九陽三災", 480, "陽三", 3, "旱"),
)


def yinyang_jiu_e(taiyi_acumyear: int) -> dict:
    """卷九「陰陽九厄水旱災期」：九會災變分期（OCR line 5007-5064）。

    出處：《太乙統宗寶鑑》卷九「明陰陽厄會水旱災期術」。

    陽九一元四千五百六十年中，有九會九厄，積五十七年災。
    五陽主旱、四陰主水。九會而復起元。
    """
    rem = (taiyi_acumyear + 130) % 4560
    cumulative = 0
    current_e = None
    for idx, name, li_zhong, e_type, e_years, water_drought in _YINYANG_JIU_E:
        if rem < li_zhong:
            current_e = (idx, name, li_zhong - rem, e_type, e_years, water_drought)
            break
        cumulative = li_zhong
    if not current_e:
        current_e = (9, "九陽三災", 0, "陽三", 3, "旱")
    idx, name, years_to, e_type, e_years, water_drought = current_e
    at_disaster = years_to <= e_years
    return {
        "陰陽九厄": [
            {"序": i, "名": n, "曆終年": lz, "災類": et, "災年": ey, "水旱": wd}
            for i, n, lz, et, ey, wd in _YINYANG_JIU_E
        ],
        "當前厄會": {
            "序": idx,
            "名": name,
            "距災終": years_to,
            "災類": e_type,
            "災年數": e_years,
            "水旱": water_drought,
        },
        "臨災年": at_disaster,
        "斷語": (
            f"{name}：{water_drought}{e_years}年"
            if at_disaster else
            f"{name}，距災終{years_to}年"
        ),
        "要訣": "九會九厄，五陽主旱、四陰主水；總合四千六百十七策起元",
    }


# 卷九「明陽九百六十大遊行限觀歷數」（OCR line 5179-5246）
# 出處：《太乙統宗寶鑑》卷九

# 十六神序（卷九行限用）
_SIXTEEN_SEQ = list("子丑艮寅卯辰巽巳午未坤申酉戌乾亥")

# 厄會四神：太陽(天罡)、陰主(天魁)、地主、武德、大義、太簇
# 即位年支加大義，視太陽/陰主所臨為厄會之期
# 大義＝天心，太陽＝天罡，陰主＝天魁

_EHUI_SISHEN_DUAN = {
    "太陽": "紀律隳廢，兵刀厄會",
    "陰主": "奸臣逆謀，凶喪禍亂",
    "地主": "禮義廢失，口舌謠言",
    "武德": "迂徙易地，叛營宮室",
    "大義": "毀折廢散，年叛立之事",
    "太簇": "國政法令變更，風俗轉移，服色鼎新",
}


def ehui_xingxian(year_zhi: str, enzhi: str | None = None) -> dict:
    """卷九「陽九百六行限觀歷數」：即位年支加大義，視太陽陰主所臨為厄會之期。

    出處：《太乙統宗寶鑑》卷九（OCR line 5198-5246）。

    法曰：以即位年干支加大義，取太陽陰主下為厄會。
    從即位年上起數，視陰陽逆順而行，以知位終之限。
    大義者天心也，太陽者天罡也，陰主者天魁也。
    """
    if not year_zhi or year_zhi not in _SIXTEEN_SEQ:
        return {"斷語": "即位年支未明", "要訣": "以即位年支加大義，視太陽陰主所臨"}
    # 大義在亥（固定）
    dayi_chen = "亥"
    # 以即位年支為起點，加「大義」到該支
    # 即：以大義加年支，視年支上神
    idx_year = _SIXTEEN_SEQ.index(year_zhi)
    idx_dayi = _SIXTEEN_SEQ.index(dayi_chen)
    offset = (idx_dayi - idx_year) % 16
    # 太陽（天罡）＝太乙所在之辰，此處以年支推算
    # 陰主（天魁）＝太陽對宮
    taiyang_idx = (idx_year + offset) % 16
    taiyang_chen = _SIXTEEN_SEQ[taiyang_idx]
    # 陰主＝太陽對宮（隔8位）
    yinzhu_idx = (taiyang_idx + 8) % 16
    yinzhu_chen = _SIXTEEN_SEQ[yinzhu_idx]

    # 推算即位年至厄會之期：從即位年起逆行至太陰/陰主所臨
    steps_to_taiyang = (taiyang_idx - idx_year) % 16 or 16
    steps_to_yinzhu = (yinzhu_idx - idx_year) % 16 or 16

    # 即位年干支（如果提供）
    enzhi_note = ""
    if enzhi:
        enzhi_note = f"即位年{enzhi}，"

    return {
        "即位年支": year_zhi,
        "大義": dayi_chen,
        "太陽(天罡)": taiyang_chen,
        "陰主(天魁)": yinzhu_chen,
        "距太陽": steps_to_taiyang,
        "距陰主": steps_to_yinzhu,
        "厄會四神": {k: v for k, v in _EHUI_SISHEN_DUAN.items()},
        "斷語": (
            f"{enzhi_note}太陽臨{taiyang_chen}主紀律隳廢兵刀厄會，"
            f"陰主臨{yinzhu_chen}主奸臣逆謀凶喪禍亂；"
            f"距太陽{steps_to_taiyang}年，距陰主{steps_to_yinzhu}年"
        ),
        "要訣": "帝王受命所稟自天，以即位年支加大義視太陽陰主所臨為厄會之期",
    }


def guozheng_bianyi(year_zhi: str) -> dict:
    """卷九「明國政章易法令變更術」：以呂申加即位年，視太簇等六神所臨。

    出處：《太乙統宗寶鑑》卷九（OCR line 5247-5261）。

    以呂申加即位創業立法之年，視太簇所臨之下為國政章易法令變更、
    風俗轉移、服色鼎新。太陽所臨之下紀律隳廢兵刀厄會；
    陰主所臨之下奸臣逆謀凶喪禍亂；地主所臨之下禮義廢失口舌謠言；
    武德所臨之下迂徙易地叛營宮室；大義所臨之下毀折廢散年叛立之事。
    """
    if not year_zhi or year_zhi not in _SIXTEEN_SEQ:
        return {"斷語": "即位年支未明"}
    # 呂申在寅（固定）
    lvshen_chen = "寅"
    idx_year = _SIXTEEN_SEQ.index(year_zhi)
    idx_lvshen = _SIXTEEN_SEQ.index(lvshen_chen)
    offset = (idx_lvshen - idx_year) % 16

    # 六神所臨：以呂申加年支，年支上神為基準
    # 各神在十六神序中的固定位置
    _GOD_CHEN = {
        "太簇": "酉", "太陽": "巳", "陰主": "戌",
        "地主": "子", "武德": "申", "大義": "亥",
    }
    six_gods = {}
    for god, chen in _GOD_CHEN.items():
        idx_god = _SIXTEEN_SEQ.index(chen)
        landing_idx = (idx_year + (idx_god - idx_lvshen)) % 16
        six_gods[god] = {
            "臨辰": _SIXTEEN_SEQ[landing_idx],
            "所主": _EHUI_SISHEN_DUAN.get(god, ""),
        }

    return {
        "即位年支": year_zhi,
        "呂申": lvshen_chen,
        "六神所臨": six_gods,
        "斷語": "；".join(f"{g}臨{v['臨辰']}：{v['所主']}" for g, v in six_gods.items()),
        "要訣": "筭和筭長之年遠在九十或一百九十，筭短不和之年近在九年或十八年",
    }


def suizhong_zaifa(year_zhi: str, hegod_zhi: str, skyeyes_chen: str) -> dict:
    """卷九「明歲中災發月日之期術」：以太歲合神加歲支，視文昌天目所臨為災發之月。

    出處：《太乙統宗寶鑑》卷九（OCR line 5263-5278）。

    法曰：以太歲合神命加歲支，視文昌天目所臨之下，而為災發之月也。
    衝處亦然。如文昌臨辰，三月見災；九月亦然。
    文昌在陽宮主歲旱，在陰宮主歲水。
    """
    if not year_zhi or year_zhi not in _SIXTEEN_SEQ:
        return {"斷語": "歲支未明"}
    if not hegod_zhi or hegod_zhi not in _SIXTEEN_SEQ:
        return {"斷語": "合神未明"}
    if not skyeyes_chen or skyeyes_chen not in _SIXTEEN_SEQ:
        return {"斷語": "文昌天目未明"}

    # 以合神加歲支：合神臨歲支，視文昌天目所臨
    idx_year = _SIXTEEN_SEQ.index(year_zhi)
    idx_hegod = _SIXTEEN_SEQ.index(hegod_zhi)
    idx_wenchang = _SIXTEEN_SEQ.index(skyeyes_chen)
    # 合神加歲支 → 歲支上神 = 合神位置
    # 文昌天目所臨之辰 = 文昌所在
    # 災月 = 文昌所臨之辰對應的月份
    offset = (idx_wenchang - idx_hegod) % 16
    zai_chen = _SIXTEEN_SEQ[(idx_year + offset) % 16]

    # 十六神→月份對照（子=十一月，丑=十二月，寅=正月...）
    _CHEN_MONTH = {
        "子": 11, "丑": 12, "寅": 1, "卯": 2, "辰": 3, "巳": 4,
        "午": 5, "未": 6, "申": 7, "酉": 8, "戌": 9, "亥": 10,
    }
    zai_month = _CHEN_MONTH.get(zai_chen)
    # 衝處
    chong_idx = (idx_wenchang + 8) % 16
    chong_chen = _SIXTEEN_SEQ[chong_idx]
    chong_month = _CHEN_MONTH.get(chong_chen)

    # 陽宮主旱、陰宮主水
    _YANG_GONG = {"子", "寅", "辰", "午", "申", "戌", "乾", "艮", "巽"}
    water_drought = "旱" if skyeyes_chen in _YANG_GONG else "水"

    months = []
    if zai_month:
        months.append(f"{zai_month}月（{zai_chen}）")
    if chong_month:
        months.append(f"{chong_month}月（{chong_chen}，衝處）")

    return {
        "歲支": year_zhi,
        "合神": hegod_zhi,
        "文昌天目": skyeyes_chen,
        "災發月": months,
        "水旱": water_drought,
        "斷語": (
            f"文昌臨{zai_chen}，{zai_month}月見災；"
            + (f"衝處{chong_chen}，{chong_month}月亦然；" if chong_month else f"衝處{chong_chen}（四維宮無月份）；")
            + f"文昌在{'陽宮主歲旱' if water_drought == '旱' else '陰宮主歲水'}"
        ),
        "要訣": "陽丑陰未加歲支，即看太陽陰主下，此日災臨禍不移",
    }


def lishu_changduan(taiyi_acumyear: int, enzhi_year: int | None = None) -> dict:
    """卷九「明歷數長短以觀遠近期術」「安居士氏歷數之期」（OCR line 4895-4937）。

    出處：《太乙統宗寶鑑》卷九。

    以大遊入卦年數淺深推帝王曆數遠近：
    - 臨初、二、四、五之爻位，數長
    - 臨三、六之爻位，數短
    - 二為時之正旺，五為時之已過
    - 大遊在內卦曆數應長，外卦曆數應短
    - 內極災輕，外極災重
    """
    dayou_nei = dayou_nei_gua(taiyi_acumyear)
    dayou_wai = dayou_wai_gua(taiyi_acumyear)

    nei_yao = dayou_nei["動爻"]
    wai_yao = dayou_wai.get("動爻", 0)
    nei_years = dayou_nei["入卦年數"]
    wai_years = dayou_wai.get("入卦年數", 0)

    # 內卦：初二四五數長，三六數短
    _LONG_YAO = {1, 2, 4, 5}
    _SHORT_YAO = {3, 6}
    nei_chang = nei_yao in _LONG_YAO
    nei_short = nei_yao in _SHORT_YAO

    # 內極（三爻）災輕，外極（上爻）災重
    nei_ji = nei_yao == 3
    wai_ji = wai_yao == 6

    # 曆數長短
    if dayou_nei["滿宮"] or nei_years >= 30:
        lishu = "長"
    elif nei_ji:
        lishu = "中等（內極災輕）"
    elif nei_short:
        lishu = "短"
    else:
        lishu = "長"

    if wai_ji:
        lishu += "，外極災重"

    # 陰陽得位
    bits = _bits_from_code(_gua_code(dayou_nei["內卦"]))
    yao_yang = bits[nei_yao - 1] if nei_yao <= len(bits) else True

    duan = []
    if nei_chang:
        duan.append(f"大遊臨第{nei_yao}爻，曆數應長")
    if nei_short:
        duan.append(f"大遊臨第{nei_yao}爻，曆數應短")
    if nei_ji:
        duan.append("臨內極三爻，災輕")
    if wai_ji:
        duan.append("臨外極上爻，災重")
    if not duan:
        duan.append(f"大遊入{dayou_nei['內卦']}卦第{nei_yao}爻，入卦{nei_years}年")

    return {
        "大遊內卦": dayou_nei["內卦"],
        "入卦年數": nei_years,
        "動爻": nei_yao,
        "曆數長短": lishu,
        "內極災輕": nei_ji,
        "外極災重": wai_ji,
        "斷語": "；".join(duan),
        "要訣": "大遊在內卦曆數應長，外卦曆數應短；內極災輕，外極災重",
    }


# 卷九「居安之代歷數之期」雲氣占卜法（OCR line 4919-4926）
_YUNQI_COLOR = {
    "黃": {"五行": "土", "數": 5}, "白": {"五行": "金", "數": 9},
    "青": {"五行": "木", "數": 8}, "黑": {"五行": "水", "數": 6}, "紅": {"五行": "火", "數": 7},
}
_GAN_NUM = {"甲": 9, "乙": 8, "丙": 7, "丁": 6, "戊": 5, "己": 4, "庚": 8, "辛": 7, "壬": 6, "癸": 5}
_ZHI_NUM = {"子": 9, "丑": 8, "寅": 7, "卯": 6, "辰": 5, "巳": 4, "午": 9, "未": 8, "申": 7, "酉": 6, "戌": 5, "亥": 4}
_GAN_WUXING = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土", "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}
_WX_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
_WX_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}


def yunqi_zhanbo(yunqi_color: str, day_gan: str, day_zhi: str) -> dict:
    """卷九「居安之代歷數之期」雲氣占卜法（OCR line 4919-4926）。

    出處：《太乙統宗寶鑑》卷九。
    雲氣色數：黃(5/土)、白(9/金)、青(8/木)、黑(6/水)、紅(7/火)
    日干支數：甲己子午九、乙庚丑未八、丙辛寅申七、丁壬卯酉六、戊癸辰戌五、己亥四
    雲生日者多子、雲生辰者多女、雲克日者絕嗣
    陰雲位不久，五色雲綿遠壽昌
    """
    yq = _YUNQI_COLOR.get(yunqi_color)
    if not yq:
        return {"斷語": f"未識雲氣顏色「{yunqi_color}」，當用黃白青黑紅五色之一"}
    yq_wx, yq_num = yq["五行"], yq["數"]
    day_num = _GAN_NUM.get(day_gan, 0) + _ZHI_NUM.get(day_zhi, 0)
    day_wx = _GAN_WUXING.get(day_gan, "")
    sheng_ri = _WX_SHENG.get(yq_wx) == day_wx
    ke_ri = _WX_KE.get(yq_wx) == day_wx
    if sheng_ri:
        duan = "雲生日者多子"
    elif ke_ri:
        duan = "雲克日者絕嗣"
    elif _WX_SHENG.get(day_wx) == yq_wx:
        duan = "雲生辰者多女"
    else:
        duan = "雲與日無生剋，當視旺相休囚"
    return {
        "雲氣": yunqi_color, "雲氣五行": yq_wx, "雲氣數": yq_num,
        "日干": day_gan, "日支": day_zhi, "日干支數": day_num, "斷語": duan,
        "要訣": "雲生日多子、雲生辰多女、雲克日絕嗣；陰雲位不久，五色雲綿遠壽昌",
    }


# 卷二十「明身命諸宮位居空無臨焰所主術」（OCR line 19934-19956）
# 各宮空亡時的具體斷語
_GONG_KONGWANG = {
    "命宮": "虛華詐偽、閑懶磨跎、欺誑泛浮、恍惚無心、守靜安樂",
    "兄弟宮": "刑害奸慝、兄弟各居、酒友花朋、遊蕩流走、尅剝不義",
    "妻妾宮": "刑剋緣寡、休離奸姤、閒諜教唆、詐冒爭訟、欺隱瞞昧",
    "子孫宮": "六畜傷損",
    "財帛宮": "家計蕭索、財帛失散、賊盜劫掠、走閃拐帶、非橫破敗",
    "田宅宮": "借貸債居、店舍旅邸、荒門草舍、籬斜壁倒、火燒水溺、爭奪廢棄",
    "官祿宮": "狐假虎威、羊質虎皮、停罷宮觀、私通水幹、巧言歇滅、除減遠闕",
    "奴僕宮": "病亡衰敗、姦詐侵欺、出尖惹禍、放逸為非、走閃轉變、無憑無倚",
    "疾厄宮": "虛狂磨難、口腹歪斜、手足跛躃、麻癱龜背、風啞聾痲、患蠱癲六指、唇缺",
    "福德宮": "僧尼道俗醫術遊謁、寒儒蕩士、隱居閑處、逍遙清虛、淡薄浮祿、遊藝岐路、倚貴托富",
    "相貌宮": "談虛說空、形容破陋、肌體尪羸、孤行獨走、多憂多屈",
    "父母宮": "父母傷剋不利、六親過房異姓、拋棄分離、詐冒邪偽、隱匿心不明",
}

# 身宮空亡
_SHENGONG_KONGWANG = "離鄉背井、倚草附木、貼閑補空、狂蕩飄蓬、輕浮怠慢、行止無定、宿食寺觀、湊合修緣傳書度信、歌妓雜劇"

# 四柱空亡
_SIZHU_KONGWANG = {
    "年": "初生無依、祖屋無依、父母刑傷、身不自立、六親間諜多招阻滯",
    "日": "妻傷子損、碌碌區區、成敗進退多憂少樂",
    "時": "鰥寡孤獨、煩惱哀慮、思愁飢飽、勞役風癱、壽無善終",
}


def gong_kongwang_duan(taiyi, sex: str, *, plate_ji: int = 4) -> dict:
    """卷二十「明身命諸宮位居空無臨焰所主術」（OCR line 19934-19956）。

    出處：《太乙統宗寶鑑》卷二十。

    各宮空亡時的具體斷語——命宮空、兄弟空、妻妾空…各有不同災象。
    身宮空主離鄉背井；年日時空各有不同。
    """
    palaces = taiyi.gongs_discription_list(sex, plate_ji)
    palace_map = taiyi._twelve_palace_map(sex)
    result = {}
    for palace, tokens in palaces.items():
        lookup_key = palace if palace.endswith("宮") else palace + "宮"
        kong = _GONG_KONGWANG.get(lookup_key) or _GONG_KONGWANG.get(palace)
        if not kong:
            continue
        is_empty = not tokens or tokens == ["空格"]
        result[palace] = {
            "空亡": is_empty,
            "斷語": kong if is_empty else "有星曜，不論空亡",
        }

    # 身宮
    from .shiti_jinfu import _life_core  # noqa: PLC0415
    shen_zhi = _life_core(taiyi, sex)["安身宮"]
    shen_palace = palace_map.get(shen_zhi, "")
    shen_tokens = palaces.get(shen_palace, [])
    shen_empty = not shen_tokens or shen_tokens == ["空格"]

    # 四柱
    gz = config.gangzhi(taiyi.year, taiyi.month, taiyi.day, taiyi.hour, taiyi.minute)
    # 年柱空亡：以命盤星曜判斷，此處簡化
    return {
        "十二宮空亡": result,
        "身宮空亡": {
            "空亡": shen_empty,
            "斷語": _SHENGONG_KONGWANG if shen_empty else "身宮有星，不論空亡",
        },
        "四柱空亡": {k: v for k, v in _SIZHU_KONGWANG.items()},
        "要訣": "空亡宮位以對宮星曜補論；年空初生無依、日空妻傷子損、時空鰥寡孤獨",
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


def ce_reference_table() -> list[dict]:
    """四象之策立成（卷九）。"""
    return [
        {"八卦": gua, "四象": ce, "策數": num}
        for gua, (ce, num) in _CE_CE.items()
    ]


def zonghe(taiyi_acumyear: int, year: int | None = None,
                month: int = 1, day: int = 15) -> dict:
    """卷九綜合：大小遊軌運、重卦策數、陽九百六限數。"""
    nei_dy = dayou_nei_gua(taiyi_acumyear)
    wai_dy = dayou_wai_gua(taiyi_acumyear)
    nei_xy = xiaoyou_nei_gua(taiyi_acumyear)
    wai_xy = xiaoyou_wai_gua(taiyi_acumyear)
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
        "大遊內卦": nei_dy,
        "大遊外卦": wai_dy,
        "小遊內卦": nei_xy,
        "小遊外卦": wai_xy,
        "四象之策": ce_reference_table(),
        "大遊落宮": config.num2gong(palace_big) if palace_big else "",
        "小遊落宮": config.num2gong(palace_small) if palace_small else "",
        "大遊入宮年數": config.bigyo_years_in(taiyi_acumyear),
        "行宮卦異": dayou["內卦"] != xiaoyou["內卦"],
        "陽九限數": yj,
        "百六限數": bl,
        "陰陽九厄": yinyang_jiu_e(taiyi_acumyear),
        "曆數長短": lishu_changduan(taiyi_acumyear, year),
        "小遊行爻災祥": xy_zai,
        **extra,
        "要訣": (
            f"大遊{dayou['重卦']}{dayou['內爻名']}（內策{dayou['內策']}+外策{dayou['外策']}="
            f"{dayou['總策']}），"
            f"小遊{xiaoyou['重卦']}{xiaoyou['內爻名']}（總策{xiaoyou['總策']}）；"
            f"陽九入限{yj['入限年數']}年，百六入限{bl['入限年數']}年"
        ),
    }