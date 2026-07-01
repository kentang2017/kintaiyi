"""連結：把 docs/contact.md（開發者資訊、同系列應用連結）轉為金色卡片列表。

與 ``tutorial_guide.py`` 走相同路線 —— 純 HTML 卡片，搭配
``custom_css.py`` 裡的 ``.links-*`` 樣式，維持與 App 其他頁面一致的
暗色古典美學。
"""

from __future__ import annotations

import re
from html import escape as _esc

_APP_LINK_RE = re.compile(
    r'<a\s+href="([^"]+)"\s*>\s*<img\s+src="([^"]+)"[^>]*>\s*</a>', re.IGNORECASE
)
_BARE_IMG_RE = re.compile(r'<img\s+src="([^"]+)"[^>]*>', re.IGNORECASE)
_TAG_RE = re.compile(r"<[^>]+>")
_H1_RE = re.compile(r"^#\s*(.+)$", re.MULTILINE)


def _hostname_title(url: str) -> str:
    m = re.search(r"https?://([^/]+)", url)
    host = m.group(1) if m else url
    name = host.split(".")[0]
    return name


def _contact_icon(line: str) -> str:
    if "微信" in line:
        return "💬"
    if "QQ" in line.upper():
        return "👥"
    return "📮"


def render_links_page(md_text: str) -> str:
    """把 docs/contact.md 轉為「連結」頁面完整 HTML。"""
    subtitle_match = _H1_RE.search(md_text)
    subtitle = subtitle_match.group(1).strip() if subtitle_match else "開發者資訊與同系列應用"

    app_links = _APP_LINK_RE.findall(md_text)
    remaining = _APP_LINK_RE.sub("", md_text)

    # 取出未被 <a> 包住的獨立圖片（如聯絡用 QR code）
    bare_images = _BARE_IMG_RE.findall(remaining)
    remaining = _BARE_IMG_RE.sub("", remaining)

    # 移除殘餘 HTML 標籤（<p align...>、</p> 等），保留純文字行
    remaining = _TAG_RE.sub("", remaining)
    remaining = _H1_RE.sub("", remaining)
    text_lines = [ln.strip() for ln in remaining.splitlines() if ln.strip()]

    html_parts = [
        '<div class="links-guide-container">',
        '  <div class="links-guide-header">',
        "    <h2>🔗 相關連結</h2>",
        '    <div class="links-guide-ornament">✦ ❖ ✦</div>',
        f'    <p class="links-guide-subtitle">{_esc(subtitle)}</p>',
        "  </div>",
    ]

    if app_links:
        html_parts.append('  <div class="links-app-grid">')
        for href, img_src in app_links:
            title = _hostname_title(href)
            html_parts.append(
                f'<a class="links-app-card" href="{_esc(href)}" target="_blank" '
                'rel="noopener noreferrer">'
                f'<img class="links-app-icon" src="{_esc(img_src)}" alt="{_esc(title)}">'
                '<div class="links-app-info">'
                f'<span class="links-app-title">{_esc(title)}</span>'
                '<span class="links-app-desc">同系列 streamlit 應用</span>'
                "</div>"
                "</a>"
            )
        html_parts.append("  </div>")

    if text_lines or bare_images:
        html_parts.append('<details class="classic-card links-contact-card" open>')
        html_parts.append('  <summary class="classic-card-header">')
        html_parts.append('    <span class="classic-card-title">📮 聯絡方式</span>')
        html_parts.append("  </summary>")
        html_parts.append('  <div class="classic-card-body">')
        if text_lines:
            html_parts.append('    <ul class="links-contact-list">')
            for line in text_lines:
                icon = _contact_icon(line)
                html_parts.append(
                    f'      <li><span class="links-contact-icon">{icon}</span>'
                    f"{_esc(line)}</li>"
                )
            html_parts.append("    </ul>")
        for img_src in bare_images:
            html_parts.append(
                f'    <img class="links-contact-image" src="{_esc(img_src)}" alt="聯絡資訊">'
            )
        html_parts.append("  </div>")
        html_parts.append("</details>")

    html_parts.append("</div>")
    return "\n".join(html_parts)
