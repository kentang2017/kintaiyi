import os
import sys
import base64
import hashlib
from html import escape as html_escape

# Resolve the repository root (one level up from apps/) so that relative paths
# to assets/ and src/ work regardless of the working directory.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Ensure the src directory is on the Python path so that the kintaiyi package
# can be imported when running from the repository root (e.g. on Streamlit Cloud).
sys.path.insert(0, os.path.join(_REPO_ROOT, "src"))

# Add the apps/ directory to sys.path so that the custom_css module is importable.
_apps_dir = os.path.dirname(os.path.abspath(__file__))
if _apps_dir not in sys.path:
    sys.path.insert(0, _apps_dir)

import streamlit as st
import datetime
import pytz
from contextlib import contextmanager, redirect_stdout
from io import StringIO
import urllib.request
import urllib.error
import json
from kintaiyi import jieqi
from kintaiyi import kintaiyi
from kintaiyi import config
from kintaiyi.chart_view import (
    build_chart_view_model,
    build_geju_overlay_svg,
    build_geju_sector_markers,
    geju_label_css,
    mark_wenchang_spots_in_svg,
    wenchang_spot_chart_css,
    wuxing_theme_chart_css,
    build_guxu_chart_model,
    build_guxu_overlay_svg,
    build_guxu_sector_hints,
    chart_svg_layout,
    guxu_rotate_layer,
    sector_panel_layer_labels,
    _layer2_gong_order,
)

import cn2an
from cn2an import an2cn

# ── Mobile detection via streamlit-screen-stats ─────────────────────────
try:
    from streamlit_screen_stats import screen_stats as _screen_stats
except Exception:
    _screen_stats = None


def _get_screen_width() -> int:
    """Return the client screen width in pixels (fallback 1024)."""
    if _screen_stats is not None:
        try:
            stats = _screen_stats()
            if isinstance(stats, dict):
                return int(stats.get("screen_width", 1024))
        except Exception:
            pass
    return 1024


def _is_mobile() -> bool:
    """True when the client viewport is below 768 px wide."""
    return _get_screen_width() < 768


# 十二地支時辰對照
_ZHI_HOURS = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]


