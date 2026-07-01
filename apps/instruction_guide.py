"""使用說明：把 docs/instruction.md 的條列步驟轉為分步指南卡片。

與 ``tutorial_guide.py`` 走相同路線 —— 純 HTML 卡片，搭配
``custom_css.py`` 裡的 ``.instruction-*`` 樣式，維持與 App 其他頁面
一致的暗色古典美學。
"""

from __future__ import annotations

import re
from html import escape as _esc

_STEP_RE = re.compile(r"^(\d+)\.\s*(.+)$")


def _parse_steps(md_text: str) -> list[str]:
    """解析編號條列步驟，回傳步驟文字清單（保持原文順序）。"""
    steps: list[str] = []
    for raw_line in md_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        m = _STEP_RE.match(line)
        if m:
            steps.append(m.group(2).strip())
        elif steps:
            # 延續前一步驟的換行內容
            steps[-1] += " " + line
    return steps


def _render_step(idx: int, text: str, *, is_last: bool) -> str:
    line_cls = "" if is_last else " instruction-step-line"
    return (
        f'<div class="instruction-step{line_cls}">'
        f'<div class="instruction-step-badge">{idx}</div>'
        '<div class="instruction-step-body">'
        f'<p class="instruction-step-text">{_esc(text)}</p>'
        "</div>"
        "</div>"
    )


def render_instruction_guide(md_text: str) -> str:
    """把 docs/instruction.md 轉為「使用說明」頁面完整 HTML。"""
    steps = _parse_steps(md_text)

    html_parts = [
        '<div class="instruction-guide-container">',
        '  <div class="instruction-guide-header">',
        "    <h2>💬 使用說明</h2>",
        '    <div class="instruction-guide-ornament">✦ ❖ ✦</div>',
        '    <p class="instruction-guide-subtitle">五分鐘上手太乙排盤</p>',
        "  </div>",
        '  <div class="instruction-step-list">',
    ]
    for i, step in enumerate(steps, start=1):
        html_parts.append(_render_step(i, step, is_last=(i == len(steps))))
    html_parts.append("  </div>")
    html_parts.append("</div>")
    return "\n".join(html_parts)
