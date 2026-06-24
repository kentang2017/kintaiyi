"""卷十五：五陣八陣視覺化資料與 SVG。"""

from __future__ import annotations

from html import escape

_WUZHEN_ORDER = ("曲陣", "直陣", "銳陣", "圓陣", "方陣")
_WUZHEN_SHORT = {"曲陣": "曲", "直陣": "直", "銳陣": "銳", "圓陣": "圓", "方陣": "方"}
_FLAG_FILL = {
    "黑旗": "#1a1a2e",
    "青旗": "#2d6a4f",
    "赤旗": "#c1121f",
    "黃旗": "#e9c46a",
    "白旗": "#e9ecef",
    "—": "#adb5bd",
}
_FLAG_STROKE = {
    "黑旗": "#4a4e69",
    "青旗": "#40916c",
    "赤旗": "#e5383b",
    "黃旗": "#f4a261",
    "白旗": "#ced4da",
    "—": "#868e96",
}
# 四正四奇：龍天虎／風握機雲／鳥地蛇
_BAZHEN_GRID = (
    ("龍", "天", "虎"),
    ("風", None, "雲"),
    ("鳥", "地", "蛇"),
)
_WUZHEN_RULES = (
    ("1、8", "曲陣", "黑旗", "北方"),
    ("3、7", "直陣", "青旗", "東方"),
    ("4、9", "銳陣", "赤旗", "南方"),
    ("2、5", "圓陣", "黃旗", "中央"),
    ("6", "方陣", "白旗", "西方"),
)
_COMPASS = {
    "西北": (0, -1),
    "正北": (0, -1),
    "東北": (1, -1),
    "正東": (1, 0),
    "東南": (1, 1),
    "正南": (0, 1),
    "西南": (-1, 1),
    "正西": (-1, 0),
}


def _cell_str(value) -> str:
    """統一為字串，避免 st.dataframe Arrow 混用 int/str。"""
    if value is None or value == "":
        return "—"
    return str(value)


def _zhen_row(label: str, zhen: dict | None) -> dict:
    zhen = zhen or {}
    return {
        "主客": label,
        "算數": _cell_str(zhen.get("算數")),
        "數位": _cell_str(zhen.get("數位")),
        "陣型": _cell_str(zhen.get("陣型")),
        "旗色": _cell_str(zhen.get("旗色")),
        "方位": _cell_str(zhen.get("方位")),
    }


def wuzhen_table_rows(wuzhen: dict | None) -> list[dict]:
    """主客五陣置旗對照表。"""
    wuzhen = wuzhen or {}
    return [
        _zhen_row("主", wuzhen.get("主陣旗")),
        _zhen_row("客", wuzhen.get("客陣旗")),
    ]


def wuzhen_reference_rows() -> list[dict]:
    """五陣置旗規則（算數個位）。"""
    return [
        {
            "算數個位": digits,
            "陣型": name,
            "旗色": flag,
            "方位": direction,
        }
        for digits, name, flag, direction in _WUZHEN_RULES
    ]


def _text_on_flag(flag: str) -> str:
    return "#1a1a2e" if flag in ("黃旗", "白旗") else "#f8f9fa"


