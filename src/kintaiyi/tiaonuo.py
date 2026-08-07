# -*- coding: utf-8 -*-
"""
朓胸定數 (Tiao-Nuo Dingshu) — 入轉中心差補正

根據古代曆法立成表（損益率 + 朓胸積）計算月亮近點月的中心差。
純整數運算，O(1) 查表，適合在太乙排盤中快速呼叫。
"""
from __future__ import annotations

from typing import NamedTuple, Tuple
from array import array


class TiaoNuoEntry(NamedTuple):
    gain_loss: int          # 損益率（正=益，負=損）
    tiao_nu: int            # 朓胸積（正=朓，負=胸）
    is_special: bool = False
    chu_shu: int = 0        # 初數（特殊日）
    mo_shu: int = 0         # 末數
    chu_lv: int = 0         # 初率
    mo_lv: int = 0          # 末率


# 日法（可依實際曆法調整；圖中常見一萬〇五百附近）
RI_FA = 10500

# ------------------------------------------------------------------
# 完整 1～28 日立成表
# 特殊日（7、14、21、28）已填入圖中初數／末數
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

# 預轉 array 加速（可選）
_GAIN_LOSS = array("i", (e.gain_loss for e in TIAO_NUO_TABLE))
_TIAO_NU = array("i", (e.tiao_nu for e in TIAO_NUO_TABLE))


def calc_tiaonuo_dingshu(
    ru_zhuan_day: int,
    ru_zhuan_yu: int,
    ri_fa: int = RI_FA,
) -> int:
    """
    求朓胸定數（純整數、O(1)）

    Parameters
    ----------
    ru_zhuan_day : int
        入轉日（算外，1～28）
    ru_zhuan_yu : int
        入轉餘（0 ≤ yu < ri_fa）
    ri_fa : int
        日法

    Returns
    -------
    int
        正 = 朓，負 = 胸
    """
    if not (1 <= ru_zhuan_day <= 28):
        raise ValueError(f"入轉日必須 1～28，收到 {ru_zhuan_day}")
    if ru_zhuan_yu < 0 or ru_zhuan_yu >= ri_fa:
        ru_zhuan_yu %= ri_fa

    entry = TIAO_NUO_TABLE[ru_zhuan_day]
    base = entry.tiao_nu

    if not entry.is_special:
        delta = (ru_zhuan_yu * abs(entry.gain_loss)) // ri_fa
        return base + delta if entry.gain_loss >= 0 else base - delta

    # 特殊日（依古籍「初數以上以初數減之…用減初率」）
    if ru_zhuan_yu <= entry.chu_shu:
        delta = (ru_zhuan_yu * entry.chu_lv) // entry.chu_shu if entry.chu_shu else 0
    else:
        yu2 = ru_zhuan_yu - entry.chu_shu
        delta = (yu2 * entry.mo_lv) // entry.mo_shu if entry.mo_shu else 0
        delta = entry.chu_lv - delta  # 用減初率

    return base + delta if entry.gain_loss >= 0 else base - delta


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


# ------------------------------------------------------------------
# 求天正經朔入曆（簡化版）
# 注意：此處常數為示意，實際應依所用曆法（紀元／授時等）精確填入
# ------------------------------------------------------------------
LI_YING_CHA = 2217032          # 曆盈差（秒級示意）
LI_ZHONG_FEN = 289302          # 曆終分（秒示意）


def calc_ru_li(shuo_ji_fen: int) -> Tuple[int, int]:
    """
    求入曆日及餘（簡化）

    Parameters
    ----------
    shuo_ji_fen : int
        朔積分

    Returns
    -------
    (入轉日, 入轉餘)
    """
    total = shuo_ji_fen + LI_YING_CHA
    day = total // LI_ZHONG_FEN
    yu = total % LI_ZHONG_FEN
    # 轉成 1～28 的入轉日（實際近點月約 27.55 日，此處簡化取模 28）
    ru_day = (day % 28) + 1
    return ru_day, yu
