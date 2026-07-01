"""災異統計：把 docs/disaster.md 的地震／水災史料表格轉為統計卡片頁面。

與 ``tutorial_guide.py`` 走相同路線 —— 純 HTML 折疊卡片
（``<details>``/``<summary>``），搭配 ``custom_css.py`` 裡的
``.classic-card`` / ``.disaster-*`` 樣式，維持與 App 其他頁面一致的
暗色古典美學，而不使用 ``st.expander``。
"""

from __future__ import annotations

import re
from html import escape as _esc

_SECTION_RE = re.compile(r"^\d+\.(.+)$", re.MULTILINE)
_YEAR_RE = re.compile(r"-?\d+")


def _parse_md_table(table_lines: list[str]) -> list[dict]:
    """把 markdown 表格（含表頭與分隔線）解析為 list of dict。"""
    if len(table_lines) < 2:
        return []

    def _split_row(line: str) -> list[str]:
        cells = line.strip().strip("|").split("|")
        return [c.strip() for c in cells]

    headers = _split_row(table_lines[0])
    rows: list[dict] = []
    for line in table_lines[2:]:
        if not line.strip():
            continue
        cells = _split_row(line)
        # 補齊/截斷欄位數，避免行末缺欄造成錯位
        if len(cells) < len(headers):
            cells += [""] * (len(headers) - len(cells))
        elif len(cells) > len(headers):
            cells = cells[: len(headers)]
        rows.append(dict(zip(headers, cells)))
    return rows


def _parse_sections(md_text: str) -> list[dict]:
    """依 `N.標題` 切段，回傳 [{title, description, rows}, ...]。"""
    matches = list(_SECTION_RE.finditer(md_text))
    sections: list[dict] = []
    for i, m in enumerate(matches):
        title = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md_text)
        body = md_text[start:end].strip()

        desc_lines: list[str] = []
        table_lines: list[str] = []
        in_table = False
        for line in body.splitlines():
            if line.strip().startswith("|"):
                in_table = True
                table_lines.append(line)
            elif not in_table and line.strip():
                desc_lines.append(line.strip())

        sections.append(
            {
                "title": title,
                "description": " ".join(desc_lines),
                "rows": _parse_md_table(table_lines),
            }
        )
    return sections


def _years(rows: list[dict], key: str) -> list[int]:
    years = []
    for r in rows:
        m = _YEAR_RE.search(r.get(key, ""))
        if m:
            try:
                years.append(int(m.group()))
            except ValueError:
                pass
    return years


def _stat_badge(value: str, label: str) -> str:
    return (
        '<div class="disaster-stat-badge">'
        f'<div class="disaster-stat-value">{_esc(value)}</div>'
        f'<div class="disaster-stat-label">{_esc(label)}</div>'
        "</div>"
    )


def _find_key(row: dict, *candidates: str) -> str:
    for c in candidates:
        if c in row:
            return row[c]
    return ""


def _render_row(row: dict) -> str:
    year = _find_key(row, "年份")
    place = _find_key(row, "地方", "受災省分/地方")
    kook = _find_key(row, "局")
    suan = _find_key(row, "主客算")
    geju = _find_key(row, "格局")
    level = _find_key(row, "級")

    matched = "符合" in geju
    mark = '<span class="disaster-match-mark" title="符合格局">✦</span>' if matched else ""

    meta_parts = []
    if level:
        meta_parts.append(f'<span class="disaster-row-level">{_esc(level)}級</span>')
    if kook:
        meta_parts.append(f'<span class="disaster-row-kook">{_esc(kook)}局</span>')
    if suan:
        meta_parts.append(f'<span class="disaster-row-suan">主客算 {_esc(suan)}</span>')
    meta_html = "".join(meta_parts)

    geju_html = f'<div class="disaster-row-geju">{_esc(geju)}{mark}</div>' if geju else ""

    return (
        '<div class="disaster-row">'
        f'<span class="disaster-row-year">{_esc(year)}</span>'
        '<div class="disaster-row-body">'
        f'<div class="disaster-row-place">{_esc(place)}</div>'
        f'<div class="disaster-row-meta">{meta_html}</div>'
        f"{geju_html}"
        "</div>"
        "</div>"
    )


_SECTION_ICONS = {"地震": "🌋", "水災": "🌊"}


def _render_section(section: dict, *, open_first: bool) -> str:
    rows = section["rows"]
    title = section["title"]
    icon = _SECTION_ICONS.get(title, "📊")
    years = _years(rows, "年份")

    badges = [_stat_badge(str(len(rows)), "史例筆數")]
    if years:
        badges.append(_stat_badge(f"{min(years)}–{max(years)}", "涵蓋年代"))
    matched_n = sum(1 for r in rows if "符合" in _find_key(r, "格局"))
    if matched_n:
        badges.append(_stat_badge(f"{matched_n}/{len(rows)}", "符合格局"))

    rows_html = "".join(_render_row(r) for r in rows)
    open_attr = " open" if open_first else ""

    return f"""
<details class="classic-card disaster-card"{open_attr}>
  <summary class="classic-card-header">
    <span class="classic-card-title">{icon} {_esc(title)}</span>
  </summary>
  <div class="classic-card-body">
    {f'<p class="disaster-section-desc">{_esc(section["description"])}</p>' if section["description"] else ""}
    <div class="disaster-stat-row">{"".join(badges)}</div>
    <div class="disaster-row-list">{rows_html}</div>
  </div>
</details>"""


def render_disaster_stats(md_text: str) -> str:
    """把 docs/disaster.md 轉為「災異統計」頁面完整 HTML。"""
    sections = _parse_sections(md_text)

    html_parts = [
        '<div class="disaster-guide-container">',
        '  <div class="disaster-guide-header">',
        "    <h2>🔥 災異統計</h2>",
        '    <div class="disaster-guide-ornament">✦ ❖ ✦</div>',
        '    <p class="disaster-guide-subtitle">太乙局式與歷史災異對照 —— 格局符應之驗</p>',
        "  </div>",
    ]
    for idx, section in enumerate(sections):
        html_parts.append(_render_section(section, open_first=(idx == 0)))
    html_parts.append("</div>")
    return "\n".join(html_parts)