def _wuzhen_bar_svg(
    wuzhen: dict | None,
    *,
    x: int,
    y: int,
    w: int,
    h: int,
    home_label: str = "主",
    away_label: str = "客",
) -> str:
    wuzhen = wuzhen or {}
    home_type = (wuzhen.get("主陣旗") or {}).get("陣型", "")
    away_type = (wuzhen.get("客陣旗") or {}).get("陣型", "")
    cell_w = w / len(_WUZHEN_ORDER)
    parts: list[str] = []
    for i, ztype in enumerate(_WUZHEN_ORDER):
        cx = x + i * cell_w + cell_w / 2
        cy = y + h * 0.42
        short = _WUZHEN_SHORT[ztype]
        sample_flag = next((f for _, n, f, _ in _WUZHEN_RULES if n == ztype), "—")
        fill = _FLAG_FILL.get(sample_flag, "#adb5bd")
        stroke = _FLAG_STROKE.get(sample_flag, "#868e96")
        active_home = ztype == home_type
        active_away = ztype == away_type
        rx = 8 if active_home or active_away else 4
        opacity = 1.0 if active_home or active_away else 0.55
        parts.append(
            f'<rect x="{x + i * cell_w + 6:.1f}" y="{y + 18:.1f}" '
            f'width="{cell_w - 12:.1f}" height="{h - 36:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{"2.5" if active_home or active_away else "1"}" '
            f'opacity="{opacity}"/>'
        )
        parts.append(
            f'<text x="{cx:.1f}" y="{cy:.1f}" text-anchor="middle" '
            f'font-size="18" font-weight="700" fill="{_text_on_flag(sample_flag)}">{short}</text>'
        )
        parts.append(
            f'<text x="{cx:.1f}" y="{y + h - 8:.1f}" text-anchor="middle" '
            f'font-size="11" fill="#495057">{escape(ztype)}</text>'
        )
        if active_home:
            parts.append(
                f'<circle cx="{x + i * cell_w + cell_w - 14:.1f}" cy="{y + 26:.1f}" r="7" '
                f'fill="#1971c2" stroke="#fff" stroke-width="1.5"/>'
            )
            parts.append(
                f'<text x="{x + i * cell_w + cell_w - 14:.1f}" y="{y + 30:.1f}" '
                f'text-anchor="middle" font-size="9" fill="#fff" font-weight="700">'
                f'{escape(home_label)}</text>'
            )
        if active_away:
            parts.append(
                f'<circle cx="{x + i * cell_w + 14:.1f}" cy="{y + 26:.1f}" r="7" '
                f'fill="#e03131" stroke="#fff" stroke-width="1.5"/>'
            )
            parts.append(
                f'<text x="{x + i * cell_w + 14:.1f}" y="{y + 30:.1f}" '
                f'text-anchor="middle" font-size="9" fill="#fff" font-weight="700">'
                f'{escape(away_label)}</text>'
            )
    return "".join(parts)


def _bazhen_grid_svg(
    *,
    x: int,
    y: int,
    size: int,
    center_label: str = "握機",
) -> str:
    cell = size / 3
    parts: list[str] = []
    for row in range(3):
        for col in range(3):
            cx = x + col * cell
            cy = y + row * cell
            name = _BAZHEN_GRID[row][col]
            if name is None:
                parts.append(
                    f'<rect x="{cx + 4:.1f}" y="{cy + 4:.1f}" '
                    f'width="{cell - 8:.1f}" height="{cell - 8:.1f}" rx="10" '
                    f'fill="#fff3bf" stroke="#f08c00" stroke-width="2"/>'
                )
                parts.append(
                    f'<text x="{cx + cell / 2:.1f}" y="{cy + cell / 2 + 5:.1f}" '
                    f'text-anchor="middle" font-size="15" font-weight="700" fill="#e67700">'
                    f'{escape(center_label)}</text>'
                )
            else:
                parts.append(
                    f'<rect x="{cx + 6:.1f}" y="{cy + 6:.1f}" '
                    f'width="{cell - 12:.1f}" height="{cell - 12:.1f}" rx="6" '
                    f'fill="#f1f3f5" stroke="#868e96" stroke-width="1"/>'
                )
                parts.append(
                    f'<text x="{cx + cell / 2:.1f}" y="{cy + cell / 2 + 5:.1f}" '
                    f'text-anchor="middle" font-size="16" font-weight="600" fill="#343a40">'
                    f'{escape(name)}</text>'
                )
    return "".join(parts)


