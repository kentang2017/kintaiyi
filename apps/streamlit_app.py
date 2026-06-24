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
    chart_svg_layout,
    sector_panel_layer_labels,
)

import cn2an
from cn2an import an2cn
from kintaiyi.taiyidict import tengan_shiji, su_dist
from kintaiyi.taiyimishu import taiyi_yingyang
from kintaiyi.historytext import chistory
import streamlit.components.v1 as components
from streamlit.components.v1 import html
import pandas as pd
from kintaiyi.cerebras_client import CerebrasClient, DEFAULT_MODEL as DEFAULT_CEREBRAS_MODEL, TokenQuotaExceededError
from kintaiyi.openai_client import OpenAIClient, DEFAULT_MODEL as DEFAULT_OPENAI_MODEL, TokenQuotaExceededError as OpenAITokenQuotaExceededError
from kintaiyi.openai_compatible_client import OpenAICompatibleClient, TokenQuotaExceededError as CompatibleTokenQuotaExceededError
from kintaiyi.game_theory import TaiyiGame, 主方策略列 as _gt_主方策略列, 客方策略列 as _gt_客方策略列
from custom_css import get_custom_css

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


# --- i18n: Translation dictionaries ---
TRANSLATIONS = {
    "zh": {
        "page_title": "堅太乙 - 太乙排盤",
        "lang_label": "語言 Language",
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
        "instant_btn": "即時盤",
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
        "taiyi_mishu": "《太乙秘書》︰",
        "history_records": "史事記載︰",
        "chart_analysis": "太乙盤局分析︰",
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
        "shi_geju": "釋格局︰",
        "sanqi": "三旗行宮︰",
        "nine_gods": "九宮貴神︰",
        "taiyi_stars": "太乙九星︰",
        "wenchang_stars": "文昌九星︰",
        "wuyun_liuqi": "五運六氣︰",
        "wuyin_shu": "五音之數︰",
        "junshi_vol5": "軍事戰略︰",
        "vol11": "州國災變︰",
        "tongyun_rugua": "統運入卦︰",
        "liunian_zhigua": "流年直卦︰",
        "ruyao_huofu": "入爻禍福︰",
        "shier_yun": "十二運立成︰",
        "lishi_ruyao": "歷史入爻例︰",
        "tongyun_detail": "統運詳情",
        "gua_xiang": "卦象觀象︰",
        "gua_xiang_detail": "卦象詳情",
        "bian_gua_najia": "變卦納甲︰",
        "shouwei": "災厄首尾︰",
        "hangzhi_biannian": "行支編年︰",
        "tongyun_extended": "統運延伸",
        "fenye": "分野疆界︰",
        "guiyun": "大小遊軌運︰",
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
        "junshi_vol17": "軍事占斷︰",
        "shenjiang_suozhu": "神將所主︰",
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
        "game_theory_header": "⚔️ 運籌博弈分析（太乙古法 × Nash 均衡）",
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
        "page_title": "KinTaiYi - Taiyi Divination Chart",
        "lang_label": "語言 Language",
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
        "instant_btn": "Instant Chart",
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
        "vol11": "State Disasters: ",
        "tongyun_rugua": "Cycle Hexagram: ",
        "liunian_zhigua": "Annual Hexagram: ",
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
        "fenye": "Territorial Divisions: ",
        "guiyun": "Major/Minor Wander Hexagrams: ",
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
        "game_theory_header": "⚔️ Operations Research & Game Theory Analysis",
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
            "rotation_hint": "Drag layers 4 and 6 to rotate. Tap for ±30° stepped viewing.",
            "paint_hint": "Tap a sector for details and sync-highlight matching rings (up to four colors).",
            "sector_panel_title": "Sector Reading",
            "sector_panel_empty": "No reading for this sector.",
            "sector_panel_geju": "Patterns (釋格局)",
            "sector_panel_close": "Close",
            "sector_click_hint": "Tap any sector to view classical readings below the chart.",

            "reset": "Reset View",
            "download_png": "Download Plate",
            "add_note": "Add Note",
            "toggle_style_dense": "Data-Dense",
            "toggle_style_compact": "Compact",
            "toggle_style_traditional": "Traditional",
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
        "rotation_hint": "拖曳第 4、6 層可旋轉，輕點則以 ±30° 校覽。",
        "paint_hint": "點選扇區查看斷事，並聯動著色同角度外環（最多四色）。",
        "sector_panel_title": "扇區斷事",
        "sector_panel_empty": "此扇區尚無斷事資料。",
        "sector_panel_geju": "釋格局",
        "sector_panel_close": "關閉",
        "sector_click_hint": "點選盤上任一扇區，於下方顯示古典斷事。",

        "reset": "重置視圖",
        "download_png": "下載盤式",
        "add_note": "加入文字",
        "toggle_style_dense": "資料密集",
        "toggle_style_compact": "簡盤",
        "toggle_style_traditional": "傳統風格",
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


def _build_chart_meta(results: dict, is_life_chart: bool, *, show_geju_markers: bool = True) -> dict:
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
        "太乙", "文昌", "主筭", "客筭", "定筭",
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
    ttext = results.get("ttext", {})
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
    geju_markers = build_geju_sector_markers(ttext) if show_geju_markers else {}
    _raw_svg = results.get("genchart1" if is_life_chart else "genchart2") or ""
    geju_overlay_svg = (
        build_geju_overlay_svg(
            ttext,
            chart_style=chart_style,
            is_life=is_life_chart,
            view_half=_svg_view_half(_raw_svg, 500),
        )
        if show_geju_markers
        else ""
    )
    chart_layout = chart_svg_layout(chart_style, is_life=is_life_chart)
    sync_nums = "、".join(lid.replace("layer", "") for lid in chart_layout["sync_layers"])
    ui_out = dict(ui)
    is_en = st.session_state.get("lang", "zh") == "en"
    if is_en:
        ui_out["sector_click_hint"] = ui["sector_click_hint"]
        ui_out["paint_hint"] = (
            f"Tap a sector for details; layers {sync_nums} sync-highlight at the same angle (up to 4 colors)."
        )
    else:
        ui_out["sector_click_hint"] = ui["sector_click_hint"]
        ui_out["paint_hint"] = (
            f"點選扇區查看斷事，第{sync_nums}層同角度聯動著色（最多四色）。"
        )
    rotate_layers = chart_layout.get("rotate_layers") or []
    if rotate_layers:
        rot_nums = "、".join(lid.replace("layer", "") for lid in rotate_layers)
        ui_out["rotation_hint"] = (
            f"Drag layers {rot_nums} to rotate; tap for ±30° steps."
            if is_en
            else f"拖曳第{rot_nums}層可旋轉，輕點則以 ±30° 校覽。"
        )
    else:
        ui_out["rotation_hint"] = (
            "This chart style does not support rotation."
            if is_en
            else "此盤式不支援轉盤旋轉。"
        )
    sector_panel = {
        "sectors": chart_view.get("sectors") or {},
        "geju": geju_markers,
        "layer_labels": sector_panel_layer_labels(
            is_life=is_life_chart, chart_style=chart_style,
        ),
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
        "show_geju_markers": show_geju_markers,
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
    """Pre-inject geju labels into chart SVG before Streamlit renders it."""
    if not chart_meta.get("show_geju_markers"):
        return raw_svg
    overlay = chart_meta.get("geju_overlay_svg", "")
    if not overlay:
        return raw_svg
    return _inject_geju_overlay(raw_svg, overlay)


def _inject_geju_overlay(svg_markup: str, overlay_svg: str) -> str:
    """Append server-rendered geju markers before the closing </svg> tag."""
    if not overlay_svg or "taiyi-geju-overlay" not in overlay_svg:
        return svg_markup
    if "taiyi-geju-overlay" in svg_markup:
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
        f"{chart_meta.get('geju_overlay_svg', '')}|{sector_panel_json}".encode("utf-8")
    ).hexdigest()[:10]
    container_id = f"taiyi-shell-{component_key}"
    svg_id = f"taiyi-svg-{component_key}"
    glow_id = f"taiyi-glow-{component_key}"
    svg_markup = _inject_geju_overlay(
        _prepare_svg_markup(svg, svg_id, num, chart_meta["title"]),
        chart_meta.get("geju_overlay_svg", ""),
    )

    chips_html = "".join(
        f"""
        <div class="taiyi-meta-chip">
            <span class="taiyi-meta-label">{html_escape(str(label))}</span>
            <strong class="taiyi-meta-value">{html_escape(str(value))}</strong>
        </div>
        """
        for label, value in chart_meta["chips"]
    )
    legend_html = "".join(
        f"""
        <div class="taiyi-legend-item">
            <span class="taiyi-swatch taiyi-swatch-{color_name}"></span>
            <span>{html_escape(detail)}</span>
        </div>
        """
        for color_name, detail in chart_meta["legend"]
    )

    export_css = """
    .taiyi-svg-root {
        background: radial-gradient(circle at 50% 44%, #1c2540 0%, #11172b 58%, #090c18 100%);
        border-radius: 50%;
    }
    .taiyi-svg-root path, .taiyi-svg-root polygon, .taiyi-svg-root rect, .taiyi-svg-root circle, .taiyi-svg-root ellipse {
        stroke: #d7bd6f !important;
        stroke-width: 1.2 !important;
        vector-effect: non-scaling-stroke;
    }
    .taiyi-svg-root text, .taiyi-svg-root tspan {
        fill: #f5f0e1 !important;
        font-family: "Noto Serif SC", "Source Han Serif", "KaiTi", serif !important;
        font-weight: 600 !important;
    }
    .taiyi-svg-root .taiyi-sector > text {
        font-size: 9px !important;
    }
    .taiyi-svg-root #layer1 path, .taiyi-svg-root #layer1 circle, .taiyi-svg-root #layer1 ellipse { fill: #c9a227 !important; }
    .taiyi-svg-root #layer2 path, .taiyi-svg-root #layer2 polygon, .taiyi-svg-root #layer2 rect { fill: rgba(24, 56, 84, 0.95) !important; }
    .taiyi-svg-root #layer3 path, .taiyi-svg-root #layer3 polygon, .taiyi-svg-root #layer3 rect { fill: rgba(14, 36, 56, 0.96) !important; }
    .taiyi-svg-root #layer4 path, .taiyi-svg-root #layer4 polygon, .taiyi-svg-root #layer4 rect { fill: rgba(18, 52, 74, 0.97) !important; }
    .taiyi-svg-root #layer5 path, .taiyi-svg-root #layer5 polygon, .taiyi-svg-root #layer5 rect { fill: rgba(34, 60, 94, 0.95) !important; }
    .taiyi-svg-root #layer6 path, .taiyi-svg-root #layer6 polygon, .taiyi-svg-root #layer6 rect { fill: rgba(22, 48, 70, 0.96) !important; }
    .taiyi-svg-root #layer7 path, .taiyi-svg-root #layer7 polygon, .taiyi-svg-root #layer7 rect { fill: rgba(10, 28, 50, 0.98) !important; }
    .taiyi-svg-root .taiyi-key-spot,
    .taiyi-svg-root .taiyi-user-mark,
    .taiyi-svg-root .taiyi-key-sector { filter: url(#__GLOW_ID__); }
    """

    template = """
    <div id="__CONTAINER_ID__" class="taiyi-shell" data-style-mode="traditional" data-interactive="__INTERACTIVE__">
        <div class="taiyi-card">
            <div class="taiyi-stage">
                <div class="taiyi-stage-frame">
                    <div class="taiyi-svg-backdrop" aria-hidden="true"></div>
                    __SVG_MARKUP__
                </div>
                <div class="taiyi-toolbar" aria-label="chart tools">
                    <button type="button" class="taiyi-btn" data-action="toggle-style">__STYLE_BUTTON__</button>
                    <button type="button" class="taiyi-btn" data-action="reset">__RESET__</button>
                    <button type="button" class="taiyi-btn" data-action="add-note">__ADD_NOTE__</button>
                    <button type="button" class="taiyi-btn" data-action="download-png">__DOWNLOAD_PNG__</button>
                </div>
                <p class="taiyi-sector-hint" aria-live="polite">__SECTOR_HINT__</p>
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
        --chart-max-width: 860px;
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
        overflow: hidden;
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
        width: min(100%, var(--chart-max-width));
        aspect-ratio: 1 / 1;
        overflow: hidden;
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
        margin: 0 auto;
        overflow: visible;
        user-select: none;
        -webkit-user-select: none;
        touch-action: none;
    }
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
    #__CONTAINER_ID__ .taiyi-svg-root text,
    #__CONTAINER_ID__ .taiyi-svg-root tspan {
        fill: var(--ivory) !important;
        font-family: "Noto Serif SC", "Source Han Serif", "KaiTi", serif !important;
        font-size: 9.5px !important;
        font-weight: 600 !important;
        letter-spacing: 0.03em;
        transition: fill 180ms ease, filter 180ms ease, opacity 180ms ease;
    }
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-sector > text {
        font-size: 8.5px !important;
    }
    #__CONTAINER_ID__ .taiyi-svg-root #layer1 path,
    #__CONTAINER_ID__ .taiyi-svg-root #layer1 polygon,
    #__CONTAINER_ID__ .taiyi-svg-root #layer1 rect,
    #__CONTAINER_ID__ .taiyi-svg-root #layer1 circle,
    #__CONTAINER_ID__ .taiyi-svg-root #layer1 ellipse {
        fill: rgba(201, 162, 39, 0.94) !important;
        stroke: rgba(245, 240, 225, 0.82) !important;
        stroke-width: 1.8 !important;
    }
    #__CONTAINER_ID__ .taiyi-svg-root #layer1 text,
    #__CONTAINER_ID__ .taiyi-svg-root #layer1 tspan {
        fill: #f5f0e1 !important;
        font-size: 11px !important;
        font-weight: 700 !important;
    }
    #__CONTAINER_ID__ .taiyi-svg-root #layer2 path,
    #__CONTAINER_ID__ .taiyi-svg-root #layer2 polygon,
    #__CONTAINER_ID__ .taiyi-svg-root #layer2 rect { fill: rgba(20, 46, 68, 0.78) !important; }
    #__CONTAINER_ID__ .taiyi-svg-root #layer3 path,
    #__CONTAINER_ID__ .taiyi-svg-root #layer3 polygon,
    #__CONTAINER_ID__ .taiyi-svg-root #layer3 rect { fill: rgba(10, 28, 43, 0.88) !important; }
    #__CONTAINER_ID__ .taiyi-svg-root #layer4 path,
    #__CONTAINER_ID__ .taiyi-svg-root #layer4 polygon,
    #__CONTAINER_ID__ .taiyi-svg-root #layer4 rect { fill: rgba(15, 43, 62, 0.92) !important; }
    #__CONTAINER_ID__ .taiyi-svg-root #layer5 path,
    #__CONTAINER_ID__ .taiyi-svg-root #layer5 polygon,
    #__CONTAINER_ID__ .taiyi-svg-root #layer5 rect { fill: rgba(31, 49, 78, 0.82) !important; }
    #__CONTAINER_ID__ .taiyi-svg-root #layer6 path,
    #__CONTAINER_ID__ .taiyi-svg-root #layer6 polygon,
    #__CONTAINER_ID__ .taiyi-svg-root #layer6 rect { fill: rgba(17, 39, 56, 0.84) !important; }
    #__CONTAINER_ID__ .taiyi-svg-root #layer7 path,
    #__CONTAINER_ID__ .taiyi-svg-root #layer7 polygon,
    #__CONTAINER_ID__ .taiyi-svg-root #layer7 rect { fill: rgba(8, 22, 40, 0.95) !important; }
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
        touch-action: none;
    }
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-rotatable.is-dragging {
        cursor: grabbing;
        transition: none;
    }
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-colorable,
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-sector-panel-target {
        cursor: pointer;
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
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-key-sector {
        stroke: rgba(212, 175, 55, 0.95) !important;
        stroke-width: 2.3 !important;
    }
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-user-mark {
        stroke: rgba(245, 240, 225, 0.92) !important;
        stroke-width: 2.1 !important;
    }
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-user-label {
        fill: #f5f0e1 !important;
        font-weight: 700 !important;
    }
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-geju-overlay {
        pointer-events: none;
    }
    #__CONTAINER_ID__ .taiyi-svg-root .taiyi-geju-label {
        pointer-events: all;
        cursor: pointer;
        user-select: none;
        font-size: 9px !important;
        font-weight: 700 !important;
        letter-spacing: 0.04em;
    }
    #__CONTAINER_ID__ .taiyi-sector-hint {
        margin: 8px 4px 0;
        font-size: 0.82rem;
        color: var(--ivory-soft);
        text-align: center;
        line-height: 1.45;
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
        }
        #__CONTAINER_ID__ .taiyi-svg-root text,
        #__CONTAINER_ID__ .taiyi-svg-root tspan {
            font-size: 14px !important;
        }
        #__CONTAINER_ID__ .taiyi-svg-root .taiyi-sector > text {
            font-size: 12.5px !important;
        }
        #__CONTAINER_ID__ .taiyi-svg-root #layer1 text,
        #__CONTAINER_ID__ .taiyi-svg-root #layer1 tspan {
            font-size: 16px !important;
        }
        #__CONTAINER_ID__ .taiyi-svg-root .taiyi-geju-label {
            font-size: 12.5px !important;
        }
        #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root text,
        #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root tspan {
            font-size: 13px !important;
        }
        #__CONTAINER_ID__[data-style-mode="dense"] .taiyi-svg-root .taiyi-sector > text {
            font-size: 11.5px !important;
        }
    }
    </style>

    <script>
    (() => {
        const root = document.getElementById("__CONTAINER_ID__");
        if (!root || root.dataset.bound === "true") return;
        root.dataset.bound = "true";

        const svg = root.querySelector(".taiyi-svg-root");
        if (!svg) return;

        const interactive = "__INTERACTIVE__" === "true";
        const ui = __UI_JSON__;
        const highlightTerms = __HIGHLIGHTS_JSON__;
        const exportMeta = __EXPORT_META_JSON__;
        const chartLayout = __CHART_LAYOUT_JSON__;
        const sectorPanelData = __SECTOR_PANEL_JSON__;
        const sectorLookup = sectorPanelData.sectors || {};
        const gejuByBranch = sectorPanelData.geju || {};
        const layerLabels = sectorPanelData.layer_labels || {};
        const colorSyncLayers = chartLayout.sync_layers || ["layer3", "layer4", "layer5"];
        const rotateLayerIds = chartLayout.rotate_layers || [];
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
            noteText: "",
            activeSectorKey: "",
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
            const isMobileViewport = window.matchMedia && window.matchMedia("(max-width: 768px)").matches;
            const heightAdjustment = isMobileViewport ? -22 : 0;
            const height = Math.ceil(Math.max(rectHeight, offsetHeight, scrollHeight) + heightAdjustment);
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
        }

        function rotateLayer(layerId, deltaAngle, immediate) {
            state.rotations[layerId] = ((state.rotations[layerId] || 0) + deltaAngle) % 360;
            applyRotation(layerId, immediate);
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
                    state.drag = null;
                    layer.classList.remove("is-dragging");
                    if (!moved) {
                        state.clickDirection[layerId] *= -1;
                        rotateLayer(layerId, 30 * state.clickDirection[layerId], false);
                    }
                };

                layer.addEventListener("pointerdown", (event) => {
                    event.preventDefault();
                    const point = clientToSvgPoint(event.clientX, event.clientY);
                    const center = getLayerCenter(layer);
                    const angle = angleFromPoint(point, center);
                    state.drag = { layerId: layerId, previousAngle: angle, startAngle: angle, moved: false };
                    layer.classList.add("is-dragging");
                    if (layer.setPointerCapture) layer.setPointerCapture(event.pointerId);
                });

                layer.addEventListener("pointermove", (event) => {
                    if (!state.drag || state.drag.layerId !== layerId) return;
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
            return Array.from(layer.querySelectorAll(":scope > .taiyi-sector"));
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

        function applySyncMarker(fraction, color) {
            colorSyncLayers.forEach((layerId) => {
                const sectorGroup = findSectorAtFraction(layerId, fraction);
                if (sectorGroup) paintSectorGroup(sectorGroup, color);
            });
        }

        function clearSyncMarker(fraction) {
            colorSyncLayers.forEach((layerId) => {
                const sectorGroup = findSectorAtFraction(layerId, fraction);
                if (sectorGroup) restoreSectorGroup(sectorGroup);
            });
        }

        function paintSectorGroup(sectorGroup, color) {
            const match = sectorNodes(sectorGroup);
            if (!match.sector) return;
            if (!match.sector.dataset.originalFill) {
                match.sector.dataset.originalFill = window.getComputedStyle(match.sector).fill || match.sector.dataset.semanticFill || "";
                match.sector.dataset.originalStroke = window.getComputedStyle(match.sector).stroke || match.sector.dataset.semanticStroke || "";
            }
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
            if (originalFill) setStyledColor(match.sector, "fill", originalFill);
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
            return layer.querySelector(':scope > .taiyi-sector[data-sector="' + parts[1] + '"]');
        }

        function clearMarker(key) {
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

        function renderGejuBlock(branch) {
            if (!sectorPanelGeju || !branch) {
                if (sectorPanelGeju) sectorPanelGeju.innerHTML = "";
                return;
            }
            const items = gejuByBranch[branch] || [];
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
            const layerLabel = layerLabels[layerId] || layerId;
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
            renderGejuBlock(posBranch);
            sectorPanel.hidden = false;
            queueFrameHeight();
        }

        function openGejuPanel(branch) {
            if (!branch || !sectorPanel) return;
            clearSectorSelection();
            if (sectorPanelLayer) sectorPanelLayer.textContent = ui.sector_panel_geju || "釋格局";
            if (sectorPanelTitle) sectorPanelTitle.textContent = branch;
            const list = sectorPanel.querySelector(".taiyi-sector-panel-lines");
            if (list) {
                list.innerHTML = "";
                const hint = document.createElement("li");
                hint.textContent = ui.sector_click_hint || "";
                list.appendChild(hint);
            }
            renderGejuBlock(branch);
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

        function handleSectorPanelClick(sectorGroup, event) {
            event.preventDefault();
            event.stopPropagation();
            const layerId = sectorGroup.getAttribute("data-layer") || "";
            if (layerId && layerId !== "layer1") {
                handleSectorColorClick(sectorGroup, event);
            }
            openSectorPanelFromGroup(sectorGroup);
        }

        function setupSectorPanel() {
            if (!sectorPanel) return;
            Array.from(svg.querySelectorAll(".taiyi-sector")).forEach((sectorGroup) => {
                sectorGroup.classList.add("taiyi-sector-panel-target");
                sectorGroup.addEventListener("pointerdown", (event) => {
                    event.stopPropagation();
                });
                sectorGroup.addEventListener("click", (event) => handleSectorPanelClick(sectorGroup, event));
            });
            Array.from(svg.querySelectorAll(".taiyi-geju-label")).forEach((labelNode) => {
                labelNode.addEventListener("click", (event) => {
                    event.preventDefault();
                    event.stopPropagation();
                    openGejuPanel(labelNode.getAttribute("data-branch") || "");
                });
            });
            const closeButton = root.querySelector('[data-action="close-panel"]');
            if (closeButton) closeButton.addEventListener("click", closeSectorPanel);
        }

        function handleSectorColorClick(sectorGroup, event) {
            event.preventDefault();
            event.stopPropagation();
            const layerId = sectorGroup.getAttribute("data-layer") || "";
            const fraction = getSectorFraction(sectorGroup);
            const isSyncLayer = colorSyncLayers.indexOf(layerId) !== -1 && fraction !== null;
            const key = isSyncLayer ? syncColorKey(fraction) : sectorColorKey(sectorGroup);
            if (!key || key === ":") return;
            if (state.colored.has(key)) {
                clearMarker(key);
                state.colored.delete(key);
                return;
            }
            if (state.colored.size >= highlightPalette.length) return;
            const color = highlightPalette[state.colored.size];
            state.colored.set(key, color);
            if (isSyncLayer) {
                applySyncMarker(fraction, color);
            } else {
                paintSectorGroup(sectorGroup, color);
            }
        }

        function setupColoring() {
            Array.from(svg.querySelectorAll(".taiyi-sector"))
                .filter((sectorGroup) => sectorGroup.getAttribute("data-layer") !== "layer1")
                .forEach((sectorGroup) => sectorGroup.classList.add("taiyi-colorable"));
        }

        function resetView() {
            rotateLayerIds.forEach((layerId) => {
                state.rotations[layerId] = 0;
                applyRotation(layerId, false);
            });
            Array.from(state.colored.keys()).forEach((key) => clearMarker(key));
            state.colored.clear();
            closeSectorPanel();
            root.setAttribute("data-style-mode", "traditional");
            state.styleMode = "traditional";
            updateStyleButton();
        }

        function updateStyleButton() {
            const button = root.querySelector('[data-action="toggle-style"]');
            if (!button) return;
            button.textContent = state.styleMode === "traditional" ? ui.toggle_style_dense : ui.toggle_style_traditional;
        }

        function toggleStyleMode() {
            state.styleMode = state.styleMode === "traditional" ? "dense" : "traditional";
            root.setAttribute("data-style-mode", state.styleMode);
            updateStyleButton();
            setFrameHeight();
        }

        function addNote() {
            const nextValue = window.prompt(ui.divination_note_prompt, state.noteText || "");
            if (nextValue === null) return;
            saveNote(nextValue);
        }

        function downloadPng() {
            const scale = 2;
            const viewBox = (svg.getAttribute("viewBox") || "0 0 __NUM__ __NUM__").split(/[ ,]+/);
            const width = parseFloat(viewBox[2]) || __NUM__;
            const height = parseFloat(viewBox[3]) || __NUM__;

            const clone = svg.cloneNode(true);
            const styleNode = document.createElementNS("http://www.w3.org/2000/svg", "style");
            styleNode.textContent = __EXPORT_CSS__;
            clone.insertBefore(styleNode, clone.firstChild);

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

        root.querySelector('[data-action="reset"]').addEventListener("click", resetView);
        root.querySelector('[data-action="toggle-style"]').addEventListener("click", toggleStyleMode);
        root.querySelector('[data-action="add-note"]').addEventListener("click", addNote);
        root.querySelector('[data-action="download-png"]').addEventListener("click", downloadPng);

        loadSavedNote();
        ensureGlowFilter();
        annotateSvg();
        highlightImportantNodes();
        setupSectorPanel();
        if (interactive) setupRotations();
        setupColoring();
        updateStyleButton();
        updateNoteButton();

        if (window.ResizeObserver) {
            const observer = new ResizeObserver(() => queueFrameHeight());
            observer.observe(root);
            observer.observe(svg);
        }
        window.addEventListener("load", queueFrameHeight, { once: true });
        setTimeout(queueFrameHeight, 80);
        setTimeout(queueFrameHeight, 260);
    })();
    </script>
    """

    html_content = (
        template
        .replace("__CONTAINER_ID__", container_id)
        .replace("__INTERACTIVE__", "true" if interactive else "false")
        .replace("__STYLE_BUTTON__", html_escape(ui["toggle_style_dense"]))
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
        .replace("__SECTOR_HINT__", html_escape(chart_meta.get("ui", ui).get("sector_click_hint", "")))
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
        .replace("__EXPORT_CSS__", json.dumps(export_css.replace("__GLOW_ID__", glow_id), ensure_ascii=False))
    )
    html(html_content, height=max(920, abs(num) + 180), scrolling=False)


def render_svg(svg, num, chart_meta):
    """Render the enhanced Taiyi chart with drag rotation on layers 4 and 6."""
    _render_taiyi_chart(svg, num, chart_meta, interactive=True)


def render_svg1(svg, num, chart_meta):
    """Render the enhanced Taiyi chart with focus-marking interactions."""
    _render_taiyi_chart(svg, num, chart_meta, interactive=False)


def render_chart_explanation_seam():
    """Tighten the gap between the chart component and the following explanation expander."""
    st.markdown(
        """
        <style>
        @media (max-width: 768px) {
            div[data-testid="stElementContainer"]:has(.taiyi-chart-seam-anchor)
            + div[data-testid="stElementContainer"]:has(iframe) {
                margin-bottom: -2.8rem !important;
            }
            div[data-testid="stElementContainer"]:has(.taiyi-chart-seam-anchor)
            + div[data-testid="stElementContainer"]:has(iframe)
            + div[data-testid="stElementContainer"] {
                margin-top: 0 !important;
            }
            div[data-testid="stElementContainer"]:has(.taiyi-chart-seam-anchor)
            + div[data-testid="stElementContainer"]:has(iframe)
            + div[data-testid="stElementContainer"] div[data-testid="stExpander"] {
                margin-top: 0 !important;
            }
        }
        </style>
        <div class="taiyi-chart-seam-anchor" aria-hidden="true"></div>
        """,
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
    components.html(htmlcode, height=height)

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
st.set_page_config(
    layout="wide",
    page_title=t("page_title"),
    page_icon=os.path.join(_REPO_ROOT, "assets", "icon.jpg")
)
# Inject Chinese classical theme CSS globally
st.markdown(get_custom_css(), unsafe_allow_html=True)
# 定義基礎 URL
BASE_URL_KINTAIYI = 'https://raw.githubusercontent.com/kentang2017/kintaiyi/master/'
BASE_URL_KINLIUREN = 'https://raw.githubusercontent.com/kentang2017/kinliuren/master/'

# 側邊欄輸入
with st.sidebar:
    lang_choice = st.selectbox(
        "語言 Language",
        ["中文", "English"],
        index=0 if st.session_state.lang == "zh" else 1,
        key="lang_select",
    )
    new_lang = "zh" if lang_choice == "中文" else "en"
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()

    st.header(t("param_header"))
    
    now = datetime.datetime.now(pytz.timezone('Asia/Hong_Kong'))
    col1, col2 = st.columns(2)
    with col1:
        my = st.number_input(t("year"), min_value=0, max_value=2100, value=now.year, key="year")
        mm = st.number_input(t("month"), min_value=1, max_value=12, value=now.month, key="month")
        md = st.number_input(t("day"), min_value=1, max_value=31, value=now.day, key="day")
    with col2:
        mh = st.number_input(t("hour"), min_value=0, max_value=23, value=now.hour, key="hour")
        mmin = st.number_input(t("minute"), min_value=0, max_value=59, value=now.minute, key="minute")
    
    option = st.selectbox(
        t("chart_method"),
        ('時計太乙', '年計太乙', '月計太乙', '日計太乙', '分計太乙', '太乙命法', '太乙命法 (魔改)'),
        format_func=to,
    )
    acum = st.selectbox(t("acc_years"), ('太乙統宗', '太乙金鏡', '太乙淘金歌', '太乙局'), format_func=to)
    ten_ching = st.selectbox(t("ten_essences"), ('無', '有'), format_func=to)
    sex_o = st.selectbox(t("life_gender"), ('男', '女'), format_func=to)
    rotation = st.selectbox(t("rotation_label"), ('固定', '轉動'), format_func=to)
    show_geju_markers = st.toggle(t("geju_markers_toggle"), value=True, key="show_geju_markers")

    num_dict = {
        '時計太乙': 3, '年計太乙': 0, '月計太乙': 1, '日計太乙': 2, '分計太乙': 4,
        '太乙命法': 6, '太乙命法 (魔改)': 5,
    }
    style = num_dict[option]
    tn_dict = {'太乙統宗': 0, '太乙金鏡': 1, '太乙淘金歌': 2, '太乙局': 3}
    tn = tn_dict[acum]
    tc_dict = {'有': 1, '無': 0}
    tc = tc_dict[ten_ching]
    
    instant = st.button(t("instant_btn"), use_container_width=True)
    
    st.markdown("---")
    st.header(t("ai_settings"))

    ai_provider = st.selectbox(
        t("ai_provider"),
        options=["Cerebras", "OpenAI", "xAI (Grok)", "DeepSeek", "Qwen", "自定義"],
        index=0,
        key="ai_provider_selector",
    )

    if ai_provider == "OpenAI":
        openai_api_key_input = st.text_input(
            t("openai_api_key_label"),
            type="password",
            placeholder=t("openai_api_key_placeholder"),
            key="openai_api_key_input",
        )
        selected_model = st.selectbox(
            t("ai_model"),
            options=OPENAI_MODEL_OPTIONS,
            index=0,
            key="openai_model_selector",
            help="\n".join(f"• {k}: {v}" for k, v in OPENAI_MODEL_DESCRIPTIONS.items())
        )
    elif ai_provider == "xAI (Grok)":
        openai_api_key_input = ""
        st.text_input(
            t("xai_api_key_label"),
            type="password",
            placeholder=t("xai_api_key_placeholder"),
            key="xai_api_key_input",
        )
        selected_model = st.selectbox(
            t("ai_model"),
            options=XAI_MODEL_OPTIONS,
            index=0,
            key="xai_model_selector",
            help="\n".join(f"• {k}: {v}" for k, v in XAI_MODEL_DESCRIPTIONS.items())
        )
    elif ai_provider == "DeepSeek":
        openai_api_key_input = ""
        st.text_input(
            t("deepseek_api_key_label"),
            type="password",
            placeholder=t("deepseek_api_key_placeholder"),
            key="deepseek_api_key_input",
        )
        selected_model = st.selectbox(
            t("ai_model"),
            options=DEEPSEEK_MODEL_OPTIONS,
            index=0,
            key="deepseek_model_selector",
            help="\n".join(f"• {k}: {v}" for k, v in DEEPSEEK_MODEL_DESCRIPTIONS.items())
        )
    elif ai_provider == "Qwen":
        openai_api_key_input = ""
        st.text_input(
            t("qwen_api_key_label"),
            type="password",
            placeholder=t("qwen_api_key_placeholder"),
            key="qwen_api_key_input",
        )
        selected_model = st.selectbox(
            t("ai_model"),
            options=QWEN_MODEL_OPTIONS,
            index=0,
            key="qwen_model_selector",
            help="\n".join(f"• {k}: {v}" for k, v in QWEN_MODEL_DESCRIPTIONS.items())
        )
    elif ai_provider == "自定義":
        # ── Custom provider settings ──────────────────────────────
        if "custom_provider_models" not in st.session_state:
            st.session_state.custom_provider_models = []

        st.text_input(
            t("custom_provider_name"),
            key="custom_provider_name",
            placeholder="自定義服務商",
        )
        st.selectbox(
            t("custom_provider_api_mode"),
            options=[t("custom_provider_api_mode_option")],
            key="custom_provider_api_mode",
        )

        # API key with show/hide and validate button
        show_key = st.toggle(t("custom_provider_show_key"), key="custom_provider_show_key", value=False)
        col_key, col_check = st.columns([3, 1])
        with col_key:
            st.text_input(
                t("custom_provider_api_key"),
                type="text" if show_key else "password",
                key="custom_provider_api_key",
            )
        with col_check:
            st.markdown("<br>", unsafe_allow_html=True)
            check_key_btn = st.button(t("custom_provider_check_btn"), key="custom_provider_check_key_btn", use_container_width=True)

        if check_key_btn:
            _ckey = st.session_state.get("custom_provider_api_key", "").strip()
            _chost = st.session_state.get("custom_provider_api_host", "").strip()
            _cpath = st.session_state.get("custom_provider_api_path", "").strip()
            _ccompat = st.session_state.get("custom_provider_network_compat", False)
            if not _ckey:
                st.error(t("custom_provider_api_key_missing"))
            elif not _chost:
                st.error(t("custom_provider_host_missing"))
            else:
                _proto = "http" if _ccompat else "https"
                _base_url = f"{_proto}://{_chost}{_cpath}"
                try:
                    _check_client = OpenAICompatibleClient(api_key=_ckey, base_url=_base_url)
                    _check_client.list_models()
                    st.success(t("custom_provider_key_ok"))
                except Exception as _check_err:
                    st.error(t("custom_provider_key_fail").format(str(_check_err)))

        # API host and path side by side
        col_host, col_path = st.columns(2)
        with col_host:
            st.text_input(
                t("custom_provider_api_host"),
                key="custom_provider_api_host",
                placeholder="api.openai.com",
            )
        with col_path:
            st.text_input(
                t("custom_provider_api_path"),
                key="custom_provider_api_path",
                placeholder="/v1",
            )

        # Network compatibility toggle
        st.toggle(
            t("custom_provider_network_compat"),
            key="custom_provider_network_compat",
            value=False,
        )

        # Models section
        st.markdown(f"**{t('custom_provider_models_label')}**")
        col_add_btn, col_reset_btn, col_fetch_btn = st.columns(3)
        with col_add_btn:
            open_add_model = st.button(t("custom_provider_add_model"), key="custom_provider_open_add_model", use_container_width=True)
        with col_reset_btn:
            reset_models_btn = st.button(t("custom_provider_reset_models"), key="custom_provider_reset_models_btn", use_container_width=True)
        with col_fetch_btn:
            fetch_models_btn = st.button(t("custom_provider_fetch_models"), key="custom_provider_fetch_models_btn", use_container_width=True)

        if reset_models_btn:
            st.session_state.custom_provider_models = []
            st.rerun()

        if fetch_models_btn:
            _ckey = st.session_state.get("custom_provider_api_key", "").strip()
            _chost = st.session_state.get("custom_provider_api_host", "").strip()
            _cpath = st.session_state.get("custom_provider_api_path", "").strip()
            _ccompat = st.session_state.get("custom_provider_network_compat", False)
            if not _ckey:
                st.error(t("custom_provider_api_key_missing"))
            elif not _chost:
                st.error(t("custom_provider_host_missing"))
            else:
                _proto = "http" if _ccompat else "https"
                _base_url = f"{_proto}://{_chost}{_cpath}"
                try:
                    _fetch_client = OpenAICompatibleClient(api_key=_ckey, base_url=_base_url)
                    _fetched = _fetch_client.list_models()
                    st.session_state.custom_provider_models = _fetched
                    st.success(t("custom_provider_fetch_ok").format(len(_fetched)))
                    st.rerun()
                except Exception as _fetch_err:
                    st.error(t("custom_provider_fetch_fail").format(str(_fetch_err)))

        if open_add_model:
            st.session_state.custom_provider_add_model_open = True

        if st.session_state.get("custom_provider_add_model_open"):
            new_model_name = st.text_input(
                t("custom_provider_models_label"),
                key="custom_provider_new_model_input",
                placeholder=t("custom_provider_new_model_placeholder"),
                label_visibility="collapsed",
            )
            if st.button("✅", key="custom_provider_confirm_add_model"):
                if new_model_name.strip():
                    models = st.session_state.custom_provider_models
                    if new_model_name.strip() not in models:
                        models.append(new_model_name.strip())
                        st.session_state.custom_provider_models = models
                    st.session_state.custom_provider_add_model_open = False
                    st.rerun()

        _custom_models = st.session_state.get("custom_provider_models", [])
        if _custom_models:
            selected_model = st.selectbox(
                t("ai_model"),
                options=_custom_models,
                index=0,
                key="custom_model_selector",
            )
        else:
            selected_model = st.text_input(
                t("ai_model"),
                key="custom_model_direct_input",
                placeholder=t("custom_provider_new_model_placeholder"),
            )
    else:
        openai_api_key_input = ""
        selected_model = st.selectbox(
            t("ai_model"),
            options=CEREBRAS_MODEL_OPTIONS,
            index=0,
            key="cerebras_model_selector",
            help="\n".join(f"• {k}: {v}" for k, v in CEREBRAS_MODEL_DESCRIPTIONS.items())
        )
    
    system_prompts_data = load_system_prompts()
    prompts_list = system_prompts_data.get("prompts", [])
    prompt_names = [prompt["name"] for prompt in prompts_list]
    selected_prompt = system_prompts_data.get("selected")
    
    if prompt_names:
        selected_index = 0
        if selected_prompt in prompt_names:
            selected_index = prompt_names.index(selected_prompt)
        
        selected_name = st.selectbox(
            t("select_prompt"),
            options=prompt_names,
            index=selected_index,
            key="qwen_system_prompt_selector",
            help=t("select_prompt_help")
        )
        
        system_prompts_data["selected"] = selected_name
        
        selected_content = ""
        for prompt in prompts_list:
            if prompt["name"] == selected_name:
                selected_content = prompt["content"]
                break
        
        if 'qwen_system_prompt' not in st.session_state:
            st.session_state.qwen_system_prompt = selected_content
        elif selected_name != st.session_state.get("last_selected_qwen_prompt"):
            st.session_state.qwen_system_prompt = selected_content
        
        st.session_state.last_selected_qwen_prompt = selected_name
        
        new_content = st.text_area(
            t("edit_prompt"),
            value=st.session_state.qwen_system_prompt,
            height=150,
            placeholder=t("edit_prompt_placeholder"),
            key="qwen_system_editor"
        )
        
        st.session_state.qwen_system_prompt = new_content
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(t("update_prompt"), key="update_qwen_prompt_button"):
                for prompt in prompts_list:
                    if prompt["name"] == selected_name:
                        prompt["content"] = new_content
                        break
                if save_system_prompts(system_prompts_data):
                    st.toast(t("prompt_updated").format(selected_name))
        
        with col2:
            if st.button(t("delete_prompt"), key="delete_qwen_prompt_button", 
                        disabled=len(prompts_list) <= 1):
                prompts_list = [p for p in prompts_list if p["name"] != selected_name]
                system_prompts_data["prompts"] = prompts_list
                if selected_name == selected_prompt and prompts_list:
                    system_prompts_data["selected"] = prompts_list[0]["name"]
                if save_system_prompts(system_prompts_data):
                    st.toast(t("prompt_deleted").format(selected_name))
                    st.rerun()
    
    if "qwen_form_key_suffix" not in st.session_state:
        st.session_state.qwen_form_key_suffix = 0
    
    name_key = f"new_qwen_prompt_name_{st.session_state.qwen_form_key_suffix}"
    content_key = f"new_qwen_prompt_content_{st.session_state.qwen_form_key_suffix}"
    
    with st.expander(t("add_prompt_expander"), expanded=False):
        new_prompt_name = st.text_input(t("new_prompt_name"), key=name_key)
        new_prompt_content = st.text_area(
            t("new_prompt_content"),
            height=100,
            placeholder=t("new_prompt_placeholder"),
            key=content_key
        )
        if st.button(t("add_prompt_btn"), key="add_qwen_prompt_button",
                    disabled=not new_prompt_name or not new_prompt_content):
            if new_prompt_name in prompt_names:
                st.error(t("prompt_exists").format(new_prompt_name))
            else:
                prompts_list.append({
                    "name": new_prompt_name,
                    "content": new_prompt_content
                })
                system_prompts_data["prompts"] = prompts_list
                if save_system_prompts(system_prompts_data):
                    st.session_state.qwen_form_key_suffix += 1
                    st.toast(t("prompt_added").format(new_prompt_name))
                    st.rerun()
    
    if st.toggle(t("advanced_settings"), key="qwen_advanced_settings_toggle"):
        st.session_state.qwen_max_tokens = st.slider(
            t("max_tokens"),
            1024, 32768,
            st.session_state.get("qwen_max_tokens", 8192),
            key="qwen_max_tokens_slider",
            help=t("max_tokens_help")
        )
        st.session_state.qwen_temperature = st.slider(
            t("temperature"),
            0.0, 1.5,
            st.session_state.get("qwen_temperature", 0.7),
            step=0.05,
            key="qwen_temperature_slider",
            help=t("temperature_help")
        )
    
    st.markdown("---")
    if st.toggle(t("debug_mode"), key="debug_mode_toggle", help=t("debug_help")):
        st.subheader(t("debug_info"))
        st.write("Session State:")
        st.json(st.session_state)

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

# 創建標籤頁
tabs = st.tabs([t('tab_chart'), t('tab_instructions'), t('tab_history'), t('tab_disaster'), t('tab_books'), t('tab_updates'), t('tab_guide'), t('tab_links')])

# 太乙排盤
with tabs[0]:
    output = st.empty()
    with st_capture(output.code):
        try:
            if instant:
                now = datetime.datetime.now(pytz.timezone('Asia/Hong_Kong'))
                results = gen_results(now.year, now.month, now.day, now.hour, now.minute, style, tn, sex_o, tc)
                st.session_state.render_default = False
            else:
                results = gen_results(my, mm, md, mh, mmin, style, tn, sex_o, tc)
                st.session_state.render_default = False

            if results:
                if _is_life_chart_style(results["style"]):
                    try:
                        start_pt = results["genchart1"][results["genchart1"].index('''viewBox="''')+22:].split(" ")[1]
                        chart_meta = _build_chart_meta(
                            results, is_life_chart=True, show_geju_markers=show_geju_markers,
                        )
                        render_chart_explanation_seam()
                        life_svg = _chart_svg_with_geju(results["genchart1"], chart_meta)
                        if rotation == "轉動":
                            render_svg(life_svg, int(start_pt), chart_meta)
                        else:
                            render_svg1(life_svg, int(start_pt), chart_meta)
                    except (ValueError, IndexError) as e:
                        st.error(f"Failed to parse SVG viewBox: {str(e)}")
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
                        _v20 = results.get("life_vol20") or {}
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
                        st.markdown(t("hexagram"))
                        st.markdown(f"{t('year_hex')}{results['ygua']}")
                        st.markdown(f"{t('month_hex')}{results['mgua']}")
                        st.markdown(f"{t('day_hex')}{results['dgua']}")
                        st.markdown(f"{t('hour_hex')}{results['hgua']}")
                        st.markdown(f"{t('minute_hex')}{results['mingua']}")
                        st.markdown("   ")
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
                    print(f"{config.gendatetime(my, mm, md, mh, mmin)} {results['zhao']} - {results['ty'].taiyi_life(results['sex_o']).get('性別')} - {config.taiyi_name(0)[0]} - {results['ty'].accnum(0, 0)} | \n{t('lunar_label')}︰{results['lunard']} | {jieqi.jq(my, mm, md, mh, mmin)} |\n{results['gz']} |\n{config.kingyear(my)} |\n{t('taiyi_life_method')} - {results['ty'].kook(0, 0).get('文')} ({results['ttext'].get('局式').get('年')}) | \n{t('epoch_label')}︰{results['ttext'].get('紀元')} | {t('home_calc')}︰{results['homecal']} {t('away_calc')}︰{results['awaycal']} |")
                else:
                    try:
                        start_pt2 = results["genchart2"][results["genchart2"].index('''viewBox="''')+22:].split(" ")[1]
                        chart_meta = _build_chart_meta(
                            results, is_life_chart=False, show_geju_markers=show_geju_markers,
                        )
                        render_chart_explanation_seam()
                        chart_svg = _chart_svg_with_geju(results["genchart2"], chart_meta)
                        if rotation == "轉動":
                            render_svg(chart_svg, int(start_pt2), chart_meta)
                        else:
                            render_svg1(chart_svg, int(start_pt2), chart_meta)
                    except (ValueError, IndexError) as e:
                        st.error(f"Failed to parse SVG viewBox: {str(e)}")
                    with st.expander(t("explanation")):
                        st.title(t("taiyi_mishu"))
                        st.markdown(results["ts"])
                        st.title(t("history_records"))
                        st.markdown(results["ch"])
                        st.title(t("chart_analysis"))
                        st.markdown(f"{t('year_star_predict')}{results['year_predict']}")
                        st.markdown(f"{t('start_star_predict')}{results['sj_su_predict']}")
                        st.markdown(f"{t('ten_stem_predict')}{results['tg_sj_su_predict']}")
                        st.markdown(f"{t('sky_ground_method')}{results['ty'].ty_gong_dist(results['style'], results['tn'])}")
                        st.markdown(f"{t('three_five')}{results['three_door'] + results['five_generals']}")
                        st.markdown(f"{t('home_away')}{results['home_vs_away1']}")
                        st.markdown(f"{t('win_loss')}{results['ttext'].get('推少多以占勝負')}")
                        st.markdown(f"{t('wind_cloud')}{results['home_vs_away3']}")
                        st.markdown(f"{t('solitary')}{results['ttext'].get('推孤單以占成敗')}")
                        st.markdown(f"{t('yin_yang_adversity')}{results['ttext'].get('推陰陽以占厄會')}")
                        st.markdown(f"{t('emperor_tour')}{results['ttext'].get('明天子巡狩之期術')}")
                        st.markdown(f"{t('ruler_base')}{results['ttext'].get('明君基太乙所主術')}")
                        st.markdown(f"{t('minister_base')}{results['ttext'].get('明臣基太乙所主術')}")
                        st.markdown(f"{t('people_base')}{results['ttext'].get('明民基太乙所主術')}")
                        st.markdown(f"{t('five_blessings')}{results['ttext'].get('明五福太乙所主術')}")
                        st.markdown(f"{t('five_blessings_calc')}{results['ttext'].get('明五福吉算所主術')}")
                        st.markdown(f"{t('heaven_yi')}{results['ttext'].get('明天乙太乙所主術')}")
                        st.markdown(f"{t('earth_yi')}{results['ttext'].get('明地乙太乙所主術')}")
                        st.markdown(f"{t('zhifu')}{results['ttext'].get('明值符太乙所主術')}")
                        # —— 十六宮分佈 ——
                        _16 = results["ttext"].get("十六宮分佈", {})
                        if _16:
                            _16_parts = []
                            for zhi, stars in _16.items():
                                if stars:
                                    _16_parts.append(f"{zhi}[{'、'.join(stars)}]")
                            if _16_parts:
                                st.markdown(f"{t('sixteen_palace')}{'；'.join(_16_parts)}")
                        # —— 卷四：釋格局 ——
                        _sg = results["ttext"].get("釋格局", {})
                        if _sg:
                            _sg_text = "；".join([f"{k}——{v}" for k, v in _sg.items()])
                            st.markdown(f"{t('shi_geju')}{_sg_text}")
                        # —— 卷十：三旗行宮 ——
                        _sq = results["ttext"].get("三旗行宮", {})
                        if _sq:
                            st.markdown(f"{t('sanqi')}太歲青龍旗{_sq.get('太歲青龍旗')}、太陰黑旗{_sq.get('太陰黑旗')}、害氣赤旗{_sq.get('害氣赤旗')}（{_sq.get('會合')}）")
                        # —— 卷十：九宮貴神 ——
                        _ng = results["ttext"].get("九宮貴神", {})
                        if _ng:
                            _dist = _ng.get("九宮貴神分布", {})
                            _dist_text = "、".join([f"{g}宮{nm}" for g, nm in _dist.items()])
                            st.markdown(f"{t('nine_gods')}直事貴神爲{_ng.get('直事貴神')}（小周餘{_ng.get('小周餘')}）；鈎宮分布：{_dist_text}")
                        # —— 卷六：太乙九星 ——
                        _ts = results["ttext"].get("太乙九星", {})
                        if _ts:
                            _ts_dist = _ts.get("九星分布", {})
                            _ts_text = "、".join([f"{g}宮{nm}" for g, nm in _ts_dist.items()])
                            st.markdown(
                                f"{t('taiyi_stars')}直符{_ts.get('直符九星')}（入宮{_ts.get('入星宮年數')}年）"
                                f"；{_ts.get('直符所主')}；分布：{_ts_text}")
                        # —— 卷六：文昌九星 ——
                        _ws = results["ttext"].get("文昌九星", {})
                        if _ws:
                            _ws_dist = _ws.get("文昌九星分布", {})
                            _ws_text = "、".join([f"{g}宮{nm}" for g, nm in _ws_dist.items()])
                            st.markdown(
                                f"{t('wenchang_stars')}直事{_ws.get('直事文昌星')}（入宮{_ws.get('入宮年數')}年）"
                                f"；臨{_ws.get('臨宮分野')}；分布：{_ws_text}")
                        # —— 卷三：五運六氣 ——
                        _wl = results["ttext"].get("五運六氣", {})
                        if _wl:
                            _hui = "、".join(_wl.get("歲會天符", []))
                            st.markdown(
                                f"{t('wuyun_liuqi')}{_wl.get('五運')}（{_wl.get('太過不及')}）"
                                f"司天{_wl.get('司天')}{_wl.get('司天化')}、在泉{_wl.get('在泉')}{_wl.get('在泉化')}；"
                                f"{_wl.get('主氣', '')}{_wl.get('客氣', '')}；歲會：{_hui}")
                        # —— 卷三：五音之數 ——
                        _wy = results["ttext"].get("五音之數", {})
                        if _wy:
                            _hm = _wy.get("主算五音", {})
                            _am = _wy.get("客算五音", {})
                            _ty = _wy.get("太乙五音", {})
                            st.markdown(
                                f"{t('wuyin_shu')}主算{_hm.get('音')}（{_hm.get('所主')}）"
                                f"、客算{_am.get('音')}（{_am.get('所主')}）"
                                f"、太乙宮{_ty.get('音', '—')}；"
                                f"主斷：{_hm.get('斷語', '')}")
                        # —— 卷五：軍事戰略 ——
                        _j5 = results["ttext"].get("軍事戰略", {})
                        if _j5:
                            _nw = _j5.get("內外占攻擊", {})
                            _zk = _j5.get("太乙助主客", {})
                            _cd = _j5.get("算長短緩急", {}).get("主算", {})
                            _zd = _j5.get("主客動靜", {})
                            _fx = _j5.get("輔相賢否", {}).get("我國輔相", {})
                            _js = _j5.get("將帥賢否", {}).get("我國將帥", {})
                            st.markdown(
                                f"{t('junshi_vol5')}"
                                f"{_nw.get('斷語', '—')}；"
                                f"{_zk.get('斷語', '')}；"
                                f"主算{_cd.get('長短', '—')}{_cd.get('和否', '')}（{_cd.get('斷語', '')}）；"
                                f"{_zd.get('勝負', '')}")
                            _line5 = []
                            if _fx.get("斷語"):
                                _line5.append(f"輔相{_fx.get('賢否', '')}（{_fx['斷語']}）")
                            if _js.get("斷語"):
                                _line5.append(f"將帥{_js.get('賢否', '')}（{_js['斷語']}）")
                            _sz = _j5.get("數有所主", {}).get("主算", {})
                            if _sz.get("斷語"):
                                _line5.append(f"主算{_sz.get('音')}音（{_sz['斷語']}）")
                            if _line5:
                                st.markdown("；".join(_line5))
                        # —— 州國災變（飛符四殺、城名厄會等）——
                        _v11 = results["ttext"].get("卷十一", {})
                        if _v11:
                            _ff = _v11.get("飛符四殺", {})
                            _zy = _v11.get("州國災變月數", {})
                            _eh = _v11.get("城名厄會", {})
                            _sn = _v11.get("城名歲內災發", {})
                            _bh = _v11.get("十六宮間變化", {})
                            st.markdown(
                                f"{t('vol11')}"
                                f"飛符{_ff.get('飛符', '—')}，"
                                f"災{_ff.get('災殺', '—')}鬼{_ff.get('鬼殺', '—')}；"
                                f"州國災月{_zy.get('斷語', '—')}")
                            _line11 = []
                            if _eh.get("斷語"):
                                _line11.append(f"城名{_eh.get('城名', '')}{_eh['斷語']}")
                            if _sn.get("斷語"):
                                _line11.append(_sn["斷語"])
                            if _ff.get("城名斷語"):
                                _line11.append(_ff["城名斷語"])
                            if _bh.get("加神"):
                                _line11.append(
                                    f"十六神以{_bh['加神']}為樞（{_bh['要訣']}）")
                            if _line11:
                                st.markdown("；".join(_line11))
                        # —— 卷十二：統運入卦 ——
                        _v12 = results["ttext"].get("卷十二", {})
                        if _v12:
                            _rg = _v12.get("統運入卦", {})
                            _hf = _v12.get("入爻禍福", {})
                            _lz = _v12.get("流年直卦", {})
                            _bg = _v12.get("變卦納甲", {})
                            _sw = _v12.get("災厄首尾", {})
                            _yj = _v12.get("要訣", "")
                            _gua_fu = _rg.get("卦符", "")
                            _gua_label = (
                                f"{_rg.get('卦', '—')}{_gua_fu}"
                                if _gua_fu
                                else _rg.get("卦", "—")
                            )
                            st.markdown(
                                f"{t('tongyun_rugua')}"
                                f"{_rg.get('運', '—')}·{_gua_label}{_rg.get('爻名', '')}"
                                f"（入卦第{_rg.get('入卦年數', '—')}年、"
                                f"入爻第{_rg.get('入爻年數', '—')}年）；"
                                f"週期第{_rg.get('週期序', '—')}輪；"
                                f"{t('ruyao_huofu')}"
                                f"{_hf.get('所主', _rg.get('斷語', ''))}")
                            _line12 = []
                            if _lz:
                                _lz_fu = _lz.get("卦符", "")
                                _lz_gua = (
                                    f"{_lz.get('直卦', '—')}{_lz_fu}"
                                    if _lz_fu
                                    else _lz.get("直卦", "—")
                                )
                                _line12.append(
                                    f"{t('liunian_zhigua')}{_lz.get('干支', '')}"
                                    f"{_lz_gua}{_lz.get('爻名', '')}"
                                    f"（{_lz.get('命爻法', '')}）")
                            if _bg:
                                _nj = _bg.get("納甲", {})
                                _line12.append(
                                    f"{t('bian_gua_najia')}"
                                    f"{_bg.get('本卦', '')}→{_bg.get('變卦', '')}"
                                    f"{_bg.get('爻名', '')}；"
                                    f"{_nj.get('納甲', '')}·{_nj.get('方位', '')}")
                            if _sw and _sw.get("是否首尾"):
                                _line12.append(
                                    f"{t('shouwei')}"
                                    f"{'、'.join(_sw.get('首尾標記', []))}；"
                                    f"{_sw.get('斷語', '')}")
                            if _yj:
                                _line12.append(_yj)
                            if _line12:
                                st.markdown("；".join(_line12))
                            _sy = _v12.get("十二運立成", {})
                            _hist = _v12.get("歷史入爻", [])
                            _gqx = _v12.get("觀象期", {})
                            _jz = _v12.get("歲本建子", {})
                            if _sy or _hist or _gqx or _jz:
                                with st.expander(t("tongyun_detail"), expanded=False):
                                    if _sy:
                                        st.markdown(
                                            f"{t('shier_yun')}"
                                            f"大週{_sy.get('大週', '—')}年，"
                                            f"{_sy.get('起運', '')}→{_sy.get('終運', '')}")
                                        if _hf.get("要訣"):
                                            st.caption(_hf["要訣"])
                                        for row in _sy.get("十二運", []):
                                            _guas = "→".join(row.get("卦序", []))
                                            st.markdown(
                                                f"· {row.get('運')}（{row.get('總年')}年）：{_guas}")
                                    if _hist:
                                        st.markdown(t("lishi_ruyao"))
                                        for h in _hist:
                                            st.markdown(
                                                f"· {h.get('紀年', '')}："
                                                f"{h.get('運', '')}·"
                                                f"{h.get('卦', '')}{h.get('爻', '')}")
                                    if _gqx.get("十二月直事"):
                                        st.markdown(f"**{t('tongyun_extended')}**")
                                        st.caption(_gqx.get("要訣", ""))
                                        for m in _gqx["十二月直事"]:
                                            st.markdown(
                                                f"· {m.get('月序')}月（{m.get('月建')}）"
                                                f"{m.get('階段')}·{m.get('卦')}"
                                                f"{m.get('爻名', '')}")
                                    if _jz:
                                        st.caption(
                                            f"{_jz.get('太乙歲本', '')}·"
                                            f"太乙歲{_jz.get('太乙歲', '—')}／"
                                            f"時王歲{_jz.get('時王歲', '—')}")
                        # —— 卷十四：行支編年 ——
                        _v14 = results["ttext"].get("卷十四", {})
                        if _v14:
                            _hz = _v14.get("行支編年", {})
                            _tip14 = _v14.get("要訣", "")
                            _exact = _hz.get("當年例", [])
                            _line14 = [t("hangzhi_biannian")]
                            if _exact:
                                e = _exact[0]
                                _line14.append(
                                    f"{e.get('紀年', '')}·"
                                    f"{e.get('卦', '')}{e.get('爻', '')}："
                                    f"{e.get('摘要', '')}")
                            elif _tip14:
                                _line14.append(_tip14)
                            st.markdown("".join(_line14) if len(_line14) == 1 else "；".join(_line14))
                        # —— 卷十三：統十二運卦象 ——
                        _v13 = results["ttext"].get("卷十三", {})
                        if _v13:
                            _gx = _v13.get("統運卦象", {})
                            _yj13 = _v13.get("要訣", "")
                            _xiang = _gx.get("象曰", "")
                            _yao_gx = _gx.get("當前爻觀象", "")
                            _line13 = [
                                f"{t('gua_xiang')}"
                                f"{_gx.get('運', '—')}·{_gx.get('卦', '—')}"
                                f"{_gx.get('爻名', '')}"
                                f"（經{_gx.get('經年', '—')}年）",
                            ]
                            if _xiang:
                                _line13.append(
                                    f"象曰{_xiang[:48]}{'…' if len(_xiang) > 48 else ''}")
                            if _yao_gx:
                                _line13.append(f"入爻觀象：{_yao_gx[:60]}{'…' if len(_yao_gx) > 60 else ''}")
                            if _yj13:
                                _line13.append(_yj13)
                            st.markdown("；".join(_line13))
                            _full = _v13.get("卦象全文") or {}
                            _zongshu = _gx.get("總述") or _full.get("總述", "")
                            if _zongshu:
                                with st.expander(t("gua_xiang_detail"), expanded=False):
                                    if _full.get("爻觀象"):
                                        st.markdown("**六爻觀象**")
                                        for yi, text in sorted(_full["爻觀象"].items()):
                                            mark = "←" if yi == _gx.get("爻") else ""
                                            st.markdown(f"· 第{yi}爻{text}{mark}")
                                    st.markdown("**卦象總述**")
                                    st.markdown(_zongshu)
                        # —— 卷八：分野疆界 ——
                        _v8 = results["ttext"].get("卷八", {})
                        if _v8:
                            _fy = _v8.get("太乙分野", {})
                            _te = _v8.get("絳宮明堂玉堂", {})
                            _line8 = [
                                f"{t('fenye')}"
                                f"{_fy.get('宮名', '—')}宮·{_fy.get('州', '—')}",
                            ]
                            if _fy.get("城名"):
                                _line8.append(f"城名{_fy['城名']}（{_fy.get('城名干支', '')}）")
                            if _v8.get("歲建分野", {}).get("國"):
                                _sz = _v8["歲建分野"]
                                _line8.append(f"歲建{_sz.get('地支', '')}·{_sz.get('國', '')}分")
                            st.markdown("；".join(_line8))
                        # —— 卷九：大小遊軌運 ——
                        _v9 = results["ttext"].get("卷九", {})
                        if _v9:
                            _dy = _v9.get("大遊軌運", {})
                            _xy = _v9.get("小遊軌運", {})
                            _yj9 = _v9.get("陽九限數", {})
                            _bl9 = _v9.get("百六限數", {})
                            st.markdown(
                                f"{t('guiyun')}"
                                f"大遊{_dy.get('重卦', '—')}{_dy.get('內爻名', '')}"
                                f"（{_dy.get('內卦', '')}/{_dy.get('外卦', '')}）；"
                                f"小遊{_xy.get('重卦', '—')}{_xy.get('內爻名', '')}；"
                                f"落宮{_v9.get('大遊落宮', '—')}/{_v9.get('小遊落宮', '—')}")
                            _line9 = []
                            if _yj9:
                                _line9.append(
                                    f"{t('yangjiu_xian')}"
                                    f"入限{_yj9.get('入限年數', '—')}年")
                            if _bl9:
                                _line9.append(
                                    f"{t('bailiu_xian')}"
                                    f"入限{_bl9.get('入限年數', '—')}年")
                            if _v9.get("要訣"):
                                _line9.append(_v9["要訣"][:80])
                            if _line9:
                                st.markdown("；".join(_line9))
                        # —— 卷十：天目合會 ——
                        _v10 = results["ttext"].get("卷十", {})
                        if _v10:
                            _wq10 = _v10.get("五運六氣", {})
                            _hh = _v10.get("天目合會", [])
                            st.markdown(
                                f"{t('vol10_hehui')}"
                                f"{_wq10.get('五運', '—')}·{_wq10.get('司天', '—')}；"
                                f"{'、'.join(_hh) if _hh else '主客氣調'}")
                        # —— 卷十八：十精雲氣 ——
                        _v18 = results["ttext"].get("卷十八", {})
                        if _v18:
                            _sj = _v18.get("十精數", {})
                            _same = _v18.get("與太乙同宮", [])
                            st.markdown(
                                f"{t('yunqi')}"
                                f"十精數{_sj.get('十精數', '—')}·{_sj.get('斷語', '')}；"
                                f"同宮{'、'.join(_same) if _same else '無'}")
                            if _v18.get("要訣"):
                                st.caption(_v18["要訣"])
                        # —— 卷十五：軍事應用 ——
                        _jy = results["ttext"].get("軍事應用", {})
                        if _jy:
                            _qb = _jy.get("奇兵伏兵", {})
                            _wz = _jy.get("五陣置旗", {})
                            _hz = _wz.get("主陣旗", {})
                            _az = _jy.get("安營置陣", {})
                            _cs = _jy.get("出兵稱神", {}).get("主稱神", {})
                            _cx = _jy.get("陳兵出鄉", {}).get("主", {})
                            _fh = _jy.get("分合用兵", {})
                            _gf = _jy.get("五音觀風察將", {})
                            _js = _jy.get("軍勢勝負", {})
                            st.markdown(
                                f"{t('junshi_vol15')}"
                                f"主奇兵{_qb.get('主奇兵位', '—')}、客奇兵{_qb.get('客奇兵位', '—')}；"
                                f"{_qb.get('伏兵', '')}；"
                                f"主陣{_hz.get('陣型', '—')}{_hz.get('旗色', '')}、"
                                f"出鄉{_cx.get('出鄉', '—')}；"
                                f"{_az.get('斷語', '')}")
                            _line2_parts = []
                            if _cs.get("咒"):
                                _line2_parts.append(
                                    f"稱神{_cs.get('祀方', '')}（{_cs.get('咒', '')}）")
                            if _fh.get("斷語"):
                                _line2_parts.append(f"分合{_fh['斷語']}")
                            if _gf.get("斷語"):
                                _line2_parts.append(f"察將{_gf['斷語']}")
                            if _js.get("斷語"):
                                _line2_parts.append(f"軍勢{_js['斷語']}")
                            if _line2_parts:
                                st.markdown("；".join(_line2_parts))
                        # —— 卷十七：軍事占斷 ——
                        _jz = results["ttext"].get("軍事占斷", {})
                        if _jz:
                            _dd = _jz.get("敵國動靜", {})
                            _jm = _jz.get("間諜虛實", {})
                            _ds = _jz.get("敵使虛實", {})
                            _dl = _jz.get("敵兵來方", {})
                            _cy = _jz.get("出兵用時", {})
                            _jw = _jz.get("見聞虛實", {})
                            _tb = _jz.get("討捕叛亡", {})
                            _zq = _jz.get("執囚對吏", {})
                            _qs = _jz.get("求索所得", {})
                            _sj = _jz.get("時計諸事", {})
                            st.markdown(
                                f"{t('junshi_vol17')}"
                                f"{_dd.get('動靜', '—')}（{_dd.get('斷語', '')}）；"
                                f"間諜{_jm.get('間諜', '—')}；"
                                f"敵使{_ds.get('虛實', '—')}；"
                                f"{_dl.get('方向', '')}{_dl.get('兵勢', '')}；"
                                f"出兵{_cy.get('主方', {}).get('斷語', '')}")
                            if _jw or _tb or _zq or _qs or _sj:
                                _sj_items = "、".join(_sj.get("諸事", [])) if _sj else ""
                                st.markdown(
                                    f"見聞{_jw.get('天目內外', '—')}（{_jw.get('斷語', '')}）；"
                                    f"討捕{_tb.get('結果', '—')}（{'；'.join(_tb.get('得機', []))}）；"
                                    f"執囚{'可解' if _zq.get('可解') else '難解'}（{_zq.get('斷語', '')}）；"
                                    f"求索{'有得' if _qs.get('有得') else '無得'}（{_qs.get('斷語', '')}）；"
                                    f"時計{_sj_items}")
                        # —— 卷二／卷七：神將所主 ——
                        _sj = results["ttext"].get("神將所主", {})
                        if _sj:
                            _16 = _sj.get("十六宮間神", {})
                            _tm = _16.get("天目所臨", {})
                            _9g = _sj.get("九宮所主", {})
                            _jy = _sj.get("陰陽絕易", {})
                            _bm = _sj.get("八門所主", {})
                            _ty = _sj.get("天乙所主", {})
                            _dy = _sj.get("地乙所主", {})
                            _zf = _sj.get("直符所主", {})
                            _fs = _sj.get("四神所主", {})
                            _dyo = _sj.get("大遊所主", {})
                            _xyo = _sj.get("小遊所主", {})
                            _jy_hits = _jy.get("臨宮", [])
                            _jy_txt = (
                                "、".join(h["類型"] for h in _jy_hits if isinstance(h, dict))
                                if _jy_hits and isinstance(_jy_hits[0], dict)
                                else str(_jy_hits[0]) if _jy_hits else "—"
                            )
                            def _god_part(label, block):
                                if not block:
                                    return ""
                                duan = block.get("斷語") or block.get("本象", "")
                                if not duan or str(duan) == "None":
                                    return ""
                                return f"{label}（{duan}）；"

                            _line1 = (
                                f"{t('shenjiang_suozhu')}"
                                f"天目臨{_tm.get('神', '—')}（{_tm.get('所主', '')}）；"
                                f"九宮{_9g.get('太乙落宮', '—')}（{_9g.get('所主', '')}）；"
                                f"絕易{_jy_txt}；"
                                f"值事{_bm.get('值事八門', '—')}門{_bm.get('值事所主', '')}；"
                                f"太乙臨{_bm.get('太乙所臨門', '—')}門（{_bm.get('太乙門吉凶', '')}）；"
                                f"{_god_part('天乙', _ty)}"
                                f"{_god_part('地乙', _dy)}"
                                f"{_god_part('直符', _zf)}"
                                f"{_god_part('四神', _fs)}"
                            ).rstrip("；")
                            st.markdown(_line1)
                            if _dyo or _xyo:
                                _dytm = _dyo.get("大遊天目", {})
                                _xyo_c = _xyo.get("合宮", []) if _xyo else []
                                _xyo_real = [
                                    c for c in _xyo_c
                                    if c and not str(c).startswith("無特殊")
                                ]
                                _xyo_txt = (
                                    "；".join(_xyo_real)
                                    if _xyo_real
                                    else (_xyo.get("本象", "") if _xyo else "")
                                )
                                _dyo_parts = []
                                if _dyo.get("凶筭所主"):
                                    _dyo_parts.append(
                                        f"大遊（{_dyo['凶筭所主']}）")
                                if _dytm.get("本象"):
                                    _dyo_parts.append(f"大遊天目（{_dytm['本象']}）")
                                if _xyo_txt:
                                    _dyo_parts.append(f"小遊（{_xyo_txt}）")
                                if _dyo_parts:
                                    st.markdown("；".join(_dyo_parts))


                    
                    print(f"{config.gendatetime(my, mm, md, mh, mmin)} | {t('acc_prefix')}{config.taiyi_name(results['style'])[0]}{t('acc_suffix')}︰{results['ty'].accnum(results['style'], results['tn'])} | \n"
                          f"{t('lunar_label')}︰{results['lunard']} | {jieqi.jq(my, mm, md, mh, mmin)} |\n"
                          f"{results['gz']} |\n"
                          f"{config.kingyear(my)} |\n"
                          f"{config.ty_method(results['tn'])}{results['ttext'].get('太乙計', '')} - {results['ty'].kook(results['style'], results['tn']).get('文', '')} "
                          f"({results['ttext'].get('局式', {}).get('年', '')}) \n{t('five_yuan')}:{results['wuyuan']} | \n"
                          f"{t('epoch_label')}︰{results['ttext'].get('紀元', '')} | {t('home_calc')}︰{results['homecal']} {t('away_calc')}︰{results['awaycal']} {t('set_calc')}︰{results['setcal']} |")

                # ── 運籌博弈分析區塊 ──────────────────────────────────────
                if st.toggle(t("game_theory_toggle"), key="game_theory_toggle_switch"):
                    with st.spinner(t("game_theory_computing")):
                        try:
                            gt = TaiyiGame(results["ttext"])
                            gt_report = gt.分析報告()
                        except Exception as gt_err:
                            st.error(f"博弈分析錯誤：{gt_err}")
                            gt_report = None
                    if gt_report:
                        with st.expander(t("game_theory_header"), expanded=True):
                            st.markdown(f"**古法推主客相闗：** {gt_report['古法推主客相闗']}")
                            st.markdown(f"**{t('game_theory_winrate')}：** {gt_report['主方勝率判斷']}")
                            st.markdown(f"**{t('game_theory_value')}：** `{gt_report['博弈均衡值']}`")

                            st.markdown(f"##### {t('game_theory_payoff')}")
                            payoff_df = pd.DataFrame(
                                gt_report["支付矩陣"],
                                index=_gt_主方策略列,
                                columns=_gt_客方策略列,
                            ).round(2)
                            st.dataframe(payoff_df)

                            col_h, col_a = st.columns(2)
                            with col_h:
                                st.markdown(f"**{t('game_theory_home_strategy')}**")
                                home_df = pd.DataFrame(
                                    {"策略": _gt_主方策略列, "概率": gt_report["主方均衡策略"]}
                                )
                                st.dataframe(home_df, hide_index=True)
                            with col_a:
                                st.markdown(f"**{t('game_theory_away_strategy')}**")
                                away_df = pd.DataFrame(
                                    {"策略": _gt_客方策略列, "概率": gt_report["客方均衡策略"]}
                                )
                                st.dataframe(away_df, hide_index=True)

                            lp = gt_report["LP最大勝率"]
                            st.markdown(f"##### {t('game_theory_lp')}")
                            st.info(lp["建議文字"])
                            st.markdown(f"**主方最優純策略：** {gt_report['主方最優純策略']}")
                            st.markdown(f"**客方最優純策略：** {gt_report['客方最優純策略']}")

                if st.button(t("ai_analyze_btn"), key="analyze_with_qwen"):
                    with st.spinner(t("ai_analyzing")):
                        _provider = st.session_state.get("ai_provider_selector", "Cerebras")
                        if _provider == "OpenAI":
                            _openai_key = st.session_state.get("openai_api_key_input", "").strip()
                            if not _openai_key:
                                st.error(t("openai_api_key_missing"))
                            else:
                                try:
                                    client = OpenAIClient(api_key=_openai_key)
                                    taiyi_prompt = format_taiyi_results_for_prompt(results)
                                    if st.session_state.get("game_theory_toggle_switch"):
                                        try:
                                            gt_summary = TaiyiGame(results["ttext"]).格局摘要文字()
                                            taiyi_prompt = taiyi_prompt + "\n\n" + gt_summary
                                        except Exception as gt_err:
                                            st.warning(f"博弈摘要生成失敗（不影響AI分析）：{gt_err}")
                                    messages = [
                                        {"role": "system", "content": st.session_state.qwen_system_prompt},
                                        {"role": "user", "content": taiyi_prompt}
                                    ]
                                    api_params = {
                                        "messages": messages,
                                        "model": selected_model,
                                        "max_tokens": st.session_state.get("qwen_max_tokens", 8192),
                                        "temperature": st.session_state.get("qwen_temperature", 0.7)
                                    }
                                    response = client.get_chat_completion(**api_params)
                                    raw_response = response.choices[0].message.content
                                    with st.expander(t("ai_result"), expanded=True):
                                        st.markdown(raw_response)
                                except OpenAITokenQuotaExceededError:
                                    st.error(t("ai_openai_quota_exceeded"))
                                except Exception as e:
                                    st.error(t("ai_error").format(str(e)))
                        elif _provider == "xAI (Grok)":
                            _xai_key = st.session_state.get("xai_api_key_input", "").strip()
                            if not _xai_key:
                                st.error(t("xai_api_key_missing"))
                            else:
                                try:
                                    client = OpenAICompatibleClient(api_key=_xai_key, base_url=XAI_BASE_URL)
                                    taiyi_prompt = format_taiyi_results_for_prompt(results)
                                    if st.session_state.get("game_theory_toggle_switch"):
                                        try:
                                            gt_summary = TaiyiGame(results["ttext"]).格局摘要文字()
                                            taiyi_prompt = taiyi_prompt + "\n\n" + gt_summary
                                        except Exception as gt_err:
                                            st.warning(f"博弈摘要生成失敗（不影響AI分析）：{gt_err}")
                                    messages = [
                                        {"role": "system", "content": st.session_state.qwen_system_prompt},
                                        {"role": "user", "content": taiyi_prompt}
                                    ]
                                    api_params = {
                                        "messages": messages,
                                        "model": selected_model,
                                        "max_tokens": st.session_state.get("qwen_max_tokens", 8192),
                                        "temperature": st.session_state.get("qwen_temperature", 0.7)
                                    }
                                    response = client.get_chat_completion(**api_params)
                                    raw_response = response.choices[0].message.content
                                    with st.expander(t("ai_result"), expanded=True):
                                        st.markdown(raw_response)
                                except CompatibleTokenQuotaExceededError:
                                    st.error(t("ai_xai_quota_exceeded"))
                                except Exception as e:
                                    st.error(t("ai_error").format(str(e)))
                        elif _provider == "DeepSeek":
                            _deepseek_key = st.session_state.get("deepseek_api_key_input", "").strip()
                            if not _deepseek_key:
                                st.error(t("deepseek_api_key_missing"))
                            else:
                                try:
                                    client = OpenAICompatibleClient(api_key=_deepseek_key, base_url=DEEPSEEK_BASE_URL)
                                    taiyi_prompt = format_taiyi_results_for_prompt(results)
                                    if st.session_state.get("game_theory_toggle_switch"):
                                        try:
                                            gt_summary = TaiyiGame(results["ttext"]).格局摘要文字()
                                            taiyi_prompt = taiyi_prompt + "\n\n" + gt_summary
                                        except Exception as gt_err:
                                            st.warning(f"博弈摘要生成失敗（不影響AI分析）：{gt_err}")
                                    messages = [
                                        {"role": "system", "content": st.session_state.qwen_system_prompt},
                                        {"role": "user", "content": taiyi_prompt}
                                    ]
                                    api_params = {
                                        "messages": messages,
                                        "model": selected_model,
                                        "max_tokens": st.session_state.get("qwen_max_tokens", 8192),
                                        "temperature": st.session_state.get("qwen_temperature", 0.7)
                                    }
                                    response = client.get_chat_completion(**api_params)
                                    raw_response = response.choices[0].message.content
                                    with st.expander(t("ai_result"), expanded=True):
                                        st.markdown(raw_response)
                                except CompatibleTokenQuotaExceededError:
                                    st.error(t("ai_deepseek_quota_exceeded"))
                                except Exception as e:
                                    st.error(t("ai_error").format(str(e)))
                        elif _provider == "Qwen":
                            _qwen_key = st.session_state.get("qwen_api_key_input", "").strip()
                            if not _qwen_key:
                                st.error(t("qwen_api_key_missing"))
                            else:
                                try:
                                    client = OpenAICompatibleClient(api_key=_qwen_key, base_url=QWEN_BASE_URL)
                                    taiyi_prompt = format_taiyi_results_for_prompt(results)
                                    if st.session_state.get("game_theory_toggle_switch"):
                                        try:
                                            gt_summary = TaiyiGame(results["ttext"]).格局摘要文字()
                                            taiyi_prompt = taiyi_prompt + "\n\n" + gt_summary
                                        except Exception as gt_err:
                                            st.warning(f"博弈摘要生成失敗（不影響AI分析）：{gt_err}")
                                    messages = [
                                        {"role": "system", "content": st.session_state.qwen_system_prompt},
                                        {"role": "user", "content": taiyi_prompt}
                                    ]
                                    api_params = {
                                        "messages": messages,
                                        "model": selected_model,
                                        "max_tokens": st.session_state.get("qwen_max_tokens", 8192),
                                        "temperature": st.session_state.get("qwen_temperature", 0.7)
                                    }
                                    response = client.get_chat_completion(**api_params)
                                    raw_response = response.choices[0].message.content
                                    with st.expander(t("ai_result"), expanded=True):
                                        st.markdown(raw_response)
                                except CompatibleTokenQuotaExceededError:
                                    st.error(t("ai_qwen_quota_exceeded"))
                                except Exception as e:
                                    st.error(t("ai_error").format(str(e)))
                        elif _provider == "自定義":
                            _ckey = st.session_state.get("custom_provider_api_key", "").strip()
                            _chost = st.session_state.get("custom_provider_api_host", "").strip()
                            _cpath = st.session_state.get("custom_provider_api_path", "").strip()
                            _ccompat = st.session_state.get("custom_provider_network_compat", False)
                            _cmodel = st.session_state.get("custom_model_selector") or st.session_state.get("custom_model_direct_input", "") or selected_model
                            if not _ckey:
                                st.error(t("custom_provider_api_key_missing"))
                            elif not _chost:
                                st.error(t("custom_provider_host_missing"))
                            elif not _cmodel:
                                st.error(t("custom_provider_no_models"))
                            else:
                                _proto = "http" if _ccompat else "https"
                                _base_url = f"{_proto}://{_chost}{_cpath}"
                                try:
                                    client = OpenAICompatibleClient(api_key=_ckey, base_url=_base_url)
                                    taiyi_prompt = format_taiyi_results_for_prompt(results)
                                    if st.session_state.get("game_theory_toggle_switch"):
                                        try:
                                            gt_summary = TaiyiGame(results["ttext"]).格局摘要文字()
                                            taiyi_prompt = taiyi_prompt + "\n\n" + gt_summary
                                        except Exception as gt_err:
                                            st.warning(f"博弈摘要生成失敗（不影響AI分析）：{gt_err}")
                                    messages = [
                                        {"role": "system", "content": st.session_state.qwen_system_prompt},
                                        {"role": "user", "content": taiyi_prompt}
                                    ]
                                    api_params = {
                                        "messages": messages,
                                        "model": _cmodel,
                                        "max_tokens": st.session_state.get("qwen_max_tokens", 8192),
                                        "temperature": st.session_state.get("qwen_temperature", 0.7)
                                    }
                                    response = client.get_chat_completion(**api_params)
                                    raw_response = response.choices[0].message.content
                                    with st.expander(t("ai_result"), expanded=True):
                                        st.markdown(raw_response)
                                except CompatibleTokenQuotaExceededError:
                                    st.error(t("ai_custom_quota_exceeded"))
                                except Exception as e:
                                    st.error(t("ai_error").format(str(e)))
                        else:
                            cerebras_api_key = st.secrets.get("CEREBRAS_API_KEY") or os.getenv("CEREBRAS_API_KEY")
                            if not cerebras_api_key:
                                st.error(t("ai_key_missing"))
                            else:
                                try:
                                    client = CerebrasClient(api_key=cerebras_api_key)
                                    taiyi_prompt = format_taiyi_results_for_prompt(results)
                                    # 若博弈分析已啟用，附加博弈摘要到提示詞
                                    if st.session_state.get("game_theory_toggle_switch"):
                                        try:
                                            gt_summary = TaiyiGame(results["ttext"]).格局摘要文字()
                                            taiyi_prompt = taiyi_prompt + "\n\n" + gt_summary
                                        except Exception as gt_err:
                                            st.warning(f"博弈摘要生成失敗（不影響AI分析）：{gt_err}")
                                    messages = [
                                        {"role": "system", "content": st.session_state.qwen_system_prompt},
                                        {"role": "user", "content": taiyi_prompt}
                                    ]
                                    api_params = {
                                        "messages": messages,
                                        "model": selected_model,
                                        "max_tokens": st.session_state.get("qwen_max_tokens", 8192),
                                        "temperature": st.session_state.get("qwen_temperature", 0.7)
                                    }
                                    response = client.get_chat_completion(**api_params)
                                    raw_response = response.choices[0].message.content
                                    with st.expander(t("ai_result"), expanded=True):
                                        st.markdown(raw_response)
                                except TokenQuotaExceededError:
                                    st.error(t("ai_quota_exceeded"))
                                except Exception as e:
                                    st.error(t("ai_error").format(str(e)))
        except Exception as e:
            st.error(t("gen_error").format(str(e)))

# 使用說明
with tabs[1]:
    st.markdown(get_file_content_as_string(BASE_URL_KINTAIYI, "docs/instruction.md"))

# 太乙局數史例
with tabs[2]:
    with open(os.path.join(_REPO_ROOT, "assets", "example.json"), "r", encoding="utf-8-sig") as f:
        data = f.read()
    timeline(data, height=600)
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
    st.markdown(render_changelog_html(_update_md), unsafe_allow_html=True)

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
st.markdown(f"### {t('chat_header')}")

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
