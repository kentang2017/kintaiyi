"""局數史例：可點擊的橫向歷史節點時間軸。

與 ``yun_timeline.py`` 同樣走「純 HTML 視覺 + Streamlit 原生互動」路線，
差別在於本模組需要真正接收使用者點擊並驅動 rerun（不只是被動顯示目前狀態），
因此節點本體採用 ``st.button``，並用 CSS 把按鈕外觀改造成金色時間軸節點，
而非額外疊加一層不可互動的純 HTML（避免兩層節點不同步的風險）。
"""

from __future__ import annotations

import streamlit as st

SESSION_KEY_DEFAULT = "history_selected_idx"


def format_year_label(year: int) -> str:
    """把西元年轉為顯示用文字，公元前以「前」字標示。"""
    year = int(year)
    if year < 0:
        return f"前{abs(year)}"
    return str(year)


def render_history_timeline(
    events: list[dict],
    *,
    t,
    key: str = SESSION_KEY_DEFAULT,
) -> int | None:
    """渲染橫向可捲動的歷史節點時間軸，回傳目前選取的事件索引（或 None）。

    Parameters
    ----------
    events : list[dict]
        歷史事件資料（見 ``history_examples.HISTORY_EVENTS``）。
    t : callable
        i18n 翻譯函數。
    key : str
        用於 ``st.session_state`` 保存目前選取索引的鍵名。

    Returns
    -------
    int | None
        目前選取的事件在 ``events`` 中的索引；尚未選取時為 ``None``。
    """
    if not events:
        return None

    st.markdown(
        f'<div class="history-timeline-title">'
        f'<span class="history-timeline-title-icon">📜</span>'
        f'<span class="history-timeline-title-text">{t("history_timeline_title")}</span>'
        f'<span class="history-timeline-title-hint">{t("history_timeline_hint")}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="history-timeline-wrap">', unsafe_allow_html=True)

    selected_idx = st.session_state.get(key)
    cols = st.columns(len(events), gap="small")
    for i, (col, event) in enumerate(zip(cols, events, strict=True)):
        with col:
            if i == 0:
                st.markdown(
                    '<div class="history-timeline-marker" aria-hidden="true"></div>',
                    unsafe_allow_html=True,
                )
            is_selected = selected_idx == i
            label = format_year_label(event.get("year", 0))
            btn_type = "primary" if is_selected else "secondary"
            clicked = st.button(
                label,
                key=f"history_node_{i}",
                help=event.get("headline", ""),
                type=btn_type,
                width="stretch",
            )
            if clicked:
                st.session_state[key] = i
                selected_idx = i
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    if selected_idx is not None and 0 <= selected_idx < len(events):
        return selected_idx
    return None
