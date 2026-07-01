"""看盤要領：把《太乙神數》古典要領整理為分組卡片，供使用者快速查閱。

與 ``hex_timeline.render_classic_reading`` 走相同路線 —— 純 HTML 折疊卡片
（``<details>``/``<summary>``），搭配 ``custom_css.py`` 裡的
``.classic-card`` / ``.tutorial-*`` 樣式，維持與 App 其他頁面一致的
暗色古典美學，而不使用 ``st.expander``（避免視覺風格不統一）。
"""

from __future__ import annotations

import re
from html import escape as _esc

# 「看盤要領」原始文件（docs/tutorial.md）以 `## 《標題》` 分節，
# 這裡把六篇古文重新分組為四個主題，貼近實務看盤流程。
GROUPS: list[dict] = [
    {
        "id": "concept",
        "icon": "📜",
        "title": "基本概念",
        "desc": "太乙神數的核心命題與筭數原理，是看懂全局的起手式。",
        "sections": [
            {"title": "《太乙四計用法》", "kind": "pills"},
            {"title": "《主客筭數要義》", "kind": "list"},
        ],
    },
    {
        "id": "watch",
        "icon": "🔍",
        "title": "重點觀察",
        "desc": "起局之後，優先檢視這些吉凶樞紐，藉以判斷全局大勢。",
        "sections": [
            {"title": "《格局分析》", "kind": "terms"},
        ],
    },
    {
        "id": "pattern",
        "icon": "⚖️",
        "title": "常見格局與口訣",
        "desc": "門具、五將發等經典占驗口訣，用以推算勝負與時機。",
        "sections": [
            {"title": "《太乙行兵主客勝負占》", "kind": "prose"},
            {"title": "《金鏡捷法小淘金歌》", "kind": "prose"},
        ],
    },
    {
        "id": "classics",
        "icon": "📖",
        "title": "進階典籍",
        "desc": "《太乙金鏡七十二局賦》全文收錄，供深入研究者細細參詳。",
        "sections": [
            {"title": "《太乙金鏡七十二局賦》", "kind": "prose", "collapsed": True},
        ],
    },
]

_HEADER_RE = re.compile(r"^##\s*(《.+?》)\s*$", re.MULTILINE)
_ANCHOR_RE = re.compile(r"<a\s+name=.*?</a>", re.DOTALL | re.IGNORECASE)
_BACKLINK_RE = re.compile(r'<p\s+align="right">.*?</p>', re.DOTALL | re.IGNORECASE)
_HR_RE = re.compile(r"^-{3,}\s*$", re.MULTILINE)
_TERM_SEP_RE = re.compile(r"[:：︰]")


def _parse_sections(md_text: str) -> dict[str, str]:
    """把 tutorial.md 依 `## 《標題》` 切段，回傳 {標題: 內文}。"""
    matches = list(_HEADER_RE.finditer(md_text))
    sections: dict[str, str] = {}
    for i, m in enumerate(matches):
        title = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md_text)
        body = md_text[start:end]
        body = _ANCHOR_RE.sub("", body)
        body = _BACKLINK_RE.sub("", body)
        body = _HR_RE.sub("", body)
        sections[title] = body.strip()
    return sections


def _paragraphs(body: str) -> list[str]:
    """依空行切成段落，並去除每段內多餘的前後空白。"""
    raw_paras = re.split(r"\n\s*\n", body.strip())
    result = []
    for p in raw_paras:
        p = p.strip()
        if p:
            result.append(p)
    return result


def _render_prose(body: str) -> str:
    parts = []
    for para in _paragraphs(body):
        lines = [_esc(line.strip()) for line in para.splitlines() if line.strip()]
        parts.append(f'<p>{"<br>".join(lines)}</p>')
    return '<div class="tutorial-prose">' + "".join(parts) + "</div>"


def _render_pills(body: str) -> str:
    items = _paragraphs(body)
    pills = "".join(f'<span class="tutorial-pill">{_esc(p)}</span>' for p in items)
    return f'<div class="tutorial-pill-grid">{pills}</div>'


