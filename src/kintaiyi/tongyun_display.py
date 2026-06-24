# 卷十二～十四：統運入卦、十二運卦象、行支編年 — 盤面／說明區摘要

from __future__ import annotations

from . import config
from .biannian import for_year as biannian_for_year


def _clip(text: str, n: int = 56) -> str:
    s = (text or "").strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def tongyun_summary_lines(ttext: dict | None, *, limit: int = 4) -> list[str]:
    """由 pan()['卷十二'～'卷十四'] 產生中宮 tooltip 用摘要行。"""
    ttext = ttext or {}
    lines: list[str] = []

    v12 = ttext.get("卷十二") or {}
    rg = v12.get("統運入卦") or {}
    if rg.get("卦"):
        period = f"（入爻{rg.get('入爻年數', '—')}年）"
        lines.append(f"統運·{rg.get('運', '')}{rg.get('卦', '')}{rg.get('爻名', '')}{period}")
        hf = v12.get("入爻禍福") or {}
        duan = hf.get("所主") or rg.get("斷語")
        if duan:
            lines.append(_clip(f"入爻·{duan}", 52))
        lz = v12.get("流年直卦") or {}
        if lz.get("直卦"):
            lines.append(
                f"流年·{lz.get('干支', '')}{lz['直卦']}{lz.get('爻名', '')}"
            )
        bg = v12.get("變卦納甲") or {}
        if bg.get("變卦"):
            lines.append(f"變卦·{bg.get('本卦', '')}→{bg['變卦']}")

    v13 = ttext.get("卷十三") or {}
    gx = v13.get("統運卦象") or {}
    if gx.get("當前爻觀象"):
        lines.append(_clip(f"卦象·{gx['當前爻觀象']}", 56))
    elif gx.get("卦"):
        lines.append(f"卦象·{gx.get('運', '')}{gx.get('卦', '')}{gx.get('爻名', '')}")

    v14 = ttext.get("卷十四") or {}
    hz = (v14.get("行支編年") or {}).get("當年例") or []
    if hz:
        e = hz[0]
        lines.append(
            _clip(
                f"編年·{e.get('紀年', '')}{e.get('卦', '')}{e.get('爻', '')}：{e.get('摘要', '')}",
                56,
            )
        )
    elif v14.get("要訣"):
        lines.append(_clip(f"編年·{v14['要訣']}", 56))

    return lines[:limit]


def ttext_vol12_14(year: int, month: int = 6, day: int = 15) -> dict:
    """依查詢年重算卷十二～十四區塊。"""
    gz = config.gangzhi(year, month, day, 12, 0)
    year_gan, year_zhi = gz[0][0], gz[0][1]
    return {
        "卷十二": config.vol12_zonghe(year, year_gan, year_zhi, month, day),
        "卷十三": config.gua_xiang_zonghe(year),
        "卷十四": config.biannian_zonghe(year),
    }


def apply_tongyun_query(
    ttext: dict | None,
    query_year: int,
    chart_year: int,
    *,
    month: int = 6,
    day: int = 15,
) -> dict:
    """以查詢年覆寫 pan 內卷十二～十四（與排盤年不同時）。"""
    base = dict(ttext or {})
    if int(query_year) == int(chart_year):
        return base
    base.update(ttext_vol12_14(int(query_year), month, day))
    return base


def historical_compare(year: int) -> dict:
    """統運入卦歷史驗例對照。"""
    info = biannian_for_year(int(year))
    rugua = info.get("統運入卦") or {}
    near: list[dict] = []
    for item in info.get("近例") or []:
        delta = int(item.get("年", year)) - int(year)
        near.append({**item, "相差": delta})
    return {
        "查詢年": int(year),
        "統運入卦": rugua,
        "當年例": list(info.get("當年例") or []),
        "同卦爻例": list(info.get("同卦爻例") or []),
        "近例": near,
    }