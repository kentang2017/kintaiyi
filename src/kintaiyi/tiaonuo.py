# -*- coding: utf-8 -*-
"""
朓胸定數 (Tiao-Nuo Dingshu) — 入轉中心差補正

根據《太乙統宗寶鑑》卷一立成表（損益率 + 朓胸積）計算月亮近點月的中心差。

入轉來源兩種：
1. 天文近似：以 Meeus 月球平近點角 (mean anomaly) 映射至 1～28 日立成表
2. 古典路徑：若有朔積分，可走 calc_ru_li（保留介面）
"""
from __future__ import annotations

from typing import NamedTuple, Tuple, Dict, Any, Optional
from array import array


class TiaoNuoEntry(NamedTuple):
    gain_loss: int          # 損益率（正=益，負=損）
    tiao_nu: int            # 朓胸積（正=朓，負=胸）
    is_special: bool = False
    chu_shu: int = 0        # 初數（特殊日）
    mo_shu: int = 0         # 末數
    chu_lv: int = 0         # 初率
    mo_lv: int = 0          # 末率


# 日法（卷一常用一萬〇五百）
RI_FA = 10500

# ------------------------------------------------------------------
# 完整 1～28 日立成表（《太乙統宗寶鑑》卷一）
# 特殊日（7、14、21、28）填入初數／末數／初率／末率
# ------------------------------------------------------------------
TIAO_NUO_TABLE: Tuple[TiaoNuoEntry, ...] = (
    TiaoNuoEntry(0, 0),  # index 0 unused

    # 初一日
    TiaoNuoEntry(30, 0),
    # 初二日
    TiaoNuoEntry(904, 1035),
    # 初三日
    TiaoNuoEntry(802, 1982),
    # 初四日
    TiaoNuoEntry(706, 2797),
    # 初五日
    TiaoNuoEntry(408, 3464),
    # 初六日
    TiaoNuoEntry(308, 3952),
    # 初七日（特殊）
    TiaoNuoEntry(88, 4235, True, chu_shu=9332, mo_shu=1168, chu_lv=88, mo_lv=88),
    # 初八日
    TiaoNuoEntry(-102, 4363),
    # 初九日
    TiaoNuoEntry(-301, 4187),
    # 初十日
    TiaoNuoEntry(-585, 3858),
    # 十一日
    TiaoNuoEntry(-705, 3343),
    # 十二日
    TiaoNuoEntry(-875, 2633),
    # 十三日
    TiaoNuoEntry(-906, 2766),
    # 十四日（特殊）
    TiaoNuoEntry(-1102, 809, True, chu_shu=8268, mo_shu=2232, chu_lv=1102, mo_lv=1102),
    # 十五日
    TiaoNuoEntry(1400, 1353),
    # 十六日
    TiaoNuoEntry(982, 1249),
    # 十七日
    TiaoNuoEntry(739, 2677),
    # 十八日
    TiaoNuoEntry(606, 2974),
    # 十九日
    TiaoNuoEntry(404, 3598),
    # 二十日
    TiaoNuoEntry(303, 4030),
    # 廿一日（特殊）
    TiaoNuoEntry(54, 4265, True, chu_shu=6993, mo_shu=3507, chu_lv=54, mo_lv=54),
    # 廿二日
    TiaoNuoEntry(-107, 4395),
    # 廿三日
    TiaoNuoEntry(-306, 4124),
    # 廿四日
    TiaoNuoEntry(-505, 3755),
    # 廿五日
    TiaoNuoEntry(-703, 3197),
    # 廿六日
    TiaoNuoEntry(-897, 2458),
    # 廿七日
    TiaoNuoEntry(-909, 1579),
    # 廿八日（特殊）
    TiaoNuoEntry(-508, 589, True, chu_shu=5824, mo_shu=4676, chu_lv=508, mo_lv=508),
)

_GAIN_LOSS = array("i", (e.gain_loss for e in TIAO_NUO_TABLE))
_TIAO_NU = array("i", (e.tiao_nu for e in TIAO_NUO_TABLE))


# ------------------------------------------------------------------
# 天文：月球平近點角 → 入轉日／餘
# ------------------------------------------------------------------
def lunar_mean_anomaly_deg(jd: float) -> float:
    """
    Meeus 《Astronomical Algorithms》月球平近點角 M（度）。
    d = JD - J2000.0
    M = 134.9634114 + 13.06499305542 × d   (mod 360)
    """
    d = jd - 2451545.0
    M = (134.9634114 + 13.06499305542 * d) % 360.0
    if M < 0:
        M += 360.0
    return M


def anomaly_to_ru_zhuan(M_deg: float, ri_fa: int = RI_FA) -> Tuple[int, int]:
    """
    將平近點角映射至古典 1～28 日立成表。

    近點月 ≈ 27.55455 日，立成表以 28 日覆蓋一整周。
    回傳 (入轉日 1～28, 入轉餘 0～ri_fa-1)
    """
    frac = (M_deg % 360.0) / 360.0
    total = frac * 28.0
    day = int(total) % 28 + 1          # 1～28
    yu = int((total % 1.0) * ri_fa)
    if yu >= ri_fa:
        yu = ri_fa - 1
    return day, yu


def ru_zhuan_from_jd(jd: float, ri_fa: int = RI_FA) -> Tuple[int, int, float]:
    """由儒略日直接得到入轉日、入轉餘、以及原始平近點角（度）。"""
    M = lunar_mean_anomaly_deg(jd)
    day, yu = anomaly_to_ru_zhuan(M, ri_fa)
    return day, yu, M


