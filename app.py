import streamlit as st
import datetime
import pytz
from contextlib import contextmanager, redirect_stdout
from io import StringIO
import urllib.request
import json
import jieqi
import kintaiyi
import config
import cn2an
from cn2an import an2cn
from taiyidict import tengan_shiji, su_dist
from taiyimishu import taiyi_yingyang
from historytext import chistory
import streamlit.components.v1 as components
from streamlit.components.v1 import html
from cerebras_client import CerebrasClient, DEFAULT_MODEL as DEFAULT_CEREBRAS_MODEL
import os
import logging

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Cerebras Model Options
CEREBRAS_MODEL_OPTIONS = [
    "qwen-3-32b",
    "llama-4-scout-17b-16e-instruct",
    "llama3.1-8b",
    "llama-3.3-70b"
]
CEREBRAS_MODEL_DESCRIPTIONS = {
    "qwen-3-32b": "Cerebras: Fast inference, great for rapid iteration.",
    "llama-4-scout-17b-16e-instruct": "Cerebras: Optimized for guided workflows.",
    "llama3.1-8b": "Cerebras: Light and fast for quick tasks.",
    "llama-3.3-70b": "Cerebras: Most capable for complex reasoning."
}

# System Prompt Management Functions
def load_system_prompts():
    SYSTEM_PROMPTS_FILE = "system_prompts.json"
    DEFAULT_SYSTEM_PROMPT = (
        "你是一位太乙神數大師，熟悉《太乙秘書》和歷史案例。請根據提供的太乙排盤數據，進行以下操作：\n"
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
                    "name": "太乙分析專家",
                    "content": DEFAULT_SYSTEM_PROMPT
                }
            ],
            "selected": "太乙分析專家"
        }
        with open(SYSTEM_PROMPTS_FILE, "w") as f:
            json.dump(default_data, f, indent=2)
        return default_data

def save_system_prompts(prompts_data):
    SYSTEM_PROMPTS_FILE = "system_prompts.json"
    try:
        with open(SYSTEM_PROMPTS_FILE, "w") as f:
            json.dump(prompts_data, f, indent=2)
        return True
    except Exception as e:
        st.error(f"錯誤儲存提示：{e}")
        return False

# Initialize session state to control rendering
if 'render_default' not in st.session_state:
    st.session_state.render_default = True

@st.cache_data
def get_file_content_as_string(base_url, path):
    """從指定 URL 獲取文件內容並返回字符串"""
    url = base_url + path
    response = urllib.request.urlopen(url)
    return response.read().decode("utf-8")

def format_text(d, parent_key=""):
    """格式化字典為可讀的文本"""
    if d is None:
        return "無數據"
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
    """Format Taiyi calculation results into a prompt for the qwen-3-32b model."""
    try:
        logger.debug("Formatting Taiyi results: %s", json.dumps(results, default=str, ensure_ascii=False))
        ttext = results.get('ttext', {}) or {}
        if not isinstance(ttext, dict):
            logger.warning("ttext is not a dictionary: %s", ttext)
            ttext = {}
        
        prompt_lines = [
            "以下是太乙排盤的計算結果，請根據這些數據提供詳細的分析和解釋：",
            f"日期時間: {results.get('gz', '未知')} (農曆: {results.get('lunard', '未知')})",
            f"紀元: {ttext.get('紀元', '無')}",
            f"局式: {ttext.get('局式', {}).get('年', '無')}",
            f"太乙計: {config.ty_method(results.get('tn', 0))}{ttext.get('太乙計', '')}",
            f"文: {results.get('kook', {}).get('文', '無')}",
            f"數: {results.get('kook_num', '無')}",
            f"主筭: {results.get('homecal', '無')}, 客筭: {results.get('awaycal', '無')}, 定筭: {results.get('setcal', '無')}",
            f"始擊值宿: {results.get('sj_su_predict', '無')}",
            f"十天干歲始擊落宮: {results.get('tg_sj_su_predict', '無')}",
            f"太歲值宿: {results.get('year_predict', '無')}",
            f"三門五將: {results.get('three_door', '無')} {results.get('five_generals', '無')}",
            f"推太乙在天外地內法: {results.get('ty', None).ty_gong_dist(results.get('style', 0), results.get('tn', 0)) if results.get('ty') else '無'}",
            f"推少多以占勝負: {ttext.get('推少多以占勝負', '無')}",
            f"推太乙風雲飛鳥助戰: {results.get('home_vs_away3', '無')}",
            f"《太乙秘書》: {results.get('ts', '無')}",
            f"史事記載: {results.get('ch', '無')}",
        ]
        if results.get("style") == 5:  # 太乙命法
            prompt_lines.extend([
                f"命法性別: {results.get('zhao', '無')} ({results.get('sex_o', '無')})",
                f"十二宮分析: {results.get('lifedisc', '無')}",
                f"太乙十六神落宮: {results.get('lifedisc2', '無')}",
                f"陽九行限: {format_text(results.get('yjxx', {}))}",
                f"百六行限: {format_text(results.get('blxx', {}))}",
                f"值卦: 年卦 {results.get('ygua', '無')}, 月卦 {results.get('mgua', '無')}, 日卦 {results.get('dgua', '無')}, 時卦 {results.get('hgua', '無')}, 分卦 {results.get('mingua', '無')}",
            ])
        formatted_prompt = "\n\n".join([line for line in prompt_lines if line])
        logger.debug("Formatted prompt: %s", formatted_prompt)
        return formatted_prompt
    except Exception as e:
        logger.error("Error formatting Taiyi results: %s", str(e), exc_info=True)
        raise ValueError(f"無法格式化太乙結果：{str(e)}")