def _hour_to_zhi(hour: int) -> str:
    """Convert 24h hour to 地支時辰 name (子=23-1, 丑=1-3, ...)."""
    _idx = ((hour + 1) // 2) % 12
    return _ZHI_HOURS[_idx]
from kintaiyi.guiyun_display import (
    chong_gua_row,
    inner_outer_rows,
    limit_rows,
)
from kintaiyi.junshi_display import (
    wuzhen_bazhen_svg,
    wuzhen_reference_rows,
    wuzhen_table_rows,
)
from kintaiyi.tongyun_display import apply_tongyun_query, historical_compare
from kintaiyi.taiyidict import tengan_shiji, su_dist
from kintaiyi.taiyimishu import taiyi_yingyang
from kintaiyi.historytext import chistory
import pandas as pd
from kintaiyi.cerebras_client import CerebrasClient, DEFAULT_MODEL as DEFAULT_CEREBRAS_MODEL, TokenQuotaExceededError
from kintaiyi.openai_client import OpenAIClient, DEFAULT_MODEL as DEFAULT_OPENAI_MODEL, TokenQuotaExceededError as OpenAITokenQuotaExceededError
from kintaiyi.openai_compatible_client import OpenAICompatibleClient, TokenQuotaExceededError as CompatibleTokenQuotaExceededError
from kintaiyi.game_theory import TaiyiGame, 主方策略列 as _gt_主方策略列, 客方策略列 as _gt_客方策略列
from custom_css import get_custom_css, get_sidebar_cursor_fix_html, get_top_nav_html, get_sidebar_brand_html
from sidebar_ui import render_grok_sidebar
from chart_layout import (
    build_chart_print_meta,
    render_chart_mobile_params,
    render_chart_side_panel,
    render_chart_stage_open,
)
from hex_timeline import render_hex_timeline, render_classic_reading
from yun_timeline import render_yun_section

# 5=太乙命法(魔改·分計落宮)  6=太乙命法(時計落宮)
LIFE_CHART_STYLES = frozenset({5, 6})
LIFE_PLATE_JI = {5: 4, 6: 3}


def _is_life_chart_style(style: int) -> bool:
    return style in LIFE_CHART_STYLES


def _life_method_label(style: int) -> str:
    if style == 5:
        return to("太乙命法 (魔改)")
    if style == 6:
        return to("太乙命法")
    return t("taiyi_life_method")


def _format_neiwai_gongji(nw: dict | None) -> str:
    """內外占攻擊摘要：孤虛、宜攻方向與斷語。"""
    if not nw:
        return "—"
    guxu = nw.get("孤虛", "—")
    attack = nw.get("宜攻", "—")
    verdict = nw.get("斷語", "—")
    if st.session_state.get("lang", "zh") == "en":
        return f"{guxu}, attack {attack} ({verdict})"
    return f"{guxu}，宜攻{attack}（{verdict}）"


def _format_guxu_duizhao(gx: dict | None) -> str:
    """卷五攻擊與卷十七求索之孤虛對照摘要。"""
    if not gx:
        return ""
    v5 = gx.get("卷五") or {}
    v17 = gx.get("卷十七") or {}
    attack_dir = v5.get("宜攻", "—")
    seek_result = v17.get("求索", "—")
    if st.session_state.get("lang", "zh") == "en":
        return (
            f"{t('guxu_duizhao')}"
            f"{gx.get('孤虛', '—')} (sky-eye {gx.get('天目內外', '—')}); "
            f"attack {attack_dir} ({v5.get('斷語', '')}); "
            f"seek {seek_result}; "
            f"{gx.get('對照', '')}: {gx.get('對照斷語', '')}"
        )
    return (
        f"{t('guxu_duizhao')}"
        f"{gx.get('孤虛', '—')}（天目{gx.get('天目內外', '—')}）·"
        f"宜攻{attack_dir}（{v5.get('斷語', '')}）；"
        f"求索{seek_result}；"
        f"{gx.get('對照', '')}：{gx.get('對照斷語', '')}"
    )


def _render_vol9_explanation(v9: dict | None) -> None:
    """卷九：大小遊軌運入卦、重卦策數、陽九百六限數。"""
    v9 = v9 or {}
    dy = v9.get("大遊軌運") or {}
    xy = v9.get("小遊軌運") or {}
    if not dy and not xy:
        return
    _yj9 = v9.get("陽九限數") or {}
    _bl9 = v9.get("百六限數") or {}
    st.markdown(
        f"{t('guiyun')}"
        f"大遊{dy.get('重卦', '—')}{dy.get('內爻名', '')}"
        f"（{dy.get('內卦', '')}/{dy.get('外卦', '')}·策{dy.get('總策', '—')}）；"
        f"小遊{xy.get('重卦', '—')}{xy.get('內爻名', '')}"
        f"（策{xy.get('總策', '—')}）；"
        f"落宮{v9.get('大遊落宮', '—')}/{v9.get('小遊落宮', '—')}"
    )
    _line9 = []
    if v9.get("大遊入宮年數") is not None:
        _line9.append(f"{t('guiyun_palace_years')}{v9['大遊入宮年數']}年")
    if v9.get("行宮卦異"):
        _line9.append(t("guiyun_gong_diff"))
    if _yj9:
        _line9.append(f"{t('yangjiu_xian')}入限{_yj9.get('入限年數', '—')}年")
    if _bl9:
        _line9.append(f"{t('bailiu_xian')}入限{_bl9.get('入限年數', '—')}年")
    if v9.get("歲計陽九支") or v9.get("歲計百六支"):
        _line9.append(
            f"歲計陽九{v9.get('歲計陽九支', '—')}／百六{v9.get('歲計百六支', '—')}"
        )
    if _line9:
        st.markdown("；".join(_line9))
    _xz = v9.get("小遊行爻災祥") or {}
    if _xz.get("斷語"):
        st.markdown(
            f"{t('guiyun_xingyao')}"
            f"{_xz.get('重卦', '')}{_xz.get('爻名', '')}·{_xz.get('納甲', '')}·"
            f"{_xz.get('天干分野', '')}{_xz.get('地支分野', '')}；"
            f"{_xz['斷語']}"
        )
    with st.expander(t("guiyun_detail"), expanded=False):
        st.markdown(f"**{t('guiyun_chong')}**")
        st.dataframe(
            pd.DataFrame([chong_gua_row(dy, scope="大遊"), chong_gua_row(xy, scope="小遊")]),
            width="stretch",
            hide_index=True,
        )
        st.markdown(f"**{t('guiyun_inner_outer')}·大遊**")
        st.dataframe(
            pd.DataFrame(inner_outer_rows(v9.get("大遊內卦"), v9.get("大遊外卦"), scope="大遊")),
            width="stretch",
            hide_index=True,
        )
        st.markdown(f"**{t('guiyun_inner_outer')}·小遊**")
        st.dataframe(
            pd.DataFrame(inner_outer_rows(v9.get("小遊內卦"), v9.get("小遊外卦"), scope="小遊")),
            width="stretch",
            hide_index=True,
        )
        _limits = limit_rows(v9)
        if _limits:
            st.markdown(f"**{t('guiyun_limits')}**")
            st.dataframe(
                pd.DataFrame(_limits),
                width="stretch",
                hide_index=True,
            )
        _ce = v9.get("四象之策") or []
        if _ce:
            st.markdown(f"**{t('guiyun_ce_ref')}**")
            st.dataframe(
                pd.DataFrame(_ce).astype(str),
                width="stretch",
                hide_index=True,
            )
        if dy.get("要訣"):
            st.caption(dy["要訣"])
        if xy.get("要訣"):
            st.caption(xy["要訣"])
        if v9.get("要訣"):
            st.caption(v9["要訣"])


def _render_wuzhen_bazhen_viz(wuzhen: dict | None) -> None:
    """卷十五：五陣置旗與八陣圖視覺化（直接渲染，不含 expander 包裝）。"""
    if not wuzhen:
        return
    st.markdown(f"**{t('five_formations')}**")
    st.dataframe(
        pd.DataFrame(wuzhen_table_rows(wuzhen)),
        width="stretch",
        hide_index=True,
    )
    st.markdown(f"**{t('wuzhen_reference')}**")
    st.dataframe(
        pd.DataFrame(wuzhen_reference_rows()),
        width="stretch",
        hide_index=True,
    )
    if wuzhen.get("八陣要訣"):
        st.caption(wuzhen["八陣要訣"])
    st.markdown(
        wuzhen_bazhen_svg(
            wuzhen,
            title_five=t("five_formations_short"),
            title_eight=t("eight_formations_short"),
            title_chubing=t("chubing_xiang_title"),
            center_label=t("bazhen_center"),
            home_label=t("side_home"),
            away_label=t("side_away"),
        ),
        unsafe_allow_html=True,
    )


def _resolve_tongyun_year(chart_year: int) -> int:
    if st.session_state.get("tongyun_sync_chart", True):
        return int(chart_year)
    return int(st.session_state.get("tongyun_query_year", chart_year))


def _display_ttext(results: dict) -> dict:
    """依統運查詢年覆寫卷十二～十四。"""
    ty = results.get("ty")
    if ty is None:
        return results.get("ttext") or {}
    query_year = _resolve_tongyun_year(ty.year)
    return apply_tongyun_query(
        results.get("ttext") or {},
        query_year,
        ty.year,
        month=ty.month,
        day=ty.day,
    )


def _render_tongyun_history_compare(query_year: int) -> None:
    compare = historical_compare(query_year)
    rugua = compare.get("統運入卦") or {}
    with st.expander(t("tongyun_history_compare"), expanded=bool(compare.get("當年例"))):
        st.caption(
            f"{rugua.get('運', '—')}·{rugua.get('卦', '—')}"
            f"{rugua.get('爻名', '')}（{query_year}）"
        )
        exact = compare.get("當年例") or []
        if exact:
            st.markdown(f"**{t('tongyun_exact_year')}**")
            for item in exact:
                st.markdown(
                    f"· {item.get('紀年', '')}（{item.get('年', '')}）"
                    f"{item.get('運', '')}·{item.get('卦', '')}{item.get('爻', '')}："
                    f"{item.get('摘要', '')}"
                )
        same = compare.get("同卦爻例") or []
        if same:
            st.markdown(f"**{t('tongyun_same_gua_yao')}**")
            for item in same:
                if item.get("年") == query_year:
                    continue
                st.markdown(
                    f"· {item.get('紀年', '')}（{item.get('年', '')}）"
                    f"{item.get('運', '')}·{item.get('卦', '')}{item.get('爻', '')}："
                    f"{item.get('摘要', '')}"
                )
        near = compare.get("近例") or []
        if near:
            st.markdown(f"**{t('tongyun_near_examples')}**")
            for item in near:
                delta = item.get("相差", 0)
                sign = f"+{delta}" if delta > 0 else str(delta)
                st.markdown(
                    f"· {item.get('紀年', '')}（{item.get('年', '')}，"
                    f"{t('tongyun_year_delta').format(delta=sign)}）"
                    f"{item.get('運', '')}·{item.get('卦', '')}{item.get('爻', '')}："
                    f"{item.get('摘要', '')}"
                )


def _render_zhao_you_songs(zhao_you: dict, *, preview: int = 6) -> None:
    """命法區：照限游年歌匹配結果（預覽＋全文展開）。"""
    songs = zhao_you.get("星歌") or []
    zhao = zhao_you.get("照限") or {}
    youn = zhao_you.get("游年") or {}
    st.markdown(
        f"{t('zhao_you')}"
        f"{zhao.get('類型', '')}限{zhao.get('地支', '')}｜"
        f"{youn.get('年份', '')}年{youn.get('地支', '')}"
    )
    if zhao.get("星曜"):
        st.caption(f"照限星：{'、'.join(zhao['星曜'])}")
    if youn.get("星曜"):
        st.caption(f"游年星：{'、'.join(youn['星曜'])}")
    if not songs:
        st.caption(t("sector_panel_empty"))
        return
    st.caption(t("zhao_you_count").format(n=len(songs)))
    for song in songs[:preview]:
        scope = []
        if song.get("照限"):
            scope.append(t("zhao_you_scope_zhao"))
        if song.get("游年"):
            scope.append(t("zhao_you_scope_you"))
        st.markdown(
            f"**【{'·'.join(scope)}·{song.get('星', '')}】** {song.get('歌訣', '')}"
        )
    if len(songs) > preview:
        with st.expander(t("zhao_you_detail"), expanded=False):
            for song in songs:
                scope = []
                if song.get("照限"):
                    scope.append(t("zhao_you_scope_zhao"))
                if song.get("游年"):
                    scope.append(t("zhao_you_scope_you"))
                st.markdown(
                    f"**【{'·'.join(scope)}·{song.get('星', '')}】** {song.get('歌訣', '')}"
                )


import re


def render_changelog_html(md_text: str) -> str:
    """Parse update.md markdown and return styled HTML for the changelog timeline."""
    lines = md_text.splitlines()
    entries: list[dict] = []
    current: dict | None = None

    for line in lines:
        stripped = line.strip()
        # Match date headers like ### 【2026/04/19】
        m = re.match(r'^###\s*【(.+?)】\s*$', stripped)
        if m:
            if current:
                entries.append(current)
            current = {"date": m.group(1), "items": []}
            continue
        if current is None:
            continue
        if stripped.startswith('-----') or stripped == '---' or stripped == '':
            continue
        # Bullet items (with or without leading "- ")
        if stripped.startswith('- '):
            current["items"].append(stripped[2:].strip())
        elif re.match(r'^\d+\.\s', stripped):
            current["items"].append(re.sub(r'^\d+\.\s*', '', stripped))
        elif stripped:
            current["items"].append(stripped)

    if current:
        entries.append(current)

    # Build HTML
    html_parts = [
        '<div class="changelog-container">',
        '  <div class="changelog-header">',
        '    <h2>堅太乙排盤更新日誌</h2>',
        '    <div class="changelog-ornament">✦ ❖ ✦</div>',
        '  </div>',
        '  <div class="changelog-timeline">',
    ]
    for entry in entries:
        html_parts.append('    <div class="changelog-entry">')
        html_parts.append(f'      <div class="changelog-date">{entry["date"]}</div>')
        if entry["items"]:
            html_parts.append('      <ul class="changelog-items">')
            for item in entry["items"]:
                html_parts.append(f'        <li>{item}</li>')
            html_parts.append('      </ul>')
        html_parts.append('    </div>')
    html_parts.append('  </div>')
    html_parts.append('</div>')
    return '\n'.join(html_parts)


@st.cache_data(show_spinner=False)
def _render_changelog_html_cached(md_text: str) -> str:
    return render_changelog_html(md_text)


@st.cache_data(show_spinner=False)
def _load_example_timeline_json() -> str:
    path = os.path.join(_REPO_ROOT, "assets", "example.json")
    with open(path, encoding="utf-8-sig") as f:
        return f.read()


# --- i18n: Translation dictionaries ---
TRANSLATIONS = {
    "zh": {
        "page_title": "堅太乙-太乙神數排盤",
        "lang_label": "語言 Language",
        "sidebar_block_basic": "基本參數",
        "sidebar_block_method": "太乙計式",
        "sidebar_block_life": "命法設定",
        "sidebar_block_visual": "盤面視覺",
        "sidebar_block_ai": "AI 解盤",
        "sidebar_block_advanced": "進階功能",
        "sidebar_ai_connection": "連線設定",
        "sidebar_ai_prompts": "提示詞",
        "sidebar_ai_cerebras_hint": "使用環境變數或 Streamlit secrets 中的 Cerebras 金鑰。",
        "sidebar_expand": "展開設定面板",
        "sidebar_collapse": "收合為圖示模式",
        "sidebar_icon_basic": "基本參數（日期、語言）",
        "sidebar_icon_method": "太乙計式",
        "sidebar_icon_life": "命法設定",
        "sidebar_icon_visual": "盤面視覺",
        "sidebar_icon_ai": "AI 解盤",
        "sidebar_icon_advanced": "進階功能",
        "date_label": "日期",
        "date_mode_label": "日期",
        "date_mode_gregorian": "西曆",
        "date_mode_bc": "公元前",
        "date_bc_hint": "",
        "time_label": "時間",
        "run_chart_btn": "立即排盤",
        "rerun_chart_btn": "重新排盤",
        "chart_params_stale_hint": "側欄日期已變更，請按「立即排盤」更新。",
        "chart_summary": "干支曆",
        "chart_meta_detail": "完整參數",
        "kook_label": "局數",
        "five_yuan_short": "五子元",
        "three_five_more": "展開全文",
        "chart_method_hint": "選擇太乙計式",
        "acc_years_hint": "積年法",
        "debug_info": "Session State",
        "param_header": "排盤參數設置",
        "year": "年",
        "month": "月",
        "day": "日",
        "hour": "時",
        "minute": "分",
        "chart_method": "起盤方式",
        "acc_years": "太乙積年數",
        "ten_essences": "太乙十精",
        "life_gender": "太乙命法性別",
        "rotation_label": "轉盤",
        "geju_markers_toggle": "顯示釋格局標記",
        "guxu_overlay_toggle": "顯示孤虛標記",
        "wuxing_color_toggle": "五行彩色排盤",
        "instant_btn": "使用現在時間（HKT）",
        "ai_settings": "AI設置",
        "ai_provider": "AI 服務商",
        "ai_model": "AI 模型",
        "custom_provider_section": "自定義服務商設置",
        "custom_provider_name": "名稱",
        "custom_provider_api_mode": "API 模式",
        "custom_provider_api_mode_option": "OpenAI API 兼容",
        "custom_provider_api_key": "API 密鑰",
        "custom_provider_show_key": "顯示密鑰",
        "custom_provider_check_btn": "檢查",
        "custom_provider_api_host": "API 主機",
        "custom_provider_api_path": "API 路徑",
        "custom_provider_network_compat": "改善網絡兼容性",
        "custom_provider_models_label": "模型",
        "custom_provider_add_model": "+ 新增",
        "custom_provider_reset_models": "↺ 重置",
        "custom_provider_fetch_models": "⟳ 獲取",
        "custom_provider_no_models": "沒有可用模型",
        "custom_provider_new_model_placeholder": "輸入模型名稱",
        "custom_provider_key_ok": "✅ 密鑰有效",
        "custom_provider_key_fail": "❌ 密鑰無效：{}",
        "custom_provider_fetch_ok": "✅ 已獲取 {} 個模型",
        "custom_provider_fetch_fail": "❌ 獲取失敗：{}",
        "custom_provider_api_key_missing": "請輸入自定義服務商 API 密鑰。",
        "custom_provider_host_missing": "請輸入 API 主機。",
        "ai_custom_quota_exceeded": "⚠️ 自定義服務商 API 配額已用盡或速率受限，請稍後再試。",
        "openai_api_key_label": "OpenAI API 密鑰",
        "openai_api_key_placeholder": "輸入你的 OpenAI API 密鑰（sk-...）",
        "openai_api_key_missing": "請輸入 OpenAI API 密鑰。",
        "xai_api_key_label": "xAI API 密鑰",
        "xai_api_key_placeholder": "輸入你的 xAI API 密鑰（xai-...）",
        "xai_api_key_missing": "請輸入 xAI API 密鑰。",
        "deepseek_api_key_label": "DeepSeek API 密鑰",
        "deepseek_api_key_placeholder": "輸入你的 DeepSeek API 密鑰（sk-...）",
        "deepseek_api_key_missing": "請輸入 DeepSeek API 密鑰。",
        "qwen_api_key_label": "Qwen API 密鑰",
        "qwen_api_key_placeholder": "輸入你的通義千問 API 密鑰",
        "qwen_api_key_missing": "請輸入 Qwen API 密鑰。",
        "select_prompt": "選擇系統提示",
        "select_prompt_help": "選擇用於AI模型的系統提示，指導其分析太乙排盤結果",
        "edit_prompt": "編輯系統提示",
        "edit_prompt_placeholder": "範例：你是一位太乙神數專家，根據排盤數據提供詳細分析...",
        "update_prompt": "💾 更新提示",
        "delete_prompt": "❌ 刪除提示",
        "add_prompt_expander": "➕ 新增提示",
        "add_prompt_btn": "➕ 新增提示",
        "new_prompt_name": "新提示名稱",
        "new_prompt_content": "新提示內容",
        "new_prompt_placeholder": "輸入AI分析指令...",
        "prompt_exists": "提示名稱 '{}' 已存在。",
        "prompt_updated": "✅ 已更新系統提示 '{}'！",
        "prompt_deleted": "✅ 已刪除系統提示 '{}'！",
        "prompt_added": "✅ 已新增系統提示 '{}'！",
        "advanced_settings": "🔧 高級設置",
        "max_tokens": "最大生成 Tokens",
        "max_tokens_help": "控制AI回應的最大長度",
        "temperature": "溫度 (專注 vs. 創意)",
        "temperature_help": "較低值 (如 0.2) 更確定性；較高值 (如 0.8) 更隨機",
        "debug_mode": "🔍 除錯模式",
        "debug_help": "顯示除錯資訊，如 session state",
        "debug_info": "🐛 除錯資訊",
        # Tabs
        "tab_chart": "🧮太乙排盤",
        "tab_instructions": "💬使用說明",
        "tab_history": "📜局數史例",
        "tab_disaster": "🔥災異統計",
        "tab_books": "📚古籍書目",
        "tab_updates": "🆕更新日誌",
        "tab_guide": "🚀看盤要領",
        "tab_links": "🔗連結",
        # Main content
        "explanation": "解釋",
        "taiyi_life_title": "《太乙命法》︰",
        "twelve_palaces": "【十二宮分析】",
        "sixteen_gods": "【太乙十六神落宮】",
        "sixteen_grades": "【太乙十六神上中下等】",
        "hexagram": "【值卦】",
        "year_hex": "年卦：",
        "month_hex": "月卦：",
        "day_hex": "日卦：",
        "hour_hex": "時卦：",
        "minute_hex": "分卦：",
        "yang_nine": "【陽九行限】",
        "bai_liu": "【百六行限】",
        "taiyi_mishu": "《太乙秘書》",
        "history_records": "史事記載︰",
        "chart_analysis": "太乙盤局分析",
        "year_star_predict": "太歲值宿斷事︰",
        "start_star_predict": "始擊值宿斷事︰",
        "ten_stem_predict": "十天干歲始擊落宮預測︰",
        "sky_ground_method": "推太乙在天外地內法︰",
        "three_five": "三門五將︰",
        "home_away": "推主客相關︰",
        "win_loss": "推少多以占勝負︰",
        "wind_cloud": "推太乙風雲飛鳥助戰︰",
        "solitary": "推孤單以占成敗:",
        "yin_yang_adversity": "推陰陽以占厄會︰",
        "emperor_tour": "明天子巡狩之期術︰",
        "ruler_base": "明君基太乙所主術︰",
        "minister_base": "明臣基太乙所主術︰",
        "people_base": "明民基太乙所主術︰",
        "five_blessings": "明五福太乙所主術︰",
        "five_blessings_calc": "明五福吉算所主術︰",
        "heaven_yi": "明天乙太乙所主術︰",
        "earth_yi": "明地乙太乙所主術︰",
        "zhifu": "明值符太乙所主術︰",
        "shi_geju": "釋格局",
        "sanqi": "三旗行宮︰",
        "nine_gods": "九宮貴神︰",
        "taiyi_stars": "太乙九星︰",
        "wenchang_stars": "文昌九星︰",
        "wuyun_liuqi": "五運六氣︰",
        "wuyin_shu": "五音之數︰",
        "junshi_vol5": "軍事戰略︰",
        "guxu_duizhao": "孤虛對照︰",
        "vol11": "州國災變︰",
        "tongyun_rugua": "統運入卦︰",
        "liunian_zhigua": "流年直卦",
        "liuyue_zhigua": "流月直卦",
        "liuri_zhigua": "流日直卦",
        "liushi_zhigua": "流時直卦",
        "liufen_zhigua": "流分直卦",
        "ruyao_huofu": "入爻禍福︰",
        "shier_yun": "十二運立成︰",
        "lishi_ruyao": "歷史入爻例︰",
        "tongyun_detail": "統運詳情",
        "gua_xiang": "卦象觀象",
        "gua_xiang_detail": "卦象詳情",
        "bian_gua_najia": "變卦納甲",
        "shouwei": "災厄首尾",
        "hangzhi_biannian": "行支編年",
        "tongyun_extended": "統運延伸",
        "tongyun_query_header": "統運查詢",
        "tongyun_sync_chart": "與排盤年同步",
        "tongyun_sync_hint": "統運入卦隨排盤年 {year} 計算",
        "tongyun_query_year": "統運查詢年",
        "tongyun_query_note": "統運以 {query} 年入卦（排盤年 {chart}）",
        "tongyun_history_compare": "統運歷史對照",
        "tongyun_exact_year": "當年驗例",
        "tongyun_same_gua_yao": "同卦爻例",
        "tongyun_near_examples": "近例",
        "tongyun_year_delta": "相差 {delta} 年",
        "yun_timeline_label": "統運 · 第",
        "yun_per_cycle": "年 / 週期",
        "yun_years": "年",
        "yun_yao_year": "入爻第",
        "yun_gua_year": "入卦第",
        "yun_ce": "策",
        "yun_cycle": "週期第",
        "yun_expand_huofu": "展開爻位禍福全文",
        "yun_ganzhi": "干支",
        "yun_year_suffix": "年",
        "yun_zhigua": "直卦",
        "yun_yao_suffix": "爻",
        "yun_mff": "命爻法",
        "yun_ben_bian": "本變",
        "yun_dong_yao": "動爻",
        "yun_najia": "納甲",
        "yun_fangwei": "方位",
        "yun_fenye": "分野",
        "yun_xiang_yue": "象曰",
        "yun_yao_guanxiang": "入爻觀象",
        "hex_xiang_yue": "象曰",
        "hex_zongshu": "卦象總述",
        "hex_yao_ci": "動爻辭",
        "liuri_label": "流日卦運",
        "liunian_label": "流年卦運",
        "liuyue_label": "流月卦運",
        "liushi_label": "流時卦運",
        "liufen_label": "流分卦運",
        "liuri_scroll_hint": "← 滑動查看未來 →",
        "star_distribution_label": "星曜分佈",
        "disaster_fenye_label": "災變分野",
        "qi_music_label": "運氣音律",
        "fenye_label": "分野疆界",
        "junshi_label": "軍事戰略",
        "wuyun_label": "五運六氣",
        "xingxian_label": "行限推論",
        "guiyun_label": "大小遊軌運",
        "life_query_age": "命法查詢虛歲",
        "life_query_year": "照限游年年份",
        "fenye": "分野疆界︰",
        "guiyun": "大小遊軌運︰",
        "guiyun_detail": "軌運策數詳情",
        "guiyun_chong": "重卦策數",
        "guiyun_inner_outer": "內外入卦",
        "guiyun_ce_ref": "四象之策",
        "guiyun_limits": "陽九百六限數",
        "guiyun_xingyao": "小遊行爻災祥",
        "guiyun_palace_years": "大遊入宮年數",
        "guiyun_gong_diff": "行宮卦異",
        "vol10_hehui": "天目合會︰",
        "yunqi": "十精雲氣︰",
        "yangjiu_xian": "陽九限數︰",
        "bailiu_xian": "百六限數︰",
        "sixteen_palace": "十六宮分佈︰",
        "shiti_jinfu": "太乙十提金賦︰",
        "mingfa_vol20": "【卷二十命法】",
        "fly_lu_ma": "飛祿飛馬行限︰",
        "sanhe_he": "三合十干合︰",
        "palace_states": "十二宮旺衰絕空刑︰",
        "qiou_sancai": "奇耦三才︰",
        "life_geju": "命盤格局︰",
        "bailiu_gua": "百六行月日卦︰",
        "zhao_you": "照限游年︰",
        "palace_state_detail": "宮位詳情",
        "rugua_xian": "百六入卦限︰",
        "yangjiu_sanxian": "陽九入三限︰",
        "wangxian_lun": "旺陷獨處同宮論︰",
        "zhao_you_detail": "照限游年歌全文",
        "zhao_you_count": "共 {n} 首",
        "zhao_you_scope_zhao": "照限",
        "zhao_you_scope_you": "游年",
        "wangxian_detail": "星論詳情",
        "feifu_sisha": "飛符四殺︰",
        "junshi_vol15": "軍事應用︰",
        "wuzhen_bazhen_viz": "五陣八陣",
        "five_formations": "五陣置旗（主客）",
        "five_formations_short": "五陣",
        "eight_formations_short": "八陣",
        "wuzhen_reference": "置旗規則（算數個位）",
        "chubing_xiang_title": "陳兵出鄉",
        "bazhen_center": "握機",
        "side_home": "主",
        "side_away": "客",
        "junshi_vol17": "軍事占斷︰",
        "shenjiang_suozhu": "神將所主",
        # AI
        "ai_analyze_btn": "🔍 使用AI分析排盤結果",
        "ai_analyzing": "AI正在分析太乙排盤結果...",
        "ai_key_missing": "CEREBRAS_API_KEY 未設置，請在 .streamlit/secrets.toml 或環境變量中設置。",
        "ai_error": "調用AI時發生錯誤：{}",
        "ai_quota_exceeded": "⚠️ Cerebras API 每日 Token 配額已用盡，請稍後再試或降低「最大生成 Tokens」設定。",
        "ai_openai_quota_exceeded": "⚠️ OpenAI API 配額已用盡或速率受限，請稍後再試。",
        "ai_xai_quota_exceeded": "⚠️ xAI API 配額已用盡或速率受限，請稍後再試。",
        "ai_deepseek_quota_exceeded": "⚠️ DeepSeek API 配額已用盡或速率受限，請稍後再試。",
        "ai_qwen_quota_exceeded": "⚠️ Qwen API 配額已用盡或速率受限，請稍後再試。",
        "gen_error": "生成盤局時發生錯誤：{}",
        "ai_result": "AI分析結果",
        "list_label": "列表",
        "save_error": "錯誤儲存提示：{}",
        # Chat
        "chat_header": "💬 AI 對話",
        "chat_placeholder": "輸入問題，與太乙AI大師對話...",
        "chat_thinking": "AI 正在思考...",
        "chat_welcome": "你好！我是太乙AI助手，可以為你解答關於太乙神數的問題。請輸入你的問題。",
        "chat_clear": "🗑️ 清除對話",
        # 博弈論
        "game_theory_toggle": "🎯 啟用運籌博弈分析（Nash 均衡）",
        "game_theory_header": "運籌博弈分析",
        "game_theory_payoff": "零和支付矩陣（主方視角）",
        "game_theory_home_strategy": "主方最優混合策略",
        "game_theory_away_strategy": "客方最優混合策略",
        "game_theory_value": "博弈均衡值（期望支付）",
        "game_theory_lp": "線性規劃最優建議",
        "game_theory_winrate": "主方勝率判斷",
        "game_theory_computing": "⚙️ 正在計算 Nash 均衡...",
        # Print labels
        "lunar_label": "農曆",
        "taiyi_life_method": "太乙命法",
        "epoch_label": "紀元",
        "home_calc": "主筭",
        "away_calc": "客筭",
        "set_calc": "定筭",
        "five_yuan": "五子元局",
        "acc_prefix": "積",
        "acc_suffix": "數",
    },
    "en": {
        "page_title": "Kin Taiyi-Taiyi Divine Number Chart",
        "lang_label": "語言 Language",
        "sidebar_block_basic": "Basic Parameters",
        "sidebar_block_method": "Taiyi Method",
        "sidebar_block_life": "Life Chart",
        "sidebar_block_visual": "Chart Display",
        "sidebar_block_ai": "AI Reading",
        "sidebar_block_advanced": "Advanced",
        "sidebar_ai_connection": "Connection",
        "sidebar_ai_prompts": "Prompts",
        "sidebar_ai_cerebras_hint": "Uses Cerebras API key from env or Streamlit secrets.",
        "sidebar_expand": "Expand settings panel",
        "sidebar_collapse": "Collapse to icon mode",
        "sidebar_icon_basic": "Basic parameters (date, language)",
        "sidebar_icon_method": "Taiyi method",
        "sidebar_icon_life": "Life chart settings",
        "sidebar_icon_visual": "Chart display",
        "sidebar_icon_ai": "AI reading",
        "sidebar_icon_advanced": "Advanced",
        "date_label": "Date",
        "date_mode_label": "Date",
        "date_mode_gregorian": "Gregorian",
        "date_mode_bc": "BCE",
        "date_bc_hint": "",
        "time_label": "Time",
        "run_chart_btn": "Run Chart",
        "rerun_chart_btn": "Re-run Chart",
        "chart_params_stale_hint": "Sidebar date changed — click Run Chart to refresh.",
        "chart_summary": "Stem-Branch",
        "chart_meta_detail": "Full parameters",
        "kook_label": "Bureau No.",
        "five_yuan_short": "Five Yuan",
        "three_five_more": "Show full text",
        "chart_method_hint": "Select Taiyi method",
        "acc_years_hint": "Accumulation method",
        "debug_info": "Session State",
        "param_header": "Chart Parameters",
        "year": "Year",
        "month": "Month",
        "day": "Day",
        "hour": "Hour",
        "minute": "Minute",
        "chart_method": "Chart Method",
        "acc_years": "Accumulated Years",
        "ten_essences": "Taiyi Ten Essences",
        "life_gender": "Life Method Gender",
        "rotation_label": "Rotation",
        "geju_markers_toggle": "Show pattern markers (釋格局)",
        "guxu_overlay_toggle": "Show Gu-Xu markers",
        "wuxing_color_toggle": "Five-element color chart",
        "instant_btn": "Use current time (HKT)",
        "ai_settings": "AI Settings",
        "ai_provider": "AI Provider",
        "ai_model": "AI Model",
        "custom_provider_section": "Custom Provider Settings",
        "custom_provider_name": "Name",
        "custom_provider_api_mode": "API Mode",
        "custom_provider_api_mode_option": "OpenAI API Compatible",
        "custom_provider_api_key": "API Key",
        "custom_provider_show_key": "Show Key",
        "custom_provider_check_btn": "Check",
        "custom_provider_api_host": "API Host",
        "custom_provider_api_path": "API Path",
        "custom_provider_network_compat": "Improve Network Compatibility",
        "custom_provider_models_label": "Models",
        "custom_provider_add_model": "+ Add",
        "custom_provider_reset_models": "↺ Reset",
        "custom_provider_fetch_models": "⟳ Fetch",
        "custom_provider_no_models": "No available models",
        "custom_provider_new_model_placeholder": "Enter model name",
        "custom_provider_key_ok": "✅ Key is valid",
        "custom_provider_key_fail": "❌ Key invalid: {}",
        "custom_provider_fetch_ok": "✅ Fetched {} model(s)",
        "custom_provider_fetch_fail": "❌ Fetch failed: {}",
        "custom_provider_api_key_missing": "Please enter the custom provider API key.",
        "custom_provider_host_missing": "Please enter the API host.",
        "ai_custom_quota_exceeded": "⚠️ Custom provider API quota exceeded or rate-limited. Please try again later.",
        "openai_api_key_label": "OpenAI API Key",
        "openai_api_key_placeholder": "Enter your OpenAI API key (sk-...)",
        "openai_api_key_missing": "Please enter your OpenAI API key.",
        "xai_api_key_label": "xAI API Key",
        "xai_api_key_placeholder": "Enter your xAI API key (xai-...)",
        "xai_api_key_missing": "Please enter your xAI API key.",
        "deepseek_api_key_label": "DeepSeek API Key",
        "deepseek_api_key_placeholder": "Enter your DeepSeek API key (sk-...)",
        "deepseek_api_key_missing": "Please enter your DeepSeek API key.",
        "qwen_api_key_label": "Qwen API Key",
        "qwen_api_key_placeholder": "Enter your Qwen (DashScope) API key",
        "qwen_api_key_missing": "Please enter your Qwen API key.",
        "select_prompt": "Select System Prompt",
        "select_prompt_help": "Select a system prompt for the AI model to guide Taiyi chart analysis",
        "edit_prompt": "Edit System Prompt",
        "edit_prompt_placeholder": "Example: You are a Taiyi expert, provide detailed analysis based on chart data...",
        "update_prompt": "💾 Update Prompt",
        "delete_prompt": "❌ Delete Prompt",
        "add_prompt_expander": "➕ Add Prompt",
        "add_prompt_btn": "➕ Add Prompt",
        "new_prompt_name": "New Prompt Name",
        "new_prompt_content": "New Prompt Content",
        "new_prompt_placeholder": "Enter AI analysis instructions...",
        "prompt_exists": "Prompt name '{}' already exists.",
        "prompt_updated": "✅ Updated system prompt '{}'!",
        "prompt_deleted": "✅ Deleted system prompt '{}'!",
        "prompt_added": "✅ Added system prompt '{}'!",
        "advanced_settings": "🔧 Advanced Settings",
        "max_tokens": "Max Generation Tokens",
        "max_tokens_help": "Control the maximum length of AI responses",
        "temperature": "Temperature (Focus vs. Creative)",
        "temperature_help": "Lower values (e.g. 0.2) more deterministic; higher values (e.g. 0.8) more random",
        "debug_mode": "🔍 Debug Mode",
        "debug_help": "Show debug info such as session state",
        "debug_info": "🐛 Debug Info",
        # Tabs
        "tab_chart": "🧮 Taiyi Chart",
        "tab_instructions": "💬 Instructions",
        "tab_history": "📜 Historical Examples",
        "tab_disaster": "🔥 Disaster Statistics",
        "tab_books": "📚 Ancient Books",
        "tab_updates": "🆕 Update Log",
        "tab_guide": "🚀 Chart Guide",
        "tab_links": "🔗 Links",
        # Main content
        "explanation": "Explanation",
        "taiyi_life_title": "Taiyi Life Method:",
        "twelve_palaces": "[Twelve Palaces Analysis]",
        "sixteen_gods": "[Taiyi Sixteen Gods Palace Positions]",
        "sixteen_grades": "[Taiyi Sixteen Gods Grades]",
        "hexagram": "[Hexagrams]",
        "year_hex": "Year Hexagram: ",
        "month_hex": "Month Hexagram: ",
        "day_hex": "Day Hexagram: ",
        "hour_hex": "Hour Hexagram: ",
        "minute_hex": "Minute Hexagram: ",
        "yang_nine": "[Yang Nine Cycle Limit]",
        "bai_liu": "[Bai Liu Cycle Limit]",
        "taiyi_mishu": "Taiyi Secret Book:",
        "history_records": "Historical Records:",
        "chart_analysis": "Taiyi Chart Analysis:",
        "year_star_predict": "Year Star Prediction: ",
        "start_star_predict": "Start Strike Star Prediction: ",
        "ten_stem_predict": "Ten Stems Start Strike Prediction: ",
        "sky_ground_method": "Taiyi Sky-Ground Method: ",
        "three_five": "Three Doors & Five Generals: ",
        "home_away": "Home vs Away Analysis: ",
        "win_loss": "Win-Loss Prediction: ",
        "wind_cloud": "Wind-Cloud Battle Support: ",
        "solitary": "Solitary Success-Failure: ",
        "yin_yang_adversity": "Yin-Yang Adversity: ",
        "emperor_tour": "Emperor Tour Period: ",
        "ruler_base": "Ruler Base Method: ",
        "minister_base": "Minister Base Method: ",
        "people_base": "People Base Method: ",
        "five_blessings": "Five Blessings Method: ",
        "five_blessings_calc": "Five Blessings Calculation: ",
        "heaven_yi": "Heaven Yi Method: ",
        "earth_yi": "Earth Yi Method: ",
        "zhifu": "Zhifu Method: ",
        "shi_geju": "Pattern Analysis: ",
        "sanqi": "Three Banners: ",
        "nine_gods": "Nine-Palace Noble Gods: ",
        "taiyi_stars": "Taiyi Nine Stars: ",
        "wenchang_stars": "Wenchang Nine Stars: ",
        "wuyun_liuqi": "Five Movements & Six Qi: ",
        "wuyin_shu": "Five-Tone Numbers: ",
        "junshi_vol5": "Military Strategy: ",
        "guxu_duizhao": "Gu-Xu Compare: ",
        "vol11": "State Disasters: ",
        "tongyun_rugua": "Cycle Hexagram: ",
        "liunian_zhigua": "Annual Hexagram: ",
        "liuyue_zhigua": "Monthly Hexagram: ",
        "liuri_zhigua": "Daily Hexagram: ",
        "liushi_zhigua": "Hourly Hexagram: ",
        "liufen_zhigua": "Minutely Hexagram: ",
        "ruyao_huofu": "Line Omen: ",
        "shier_yun": "Twelve-Cycle Table: ",
        "lishi_ruyao": "Historical Line Entries: ",
        "tongyun_detail": "Cycle Details",
        "gua_xiang": "Hexagram Image: ",
        "gua_xiang_detail": "Hexagram Details",
        "bian_gua_najia": "Changed Hexagram: ",
        "shouwei": "Cycle Boundaries: ",
        "hangzhi_biannian": "Historical Cycle: ",
        "tongyun_extended": "Cycle Extended",
        "tongyun_query_header": "Cycle Query",
        "tongyun_sync_chart": "Sync with chart year",
        "tongyun_sync_hint": "Cycle hexagram follows chart year {year}",
        "tongyun_query_year": "Cycle query year",
        "tongyun_query_note": "Cycle uses {query} (chart year {chart})",
        "tongyun_history_compare": "Historical cycle compare",
        "tongyun_exact_year": "Exact year",
        "tongyun_same_gua_yao": "Same hexagram/yao",
        "tongyun_near_examples": "Nearby examples",
        "tongyun_year_delta": "Δ {delta} yr",
        "yun_timeline_label": "Cycle · No.",
        "yun_per_cycle": "yr / cycle",
        "yun_years": "yr",
        "yun_yao_year": "Yao yr",
        "yun_gua_year": "Gua yr",
        "yun_ce": "Ce",
        "yun_cycle": "Cycle",
        "yun_expand_huofu": "Expand full yao fortune text",
        "yun_ganzhi": "Stem-Branch",
        "yun_year_suffix": "",
        "yun_zhigua": "Direct hexagram",
        "yun_yao_suffix": "",
        "yun_mff": "Yao method",
        "yun_ben_bian": "Origin→Changed",
        "yun_dong_yao": "Moving yao",
        "yun_najia": "Najia",
        "yun_fangwei": "Direction",
        "yun_fenye": "Domain",
        "yun_xiang_yue": "Image says",
        "yun_yao_guanxiang": "Yao observation",
        "hex_xiang_yue": "Image says",
        "hex_zongshu": "Hexagram overview",
        "hex_yao_ci": "Moving Yao Text",
        "liuri_label": "Daily Hexagram Flow",
        "liunian_label": "Yearly Hexagram Flow",
        "liuyue_label": "Monthly Hexagram Flow",
        "liushi_label": "Hourly Hexagram Flow",
        "liufen_label": "Minutely Hexagram Flow",
        "liuri_scroll_hint": "← Scroll for future →",
        "star_distribution_label": "Star Distribution",
        "disaster_fenye_label": "Disasters & Domains",
        "qi_music_label": "Qi & Music",
        "fenye_label": "Territorial Divisions",
        "junshi_label": "Military Strategy",
        "wuyun_label": "Five Phases & Six Qi",
        "xingxian_label": "Cycle Limits",
        "guiyun_label": "Great/Small Rotation",
        "life_query_age": "Life chart age",
        "life_query_year": "Limit/year query",
        "fenye": "Territorial Divisions: ",
        "guiyun": "Major/Minor Wander Hexagrams: ",
        "guiyun_detail": "Orbit hexagram & tally details",
        "guiyun_chong": "Compound hexagram tallies",
        "guiyun_inner_outer": "Inner / outer entry",
        "guiyun_ce_ref": "Four images tally",
        "guiyun_limits": "Yang-9 / Bai-6 limits",
        "guiyun_xingyao": "Minor wander line omens",
        "guiyun_palace_years": "Major wander years in palace",
        "guiyun_gong_diff": "Palace hexagrams differ",
        "vol10_hehui": "Sky-Eye Conjunction: ",
        "yunqi": "Ten Spirits & Clouds: ",
        "yangjiu_xian": "Yang-Nine Limits: ",
        "bailiu_xian": "Hundred-Six Limits: ",
        "sixteen_palace": "Sixteen Palaces: ",
        "shiti_jinfu": "Ten Golden Odes: ",
        "mingfa_vol20": "[Vol.20 Life Method]",
        "fly_lu_ma": "Flying Prosperity/Horse Limits: ",
        "sanhe_he": "Triple Harmony & Stem Union: ",
        "palace_states": "Twelve Palace States: ",
        "qiou_sancai": "Odd-Even & Three Talents: ",
        "life_geju": "Life Chart Patterns: ",
        "bailiu_gua": "Bailiu Month/Day Hexagrams: ",
        "zhao_you": "Limit-Year Stars: ",
        "palace_state_detail": "Palace Details",
        "rugua_xian": "Bailiu Hexagram Limits: ",
        "yangjiu_sanxian": "Yangjiu Three Limits: ",
        "wangxian_lun": "Star Prosperity Songs: ",
        "zhao_you_detail": "Full limit-year songs",
        "zhao_you_count": "{n} songs matched",
        "zhao_you_scope_zhao": "Limit",
        "zhao_you_scope_you": "Year",
        "wangxian_detail": "Star Discourse",
        "feifu_sisha": "Flying Talisman Four Kills: ",
        "junshi_vol15": "Military Application: ",
        "wuzhen_bazhen_viz": "Five & Eight Formations",
        "five_formations": "Five-formation flags (home/away)",
        "five_formations_short": "Five",
        "eight_formations_short": "Eight",
        "wuzhen_reference": "Flag rules (calc digit)",
        "chubing_xiang_title": "Deploy direction",
        "bazhen_center": "Pivot",
        "side_home": "H",
        "side_away": "A",
        "junshi_vol17": "Military Divination: ",
        "shenjiang_suozhu": "Gods & Doors Meanings: ",
        # AI
        "ai_analyze_btn": "🔍 Analyze with AI",
        "ai_analyzing": "AI is analyzing the Taiyi chart...",
        "ai_key_missing": "CEREBRAS_API_KEY not set. Please set it in .streamlit/secrets.toml or environment variables.",
        "ai_error": "Error calling AI: {}",
        "ai_quota_exceeded": "⚠️ Cerebras API daily token quota exceeded. Please try again later or reduce the 'Max Generation Tokens' setting.",
        "ai_openai_quota_exceeded": "⚠️ OpenAI API quota exceeded or rate-limited. Please try again later.",
        "ai_xai_quota_exceeded": "⚠️ xAI API quota exceeded or rate-limited. Please try again later.",
        "ai_deepseek_quota_exceeded": "⚠️ DeepSeek API quota exceeded or rate-limited. Please try again later.",
        "ai_qwen_quota_exceeded": "⚠️ Qwen API quota exceeded or rate-limited. Please try again later.",
        "gen_error": "Error generating chart: {}",
        "ai_result": "AI Analysis Result",
        "list_label": "List",
        "save_error": "Error saving prompt: {}",
        # Chat
        "chat_header": "💬 AI Chat",
        "chat_placeholder": "Ask a question to the Taiyi AI master...",
        "chat_thinking": "AI is thinking...",
        "chat_welcome": "Hello! I'm the Taiyi AI assistant. Feel free to ask me anything about Taiyi divination.",
        "chat_clear": "🗑️ Clear Chat",
        # Game Theory
        "game_theory_toggle": "🎯 Enable Game Theory Analysis (Nash Equilibrium)",
        "game_theory_header": "Operations Research & Game Theory Analysis",
        "game_theory_payoff": "Zero-Sum Payoff Matrix (Home Perspective)",
        "game_theory_home_strategy": "Home Optimal Mixed Strategy",
        "game_theory_away_strategy": "Away Optimal Mixed Strategy",
        "game_theory_value": "Game Value (Expected Payoff)",
        "game_theory_lp": "LP Optimal Recommendation",
        "game_theory_winrate": "Home Win Assessment",
        "game_theory_computing": "⚙️ Computing Nash Equilibrium...",
        # Print labels
        "lunar_label": "Lunar",
        "taiyi_life_method": "Taiyi Life",
        "epoch_label": "Epoch",
        "home_calc": "Home Calc",
        "away_calc": "Away Calc",
        "set_calc": "Set Calc",
        "five_yuan": "Five Yuan Cycle",
        "acc_prefix": "Acc. ",
        "acc_suffix": " Count",
    },
}

OPTION_LABELS = {
    "en": {
        "時計太乙": "Hourly Taiyi",
        "年計太乙": "Yearly Taiyi",
        "月計太乙": "Monthly Taiyi",
        "日計太乙": "Daily Taiyi",
        "分計太乙": "Minute Taiyi",
        "太乙命法": "Taiyi Life Method",
        "太乙命法 (魔改)": "Taiyi Life (Modified)",
        "太乙統宗": "Taiyi Tongzong",
        "太乙金鏡": "Taiyi Jinjing",
        "太乙淘金歌": "Taiyi Taojin Song",
        "太乙局": "Taiyi Bureau",
        "有": "Yes",
        "無": "No",
        "男": "Male",
        "女": "Female",
        "固定": "Fixed",
        "轉動": "Rotating",
    },
}

def t(key):
    """Get translated UI text for the current language."""
    lang = st.session_state.get("lang", "zh")
    return TRANSLATIONS.get(lang, TRANSLATIONS["zh"]).get(key, key)

def to(option):
    """Translate a selectbox option value for display."""
    lang = st.session_state.get("lang", "zh")
    if lang == "zh":
        return option
    return OPTION_LABELS.get(lang, {}).get(option, option)

# Cerebras Model Options
# Maximum number of recent chat messages to include as context for the LLM
_MAX_CHAT_HISTORY = 20

CEREBRAS_MODEL_OPTIONS = [
    "gpt-oss-120b",
    "llama3.1-8b",
    "zai-glm-4.7",
]
CEREBRAS_MODEL_DESCRIPTIONS = {
    "gpt-oss-120b": "Cerebras: High-capacity open-source model for complex tasks.",
    "llama3.1-8b": "Cerebras: Light and fast for quick tasks.",
    "zai-glm-4.7": "Cerebras: GLM-based model for versatile analysis.",
}

OPENAI_MODEL_OPTIONS = [
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-4.1",
    "gpt-4.1-mini",
    "o4-mini",
]
OPENAI_MODEL_DESCRIPTIONS = {
    "gpt-4o-mini": "OpenAI: Affordable and capable for most tasks.",
    "gpt-4o": "OpenAI: Most capable multimodal model.",
    "gpt-4.1": "OpenAI: Latest GPT-4.1 model.",
    "gpt-4.1-mini": "OpenAI: Fast and cost-effective GPT-4.1 mini.",
    "o4-mini": "OpenAI: Compact reasoning model.",
}

# xAI (Grok) Model Options
XAI_BASE_URL = "https://api.x.ai/v1"
XAI_MODEL_OPTIONS = [
    "grok-3",
    "grok-3-mini",
    "grok-2-1212",
]
XAI_MODEL_DESCRIPTIONS = {
    "grok-3": "xAI: Most capable Grok model for complex reasoning.",
    "grok-3-mini": "xAI: Fast and cost-effective Grok model.",
    "grok-2-1212": "xAI: Previous-generation Grok model.",
}

# DeepSeek Model Options
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL_OPTIONS = [
    "deepseek-chat",
    "deepseek-reasoner",
]
DEEPSEEK_MODEL_DESCRIPTIONS = {
    "deepseek-chat": "DeepSeek: V3 model, fast and capable for most tasks.",
    "deepseek-reasoner": "DeepSeek: R1 reasoning model for complex analysis.",
}

# Qwen (Alibaba DashScope) Model Options
QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
QWEN_MODEL_OPTIONS = [
    "qwen-max",
    "qwen-plus",
    "qwen-turbo",
    "qwen-long",
]
QWEN_MODEL_DESCRIPTIONS = {
    "qwen-max": "Qwen: Most capable Qwen model for complex tasks.",
    "qwen-plus": "Qwen: Balanced performance and cost.",
    "qwen-turbo": "Qwen: Fast and lightweight.",
    "qwen-long": "Qwen: Optimized for long-context tasks.",
}

# System Prompt Management Functions
@st.cache_data(show_spinner=False)
def load_system_prompts():
    SYSTEM_PROMPTS_FILE = os.path.join(_REPO_ROOT, "assets", "system_prompts.json")
    DEFAULT_SYSTEM_PROMPT = (
        "你是一位太乙神數大師，熟悉《太乙秘書》、《太乙命法》歷史案例。請根據提供的太乙排盤數據，進行以下操作：\n"
        "1. 解釋盤局的關鍵要素（主筭、客筭、始擊、太歲等）。\n"
        "2. 結合《太乙秘書》中的理論，分析盤局的吉凶和潛在影響。\n"
        "3. 若為太乙命法，評估命主的運勢和人生趨勢。\n"
        "4. 提供實用的建議或應對策略。\n"
        "請以清晰的結構（分段、標題）呈現，語言專業且易懂，適當引用歷史案例或經典理論。"
    )
    
    try:
        with open(SYSTEM_PROMPTS_FILE, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError):
        default_data = {
            "prompts": [
                {
                    "name": "太乙大師",
                    "content": DEFAULT_SYSTEM_PROMPT
                }
            ],
            "selected": "太乙大師"
        }
        with open(SYSTEM_PROMPTS_FILE, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=2, ensure_ascii=False)
        return default_data

def save_system_prompts(prompts_data):
    SYSTEM_PROMPTS_FILE = os.path.join(_REPO_ROOT, "assets", "system_prompts.json")
    try:
        with open(SYSTEM_PROMPTS_FILE, "w", encoding="utf-8") as f:
            json.dump(prompts_data, f, indent=2, ensure_ascii=False)
        load_system_prompts.clear()
        return True
    except Exception as e:
        st.error(t("save_error").format(e))
        return False

# Initialize session state to control rendering
if 'render_default' not in st.session_state:
    st.session_state.render_default = True

@st.cache_data
def get_file_content_as_string(base_url, path):
    """從指定 URL 獲取文件內容並返回字符串"""
    url = base_url + path
    try:
        response = urllib.request.urlopen(url)
        return response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return f"⚠️ 無法載入內容 ({url}): HTTP {e.code}"
    except Exception as e:
        return f"⚠️ 無法載入內容 ({url}): {e}"

def format_text(d, parent_key=""):
    """格式化字典為可讀的文本"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(format_text(v, new_key + ":").splitlines())
        elif isinstance(v, list):
            items.append(f"{new_key}: {', '.join(map(str, v))}")
        else:
            items.append(f"{new_key}: {v}")
    return "\n\n".join(items) + "\n\n"

def format_taiyi_results_for_prompt(results):
    """Format Taiyi calculation results into a prompt for the AI model."""
    prompt_lines = [
        "以下是太乙排盤的計算結果，請根據這些數據提供詳細的分析和解釋：",
        f"日期時間: {results['gz']} (農曆: {results['lunard']})",
        f"紀元: {results['ttext'].get('紀元', '無')}",
        f"局式: {results['ttext'].get('局式', {}).get('年', '無')}",
        f"太乙計: {config.ty_method(results['tn'])}{results['ttext'].get('太乙計', '')}",
        f"文: {results['kook'].get('文', '無')}",
        f"數: {results['kook_num']}",
        f"主筭: {results['homecal']}, 客筭: {results['awaycal']}, 定筭: {results['setcal']}",
        f"始擊值宿: {results['sj_su_predict']}",
        f"十天干歲始擊落宮: {results['tg_sj_su_predict']}",
        f"太歲值宿: {results['year_predict']}",
        f"三門五將: {results['three_door']} {results['five_generals']}",
        #f"推太乙在天外地內法: {results['ty'].ty_gong_dist(results['style'], results['tn'])}",
        f"推少多以占勝負: {results['ttext'].get('推少多以占勝負', '無')}",
        f"推太乙風雲飛鳥助戰: {results['home_vs_away3']}",
        f"《太乙秘書》: {results['ts']}",
        f"史事記載: {results['ch']}",
    ]
    if _is_life_chart_style(results["style"]):
        prompt_lines.extend([
            f"命法性別: {results['zhao']} ({results['sex_o']})",
            f"十二宮分析: {results['lifedisc']}",
            f"太乙十六神落宮: {results['lifedisc2']}",
        ])
    return "\n\n".join(prompt_lines)

def _chart_visual_text():
    """Visual copy for the Taiyi chart shell, aligned with the current language."""
    if st.session_state.get("lang", "zh") == "en":
        return {
            "heading": "Taiyi Divine Chart",
            "subheading": "Classical cosmology · digital observatory plate",
            "legend_title": "Legend",
            "legend_gold": "Imperial gold · auspicious force / honored positions",
            "legend_cinnabar": "Cinnabar · warnings / fierce emphasis",
            "legend_jade": "Jade green · manual focus markers",
            "legend_ivory": "Ivory · labels, symbols, and fine inscriptions",
            "interaction_title": "Interaction",
            "rotation_hint": "Drag rings 3–5 to rotate together; tap a sector to sync-highlight.",
            "sector_panel_title": "Sector Reading",
            "sector_panel_empty": "No reading for this sector.",
            "sector_panel_geju": "Patterns (釋格局)",
            "sector_panel_close": "Close",
            "reset": "Reset View",
            "download_png": "Download Plate",
            "toggle_geju_follow": "Patterns Follow",
            "toggle_geju_fixed": "Patterns Fixed",
            "add_note": "Add Note",
        "toggle_style_dense": "Data-Dense",
        "toggle_style_compact": "Compact",
        "toggle_style_traditional": "Traditional",
        "toggle_wuxing_color": "Five-Element Colors",
        "toggle_wuxing_traditional": "Traditional Style",
            "tooltip_fallback": "Taiyi sector",
            "chart_kind": "Chart",
            "export_title": "Taiyi Plate",
            "follow_label": "Follow the official account",
            "divination_note_label": "Query",
            "divination_note_prompt": "Save a divination note for the export card:",
            "bureau": "Bureau",
            "method": "Method",
            "stem_branch": "Stem-Branch",
            "kook_number": "Bureau Number",
            "lunar": "Lunar",
            "yin_yang": "Yin/Yang",
            "calc_triplet": "Home / Away / Set",
            "life_style": "Life Type",
            "five_yuan": "Five Cycles",
        }
    return {
        "heading": "太乙神數 盤式",
        "subheading": "古法推演 · 數位天文盤",
        "legend_title": "圖例",
        "legend_gold": "帝王金 · 吉象、尊位、核心天機",
        "legend_cinnabar": "朱砂赤 · 凶象、警示、重點標記",
        "legend_jade": "柔翠綠 · 手動點選的觀盤記號",
        "legend_ivory": "象牙白 · 盤面文字與細部刻記",
        "interaction_title": "互動",
        "rotation_hint": "拖曳第 3、4、5 層可聯動旋轉；輕點扇區則聯動著色。",
        "sector_panel_title": "扇區斷事",
        "sector_panel_empty": "此扇區尚無斷事資料。",
        "sector_panel_geju": "釋格局",
        "sector_panel_close": "關閉",
        "reset": "重置視圖",
        "download_png": "下載盤式",
        "toggle_geju_follow": "格局跟盤",
        "toggle_geju_fixed": "格局固定",
        "add_note": "加入文字",
        "toggle_style_dense": "資料密集",
        "toggle_style_compact": "簡盤",
        "toggle_style_traditional": "傳統風格",
        "toggle_wuxing_color": "五行彩色",
        "toggle_wuxing_traditional": "傳統著色",
        "tooltip_fallback": "太乙盤位",
        "chart_kind": "盤式",
        "export_title": "太乙式盤",
        "follow_label": "關注公眾號",
        "divination_note_label": "占問",
        "divination_note_prompt": "請輸入要儲存到盤式圖片的占問文字：",
        "bureau": "局式",
        "method": "太乙計",
        "stem_branch": "干支",
        "kook_number": "局數",
        "lunar": "農曆",
        "yin_yang": "陰陽",
        "calc_triplet": "主 / 客 / 定",
        "life_style": "命式",
        "five_yuan": "五子元",
    }


@st.cache_data(show_spinner=False)
def _load_export_qrcode_data_uri() -> str:
    """Load the public account QR code as a data URI for export cards."""
    candidates = [
        os.path.join(_REPO_ROOT, "pic", "qrcode_for_gh_561840f80b67_258.png"),
        os.path.join(_REPO_ROOT, "pic", "qrcode_for_gh_561840f80b67_258.jpg"),
    ]
    for path in candidates:
        if not os.path.exists(path):
            continue
        ext = os.path.splitext(path)[1].lower()
        mime = "image/png" if ext == ".png" else "image/jpeg"
        with open(path, "rb") as file_obj:
            encoded = base64.b64encode(file_obj.read()).decode("ascii")
        return f"data:{mime};base64,{encoded}"
    return ""


def _build_chart_meta(
    results: dict,
    is_life_chart: bool,
    *,
    show_geju_markers: bool = True,
    show_guxu_overlay: bool = True,
    wuxing_color: bool = True,
) -> dict:
    """Assemble display-only metadata for the Taiyi chart header/legend."""
    ui = _chart_visual_text()
    ty_instance = results.get("ty")
    year = getattr(ty_instance, "year", 0)
    month = getattr(ty_instance, "month", 0)
    day = getattr(ty_instance, "day", 0)
    hour = getattr(ty_instance, "hour", 0)
    minute = getattr(ty_instance, "minute", 0)
    bureau_name = results.get("ttext", {}).get("局式", {}).get("年", "") or results.get("kook", {}).get("文", "")
    method_name = f"{config.ty_method(results.get('tn', 0))}{results.get('ttext', {}).get('太乙計', '')}".strip()
    chart_title = (
        f"{results.get('zhao', '')} · {_life_method_label(results.get('style', 6))}"
        if is_life_chart
        else (bureau_name or ui["chart_kind"])
    )
    subtitle_bits = [ui["subheading"], results.get("gz", ""), results.get("lunard", "")]
    info_chips = [
        (ui["bureau"], bureau_name or "—"),
        (ui["method"], method_name or "—"),
        (ui["stem_branch"], results.get("gz", "—")),
        (ui["lunar"], results.get("lunard", "—")),
        (ui["yin_yang"], f"{results.get('kook', {}).get('文', '—')} · {results.get('kook_num', '—')}"),
        (ui["calc_triplet"], f"{results.get('homecal', '—')} / {results.get('awaycal', '—')} / {results.get('setcal', '—')}"),
    ]
    if is_life_chart:
        info_chips.insert(1, (ui["life_style"], results.get("zhao", "—")))
    elif results.get("wuyuan"):
        info_chips.append((ui["five_yuan"], results.get("wuyuan", "—")))

    highlights = [
        "太乙", "主筭", "客筭", "定筭",
        str(results.get("homecal", "")),
        str(results.get("awaycal", "")),
        str(results.get("setcal", "")),
    ]
    acc_style = (
        results.get("plate_ji", 3) if is_life_chart else results.get("style", 0)
    )
    acc_tn = 0 if is_life_chart else results.get("tn", 0)
    ty_obj = results.get("ty")
    chart_style_label = {
        0: "年計",
        1: "月計",
        2: "日計",
        3: "時計",
        4: "分計",
        5: "命法(魔改)",
        6: "命法",
    }.get(results.get("style", 0), "太乙")
    kook_num = results.get("kook_num", "")
    kook_num_text = an2cn(kook_num) if isinstance(kook_num, (int, float)) else str(kook_num)
    datetime_text = config.gendatetime(year, month, day, hour, minute)
    acc_text = f"{t('acc_prefix')}{config.taiyi_name(acc_style)[0]}{t('acc_suffix')}︰{ty_obj.accnum(acc_style, acc_tn)}"
    lunar_line = f"{t('lunar_label')}︰{results.get('lunard', '—')} | {jieqi.jq(year, month, day, hour, minute)} |"
    if is_life_chart:
        kook_line = (
            f"{_life_method_label(results.get('style', 6))} - {ty_obj.kook(0, 0).get('文', '—')} "
            f"({results.get('ttext', {}).get('局式', {}).get('年', '—')})"
        )
        summary_line = (
            f"{t('epoch_label')}︰{results.get('ttext', {}).get('紀元', '')} | "
            f"{t('home_calc')}︰{results.get('homecal', '—')} {t('away_calc')}︰{results.get('awaycal', '—')} |"
        )
    else:
        kook_line = (
            f"{method_name} - {results.get('kook', {}).get('文', '—')}"
            f"({results.get('ttext', {}).get('局式', {}).get('年', '—')})"
        )
        summary_line = (
            f"{t('five_yuan')}:{results.get('wuyuan', '')} | {t('epoch_label')}︰{results.get('ttext', {}).get('紀元', '')} | "
            f"{t('home_calc')}︰{results.get('homecal', '—')} {t('away_calc')}︰{results.get('awaycal', '—')} "
            f"{t('set_calc')}︰{results.get('setcal', '—')} |"
        )
    export_title = (
        f"堅太乙{chart_style_label}排盤 Kintaiyi Chart"
        if chart_style_label == "命法"
        else f"堅太乙{chart_style_label}排盤 Kintaiyi Chart"
    )
    export_lines = [
        f"{datetime_text} · {results.get('gz', '—')}",
        f"{kook_line}",
        f"{t('home_calc')} {results.get('homecal', '—')}  /  {t('away_calc')} {results.get('awaycal', '—')}  /  {t('set_calc')} {results.get('setcal', '—')}",
    ]
    if not is_life_chart and results.get("wuyuan"):
        export_lines.insert(2, f"{t('five_yuan')}：{results.get('wuyuan', '')} · {t('epoch_label')}︰{results.get('ttext', {}).get('紀元', '')}")
    else:
        export_lines.insert(2, f"{t('epoch_label')}︰{results.get('ttext', {}).get('紀元', '')}")

    chart_style = results.get("style", 6) if is_life_chart else results.get("style", 0)
    ttext = _display_ttext(results) if not is_life_chart else (results.get("ttext") or {})
    chart_view = build_chart_view_model(
        ttext,
        chart_style=chart_style,
        is_life=is_life_chart,
        life1=results.get("life1"),
        life_pan=results.get("life_pan"),
        sex=results.get("sex_o"),
        ty=ty_obj,
        tn=results.get("tn", 0),
    )
    mishu_text = results.get("ts") or ""
    geju_markers = (
        build_geju_sector_markers(ttext, mishu_text=mishu_text)
        if show_geju_markers
        else {}
    )
    _raw_svg = results.get("genchart1" if is_life_chart else "genchart2") or ""
    view_half = _svg_view_half(_raw_svg, 500)
    geju_overlay_svg = (
        build_geju_overlay_svg(
            ttext,
            chart_style=chart_style,
            is_life=is_life_chart,
            view_half=view_half,
            mishu_text=mishu_text,
        )
        if show_geju_markers
        else ""
    )
    guxu_model = build_guxu_chart_model(ttext) if show_guxu_overlay and not is_life_chart else None
    guxu_overlay_svg = (
        build_guxu_overlay_svg(
            ttext,
            chart_style=chart_style,
            is_life=is_life_chart,
            view_half=view_half,
        )
        if show_guxu_overlay and not is_life_chart
        else ""
    )
    chart_layout = chart_svg_layout(chart_style, is_life=is_life_chart)
    chart_layout = {
        **chart_layout,
        "guxu_rotate_layer": guxu_rotate_layer(chart_style, is_life=is_life_chart),
    }
    ui_out = dict(ui)
    is_en = st.session_state.get("lang", "zh") == "en"
    rotate_layers = chart_layout.get("rotate_layers") or []
    if rotate_layers:
        rot_nums = "、".join(lid.replace("layer", "") for lid in rotate_layers)
        ui_out["rotation_hint"] = (
            f"Drag rings {rot_nums} together to rotate; tap a sector to sync-highlight."
            if is_en
            else f"拖曳第{rot_nums}層可聯動旋轉；輕點扇區則聯動著色。"
        )
    else:
        ui_out["rotation_hint"] = (
            "This chart style does not support rotation."
            if is_en
            else "此盤式不支援轉盤旋轉。"
        )
    # ── 直符所在宮位的 sector key（用於初始化時自動開啟）──
    _zhifu_branch = ttext.get("直符") or ""
    _SIXTEEN_BRANCHES = ("巳", "午", "未", "坤", "申", "酉", "戌", "乾", "亥", "子", "丑", "艮", "寅", "卯", "辰", "巽")
    _zhifu_sector_key = ""
    if isinstance(_zhifu_branch, str) and _zhifu_branch in _SIXTEEN_BRANCHES:
        _zhifu_sector_key = f"layer4:{_SIXTEEN_BRANCHES.index(_zhifu_branch)}"

    sector_panel = {
        "sectors": chart_view.get("sectors") or {},
        "geju": geju_markers,
        "guxu": build_guxu_sector_hints(guxu_model) if guxu_model else {},
        "layer_labels": sector_panel_layer_labels(
            is_life=is_life_chart, chart_style=chart_style,
        ),
        "layer2_gongs": _layer2_gong_order(ttext) if not is_life_chart else [],
        "gong_by_branch": {
            br: config.gong2.get(br)
            for br in config.sixteen
            if config.gong2.get(br)
        },
        "gong_names": {
            str(i): config.num2gong(i) or ""
            for i in (1, 2, 3, 4, 6, 7, 8, 9)
        },
        "zhifu_sector_key": _zhifu_sector_key,
    }

    return {
        "heading": ui["heading"],
        "title": chart_title,
        "subtitle": " · ".join([bit for bit in subtitle_bits if bit]),
        "chips": [(label, value) for label, value in info_chips if value],
        "legend": [
            ("gold", ui["legend_gold"]),
            ("cinnabar", ui["legend_cinnabar"]),
            ("jade", ui["legend_jade"]),
            ("ivory", ui["legend_ivory"]),
        ],
        "highlights": highlights,
        "chart_view": chart_view,
        "geju_markers": geju_markers,
        "geju_overlay_svg": geju_overlay_svg,
        "guxu_overlay_svg": guxu_overlay_svg,
        "show_geju_markers": show_geju_markers,
        "show_guxu_overlay": show_guxu_overlay and not is_life_chart,
        "wuxing_color": wuxing_color,
        "chart_layout": chart_layout,
        "sector_panel": sector_panel,
        "export_title": export_title,
        "export_lines": export_lines,
        "export_follow_label": "關注「探究三式」微信公眾號 / 微信 gnatnek",
        "export_qrcode": _load_export_qrcode_data_uri(),
        "export_storage_key": hashlib.md5(
            f"{export_title}|{results.get('gz', '')}|{results.get('lunard', '')}|{results.get('style', '')}|{results.get('tn', '')}|{is_life_chart}".encode("utf-8")
        ).hexdigest(),
        "ui": ui_out,
    }


def _prepare_svg_markup(svg: str, svg_id: str, num: int, aria_label: str) -> str:
    """Normalize the incoming SVG root so CSS/JS can enhance the original chart safely."""
    svg_markup = re.sub(r"^\s*<\?xml[^>]*>\s*", "", svg.strip(), flags=re.IGNORECASE)
    match = re.search(r"<svg\b([^>]*)>", svg_markup, flags=re.IGNORECASE)
    if not match:
        return svg_markup

    attrs = match.group(1)
    attrs = re.sub(
        r'\s(?:id|class|width|height|style|preserveAspectRatio|role|aria-label)="[^"]*"',
        "",
        attrs,
        flags=re.IGNORECASE,
    ).strip()
    if "viewBox=" not in attrs:
        attrs = f'{attrs} viewBox="0 0 {num} {num}"'.strip()
    if "xmlns=" not in attrs:
        attrs = f'{attrs} xmlns="http://www.w3.org/2000/svg"'.strip()

    opening = (
        f'<svg {attrs} id="{svg_id}" class="taiyi-svg-root" width="100%" height="100%" '
        f'preserveAspectRatio="xMidYMid meet" role="img" aria-label="{html_escape(aria_label, quote=True)}">'
    )
    return re.sub(r"<svg\b[^>]*>", opening, svg_markup, count=1, flags=re.IGNORECASE)


def _chart_svg_with_geju(raw_svg: str, chart_meta: dict) -> str:
    """Pre-inject geju / guxu overlays into chart SVG before Streamlit renders it."""
    svg = mark_wenchang_spots_in_svg(raw_svg)
    if chart_meta.get("show_geju_markers"):
        svg = _inject_chart_overlay(svg, chart_meta.get("geju_overlay_svg", ""), "taiyi-geju-overlay")
    if chart_meta.get("show_guxu_overlay"):
        svg = _inject_chart_overlay(svg, chart_meta.get("guxu_overlay_svg", ""), "taiyi-guxu-overlay")
    return svg


def _inject_chart_overlay(svg_markup: str, overlay_svg: str, marker_class: str) -> str:
    """Append server-rendered overlay group before the closing </svg> tag."""
    if not overlay_svg or marker_class not in overlay_svg:
        return svg_markup
    if marker_class in svg_markup:
        return svg_markup
    lower = svg_markup.lower()
    closing = lower.rfind("</svg>")
    if closing < 0:
        return svg_markup
    return svg_markup[:closing] + overlay_svg + svg_markup[closing:]


def _svg_view_half(svg: str, fallback: int) -> float:
    """Parse viewBox half-width for geju label radius (origin=center charts)."""
    match = re.search(r'viewBox="([^"]+)"', svg, flags=re.IGNORECASE)
    if not match:
        return float(fallback) / 2.0
    parts = match.group(1).replace(",", " ").split()
    if len(parts) >= 4:
        try:
            width = abs(float(parts[2]))
            return width / 2.0
        except ValueError:
            pass
    return float(fallback) / 2.0


def _sanqi_flag_chart_css(scope: str = ".taiyi-svg-root") -> str:
    """三旗行宮：太陰黑旗在深底／PNG 匯出須保留金邊與可見填色。"""
    return f"""
    {scope} path.taiyi-sanqi-flag-banner.taiyi-sanqi-flag-black {{
        fill: #1e2438 !important;
        stroke: #d7bd6f !important;
        stroke-width: 1.6 !important;
    }}
    {scope} path.taiyi-sanqi-flag-pole.taiyi-sanqi-flag-black {{
        stroke: #d7bd6f !important;
        stroke-width: 1.5 !important;
    }}
    {scope} path.taiyi-sanqi-flag-banner:not(.taiyi-sanqi-flag-black) {{
        stroke: #e9cc88 !important;
        stroke-width: 1.1 !important;
    }}
    {scope} path.taiyi-sanqi-flag-pole:not(.taiyi-sanqi-flag-black) {{
        stroke: #e9cc88 !important;
        stroke-width: 1.4 !important;
    }}
    """


def _chart_export_overlay_css(glow_id: str, scope: str = ".taiyi-svg-root") -> str:
    """Export rules shared by all style modes (孤虛／釋格局／文昌／重點高亮)."""
    return f"""
    {scope} .taiyi-guxu-border-inner {{
        fill: none !important;
        stroke: #4D8CFF !important;
        stroke-width: 2px !important;
        vector-effect: non-scaling-stroke;
    }}
    {scope} .taiyi-guxu-border-outer {{
        fill: none !important;
        stroke: #FFBF00 !important;
        stroke-width: 2px !important;
        vector-effect: non-scaling-stroke;
    }}
    {scope} .taiyi-guxu-arrow {{
        stroke: #FFB300 !important;
        stroke-width: 2.4px !important;
    }}
    {scope} .taiyi-guxu-label-inner,
    {scope} .taiyi-guxu-label-sky-inner {{
        fill: #4D8CFF !important;
    }}
    {scope} .taiyi-guxu-label-outer,
    {scope} .taiyi-guxu-label-sky-outer {{
        fill: #FFBF00 !important;
    }}
    {scope} .taiyi-guxu-label-attack {{
        fill: #FFD54F !important;
    }}
""" + geju_label_css().replace(".taiyi-svg-root", scope) + wenchang_spot_chart_css(scope) + f"""
    {scope} .taiyi-key-spot {{
        fill: #fdf5cf !important;
        font-weight: 700 !important;
    }}
    {scope} .taiyi-key-sector {{
        stroke: rgba(212, 175, 55, 0.95) !important;
        stroke-width: 2.3 !important;
    }}
    {scope} .taiyi-user-mark {{
        stroke: rgba(245, 240, 225, 0.92) !important;
        stroke-width: 2.1 !important;
    }}
    {scope} path.taiyi-user-mark,
    {scope} polygon.taiyi-user-mark,
    {scope} rect.taiyi-user-mark {{
        fill: var(--taiyi-user-fill) !important;
    }}
    {scope} .taiyi-user-label {{
        fill: #f5f0e1 !important;
        font-weight: 700 !important;
    }}
    {scope} .taiyi-key-spot,
    {scope} .taiyi-user-mark,
    {scope} .taiyi-key-sector {{ filter: url(#{glow_id}); }}
    """


def _chart_export_css_bundle(glow_id: str) -> dict[str, str]:
    """Per-mode SVG export CSS so downloaded PNG matches on-screen styling."""
    scope = ".taiyi-svg-root"
    shell = f"""
    {scope} {{
        background: radial-gradient(circle at 50% 44%, #1c2540 0%, #11172b 58%, #090c18 100%);
        border-radius: 50%;
    }}
    {scope} path, {scope} polygon, {scope} rect, {scope} circle, {scope} ellipse {{
        stroke: #d7bd6f !important;
        stroke-width: 1.2 !important;
        vector-effect: non-scaling-stroke;
    }}
    {scope} circle.taiyi-chart-bg {{
        stroke: none !important;
        fill: #141826 !important;
    }}
    {scope} circle.taiyi-ornament-ring {{
        stroke: rgba(199, 154, 78, 0.5) !important;
        stroke-width: 0.9 !important;
        fill: none !important;
    }}
    """ + _sanqi_flag_chart_css(scope)
    traditional_layers = f"""
    {scope} text, {scope} tspan {{
        fill: #f5f0e1 !important;
        font-family: "Noto Serif SC", "Source Han Serif", "KaiTi", serif !important;
        font-weight: 600 !important;
    }}
    {scope} .taiyi-sector > text {{
        font-size: 9px !important;
    }}
    {scope} #layer1 path, {scope} #layer1 circle, {scope} #layer1 ellipse {{
        fill: #c9a227 !important;
    }}
    {scope} #layer1 text, {scope} #layer1 tspan {{
        fill: #f5f0e1 !important;
        font-size: 11px !important;
        font-weight: 700 !important;
    }}
    {scope} #layer2 path, {scope} #layer2 polygon, {scope} #layer2 rect {{
        fill: rgba(20, 46, 68, 0.78) !important;
    }}
    {scope} #layer3 path, {scope} #layer3 polygon, {scope} #layer3 rect {{
        fill: rgba(10, 28, 43, 0.88) !important;
    }}
    {scope} #layer4 path, {scope} #layer4 polygon, {scope} #layer4 rect {{
        fill: rgba(15, 43, 62, 0.92) !important;
    }}
    {scope} #layer5 path, {scope} #layer5 polygon, {scope} #layer5 rect {{
        fill: rgba(31, 49, 78, 0.82) !important;
    }}
    {scope} #layer6 path, {scope} #layer6 polygon, {scope} #layer6 rect {{
        fill: rgba(17, 39, 56, 0.84) !important;
    }}
    {scope} #layer7 path, {scope} #layer7 polygon, {scope} #layer7 rect {{
        fill: rgba(8, 22, 40, 0.95) !important;
    }}
    """
    dense_overrides = f"""
    {scope} text, {scope} tspan {{
        font-size: 10px !important;
        letter-spacing: 0.02em;
    }}
    {scope} .taiyi-sector > text {{
        font-size: 9px !important;
    }}
    """
    wuxing_layers = (
        f"""
    {scope} text, {scope} tspan {{
        font-family: "Noto Serif SC", "Source Han Serif", "KaiTi", serif !important;
        font-size: 9.5px !important;
        font-weight: 600 !important;
        letter-spacing: 0.03em;
    }}
    {scope} .taiyi-sector > text {{
        font-size: 8.5px !important;
    }}
