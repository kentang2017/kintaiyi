"""十二運時間軸 + 運勢卡片 HTML 組件。

Phase 1 實作：純 HTML/CSS，不含 JS。
在排盤與完整參數之下、解釋展開區之上，顯示統運入卦的時間流動感。
"""

from __future__ import annotations

from html import escape as _esc

from kintaiyi import config

# ── 十二運 CSS 色變數索引 ──────────────────────────────
_YUN_COLORS = [
    "--yun-1",  "--yun-2",  "--yun-3",  "--yun-4",
    "--yun-5",  "--yun-6",  "--yun-7",  "--yun-8",
    "--yun-9",  "--yun-10", "--yun-11", "--yun-12",
]

# ── 爻位吉凶 badge ────────────────────────────────────
_JI_BADGE: dict[int, tuple[str, str]] = {
    1: ("yun-ji-fu",    "建功立德"),
    2: ("yun-ji-ji",    "安平之限"),
    3: ("yun-ji-xiong", "內極災變"),
    4: ("yun-ji-xiong", "待治之限"),
    5: ("yun-ji-zai",   "君弱臣強"),
    6: ("yun-ji-zai",   "外極災變"),
}


def _yun_css_var(yun_name: str) -> str:
    """由運名找 CSS 色變數。"""
    for i, (yun, *_rest) in enumerate(config._TONGYUN_YUN_DEF):
        if yun == yun_name:
            return _YUN_COLORS[i] if i < len(_YUN_COLORS) else "--yun-2"
    return "--yun-2"


def _current_segment(rugua: dict) -> dict:
    """由 rugua 找當前 segment。"""
    pos = rugua.get("週期位置", 0)
    for s in config._TONGYUN_SEGMENTS:
        if s["週期起"] <= pos < s["週期迄"]:
            return s
    return config._TONGYUN_SEGMENTS[-1]


def _yun_index(yun_name: str) -> int:
    """由運名找在 _TONGYUN_YUN_DEF 中的索引。"""
    for i, (yun, *_rest) in enumerate(config._TONGYUN_YUN_DEF):
        if yun == yun_name:
            return i
    return 1


# ── 主入口 ────────────────────────────────────────────

def render_yun_section(
    results: dict,
    *,
    t,
) -> str:
    """渲染整個統運時間軸區塊的 HTML。

    Parameters
    ----------
    results : dict
        排盤結果（pan() 返回值），需包含 ``"ttext"``。
    t : callable
        i18n 翻譯函數。

    Returns
    -------
    str
        完整的 ``<section class="yun-section">…</section>`` HTML。
    """
    from kintaiyi.tongyun_display import apply_tongyun_query

    ty = results.get("ty")
    if ty is None:
        return ""

    # 同步統運查詢年（與 streamlit_app 邏輯一致）
    sync = st_session_get("tongyun_sync_chart", True)
    query_year = int(ty.year) if sync else int(st_session_get("tongyun_query_year", ty.year))

    base_ttext = results.get("ttext") or {}
    if query_year != int(ty.year):
        ttext = apply_tongyun_query(base_ttext, query_year, ty.year, month=ty.month, day=ty.day)
    else:
        ttext = base_ttext

    v12 = ttext.get("卷十二") or {}
    v13 = ttext.get("卷十三") or {}
    v14 = ttext.get("卷十四") or {}
    rugua = v12.get("統運入卦") or {}
    if not rugua:
        return ""

    huofu = v12.get("入爻禍福") or {}
    shier_yun = v12.get("十二運立成") or {}

    parts: list[str] = []

    # 統運查詢年提示
    if query_year != int(ty.year):
        parts.append(
            f'<div class="yun-query-note">{_esc(t("tongyun_query_note").format(query=query_year, chart=ty.year))}</div>'
        )

    # 時間軸
    parts.append(_render_timeline(rugua, shier_yun, t=t))

    # 當前運勢卡片
    parts.append(_render_current_card(rugua, huofu, t=t))

    # 折疊子卡片
    parts.append(_render_sub_cards(v12, v13, v14, rugua, t=t))

    # 歷史對照（簡要）
    parts.append(_render_history_compare(query_year, t=t))

    inner = "\n".join(parts)
    return f'<section class="yun-section">{inner}</section>'


