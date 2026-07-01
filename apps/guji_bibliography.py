"""古籍書目：把 docs/guji.md 的朝代書目表格轉為典雅書目卡片頁面。

與 ``tutorial_guide.py`` 走相同路線 —— 依朝代分組 + 錨點導覽 pill，
搭配 ``custom_css.py`` 裡的 ``.guji-*`` 樣式，維持與 App 其他頁面一致
的暗色古典美學。
"""

from __future__ import annotations

import re
from html import escape as _esc

_URL_RE = re.compile(r"(https?://[^\s\u3000]+)")


def _split_row(line: str) -> list[str]:
    cells = line.strip().strip("|").split("|")
    return [c.strip() for c in cells]


def _parse_table(md_text: str) -> list[dict]:
    """解析 docs/guji.md 裡唯一的 markdown 表格，回傳 list of dict。"""
    lines = [ln for ln in md_text.splitlines() if ln.strip().startswith("|")]
    if len(lines) < 2:
        return []
    headers = _split_row(lines[0])
    rows: list[dict] = []
    for line in lines[2:]:
        cells = _split_row(line)
        if len(cells) < len(headers):
            cells += [""] * (len(headers) - len(cells))
        elif len(cells) > len(headers):
            cells = cells[: len(headers)]
        rows.append(dict(zip(headers, cells)))
    return rows


def _group_by_dynasty(rows: list[dict]) -> list[dict]:
    """依「年份」欄（實為朝代）將連續同朝代書目歸為一組，保留原文順序。"""
    groups: list[dict] = []
    for row in rows:
        dynasty = row.get("年份", "").strip() or "未詳"
        if groups and groups[-1]["dynasty"] == dynasty:
            groups[-1]["books"].append(row)
        else:
            groups.append({"dynasty": dynasty, "books": [row]})
    return groups


def _linkify(text: str) -> str:
    """把備註中的裸網址轉為金色底線超連結，其餘文字正常 escape。"""
    parts = _URL_RE.split(text)
    out = []
    for i, part in enumerate(parts):
        if i % 2 == 1:
            out.append(
                f'<a class="guji-link" href="{_esc(part)}" target="_blank" '
                f'rel="noopener noreferrer">{_esc(part)}</a>'
            )
        else:
            out.append(_esc(part))
    return "".join(out)


def _slugify(dynasty: str) -> str:
    return "guji-" + re.sub(r"\s+", "", dynasty)


def _render_book_card(row: dict) -> str:
    title = row.get("書名", "").strip()
    author = row.get("作者", "").strip()
    note = row.get("備註", "").strip()
    note_html = f'<div class="guji-book-note">{_linkify(note)}</div>' if note else ""
    author_html = f'<span class="guji-book-author">{_esc(author)}</span>' if author else ""
    return (
        '<div class="guji-book-card">'
        '<div class="guji-book-head">'
        f'<span class="guji-book-title">{_esc(title)}</span>'
        f"{author_html}"
        "</div>"
        f"{note_html}"
        "</div>"
    )


def render_guji_bibliography(md_text: str) -> str:
    """把 docs/guji.md 轉為「古籍書目」頁面完整 HTML。"""
    rows = _parse_table(md_text)
    groups = _group_by_dynasty(rows)

    toc_pills = "".join(
        f'<a class="tutorial-toc-pill" href="#{_slugify(g["dynasty"])}">'
        f'{_esc(g["dynasty"])} ({len(g["books"])})</a>'
        for g in groups
    )

    html_parts = [
        '<div class="guji-guide-container">',
        '  <div class="guji-guide-header">',
        "    <h2>📚 太乙古籍書目</h2>",
        '    <div class="guji-guide-ornament">✦ ❖ ✦</div>',
        '    <p class="guji-guide-subtitle">歷代太乙典籍輯錄，考鏡源流</p>',
        "  </div>",
        f'  <div class="tutorial-toc guji-toc">{toc_pills}</div>',
    ]

    for g in groups:
        html_parts.append(
            f'  <div class="tutorial-group guji-group" id="{_slugify(g["dynasty"])}">'
        )
        html_parts.append('    <div class="tutorial-group-header">')
        html_parts.append('      <span class="tutorial-group-icon">📖</span>')
        html_parts.append(
            f'      <span class="tutorial-group-title">{_esc(g["dynasty"])}'
            f'（{len(g["books"])} 種）</span>'
        )
        html_parts.append("    </div>")
        html_parts.append('    <div class="guji-book-list">')
        for row in g["books"]:
            html_parts.append(_render_book_card(row))
        html_parts.append("    </div>")
        html_parts.append("  </div>")

    html_parts.append("</div>")
    return "\n".join(html_parts)