"""
        + wuxing_theme_chart_css(scope)
    )
    overlays = _chart_export_overlay_css(glow_id, scope)
    traditional = shell + traditional_layers + overlays
    return {
        "traditional": traditional,
        "dense": shell + traditional_layers + dense_overrides + overlays,
        "wuxing": shell + wuxing_layers + overlays,
    }


def _render_taiyi_chart(svg: str, num: int, chart_meta: dict, interactive: bool) -> None:
    """Render the Taiyi SVG inside a themed responsive shell without touching calculation logic."""
    if not svg or "svg" not in svg.lower():
        st.error("Invalid SVG content provided")
        return

    ui = chart_meta["ui"]
    sector_panel_json = json.dumps(
        chart_meta.get("sector_panel") or {},
        ensure_ascii=False,
        sort_keys=True,
    )
    component_key = hashlib.md5(
        f"{svg}|{interactive}|{chart_meta.get('show_geju_markers')}|"
        f"{chart_meta.get('geju_overlay_svg', '')}|{chart_meta.get('show_guxu_overlay')}|"
        f"{chart_meta.get('guxu_overlay_svg', '')}|{chart_meta.get('wuxing_color')}|"
        f"{sector_panel_json}".encode("utf-8")
    ).hexdigest()[:10]
    initial_style_mode = "wuxing" if chart_meta.get("wuxing_color") else "traditional"
    container_id = f"taiyi-shell-{component_key}"
    svg_id = f"taiyi-svg-{component_key}"
    glow_id = f"taiyi-glow-{component_key}"
    svg_markup = _chart_svg_with_geju(
        _prepare_svg_markup(svg, svg_id, num, chart_meta["title"]),
        chart_meta,
    )

    export_css_bundle = _chart_export_css_bundle(glow_id)
    export_css = export_css_bundle["traditional"]

    template = """
    <div id="__CONTAINER_ID__" class="taiyi-shell" data-style-mode="__INITIAL_STYLE_MODE__" data-interactive="__INTERACTIVE__">
        <div class="taiyi-card">
            <div class="taiyi-stage">
                <div class="taiyi-stage-frame">
                    <div class="taiyi-svg-backdrop" aria-hidden="true"></div>
                    __SVG_MARKUP__
                </div>
                <div class="taiyi-toolbar" aria-label="chart tools">
                    <button type="button" class="taiyi-btn" data-action="toggle-style">__STYLE_BUTTON__</button>
                    <button type="button" class="taiyi-btn taiyi-btn-optional" data-action="toggle-geju-follow" hidden>__TOGGLE_GEJU_FOLLOW__</button>
                    <button type="button" class="taiyi-btn" data-action="reset">__RESET__</button>
                    <button type="button" class="taiyi-btn" data-action="add-note">__ADD_NOTE__</button>
                    <button type="button" class="taiyi-btn" data-action="download-png">__DOWNLOAD_PNG__</button>
                </div>
                <div class="taiyi-sector-panel" hidden aria-live="polite">
                    <div class="taiyi-sector-panel-header">
                        <div class="taiyi-sector-panel-heading">
                            <span class="taiyi-sector-panel-layer"></span>
                            <strong class="taiyi-sector-panel-title"></strong>
                        </div>
                        <button type="button" class="taiyi-sector-panel-close" data-action="close-panel" aria-label="__PANEL_CLOSE__">×</button>
                    </div>
                    <ul class="taiyi-sector-panel-lines"></ul>
                    <div class="taiyi-sector-panel-geju"></div>
                </div>
            </div>
        </div>
    </div>

    <style>
    #__CONTAINER_ID__ {
        --bg-deep: #0d1b2a;
        --bg-panel: rgba(10, 22, 40, 0.94);
        --gold: #d4af37;
        --gold-strong: #c9a227;
        --cinnabar: #c41e3a;
        --ivory: #f5f0e1;
        --ivory-soft: #e8dfc8;
        --jade: #4a9c6d;
        --line: rgba(212, 175, 55, 0.35);
        --chart-max-width: 1100px;
        --shadow: 0 18px 50px rgba(0, 0, 0, 0.45);
        margin: 0;
        padding: 0;
        container-type: inline-size;
        color: var(--ivory);
        font-family: "Noto Serif SC", "Source Han Serif", "KaiTi", serif;
    }
    #__CONTAINER_ID__ * { box-sizing: border-box; }
    #__CONTAINER_ID__ .taiyi-card {
        position: relative;
        overflow: visible;
        border: 1px solid rgba(212, 175, 55, 0.62);
        border-radius: 22px;
        padding: 10px;
        background:
            radial-gradient(circle at 12% 16%, rgba(212, 175, 55, 0.13), transparent 30%),
            radial-gradient(circle at 88% 12%, rgba(196, 30, 58, 0.12), transparent 24%),
            linear-gradient(180deg, rgba(18, 33, 52, 0.98), rgba(10, 22, 40, 0.98));
        box-shadow: var(--shadow);
        isolation: isolate;
    }
    #__CONTAINER_ID__ .taiyi-card::before,
    #__CONTAINER_ID__ .taiyi-card::after {
        content: "";
        position: absolute;
        inset: 10px;
        border-radius: 18px;
        pointer-events: none;
    }
    /* 美學調整區 */
    #__CONTAINER_ID__ .taiyi-card::before {
        border: 1px solid rgba(212, 175, 55, 0.25);
        background:
            radial-gradient(circle at 10% 20%, rgba(245, 240, 225, 0.08) 0 1px, transparent 1.5px),
            radial-gradient(circle at 82% 24%, rgba(245, 240, 225, 0.08) 0 1px, transparent 1.5px),
            radial-gradient(circle at 26% 86%, rgba(245, 240, 225, 0.06) 0 1px, transparent 1.5px),
            radial-gradient(circle at 76% 78%, rgba(212, 175, 55, 0.08) 0 1px, transparent 1.5px);
        background-size: 160px 160px, 200px 200px, 180px 180px, 220px 220px;
        opacity: 0.9;
    }
    #__CONTAINER_ID__ .taiyi-card::after {
        inset: 3px;
        border: 1px solid rgba(212, 175, 55, 0.12);
    }
    #__CONTAINER_ID__ .taiyi-toolbar {
        position: relative;
        z-index: 2;
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 8px;
        width: min(100%, var(--chart-max-width));
        justify-content: center;
        align-items: center;
        margin-top: 6px;
        padding: 0 4px 0;
    }
    #__CONTAINER_ID__ .taiyi-toolbar.has-geju-follow {
        grid-template-columns: repeat(5, minmax(0, 1fr));
    }
    #__CONTAINER_ID__ .taiyi-btn {
        appearance: none;
        border: 1px solid rgba(212, 175, 55, 0.38);
        border-radius: 999px;
        background: linear-gradient(180deg, rgba(18, 37, 58, 0.82), rgba(9, 24, 38, 0.88));
        color: var(--ivory);
        font-family: inherit;
        font-size: 0.76rem;
        line-height: 1;
        padding: 9px 12px;
        cursor: pointer;
        transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease, color 180ms ease;
        box-shadow: 0 8px 18px rgba(0, 0, 0, 0.22);
        white-space: nowrap;
        width: 100%;
        min-width: 0;
        backdrop-filter: blur(8px);
    }
    #__CONTAINER_ID__ .taiyi-btn:hover {
        transform: translateY(-1px);
        color: var(--gold);
        border-color: rgba(212, 175, 55, 0.7);
        box-shadow: 0 10px 22px rgba(0, 0, 0, 0.28);
    }
    #__CONTAINER_ID__ .taiyi-btn.is-active {
        color: var(--gold);
        border-color: rgba(212, 175, 55, 0.78);
        box-shadow: 0 0 0 1px rgba(212, 175, 55, 0.18), 0 10px 22px rgba(0, 0, 0, 0.28);
    }
    #__CONTAINER_ID__ .taiyi-stage {
        position: relative;
        z-index: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
    }
    #__CONTAINER_ID__ .taiyi-stage-frame {
        position: relative;
        /* Square frame: width must not exceed available height (parent viewport
           minus topnav+tabs+toolbar+card-padding+toolbar+margin ~280px). This keeps
           the entire chart visible without any scrollbar — the square shrinks to fit. */
        width: min(100%, var(--chart-max-width), calc(var(--parent-vh, 100vh) - 280px));
        aspect-ratio: 1 / 1;
        overflow: visible;
        border-radius: 22px;
        border: 1px solid rgba(212, 175, 55, 0.34);
        background:
            radial-gradient(circle at 50% 50%, rgba(212, 175, 55, 0.09), transparent 42%),
            radial-gradient(circle at 52% 49%, rgba(245, 240, 225, 0.07), transparent 58%),
            linear-gradient(180deg, rgba(9, 21, 37, 0.98), rgba(5, 13, 23, 1));
        padding: clamp(14px, 3vw, 26px);
        display: flex;
        align-items: center;
        justify-content: center;
    }
    #__CONTAINER_ID__ .taiyi-svg-backdrop {
        position: absolute;
        inset: 10px;
        border-radius: 18px;
        pointer-events: none;
        background:
            radial-gradient(circle at center, rgba(212, 175, 55, 0.06) 0, transparent 46%),
            radial-gradient(circle at 28% 24%, rgba(245, 240, 225, 0.045), transparent 18%),
            radial-gradient(circle at 72% 74%, rgba(245, 240, 225, 0.04), transparent 16%);
    }
    #__CONTAINER_ID__ .taiyi-svg-root {
        position: relative;
        z-index: 1;
        display: block;
        width: 100% !important;
        height: auto !important;
        max-width: 100%;
        max-height: 920px;
        margin: 0 auto;
        overflow: visible;
        user-select: none;
        -webkit-user-select: none;
        touch-action: pan-x pan-y;
    }
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-colorable,
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-colorable > path,
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-colorable > polygon,
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-colorable > rect {
        touch-action: manipulation;
        -webkit-tap-highlight-color: transparent;
    }
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-sector > text,
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-sector > tspan {
        pointer-events: none;
    }
    #__CONTAINER_ID__ .taiyi-svg-root > circle {
        pointer-events: none;
    }
    #__CONTAINER_ID__ .taiyi-svg-root circle.taiyi-chart-bg {
        stroke: none !important;
        fill: #141826 !important;
    }
    #__CONTAINER_ID__ .taiyi-svg-root circle.taiyi-ornament-ring {
        stroke: rgba(199, 154, 78, 0.5) !important;
        stroke-width: 0.9 !important;
        fill: none !important;
    }