# ── 內部渲染函數 ──────────────────────────────────────

def _render_timeline(rugua: dict, shier_yun: dict, *, t) -> str:
    """十二運時間軸。"""
    twelve = shier_yun.get("十二運", [])
    if not twelve:
        # fallback: 從 _TONGYUN_YUN_DEF 構建
        twelve = config.tongyun_shier_yun().get("十二運", [])

    current_idx = _yun_index(rugua.get("運", ""))
    seg = _current_segment(rugua)
    elapsed = rugua.get("週期位置", 0) - seg["週期起"]
    seg_total = seg["年數"]
    pct = min(100, max(0, int(elapsed / max(1, seg_total) * 100)))

    segs_html: list[str] = []
    for i, row in enumerate(twelve):
        is_current = i == current_idx
        css_var = _YUN_COLORS[i] if i < len(_YUN_COLORS) else "--yun-2"
        flex = row.get("總年", 100)
        cls = "yun-timeline-seg"
        if is_current:
            cls += " yun-current"
        name = _esc(row.get("運", ""))
        years = row.get("總年", 0)
        marker = '<span class="yun-timeline-marker"></span>' if is_current else ""
        segs_html.append(
            f'<button class="{cls}" data-yun-idx="{i}" '
            f'style="flex-grow: {flex}; --yun-color: var({css_var});" '
            f'type="button">'
            f'<span class="yun-timeline-seg-name">{name}</span>'
            f'<span class="yun-timeline-seg-years">{years}年</span>'
            f"{marker}"
            f"</button>"
        )

    cycle_num = rugua.get("週期序", "—")
    big_week = shier_yun.get("大週", config._TONGYUN_CYCLE)

    return f"""
<div class="yun-timeline-container">
  <div class="yun-timeline-header">
    <span class="yun-timeline-label">{_esc(t("yun_timeline_label"))}
      <span class="yun-cycle-num">{cycle_num}</span>
    </span>
    <span class="yun-timeline-sub">{big_week} {_esc(t("yun_per_cycle"))}</span>
  </div>
  <div class="yun-timeline-track">
    {"".join(segs_html)}
  </div>
  <div class="yun-timeline-progress">
    <div class="yun-timeline-progress-bar" style="width: {pct}%">
    </div>
  </div>
</div>"""


