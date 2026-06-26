# 《太乙統宗寶鑑》卷二十：太乙命法（飛祿飛馬、三合十干合、旺衰絕空刑、奇耦三才、照限游年、行月日行卦）

from __future__ import annotations

from datetime import date
import datetime as _dt

from . import config
from . import taiyi_life_dict
from .mingfa_songs import (
    SAN_XIAN_DUAN,
    STAR_WANG_ZHI,
    classify_san_xian_ji_xiong,
    match_zhao_you_songs,
)
from .tongyun_extras import _bits_from_code, _flip_yao, _gua_code

_DI_ZHI = list(config.di_zhi)
_TWELVE_PALACES = "命宮,兄弟,妻妾,子孫,財帛,田宅,官祿,奴僕,疾厄,福德,相貌,父母".split(",")
_OPPOSITE = dict(zip(_DI_ZHI, _DI_ZHI[6:] + _DI_ZHI[:6]))

_SANHE = {
    "木": {"支": ("亥", "卯", "未"), "順": "木星", "絕": "金", "殺": "金", "弱": "水"},
    "火": {"支": ("寅", "午", "戌"), "順": "火星", "絕": "水", "殺": "水", "弱": "木"},
    "金": {"支": ("巳", "酉", "丑"), "順": "金星", "絕": "火", "殺": "火", "弱": "土"},
    "水": {"支": ("申", "子", "辰"), "順": "水星", "絕": "木", "殺": "土", "弱": "金"},
}

_SHIGAN_HE = {
    frozenset({"甲", "己"}): ("土星", "火順水戰木剋金弱", "旺相高顯衰敗不信"),
    frozenset({"乙", "庚"}): ("金星", "土順木戰火剋水弱", "旺相剛毅衰敗不義"),
    frozenset({"丙", "辛"}): ("水星", "金順火戰土剋木弱", "旺相秀實衰敗不智"),
    frozenset({"丁", "壬"}): ("木星", "水順土戰金剋火弱", "旺相茂盛衰敗不仁"),
    frozenset({"戊", "癸"}): ("火星", "木順金戰水剋土弱", "旺相炎發衰敗不禮"),
}

_FLY_LU_MA = {
    tuple("甲乙"): (3, "亥", "木"),
    tuple("丙丁"): (2, "寅", "火"),
    tuple("戊己"): (5, "午", "土"),
    tuple("庚辛"): (4, "巳", "金"),
    tuple("壬癸"): (1, "申", "水"),
}

_SHANG_HE = frozenset({14, 18})
_ZHONG_HE = frozenset({23, 29, 32, 36})
_XIA_HE = frozenset({12, 16, 21, 27, 34})
_ZA_CHONG_YANG = frozenset({13, 19, 31, 37})
_ZA_CHONG_YIN = frozenset({24, 28})
_YIN_ZHONG_YANG = frozenset({11, 17})
_CHUN_YANG = frozenset({33, 39})
_CHUN_YIN = frozenset({22, 26})

_YANG_GONG = frozenset({8, 3, 4, 9})
_YIN_GONG = frozenset({1, 2, 6, 7})
_DI_GONG = frozenset({2, 5})
_YIN_DE_GONG = frozenset({1, 6, 7})

_PALACE_STATE_MEAN = {
    "旺": "和安喜高長顯順",
    "衰": "吝厄病傷短退逆",
    "絕": "害災傷無失囚禍",
    "空": "散休死陷損失走",
    "刑": "亂剋拋散喪罪盜",
}

_STAR_PRIORITY = (
    "君基", "臣基", "民基", "五福", "文昌", "計神", "小游",
    "主大", "客大", "主參", "客參", "始擊", "飛符", "四神", "天乙", "地乙",
)

_YINGCHA = 2
_YANG_ZHI = frozenset("子寅辰午申戌")
_YANG_BRANCHES = "子寅辰午申戌"
_YIN_BRANCHES = "丑卯巳未酉亥"