def render_svg(svg, num):
    """渲染交互式 SVG 圖表，針對 id='layer4' 和 id='layer6' 的 <g> 標籤進行順時針或逆時針旋轉，支援按住滑鼠旋轉並移除殞地影像"""
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

        function generateTwoColors() {
            let color1 = getRandomColor();
            let color2 = getRandomColor();
            while (color1 === color2) {
                color2 = getRandomColor();
            }
            return [color1, color2];
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
                        } else if (coloredGroups.size < 2) {
                            if (coloredGroups.size === 0 || currentColors.length === 0) {
                                currentColors = generateTwoColors();
                                console.log('Generated new colors:', currentColors);
                            }
                            const colorToUse = currentColors[coloredGroups.size];
                            layersToColor.forEach(l => {
                                if (l.segments[segmentIndex]) {
                                    l.segments[segmentIndex].setAttribute('fill', colorToUse);
                                }
                            });
                            coloredGroups.add(groupId);
                            if (coloredGroups.size === 2) {
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

# Streamlit 頁面配置
st.set_page_config(layout="wide", page_title="堅太乙 - 太乙排盤")

# 定義基礎 URL
BASE_URL_KINTAIYI = 'https://raw.githubusercontent.com/kentang2017/kintaiyi/master/'
BASE_URL_KINLIUREN = 'https://raw.githubusercontent.com/kentang2017/kinliuren/master/'

# 側邊欄輸入
with st.sidebar:
    st.header("排盤參數設置")
    
    now = datetime.datetime.now(pytz.timezone('Asia/Hong_Kong'))
    col1, col2 = st.columns(2)
    with col1:
        my = st.number_input('年', min_value=0, max_value=2100, value=now.year, key="year")
        mm = st.number_input('月', min_value=1, max_value=12, value=now.month, key="month")
        md = st.number_input('日', min_value=1, max_value=31, value=now.day, key="day")
    with col2:
        mh = st.number_input('時', min_value=0, max_value=23, value=now.hour, key="hour")
        mmin = st.number_input('分', min_value=0, max_value=59, value=now.minute, key="minute")
    
    option = st.selectbox('起盤方式', ('時計太乙', '年計太乙', '月計太乙', '日計太乙', '分計太乙', '太乙命法'))
    acum = st.selectbox('太乙積年數', ('太乙統宗', '太乙金鏡', '太乙淘金歌', '太乙局'))
    ten_ching = st.selectbox('太乙十精', ('無', '有'))
    sex_o = st.selectbox('太乙命法性別', ('男', '女'))
    rotation = st.selectbox('轉盤', ('固定', '轉動'))
    
    num_dict = {'時計太乙': 3, '年計太乙': 0, '月計太乙': 1, '日計太乙': 2, '分計太乙': 4, '太乙命法': 5}
    style = num_dict[option]
    tn_dict = {'太乙統宗': 0, '太乙金鏡': 1, '太乙淘金歌': 2, '太乙局': 3}
    tn = tn_dict[acum]
    tc_dict = {'有': 1, '無': 0}
    tc = tc_dict[ten_ching]
    
    instant = st.button('即時盤', use_container_width=True)
    
    st.markdown("---")
    st.header("qwen-3-32b 設置")
    
    system_prompts_data = load_system_prompts()
    prompts_list = system_prompts_data.get("prompts", [])
    prompt_names = [prompt["name"] for prompt in prompts_list]
    selected_prompt = system_prompts_data.get("selected")
    
    if prompt_names:
        selected_index = 0
        if selected_prompt in prompt_names:
            selected_index = prompt_names.index(selected_prompt)
        
        selected_name = st.selectbox(
            "選擇系統提示",
            options=prompt_names,
            index=selected_index,
            key="qwen_system_prompt_selector",
            help="選擇用於 qwen-3-32b 模型的系統提示，指導其分析太乙排盤結果"
        )
        
        system_prompts_data["selected"] = selected_name
        
        selected_content = next((prompt["content"] for prompt in prompts_list if prompt["name"] == selected_name), "")
        
        if 'qwen_system_prompt' not in st.session_state:
            st.session_state.qwen_system_prompt = selected_content
        
        if selected_name != st.session_state.get("last_selected_qwen_prompt"):
            st.session_state.qwen_system_prompt = selected_content
            st.session_state.last_selected_qwen_prompt = selected_name
            logger.debug("Updated qwen_system_prompt to: %s", selected_content)
        
        new_content = st.text_area(
            "編輯系統提示",
            value=st.session_state.qwen_system_prompt,
            height=150,
            placeholder="範例：你是一位太乙神數專家，根據排盤數據提供詳細分析...",
            key=f"qwen_system_prompt_editor_{selected_name}"
        )
        
        if new_content != st.session_state.qwen_system_prompt:
            st.session_state.qwen_system_prompt = new_content
            logger.debug("User edited qwen_system_prompt to: %s", new_content)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 更新提示", key="update_qwen_prompt_button"):
                for prompt in prompts_list:
                    if prompt["name"] == selected_name:
                        prompt["content"] = st.session_state.qwen_system_prompt
                        break
                if save_system_prompts(system_prompts_data):
                    st.toast(f"✅ 已更新系統提示 '{selected_name}'！")
                logger.debug("Saved updated prompt: %s", selected_name)
        
        with col2:
            if st.button("❌ 刪除提示", key="delete_qwen_prompt_button", 
                        disabled=len(prompts_list) <= 1):
                prompts_list = [p for p in prompts_list if p["name"] != selected_name]
                system_prompts_data["prompts"] = prompts_list
                if selected_name == selected_prompt and prompts_list:
                    system_prompts_data["selected"] = prompts_list[0]["name"]
                    st.session_state.qwen_system_prompt = prompts_list[0]["content"]
                    st.session_state.last_selected_qwen_prompt = prompts_list[0]["name"]
                if save_system_prompts(system_prompts_data):
                    st.toast(f"✅ 已刪除系統提示 '{selected_name}'！")
                    st.rerun()
                logger.debug("Deleted prompt: %s", selected_name)
    
    if "qwen_form_key_suffix" not in st.session_state:
        st.session_state.qwen_form_key_suffix = 0
    
    name_key = f"new_qwen_prompt_name_{st.session_state.qwen_form_key_suffix}"
    content_key = f"new_qwen_prompt_content_{st.session_state.qwen_form_key_suffix}"
    
    with st.expander("➕ 新增提示", expanded=False):
        new_prompt_name = st.text_input("新提示名稱", key=name_key)
        new_prompt_content = st.text_area(
            "新提示內容",
            height=100,
            placeholder="輸入 qwen-3-32b 的分析指令...",
            key=content_key
        )
        if st.button("➕ 新增提示", key="add_qwen_prompt_button",
                    disabled=not new_prompt_name or not new_prompt_content):
            if new_prompt_name in prompt_names:
                st.error(f"提示名稱 '{new_prompt_name}' 已存在。")
            else:
                prompts_list.append({
                    "name": new_prompt_name,
                    "content": new_prompt_content
                })
                system_prompts_data["prompts"] = prompts_list
                system_prompts_data["selected"] = new_prompt_name
                st.session_state.qwen_system_prompt = new_prompt_content
                st.session_state.last_selected_qwen_prompt = new_prompt_name
                if save_system_prompts(system_prompts_data):
                    st.session_state.qwen_form_key_suffix += 1
                    st.toast(f"✅ 已新增系統提示 '{new_prompt_name}'！")
                    st.rerun()
                logger.debug("Added new prompt: %s", new_prompt_name)
    
    if st.toggle("🔧 高級設置", key="qwen_advanced_settings_toggle"):
        st.session_state.qwen_max_tokens = st.slider(
            "最大生成 Tokens",
            100, 10000,
            st.session_state.get("qwen_max_tokens", 4000),
            key="qwen_max_tokens_slider",
            help="控制 qwen-3-32b 回應的最大長度"
        )
        st.session_state.qwen_temperature = st.slider(
            "溫度 (專注 vs. 創意)",
            0.0, 1.5,
            st.session_state.get("qwen_temperature", 0.7),
            step=0.05,
            key="qwen_temperature_slider",
            help="較低值 (如 0.2) 更確定性；較高值 (如 0.8) 更隨機"
        )
    
    st.markdown("---")
    if st.toggle("🔍 除錯模式", key="debug_mode_toggle", help="顯示除錯資訊，如 session state"):
        st.subheader("🐛 除錯資訊")
        st.write("Session State:")
        st.json(st.session_state)

@st.cache_data
def gen_results(my, mm, md, mh, mmin, style, tn, sex_o, tc):
    """生成太乙計算結果，返回數據字典"""
    logger.debug("Generating Taiyi results for: year=%s, month=%s, day=%s, hour=%s, minute=%s, style=%s, tn=%s, sex_o=%s, tc=%s",
                 my, mm, md, mh, mmin, style, tn, sex_o, tc)
    try:
        ty = kintaiyi.Taiyi(my, mm, md, mh, mmin)
        if style != 5:
            ttext = ty.pan(style, tn) or {}
            if not isinstance(ttext, dict):
                logger.warning("ttext is not a dictionary for style=%s, tn=%s: %s", style, tn, ttext)
                ttext = {}
            kook = ty.kook(style, tn)
            sj_su_predict = f"始擊落{ty.sf_num(style, tn)}宿，{su_dist.get(ty.sf_num(style, tn))}"
            tg_sj_su_predict = config.multi_key_dict_get(tengan_shiji, config.gangzhi(my, mm, md, mh, mmin)[0][0]).get(config.Ganzhiwuxing(ty.sf(style, tn)))
            three_door = ty.threedoors(style, tn)
            five_generals = ty.fivegenerals(style, tn)
            home_vs_away1 = ty.wc_n_sj(style, tn)
            genchart2 = ty.gen_gong(style, tn, tc)
        else:
            tn = 0
            ttext = ty.pan(3, 0) or {}
            if not isinstance(ttext, dict):
                logger.warning("ttext is not a dictionary for style=3, tn=0: %s", ttext)
                ttext = {}
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
        lifedisc2 = ty.stars_descriptions_text(4, 0)
        yc = ty.year_chin()
        year_predict = f"太歲{yc}值宿，{su_dist.get(yc)}"
        home_vs_away3 = ttext.get("推太乙風雲飛鳥助戰法", "無")
        ts = taiyi_yingyang.get(kook.get('文')[0:2]).get(kook.get('數'))
        gz = f"{ttext.get('干支', ['未知']*5)[0]}年 {ttext.get('干支', ['未知']*5)[1]}月 {ttext.get('干支', ['未知']*5)[2]}日 {ttext.get('干支', ['未知']*5)[3]}時 {ttext.get('干支', ['未知']*5)[4]}分"
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
        
        results = {
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
        logger.debug("Generated Taiyi results: %s", json.dumps(results, default=str, ensure_ascii=False))
        return results
    except Exception as e:
        logger.error("Error generating Taiyi results: %s", str(e), exc_info=True)
        raise

# 創建標籤頁
tabs = st.tabs(['🧮太乙排盤', '💬使用說明', '📜局數史例', '🔥災異統計', '📚古籍書目', '🆕更新日誌', '🚀看盤要領', '🔗連結'])

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
                # Debug: Display results dictionary if debug mode is enabled
                if st.session_state.get("debug_mode_toggle"):
                    with st.expander("Debug: Results Dictionary", expanded=False):
                        st.json(results)
                
                if results["style"] == 5:
                    try:
                        start_pt = results["genchart1"][results["genchart1"].index('''viewBox="''')+22:].split(" ")[1]
                        if rotation == "轉動":
                            render_svg(results["genchart1"], int(start_pt))
                        else:
                            render_svg1(results["genchart1"], int(start_pt))
                    except (ValueError, IndexError) as e:
                        st.error(f"Failed to parse SVG viewBox: {str(e)}")
                    with st.expander("解釋"):
                        st.title("《太乙命法》︰")
                        st.markdown("【十二宮分析】")
                        st.markdown(results["lifedisc"])
                        st.markdown("【太乙十六神落宮】")
                        st.markdown(results["lifedisc2"])
                        st.markdown("【值卦】")
                        st.markdown(f"年卦：{results['ygua']}")
                        st.markdown(f"月卦：{results['mgua']}")
                        st.markdown(f"日卦：{results['dgua']}")
                        st.markdown(f"時卦：{results['hgua']}")
                        st.markdown(f"分卦：{results['mingua']}")
                        st.markdown("【陽九行限】")
                        st.markdown(format_text(results["yjxx"]))
                        st.markdown("【百六行限】")
                        st.markdown(format_text(results["blxx"]))
                        st.title("《太乙秘書》︰")
                        st.markdown(results["ts"])
                        st.title("史事記載︰")
                        st.markdown(results["ch"])
                    print(f"{config.gendatetime(my, mm, md, mh, mmin)} {results['zhao']} - {results['ty'].taiyi_life(results['sex_o']).get('性別')} - {config.taiyi_name(0)[0]} - {results['ty'].accnum(0, 0)} | \n農曆︰{results['lunard']} | {jieqi.jq(my, mm, md, mh, mmin)} |\n{results['gz']} |\n{config.kingyear(my)} |\n太乙命法 - {results['ty'].kook(0, 0).get('文')} ({results['ttext'].get('局式', {}).get('年', '無')}) | \n紀元︰{results['ttext'].get('紀元', '無')} | 主筭︰{results['homecal']} 客筭︰{results['awaycal']} |")
                else:
                    try:
                        start_pt2 = results["genchart2"][results["genchart2"].index('''viewBox="''')+22:].split(" ")[1]
                        if rotation == "轉動":
                            render_svg(results["genchart2"], int(start_pt2))
                        else:
                            render_svg1(results["genchart2"], int(start_pt2))
                    except (ValueError, IndexError) as e:
                        st.error(f"Failed to parse SVG viewBox: {str(e)}")
                    with st.expander("解釋"):
                        st.title("《太乙秘書》︰")
                        st.markdown(results["ts"])
                        st.title("史事記載︰")
                        st.markdown(results["ch"])
                        st.title("太乙盤局分析︰")
                        st.markdown(f"太歲值宿斷事︰{results['year_predict']}")
                        st.markdown(f"始擊值宿斷事︰{results['sj_su_predict']}")
                        st.markdown(f"十天干歲始擊落宮預測︰{results['tg_sj_su_predict']}")
                        st.markdown(f"推太乙在天外地內法︰{results['ty'].ty_gong_dist(results['style'], results['tn'])}")
                        st.markdown(f"三門五將︰{results['three_door'] + results['five_generals']}")
                        st.markdown(f"推主客相關︰{results['home_vs_away1']}")
                        st.markdown(f"推少多以占勝負�：{results['ttext'].get('推少多以占勝負', '無')}")
                        st.markdown(f"推太乙風雲飛鳥助戰︰{results['home_vs_away3']}")
                    print(f"{config.gendatetime(my, mm, md, mh, mmin)} | 積{config.taiyi_name(results['style'])[0]}數︰{results['ty'].accnum(results['style'], results['tn'])} | \n"
                          f"農曆︰{results['lunard']} | {jieqi.jq(my, mm, md, mh, mmin)} |\n"
                          f"{results['gz']} |\n"
                          f"{config.kingyear(my)} |\n"
                          f"{config.ty_method(results['tn'])}{results['ttext'].get('太乙計', '')} - {results['ty'].kook(results['style'], results['tn']).get('文', '')} "
                          f"({results['ttext'].get('局式', {}).get('年', '')}) \n五子元局:{results['wuyuan']} | \n"
                          f"紀元�：{results['ttext'].get('紀元', '')} | 主筭︰{results['homecal']} 客筭ﺷ{results['awaycal']} 定筭ﺷ{results['setcal']} |")

                if st.button("🔍 使用 qwen-3-32b 分析排盤結果", key="analyze_with_qwen"):
                    with st.spinner("qwen-3-32b 正在分析太乙排盤結果..."):
                        cerebras_api_key = st.secrets.get("CEREBRAS_API_KEY") or os.getenv("CEREBRAS_API_KEY")
                        if not cerebras_api_key:
                            st.error("CEREBRAS_API_KEY 未設置，請在 .streamlit/secrets.toml 或環境變量中設置。")
                        else:
                            try:
                                client = CerebrasClient(api_key=cerebras_api_key)
                                taiyi_prompt = format_taiyi_results_for_prompt(results)
                                logger.debug("Taiyi prompt for qwen-3-32b: %s", taiyi_prompt)
                                messages = [
                                    {"role": "system", "content": st.session_state.qwen_system_prompt},
                                    {"role": "user", "content": taiyi_prompt}
                                ]
                                api_params = {
                                    "messages": messages,
                                    "model": "qwen-3-32b",
                                    "max_tokens": st.session_state.get("qwen_max_tokens", 4000),
                                    "temperature": st.session_state.get("qwen_temperature", 0.7)
                                }
                                response = client.get_chat_completion(**api_params)
                                raw_response = response.choices[0].message.content
                                with st.expander("qwen-3-32b 分析結果", expanded=True):
                                    st.markdown(raw_response)
                            except Exception as e:
                                logger.error("Error calling qwen-3-32b: %s", str(e), exc_info=True)
                                st.error(f"調用 qwen-3-32b 時發生錯誤：{str(e)}\n請檢查日誌以獲取更多資訊。")
        except Exception as e:
            logger.error("Error generating Taiyi chart: %s", str(e), exc_info=True)
            st.error(f"生成盤局時發生錯誤：{str(e)}")

# 使用說明
with tabs[1]:
    st.markdown(get_file_content_as_string(BASE_URL_KINTAIYI, "instruction.md"))

# 太乙局數史例
with tabs[2]:
    with open('example.json', "r") as f:
        data = f.read()
    timeline(data, height=600)
    with st.expander("列表"):
        st.markdown(get_file_content_as_string(BASE_URL_KINTAIYI, "example.md"))

# 災害統計
with tabs[3]:
    st.markdown(get_file_content_as_string(BASE_URL_KINTAIYI, "disaster.md"))

# 古籍書目
with tabs[4]:
    st.markdown(get_file_content_as_string(BASE_URL_KINTAIYI, "guji.md"))

# 更新日誌
with tabs[5]:
    st.markdown(get_file_content_as_string(BASE_URL_KINTAIYI, "update.md"))

# 看盤要領
with tabs[6]:
    st.markdown(get_file_content_as_string(BASE_URL_KINTAIYI, "tutorial.md"), unsafe_allow_html=True)

# 連結
with tabs[7]:
    st.markdown(get_file_content_as_string(BASE_URL_KINLIUREN, "update.md"), unsafe_allow_html=True)

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