def _render_current_card(rugua: dict, huofu: dict, *, t) -> str:
    """當前運勢卡片。"""
    css_var = _yun_css_var(rugua.get("運", ""))
    yao_idx = rugua.get("爻", 1)
    ji_class, ji_label = _JI_BADGE.get(yao_idx, ("yun-ji-fu", "—"))

    gua_name = _esc(rugua.get("卦", "—"))
    gua_symbol = _esc(rugua.get("卦符", ""))
    yao_name = _esc(rugua.get("爻名", ""))
    ru_gua_year = rugua.get("入卦年數", "—")
    ru_yao_year = rugua.get("入爻年數", "—")
    ce = rugua.get("爻策", "—")
    zhou = rugua.get("週期序", "—")

    duan_raw = huofu.get("所主") or rugua.get("斷語", "") or ""
    duan_short = duan_raw.split("；")[0] if duan_raw else ""
    duan_full = duan_raw
    yaoju = huofu.get("要訣", "") or ""
    if yaoju and yaoju not in duan_full:
        duan_full = f"{duan_full}。{yaoju}"

    seg = _current_segment(rugua)
    elapsed = rugua.get("週期位置", 0) - seg["週期起"]
    seg_total = seg["年數"]
    pct = min(100, max(0, int(elapsed / max(1, seg_total) * 100)))

    # 當前運中的卦序
    yun_name = rugua.get("運", "")
    yun_segs = [s for s in config._TONGYUN_SEGMENTS if s["運"] == yun_name]
    gua_names = [s["卦"] for s in yun_segs]
    current_gua = rugua.get("卦", "")
    gua_seq_html = ""
    if gua_names:
        items = []
        for g in gua_names:
            is_cur = g == current_gua
            cls = "yun-card-gua-seq-item yun-card-gua-seq-current" if is_cur else "yun-card-gua-seq-item"
            items.append(f'<span class="{cls}">{_esc(g)}</span>')
        gua_seq_html = f'<div class="yun-card-gua-seq">{"".join(items)}</div>'

    return f"""
<article class="yun-card yun-card--current" style="--yun-color: var({css_var});">
  <div class="yun-card-header">
    <span class="yun-card-yun-name">{_esc(yun_name)}</span>
    <span class="yun-card-ji-badge {ji_class}"><span class="yun-ji-dot"></span>{_esc(ji_label)}</span>
  </div>
  <div class="yun-card-body">
    <div class="yun-card-gua">
      <span class="yun-card-gua-symbol">{gua_symbol}</span>
      <span class="yun-card-gua-name">{gua_name}</span>
    </div>
    <div class="yun-card-info">
      <div class="yun-card-yao">{yao_name} · {_esc(t("yun_yao_year"))} {ru_yao_year} {_esc(t("yun_years"))}</div>
      <div class="yun-card-meta">
        <span>{_esc(t("yun_gua_year"))} {ru_gua_year} {_esc(t("yun_years"))}</span>
        <span>{_esc(t("yun_ce"))} {ce}</span>
        <span>{_esc(t("yun_cycle"))} {zhou}</span>
      </div>
      <div class="yun-card-duan">{_esc(duan_short)}</div>
      {gua_seq_html}
    </div>
  </div>
  <div class="yun-card-progress">
    <div class="yun-card-progress-fill" style="width: {pct}%;"></div>
  </div>
  <details class="yun-card-details">
    <summary>{_esc(t("yun_expand_huofu"))}</summary>
    <p class="yun-card-details-body">{_esc(duan_full)}</p>
  </details>
</article>"""


