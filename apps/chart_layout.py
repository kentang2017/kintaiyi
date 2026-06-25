"""Chart area layout: desktop side panel and mobile print-meta overlay on chart stage."""

from __future__ import annotations

import re
from html import escape as html_escape

import streamlit as st

from kintaiyi import config, jieqi

THREE_FIVE_PREVIEW_LEN = 96
THREE_FIVE_KEYWORD_LEN = 48


def _gz_pillars(gz: str) -> list[tuple[str, str]]:
    pillars: list[tuple[str, str]] = []
    for token in (gz or "").split():
        if len(token) < 2:
            continue
        label, value = token[-1], token[:-1]
        if label in "年月日時分" and value:
            pillars.append((label, value))
    return pillars


def _pillars_html(pillars: list[tuple[str, str]]) -> str:
    if not pillars:
        return ""
    return "".join(
        f'<span class="chart-meta-pillar">'
        f'<span class="chart-meta-pillar-label">{html_escape(label)}</span>'
        f'<span class="chart-meta-pillar-value">{html_escape(value)}</span>'
        f"</span>"
        for label, value in pillars
    )


def _truncate_text(text: str, max_len: int) -> tuple[str, bool]:
    text = (text or "").strip()
    if len(text) <= max_len:
        return text, False
    return text[:max_len].rstrip() + "…", True


def _three_five_keywords(raw: str) -> str:
    raw = (raw or "").strip()
    if not raw:
        return "—"
    chunks = re.split(r"[；;。\n]+", raw)
    bits = [c.strip() for c in chunks if c.strip()]
    if not bits:
        return _truncate_text(raw, THREE_FIVE_KEYWORD_LEN)[0]
    line = " · ".join(bits[:3])
    return _truncate_text(line, THREE_FIVE_KEYWORD_LEN)[0]


def _meta_secondary_lines(results: dict) -> tuple[str, str]:
    ty = results.get("ty")
    if ty is None:
        return (results.get("lunard") or "").strip(), ""
    date_line = " · ".join(
        b
        for b in [
            (results.get("lunard") or "").strip(),
            jieqi.jq(ty.year, ty.month, ty.day, ty.hour, ty.minute),
        ]
        if b
    )
    return date_line, (config.kingyear(ty.year) or "").strip()


def _bureau_year_name(results: dict) -> str:
    return ((results.get("ttext") or {}).get("局式", {}) or {}).get("年", "") or ""


def _format_bureau_line(
    results: dict,
    kook_text: str,
    *,
    t,
    is_life_chart: bool = False,
) -> str:
    """e.g. 陰遁六局 (五子元 陰遁七十八局) 理人"""
    primary = (kook_text or (results.get("kook") or {}).get("文", "") or "").strip() or "—"
    bureau_year = _bureau_year_name(results).strip()
    wuyuan = (results.get("wuyuan") or "").strip()
    parts = [primary]

    if wuyuan and not is_life_chart:
        parts.append(f"({t('five_yuan_short')} {wuyuan})")
    elif is_life_chart and bureau_year:
        parts.append(f"({bureau_year})")

    tail = bureau_year if not is_life_chart else ""
    if tail and tail not in primary and tail not in " ".join(parts):
        parts.append(tail)

    return " ".join(parts)


_SKIP_CHIP_LABELS = frozenset({
    "干支", "Stem-Branch",
    "農曆", "Lunar",
    "局式", "Bureau",
    "陰陽", "Yin/Yang",
    "五子元", "Five Cycles",
})


def _params_card_html(chart_meta: dict) -> str:
    chips = chart_meta.get("chips") or []
    rows = []
    for label, value in chips:
        label_s = str(label).strip()
        value_s = str(value).strip()
        if not value_s or label_s in _SKIP_CHIP_LABELS:
            continue
        rows.append(
            f'<div class="chart-meta-detail-row">'
            f'<span class="chart-meta-detail-label">{html_escape(label_s)}</span>'
            f'<span class="chart-meta-detail-value">{html_escape(value_s)}</span>'
            f"</div>"
        )
    if not rows:
        return ""
    return (
        f'<article class="grok-card-v2 chart-side-params">'
        f'<div class="chart-side-params-grid">{"".join(rows)}</div>'
        f"</article>"
    )