def _compass_svg(
    wuzhen: dict | None,
    *,
    cx: float,
    cy: float,
    r: float,
    home_label: str = "主",
    away_label: str = "客",
) -> str:
    wuzhen = wuzhen or {}
    chubing = wuzhen.get("陳兵出鄉") or {}
    home_dir = chubing.get("主", "—")
    away_dir = chubing.get("客", "—")
    parts = [
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="#f8f9fa" '
        f'stroke="#ced4da" stroke-width="1.5"/>',
        f'<line x1="{cx - r:.1f}" y1="{cy:.1f}" x2="{cx + r:.1f}" y2="{cy:.1f}" '
        f'stroke="#dee2e6" stroke-width="1"/>',
        f'<line x1="{cx:.1f}" y1="{cy - r:.1f}" x2="{cx:.1f}" y2="{cy + r:.1f}" '
        f'stroke="#dee2e6" stroke-width="1"/>',
        f'<text x="{cx:.1f}" y="{cy - r - 6:.1f}" text-anchor="middle" '
        f'font-size="10" fill="#868e96">北</text>',
        f'<text x="{cx:.1f}" y="{cy + r + 14:.1f}" text-anchor="middle" '
        f'font-size="10" fill="#868e96">南</text>',
        f'<text x="{cx - r - 10:.1f}" y="{cy + 4:.1f}" text-anchor="end" '
        f'font-size="10" fill="#868e96">西</text>',
        f'<text x="{cx + r + 10:.1f}" y="{cy + 4:.1f}" text-anchor="start" '
        f'font-size="10" fill="#868e96">東</text>',
    ]
    for label, direction, color in (
        (home_label, home_dir, "#1971c2"),
        (away_label, away_dir, "#e03131"),
    ):
        vec = _COMPASS.get(direction)
        if not vec:
            continue
        dx, dy = vec
        length = r * 0.72
        x2 = cx + dx * length
        y2 = cy + dy * length
        parts.append(
            f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="2.5" marker-end="url(#arrow-{color[1:]})"/>'
        )
        parts.append(
            f'<text x="{x2 + dx * 12:.1f}" y="{y2 + dy * 12 + 4:.1f}" '
            f'text-anchor="middle" font-size="10" fill="{color}" font-weight="600">'
            f'{escape(label)}·{escape(direction)}</text>'
        )
    return "".join(parts)


def wuzhen_bazhen_svg(
    wuzhen: dict | None,
    *,
    width: int = 560,
    height: int = 300,
    title_five: str = "五陣",
    title_eight: str = "八陣",
    title_chubing: str = "陳兵出鄉",
    center_label: str = "握機",
    home_label: str = "主",
    away_label: str = "客",
) -> str:
    """五陣條 + 八陣九宮 + 出鄉羅盤。"""
    w = width
    h = height
    bar_w = int(w * 0.58)
    grid_size = min(int(h * 0.78), int(w * 0.34))
    grid_x = w - grid_size - 16
    markers = (
        '<defs>'
        '<marker id="arrow-1971c2" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M 0 0 L 10 5 L 0 10 z" fill="#1971c2"/></marker>'
        '<marker id="arrow-e03131" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M 0 0 L 10 5 L 0 10 z" fill="#e03131"/></marker>'
        '</defs>'
    )
    body = (
        f'<text x="16" y="22" font-size="13" font-weight="700" fill="#343a40">'
        f'{escape(title_five)}</text>'
        f'{_wuzhen_bar_svg(wuzhen, x=12, y=28, w=bar_w - 24, h=118, home_label=home_label, away_label=away_label)}'
        f'<text x="16" y="168" font-size="12" font-weight="600" fill="#495057">'
        f'{escape(title_chubing)}</text>'
        f'{_compass_svg(wuzhen, cx=bar_w / 2, cy=228, r=52, home_label=home_label, away_label=away_label)}'
        f'<text x="{grid_x:.1f}" y="22" font-size="13" font-weight="700" fill="#343a40">'
        f'{escape(title_eight)}</text>'
        f'{_bazhen_grid_svg(x=grid_x, y=28, size=grid_size - 20, center_label=center_label)}'
        f'<text x="{grid_x:.1f}" y="{h - 8:.1f}" font-size="10" fill="#868e96" text-anchor="start">'
        f'{escape((wuzhen or {}).get("八陣要訣", ""))}</text>'
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="100%" style="max-width:{w}px;display:block;margin:0 auto;">'
        f'{markers}{body}</svg>'
    )