def _render_sub_cards(v12: dict, v13: dict, v14: dict, rugua: dict, *, t) -> str:
    """流年直卦、變卦納甲、卦象觀象等折疊子卡片。"""
    cards: list[str] = []

    # ── 流年直卦 ──
    lz = v12.get("流年直卦") or {}
    if lz.get("直卦"):
        gz = _esc(lz.get("干支", ""))
        gua = _esc(lz.get("直卦", ""))
        sym = _esc(lz.get("卦符", ""))
        yao = _esc(lz.get("爻名", ""))
        mff = _esc(lz.get("命爻法", ""))
        yj = _esc(lz.get("要訣", ""))
        cards.append(f"""
<details class="yun-sub-card">
  <summary class="yun-sub-card-header">
    <span class="yun-sub-card-title">{_esc(t("liunian_zhigua"))}</span>
    <span class="yun-sub-card-preview">{gz} · {gua} {sym} · {yao}</span>
  </summary>
  <div class="yun-sub-card-body">
    <p>{_esc(t("yun_ganzhi"))}：{gz}{_esc(t("yun_year_suffix"))}</p>
    <p>{_esc(t("yun_zhigua"))}：{gua} {sym} · {yao}{_esc(t("yun_yao_suffix"))}</p>
    <p>{_esc(t("yun_mff"))}：{mff}</p>
    <p class="yun-sub-card-note">{yj}</p>
  </div>
</details>""")

    # ── 變卦納甲 ──
    bg = v12.get("變卦納甲") or {}
    if bg.get("變卦"):
        ben = _esc(bg.get("本卦", ""))
        bian = _esc(bg.get("變卦", ""))
        dy = _esc(bg.get("爻名", ""))
        nj = bg.get("納甲", {}) or {}
        nj_str = _esc(nj.get("納甲", ""))
        nw = _esc(nj.get("內外", ""))
        bg8 = _esc(nj.get("八卦", ""))
        fang = _esc(nj.get("方位", ""))
        zhi_fy = _esc(nj.get("地支分野", ""))
        gan_fy = _esc(nj.get("天干分野", ""))
        cards.append(f"""
<details class="yun-sub-card">
  <summary class="yun-sub-card-header">
    <span class="yun-sub-card-title">{_esc(t("bian_gua_najia"))}</span>
    <span class="yun-sub-card-preview">{ben} → {bian}</span>
  </summary>
  <div class="yun-sub-card-body">
    <p>{_esc(t("yun_ben_bian"))}：{ben} → {bian}（{_esc(t("yun_dong_yao"))}{dy}）</p>
    <p>{_esc(t("yun_najia"))}：{nj_str} · {nw} · {bg8}</p>
    <p>{_esc(t("yun_fangwei"))}：{fang}；{_esc(t("yun_fenye"))}：{zhi_fy}；{gan_fy}</p>
  </div>
</details>""")

    # ── 卦象觀象 ──
    gx = v13.get("統運卦象") or {}
    full = v13.get("卦象全文") or {}
    if gx.get("卦"):
        xiang = gx.get("象曰", "") or ""
        xiang_preview = xiang[:36] + "…" if len(xiang) > 36 else xiang
        yao_obs = gx.get("當前爻觀象", "")
        yao_observations = full.get("爻觀象", {}) or {}
        current_yao = gx.get("爻", 0)
        yao_list_html = ""
        for yi in sorted(yao_observations.keys()):
            cls = "yun-gua-yao-item"
            if yi == current_yao:
                cls += " yun-gua-yao-current"
            elif yi <= current_yao:
                cls += " yun-gua-yao-active"
            yao_list_html += (
                f'<div class="{cls}">'
                f'<span class="yun-gua-yao-idx">{yi}</span>'
                f'<span class="yun-gua-yao-text">{_esc(yao_observations[yi])}</span>'
                f"</div>"
            )
        cards.append(f"""
<details class="yun-sub-card">
  <summary class="yun-sub-card-header">
    <span class="yun-sub-card-title">{_esc(t("gua_xiang"))}</span>
    <span class="yun-sub-card-preview">{_esc(gx.get("卦", ""))} · {_esc(xiang_preview)}</span>
  </summary>
  <div class="yun-sub-card-body">
    <p class="yun-gua-xiang">{_esc(t("yun_xiang_yue"))}：{_esc(xiang)}</p>
    <p class="yun-gua-yao-current-line">▶ {_esc(t("yun_yao_guanxiang"))}（{_esc(gx.get("爻名", ""))}）：{_esc(yao_obs)}</p>
    {f'<div class="yun-gua-yao-list">{yao_list_html}</div>' if yao_list_html else ""}
  </div>
</details>""")

    # ── 行支編年 ──
    hz = (v14.get("行支編年") or {}) if v14 else {}
    exact = hz.get("當年例", []) if hz else []
    tip14 = v14.get("要訣", "") if v14 else ""
    if exact:
        e = exact[0]
        cards.append(f"""
<details class="yun-sub-card">
  <summary class="yun-sub-card-header">
    <span class="yun-sub-card-title">{_esc(t("hangzhi_biannian"))}</span>
    <span class="yun-sub-card-preview">{_esc(e.get("紀年", ""))} · {_esc(e.get("卦", ""))}{_esc(e.get("爻", ""))}</span>
  </summary>
  <div class="yun-sub-card-body">
    <p>{_esc(e.get("紀年", ""))}（{e.get("年", "—")}）</p>
    <p>{_esc(e.get("運", ""))}·{_esc(e.get("卦", ""))}{_esc(e.get("爻", ""))}</p>
    <p>{_esc(e.get("摘要", ""))}</p>
  </div>
</details>""")
    elif tip14:
        cards.append(f"""
<details class="yun-sub-card">
  <summary class="yun-sub-card-header">
    <span class="yun-sub-card-title">{_esc(t("hangzhi_biannian"))}</span>
    <span class="yun-sub-card-preview">{_esc(tip14[:24])}…</span>
  </summary>
  <div class="yun-sub-card-body">
    <p>{_esc(tip14)}</p>
  </div>
</details>""")

    # ── 災厄首尾 ──
    sw = v12.get("災厄首尾") or {}
    if sw.get("是否首尾") or sw.get("首尾標記"):
        flags = "、".join(sw.get("首尾標記", []) or [])
        if flags:
            cards.append(f"""
<details class="yun-sub-card">
  <summary class="yun-sub-card-header">
    <span class="yun-sub-card-title">{_esc(t("shouwei"))}</span>
    <span class="yun-sub-card-preview">{_esc(flags)}</span>
  </summary>
  <div class="yun-sub-card-body">
    <p>{_esc(sw.get("斷語", ""))}</p>
    <p class="yun-sub-card-note">{_esc(sw.get("要訣", ""))}</p>
  </div>
</details>""")

    # ── 觀象期十二月直事 ──
    gqx = v12.get("觀象期") or {}
    months = gqx.get("十二月直事") or []
    if months:
        month_items = []
        for m in months:
            is_first_half = m.get("階段") == "本卦"
            cls = "yun-month-item" + (" yun-month-ben" if is_first_half else " yun-month-bian")
            month_items.append(
                f'<span class="{cls}">'
                f'<span class="yun-month-seq">{m.get("月序", "")}</span>'
                f'<span class="yun-month-gua">{_esc(m.get("卦", ""))}</span>'
                f'<span class="yun-month-yao">{_esc(m.get("爻名", ""))}</span>'
                f"</span>"
            )
        month_inner = "\n".join(month_items)
        cards.append(f"""
<details class="yun-sub-card">
  <summary class="yun-sub-card-header">
    <span class="yun-sub-card-title">{_esc(t("tongyun_extended"))}</span>
    <span class="yun-sub-card-preview">{_esc(gqx.get("本卦", ""))} / {_esc(gqx.get("變卦", ""))}</span>
  </summary>
  <div class="yun-sub-card-body">
    <p class="yun-sub-card-note">{_esc(gqx.get("要訣", ""))}</p>
    <div class="yun-month-grid">{month_inner}</div>
  </div>
</details>""")

    return "".join(cards)