def _render_list(body: str) -> str:
    items = _paragraphs(body)
    lis = "".join(
        f'<li><span class="tutorial-list-mark">✦</span>{_esc(p)}</li>' for p in items
    )
    return f'<ul class="tutorial-highlight-list">{lis}</ul>'


def _parse_terms(body: str) -> list[tuple[str, str]]:
    """解析『格局分析』的編號列表，合併縮排延續行，回傳 (術語, 說明) 清單。"""
    items: list[dict] = []
    current: dict | None = None
    for raw_line in body.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue
        m = re.match(r"^\s*(\d+)\.\s*(.+)$", line)
        if m:
            if current is not None:
                items.append(current)
            current = {"text": m.group(2).strip()}
        elif current is not None:
            current["text"] += " " + line.strip()
    if current is not None:
        items.append(current)

    parsed: list[tuple[str, str]] = []
    for it in items:
        text = it["text"]
        sep = _TERM_SEP_RE.search(text)
        if sep:
            term = text[: sep.start()].strip()
            desc = text[sep.end() :].strip()
        else:
            term, desc = text, ""
        parsed.append((term, desc))
    return parsed


def _render_terms(body: str) -> str:
    cards = []
    for term, desc in _parse_terms(body):
        cards.append(
            '<div class="tutorial-term-card">'
            f'<div class="tutorial-term-name">{_esc(term)}</div>'
            f'<div class="tutorial-term-desc">{_esc(desc)}</div>'
            "</div>"
        )
    return f'<div class="tutorial-term-grid">{"".join(cards)}</div>'


_RENDERERS = {
    "prose": _render_prose,
    "pills": _render_pills,
    "list": _render_list,
    "terms": _render_terms,
}


def _card(title: str, body_html: str, *, collapsed: bool = False) -> str:
    open_attr = "" if collapsed else " open"
    return f"""
<details class="classic-card tutorial-card"{open_attr}>
  <summary class="classic-card-header">
    <span class="classic-card-title">{_esc(title)}</span>
  </summary>
  <div class="classic-card-body">
    {body_html}
  </div>
</details>"""


def render_tutorial_guide(md_text: str) -> str:
    """把 docs/tutorial.md 轉為「看盤要領」頁面完整 HTML（含導覽、分組卡片）。"""
    sections = _parse_sections(md_text)

    toc_pills = "".join(
        f'<a class="tutorial-toc-pill" href="#tutorial-{g["id"]}">'
        f'{g["icon"]} {_esc(g["title"])}</a>'
        for g in GROUPS
    )

    html_parts = [
        '<div class="tutorial-guide-container">',
        '  <div class="tutorial-guide-header">',
        "    <h2>🚀 看盤要領</h2>",
        '    <div class="tutorial-guide-ornament">✦ ❖ ✦</div>',
        '    <p class="tutorial-guide-subtitle">太乙神數排盤解讀指南 —— 由淺入深，掌握主客勝負之機</p>',
        "  </div>",
        f'  <div class="tutorial-toc">{toc_pills}</div>',
    ]

    for g in GROUPS:
        html_parts.append(f'  <div class="tutorial-group" id="tutorial-{g["id"]}">')
        html_parts.append('    <div class="tutorial-group-header">')
        html_parts.append(f'      <span class="tutorial-group-icon">{g["icon"]}</span>')
        html_parts.append(
            f'      <span class="tutorial-group-title">{_esc(g["title"])}</span>'
        )
        html_parts.append("    </div>")
        html_parts.append(f'    <p class="tutorial-group-desc">{_esc(g["desc"])}</p>')
        for sec in g["sections"]:
            title = sec["title"]
            body = sections.get(title, "")
            renderer = _RENDERERS[sec["kind"]]
            body_html = renderer(body)
            html_parts.append(_card(title, body_html, collapsed=sec.get("collapsed", False)))
        html_parts.append("  </div>")

    html_parts.append("</div>")
    return "\n".join(html_parts)