def build_chart_print_meta(
    results: dict,
    *,
    t,
    is_life_chart: bool = False,
    life_method_label: str = "",
) -> str:
    """Plain-text chart header (legacy print() format) for mobile overlay."""
    ty = results.get("ty")
    if ty is None:
        return ""
    year, month, day, hour, minute = ty.year, ty.month, ty.day, ty.hour, ty.minute
    ttext = results.get("ttext") or {}
    lines: list[str] = []

    if is_life_chart:
        sex_label = ty.taiyi_life(results.get("sex_o", "")).get("性別", "")
        lines.append(
            f"{config.gendatetime(year, month, day, hour, minute)} "
            f"{results.get('zhao', '')} - {sex_label} - "
            f"{config.taiyi_name(0)[0]} - {ty.accnum(0, 0)} |"
        )
        lines.append(
            f"{t('lunar_label')}︰{results.get('lunard', '')} | "
            f"{jieqi.jq(year, month, day, hour, minute)} |"
        )
        lines.append(f"{results.get('gz', '')} |")
        lines.append(
            f"{life_method_label or t('taiyi_life_method')} - "
            f"{ty.kook(0, 0).get('文', '')} "
            f"({ttext.get('局式', {}).get('年', '')}) |"
        )
        lines.append(
            f"{t('epoch_label')}︰{ttext.get('紀元', '')} | "
            f"{t('home_calc')}︰{results.get('homecal', '')} "
            f"{t('away_calc')}︰{results.get('awaycal', '')} |"
        )
    else:
        style = results.get("style", 0)
        tn = results.get("tn", 0)
        method = f"{config.ty_method(tn)}{ttext.get('太乙計', '')}"
        lines.append(
            f"{config.gendatetime(year, month, day, hour, minute)} | "
            f"{t('acc_prefix')}{config.taiyi_name(style)[0]}{t('acc_suffix')}︰"
            f"{ty.accnum(style, tn)} |"
        )
        lines.append(
            f"{t('lunar_label')}︰{results.get('lunard', '')} | "
            f"{jieqi.jq(year, month, day, hour, minute)} |"
        )
        lines.append(f"{results.get('gz', '')} |")
        lines.append(
            f"{method} - {ty.kook(style, tn).get('文', '')} "
            f"({ttext.get('局式', {}).get('年', '')}) | "
            f"{t('five_yuan')}:{results.get('wuyuan', '')} |"
        )
        lines.append(
            f"{t('epoch_label')}︰{ttext.get('紀元', '')} | "
            f"{t('home_calc')}︰{results.get('homecal', '')} "
            f"{t('away_calc')}︰{results.get('awaycal', '')} "
            f"{t('set_calc')}︰{results.get('setcal', '')} |"
        )

    return "\n".join(lines)


def _build_chart_summary_context(
    chart_meta: dict,
    results: dict,
    *,
    t,
    is_life_chart: bool = False,
) -> dict:
    ty = results.get("ty")
    style = results.get("style", 0)
    tn = results.get("tn", 0)
    gz = results.get("gz", "")
    pillars = _gz_pillars(gz)
    secondary_date, secondary_king = _meta_secondary_lines(results)

    kook_text = ""
    if ty is not None:
        kook_style = results.get("plate_ji", style) if is_life_chart else style
        kook_tn = 0 if is_life_chart else tn
        kook_text = ty.kook(kook_style, kook_tn).get("文", "") or ""

    bureau_line = _format_bureau_line(
        results, kook_text, t=t, is_life_chart=is_life_chart,
    )

    three_five_raw = (results.get("three_door") or "") + (results.get("five_generals") or "")
    keywords = _three_five_keywords(three_five_raw)
    preview, truncated = _truncate_text(three_five_raw, THREE_FIVE_PREVIEW_LEN)

    if truncated:
        three_five_body = (
            f'<p class="grok-card-v2-lead">{html_escape(keywords)}</p>'
            f'<p class="grok-card-v2-body grok-card-v2-preview">{html_escape(preview)}</p>'
            f'<details class="grok-card-v2-details">'
            f'<summary>{html_escape(t("three_five_more"))}</summary>'
            f'<p class="grok-card-v2-body">{html_escape(three_five_raw)}</p>'
            f"</details>"
        )
    else:
        three_five_body = (
            f'<p class="grok-card-v2-lead">{html_escape(keywords)}</p>'
            f'<p class="grok-card-v2-body">{html_escape(preview or "—")}</p>'
        )

    return {
        "pillars": pillars,
        "gz": gz,
        "secondary_date": secondary_date,
        "secondary_king": secondary_king,
        "bureau_line": bureau_line,
        "three_five_body": three_five_body,
        "params_html": _params_card_html(chart_meta),
        "t": t,
    }