""" + _sanqi_flag_chart_css("#__CONTAINER_ID__ .taiyi-svg-root") + """
    #__CONTAINER_ID__ .taiyi-svg-root * {
        user-select: none;
        -webkit-user-select: none;
        vector-effect: non-scaling-stroke;
    }
    #__CONTAINER_ID__ .taiyi-svg-root path,
    #__CONTAINER_ID__ .taiyi-svg-root polygon,
    #__CONTAINER_ID__ .taiyi-svg-root rect,
    #__CONTAINER_ID__ .taiyi-svg-root circle,
    #__CONTAINER_ID__ .taiyi-svg-root ellipse {
        stroke: #d7bd6f !important;
        stroke-width: 1.2 !important;
        transition: fill 180ms ease, stroke 180ms ease, filter 180ms ease, opacity 180ms ease;
    }
    #__CONTAINER_ID__[data-style-mode="traditional"] .taiyi-svg-root text,
    #__CONTAINER_ID__[data-style-mode="traditional"] .taiyi-svg-root tspan,
    #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root text,
    #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root tspan {
        fill: var(--ivory) !important;
        font-family: "Noto Serif SC", "Source Han Serif", "KaiTi", serif !important;
        font-size: 9.5px !important;
        font-weight: 600 !important;
        letter-spacing: 0.03em;
        transition: fill 180ms ease, filter 180ms ease, opacity 180ms ease;
    }
    #__CONTAINER_ID__[data-style-mode="traditional"] .taiyi-svg-root .taiyi-sector > text,
    #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root .taiyi-sector > text {
        font-size: 8.5px !important;
    }
    #__CONTAINER_ID__[data-style-mode="wuxing"] .taiyi-svg-root text,
    #__CONTAINER_ID__[data-style-mode="wuxing"] .taiyi-svg-root tspan {
        font-family: "Noto Serif SC", "Source Han Serif", "KaiTi", serif !important;
        font-size: 9.5px !important;
        font-weight: 600 !important;
        letter-spacing: 0.03em;
        transition: fill 180ms ease, filter 180ms ease, opacity 180ms ease;
    }
    #__CONTAINER_ID__[data-style-mode="wuxing"] .taiyi-svg-root .taiyi-sector > text {
        font-size: 8.5px !important;
    }
""" + wuxing_theme_chart_css("#__CONTAINER_ID__[data-style-mode=\"wuxing\"] .taiyi-svg-root") + """
    #__CONTAINER_ID__[data-style-mode="traditional"] .taiyi-svg-root #layer1 path,
    #__CONTAINER_ID__[data-style-mode="traditional"] .taiyi-svg-root #layer1 polygon,
    #__CONTAINER_ID__[data-style-mode="traditional"] .taiyi-svg-root #layer1 rect,
    #__CONTAINER_ID__[data-style-mode="traditional"] .taiyi-svg-root #layer1 circle,
    #__CONTAINER_ID__[data-style-mode="traditional"] .taiyi-svg-root #layer1 ellipse,
    #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root #layer1 path,
    #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root #layer1 polygon,
    #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root #layer1 rect,
    #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root #layer1 circle,
    #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root #layer1 ellipse {
        fill: rgba(201, 162, 39, 0.94) !important;
        stroke: rgba(245, 240, 225, 0.82) !important;
        stroke-width: 1.8 !important;
    }
    #__CONTAINER_ID__[data-style-mode="traditional"] .taiyi-svg-root #layer1 text,
    #__CONTAINER_ID__[data-style-mode="traditional"] .taiyi-svg-root #layer1 tspan,
    #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root #layer1 text,
    #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root #layer1 tspan {
        fill: #f5f0e1 !important;
        font-size: 11px !important;
        font-weight: 700 !important;
    }
    #__CONTAINER_ID__[data-style-mode="traditional"] .taiyi-svg-root #layer2 path,
    #__CONTAINER_ID__[data-style-mode="traditional"] .taiyi-svg-root #layer2 polygon,
    #__CONTAINER_ID__[data-style-mode="traditional"] .taiyi-svg-root #layer2 rect,
    #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root #layer2 path,
    #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root #layer2 polygon,
    #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root #layer2 rect { fill: rgba(20, 46, 68, 0.78) !important; }
    #__CONTAINER_ID__[data-style-mode="traditional"] .taiyi-svg-root #layer3 path,
    #__CONTAINER_ID__[data-style-mode="traditional"] .taiyi-svg-root #layer3 polygon,
    #__CONTAINER_ID__[data-style-mode="traditional"] .taiyi-svg-root #layer3 rect,
    #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root #layer3 path,
    #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root #layer3 polygon,
    #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root #layer3 rect { fill: rgba(10, 28, 43, 0.88) !important; }
    #__CONTAINER_ID__[data-style-mode="traditional"] .taiyi-svg-root #layer4 path,
    #__CONTAINER_ID__[data-style-mode="traditional"] .taiyi-svg-root #layer4 polygon,
    #__CONTAINER_ID__[data-style-mode="traditional"] .taiyi-svg-root #layer4 rect,
    #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root #layer4 path,
    #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root #layer4 polygon,
    #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root #layer4 rect { fill: rgba(15, 43, 62, 0.92) !important; }
    #__CONTAINER_ID__[data-style-mode="traditional"] .taiyi-svg-root #layer5 path,
    #__CONTAINER_ID__[data-style-mode="traditional"] .taiyi-svg-root #layer5 polygon,
    #__CONTAINER_ID__[data-style-mode="traditional"] .taiyi-svg-root #layer5 rect,
    #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root #layer5 path,
    #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root #layer5 polygon,
    #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root #layer5 rect { fill: rgba(31, 49, 78, 0.82) !important; }
    #__CONTAINER_ID__[data-style-mode="traditional"] .taiyi-svg-root #layer6 path,
    #__CONTAINER_ID__[data-style-mode="traditional"] .taiyi-svg-root #layer6 polygon,
    #__CONTAINER_ID__[data-style-mode="traditional"] .taiyi-svg-root #layer6 rect,
    #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root #layer6 path,
    #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root #layer6 polygon,
    #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root #layer6 rect { fill: rgba(17, 39, 56, 0.84) !important; }
    #__CONTAINER_ID__[data-style-mode="traditional"] .taiyi-svg-root #layer7 path,
    #__CONTAINER_ID__[data-style-mode="traditional"] .taiyi-svg-root #layer7 polygon,
    #__CONTAINER_ID__[data-style-mode="traditional"] .taiyi-svg-root #layer7 rect,
    #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root #layer7 path,
    #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root #layer7 polygon,
    #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root #layer7 rect { fill: rgba(8, 22, 40, 0.95) !important; }
    #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root text,
    #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root tspan {
        font-size: 10px !important;
        letter-spacing: 0.02em;
    }
    #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root .taiyi-sector > text {
        font-size: 9px !important;
    }
    #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-stage-frame {
        padding: clamp(10px, 2.2vw, 20px);
    }
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-rotatable {
        cursor: grab;
        transform-box: fill-box;
        transform-origin: center;
        transition: transform 260ms cubic-bezier(0.22, 1, 0.36, 1);
        touch-action: pan-x pan-y;
    }
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-rotatable.is-dragging {
        cursor: grabbing;
        transition: none;
    }
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-colorable,
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-sector-panel-target {
        cursor: pointer;
    }
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-colorable > path,
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-colorable > polygon,
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-colorable > rect,
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-colorable-shape {
        pointer-events: all;
    }
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-sector-active path,
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-sector-active polygon,
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-sector-active rect {
        stroke: rgba(212, 175, 55, 0.98) !important;
        stroke-width: 2.6 !important;
        filter: url(#__GLOW_ID__);
    }
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-key-spot {
        fill: #fdf5cf !important;
        font-weight: 700 !important;
    }
""" + wenchang_spot_chart_css("#__CONTAINER_ID__ .taiyi-svg-root") + """
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-key-sector {
        stroke: rgba(212, 175, 55, 0.95) !important;
        stroke-width: 2.3 !important;
    }
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-user-mark {
        stroke: rgba(245, 240, 225, 0.92) !important;
        stroke-width: 2.1 !important;
    }
    #__CONTAINER_ID__ .taiyi-svg-root path.taiyi-user-mark,
    #__CONTAINER_ID__ .taiyi-svg-root polygon.taiyi-user-mark,
    #__CONTAINER_ID__ .taiyi-svg-root rect.taiyi-user-mark,
    #__CONTAINER_ID__ .taiyi-svg-root path[data-user-fill],
    #__CONTAINER_ID__ .taiyi-svg-root polygon[data-user-fill],
    #__CONTAINER_ID__ .taiyi-svg-root rect[data-user-fill] {
        opacity: 1 !important;
    }
    #__CONTAINER_ID__ .taiyi-svg-root #layer3 .taiyi-sector > path,
    #__CONTAINER_ID__ .taiyi-svg-root #layer4 .taiyi-sector > path,
    #__CONTAINER_ID__ .taiyi-svg-root #layer5 .taiyi-sector > path,
    #__CONTAINER_ID__ .taiyi-svg-root #layer3 .taiyi-sector > polygon,
    #__CONTAINER_ID__ .taiyi-svg-root #layer4 .taiyi-sector > polygon,
    #__CONTAINER_ID__ .taiyi-svg-root #layer5 .taiyi-sector > polygon,
    #__CONTAINER_ID__ .taiyi-svg-root #layer3 .taiyi-sector > rect,
    #__CONTAINER_ID__ .taiyi-svg-root #layer4 .taiyi-sector > rect,
    #__CONTAINER_ID__ .taiyi-svg-root #layer5 .taiyi-sector > rect {
        pointer-events: all !important;
        cursor: pointer;
    }
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-user-label {
        fill: #f5f0e1 !important;
        font-weight: 700 !important;
    }
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-geju-overlay,
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-guxu-overlay {
        pointer-events: none !important;
    }
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-geju-overlay *,
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-guxu-overlay * {
        pointer-events: none !important;
    }
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-geju-label {
        pointer-events: all !important;
        cursor: pointer;
        user-select: none;
        font-size: 9px !important;
        font-weight: 700 !important;
        letter-spacing: 0.04em;
    }
