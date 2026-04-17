import os
import sys

# Resolve the repository root (one level up from apps/) so that relative paths
# to assets/ and src/ work regardless of the working directory.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Ensure the src directory is on the Python path so that the kintaiyi package
# can be imported when running from the repository root (e.g. on Streamlit Cloud).
sys.path.insert(0, os.path.join(_REPO_ROOT, "src"))

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
import cn2an
from cn2an import an2cn
from kintaiyi.taiyidict import tengan_shiji, su_dist
from kintaiyi.taiyimishu import taiyi_yingyang
from kintaiyi.historytext import chistory
import streamlit.components.v1 as components
from streamlit.components.v1 import html
import pandas as pd
from kintaiyi.cerebras_client import CerebrasClient, DEFAULT_MODEL as DEFAULT_CEREBRAS_MODEL, TokenQuotaExceededError
from kintaiyi.game_theory import TaiyiGame, 主方策略列 as _gt_主方策略列, 客方策略列 as _gt_客方策略列

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
        "instant_btn": "即時盤",
        "ai_settings": "AI設置",
        "ai_model": "AI 模型",
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
        # AI
        "ai_analyze_btn": "🔍 使用AI分析排盤結果",
        "ai_analyzing": "AI正在分析太乙排盤結果...",
        "ai_key_missing": "CEREBRAS_API_KEY 未設置，請在 .streamlit/secrets.toml 或環境變量中設置。",
        "ai_error": "調用AI時發生錯誤：{}",
        "ai_quota_exceeded": "⚠️ Cerebras API 每日 Token 配額已用盡，請稍後再試或降低「最大生成 Tokens」設定。",
        "gen_error": "生成盤局時發生錯誤：{}",
        "ai_result": "AI分析結果",
        "list_label": "列表",
        "save_error": "錯誤儲存提示：{}",
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
        "instant_btn": "Instant Chart",
        "ai_settings": "AI Settings",
        "ai_model": "AI Model",
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
        # AI
        "ai_analyze_btn": "🔍 Analyze with AI",
        "ai_analyzing": "AI is analyzing the Taiyi chart...",
        "ai_key_missing": "CEREBRAS_API_KEY not set. Please set it in .streamlit/secrets.toml or environment variables.",
        "ai_error": "Error calling AI: {}",
        "ai_quota_exceeded": "⚠️ Cerebras API daily token quota exceeded. Please try again later or reduce the 'Max Generation Tokens' setting.",
        "gen_error": "Error generating chart: {}",
        "ai_result": "AI Analysis Result",
        "list_label": "List",
        "save_error": "Error saving prompt: {}",
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
CEREBRAS_MODEL_OPTIONS = [
    "gpt-oss-120b",
    "llama3.1-8b",
    "zai-glm-4.7",
    "qwen-3-235b-a22b-instruct-2507",
]
CEREBRAS_MODEL_DESCRIPTIONS = {
    "gpt-oss-120b": "Cerebras: High-capacity open-source model for complex tasks.",
    "llama3.1-8b": "Cerebras: Light and fast for quick tasks.",
    "zai-glm-4.7": "Cerebras: GLM-based model for versatile analysis.",
    "qwen-3-235b-a22b-instruct-2507": "Cerebras: Fast inference, great for rapid iteration.",
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
        with open(SYSTEM_PROMPTS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        default_data = {
            "prompts": [
                {
                    "name": "太乙大師",
                    "content": DEFAULT_SYSTEM_PROMPT
                }
            ],
            "selected": "太乙大師"
        }
        with open(SYSTEM_PROMPTS_FILE, "w") as f:
            json.dump(default_data, f, indent=2)
        return default_data

def save_system_prompts(prompts_data):
    SYSTEM_PROMPTS_FILE = os.path.join(_REPO_ROOT, "assets", "system_prompts.json")
    try:
        with open(SYSTEM_PROMPTS_FILE, "w") as f:
            json.dump(prompts_data, f, indent=2)
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
    if results["style"] == 5:  # 太乙命法
        prompt_lines.extend([
            f"命法性別: {results['zhao']} ({results['sex_o']})",
            f"十二宮分析: {results['lifedisc']}",
            f"太乙十六神落宮: {results['lifedisc2']}",
        ])
    return "\n\n".join(prompt_lines)

def render_svg(svg, num):
    """渲染交互式 SVG 圖表，針對 id='layer4' 和 id='layer6' 的 <g> 標籤進行順時針或逆時針旋轉，支援按住滑鼠旋轉並移除殘影"""
    if not svg or 'svg' not in svg.lower():
        st.error("Invalid SVG content provided")
        return
    
    js_code = """
    const rotations = { "layer4": 0, "layer6": 0 };

    function rotateLayer(layer, deltaAngle) {
      if (!layer || !layer.getAttribute) {
        console.error("層元素無效");
        return;
      }
      const id = layer.getAttribute('id');
      if (!id || rotations[id] === undefined) {
        console.error(`未找到 ${id} 的旋轉數據`);
        return;
      }
      rotations[id] += deltaAngle;
      const newRotation = rotations[id] % 360;
      console.log(`計算 newRotation 為 ${id}: ${newRotation}, 累計旋轉: ${rotations[id]}`);

      const bbox = layer.getBBox();
      const centerX = bbox.x + bbox.width / 2;
      const centerY = bbox.y + bbox.height / 2;
      const transformValue = "rotate(" + newRotation + " " + centerX + " " + centerY + ")";
      layer.setAttribute("transform", transformValue);

      layer.querySelectorAll("text").forEach(text => {
        if (!text || !text.getAttribute) return;
        const x = parseFloat(text.getAttribute("x") || 0);
        const y = parseFloat(text.getAttribute("y") || 0);
        if (isNaN(x) || isNaN(y)) return;
        const textTransform = "rotate(" + (-newRotation) + " " + x + " " + y + ")";
        text.setAttribute("transform", textTransform);
      });
      console.log(`旋轉 ${id} 至 ${newRotation}°，中心 (${centerX}, ${centerY})`);
    }

    function setupEventListeners() {
      ["layer4", "layer6"].forEach(id => {
        const layer = document.querySelector("#" + id);
        if (layer) {
          layer.style.pointerEvents = "all";
          layer.style.cursor = "pointer";

          let isRotating = false;
          let startX = 0;

          layer.addEventListener("mousedown", (event) => {
            event.preventDefault();
            event.stopPropagation();
            isRotating = true;
            startX = event.clientX;
            const bbox = layer.getBBox();
            console.log(`mousedown on ${id}, startX: ${startX}, clientX: ${event.clientX}, clientY: ${event.clientY}, bbox:`, bbox);
          });

          layer.addEventListener("mousemove", (event) => {
            if (isRotating) {
              event.preventDefault();
              event.stopPropagation();
              const deltaX = event.clientX - startX;
              const deltaAngle = deltaX * 1.0;
              rotateLayer(layer, deltaAngle);
              startX = event.clientX;
              console.log(`mousemove on ${id}, deltaX: ${deltaX}, deltaAngle: ${deltaAngle}`);
            }
          });

          layer.addEventListener("mouseup", (event) => {
            event.preventDefault();
            event.stopPropagation();
            isRotating = false;
            console.log(`mouseup on ${id}`);
          });

          layer.addEventListener("mouseleave", () => {
            isRotating = false;
            console.log(`mouseleave on ${id}`);
          });

          layer.addEventListener("click", (event) => {
            if (!isRotating) {
              event.preventDefault();
              event.stopPropagation();
              const direction = Math.random() < 0.5 ? 30 : -30;
              rotateLayer(layer, direction);
              console.log(`click on ${id}, direction: ${direction}°`);
            }
          });
          console.log(`事件監聽器已為 ${id} 添加, layer found:`, layer);
        } else {
          console.error(`未找到 id='${id}' 的 <g> 元素`);
        }
      });
    }

    requestAnimationFrame(() => {
      setupEventListeners();
      console.log("SVG 渲染完成，事件監聽器已設置");
    });

    window.addEventListener("load", () => {
      console.log("SVG 已完全載入");
      ["layer4", "layer6"].forEach(id => {
        const layer = document.querySelector("#" + id);
        if (layer) console.log(`找到 ${id}，準備旋轉`);
        else console.error(`載入後仍未找到 ${id}`);
      });
    });
    """

    html_content = f"""
    <div style="margin: 0; padding: 0;">
      <svg id="interactive-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {num} {num}" width="100%" height="auto" style="max-height: 400px; display: block; margin: 0 auto;">
        {svg}
      </svg>
      <script>
        {js_code}
      </script>
    </div>
    <style>
        #interactive-svg {{
            margin-top: 10px;
            margin-bottom: 10px;
            user-select: none;
            -webkit-user-select: none;
            -moz-user-select: none;
            -ms-user-select: none;
            outline: none;
            -webkit-tap-highlight-color: transparent;
            touch-action: none;
        }}
        #interactive-svg * {{
            user-select: none;
            -webkit-user-select: none;
            -moz-user-select: none;
            -ms-user-select: none;
            outline: none;
        }}
        .stCodeBlock {{
            margin-bottom: 10px !important;
        }}
    </style>
    """
    html(html_content, height=num)
    
def render_svg1(svg, num):
    """渲染靜態 SVG 圖表（可點擊同時著色第二、三、四層的十六分之一部分）"""
    if not svg or 'svg' not in svg.lower():
        st.error("Invalid SVG content provided")
        return
    
    js_script = """
    <script>
        const coloredGroups = new Set();
        let currentColors = [];

        function getRandomColor() {
            const letters = '0123456789ABCDEF';
            let color = '#';
            for (let i = 0; i < 6; i++) {
                color += letters[Math.floor(Math.random() * 16)];
            }
            return color;
        }

        function generateFourColors() {
            let colors = [];
            for (let i = 0; i < 4; i++) {
                let newColor = getRandomColor();
                while (colors.includes(newColor)) {
                    newColor = getRandomColor();
                }
                colors.push(newColor);
            }
            return colors;
        }

        const allGroups = document.querySelectorAll('#static-svg g');
        const targetLayers = [];
        allGroups.forEach((group, groupIndex) => {
            const segments = group.querySelectorAll('path, polygon, rect');
            if (segments.length > 0) {
                targetLayers.push({ group: group, index: groupIndex, segments: Array.from(segments) });
            }
        });

        console.log('Found ' + targetLayers.length + ' layers with segments:', targetLayers.map(l => ({ index: l.index, segmentCount: l.segments.length })));

        if (targetLayers.length >= 4) {
            const layersToColor = [targetLayers[1], targetLayers[2], targetLayers[3]];

            layersToColor.forEach((layer, layerNum) => {
                layer.segments.forEach((segment, index) => {
                    segment.style.cursor = 'pointer';
                    segment.style.pointerEvents = 'all';
                    segment.style.zIndex = '10';
                    segment.setAttribute('data-index', index);
                    segment.setAttribute('data-layer', layerNum);
                    segment.addEventListener('click', function(event) {
                        event.stopPropagation();
                        const segmentIndex = parseInt(segment.getAttribute('data-index'));
                        const groupId = `group_${segmentIndex}`;

                        console.log(`Clicked segment in layer ${parseInt(segment.getAttribute('data-layer')) + 2}, index: ${segmentIndex}`);

                        const isColored = coloredGroups.has(groupId);

                        if (isColored) {
                            layersToColor.forEach(l => {
                                if (l.segments[segmentIndex]) {
                                    l.segments[segmentIndex].removeAttribute('fill');
                                }
                            });
                            coloredGroups.delete(groupId);
                        } else if (coloredGroups.size < 4) {
                            if (coloredGroups.size === 0 || currentColors.length === 0) {
                                currentColors = generateFourColors();
                                console.log('Generated new colors:', currentColors);
                            }
                            const colorToUse = currentColors[coloredGroups.size];
                            layersToColor.forEach(l => {
                                if (l.segments[segmentIndex]) {
                                    l.segments[segmentIndex].setAttribute('fill', colorToUse);
                                }
                            });
                            coloredGroups.add(groupId);
                            if (coloredGroups.size === 4) {
                                currentColors = [];
                            }
                        }
                    });
                });
            });
        } else {
            console.error('Not enough layers found. Found only ' + targetLayers.length + ' layers.');
        }
    </script>
    """

    html_content = f"""
    <div style="margin: 0; padding: 0;">
      <svg id="static-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {num} {num}" width="100%" height="auto" style="max-height: 400px; display: block; margin: 0 auto;">
        {svg}
      </svg>
      {js_script}
    </div>
    <style>
        #static-svg {{ 
            margin-top: 10px;
            margin-bottom: 10px;
        }}
        #static-svg path, #static-svg polygon, #static-svg rect {{
            pointer-events: all !important;
            z-index: 10 !important;
        }}
        .stCodeBlock {{
            margin-bottom: 10px !important;
        }}
    </style>
    """
    html(html_content, height=num)

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
    
    option = st.selectbox(t("chart_method"), ('時計太乙', '年計太乙', '月計太乙', '日計太乙', '分計太乙', '太乙命法'), format_func=to)
    acum = st.selectbox(t("acc_years"), ('太乙統宗', '太乙金鏡', '太乙淘金歌', '太乙局'), format_func=to)
    ten_ching = st.selectbox(t("ten_essences"), ('無', '有'), format_func=to)
    sex_o = st.selectbox(t("life_gender"), ('男', '女'), format_func=to)
    rotation = st.selectbox(t("rotation_label"), ('固定', '轉動'), format_func=to)
    
    num_dict = {'時計太乙': 3, '年計太乙': 0, '月計太乙': 1, '日計太乙': 2, '分計太乙': 4, '太乙命法': 5}
    style = num_dict[option]
    tn_dict = {'太乙統宗': 0, '太乙金鏡': 1, '太乙淘金歌': 2, '太乙局': 3}
    tn = tn_dict[acum]
    tc_dict = {'有': 1, '無': 0}
    tc = tc_dict[ten_ching]
    
    instant = st.button(t("instant_btn"), use_container_width=True)
    
    st.markdown("---")
    st.header(t("ai_settings"))
    
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
    if style != 5:
        ttext = ty.pan(style, tn)
        kook = ty.kook(style, tn)
        sj_su_predict = f"始擊落{ty.sf_num(style, tn)}宿，{su_dist.get(ty.sf_num(style, tn))}"
        tg_sj_su_predict = config.multi_key_dict_get(tengan_shiji, config.gangzhi(my, mm, md, mh, mmin)[0][0]).get(config.Ganzhiwuxing(ty.sf(style, tn)))
        three_door = ty.threedoors(style, tn)
        five_generals = ty.fivegenerals(style, tn)
        home_vs_away1 = ty.wc_n_sj(style, tn)
        genchart2 = ty.gen_gong(style, tn, tc)
    if style == 5:
        tn = 0
        ttext = ty.pan(3, 0)
        kook = ty.kook(3, 0)
        sj_su_predict = f"始擊落{ty.sf_num(3, 0)}宿，{su_dist.get(ty.sf_num(3, 0))}"
        tg_sj_su_predict = config.multi_key_dict_get(tengan_shiji, config.gangzhi(my, mm, md, mh, mmin)[0][0]).get(config.Ganzhiwuxing(ty.sf(3, 0)))
        three_door = ty.threedoors(3, 0)
        five_generals = ty.fivegenerals(3, 0)
        home_vs_away1 = ty.wc_n_sj(3, 0)
        genchart2 = ty.gen_gong(3, tn, tc)
    genchart1 = ty.gen_life_gong(sex_o)
    kook_num = kook.get("數")
    yingyang = kook.get("文")[0]
    wuyuan = ty.get_five_yuan_kook(style, tn) if style != 5 else ""
    homecal, awaycal, setcal = config.find_cal(yingyang, kook_num)
    zhao = {"男": "乾造", "女": "坤造"}.get(sex_o)
    life1 = ty.gongs_discription(sex_o)
    life2 = ty.twostar_disc(sex_o)
    lifedisc = ty.convert_gongs_text(life1, life2)
    lifedisc2 = ty.stars_descriptions_text(3, 0)
    lifedisc3 = ty.sixteen_gong_grades(3,0)
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
                if results["style"] == 5:
                    try:
                        start_pt = results["genchart1"][results["genchart1"].index('''viewBox="''')+22:].split(" ")[1]
                        if rotation == "轉動":
                            render_svg(results["genchart1"], int(start_pt))
                        else:
                            render_svg1(results["genchart1"], int(start_pt))
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
                        if rotation == "轉動":
                            render_svg(results["genchart2"], int(start_pt2))
                        else:
                            render_svg1(results["genchart2"], int(start_pt2))
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
    with open(os.path.join(_REPO_ROOT, "assets", "example.json"), "r") as f:
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
    st.markdown(get_file_content_as_string(BASE_URL_KINTAIYI, "docs/update.md"))

# 看盤要領
with tabs[6]:
    st.markdown(get_file_content_as_string(BASE_URL_KINTAIYI, "docs/tutorial.md"), unsafe_allow_html=True)

# 連結
with tabs[7]:
    st.markdown(get_file_content_as_string(BASE_URL_KINLIUREN, "docs/contact.md"), unsafe_allow_html=True)

# Custom CSS (aligned with chat_main.py styling)
st.markdown(
    """
    <style>
    /* General chat message container styling */
    [data-testid="stChatMessage"] { 
        margin-bottom: 10px !important;
    }

    /* User message styling */
    html[data-theme="light"] [data-testid="stChatMessage"]:has(div[data-testid="stChatMessageContent"][data-test-id="stChatMessageContent-user"]) [data-testid="stChatMessageContent"],
    [data-testid="stChatMessage"]:has(div[data-testid="stChatMessageContent"][data-test-id="stChatMessageContent-user"]) [data-testid="stChatMessageContent"] {
        background-color: #e6f2ff !important;
        border-radius: 10px !important;
        padding: 10px !important;
    }
    html[data-theme="dark"] [data-testid="stChatMessage"]:has(div[data-testid="stChatMessageContent"][data-test-id="stChatMessageContent-user"]) [data-testid="stChatMessageContent"] {
        background-color: #2a3950 !important;
        border-radius: 10px !important;
        padding: 10px !important;
        color: #e0e0e0 !important;
    }

    /* Assistant message styling */
    html[data-theme="light"] [data-testid="stChatMessage"]:has(div[data-testid="stChatMessageContent"][data-test-id="stChatMessageContent-assistant"]) [data-testid="stChatMessageContent"],
    [data-testid="stChatMessage"]:has(div[data-testid="stChatMessageContent"][data-test-id="stChatMessageContent-assistant"]) [data-testid="stChatMessageContent"] {
        background-color: #f5f5f5 !important;
        border-radius: 10px !important;
        padding: 10px !important;
    }
    html[data-theme="dark"] [data-testid="stChatMessage"]:has(div[data-testid="stChatMessageContent"][data-test-id="stChatMessageContent-assistant"]) [data-testid="stChatMessageContent"] {
        background-color: #262730 !important;
        border-radius: 10px !important;
        padding: 10px !important;
        color: #d1d1d1 !important;
    }

    .stMarkdown [data-testid="stMarkdownContainer"] {
        white-space: pre-wrap !important;
    }

    .stExpander {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        margin-top: 5px;
        margin-bottom: 10px;
    }
    html[data-theme="dark"] .stExpander {
        border: 1px solid #3d3d3d;
    }

    input[type="text"], textarea {
        border-radius: 6px;
        border: 1px solid #ced4da;
    }
    html[data-theme="dark"] input[type="text"], 
    html[data-theme="dark"] textarea {
        border: 1px solid #4d5154;
    }
    
    .stButton button {
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.15s ease-in-out;
    }
    
    .stButton button {
        background-color: #4e7496;
        color: white;
    }
    .stButton button:hover:enabled {
        background-color: #3a5a78;
        transform: translateY(-1px);
    }
    
    button[kind="error"], button[data-testid="baseButton-secondary"] {
        background-color: #6c757d;
    }
    
    .stExpander [data-testid="stExpanderDetails"] {
        padding: 10px;
    }
    
    .thinking-content {
        background-color: #f8f9fa;
        border-left: 4px solid #007bff;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
        max-height: 400px;
        overflow-y: auto;
        color: #333;
    }
    
    html[data-theme="dark"] .thinking-content {
        background-color: #2c2c2c;
        border-left: 4px solid #4dabf7;
        color: #e0e0e0;
    }
    </style>
    """,
    unsafe_allow_html=True
)