# ------------------------------------------------------------------
# 古典查表：求朓胸定數 + 全部中間組數
# ------------------------------------------------------------------
def calc_tiaonuo_dingshu(
    ru_zhuan_day: int,
    ru_zhuan_yu: int,
    ri_fa: int = RI_FA,
) -> int:
    """純整數求朓胸定數（相容舊介面）。"""
    detail = calc_tiaonuo_detail(ru_zhuan_day, ru_zhuan_yu, ri_fa)
    return detail["朓胸定數"]


def calc_tiaonuo_detail(
    ru_zhuan_day: int,
    ru_zhuan_yu: int,
    ri_fa: int = RI_FA,
) -> Dict[str, Any]:
    """
    求朓胸定數，並回傳卷一所有中間組數。

    回傳字典包含：
      入轉日, 入轉餘, 損益率, 朓胸積,
      是否特殊日, 初數, 末數, 初率, 末率,
      中間delta, 計算說明, 朓胸定數
    """
    if not (1 <= ru_zhuan_day <= 28):
        raise ValueError(f"入轉日必須 1～28，收到 {ru_zhuan_day}")
    yu = ru_zhuan_yu % ri_fa if ru_zhuan_yu else 0

    entry = TIAO_NUO_TABLE[ru_zhuan_day]
    base = entry.tiao_nu
    gain = entry.gain_loss

    result: Dict[str, Any] = {
        "入轉日": ru_zhuan_day,
        "入轉餘": yu,
        "損益率": gain,
        "朓胸積": base,
        "是否特殊日": entry.is_special,
        "初數": entry.chu_shu if entry.is_special else None,
        "末數": entry.mo_shu if entry.is_special else None,
        "初率": entry.chu_lv if entry.is_special else None,
        "末率": entry.mo_lv if entry.is_special else None,
        "日法": ri_fa,
    }

    if not entry.is_special:
        delta = (yu * abs(gain)) // ri_fa
        dingshu = base + delta if gain >= 0 else base - delta
        result["中間delta"] = delta
        result["計算說明"] = (
            f"普通日：朓胸積({base}) {'+' if gain >= 0 else '−'} "
            f"(入轉餘 × |損益率|) // 日法 = {base} {'+' if gain >= 0 else '−'} {delta}"
        )
    else:
        # 特殊日分段
        if yu <= entry.chu_shu:
            delta = (yu * entry.chu_lv) // entry.chu_shu if entry.chu_shu else 0
            segment = "初數以下"
            formula = f"(入轉餘 × 初率) // 初數 = ({yu} × {entry.chu_lv}) // {entry.chu_shu} = {delta}"
        else:
            yu2 = yu - entry.chu_shu
            delta = (yu2 * entry.mo_lv) // entry.mo_shu if entry.mo_shu else 0
            delta = entry.chu_lv - delta  # 用減初率
            segment = "初數以上"
            formula = (
                f"初數以上：用減初率 → 初率 − (餘 × 末率)//末數 = "
                f"{entry.chu_lv} − ({yu2} × {entry.mo_lv})//{entry.mo_shu}"
            )
        dingshu = base + delta if gain >= 0 else base - delta
        result["中間delta"] = delta
        result["計算說明"] = f"特殊日（{segment}）：{formula} → 定數 = {base} {'+' if gain >= 0 else '−'} {delta}"

    result["朓胸定數"] = dingshu
    return result


def apply_tiaonuo(
    jing_xiao_yu: int,
    tiaonuo: int,
    ri_fa: int = RI_FA,
) -> Tuple[int, int]:
    """
    套用到經朔小餘 → (大餘進退, 定小餘)
    古籍：朓減、胸加。
    """
    xiao = jing_xiao_yu - tiaonuo
    da_tui = 0
    if xiao < 0:
        da_tui = -1
        xiao += ri_fa
    elif xiao >= ri_fa:
        da_tui = 1
        xiao -= ri_fa
    return da_tui, xiao


def full_tiaonuo_pipeline(
    jd: float,
    jing_xiao_yu: Optional[int] = None,
    ri_fa: int = RI_FA,
) -> Dict[str, Any]:
    """
    完整卷一流程：儒略日 → 入轉 → 立成表 → 朓胸定數 → 定朔小餘

    若未提供 jing_xiao_yu，則以當日時間比例示意（0～日法）。
    """
    ru_day, ru_yu, M_deg = ru_zhuan_from_jd(jd, ri_fa)
    detail = calc_tiaonuo_detail(ru_day, ru_yu, ri_fa)

    if jing_xiao_yu is None:
        # 以儒略日小數部分作為示意小餘
        frac = jd % 1.0
        jing_xiao_yu = int(frac * ri_fa)

    da_tui, ding_xiao = apply_tiaonuo(jing_xiao_yu, detail["朓胸定數"], ri_fa)

    detail.update({
        "平近點角": round(M_deg, 4),
        "經朔小餘": jing_xiao_yu,
        "定朔大餘進退": da_tui,
        "定朔小餘": ding_xiao,
    })
    return detail


# ------------------------------------------------------------------
# 古典「求天正經朔入曆」保留介面（若有真實朔積分可用）
# ------------------------------------------------------------------
LI_YING_CHA = 2217032
LI_ZHONG_FEN = 289302


def calc_ru_li(shuo_ji_fen: int) -> Tuple[int, int]:
    """
    求入曆日及餘（古典路徑，需真實朔積分）。
    目前常數為示意，實際應依所用曆法精確填入。
    """
    total = shuo_ji_fen + LI_YING_CHA
    day = total // LI_ZHONG_FEN
    yu = total % LI_ZHONG_FEN
    ru_day = (day % 28) + 1
    return ru_day, yu