def _gua_name(num: int) -> str:
    n = num % 64 or 64
    raw = config.gua.get(n, "")
    if not raw:
        return ""
    return "".join(c for c in raw if not ("\u4dc0" <= c <= "\u4dff"))


def _dong_yao(gua_name: str, seq: int, yang_mode: bool) -> tuple[int, str]:
    bits = _bits_from_code(_gua_code(gua_name))
    pool = [i + 1 for i, b in enumerate(bits) if b == yang_mode]
    if not pool:
        pool = list(range(1, 7))
    yao = pool[(seq - 1) % len(pool)]
    yang = bits[yao - 1]
    names = config._YAO_NAMES_YANG if yang else config._YAO_NAMES_YIN
    return yao, names[yao - 1]


def _fly_config(day_gan: str) -> tuple[int, str, str]:
    for stems, cfg in _FLY_LU_MA.items():
        if day_gan in stems:
            return cfg
    return 3, "亥", "木"


def fly_lu_ma_limits(day_gan: str, sex: str, age: int | None = None) -> dict:
    """飛祿飛馬行限（卷二十）：日干五行生數起長生宮，祿順馬逆，十年一易。"""
    start_age, changsheng, wuxing = _fly_config(day_gan)
    if age is None:
        age = 0
    periods = []
    for p in range(12):
        begin = start_age + p * 10
        end = begin + 9
        lu_zhi = config.new_list(_DI_ZHI, changsheng)[p % 12]
        ma_zhi = config.new_list(list(reversed(_DI_ZHI)), changsheng)[p % 12]
        periods.append({
            "歲數": f"{begin}-{end}",
            "飛祿宮": lu_zhi,
            "飛馬宮": ma_zhi,
        })
    active = None
    if age >= start_age:
        p = min((age - start_age) // 10, 11)
        active = {
            "當前歲": age,
            "飛祿宮": periods[p]["飛祿宮"],
            "飛馬宮": periods[p]["飛馬宮"],
            "期間": periods[p]["歲數"],
        }
    return {
        "日干": day_gan,
        "五行": wuxing,
        "生數": start_age,
        "長生宮": changsheng,
        "起限歲": start_age,
        "行限表": periods,
        "當前": active,
        "要訣": f"{day_gan}屬{wuxing}，生於{changsheng}；祿限順行、馬限逆行，十年一易",
    }


def sanhe_info(branch: str) -> dict:
    """地支三合（卷二十）。"""
    for wx, info in _SANHE.items():
        if branch in info["支"]:
            mates = [z for z in info["支"] if z != branch]
            return {
                "地支": branch,
                "三合": "".join(info["支"]),
                "五行": wx,
                "順行": info["順"],
                "絕生": info["絕"],
                "殺": info["殺"],
                "弱": info["弱"],
                "同局": mates,
            }
    return {"地支": branch, "三合": "—"}


def shigan_he_info(year_gan: str) -> dict:
    """十干合（卷二十，年上取用）。"""
    for pair, (he_wx, relation, duan) in _SHIGAN_HE.items():
        if year_gan in pair:
            other = next(g for g in pair if g != year_gan)
            return {
                "年干": year_gan,
                "合干": other,
                "合化": he_wx,
                "生剋": relation,
                "斷語": duan,
            }
    return {"年干": year_gan, "合干": "—"}


def _star_grade(star: str, zhi: str) -> str:
    grades = taiyi_life_dict.sixteen_three_grades.get(star)
    if not grades:
        return "中"
    for branches, text in grades.items():
        if zhi in branches:
            if "上等" in text:
                return "上"
            if "下等" in text:
                return "下"
            return "中"
    return "中"


def _palace_stars(taiyi, sex: str, *, plate_ji: int = 4) -> dict[str, list[str]]:
    raw = taiyi.gongs_discription_list(sex, plate_ji)
    return {k: (v if v else ["空格"]) for k, v in raw.items()}


def _branch_for_palace(palace_map: dict[str, str], palace: str) -> str | None:
    for br, name in palace_map.items():
        if name == palace:
            return br
    return None


def palace_wangshuai(
    taiyi, sex: str, *, palace_map: dict | None = None, plate_ji: int = 4,
) -> dict:
    """十二宮旺衰絕空刑（卷二十）：空宮取對宮，合星等第論休咎。"""
    palace_map = palace_map or taiyi._twelve_palace_map(sex)
    stars_by_palace = _palace_stars(taiyi, sex, plate_ji=plate_ji)
    gz = config.gangzhi(taiyi.year, taiyi.month, taiyi.day, taiyi.hour, taiyi.minute)
    year_zhi = gz[0][1]
    sanhe = sanhe_info(year_zhi)
    xing_zhi = set()
    if "支" in sanhe:
        xing_set = set(sanhe.get("同局", ()))
        xing_zhi = xing_set

    out = {}
    for palace in _TWELVE_PALACES:
        br = _branch_for_palace(palace_map, palace)
        stars = stars_by_palace.get(palace, ["空格"])
        norm = [s for s in stars if s and s != "空格"]
        state = "旺"
        duan = ""
        if not norm:
            opp = _OPPOSITE.get(br, "")
            opp_palace = palace_map.get(opp, "")
            opp_stars = stars_by_palace.get(opp_palace, [])
            opp_norm = [s for s in opp_stars if s and s != "空格"]
            if opp_norm:
                norm = opp_norm
                state = "衰"
                duan = f"本宮空，取對宮{opp}（{opp_palace}）星論"
            else:
                state = "空"
                duan = taiyi_life_dict.twelve_gong_stars.get(palace, {}).get("空格", "虛花無依")
        if state != "空":
            if br in xing_zhi:
                state = "刑"
            best = None
            for name in _STAR_PRIORITY:
                if any(name in s for s in norm):
                    best = name
                    break
            if best and br:
                grade = _star_grade(best, br)
                state = {"上": "旺", "中": "衰", "下": "絕"}.get(grade, "衰")
                song = taiyi_life_dict.stars_twelve.get(best, [])
                zhi_idx = _DI_ZHI.index(br) if br in _DI_ZHI else 0
                if zhi_idx < len(song):
                    duan = song[zhi_idx][:48]
        out[palace] = {
            "地支": br,
            "星曜": norm or ["空格"],
            "狀態": state,
            "所主": _PALACE_STATE_MEAN.get(state, ""),
            "斷語": duan,
        }
    return out


def qi_ou_he_analysis(taiyi, *, plate_ji: int = 4) -> dict:
    """奇耦上中下筭和、雜重陽陰、純陽陰（卷二十，以定算為和數）。"""
    ty_g = taiyi.ty_gong(plate_ji, 0)
    wc_g = config.gong2.get(taiyi.skyeyes(plate_ji, 0).replace("中", "辰"), 5)
    ding = taiyi.set_cal(plate_ji, 0)
    ty_yang = ty_g in _YANG_GONG
    label = "不和"
    if ty_yang and ding % 2 == 0:
        label = "陽宮得耦"
    elif not ty_yang and ding % 2 != 0:
        label = "陰宮得奇"
    he_type = "不和"
    if ding in _SHANG_HE:
        he_type = "上和"
    elif ding in _ZHONG_HE:
        he_type = "中和"
    elif ding in _XIA_HE:
        he_type = "下和"
    special = None
    if ding in _ZA_CHONG_YANG and wc_g in _DI_GONG:
        special = "雜重陽"
    elif ding in _ZA_CHONG_YIN and wc_g in _YIN_DE_GONG:
        special = "雜重陰"
    elif ding in _YIN_ZHONG_YANG and wc_g in _YIN_DE_GONG:
        special = "陰中重陽"
    elif ding in _CHUN_YANG and wc_g in _DI_GONG:
        special = "純陽"
    elif ding in _CHUN_YIN and wc_g in _YIN_DE_GONG:
        special = "純陰"
    return {
        "定算": ding,
        "太乙宮": config.num2gong(ty_g),
        "文昌宮": config.num2gong(wc_g),
        "陰陽相配": label,
        "和數類型": he_type,
        "特殊數": special,
        "要訣": (
            f"定算{ding}為{he_type}"
            + (f"，{special}" if special else "")
            + f"；{label}"
        ),
    }


def _calc_sancai_flags(val: int) -> list[str]:
    s = str(abs(int(val)))
    digits = set(s)
    flags = []
    if val < 10:
        flags.append("無天")
    if "5" not in digits:
        flags.append("無地")
    if not digits & {"2", "3", "4"}:
        flags.append("無人")
    return flags


def san_cai_wu_suan(taiyi, *, plate_ji: int = 4) -> dict:
    """三才無筭（卷二十）：主客定算缺天十、地五、人二三四。"""
    home = taiyi.home_cal(plate_ji, 0)
    away = taiyi.away_cal(plate_ji, 0)
    ding = taiyi.set_cal(plate_ji, 0)
    parts = {}
    all_flags = []
    for name, val in (("主算", home), ("客算", away), ("定算", ding)):
        flags = _calc_sancai_flags(val)
        parts[name] = {"數": val, "缺失": flags or ["俱全"]}
        all_flags.extend(flags)
    triple_none = all(
        _calc_sancai_flags(v) == ["無天", "無地", "無人"]
        for v in (home, away, ding)
    )
    return {
        "三才": parts,
        "三才俱無": triple_none,
        "要訣": (
            "三才俱無，災禍尤重，宜修德禳之"
            if triple_none
            else "；".join(
                f"{k}缺{''.join(v['缺失'])}" for k, v in parts.items() if v["缺失"] != ["俱全"]
            ) or "三才俱全"
        ),
    }


def life_geju(taiyi, *, plate_ji: int = 4) -> dict:
    """命盤格局（卷二十掩迫關囚擊格對）。"""
    return taiyi.shi_geju(plate_ji, 0)


def bailiu_month_gua(taiyi, month: int | None = None) -> dict:
    """百六行月卦（卷二十）。"""
    month = month if month is not None else config.lunar_date_d(
        taiyi.year, taiyi.month, taiyi.day,
    ).get("月", taiyi.month)
    if isinstance(month, str):
        month = {"正": 1, "一": 1, "十二": 12}.get(month, taiyi.month)
    year_num = taiyi.year_gua()[0]
    base = year_num + _YINGCHA
    num = base + int(month)
    gua = _gua_name(num)
    yang_month = int(month) % 2 == 1
    yao, yao_name = _dong_yao(gua, num, yang_month)
    return {
        "流年卦數": year_num,
        "月序": month,
        "卦數": num,
        "卦": gua,
        "動爻": yao,
        "爻名": yao_name,
        "要訣": f"流年卦加盈差{_YINGCHA}，逐月累加得{gua}{yao_name}",
    }


def bailiu_day_gua(taiyi, day_gz: str | None = None, month: int | None = None) -> dict:
    """百六行日卦（卷二十）。"""
    mg = bailiu_month_gua(taiyi, month)
    gz = day_gz or config.gangzhi(taiyi.year, taiyi.month, taiyi.day, taiyi.hour, taiyi.minute)[2]
    jiazi_idx = dict(zip(config.jiazi(), range(1, 61))).get(gz, 1)
    num = mg["卦數"] + jiazi_idx
    gua = _gua_name(num)
    yang_day = gz[0] in "甲丙戊庚壬"
    yao, yao_name = _dong_yao(gua, num, yang_day)
    return {
        "月卦": mg["卦"],
        "日干支": gz,
        "卦數": num,
        "卦": gua,
        "動爻": yao,
        "爻名": yao_name,
        "要訣": f"月卦數加甲子序{jiazi_idx}得{gua}{yao_name}",
    }


def _extract_star_names(star_tokens: list[str]) -> set[str]:
    names = (
        "主參", "客參", "主大", "客大", "始擊", "文昌", "計神", "小游",
        "君基", "臣基", "民基", "五福", "飛符", "四神", "天乙", "地乙",
    )
    blob = "".join(star_tokens)
    return {n for n in names if n in blob}


def _age_limit_branch(taiyi, sex: str, age: int, *, kind: str | None = None) -> tuple[str, str]:
    age = max(age, 1)
    tables = []
    if kind in (None, "陽九"):
        tables.append(("陽九", taiyi.yangjiu_xingxian(sex)))
    if kind in (None, "百六"):
        tables.append(("百六", taiyi.bailiu_xingxian(sex)))
    for label, table in tables:
        for rng, zhi in table.items():
            lo, hi = (int(x) for x in rng.split("-"))
            if lo <= age <= hi:
                return label, zhi
    return "—", "—"


def _shouqi_zhi(taiyi) -> str:
    return taiyi.shouqi_ganzhi()[1]


def _shouqi_ganzhi(taiyi) -> str:
    return taiyi.shouqi_ganzhi()


def _zhishi_yao_from_qi(qi_zhi: str) -> int:
    """直事爻：命起子丑寅卯辰巳，六支一週（卷二十）。"""
    return _DI_ZHI.index(qi_zhi) % 6 + 1


def _liunian_yao_from_bl(gua_name: str, bl_zhi: str) -> tuple[int, str]:
    """流年直事爻：視百六限所到宮辰，陽用陽爻、陰用陰爻（卷二十）。"""
    if bl_zhi not in _DI_ZHI:
        return 1, "初九"
    bits = _bits_from_code(_gua_code(gua_name))
    yang_mode = bl_zhi in _YANG_ZHI
    pool = [i + 1 for i, b in enumerate(bits) if b == yang_mode]
    if not pool:
        pool = list(range(1, 7))
    branches = _YANG_BRANCHES if yang_mode else _YIN_BRANCHES
    idx = branches.index(bl_zhi) if bl_zhi in branches else _DI_ZHI.index(bl_zhi)
    yao = pool[idx % len(pool)]
    yao_name = (config._YAO_NAMES_YANG if bits[yao - 1] else config._YAO_NAMES_YIN)[yao - 1]
    return yao, yao_name


def _bian_gua(gua_name: str, yao: int) -> str:
    code = _flip_yao(_gua_code(gua_name), yao)
    return config.multi_key_dict_get(config.sixtyfourgua, code) or gua_name


def _gua_yao_schedule(gua_name: str, start_yao: int = 1, start_age: int = 1) -> tuple[list[dict], int]:
    bits = _bits_from_code(_gua_code(gua_name))
    order = list(range(1, 7))
    idx = order.index(start_yao)
    order = order[idx:] + order[:idx]
    schedule: list[dict] = []
    age = start_age
    for yao in order:
        yang = bits[yao - 1]
        dur = 9 if yang else 6
        yao_name = (config._YAO_NAMES_YANG if yang else config._YAO_NAMES_YIN)[yao - 1]
        schedule.append({
            "爻": yao,
            "爻名": yao_name,
            "歲數": f"{age}-{age + dur - 1}",
            "年限": dur,
            "陽爻": yang,
        })
        age += dur
    return schedule, age - 1


def _schedule_at_age(schedule: list[dict], age: int) -> dict | None:
    for seg in schedule:
        lo, hi = (int(x) for x in seg["歲數"].split("-"))
        if lo <= age <= hi:
            seg = dict(seg)
            seg["限內第幾年"] = age - lo + 1
            return seg
    return None


def _year_gua_at_age(taiyi, age: int) -> tuple[int, str]:
    base = taiyi.life_start_gua()[0]
    num = base + age
    if num > 64:
        num = num % 64 or 64
    return num, _gua_name(num)


def bailiu_rugua_xian(taiyi, sex: str, age: int | None = None) -> dict:
    """百六入卦限、流年卦限（卷二十）。"""
    if age is None:
        age = config.calculateAge(_dt.date(taiyi.year, taiyi.month, taiyi.day) if taiyi.year >= 1 else _dt.date(1, 1, 1))
    birth_num, _ = taiyi.life_start_gua()
    birth_gua = _gua_name(birth_num)
    qi_gz = _shouqi_ganzhi(taiyi)
    qi_zhi = qi_gz[1]
    zhishi = _zhishi_yao_from_qi(qi_zhi)
    chushen_sched, chushen_end = _gua_yao_schedule(birth_gua, zhishi, 1)
    liunian_num, liunian_gua = _year_gua_at_age(taiyi, age)
    _, bl_zhi = _age_limit_branch(taiyi, sex, age, kind="百六")
    ln_yao, ln_yao_name = _liunian_yao_from_bl(liunian_gua, bl_zhi)
    current = _schedule_at_age(chushen_sched, age)
    phase = "出身卦限"
    active_gua = birth_gua
    active_sched = chushen_sched
    liye_gua = None
    liye_sched = None
    if age > chushen_end:
        phase = "立業卦限"
        liye_gua = _bian_gua(birth_gua, zhishi)
        liye_sched, _ = _gua_yao_schedule(liye_gua, zhishi, chushen_end + 1)
        active_gua = liye_gua
        active_sched = liye_sched
        current = _schedule_at_age(liye_sched, age)
    return {
        "出身卦": {
            "卦數": birth_num,
            "卦": birth_gua,
            "受氣": qi_gz,
            "直事爻": zhishi,
            "行限表": chushen_sched,
        },
        "立業卦": (
            {"卦": liye_gua, "行限表": liye_sched}
            if liye_gua
            else None
        ),
        "當前卦限": {
            "階段": phase,
            "卦": active_gua,
            "當前爻": current,
        },
        "流年卦限": {
            "歲": age,
            "卦數": liunian_num,
            "卦": liunian_gua,
            "動爻": ln_yao,
            "爻名": ln_yao_name,
            "百六限支": bl_zhi,
        },
        "要訣": (
            f"出身{birth_gua}，"
            f"{'立業' + liye_gua + '，' if liye_gua else ''}"
            f"{age}歲流年{liunian_gua}{ln_yao_name}"
        ),
    }


def yangjiu_san_xian(
    taiyi, sex: str, age: int | None = None, *, plate_ji: int = 4,
) -> dict:
    """陽九入三限所主災祥（卷二十：初1-25、中26-50、末51-75）。"""
    if age is None:
        age = config.calculateAge(_dt.date(taiyi.year, taiyi.month, taiyi.day) if taiyi.year >= 1 else _dt.date(1, 1, 1))
    period = "初限" if age <= 25 else "中限" if age <= 50 else "末限"
    _, yj_zhi = _age_limit_branch(taiyi, sex, age, kind="陽九")
    stars = _stars_at_branch(taiyi, yj_zhi, plate_ji=plate_ji)
    star_names = _extract_star_names(stars)
    ji_xiong = classify_san_xian_ji_xiong(star_names)
    duan = SAN_XIAN_DUAN[period].get(
        ji_xiong,
        f"陽九入{period}，星曜平穩，無大吉凶。",
    )
    return {
        "當前歲": age,
        "三限": period,
        "陽九限支": yj_zhi,
        "星曜": stars,
        "吉凶": ji_xiong,
        "斷語": duan,
        "要訣": f"{period}遇陽九在{yj_zhi}，{ji_xiong}",
    }


def star_wangxian_lun(taiyi, sex: str, *, plate_ji: int = 4) -> dict:
    """諸星旺陷獨處同宮論歌（卷二十）。"""
    palace_map = taiyi._twelve_palace_map(sex)
    raw = taiyi.gongs_discription_list(sex, plate_ji)
    dugu: list[dict] = []
    tonggong: list[dict] = []
    twostars = taiyi_life_dict.twostars
    for palace in _TWELVE_PALACES:
        br = _branch_for_palace(palace_map, palace)
        tokens = raw.get(palace, ["空格"])
        norm = [t for t in tokens if t and t != "空格"]
        if len(norm) == 1:
            names = _extract_star_names(norm)
            if names and br:
                star = next(iter(names))
                grade = _star_grade(star, br)
                zhi_idx = _DI_ZHI.index(br) if br in _DI_ZHI else 0
                songs = taiyi_life_dict.stars_twelve.get(star, [])
                song = songs[zhi_idx] if zhi_idx < len(songs) else ""
                wang = "旺" if br in STAR_WANG_ZHI.get(star, ()) else "平"
                dugu.append({
                    "宮": palace,
                    "地支": br,
                    "星": star,
                    "等第": grade,
                    "旺陷": wang,
                    "論歌": song,
                })
        if len(norm) >= 2:
            val_set = set("".join(norm))
            for key, text in twostars.items():
                if set(key) <= val_set:
                    tonggong.append({
                        "宮": palace,
                        "地支": br,
                        "星組": key,
                        "論歌": text,
                    })
    return {
        "獨處諸星": dugu,
        "同宮論歌": tonggong,
        "要訣": (
            f"獨處{len(dugu)}處，同宮{len(tonggong)}組"
            + (f"；{dugu[0]['星']}獨處{dugu[0]['旺陷']}" if dugu else "")
        ),
    }


def _stars_at_branch(taiyi, zhi: str, *, plate_ji: int = 4) -> list[str]:
    sixteen = taiyi.sixteen_gong11(plate_ji, 0)
    raw = sixteen.get(zhi, [])
    return [s for s in raw if s]


def zhao_xian_you_nian(
    taiyi, sex: str, age: int | None = None, query_year: int | None = None, *,
    plate_ji: int = 4,
) -> dict:
    """諸星照限游年歌（卷二十全文匹配）。"""
    if age is None:
        age = config.calculateAge(_dt.date(taiyi.year, taiyi.month, taiyi.day) if taiyi.year >= 1 else _dt.date(1, 1, 1))
    query_year = query_year or date.today().year
    limit_type, zhao_zhi = _age_limit_branch(taiyi, sex, age)
    you_zhi = config.gangzhi(query_year, 6, 15, 12, 0)[0][1]
    zhao_stars = _stars_at_branch(taiyi, zhao_zhi, plate_ji=plate_ji)
    you_stars = _stars_at_branch(taiyi, you_zhi, plate_ji=plate_ji)
    hits = match_zhao_you_songs(zhao_stars, you_stars, zhao_zhi, you_zhi)
    if not hits:
        for star in _STAR_PRIORITY:
            in_z = any(star in s for s in zhao_stars)
            in_y = any(star in s for s in you_stars)
            if in_z or in_y:
                hits.append({"星": star, "照限": in_z, "游年": in_y, "歌訣": f"{star}臨照限游年，宜審旺陷消息。"})
                break
    return {
        "當前歲": age,
        "照限": {"類型": limit_type, "地支": zhao_zhi, "星曜": zhao_stars},
        "游年": {"年份": query_year, "地支": you_zhi, "星曜": you_stars},
        "星歌": hits,
        "要訣": (
            f"{limit_type}限在{zhao_zhi}，{query_year}游年{you_zhi}；"
            f"{hits[0]['歌訣'][:36]}…" if hits else "照限游年星稀，宜再審大限"
        ),
    }


def zonghe(
    taiyi, sex: str, *, age: int | None = None, query_year: int | None = None,
    plate_ji: int = 4,
) -> dict:
    """卷二十命法綜合。"""
    age = _default_life_age(taiyi, age)
    gz = config.gangzhi(taiyi.year, taiyi.month, taiyi.day, taiyi.hour, taiyi.minute)
    day_gan, year_gan = gz[2][0], gz[0][0]
    palace_map = taiyi._twelve_palace_map(sex)
    fly = fly_lu_ma_limits(day_gan, sex, age)
    wang = palace_wangshuai(taiyi, sex, palace_map=palace_map, plate_ji=plate_ji)
    qi_ou = qi_ou_he_analysis(taiyi, plate_ji=plate_ji)
    month_gua = bailiu_month_gua(taiyi)
    return {
        "飛祿飛馬": fly,
        "年支三合": sanhe_info(gz[0][1]),
        "命宮三合": sanhe_info(next(iter(palace_map))),
        "十干合": shigan_he_info(year_gan),
        "十二宮旺衰絕空刑": wang,
        "奇耦上和": qi_ou,
        "三才無筭": san_cai_wu_suan(taiyi, plate_ji=plate_ji),
        "命盤格局": life_geju(taiyi, plate_ji=plate_ji),
        "百六行月卦": month_gua,
        "百六行日卦": bailiu_day_gua(taiyi),
        "百六入卦限": bailiu_rugua_xian(taiyi, sex, age),
        "陽九入三限": yangjiu_san_xian(taiyi, sex, age, plate_ji=plate_ji),
        "旺陷獨處同宮論": star_wangxian_lun(taiyi, sex, plate_ji=plate_ji),
        "照限游年": zhao_xian_you_nian(taiyi, sex, age, query_year, plate_ji=plate_ji),
        "要訣": (
            f"飛祿{(fly.get('當前') or {}).get('飛祿宮', '未起限')}飛馬{(fly.get('當前') or {}).get('飛馬宮', '未起限')}；"
            f"{qi_ou['和數類型']}；"
            f"月卦{month_gua['卦']}"
        ),
    }


_CHART_LIFE_BRANCHES = tuple(_DI_ZHI[5:] + _DI_ZHI[:5])  # 巳午未申酉戌亥子丑寅卯辰


def _default_life_age(taiyi, age: int | None = None) -> int:
    if age is not None:
        return int(age)
    today = date.today()
    years = today.year - taiyi.year
    if (today.month, today.day) < (taiyi.month, taiyi.day):
        years -= 1
    return max(years, 0)


def _sanhe_branch_set(*blocks: dict | None) -> set[str]:
    found: set[str] = set()
    for block in blocks:
        if not block:
            continue
        tri = block.get("三合", "")
        if not tri or tri == "—":
            continue
        for ch in tri:
            if ch in _DI_ZHI:
                found.add(ch)
    return found


def life_chart_annotations(
    taiyi,
    sex: str,
    *,
    age: int | None = None,
    plate_ji: int = 4,
) -> dict:
    """命盤扇區／SVG 用卷二十標記（祿馬合、旺衰絕空刑）。"""
    vol20 = zonghe(
        taiyi,
        sex,
        age=_default_life_age(taiyi, age),
        plate_ji=plate_ji,
    )
    fly = vol20.get("飛祿飛馬") or {}
    cur = fly.get("當前") or {}
    lu = cur.get("飛祿宮")
    ma = cur.get("飛馬宮")
    ming_san = vol20.get("命宮三合") or {}
    nian_san = vol20.get("年支三合") or {}
    she = vol20.get("十干合") or {}
    san_set = _sanhe_branch_set(ming_san, nian_san)
    palace_map = taiyi._twelve_palace_map(sex)
    wang = vol20.get("十二宮旺衰絕空刑") or {}

    branch_tags: dict[str, str] = {}
    branch_states: dict[str, str] = {}
    for br in _CHART_LIFE_BRANCHES:
        tags: list[str] = []
        if lu and br == lu:
            tags.append("祿")
        if ma and br == ma:
            tags.append("馬")
        if br in san_set:
            tags.append("合")
        palace = palace_map.get(br, "")
        state = (wang.get(palace) or {}).get("狀態", "")
        if state:
            branch_states[br] = state
            tags.append(state)
        if tags:
            branch_tags[br] = "".join(tags)

    center_lines: list[str] = []
    if lu or ma:
        period = f"（{cur['期間']}）" if cur.get("期間") else ""
        center_lines.append(f"祿{lu or '—'}馬{ma or '—'}{period}")

    return {
        "卷二十": vol20,
        "branch_tags": branch_tags,
        "branch_states": branch_states,
        "center_lines": center_lines,
        "飛祿宮": lu,
        "飛馬宮": ma,
        "三合地支": sorted(san_set),
        "十干合": she,
    }