def _summary_articles_html(ctx: dict) -> str:
    t = ctx["t"]
    pillars_html = _pillars_html(ctx["pillars"]) or (
        f'<p class="grok-card-v2-body">{html_escape(ctx["gz"])}</p>'
    )
    secondary_html = (
        f'<p class="chart-meta-secondary">{html_escape(ctx["secondary_date"])}</p>'
    )
    if ctx["secondary_king"]:
        secondary_html += (
            f'<p class="chart-meta-secondary chart-meta-kingyear">'
            f'{html_escape(ctx["secondary_king"])}</p>'
        )

    parts = [
        f'<article class="grok-card-v2 chart-side-hero">',
        f'<p class="grok-card-v2-title">{html_escape(t("chart_summary"))}</p>',
        f'<div class="chart-meta-gz-row">{pillars_html}</div>',
        secondary_html,
        "</article>",
        f'<article class="grok-card-v2 grok-card-v2-bureau">',
        f'<p class="grok-card-v2-title">{html_escape(t("kook_label"))}</p>',
        f'<p class="grok-card-v2-value grok-card-v2-bureau-line">{html_escape(ctx["bureau_line"])}</p>',
        "</article>",
        f'<article class="grok-card-v2 grok-card-v2-three-five">',
        f'<p class="grok-card-v2-title">{html_escape(t("three_five"))}</p>',
        ctx["three_five_body"],
        "</article>",
    ]
    if ctx["params_html"]:
        parts.append(ctx["params_html"])
    return "".join(parts)


def render_chart_side_panel(
    chart_meta: dict,
    results: dict,
    *,
    t,
    is_life_chart: bool = False,
) -> None:
    """Chart summary in right column — visible on desktop only (CSS)."""
    ctx = _build_chart_summary_context(
        chart_meta, results, t=t, is_life_chart=is_life_chart,
    )
    st.markdown(
        f'<aside class="chart-side-panel chart-summary-desktop">'
        f"{_summary_articles_html(ctx)}"
        f"</aside>",
        unsafe_allow_html=True,
    )


def render_chart_mobile_params(
    chart_meta: dict,
    results: dict,
    *,
    t,
) -> None:
    """Mobile-only collapsible full parameters below chart."""
    chips = chart_meta.get("chips") or []
    three_five = ((results.get("three_door") or "") + (results.get("five_generals") or "")).strip()
    if not chips and not three_five:
        return

    st.markdown(
        '<span class="chart-mobile-params-anchor" aria-hidden="true"></span>',
        unsafe_allow_html=True,
    )
    epoch = ((results.get("ttext") or {}).get("紀元", "") or "").strip()
    with st.expander(t("chart_meta_detail"), expanded=False):
        param_rows: list[tuple[str, str]] = list(chips)
        if epoch:
            param_rows.append((t("epoch_label"), epoch))
        if param_rows:
            cols = st.columns(2, gap="small")
            for idx, (label, value) in enumerate(param_rows):
                with cols[idx % 2]:
                    st.markdown(
                        f'<div class="chart-meta-detail-row">'
                        f'<span class="chart-meta-detail-label">{html_escape(str(label))}</span>'
                        f'<span class="chart-meta-detail-value">{html_escape(str(value))}</span>'
                        f"</div>",
                        unsafe_allow_html=True,
                    )
        if three_five:
            st.markdown(
                f'<p class="chart-mobile-param-heading">{html_escape(t("three_five"))}</p>'
                f'<p class="chart-mobile-param-body">{html_escape(three_five)}</p>',
                unsafe_allow_html=True,
            )


def render_chart_mobile_meta(print_meta: str) -> None:
    """Mobile-only summary text above chart (not overlapping the disk)."""
    if not print_meta.strip():
        return
    st.markdown(
        f'<div class="chart-stage-mobile-meta" aria-label="Chart metadata">'
        f'<div class="chart-print-meta">{html_escape(print_meta)}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )


def render_chart_stage_open(*, print_meta: str = "") -> None:
    """Marker + radial stage styling; mobile meta sits above the chart."""
    render_chart_mobile_meta(print_meta)
    st.markdown(
        '<div class="chart-stage-marker" aria-hidden="true"></div>',
        unsafe_allow_html=True,
    )