def _render_history_compare(query_year: int, *, t) -> str:
    """歷史驗例簡要。"""
    from kintaiyi.tongyun_display import historical_compare

    compare = historical_compare(query_year)
    rugua = compare.get("統運入卦") or {}
    exact = compare.get("當年例") or []
    same = compare.get("同卦爻例") or []

    if not exact and not same:
        return ""

    items: list[str] = []
    for item in exact[:3]:
        items.append(
            f'<div class="yun-hist-item yun-hist-exact">'
            f'<span class="yun-hist-year">{_esc(item.get("紀年", ""))}（{item.get("年", "")}）</span>'
            f'<span class="yun-hist-gua">{_esc(item.get("運", ""))}·{_esc(item.get("卦", ""))}{_esc(item.get("爻", ""))}</span>'
            f'<span class="yun-hist-summary">{_esc(item.get("摘要", ""))}</span>'
            f"</div>"
        )
    for item in same[:3]:
        if item.get("年") == query_year:
            continue
        items.append(
            f'<div class="yun-hist-item">'
            f'<span class="yun-hist-year">{_esc(item.get("紀年", ""))}（{item.get("年", "")}）</span>'
            f'<span class="yun-hist-gua">{_esc(item.get("運", ""))}·{_esc(item.get("卦", ""))}{_esc(item.get("爻", ""))}</span>'
            f'<span class="yun-hist-summary">{_esc(item.get("摘要", ""))}</span>'
            f"</div>"
        )

    if not items:
        return ""

    label = t("tongyun_history_compare")
    return f"""
<details class="yun-sub-card yun-hist-card">
  <summary class="yun-sub-card-header">
    <span class="yun-sub-card-title">{_esc(label)}</span>
    <span class="yun-sub-card-preview">{_esc(rugua.get("運", "—"))}·{_esc(rugua.get("卦", "—"))}{_esc(rugua.get("爻名", ""))}</span>
  </summary>
  <div class="yun-sub-card-body">
    {"".join(items)}
  </div>
</details>"""


# ── 輔助：安全讀取 session_state ──────────────────────

def st_session_get(key: str, default=None):
    """安全讀取 st.session_state，避免在非 Streamlit 環境報錯。"""
    try:
        import streamlit as st
        return st.session_state.get(key, default)
    except Exception:
        return default