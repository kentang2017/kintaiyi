"""卷九：大小遊軌運入卦、重卦策數 — 盤面／說明區摘要。"""

from __future__ import annotations


def _cell_str(value) -> str:
    """統一為字串，避免 st.dataframe Arrow 混用 int/str。"""
    if value is None or value == "":
        return "—"
    return str(value)


def _clip(text: str, n: int = 56) -> str:
    s = (text or "").strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def inner_outer_rows(
    nei: dict | None,
    wai: dict | None,
    *,
    scope: str,
) -> list[dict]:
    """內外入卦、動爻、四象策數對照表。"""
    rows: list[dict] = []
    nei = nei or {}
    wai = wai or {}
    if nei:
        yao = nei.get("爻名") or nei.get("動爻")
        rows.append({
            "層次": f"{scope}內",
            "卦": _cell_str(nei.get("內卦")),
            "卦序": _cell_str(nei.get("卦序")),
            "入卦年": _cell_str(nei.get("入卦年數")),
            "動爻": _cell_str(yao),
            "四象": _cell_str(nei.get("四象")),
            "策數": _cell_str(nei.get("策數")),
            "備註": _cell_str(nei.get("要訣")),
        })
    if wai:
        note = wai.get("要訣", "")
        if wai.get("三才"):
            note = f"{wai['三才']}；{note}" if note else wai["三才"]
        rows.append({
            "層次": f"{scope}外",
            "卦": _cell_str(wai.get("外卦")),
            "卦序": _cell_str(wai.get("卦序")),
            "入卦年": _cell_str(wai.get("入卦年數")),
            "動爻": _cell_str(wai.get("動爻")),
            "四象": _cell_str(wai.get("四象")),
            "策數": _cell_str(wai.get("策數")),
            "備註": _cell_str(note),
        })
    return rows


def chong_gua_row(block: dict | None, *, scope: str) -> dict:
    """重卦合計一行。"""
    block = block or {}
    return {
        "遊": _cell_str(scope),
        "重卦": _cell_str(block.get("重卦")),
        "內卦": _cell_str(block.get("內卦")),
        "外卦": _cell_str(block.get("外卦")),
        "內爻": _cell_str(block.get("內爻名")),
        "內策": _cell_str(block.get("內策")),
        "外策": _cell_str(block.get("外策")),
        "總策": _cell_str(block.get("總策")),
        "入內年": _cell_str(block.get("入內年數")),
        "入外年": _cell_str(block.get("入外年數")),
    }


def limit_rows(v9: dict | None) -> list[dict]:
    """陽九、百六大小限對照。"""
    v9 = v9 or {}
    rows: list[dict] = []
    for label, key in (("陽九", "陽九限數"), ("百六", "百六限數")):
        info = v9.get(key) or {}
        if not info:
            continue
        rows.append({
            "限名": _cell_str(label),
            "大限": _cell_str(info.get("大限元數")),
            "小限": _cell_str(info.get("小限元數")),
            "入小限序": _cell_str(info.get("入小限序")),
            "入限年數": _cell_str(info.get("入限年數")),
            "臨數終": "是" if info.get("臨數終") else "否",
            "斷語": _cell_str(info.get("斷語")),
        })
    return rows


def guiyun_summary_lines(v9: dict | None, *, limit: int = 4) -> list[str]:
    """中宮 tooltip 用卷九摘要。"""
    v9 = v9 or {}
    lines: list[str] = []
    dy = v9.get("大遊軌運") or {}
    xy = v9.get("小遊軌運") or {}
    if dy.get("重卦"):
        lines.append(
            f"大遊·{dy['重卦']}{dy.get('內爻名', '')}"
            f"（策{dy.get('總策', '—')}）"
        )
    if xy.get("重卦"):
        lines.append(
            f"小遊·{xy['重卦']}{xy.get('內爻名', '')}"
            f"（策{xy.get('總策', '—')}）"
        )
    if v9.get("大遊落宮") or v9.get("小遊落宮"):
        lines.append(
            f"落宮·{v9.get('大遊落宮', '—')}/{v9.get('小遊落宮', '—')}"
        )
    xz = v9.get("小遊行爻災祥") or {}
    if xz.get("斷語"):
        lines.append(_clip(f"行爻·{xz['斷語']}", 52))
    yj = v9.get("陽九限數") or {}
    bl = v9.get("百六限數") or {}
    if yj or bl:
        lines.append(
            f"限數·陽九{yj.get('入限年數', '—')}／百六{bl.get('入限年數', '—')}年"
        )
    return lines[:limit]