# tiaonuo.py
from typing import NamedTuple, Tuple
from array import array

class TiaoNuoEntry(NamedTuple):
    gain_loss: int          # 損益率（正=益，負=損）
    tiao_nu: int            # 朓胸積
    is_special: bool = False
    chu_shu: int = 0        # 初數
    mo_shu: int = 0         # 末數
    chu_lv: int = 0         # 初率
    mo_lv: int = 0          # 末率


# ------------------------------------------------------------------
# 完整 1～28 日表 + 圖中精確初末數
# 日法先用 10500（圖中「日法一萬〇五百」附近），可依實際曆法調整
# ------------------------------------------------------------------
RI_FA = 10500

TIAO_NUO_TABLE: Tuple[TiaoNuoEntry, ...] = (
    TiaoNuoEntry(0, 0),  # dummy

    # 1
    TiaoNuoEntry(30, 0),
    # 2
    TiaoNuoEntry(904, 1035),
    # 3
    TiaoNuoEntry(802, 1982),
    # 4
    TiaoNuoEntry(706, 2797),
    # 5
    TiaoNuoEntry(408, 3464),
    # 6
    TiaoNuoEntry(308, 3952),
    # 7（特殊）
    TiaoNuoEntry(88, 4235, True, chu_shu=9332, mo_shu=1168, chu_lv=88, mo_lv=88),
    # 8
    TiaoNuoEntry(-102, 4363),
    # 9
    TiaoNuoEntry(-301, 4187),
    # 10
    TiaoNuoEntry(-585, 3858),
    # 11
    TiaoNuoEntry(-705, 3343),
    # 12
    TiaoNuoEntry(-875, 2633),
    # 13
    TiaoNuoEntry(-906, 2766),
    # 14（特殊）
    TiaoNuoEntry(-1102, 809, True, chu_shu=8268, mo_shu=2232, chu_lv=1102, mo_lv=1102),
    # 15
    TiaoNuoEntry(1400, 1353),
    # 16
    TiaoNuoEntry(982, 1249),
    # 17
    TiaoNuoEntry(739, 2677),
    # 18
    TiaoNuoEntry(606, 2974),
    # 19
    TiaoNuoEntry(404, 3598),
    # 20
    TiaoNuoEntry(303, 4030),
    # 21（特殊）
    TiaoNuoEntry(54, 4265, True, chu_shu=6993, mo_shu=3507, chu_lv=54, mo_lv=54),
    # 22
    TiaoNuoEntry(-107, 4395),
    # 23
    TiaoNuoEntry(-306, 4124),
    # 24
    TiaoNuoEntry(-505, 3755),
    # 25
    TiaoNuoEntry(-703, 3197),
    # 26
    TiaoNuoEntry(-897, 2458),
    # 27
    TiaoNuoEntry(-909, 1579),
    # 28（特殊）
    TiaoNuoEntry(-508, 589, True, chu_shu=5824, mo_shu=4676, chu_lv=508, mo_lv=508),
)

_GAIN_LOSS = array('i', (e.gain_loss for e in TIAO_NUO_TABLE))
_TIAO_NU  = array('i', (e.tiao_nu   for e in TIAO_NUO_TABLE))


def calc_tiaonuo_dingshu(
    ru_zhuan_day: int,
    ru_zhuan_yu: int,
    ri_fa: int = RI_FA,
) -> int:
    """
    求朓胸定數（純整數、O(1)）
    回傳正=朓、負=胸
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

    # 特殊日（依圖「初數以上以初數減之…用減初率」）
    if ru_zhuan_yu <= entry.chu_shu:
        delta = (ru_zhuan_yu * entry.chu_lv) // entry.chu_shu
    else:
        yu2 = ru_zhuan_yu - entry.chu_shu
        delta = (yu2 * entry.mo_lv) // entry.mo_shu
        delta = entry.chu_lv - delta          # 用減初率

    return base + delta if entry.gain_loss >= 0 else base - delta


def apply_tiaonuo(
    jing_xiao_yu: int,
    tiaonuo: int,
    ri_fa: int = RI_FA,
) -> Tuple[int, int]:
    """
    套用到經朔小餘 → (大餘進退, 定小餘)
    朓減、胸加
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
# 求天正經朔入曆（簡化版，依圖常數）
# ------------------------------------------------------------------
LI_YING_CHA = 2217032          # 曆盈差（秒級，依圖調整）
LI_ZHONG_FEN = 289302          # 曆終分（秒）

def calc_ru_li(shuo_ji_fen: int) -> Tuple[int, int]:
    """
    求入曆日及餘
    回傳 (入轉日, 入轉餘)
    """
    total = shuo_ji_fen + LI_YING_CHA
    day = total // LI_ZHONG_FEN
    yu = total % LI_ZHONG_FEN
    # 再轉成 1～28 的入轉日（依實際曆終日數調整）
    ru_day = (day % 28) + 1
    return ru_day, yu