""" + geju_label_css().replace(".taiyi-svg-root", "#__CONTAINER_ID__ .taiyi-svg-root") + """
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-guxu-label {
        pointer-events: none;
        user-select: none;
        font-size: 9px !important;
        font-weight: 700 !important;
        letter-spacing: 0.04em;
    }
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-guxu-border-inner {
        fill: none !important;
        stroke: #4D8CFF !important;
        stroke-width: 2px !important;
        vector-effect: non-scaling-stroke;
    }
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-guxu-border-outer {
        fill: none !important;
        stroke: #FFBF00 !important;
        stroke-width: 2px !important;
        vector-effect: non-scaling-stroke;
    }
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-guxu-arrow {
        stroke: #FFB300 !important;
        stroke-width: 2.4px !important;
    }
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-guxu-label-inner,
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-guxu-label-sky-inner {
        fill: #4D8CFF !important;
    }
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-guxu-label-outer,
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-guxu-label-sky-outer {
        fill: #FFBF00 !important;
    }
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-guxu-label-attack {
        fill: #FFD54F !important;
    }
    #__CONTAINER_ID__ .taiyi-sector-panel {
        margin-top: 10px;
        padding: 12px 14px 10px;
        border: 1px solid rgba(212, 175, 55, 0.42);
        border-radius: 14px;
        background: linear-gradient(180deg, rgba(16, 30, 48, 0.96), rgba(8, 18, 34, 0.98));
        box-shadow: inset 0 1px 0 rgba(212, 175, 55, 0.12);
    }
    #__CONTAINER_ID__ .taiyi-sector-panel[hidden] {
        display: none !important;
    }
    #__CONTAINER_ID__ .taiyi-sector-panel-header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 10px;
        margin-bottom: 8px;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(212, 175, 55, 0.22);
    }
    #__CONTAINER_ID__ .taiyi-sector-panel-heading {
        display: flex;
        flex-direction: column;
        gap: 2px;
        min-width: 0;
    }
    #__CONTAINER_ID__ .taiyi-sector-panel-layer {
        font-size: 0.74rem;
        color: var(--gold);
        letter-spacing: 0.06em;
    }
    #__CONTAINER_ID__ .taiyi-sector-panel-title {
        font-size: 1.05rem;
        color: var(--ivory);
        font-weight: 700;
        line-height: 1.35;
        word-break: break-word;
    }
    #__CONTAINER_ID__ .taiyi-sector-panel-close {
        flex: 0 0 auto;
        width: 28px;
        height: 28px;
        border: 1px solid rgba(212, 175, 55, 0.45);
        border-radius: 999px;
        background: rgba(8, 18, 34, 0.85);
        color: var(--ivory-soft);
        font-size: 1.1rem;
        line-height: 1;
        cursor: pointer;
    }
    #__CONTAINER_ID__ .taiyi-sector-panel-lines {
        margin: 0;
        padding: 0 0 0 1.1rem;
        color: var(--ivory-soft);
        font-size: 0.88rem;
        line-height: 1.55;
    }
    #__CONTAINER_ID__ .taiyi-sector-panel-lines li + li {
        margin-top: 4px;
    }
    #__CONTAINER_ID__ .taiyi-sector-panel-lines li.taiyi-sector-panel-empty {
        list-style: none;
        margin-left: -1.1rem;
    }
    #__CONTAINER_ID__ .taiyi-sector-panel-empty {
        margin: 0;
        color: rgba(232, 223, 200, 0.72);
        font-size: 0.86rem;
    }
    #__CONTAINER_ID__ .taiyi-sector-panel-geju {
        margin-top: 10px;
        padding-top: 8px;
        border-top: 1px dashed rgba(212, 175, 55, 0.24);
    }
    #__CONTAINER_ID__ .taiyi-sector-panel-geju-title {
        font-size: 0.78rem;
        color: var(--gold);
        margin-bottom: 6px;
        letter-spacing: 0.05em;
    }
    #__CONTAINER_ID__ .taiyi-geju-panel-item {
        margin: 0 0 6px;
        padding: 6px 8px;
        border-radius: 8px;
        font-size: 0.84rem;
        line-height: 1.5;
        background: rgba(255, 255, 255, 0.03);
    }
    #__CONTAINER_ID__ .taiyi-geju-panel-item[data-tone="danger"] {
        border-left: 3px solid var(--cinnabar);
    }
    #__CONTAINER_ID__ .taiyi-geju-panel-item[data-tone="warn"] {
        border-left: 3px solid #c9a227;
    }
    #__CONTAINER_ID__ .taiyi-geju-panel-item[data-tone="caution"] {
        border-left: 3px solid #5b8fd0;
    }
    #__CONTAINER_ID__ .taiyi-geju-panel-item[data-tone="info"] {
        border-left: 3px solid #7e8fa3;
    }
    #__CONTAINER_ID__ .taiyi-geju-panel-item strong {
        color: var(--ivory);
        margin-right: 6px;
    }

    /* Responsive 調整區 */
    @container (max-width: 860px) {
        #__CONTAINER_ID__ .taiyi-stage-frame {
            padding: clamp(12px, 2.6vw, 18px);
        }
    }
    @media (max-width: 768px) {
        #__CONTAINER_ID__ { padding-top: 0; padding-bottom: 0; }
        #__CONTAINER_ID__ .taiyi-card {
            border-radius: 18px;
            padding: 3px;
        }
        #__CONTAINER_ID__ .taiyi-card::before { inset: 6px; }
        #__CONTAINER_ID__ .taiyi-btn {
            width: 100%;
            text-align: center;
        }
        #__CONTAINER_ID__ .taiyi-toolbar {
            grid-template-columns: repeat(2, minmax(0, 1fr));
            justify-content: stretch;
            align-self: stretch;
        }
        #__CONTAINER_ID__ .taiyi-stage-frame {
            width: 100%;
            padding: 3px;
        }
        #__CONTAINER_ID__ .taiyi-svg-root {
            max-width: 100%;
            touch-action: pan-x pan-y;
        }
        #__CONTAINER_ID__ .taiyi-svg-root .taiyi-rotatable {
            touch-action: pan-x pan-y;
        }
        #__CONTAINER_ID__ .taiyi-svg-root .taiyi-colorable,
        #__CONTAINER_ID__ .taiyi-svg-root .taiyi-colorable > path,
        #__CONTAINER_ID__ .taiyi-svg-root .taiyi-colorable > polygon,
        #__CONTAINER_ID__ .taiyi-svg-root .taiyi-colorable > rect,
        #__CONTAINER_ID__ .taiyi-svg-root .taiyi-colorable-shape {
            touch-action: manipulation !important;
        }
        #__CONTAINER_ID__ .taiyi-svg-root text,
        #__CONTAINER_ID__ .taiyi-svg-root tspan {
            font-size: 12px !important;
        }
        #__CONTAINER_ID__ .taiyi-svg-root .taiyi-sector > text {
            font-size: 11px !important;
        }
        #__CONTAINER_ID__ .taiyi-svg-root #layer1 text,
        #__CONTAINER_ID__ .taiyi-svg-root #layer1 tspan {
            font-size: 13.5px !important;
        }
        #__CONTAINER_ID__ .taiyi-svg-root .taiyi-geju-label,
        #__CONTAINER_ID__ .taiyi-svg-root .taiyi-guxu-label {
            font-size: 11px !important;
        }
        #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root text,
        #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root tspan {
            font-size: 11.5px !important;
        }
        #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root .taiyi-sector > text {
            font-size: 10.5px !important;
        }
    }
    </style>

    <script>
    (() => {
        try {
        const root = document.getElementById("__CONTAINER_ID__");
        if (!root) return;
        if (root.dataset.bound === "true") return;
        root.dataset.bound = "true";

        const svg = root.querySelector(".taiyi-svg-root");
        if (!svg) return;

        // Inject parent viewport height so the chart square can shrink to fit
        // the visible area — no scrollbar needed.
        try {
            const pvh = window.parent.innerHeight || window.innerHeight || 0;
            if (pvh > 0) {
                root.style.setProperty("--parent-vh", pvh + "px");
            }
        } catch (e) { /* cross-origin */ }

        const interactive = "__INTERACTIVE__" === "true";
        const ui = __UI_JSON__;
        const highlightTerms = __HIGHLIGHTS_JSON__;
        const exportMeta = __EXPORT_META_JSON__;
        const chartLayout = __CHART_LAYOUT_JSON__;
        const sectorPanelData = __SECTOR_PANEL_JSON__;
        const initialWuxingColor = __WUXING_COLOR__ === true || __WUXING_COLOR__ === "true";
        const sectorLookup = sectorPanelData.sectors || {};
        const gejuByGong = sectorPanelData.geju || {};
        const guxuByBranch = sectorPanelData.guxu || {};
        const layerLabels = sectorPanelData.layer_labels || {};
        const layer2Gongs = sectorPanelData.layer2_gongs || [];
        const gongByBranch = sectorPanelData.gong_by_branch || {};
        const gongNames = sectorPanelData.gong_names || {};
        const zhifuSectorKey = sectorPanelData.zhifu_sector_key || "";
        const colorSyncLayers = chartLayout.sync_layers || ["layer3", "layer4", "layer5"];
        const syncRotateLayers = colorSyncLayers.slice();
        const syncRotateSet = new Set(syncRotateLayers);
        const rotateLayerIds = chartLayout.rotate_layers || [];
        const gejuRotateLayerId = chartLayout.geju_rotate_layer || null;
        const guxuRotateLayerId = chartLayout.guxu_rotate_layer || null;
        const gejuOverlay = svg.querySelector(".taiyi-geju-overlay");
        const guxuOverlay = svg.querySelector(".taiyi-guxu-overlay");
        const highlightPalette = ["#D4AF37", "#4A9C6D", "#7E8FA3", "#C41E3A"];
        const paletteByElement = {
            wood: { fill: "#4A9C6D", stroke: "#78C18D", text: "#F5F0E1" },
            fire: { fill: "#A61E35", stroke: "#D9646E", text: "#F8E8E4" },
            earth: { fill: "#70543A", stroke: "#B59067", text: "#F5E8D5" },
            metal: { fill: "#C9A227", stroke: "#F0D57A", text: "#17120A" },
            water: { fill: "#355C8C", stroke: "#7EA3D8", text: "#EEF5FF" },
        };
        const branchToElement = {
            "子": "water", "亥": "water",
            "丑": "earth", "未": "earth", "辰": "earth", "戌": "earth",
            "寅": "wood", "卯": "wood", "巽": "wood",
            "巳": "fire", "午": "fire",
            "申": "metal", "酉": "metal", "乾": "metal",
            "坤": "earth", "艮": "earth",
        };
        const gateToBranch = {
            "休": "子", "生": "丑", "傷": "寅", "杜": "卯",
            "景": "巳", "死": "未", "驚": "申", "開": "酉",
        };
        const lifeBranchOrder = ["巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑", "寅", "卯", "辰"];
        const constellationToElement = {
            "角": "wood", "斗": "wood", "奎": "wood", "井": "wood",
            "尾": "fire", "室": "fire", "觜": "fire", "翼": "fire",
            "氐": "earth", "女": "earth", "胃": "earth", "柳": "earth",
            "房": "earth", "虛": "earth", "昴": "earth", "星": "earth",
            "亢": "metal", "牛": "metal", "婁": "metal", "鬼": "metal",
            "心": "metal", "危": "metal", "畢": "metal", "張": "metal",
            "箕": "water", "壁": "water", "參": "water", "軫": "water",
        };
        const state = {
            rotations: Object.fromEntries(rotateLayerIds.map((layerId) => [layerId, 0])),
            clickDirection: Object.fromEntries(rotateLayerIds.map((layerId) => [layerId, -1])),
            drag: null,
            colored: new Map(),
            styleMode: "traditional",
            wuxingColor: initialWuxingColor,
            gejuFollowDisk: true,
            noteText: "",
            activeSectorKey: "",
            handledTapPointerId: null,
        };
        let lastReportedHeight = 0;
        const sectorPanel = root.querySelector(".taiyi-sector-panel");
        const sectorPanelLayer = root.querySelector(".taiyi-sector-panel-layer");
        const sectorPanelTitle = root.querySelector(".taiyi-sector-panel-title");
        const sectorPanelLines = root.querySelector(".taiyi-sector-panel-lines");
        const sectorPanelGeju = root.querySelector(".taiyi-sector-panel-geju");
        let heightFramePending = false;
        const noteStorageKey = "taiyi-chart-note:" + (exportMeta.storageKey || "__CONTAINER_ID__");

        function setFrameHeight() {
            heightFramePending = false;
            const rectHeight = root.getBoundingClientRect ? root.getBoundingClientRect().height : 0;
            const offsetHeight = root.offsetHeight || 0;
            const scrollHeight = root.scrollHeight || 0;
            let height = Math.ceil(Math.max(rectHeight, offsetHeight, scrollHeight));
            // Guard: never send a non-positive height — it would collapse the iframe to 0.
            if (height <= 0) {
                return;
            }
            // Clamp to parent viewport so the iframe never exceeds the visible area
            // — no scrollbar, chart always fully visible without scrolling.
            try {
                const vh = window.parent.innerHeight || 0;
                if (vh > 0) {
                    // topnav(38) + tabs(~36) + tab-content padding(~8) + page padding(~16)
                    // + card padding(20) + toolbar(~36) + safety margin(~56) = ~210
                    // CSS square subtracts 280px; content = (vh-280)+56 = vh-224 < vh-210 ✓
                    const topOffset = 210;
                    const maxH = vh - topOffset;
                    if (height > maxH) {
                        height = maxH;
                    }
                    if (height < 200) {
                        height = 200;
                    }
                }
            } catch (e) { /* cross-origin: skip clamping */ }
            if (Math.abs(height - lastReportedHeight) < 2) {
                return;
            }
            lastReportedHeight = height;
            window.parent.postMessage(
                { isStreamlitMessage: true, type: "streamlit:setFrameHeight", height: height },
                "*"
            );
        }

        function queueFrameHeight() {
            if (heightFramePending) return;
            heightFramePending = true;
            requestAnimationFrame(setFrameHeight);
        }

        function cleanText(value) {
            return (value || "").replace(/\\s+/g, " ").trim();
        }

        function compactText(value) {
            return cleanText(value).replace(/\\s+/g, "");
        }

        function loadSavedNote() {
            try {
                state.noteText = cleanText(window.localStorage.getItem(noteStorageKey) || "");
            } catch (error) {
                state.noteText = "";
            }
        }

        function saveNote(value) {
            state.noteText = cleanText(value);
            try {
                if (state.noteText) {
                    window.localStorage.setItem(noteStorageKey, state.noteText);
                } else {
                    window.localStorage.removeItem(noteStorageKey);
                }
            } catch (error) {
                // Ignore storage write failures and keep the note in current state.
            }
            updateNoteButton();
        }

        function updateNoteButton() {
            const button = root.querySelector('[data-action="add-note"]');
            if (!button) return;
            button.textContent = ui.add_note;
            button.classList.toggle("is-active", Boolean(state.noteText));
            button.title = state.noteText
                ? `${ui.divination_note_label}: ${state.noteText}`
                : ui.divination_note_prompt;
        }

        function setStyledColor(node, propertyName, value) {
            if (!node || !value) return;
            node.style.setProperty(propertyName, value, "important");
            if (propertyName === "fill") {
                node.style.setProperty("--taiyi-user-fill", value);
            }
        }

        function getBranchFromLabel(label) {
            const compact = compactText(label);
            for (const char of compact) {
                if (branchToElement[char]) return char;
            }
            for (const char of compact) {
                if (gateToBranch[char]) return gateToBranch[char];
            }
            return "";
        }

        function getSemanticPalette(label, groupId, index, sectorCount) {
            const compact = compactText(label);
            const branch = getBranchFromLabel(compact);
            if (branch && branchToElement[branch]) {
                return paletteByElement[branchToElement[branch]];
            }
            if (!branch && groupId === "layer2" && sectorCount === 12) {
                return paletteByElement[branchToElement[lifeBranchOrder[index % lifeBranchOrder.length]]];
            }
            const firstChar = compact.charAt(0);
            if (constellationToElement[firstChar]) {
                return paletteByElement[constellationToElement[firstChar]];
            }
            return null;
        }

        function applySemanticPalette(sector, textNode, palette) {
            if (!sector || !palette) return;
            setStyledColor(sector, "fill", palette.fill);
            setStyledColor(sector, "stroke", palette.stroke);
            sector.dataset.semanticFill = palette.fill;
            sector.dataset.semanticStroke = palette.stroke;
            if (textNode) {
                setStyledColor(textNode, "fill", palette.text);
                textNode.dataset.semanticFill = palette.text;
            }
        }

        function ensureGlowFilter() {
            const ns = "http://www.w3.org/2000/svg";
            let defs = svg.querySelector("defs");
            if (!defs) {
                defs = document.createElementNS(ns, "defs");
                svg.insertBefore(defs, svg.firstChild);
            }
            if (svg.querySelector("#__GLOW_ID__")) return;

            const filter = document.createElementNS(ns, "filter");
            filter.setAttribute("id", "__GLOW_ID__");
            filter.setAttribute("x", "-50%");
            filter.setAttribute("y", "-50%");
            filter.setAttribute("width", "200%");
            filter.setAttribute("height", "200%");

            const blur = document.createElementNS(ns, "feGaussianBlur");
            blur.setAttribute("stdDeviation", "2.2");
            blur.setAttribute("result", "blur");

            const flood = document.createElementNS(ns, "feFlood");
            flood.setAttribute("flood-color", "#d4af37");
            flood.setAttribute("flood-opacity", "0.55");
            flood.setAttribute("result", "glowColor");

            const composite = document.createElementNS(ns, "feComposite");
            composite.setAttribute("in", "glowColor");
            composite.setAttribute("in2", "blur");
            composite.setAttribute("operator", "in");
            composite.setAttribute("result", "softGlow");

            const merge = document.createElementNS(ns, "feMerge");
            const node1 = document.createElementNS(ns, "feMergeNode");
            node1.setAttribute("in", "softGlow");
            const node2 = document.createElementNS(ns, "feMergeNode");
            node2.setAttribute("in", "SourceGraphic");
            merge.appendChild(node1);
            merge.appendChild(node2);

            filter.appendChild(blur);
            filter.appendChild(flood);
            filter.appendChild(composite);
            filter.appendChild(merge);
            defs.appendChild(filter);
        }

        function annotateSectorGroup(sectorGroup, groupId, index, sectorCount) {
            const pathNode = sectorGroup.querySelector("path, polygon, rect, circle, ellipse");
            const textNode = sectorGroup.querySelector("text");
            const paletteLabel = textNode
                ? cleanText(textNode.textContent)
                : cleanText(sectorGroup.getAttribute("data-full") || groupId + " " + (index + 1));
            const palette = getSemanticPalette(paletteLabel, groupId, index, sectorCount);
            if (palette && pathNode) {
                applySemanticPalette(pathNode, textNode, palette);
            }
            if (textNode && !textNode.dataset.baseTransform) {
                textNode.dataset.fullText = textNode.textContent || "";
                textNode.dataset.baseTransform = textNode.getAttribute("transform") || "";
            }
        }

        function annotateSvg() {
            const sectorGroups = Array.from(svg.querySelectorAll(".taiyi-sector"));
            if (sectorGroups.length) {
                sectorGroups.forEach((sectorGroup) => {
                    const parent = sectorGroup.parentElement;
                    const groupId = parent ? parent.id : "";
                    const siblings = parent ? Array.from(parent.querySelectorAll(":scope > .taiyi-sector")) : [sectorGroup];
                    const index = siblings.indexOf(sectorGroup);
                    annotateSectorGroup(sectorGroup, groupId, index, siblings.length);
                });
                return;
            }
            const groups = Array.from(svg.querySelectorAll("g"));
            groups.forEach((group) => {
                const directChildren = Array.from(group.children);
                const sectors = directChildren.filter((node) => /^(path|polygon|rect|circle|ellipse)$/i.test(node.tagName));
                const texts = directChildren.filter((node) => /^text$/i.test(node.tagName));
                const sectorCount = sectors.length;
                sectors.forEach((sector, index) => {
                    const pairedText = texts[index];
                    const label = pairedText ? cleanText(pairedText.textContent) : cleanText(group.id + " " + (index + 1));
                    const palette = getSemanticPalette(label, group.id, index, sectorCount);
                    if (palette) applySemanticPalette(sector, pairedText, palette);
                });
                texts.forEach((textNode) => {
                    if (!textNode.dataset.baseTransform) {
                        textNode.dataset.baseTransform = textNode.getAttribute("transform") || "";
                    }
                });
            });
        }

        function highlightImportantNodes() {
            const terms = highlightTerms.map((item) => compactText(String(item || ""))).filter(Boolean);
            svg.querySelectorAll("text").forEach((textNode) => {
                if (textNode.classList.contains("taiyi-wenchang-spot")
                    || textNode.querySelector(".taiyi-wenchang-spot")) {
                    return;
                }
                const content = compactText(textNode.textContent);
                if (!content) return;
                if (terms.some((token) => token && content.includes(token))) {
                    textNode.classList.add("taiyi-key-spot");
                    const sectorGroup = textNode.closest(".taiyi-sector");
                    const pathNode = sectorGroup
                        ? sectorGroup.querySelector("path, polygon, rect, circle, ellipse")
                        : textNode.previousElementSibling;
                    if (pathNode && /^(path|polygon|rect|circle|ellipse)$/i.test(pathNode.tagName)) {
                        pathNode.classList.add("taiyi-key-sector");
                    }
                }
            });
        }

        function getLayerCenter(layer) {
            const box = layer.getBBox();
            return { x: box.x + box.width / 2, y: box.y + box.height / 2 };
        }

        function clientToSvgPoint(clientX, clientY) {
            const point = svg.createSVGPoint();
            point.x = clientX;
            point.y = clientY;
            const matrix = svg.getScreenCTM();
            return matrix ? point.matrixTransform(matrix.inverse()) : { x: 0, y: 0 };
        }

        function angleFromPoint(point, center) {
            return Math.atan2(point.y - center.y, point.x - center.x) * 180 / Math.PI;
        }

        function applyFollowOverlayRotation(overlay, immediate, rotateLayerId, labelSelector) {
            if (!overlay || !rotateLayerId) return;
            const anchorLayer = svg.querySelector("#" + rotateLayerId);
            const center = anchorLayer ? getLayerCenter(anchorLayer) : getLayerCenter(svg);
            overlay.style.transition = immediate ? "none" : "";
            if (!state.gejuFollowDisk) {
                overlay.removeAttribute("transform");
                if (labelSelector) {
                    overlay.querySelectorAll(labelSelector).forEach((label) => {
                        label.removeAttribute("transform");
                    });
                }
                return;
            }
            const angle = state.rotations[rotateLayerId] || 0;
            overlay.setAttribute(
                "transform",
                "rotate(" + angle + " " + center.x + " " + center.y + ")"
            );
            if (labelSelector) {
                overlay.querySelectorAll(labelSelector).forEach((label) => {
                    const x = parseFloat(label.getAttribute("x") || center.x);
                    const y = parseFloat(label.getAttribute("y") || center.y);
                    label.setAttribute("transform", "rotate(" + (-angle) + " " + x + " " + y + ")");
                });
            }
        }

        function applyGuxuRotation(immediate) {
            if (!guxuOverlay) return;
            guxuOverlay.querySelectorAll(".taiyi-guxu-ring[data-rotate-layer]").forEach((group) => {
                applyFollowOverlayRotation(
                    group,
                    immediate,
                    group.getAttribute("data-rotate-layer"),
                    ""
                );
            });
            guxuOverlay.querySelectorAll(
                ".taiyi-guxu-labels[data-rotate-layer], .taiyi-guxu-arrow-group[data-rotate-layer]"
            ).forEach((group) => {
                applyFollowOverlayRotation(
                    group,
                    immediate,
                    group.getAttribute("data-rotate-layer"),
                    ".taiyi-guxu-label"
                );
            });
        }

        function applyGejuRotation(immediate) {
            applyFollowOverlayRotation(
                gejuOverlay, immediate, gejuRotateLayerId, ".taiyi-geju-label"
            );
            applyGuxuRotation(immediate);
        }

        function applyRotation(layerId, immediate) {
            const layer = svg.querySelector("#" + layerId);
            if (!layer) return;
            const angle = state.rotations[layerId] || 0;
            const center = getLayerCenter(layer);
            layer.style.transition = immediate ? "none" : "";
            layer.setAttribute("transform", "rotate(" + angle + " " + center.x + " " + center.y + ")");

            layer.querySelectorAll("text").forEach((textNode) => {
                const x = parseFloat(textNode.getAttribute("x") || center.x);
                const y = parseFloat(textNode.getAttribute("y") || center.y);
                const base = textNode.dataset.baseTransform || "";
                const rotation = "rotate(" + (-angle) + " " + x + " " + y + ")";
                textNode.setAttribute("transform", cleanText(base + " " + rotation));
            });
            applyGejuRotation(immediate);
        }

        function layersRotatedTogether(layerId) {
            if (syncRotateSet.has(layerId)) return syncRotateLayers;
            return [layerId];
        }

        function rotateLayer(layerId, deltaAngle, immediate) {
            layersRotatedTogether(layerId).forEach((lid) => {
                state.rotations[lid] = ((state.rotations[lid] || 0) + deltaAngle) % 360;
                applyRotation(lid, immediate);
            });
        }

        function setupRotations() {
            rotateLayerIds.forEach((layerId) => {
                const layer = svg.querySelector("#" + layerId);
                if (!layer) return;
                layer.classList.add("taiyi-rotatable");

                const finishDrag = (event) => {
                    if (!state.drag || state.drag.layerId !== layerId) return;
                    if (event && layer.hasPointerCapture && layer.hasPointerCapture(event.pointerId)) {
                        layer.releasePointerCapture(event.pointerId);
                    }
                    const moved = state.drag.moved;
                    const deferredTap = state.drag.deferCapture && !moved;
                    const tapSectorGroup = state.drag.tapSectorGroup || null;
                    const pointerId = event ? event.pointerId : state.drag.pointerId;
                    state.drag = null;
                    layer.classList.remove("is-dragging");
                    if (deferredTap) {
                        if (tapSectorGroup) {
                            state.handledTapPointerId = pointerId;
                            activateSector(tapSectorGroup, event);
                        }
                        return;
                    }
                    if (!moved && !syncRotateSet.has(layerId)) {
                        state.clickDirection[layerId] *= -1;
                        rotateLayer(layerId, 30 * state.clickDirection[layerId], false);
                    }
                };

                function beginLayerDrag(event, deferCapture, tapSectorGroup) {
                    const point = clientToSvgPoint(event.clientX, event.clientY);
                    const center = getLayerCenter(layer);
                    const angle = angleFromPoint(point, center);
                    state.drag = {
                        layerId: layerId,
                        previousAngle: angle,
                        startAngle: angle,
                        moved: false,
                        deferCapture: Boolean(deferCapture),
                        pointerId: event.pointerId,
                        originX: event.clientX,
                        originY: event.clientY,
                        tapSectorGroup: tapSectorGroup || null,
                    };
                    if (!deferCapture) {
                        layer.classList.add("is-dragging");
                        if (layer.setPointerCapture) layer.setPointerCapture(event.pointerId);
                    }
                }

                function ensureLayerDragCapture(event) {
                    if (!state.drag || state.drag.layerId !== layerId || !state.drag.deferCapture) return;
                    state.drag.deferCapture = false;
                    state.drag.tapSectorGroup = null;
                    layer.classList.add("is-dragging");
                    if (layer.setPointerCapture) layer.setPointerCapture(event.pointerId);
                }

                layer.addEventListener("pointerdown", (event) => {
                    const colorableNode = event.target.closest(".taiyi-colorable");
                    const onColorable = Boolean(colorableNode);
                    if (!onColorable) event.preventDefault();
                    beginLayerDrag(event, onColorable, colorableNode);
                });

                layer.addEventListener("pointermove", (event) => {
                    if (!state.drag || state.drag.layerId !== layerId) return;
                    if (state.drag.deferCapture) {
                        const dx = event.clientX - state.drag.originX;
                        const dy = event.clientY - state.drag.originY;
                        if ((dx * dx) + (dy * dy) < 144) return;
                        ensureLayerDragCapture(event);
                    }
                    event.preventDefault();
                    const point = clientToSvgPoint(event.clientX, event.clientY);
                    const center = getLayerCenter(layer);
                    const angle = angleFromPoint(point, center);
                    let delta = angle - state.drag.previousAngle;
                    if (delta > 180) delta -= 360;
                    if (delta < -180) delta += 360;
                    if (Math.abs(delta) > 0.05) {
                        rotateLayer(layerId, delta, true);
                        state.drag.previousAngle = angle;
                        if (Math.abs(angle - state.drag.startAngle) > 1.6) {
                            state.drag.moved = true;
                        }
                    }
                });

                layer.addEventListener("pointerup", finishDrag);
                layer.addEventListener("pointercancel", finishDrag);
                layer.addEventListener("lostpointercapture", finishDrag);
            });
        }

        function sectorNodes(sectorGroup) {
            return {
                sector: sectorGroup.querySelector("path, polygon, rect, circle, ellipse"),
                textNode: sectorGroup.querySelector("text"),
            };
        }

        function sectorColorKey(sectorGroup) {
            const layerId = sectorGroup.getAttribute("data-layer") || "";
            const sectorIdx = sectorGroup.getAttribute("data-sector") || "";
            return layerId + ":" + sectorIdx;
        }

        function getLayerSectorGroups(layerId) {
            const layer = svg.querySelector("#" + layerId);
            if (!layer) return [];
            const scoped = layer.querySelectorAll(":scope > .taiyi-sector");
            if (scoped.length) return Array.from(scoped);
            return Array.from(layer.children).filter(
                (node) => node.classList && node.classList.contains("taiyi-sector")
            );
        }

        function getSectorFraction(sectorGroup) {
            const index = parseInt(sectorGroup.getAttribute("data-sector"), 10);
            const layerId = sectorGroup.getAttribute("data-layer") || "";
            const sectorGroups = getLayerSectorGroups(layerId);
            if (!sectorGroups.length || Number.isNaN(index)) return null;
            return (index + 0.5) / sectorGroups.length;
        }

        function findSectorAtFraction(layerId, fraction) {
            const sectorGroups = getLayerSectorGroups(layerId);
            if (!sectorGroups.length || fraction === null) return null;
            let bestGroup = sectorGroups[0];
            let bestDistance = Infinity;
            sectorGroups.forEach((sectorGroup, index) => {
                const midFraction = (index + 0.5) / sectorGroups.length;
                const distance = Math.abs(midFraction - fraction);
                if (distance < bestDistance) {
                    bestDistance = distance;
                    bestGroup = sectorGroup;
                }
            });
            return bestGroup;
        }

        function syncColorKey(fraction) {
            return "sync:" + fraction.toFixed(6);
        }

        function branchSyncKey(branch) {
            return "sync:br:" + (branch || "");
        }

        function getSyncBranch(sectorGroup) {
            return sectorGroup.getAttribute("data-pos-branch")
                || sectorGroup.getAttribute("data-branch")
                || "";
        }

        function findSectorByBranch(layerId, branch) {
            if (!branch) return null;
            return getLayerSectorGroups(layerId).find(
                (sectorGroup) => getSyncBranch(sectorGroup) === branch
            ) || null;
        }

        function applySyncMarker(fraction, color) {
            colorSyncLayers.forEach((layerId) => {
                const sectorGroup = findSectorAtFraction(layerId, fraction);
                if (sectorGroup) paintSectorGroup(sectorGroup, color);
            });
        }

        function applySyncMarkerForBranch(branch, color) {
            if (!branch) return;
            colorSyncLayers.forEach((layerId) => {
                const sectorGroup = findSectorByBranch(layerId, branch);
                if (sectorGroup) paintSectorGroup(sectorGroup, color);
            });
        }

        function clearSyncMarker(fraction) {
            colorSyncLayers.forEach((layerId) => {
                const sectorGroup = findSectorAtFraction(layerId, fraction);
                if (sectorGroup) restoreSectorGroup(sectorGroup);
            });
        }

        function clearSyncMarkerForBranch(branch) {
            if (!branch) return;
            colorSyncLayers.forEach((layerId) => {
                const sectorGroup = findSectorByBranch(layerId, branch);
                if (sectorGroup) restoreSectorGroup(sectorGroup);
            });
        }

        function paintSectorGroup(sectorGroup, color) {
            const match = sectorNodes(sectorGroup);
            if (!match.sector) return;
            if (!match.sector.dataset.originalFill) {
                match.sector.dataset.originalFill = window.getComputedStyle(match.sector).fill || match.sector.dataset.semanticFill || "";
                match.sector.dataset.originalStroke = window.getComputedStyle(match.sector).stroke || match.sector.dataset.semanticStroke || "";
                match.sector.dataset.originalAttrFill = match.sector.getAttribute("fill") || "";
            }
            match.sector.setAttribute("fill", color);
            match.sector.setAttribute("data-user-fill", color);
            setStyledColor(match.sector, "fill", color);
            match.sector.classList.add("taiyi-user-mark");
            if (match.textNode) {
                if (!match.textNode.dataset.originalFill) {
                    match.textNode.dataset.originalFill = window.getComputedStyle(match.textNode).fill || match.textNode.dataset.semanticFill || "";
                }
                match.textNode.classList.add("taiyi-user-label");
            }
        }

        function restoreSectorGroup(sectorGroup) {
            const match = sectorNodes(sectorGroup);
            if (!match.sector) return;
            const originalFill = match.sector.dataset.originalFill || "";
            const originalStroke = match.sector.dataset.originalStroke || "";
            const originalAttrFill = match.sector.dataset.originalAttrFill || "";
            if (originalAttrFill) {
                match.sector.setAttribute("fill", originalAttrFill);
            } else {
                match.sector.removeAttribute("fill");
            }
            match.sector.removeAttribute("data-user-fill");
            if (originalFill) setStyledColor(match.sector, "fill", originalFill);
            else match.sector.style.removeProperty("fill");
            match.sector.style.removeProperty("--taiyi-user-fill");
            if (originalStroke) setStyledColor(match.sector, "stroke", originalStroke);
            match.sector.classList.remove("taiyi-user-mark");
            if (match.textNode) {
                const textFill = match.textNode.dataset.originalFill || match.textNode.dataset.semanticFill || "";
                if (textFill) setStyledColor(match.textNode, "fill", textFill);
                match.textNode.classList.remove("taiyi-user-label");
            }
        }

        function findSectorGroupByKey(key) {
            const parts = key.split(":");
            if (parts.length !== 2) return null;
            const layer = svg.querySelector("#" + parts[0]);
            if (!layer) return null;
            const scoped = layer.querySelector(':scope > .taiyi-sector[data-sector="' + parts[1] + '"]');
            if (scoped) return scoped;
            return getLayerSectorGroups(parts[0]).find(
                (sectorGroup) => sectorGroup.getAttribute("data-sector") === parts[1]
            ) || null;
        }

        function clearMarker(key) {
            if (key.indexOf("sync:br:") === 0) {
                clearSyncMarkerForBranch(key.slice(8));
                return;
            }
            if (key.indexOf("sync:") === 0) {
                clearSyncMarker(parseFloat(key.slice(5)));
                return;
            }
            const sectorGroup = findSectorGroupByKey(key);
            if (sectorGroup) restoreSectorGroup(sectorGroup);
        }

        function clearSectorSelection() {
            if (state.activeSectorKey) {
                const previous = findSectorGroupByKey(state.activeSectorKey);
                if (previous) previous.classList.remove("taiyi-sector-active");
            }
            state.activeSectorKey = "";
        }

        function gejuLookupKey(branch, layerId, sectorIdx) {
            if (layerId === "layer2" && sectorIdx >= 0 && layer2Gongs[sectorIdx]) {
                return String(layer2Gongs[sectorIdx]);
            }
            if (branch && gongByBranch[branch]) {
                return String(gongByBranch[branch]);
            }
            return "";
        }

        function renderGejuBlock(gongKey) {
            if (!sectorPanelGeju || !gongKey) {
                if (sectorPanelGeju) sectorPanelGeju.innerHTML = "";
                return;
            }
            const items = gejuByGong[gongKey] || [];
            if (!items.length) {
                sectorPanelGeju.innerHTML = "";
                return;
            }
            const title = document.createElement("div");
            title.className = "taiyi-sector-panel-geju-title";
            title.textContent = ui.sector_panel_geju || "釋格局";
            sectorPanelGeju.innerHTML = "";
            sectorPanelGeju.appendChild(title);
            items.forEach((item) => {
                const row = document.createElement("p");
                row.className = "taiyi-geju-panel-item";
                row.dataset.tone = item.tone || "info";
                const label = document.createElement("strong");
                label.textContent = item.key || item.short || "";
                row.appendChild(label);
                row.appendChild(document.createTextNode(item.text || ""));
                sectorPanelGeju.appendChild(row);
            });
        }

        function openSectorPanelByKey(key, branch) {
            if (!sectorPanel) return;
            const entry = sectorLookup[key] || null;
            const layerId = key.split(":")[0] || "";
            const layerLabel = layerLabels[layerId] || "";
            clearSectorSelection();
            state.activeSectorKey = key;
            const sectorGroup = findSectorGroupByKey(key);
            if (sectorGroup) sectorGroup.classList.add("taiyi-sector-active");

            if (sectorPanelLayer) sectorPanelLayer.textContent = layerLabel;
            if (sectorPanelTitle) {
                sectorPanelTitle.textContent = entry && entry.title
                    ? entry.title
                    : (sectorGroup ? cleanText(sectorGroup.getAttribute("data-full") || "") : key);
            }
            const listEl = sectorPanel.querySelector(".taiyi-sector-panel-lines");
            if (listEl) {
                listEl.innerHTML = "";
                const lines = entry && Array.isArray(entry.lines) ? entry.lines.filter(Boolean) : [];
                if (!lines.length) {
                    const item = document.createElement("li");
                    item.className = "taiyi-sector-panel-empty";
                    item.textContent = ui.sector_panel_empty || ui.tooltip_fallback || "";
                    listEl.appendChild(item);
                } else {
                    lines.forEach((line) => {
                        const item = document.createElement("li");
                        item.textContent = line;
                        listEl.appendChild(item);
                    });
                }
            }
            const posBranch = branch
                || (sectorGroup ? sectorGroup.getAttribute("data-pos-branch") : "")
                || (sectorGroup ? sectorGroup.getAttribute("data-branch") : "");
            const sectorIdx = Number.parseInt((key.split(":")[1] || "-1"), 10);
            renderGejuBlock(gejuLookupKey(posBranch, layerId, sectorIdx));
            if (listEl && posBranch && guxuByBranch[posBranch]) {
                const guxuItem = document.createElement("li");
                guxuItem.className = "taiyi-sector-panel-guxu";
                guxuItem.textContent = guxuByBranch[posBranch];
                listEl.appendChild(guxuItem);
            }
            sectorPanel.hidden = false;
            queueFrameHeight();
        }

        function openGejuPanel(gongKey) {
            if (!gongKey || !sectorPanel) return;
            clearSectorSelection();
            if (sectorPanelLayer) sectorPanelLayer.textContent = ui.sector_panel_geju || "釋格局";
            const gongLabel = gongNames[gongKey] || gongKey;
            if (sectorPanelTitle) sectorPanelTitle.textContent = gongLabel ? `${gongLabel}宮` : gongKey;
            const list = sectorPanel.querySelector(".taiyi-sector-panel-lines");
            if (list) list.innerHTML = "";
            renderGejuBlock(gongKey);
            sectorPanel.hidden = false;
            queueFrameHeight();
        }

        function closeSectorPanel() {
            if (!sectorPanel) return;
            sectorPanel.hidden = true;
            clearSectorSelection();
            queueFrameHeight();
        }

        function openSectorPanelFromGroup(sectorGroup) {
            const key = sectorGroup.getAttribute("data-tooltip-key")
                || sectorColorKey(sectorGroup);
            if (!key || key === ":") return;
            const branch = sectorGroup.getAttribute("data-pos-branch")
                || sectorGroup.getAttribute("data-branch")
                || "";
            openSectorPanelByKey(key, branch);
        }

        function isColorableSector(sectorGroup) {
            const layerId = sectorGroup.getAttribute("data-layer") || "";
            return colorSyncLayers.indexOf(layerId) !== -1;
        }

        function handleSectorColorClick(sectorGroup, event) {
            if (event) {
                event.preventDefault();
                event.stopPropagation();
            }
            if (!isColorableSector(sectorGroup)) return;
            const branch = getSyncBranch(sectorGroup);
            let key = branch ? branchSyncKey(branch) : "";
            if (!key) {
                const fraction = getSectorFraction(sectorGroup);
                if (fraction === null) return;
                key = syncColorKey(fraction);
            }
            if (state.colored.has(key)) {
                clearMarker(key);
                state.colored.delete(key);
                return;
            }
            if (state.colored.size >= highlightPalette.length) return;
            const color = highlightPalette[state.colored.size];
            state.colored.set(key, color);
            if (branch) {
                applySyncMarkerForBranch(branch, color);
            } else {
                applySyncMarker(getSectorFraction(sectorGroup), color);
            }
        }

        function activateSector(sectorGroup, event) {
            if (!sectorGroup) return;
            if (state.drag && state.drag.moved) return;
            if (isColorableSector(sectorGroup)) {
                handleSectorColorClick(sectorGroup, event);
            }
            if (sectorPanel) {
                openSectorPanelFromGroup(sectorGroup);
            }
        }

        function bindSectorShape(shapeNode, sectorGroup) {
            if (!shapeNode || shapeNode.dataset.sectorBound === "1") return;
            shapeNode.dataset.sectorBound = "1";
            const onActivate = (event) => {
                if (state.drag && state.drag.moved) return;
                if (event) {
                    event.stopPropagation();
                }
                activateSector(sectorGroup, event);
            };
            shapeNode.addEventListener("click", onActivate);
            shapeNode.addEventListener("pointerup", (event) => {
                if (event.pointerType === "mouse") return;
                if (state.handledTapPointerId === event.pointerId) {
                    state.handledTapPointerId = null;
                    return;
                }
                onActivate(event);
            });
        }

        function bindSectorInteractions() {
            Array.from(svg.querySelectorAll(".taiyi-sector")).forEach((sectorGroup) => {
                const shape = sectorGroup.querySelector("path, polygon, rect, circle, ellipse");
                if (isColorableSector(sectorGroup)) {
                    sectorGroup.classList.add("taiyi-colorable");
                    if (shape) shape.classList.add("taiyi-colorable-shape");
                }
                if (sectorPanel) {
                    sectorGroup.classList.add("taiyi-sector-panel-target");
                }
                if (shape) bindSectorShape(shape, sectorGroup);
            });
        }

        function setupSectorPanel() {
            bindSectorInteractions();
            Array.from(svg.querySelectorAll(".taiyi-geju-label")).forEach((labelNode) => {
                if (labelNode.dataset.gejuBound === "1") return;
                labelNode.dataset.gejuBound = "1";
                labelNode.addEventListener("click", (event) => {
                    event.preventDefault();
                    event.stopPropagation();
                    openGejuPanel(labelNode.getAttribute("data-gong") || "");
                });
            });
            const closeButton = root.querySelector('[data-action="close-panel"]');
            if (closeButton && !closeButton.dataset.bound) {
                closeButton.dataset.bound = "1";
                closeButton.addEventListener("click", closeSectorPanel);
            }
        }

        function resetView() {
            rotateLayerIds.forEach((layerId) => {
                state.rotations[layerId] = 0;
                applyRotation(layerId, false);
            });
            Array.from(state.colored.keys()).forEach((key) => clearMarker(key));
            state.colored.clear();
            closeSectorPanel();
            state.styleMode = "traditional";
            state.wuxingColor = initialWuxingColor;
            state.gejuFollowDisk = true;
            applyStyleMode();
            updateStyleButton();
            updateGejuFollowButton();
            applyGejuRotation(false);
        }

        function updateGejuFollowButton() {
            const button = root.querySelector('[data-action="toggle-geju-follow"]');
            if (!button || button.hidden) return;
            button.textContent = state.gejuFollowDisk ? ui.toggle_geju_fixed : ui.toggle_geju_follow;
            button.classList.toggle("is-active", state.gejuFollowDisk);
            button.setAttribute("aria-pressed", state.gejuFollowDisk ? "true" : "false");
        }

        function toggleGejuFollow() {
            state.gejuFollowDisk = !state.gejuFollowDisk;
            applyGejuRotation(false);
            updateGejuFollowButton();
        }

        function setupGejuFollowControl() {
            const button = root.querySelector('[data-action="toggle-geju-follow"]');
            const toolbar = root.querySelector(".taiyi-toolbar");
            if (!button || !gejuOverlay || !gejuRotateLayerId) return;
            if (rotateLayerIds.indexOf(gejuRotateLayerId) === -1) return;
            button.hidden = false;
            if (toolbar) toolbar.classList.add("has-geju-follow");
            button.addEventListener("click", toggleGejuFollow);
            updateGejuFollowButton();
            applyGejuRotation(false);
        }

        function applyStyleMode() {
            const mode = state.wuxingColor ? "wuxing" : state.styleMode;
            root.setAttribute("data-style-mode", mode);
        }

        function updateStyleButton() {
            const button = root.querySelector('[data-action="toggle-style"]');
            if (!button) return;
            button.textContent = state.styleMode === "traditional" ? ui.toggle_style_dense : ui.toggle_style_traditional;
        }

        function toggleStyleMode() {
            state.styleMode = state.styleMode === "traditional" ? "dense" : "traditional";
            applyStyleMode();
            updateStyleButton();
            setFrameHeight();
        }

        function addNote() {
            const nextValue = window.prompt(ui.divination_note_prompt, state.noteText || "");
            if (nextValue === null) return;
            saveNote(nextValue);
        }

        const exportCssByMode = __EXPORT_CSS_BY_MODE__;

        function currentExportMode() {
            return state.wuxingColor ? "wuxing" : state.styleMode;
        }

        function resolveExportCss() {
            const mode = currentExportMode();
            return (exportCssByMode && exportCssByMode[mode]) || exportCssByMode.traditional || __EXPORT_CSS__;
        }

        function bakeSvgVisualState(sourceRoot, targetRoot) {
            const paintProps = [
                "fill", "stroke", "stroke-width", "stroke-opacity", "fill-opacity",
                "font-size", "font-weight", "font-family", "letter-spacing", "opacity",
            ];
            const sourceNodes = [sourceRoot, ...sourceRoot.querySelectorAll("*")];
            const targetNodes = [targetRoot, ...targetRoot.querySelectorAll("*")];
            sourceNodes.forEach((src, index) => {
                const tgt = targetNodes[index];
                if (!tgt || !src) return;
                const computed = window.getComputedStyle(src);
                paintProps.forEach((prop) => {
                    const value = computed.getPropertyValue(prop);
                    if (!value || value === "none" || value === "normal" || value === "rgba(0, 0, 0, 0)") {
                        return;
                    }
                    tgt.style.setProperty(prop, value, "important");
                });
                if (src.hasAttribute("transform")) {
                    tgt.setAttribute("transform", src.getAttribute("transform"));
                }
            });
        }

        function prepareSvgCloneForExport() {
            closeSectorPanel();
            const clone = svg.cloneNode(true);
            clone.querySelectorAll(
                ".taiyi-sector-active, .taiyi-rotatable, .is-dragging, .taiyi-colorable, .taiyi-sector-panel-target"
            ).forEach((node) => {
                node.classList.remove(
                    "taiyi-sector-active",
                    "taiyi-rotatable",
                    "is-dragging",
                    "taiyi-colorable",
                    "taiyi-sector-panel-target"
                );
            });
            bakeSvgVisualState(svg, clone);
            const styleNode = document.createElementNS("http://www.w3.org/2000/svg", "style");
            styleNode.textContent = resolveExportCss();
            clone.insertBefore(styleNode, clone.firstChild);
            return clone;
        }

        function downloadPng() {
            const scale = 2;
            const viewBox = (svg.getAttribute("viewBox") || "0 0 __NUM__ __NUM__").split(/[ ,]+/);
            const width = parseFloat(viewBox[2]) || __NUM__;
            const height = parseFloat(viewBox[3]) || __NUM__;

            const clone = prepareSvgCloneForExport();

            const serialized = new XMLSerializer().serializeToString(clone);
            const blob = new Blob([serialized], { type: "image/svg+xml;charset=utf-8" });
            const url = URL.createObjectURL(blob);
            const image = new Image();
            const loadOptionalImage = (src) => new Promise((resolve) => {
                if (!src) {
                    resolve(null);
                    return;
                }
                const optionalImage = new Image();
                optionalImage.onload = () => resolve(optionalImage);
                optionalImage.onerror = () => resolve(null);
                optionalImage.src = src;
            });

            const wrapText = (ctx, text, maxWidth) => {
                const chars = Array.from(text || "");
                const lines = [];
                let current = "";
                chars.forEach((char) => {
                    const probe = current + char;
                    if (ctx.measureText(probe).width > maxWidth && current) {
                        lines.push(current);
                        current = char;
                    } else {
                        current = probe;
                    }
                });
                if (current) lines.push(current);
                return lines;
            };

            image.onload = async () => {
                const summaryLines = Array.isArray(exportMeta.lines) ? exportMeta.lines.filter(Boolean) : [];
                const noteLine = state.noteText ? `${ui.divination_note_label}: ${state.noteText}` : "";
                const qrImage = await loadOptionalImage(exportMeta.qrcode || "");
                const canvasSize = 1080 * scale;
                const canvas = document.createElement("canvas");
                canvas.width = canvasSize;
                canvas.height = canvasSize;
                const context = canvas.getContext("2d");

                context.fillStyle = "#0d1b2a";
                context.fillRect(0, 0, canvas.width, canvas.height);
                const gradient = context.createLinearGradient(0, 0, canvas.width, canvas.height);
                gradient.addColorStop(0, "rgba(212, 175, 55, 0.18)");
                gradient.addColorStop(0.35, "rgba(13, 27, 42, 0.02)");
                gradient.addColorStop(1, "rgba(196, 30, 58, 0.14)");
                context.fillStyle = gradient;
                context.fillRect(0, 0, canvas.width, canvas.height);

                const glow = context.createRadialGradient(
                    canvas.width * 0.5, canvas.height * 0.54, 40,
                    canvas.width * 0.5, canvas.height * 0.54, canvas.width * 0.46
                );
                glow.addColorStop(0, "rgba(212, 175, 55, 0.12)");
                glow.addColorStop(0.55, "rgba(212, 175, 55, 0.03)");
                glow.addColorStop(1, "rgba(212, 175, 55, 0)");
                context.fillStyle = glow;
                context.fillRect(0, 0, canvas.width, canvas.height);

                context.strokeStyle = "rgba(212, 175, 55, 0.62)";
                context.lineWidth = 2 * scale;
                context.strokeRect(24 * scale, 24 * scale, canvas.width - 48 * scale, canvas.height - 48 * scale);
                context.strokeStyle = "rgba(212, 175, 55, 0.22)";
                context.strokeRect(40 * scale, 40 * scale, canvas.width - 80 * scale, canvas.height - 80 * scale);

                const sidePadding = 64 * scale;
                const summaryWidth = canvas.width - sidePadding * 2;
                let cursorY = 88 * scale;

                context.fillStyle = "#d4af37";
                context.font = `700 ${32 * scale}px "Microsoft YaHei", "Microsoft JhengHei", "PingFang SC", sans-serif`;
                context.fillText(exportMeta.title || ui.chart_kind, sidePadding, cursorY);
                cursorY += 18 * scale;

                context.fillStyle = "#f5f0e1";
                context.font = `600 ${13.2 * scale}px "Songti SC", "STSong", "SimSun", "Noto Serif SC", serif`;
                summaryLines.slice(0, 3).forEach((line) => {
                    wrapText(context, line, summaryWidth).slice(0, 2).forEach((wrappedLine) => {
                        context.fillText(wrappedLine, sidePadding, cursorY);
                        cursorY += 16 * scale;
                    });
                });
                if (noteLine) {
                    context.fillStyle = "#e8dfc8";
                    context.font = `600 ${13.2 * scale}px "Songti SC", "STSong", "SimSun", "Noto Serif SC", serif`;
                    wrapText(context, noteLine, summaryWidth).slice(0, 2).forEach((wrappedLine) => {
                        context.fillText(wrappedLine, sidePadding, cursorY);
                        cursorY += 16 * scale;
                    });
                }

                const chartTop = cursorY + 2 * scale;
                const footerHeight = qrImage ? 82 * scale : 36 * scale;
                const chartSize = Math.min(canvas.width * 0.92, canvas.height * 0.92, canvas.height - chartTop - footerHeight);
                const chartX = (canvas.width - chartSize) / 2;
                const chartY = chartTop;

                context.fillStyle = "rgba(255, 255, 255, 0.02)";
                context.beginPath();
                context.arc(canvas.width / 2, chartY + chartSize / 2, chartSize * 0.52, 0, Math.PI * 2);
                context.fill();
                context.drawImage(image, chartX, chartY, chartSize, chartSize);

                const footerY = chartY + chartSize - 18 * scale;
                context.strokeStyle = "rgba(212, 175, 55, 0.36)";
                context.lineWidth = 1.5 * scale;
                context.beginPath();
                context.moveTo(sidePadding, footerY);
                context.lineTo(canvas.width - sidePadding, footerY);
                context.stroke();

                if (qrImage) {
                    const qrSize = 102 * scale;
                    const qrX = canvas.width - sidePadding - qrSize;
                    const qrY = footerY - 20 * scale;
                    context.fillStyle = "#f5f0e1";
                    context.fillRect(qrX - 8 * scale, qrY - 8 * scale, qrSize + 16 * scale, qrSize + 16 * scale);
                    context.drawImage(qrImage, qrX, qrY, qrSize, qrSize);

                    context.fillStyle = "#d4af37";
                    context.font = `700 ${13.5 * scale}px "Songti SC", "STSong", "SimSun", "Noto Serif SC", serif`;
                    context.fillText(exportMeta.followLabel || "", sidePadding, footerY + 44 * scale);
                }

                URL.revokeObjectURL(url);
                canvas.toBlob((pngBlob) => {
                    if (!pngBlob) return;
                    const link = document.createElement("a");
                    link.href = URL.createObjectURL(pngBlob);
                    link.download = ui.chart_kind.toLowerCase().replace(/\\s+/g, "-") + "-card.png";
                    link.click();
                    setTimeout(() => URL.revokeObjectURL(link.href), 1200);
                }, "image/png");
            };

            image.onerror = () => URL.revokeObjectURL(url);
            image.src = url;
        }

        loadSavedNote();
        ensureGlowFilter();
        annotateSvg();
        highlightImportantNodes();
        setupSectorPanel();
        if (interactive) setupRotations();

        [
            ["reset", resetView],
            ["toggle-style", toggleStyleMode],
            ["add-note", addNote],
            ["download-png", downloadPng],
        ].forEach(([action, handler]) => {
            const button = root.querySelector('[data-action="' + action + '"]');
            if (button) button.addEventListener("click", handler);
        });
        setupGejuFollowControl();
        applyStyleMode();
        updateStyleButton();
        updateNoteButton();

        // ── 預設開啟直符所在宮位的 sector panel ──
        if (zhifuSectorKey && sectorLookup[zhifuSectorKey]) {
            setTimeout(() => {
                openSectorPanelByKey(zhifuSectorKey);
            }, 300);
        }

        if (window.ResizeObserver) {
            const observer = new ResizeObserver(() => queueFrameHeight());
            observer.observe(root);
            observer.observe(svg);
        }
        window.addEventListener("load", queueFrameHeight, { once: true });
        setTimeout(queueFrameHeight, 80);
        setTimeout(queueFrameHeight, 260);
        } catch (error) {
            console.error("Taiyi chart init failed:", error);
            const root = document.getElementById("__CONTAINER_ID__");
            if (root) {
                const alert = document.createElement("p");
                alert.className = "taiyi-init-error";
                alert.textContent = "排盤互動載入失敗，請重新整理頁面。";
                alert.style.cssText = "color:#ffb4b4;padding:8px 12px;margin:8px 0;";
                root.prepend(alert);
            }
        }
    })();
    </script>
    """

    html_content = (
        template
        .replace("__CONTAINER_ID__", container_id)
        .replace("__INTERACTIVE__", "true" if interactive else "false")
        .replace("__INITIAL_STYLE_MODE__", html_escape(initial_style_mode))
        .replace("__WUXING_COLOR__", json.dumps(bool(chart_meta.get("wuxing_color"))))
        .replace("__STYLE_BUTTON__", html_escape(ui["toggle_style_dense"]))
        .replace("__TOGGLE_GEJU_FOLLOW__", html_escape(ui["toggle_geju_fixed"]))
        .replace("__RESET__", html_escape(ui["reset"]))
        .replace("__ADD_NOTE__", html_escape(ui["add_note"]))
        .replace("__DOWNLOAD_PNG__", html_escape(ui["download_png"]))
        .replace("__SVG_MARKUP__", svg_markup)
        .replace("__UI_JSON__", json.dumps(chart_meta.get("ui", ui), ensure_ascii=False))
        .replace("__HIGHLIGHTS_JSON__", json.dumps(chart_meta["highlights"], ensure_ascii=False))
        .replace("__CHART_LAYOUT_JSON__", json.dumps(chart_meta.get("chart_layout", {}), ensure_ascii=False))
        .replace(
            "__SECTOR_PANEL_JSON__",
            json.dumps(chart_meta.get("sector_panel") or {}, ensure_ascii=False),
        )
        .replace("__PANEL_CLOSE__", html_escape(chart_meta.get("ui", ui).get("sector_panel_close", "")))

        .replace(
            "__EXPORT_META_JSON__",
            json.dumps(
                {
                    "title": chart_meta.get("export_title", ui["chart_kind"]),
                    "lines": chart_meta.get("export_lines", []),
                    "followLabel": chart_meta.get("export_follow_label", ""),
                    "qrcode": chart_meta.get("export_qrcode", ""),
                    "storageKey": chart_meta.get("export_storage_key", ""),
                },
                ensure_ascii=False,
            ),
        )
        .replace("__GLOW_ID__", glow_id)
        .replace("__NUM__", str(num))
        .replace("__EXPORT_CSS__", json.dumps(export_css, ensure_ascii=False))
        .replace("__EXPORT_CSS_BY_MODE__", json.dumps(export_css_bundle, ensure_ascii=False))
    )
    # st.iframe with inline HTML (replaces deprecated st.components.v1.html).
    # Passing an HTML string as the first positional arg (src) makes Streamlit
    # auto-detect it as srcdoc content.
    # height="content" lets Streamlit auto-size the iframe to exact content
    # height — no fixed height, no gap between chart and hex/yun timeline.
    # The template JS postMessage setFrameHeight is kept as a fallback.
    st.iframe(html_content, height="content", width="stretch")


def render_svg(svg, num, chart_meta):
    """Render the enhanced Taiyi chart with drag rotation on layers 4 and 6."""
    _render_taiyi_chart(svg, num, chart_meta, interactive=True)


def render_svg1(svg, num, chart_meta):
    """Render the enhanced Taiyi chart with focus-marking interactions."""
    _render_taiyi_chart(svg, num, chart_meta, interactive=False)


def render_chart_explanation_seam():
    """Tighten mobile gaps: chart → 完整參數 → 解釋."""
    st.markdown(
        '<div class="taiyi-chart-seam-anchor" aria-hidden="true"></div>',
        unsafe_allow_html=True,
    )


def timeline(data, height=800):
    """渲染時間線組件"""
    if isinstance(data, str):
        data = json.loads(data)
    json_text = json.dumps(data)
    source_param = 'timeline_json'
    source_block = f'var {source_param} = {json_text};'
    cdn_path = 'https://cdn.knightlab.com/libs/timeline3/latest'
    css_block = f'<link title="timeline-styles" rel="stylesheet" href="{cdn_path}/css/timeline.css">'
    js_block = f'<script src="{cdn_path}/js/timeline.js"></script>'
    htmlcode = f'''
        {css_block}
        {js_block}
        <div id='timeline-embed' style="width: 95%; height: {height}px; margin: 1px;"></div>
        <script type="text/javascript">
            var additionalOptions = {{ start_at_end: false, is_embed: true, default_bg_color: {{r:14, g:17, b:23}} }};
            {source_block}
            timeline = new TL.Timeline('timeline-embed', {source_param}, additionalOptions);
        </script>
    '''
    st.iframe(htmlcode, height=height, width="stretch")

@contextmanager
def st_capture(output_func):
    """捕獲 stdout 並將其傳遞給指定的輸出函數"""
    with StringIO() as stdout, redirect_stdout(stdout):
        old_write = stdout.write
        def new_write(string):
            ret = old_write(string)
            output_func(stdout.getvalue())
            return ret
        stdout.write = new_write
        yield

# Initialize language in session state
if "lang" not in st.session_state:
    st.session_state.lang = "zh"

# Streamlit 頁面配置
_page_icon = os.path.join(_REPO_ROOT, "assets", "icon.png")
if not os.path.isfile(_page_icon):
    _page_icon = "☯"
st.set_page_config(
    layout="wide",
    page_title=t("page_title"),
    page_icon=_page_icon,
)
# Inject Grok theme CSS on every run.
# st.markdown(unsafe_allow_html=True) injects raw <style> without DOMPurify
# sanitization. Re-injecting every run guarantees the <style> block survives
# reruns (date change, sidebar toggle, etc.).
st.markdown(get_custom_css(), unsafe_allow_html=True)
# Sidebar cursor fix is now pure CSS — no JS injection needed.
# Previous st.iframe(..., unsafe_allow_javascript=True) caused React error #185
# because each rerun created a new iframe with a MutationObserver that
# triggered cascading DOM mutations.
# 定義基礎 URL
BASE_URL_KINTAIYI = 'https://raw.githubusercontent.com/kentang2017/kintaiyi/master/'
BASE_URL_KINLIUREN = 'https://raw.githubusercontent.com/kentang2017/kinliuren/master/'

# Grok-style top nav (disabled — brand moved to sidebar top)
_nav_html = get_top_nav_html(st.session_state.get("lang", "zh"))
if _nav_html:
    st.markdown(_nav_html, unsafe_allow_html=True)

_MODELS = {
    "CEREBRAS_MODEL_OPTIONS": CEREBRAS_MODEL_OPTIONS,
    "CEREBRAS_MODEL_DESCRIPTIONS": CEREBRAS_MODEL_DESCRIPTIONS,
    "OPENAI_MODEL_OPTIONS": OPENAI_MODEL_OPTIONS,
    "OPENAI_MODEL_DESCRIPTIONS": OPENAI_MODEL_DESCRIPTIONS,
    "XAI_MODEL_OPTIONS": XAI_MODEL_OPTIONS,
    "XAI_MODEL_DESCRIPTIONS": XAI_MODEL_DESCRIPTIONS,
    "DEEPSEEK_MODEL_OPTIONS": DEEPSEEK_MODEL_OPTIONS,
    "DEEPSEEK_MODEL_DESCRIPTIONS": DEEPSEEK_MODEL_DESCRIPTIONS,
    "QWEN_MODEL_OPTIONS": QWEN_MODEL_OPTIONS,
    "QWEN_MODEL_DESCRIPTIONS": QWEN_MODEL_DESCRIPTIONS,
}
with st.sidebar:
    st.markdown(get_sidebar_brand_html(st.session_state.get("lang", "zh")), unsafe_allow_html=True)
    _sb = render_grok_sidebar(
        t=t, to=to,
        load_system_prompts=load_system_prompts,
        save_system_prompts=save_system_prompts,
        models=_MODELS,
    )
my, mm, md, mh, mmin = _sb.my, _sb.mm, _sb.md, _sb.mh, _sb.mmin
style, tn, tc, sex_o = _sb.style, _sb.tn, _sb.tc, _sb.sex_o
rotation = _sb.rotation
show_geju_markers = _sb.show_geju_markers
show_wuxing_color = _sb.show_wuxing_color
show_guxu_overlay = _sb.show_guxu_overlay
instant = _sb.instant
selected_model = _sb.selected_model
openai_api_key_input = _sb.openai_api_key_input

@st.cache_data
def gen_results(my, mm, md, mh, mmin, style, tn, sex_o, tc):
    """生成太乙計算結果，返回數據字典"""
    ty = kintaiyi.Taiyi(my, mm, md, mh, mmin)
    if not _is_life_chart_style(style):
        ttext = ty.pan(style, tn)
        kook = ty.kook(style, tn)
        sj_su_predict = f"始擊落{ty.sf_num(style, tn)}宿，{su_dist.get(ty.sf_num(style, tn))}"
        tg_sj_su_predict = config.multi_key_dict_get(tengan_shiji, config.gangzhi(my, mm, md, mh, mmin)[0][0]).get(config.Ganzhiwuxing(ty.sf(style, tn)))
        three_door = ty.threedoors(style, tn)
        five_generals = ty.fivegenerals(style, tn)
        home_vs_away1 = ty.wc_n_sj(style, tn)
        genchart2 = ty.gen_gong(style, tn, tc)
        genchart1 = None
    else:
        plate_ji = LIFE_PLATE_JI[style]
        tn = 0
        ttext = ty.pan(plate_ji, 0)
        kook = ty.kook(plate_ji, 0)
        sj_su_predict = f"始擊落{ty.sf_num(plate_ji, 0)}宿，{su_dist.get(ty.sf_num(plate_ji, 0))}"
        tg_sj_su_predict = config.multi_key_dict_get(
            tengan_shiji, config.gangzhi(my, mm, md, mh, mmin)[0][0],
        ).get(config.Ganzhiwuxing(ty.sf(plate_ji, 0)))
        three_door = ty.threedoors(plate_ji, 0)
        five_generals = ty.fivegenerals(plate_ji, 0)
        home_vs_away1 = ty.wc_n_sj(plate_ji, 0)
        genchart2 = ty.gen_gong(plate_ji, tn, tc)
        genchart1 = ty.gen_life_gong(sex_o, plate_ji)
    kook_num = kook.get("數")
    yingyang = kook.get("文")[0]
    wuyuan = ty.get_five_yuan_kook(style, tn) if not _is_life_chart_style(style) else ""
    homecal, awaycal, setcal = config.find_cal(yingyang, kook_num)
    zhao = {"男": "乾造", "女": "坤造"}.get(sex_o)
    plate_ji = LIFE_PLATE_JI.get(style) if _is_life_chart_style(style) else None
    if plate_ji is not None:
        life1 = ty.gongs_discription(sex_o, plate_ji)
        life2 = ty.twostar_disc(sex_o, plate_ji)
        lifedisc = ty.convert_gongs_text(life1, life2)
        lifedisc2 = ty.stars_descriptions_text(plate_ji, 0, life_ring=True)
        lifedisc3 = ty.sixteen_gong_grades(plate_ji, 0, life_ring=True)
        lifedisc4 = ty.shiti_jinfu_text(sex_o, plate_ji)
        life_pan = ty.taiyi_life(sex_o, plate_ji)
        life_vol20 = life_pan.get("卷二十", {})
    else:
        life1 = life2 = lifedisc = lifedisc2 = lifedisc3 = lifedisc4 = None
        life_pan = life_vol20 = None
    yc = ty.year_chin()
    year_predict = f"太歲{yc}值宿，{su_dist.get(yc)}"
    home_vs_away3 = ttext.get("推太乙風雲飛鳥助戰法")
    ts = taiyi_yingyang.get(kook.get('文')[0:2]).get(kook.get('數'))
    gz = f"{ttext.get('干支')[0]}年 {ttext.get('干支')[1]}月 {ttext.get('干支')[2]}日 {ttext.get('干支')[3]}時 {ttext.get('干支')[4]}分"
    lunard = f"{cn2an.transform(str(config.lunar_date_d(my, mm, md).get('年')) + '年', 'an2cn')}{an2cn(config.lunar_date_d(my, mm, md).get('月'))}月{an2cn(config.lunar_date_d(my, mm, md).get('日'))}日"
    ch = chistory.get(my, "")
    tys = "".join([ts[i:i+25] + "\n" for i in range(0, len(ts), 25)])
    yjxx = ty.yangjiu_xingxian(sex_o)
    blxx = ty.bailiu_xingxian(sex_o)
    ygua = ty.year_gua()[1]
    mgua = ty.month_gua()[1]
    dgua = ty.day_gua()[1]
    hgua = ty.hour_gua()[1]
    mingua = ty.minute_gua()[1]
    
    return {
        "ttext": ttext,
        "kook": kook,
        "sj_su_predict": sj_su_predict,
        "tg_sj_su_predict": tg_sj_su_predict,
        "three_door": three_door,
        "five_generals": five_generals,
        "home_vs_away1": home_vs_away1,
        "genchart1": genchart1,
        "genchart2": genchart2,
        "kook_num": kook_num,
        "yingyang": yingyang,
        "wuyuan": wuyuan,
        "homecal": homecal,
        "awaycal": awaycal,
        "setcal": setcal,
        "zhao": zhao,
        "life1": life1,
        "life2": life2,
        "lifedisc": lifedisc,
        "lifedisc2": lifedisc2,
        "lifedisc3": lifedisc3,
        "lifedisc4": lifedisc4,
        "life_vol20": life_vol20,
        "life_pan": life_pan,
        "plate_ji": plate_ji,
        "year_predict": year_predict,
        "home_vs_away3": home_vs_away3,
        "ts": ts,
        "gz": gz,
        "lunard": lunard,
        "ch": ch,
        "tys": tys,
        "yjxx": yjxx,
        "blxx": blxx,
        "ygua": ygua,
        "mgua": mgua,
        "dgua": dgua,
        "hgua": hgua,
        "mingua": mingua,
        "style": style,
        "tn": tn,
        "sex_o": sex_o,
        "ty": ty
    }


def _chart_input_key(my, mm, md, mh, mmin, style, tn, sex_o, tc) -> tuple:
    return (my, mm, md, mh, mmin, style, tn, sex_o, tc)


def _resolve_chart_results(
    *,
    instant: bool,
    my: int,
    mm: int,
    md: int,
    mh: int,
    mmin: int,
    style: int,
    tn: int,
    sex_o: str,
    tc: int,
) -> dict | None:
    """Reuse session cache; only recompute Taiyi when user runs chart or first load."""
    key = _chart_input_key(my, mm, md, mh, mmin, style, tn, sex_o, tc)
    cached = st.session_state.get("chart_results")
    cached_key = st.session_state.get("chart_input_key")

    if instant:
        results = gen_results(my, mm, md, mh, mmin, style, tn, sex_o, tc)
        st.session_state.chart_results = results
        st.session_state.chart_input_key = key
        st.session_state.pop("chart_meta_key", None)
        st.session_state.chart_params_stale = False
        return results

    if cached is not None and cached_key == key:
        st.session_state.chart_params_stale = False
        return cached

    if cached is not None and cached_key != key:
        st.session_state.chart_params_stale = True
        return cached

    results = gen_results(my, mm, md, mh, mmin, style, tn, sex_o, tc)
    st.session_state.chart_results = results
    st.session_state.chart_input_key = key
    st.session_state.pop("chart_meta_key", None)
    st.session_state.chart_params_stale = False
    return results


def _resolve_chart_meta(
    results: dict,
    *,
    is_life_chart: bool,
    show_geju_markers: bool,
    show_guxu_overlay: bool,
    show_wuxing_color: bool,
) -> dict:
    """Cache expensive overlay/sector-panel assembly across chat-only reruns."""
    meta_key = (
        st.session_state.get("chart_input_key"),
        show_geju_markers,
        show_guxu_overlay,
        show_wuxing_color,
        st.session_state.get("lang", "zh"),
        results.get("style"),
        is_life_chart,
    )
    if (
        st.session_state.get("chart_meta_key") == meta_key
        and st.session_state.get("chart_meta") is not None
    ):
        return st.session_state.chart_meta

    meta = _build_chart_meta(
        results,
        is_life_chart=is_life_chart,
        show_geju_markers=show_geju_markers,
        show_guxu_overlay=show_guxu_overlay,
        wuxing_color=show_wuxing_color,
    )
    st.session_state.chart_meta = meta
    st.session_state.chart_meta_key = meta_key
    return meta


# 創建標籤頁
tabs = st.tabs([t('tab_chart'), t('tab_instructions'), t('tab_history'), t('tab_disaster'), t('tab_books'), t('tab_updates'), t('tab_guide'), t('tab_links')])

# 太乙排盤
with tabs[0]:
    try:
        results = _resolve_chart_results(
            instant=instant,
            my=my, mm=mm, md=md, mh=mh, mmin=mmin,
            style=style, tn=tn, sex_o=sex_o, tc=tc,
        )
        if st.session_state.get("chart_params_stale"):
            pass  # suppress stale hint text on mobile

        if results:
                if _is_life_chart_style(results["style"]):
                    try:
                        start_pt = results["genchart1"][results["genchart1"].index('''viewBox="''')+22:].split(" ")[1]
                        chart_meta = _resolve_chart_meta(
                            results,
                            is_life_chart=True,
                            show_geju_markers=show_geju_markers,
                            show_guxu_overlay=show_guxu_overlay,
                            show_wuxing_color=show_wuxing_color,
                        )
                        chart_life_main, chart_life_side = st.columns([1.65, 0.85], gap="large")
                        with chart_life_main:
                            render_chart_stage_open(
                                print_meta=build_chart_print_meta(
                                    results,
                                    t=t,
                                    is_life_chart=True,
                                    life_method_label=_life_method_label(results["style"]),
                                ),
                            )
                            render_chart_explanation_seam()
                            if rotation == "轉動":
                                render_svg(results["genchart1"], int(start_pt), chart_meta)
                            else:
                                render_svg1(results["genchart1"], int(start_pt), chart_meta)
                            render_chart_mobile_params(chart_meta, results, t=t)
                        with chart_life_side:
                            render_chart_side_panel(
                                chart_meta, results, t=t, is_life_chart=True,
                            )
                    except (ValueError, IndexError) as e:
                        st.error(f"Failed to parse SVG viewBox: {str(e)}")
                    st.markdown(
                        '<span class="chart-explanation-anchor" aria-hidden="true"></span>',
                        unsafe_allow_html=True,
                    )
                    with st.expander(t("explanation")):
                        st.title(t("taiyi_life_title"))
                        st.markdown(t("twelve_palaces"))
                        st.markdown(results["lifedisc"])
                        st.markdown("   ")
                        st.markdown(t("sixteen_gods"))
                        st.markdown(results["lifedisc2"])
                        st.markdown("   ")
                        st.markdown(t("sixteen_grades"))
                        st.markdown(results["lifedisc3"])
                        st.markdown("   ")
                        if results.get("lifedisc4"):
                            st.markdown(t("shiti_jinfu"))
                            st.markdown(results["lifedisc4"])
                            st.markdown("   ")
                        from kintaiyi import mingfa as _mingfa_mod

                        _ty_life = results["ty"]
                        try:
                            _default_age = config.calculateAge(
                                datetime.date(_ty_life.year, _ty_life.month, _ty_life.day)
                            )
                        except (ValueError, OverflowError):
                            _default_age = 0
                        _life_age = st.slider(
                            t("life_query_age"),
                            0,
                            90,
                            value=int(st.session_state.get("life_query_age", _default_age)),
                            key="life_query_age",
                        )
                        _query_year = st.slider(
                            t("life_query_year"),
                            1900,
                            2100,
                            value=int(st.session_state.get("life_query_year", datetime.date.today().year)),
                            key="life_query_year",
                        )
                        _v20 = _mingfa_mod.zonghe(
                            _ty_life,
                            results["sex_o"],
                            age=_life_age,
                            query_year=_query_year,
                            plate_ji=LIFE_PLATE_JI[results["style"]],
                        )
                        if _v20:
                            _fly = _v20.get("飛祿飛馬", {})
                            _cur = _fly.get("當前") or {}
                            if _cur:
                                st.markdown(
                                    f"{t('fly_lu_ma')}"
                                    f"{_cur.get('期間', '')} "
                                    f"祿{_cur.get('飛祿宮', '—')}／馬{_cur.get('飛馬宮', '—')}"
                                )
                            _she = _v20.get("十干合", {})
                            _san = _v20.get("命宮三合", {})
                            st.markdown(
                                f"{t('sanhe_he')}"
                                f"{_san.get('三合', '—')}（{_san.get('五行', '')}）｜"
                                f"{_she.get('年干', '')}{_she.get('合干', '')}合{_she.get('合化', '')}"
                            )
                            _qi = _v20.get("奇耦上和", {})
                            _sc = _v20.get("三才無筭", {})
                            st.markdown(
                                f"{t('qiou_sancai')}"
                                f"{_qi.get('和數類型', '')}·{_qi.get('陰陽相配', '')}"
                                f"｜{_sc.get('要訣', '')}"
                            )
                            _mg = _v20.get("百六行月卦", {})
                            _dg = _v20.get("百六行日卦", {})
                            st.markdown(
                                f"{t('bailiu_gua')}"
                                f"月{_mg.get('卦', '')}{_mg.get('爻名', '')}｜"
                                f"日{_dg.get('卦', '')}{_dg.get('爻名', '')}"
                            )
                            _rg = _v20.get("百六入卦限", {})
                            _cs = _rg.get("當前卦限", {})
                            _ln = _rg.get("流年卦限", {})
                            if _ln:
                                st.markdown(
                                    f"{t('rugua_xian')}"
                                    f"{_cs.get('階段', '')}{_cs.get('卦', '')}"
                                    f"{(_cs.get('當前爻') or {}).get('爻名', '')}｜"
                                    f"流年{_ln.get('歲', '')}歲{_ln.get('卦', '')}{_ln.get('爻名', '')}"
                                )
                            _yj3 = _v20.get("陽九入三限", {})
                            if _yj3:
                                st.markdown(
                                    f"{t('yangjiu_sanxian')}"
                                    f"{_yj3.get('三限', '')}·{_yj3.get('吉凶', '')}｜"
                                    f"{_yj3.get('斷語', '')[:40]}"
                                )
                            _wx = _v20.get("旺陷獨處同宮論", {})
                            if _wx.get("獨處諸星") or _wx.get("同宮論歌"):
                                _wx_line = "｜".join(
                                    f"{x.get('星', x.get('星組', ''))}{x.get('旺陷', '')}"
                                    for x in (_wx.get("獨處諸星") or [])[:3]
                                )
                                st.markdown(f"{t('wangxian_lun')}{_wx_line or '同宮論'}")
                                with st.expander(t("wangxian_detail"), expanded=False):
                                    for item in _wx.get("獨處諸星") or []:
                                        st.markdown(
                                            f"**{item.get('宮')}** {item.get('星')}·"
                                            f"{item.get('旺陷', item.get('等第', ''))}"
                                        )
                                        st.caption((item.get("論歌") or "")[:120])
                                    for item in _wx.get("同宮論歌") or []:
                                        st.markdown(f"**{item.get('宮')}** {item.get('星組')}")
                                        st.caption((item.get("論歌") or "")[:120])
                            _render_zhao_you_songs(_v20.get("照限游年", {}))
                            _gj = _v20.get("命盤格局", {})
                            if _gj:
                                st.markdown(
                                    f"{t('life_geju')}"
                                    + "；".join(f"{k}：{v}" for k, v in list(_gj.items())[:6])
                                )
                            _pal = _v20.get("十二宮旺衰絕空刑", {})
                            if _pal:
                                _pal_line = "｜".join(
                                    f"{k}{v.get('狀態', '')}"
                                    for k, v in _pal.items()
                                    if v.get("狀態") in ("空", "刑", "絕")
                                )
                                if _pal_line:
                                    st.markdown(f"{t('palace_states')}{_pal_line}")
                                with st.expander(t("palace_state_detail"), expanded=False):
                                    for pname, pinfo in _pal.items():
                                        st.markdown(
                                            f"**{pname}**（{pinfo.get('地支', '')}·"
                                            f"{pinfo.get('狀態', '')}）"
                                            f" {''.join(pinfo.get('星曜', []))}"
                                        )
                                        if pinfo.get("斷語"):
                                            st.caption(pinfo["斷語"])
                            st.markdown("   ")
                        # —— 流日卦時間軸 ——
                        _hex_html = render_hex_timeline(results, t=t)
                        if _hex_html:
                            st.markdown(_hex_html, unsafe_allow_html=True)
                        # —— 統運入卦時間軸 + 運勢卡片 ——
                        _yun_html = render_yun_section(results, t=t)
                        if _yun_html:
                            st.markdown(_yun_html, unsafe_allow_html=True)
                        st.markdown(t("yang_nine"))
                        st.markdown(format_text(results["yjxx"]))
                        st.markdown("   ")
                        st.markdown(t("bai_liu"))
                        st.markdown(format_text(results["blxx"]))
                        st.markdown("   ")
                        st.title(t("taiyi_mishu"))
                        st.markdown(results["ts"])
                        st.title(t("history_records"))
                        st.markdown(results["ch"])
                else:
                    _mobile = _is_mobile()
                    try:
                        start_pt2 = results["genchart2"][results["genchart2"].index('''viewBox="''')+22:].split(" ")[1]
                        chart_meta = _resolve_chart_meta(
                            results,
                            is_life_chart=False,
                            show_geju_markers=show_geju_markers,
                            show_guxu_overlay=show_guxu_overlay,
                            show_wuxing_color=show_wuxing_color,
                        )
                    except (ValueError, IndexError) as e:
                        st.error(f"Failed to parse SVG viewBox: {str(e)}")
                        start_pt2 = 0
                        chart_meta = {}

                    # ── 動態 expander 標題：已選參數摘要 ──
                    _ty_obj = results["ty"]
                    _method_name = (config.ty_method(results["tn"]) or "") + (results["ttext"].get("太乙計", "") or "")
                    _bureau_name = results["ttext"].get("局式", {}).get("年", "") or results.get("kook", {}).get("文", "")
                    _zhi_hour = _hour_to_zhi(_ty_obj.hour)
                    _params_title = (
                        f"已選參數：{_ty_obj.year}年{_ty_obj.month}月{_ty_obj.day}日 "
                        f"{_zhi_hour}時，{_method_name}，{_bureau_name}"
                    )

                    if _mobile:
                        # ── 手機版：排盤結果置頂 + 重新排盤按鈕 + 參數收合 ──
                        # 1. 頂部醒目「重新排盤」按鈕
                        st.markdown('<div class="mobile-run-top">', unsafe_allow_html=True)
                        if st.button(t("rerun_chart_btn"), type="primary",
                                     use_container_width=True, key="mobile_rerun_top"):
                            st.session_state.chart_results = None
                            st.session_state.chart_input_key = None
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

                        # 2. 已選參數收合 expander（動態標題，單層 expander）
                        render_chart_mobile_params(chart_meta, results, t=t, expander_title=_params_title)

                        # 3. 排盤結果（SVG 局式）— 最大視覺權重
                        render_chart_stage_open(
                            print_meta=build_chart_print_meta(results, t=t),
                        )
                        render_chart_explanation_seam()
                        if rotation == "轉動":
                            render_svg(results["genchart2"], int(start_pt2), chart_meta)
                        else:
                            render_svg1(results["genchart2"], int(start_pt2), chart_meta)

                        # 4. 流日卦時間軸
                        _hex_html = render_hex_timeline(results, t=t)
                        if _hex_html:
                            st.markdown(_hex_html, unsafe_allow_html=True)
                        # 5. 統運入卦時間軸 + 運勢卡片
                        _yun_html = render_yun_section(results, t=t)
                        if _yun_html:
                            st.markdown(_yun_html, unsafe_allow_html=True)

                        # 6. 解釋區（巢狀 expander）
                        st.markdown(
                            '<span class="chart-explanation-anchor" aria-hidden="true"></span>',
                            unsafe_allow_html=True,
                        )
                        with st.expander(t("explanation")):
                            _classic_html = render_classic_reading(results, t=t)
                            if _classic_html:
                                st.markdown(_classic_html, unsafe_allow_html=True)

                    else:
                        # ── 桌面版：左排盤 + 右參數面板 雙欄佈局 ──
                        chart_main_col, chart_side_col = st.columns([6.5, 1.8], gap="small")
                        with chart_main_col:
                            render_chart_stage_open(
                                print_meta=build_chart_print_meta(results, t=t),
                            )
                            render_chart_explanation_seam()
                            if rotation == "轉動":
                                render_svg(results["genchart2"], int(start_pt2), chart_meta)
                            else:
                                render_svg1(results["genchart2"], int(start_pt2), chart_meta)
                        with chart_side_col:
                            # 右側資訊面板，預設展開
                            render_chart_side_panel(chart_meta, results, t=t)

                        # —— 流日卦時間軸 ——
                        _hex_html = render_hex_timeline(results, t=t)
                        if _hex_html:
                            st.markdown(_hex_html, unsafe_allow_html=True)
                        # —— 統運入卦時間軸 + 運勢卡片 ——
                        _yun_html = render_yun_section(results, t=t)
                        if _yun_html:
                            st.markdown(_yun_html, unsafe_allow_html=True)
                        st.markdown(
                            '<span class="chart-explanation-anchor" aria-hidden="true"></span>',
                            unsafe_allow_html=True,
                        )
                        with st.expander(t("explanation")):
                            # —— 古典解讀卡片群（全部整合，無重複）——
                            _classic_html = render_classic_reading(results, t=t)
                            if _classic_html:
                                st.markdown(_classic_html, unsafe_allow_html=True)

    except Exception as e:
        st.error(t("gen_error").format(str(e)))

# 使用說明
with tabs[1]:
    st.markdown(get_file_content_as_string(BASE_URL_KINTAIYI, "docs/instruction.md"))

# 太乙局數史例
with tabs[2]:
    timeline(_load_example_timeline_json(), height=600)
    with st.expander(t("list_label")):
        st.markdown(get_file_content_as_string(BASE_URL_KINTAIYI, "docs/example.md"))

# 災害統計
with tabs[3]:
    st.markdown(get_file_content_as_string(BASE_URL_KINTAIYI, "docs/disaster.md"))

# 古籍書目
with tabs[4]:
    st.markdown(get_file_content_as_string(BASE_URL_KINTAIYI, "docs/guji.md"))

# 更新日誌
with tabs[5]:
    _update_md = get_file_content_as_string(BASE_URL_KINTAIYI, "docs/update.md")
    st.markdown(_render_changelog_html_cached(_update_md), unsafe_allow_html=True)

# 看盤要領
with tabs[6]:
    st.markdown(get_file_content_as_string(BASE_URL_KINTAIYI, "docs/tutorial.md"), unsafe_allow_html=True)

# 連結
with tabs[7]:
    st.markdown(get_file_content_as_string(BASE_URL_KINLIUREN, "docs/contact.md"), unsafe_allow_html=True)

# Note: global styling is now handled by custom_css.py (injected near the top of this file).

# ── Fixed Bottom LLM Chat Section ───────────────────────────────────────
# Initialize chat history in session state
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

st.markdown("---")

# Clear chat button
if st.button(t("chat_clear"), key="clear_chat_btn"):
    st.session_state.chat_messages = []
    st.rerun()

# Display welcome message if no messages yet
if not st.session_state.chat_messages:
    with st.chat_message("assistant", avatar="👲"):
        st.markdown(t("chat_welcome"))

# Display chat history
for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"], avatar="👲" if msg["role"] == "assistant" else None):
        st.markdown(msg["content"])

# Chat input (Streamlit auto-fixes this at the bottom)
if user_input := st.chat_input(t("chat_placeholder")):
    # Add user message to history
    st.session_state.chat_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate AI response
    with st.chat_message("assistant", avatar="👲"):
        _provider = st.session_state.get("ai_provider_selector", "Cerebras")
        if _provider == "OpenAI":
            _openai_key = st.session_state.get("openai_api_key_input", "").strip()
            if not _openai_key:
                error_msg = t("openai_api_key_missing")
                st.error(error_msg)
                st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
            else:
                with st.spinner(t("chat_thinking")):
                    try:
                        client = OpenAIClient(api_key=_openai_key)
                        _default_prompt = t("chat_welcome")
                        system_prompt = st.session_state.get("qwen_system_prompt", _default_prompt)
                        messages = [{"role": "system", "content": system_prompt}]
                        messages.extend(st.session_state.chat_messages[-_MAX_CHAT_HISTORY:])
                        api_params = {
                            "messages": messages,
                            "model": st.session_state.get("openai_model_selector", OPENAI_MODEL_OPTIONS[0]),
                            "max_tokens": st.session_state.get("qwen_max_tokens", 8192),
                            "temperature": st.session_state.get("qwen_temperature", 0.7),
                        }
                        response = client.get_chat_completion(**api_params)
                        reply = response.choices[0].message.content
                        st.markdown(reply)
                        st.session_state.chat_messages.append({"role": "assistant", "content": reply})
                    except OpenAITokenQuotaExceededError:
                        error_msg = t("ai_openai_quota_exceeded")
                        st.error(error_msg)
                        st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
                    except Exception as e:
                        error_msg = t("ai_error").format(str(e))
                        st.error(error_msg)
                        st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
        elif _provider == "xAI (Grok)":
            _xai_key = st.session_state.get("xai_api_key_input", "").strip()
            if not _xai_key:
                error_msg = t("xai_api_key_missing")
                st.error(error_msg)
                st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
            else:
                with st.spinner(t("chat_thinking")):
                    try:
                        client = OpenAICompatibleClient(api_key=_xai_key, base_url=XAI_BASE_URL)
                        _default_prompt = t("chat_welcome")
                        system_prompt = st.session_state.get("qwen_system_prompt", _default_prompt)
                        messages = [{"role": "system", "content": system_prompt}]
                        messages.extend(st.session_state.chat_messages[-_MAX_CHAT_HISTORY:])
                        api_params = {
                            "messages": messages,
                            "model": st.session_state.get("xai_model_selector", XAI_MODEL_OPTIONS[0]),
                            "max_tokens": st.session_state.get("qwen_max_tokens", 8192),
                            "temperature": st.session_state.get("qwen_temperature", 0.7),
                        }
                        response = client.get_chat_completion(**api_params)
                        reply = response.choices[0].message.content
                        st.markdown(reply)
                        st.session_state.chat_messages.append({"role": "assistant", "content": reply})
                    except CompatibleTokenQuotaExceededError:
                        error_msg = t("ai_xai_quota_exceeded")
                        st.error(error_msg)
                        st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
                    except Exception as e:
                        error_msg = t("ai_error").format(str(e))
                        st.error(error_msg)
                        st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
        elif _provider == "DeepSeek":
            _deepseek_key = st.session_state.get("deepseek_api_key_input", "").strip()
            if not _deepseek_key:
                error_msg = t("deepseek_api_key_missing")
                st.error(error_msg)
                st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
            else:
                with st.spinner(t("chat_thinking")):
                    try:
                        client = OpenAICompatibleClient(api_key=_deepseek_key, base_url=DEEPSEEK_BASE_URL)
                        _default_prompt = t("chat_welcome")
                        system_prompt = st.session_state.get("qwen_system_prompt", _default_prompt)
                        messages = [{"role": "system", "content": system_prompt}]
                        messages.extend(st.session_state.chat_messages[-_MAX_CHAT_HISTORY:])
                        api_params = {
                            "messages": messages,
                            "model": st.session_state.get("deepseek_model_selector", DEEPSEEK_MODEL_OPTIONS[0]),
                            "max_tokens": st.session_state.get("qwen_max_tokens", 8192),
                            "temperature": st.session_state.get("qwen_temperature", 0.7),
                        }
                        response = client.get_chat_completion(**api_params)
                        reply = response.choices[0].message.content
                        st.markdown(reply)
                        st.session_state.chat_messages.append({"role": "assistant", "content": reply})
                    except CompatibleTokenQuotaExceededError:
                        error_msg = t("ai_deepseek_quota_exceeded")
                        st.error(error_msg)
                        st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
                    except Exception as e:
                        error_msg = t("ai_error").format(str(e))
                        st.error(error_msg)
                        st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
        elif _provider == "Qwen":
            _qwen_key = st.session_state.get("qwen_api_key_input", "").strip()
            if not _qwen_key:
                error_msg = t("qwen_api_key_missing")
                st.error(error_msg)
                st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
            else:
                with st.spinner(t("chat_thinking")):
                    try:
                        client = OpenAICompatibleClient(api_key=_qwen_key, base_url=QWEN_BASE_URL)
                        _default_prompt = t("chat_welcome")
                        system_prompt = st.session_state.get("qwen_system_prompt", _default_prompt)
                        messages = [{"role": "system", "content": system_prompt}]
                        messages.extend(st.session_state.chat_messages[-_MAX_CHAT_HISTORY:])
                        api_params = {
                            "messages": messages,
                            "model": st.session_state.get("qwen_model_selector", QWEN_MODEL_OPTIONS[0]),
                            "max_tokens": st.session_state.get("qwen_max_tokens", 8192),
                            "temperature": st.session_state.get("qwen_temperature", 0.7),
                        }
                        response = client.get_chat_completion(**api_params)
                        reply = response.choices[0].message.content
                        st.markdown(reply)
                        st.session_state.chat_messages.append({"role": "assistant", "content": reply})
                    except CompatibleTokenQuotaExceededError:
                        error_msg = t("ai_qwen_quota_exceeded")
                        st.error(error_msg)
                        st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
                    except Exception as e:
                        error_msg = t("ai_error").format(str(e))
                        st.error(error_msg)
                        st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
        elif _provider == "自定義":
            _ckey = st.session_state.get("custom_provider_api_key", "").strip()
            _chost = st.session_state.get("custom_provider_api_host", "").strip()
            _cpath = st.session_state.get("custom_provider_api_path", "").strip()
            _ccompat = st.session_state.get("custom_provider_network_compat", False)
            _cmodel = st.session_state.get("custom_model_selector") or st.session_state.get("custom_model_direct_input", "")
            if not _ckey:
                error_msg = t("custom_provider_api_key_missing")
                st.error(error_msg)
                st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
            elif not _chost:
                error_msg = t("custom_provider_host_missing")
                st.error(error_msg)
                st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
            elif not _cmodel:
                error_msg = t("custom_provider_no_models")
                st.error(error_msg)
                st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
            else:
                _proto = "http" if _ccompat else "https"
                _base_url = f"{_proto}://{_chost}{_cpath}"
                with st.spinner(t("chat_thinking")):
                    try:
                        client = OpenAICompatibleClient(api_key=_ckey, base_url=_base_url)
                        _default_prompt = t("chat_welcome")
                        system_prompt = st.session_state.get("qwen_system_prompt", _default_prompt)
                        messages = [{"role": "system", "content": system_prompt}]
                        messages.extend(st.session_state.chat_messages[-_MAX_CHAT_HISTORY:])
                        api_params = {
                            "messages": messages,
                            "model": _cmodel,
                            "max_tokens": st.session_state.get("qwen_max_tokens", 8192),
                            "temperature": st.session_state.get("qwen_temperature", 0.7),
                        }
                        response = client.get_chat_completion(**api_params)
                        reply = response.choices[0].message.content
                        st.markdown(reply)
                        st.session_state.chat_messages.append({"role": "assistant", "content": reply})
                    except CompatibleTokenQuotaExceededError:
                        error_msg = t("ai_custom_quota_exceeded")
                        st.error(error_msg)
                        st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
                    except Exception as e:
                        error_msg = t("ai_error").format(str(e))
                        st.error(error_msg)
                        st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
        else:
            cerebras_api_key = st.secrets.get("CEREBRAS_API_KEY") or os.getenv("CEREBRAS_API_KEY")
            if not cerebras_api_key:
                error_msg = t("ai_key_missing")
                st.error(error_msg)
                st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
            else:
                with st.spinner(t("chat_thinking")):
                    try:
                        client = CerebrasClient(api_key=cerebras_api_key)
                        _default_prompt = t("chat_welcome")
                        system_prompt = st.session_state.get("qwen_system_prompt", _default_prompt)
                        messages = [{"role": "system", "content": system_prompt}]
                        # Include recent chat history for context
                        messages.extend(st.session_state.chat_messages[-_MAX_CHAT_HISTORY:])
                        api_params = {
                            "messages": messages,
                            "model": st.session_state.get("cerebras_model_selector", CEREBRAS_MODEL_OPTIONS[0]),
                            "max_tokens": st.session_state.get("qwen_max_tokens", 8192),
                            "temperature": st.session_state.get("qwen_temperature", 0.7),
                        }
                        response = client.get_chat_completion(**api_params)
                        reply = response.choices[0].message.content
                        st.markdown(reply)
                        st.session_state.chat_messages.append({"role": "assistant", "content": reply})
                    except TokenQuotaExceededError:
                        error_msg = t("ai_quota_exceeded")
                        st.error(error_msg)
                        st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
                    except Exception as e:
                        error_msg = t("ai_error").format(str(e))
                        st.error(error_msg)
                        st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
