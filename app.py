import streamlit as st
import datetime
import pytz
from contextlib import contextmanager, redirect_stdout
from io import StringIO
import urllib.request
import base64
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

# 注入自定義 CSS
def set_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700&display=swap');
        /* 設置全域字體 */
        body, h1, h2, h3, h4, h5, h6, p, div, span, .stMarkdown, .stText, .stSelectbox, .stNumberInput, .stButton, .stExpander, .stTabs {
            font-family: 'Noto Sans TC', 'PingFang TC', 'Microsoft YaHei', sans-serif !important;
        }
        /* 強化暗黑模式 */
        .stApp {
            background-color: #1A1C23;
            color: #E0E0E0;
        }
        .stSidebar {
            background-color: #252730;
        }
        .stTabs [role="tab"] {
            background-color: #2E3038;
            color: #E0E0E0;
        }
        .stTabs [role="tab"][aria-selected="true"] {
            background-color: #3A3C45;
            color: #FFFFFF;
        }
        .stButton > button {
            background-color: #3A3C45;
            color: #FFFFFF;
            border: 1px solid #555;
        }
        .stButton > button:hover {
            background-color: #4A4C55;
            color: #FFFFFF;
        }
        .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
            background-color: #2E3038;
            color: #E0E0E0;
            border: 1px solid #555;
        }
        .stExpander {
            background-color: #2E3038;
            color: #E0E0E0;
        }
        #interactive-svg text, #static-svg text {
            font-family: 'Noto Sans TC', 'PingFang TC', 'Microsoft YaHei', sans-serif !important;
            fill: #E0E0E0;
        }
        </style>
    """, unsafe_allow_html=True)

# 調用自定義 CSS
set_custom_css()


st.set_page_config(layout="wide", page_title="堅太乙 - 太乙排盤", initial_sidebar_state="expanded")
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

def render_svg(svg, num):
    """渲染交互式 SVG 圖表，針對 id='layer4' 和 id='layer6' 的 <g> 標籤進行順時針或逆時針旋轉，支援按住滑鼠旋轉並移除殘影"""
    # Validate SVG input
    if not svg or 'svg' not in svg.lower():
        st.error("Invalid SVG content provided")
        return
    
    # 分離 JavaScript 代碼，避免 f-string 嵌套問題
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
      const newRotation = rotations[id] % 360; // 確保 0-359 範圍
      console.log(`計算 newRotation 為 ${id}: ${newRotation}, 累計旋轉: ${rotations[id]}`);

      // 獲取層的邊界框中心作為旋轉點
      const bbox = layer.getBBox();
      const centerX = bbox.x + bbox.width / 2;
      const centerY = bbox.y + bbox.height / 2;
      const transformValue = "rotate(" + newRotation + " " + centerX + " " + centerY + ")";
      layer.setAttribute("transform", transformValue);

      // 旋轉內部的 <text> 元素
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
              const deltaAngle = deltaX * 1.0; // 調整靈敏度，1 像素 = 1 度
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
    # Validate SVG input
    if not svg or 'svg' not in svg.lower():
        st.error("Invalid SVG content provided")
        return
    
    # JavaScript for click handling
    js_script = """
    <script>
        const coloredGroups = new Set();
        let currentColors = []; // Store the current pair of colors

        // Function to generate a random hex color
        function getRandomColor() {
            const letters = '0123456789ABCDEF';
            let color = '#';
            for (let i = 0; i < 6; i++) {
                color += letters[Math.floor(Math.random() * 16)];
            }
            return color;
        }

        // Function to generate two different random colors
        function generateTwoColors() {
            let color1 = getRandomColor();
            let color2 = getRandomColor();
            // Ensure the two colors are different
            while (color1 === color2) {
                color2 = getRandomColor();
            }
            return [color1, color2];
        }

        // Find all segments across all groups
        const allGroups = document.querySelectorAll('#static-svg g');
        const targetLayers = [];
        allGroups.forEach((group, groupIndex) => {
            const segments = group.querySelectorAll('path, polygon, rect');
            if (segments.length > 0) {
                targetLayers.push({ group: group, index: groupIndex, segments: Array.from(segments) });
            }
        });

        // Debug: Log the layers found
        console.log('Found ' + targetLayers.length + ' layers with segments:', targetLayers.map(l => ({ index: l.index, segmentCount: l.segments.length })));

        // Ensure we have at least 4 layers to select the 2nd, 3rd, and 4th
        if (targetLayers.length >= 4) {
            const layersToColor = [targetLayers[1], targetLayers[2], targetLayers[3]]; // 2nd, 3rd, 4th layers

            // Add click handlers to all segments
            layersToColor.forEach((layer, layerNum) => {
                layer.segments.forEach((segment, index) => {
                    segment.style.cursor = 'pointer';
                    segment.style.pointerEvents = 'all';
                    segment.style.zIndex = '10'; // Ensure segments are on top
                    segment.setAttribute('data-index', index);
                    segment.setAttribute('data-layer', layerNum); // Track which layer this segment belongs to
                    segment.addEventListener('click', function(event) {
                        event.stopPropagation();
                        const segmentIndex = parseInt(segment.getAttribute('data-index'));
                        const groupId = `group_${segmentIndex}`;

                        // Debug: Log the click
                        console.log(`Clicked segment in layer ${parseInt(segment.getAttribute('data-layer')) + 2}, index: ${segmentIndex}`);

                        // Check if this group of segments is already colored
                        const isColored = coloredGroups.has(groupId);

                        if (isColored) {
                            layersToColor.forEach(l => {
                                if (l.segments[segmentIndex]) {
                                    l.segments[segmentIndex].removeAttribute('fill');
                                }
                            });
                            coloredGroups.delete(groupId);
                        } else if (coloredGroups.size < 2) {
                            // Generate new random colors if this is a new group
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
                            // Reset colors when both groups are filled
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

# 創建標籤頁
tabs = st.tabs(['🧮太乙排盤', '💬使用說明', '📜局數史例', '🔥災異統計', '📚古籍書目', '🆕更新日誌', '🚀看盤要領', '🔗連結'])

# 側邊欄輸入
with st.sidebar:
    now = datetime.datetime.now(pytz.timezone('Asia/Hong_Kong'))
    st.header("排盤參數設置")
    
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
    lifedisc2 = ty.stars_descriptions_text(4, 0)
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

# 太乙排盤
with tabs[0]:
    output = st.empty()
    with st_capture(output.code):
        try:
            if instant:
                # 即時盤：使用當前時間
                now = datetime.datetime.now(pytz.timezone('Asia/Hong_Kong'))
                results = gen_results(now.year, now.month, now.day, now.hour, now.minute, style, tn, sex_o, tc)
                st.session_state.render_default = False
            else:
                # 使用 timepicker 選擇的日期和時間生成盤式
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
                    print(f"{config.gendatetime(my, mm, md, mh, mmin)} {results['zhao']} - {results['ty'].taiyi_life(results['sex_o']).get('性別')} - {config.taiyi_name(0)[0]} - {results['ty'].accnum(0, 0)} | \n農曆︰{results['lunard']} | {jieqi.jq(my, mm, md, mh, mmin)} |\n{results['gz']} |\n{config.kingyear(my)} |\n太乙命法 - {results['ty'].kook(0, 0).get('文')} ({results['ttext'].get('局式').get('年')}) | \n紀元︰{results['ttext'].get('紀元')} | 主筭︰{results['homecal']} 客筭︰{results['awaycal']} |")
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
                        st.markdown(f"推少多以占勝負︰{results['ttext'].get('推少多以占勝負')}")
                        st.markdown(f"推太乙風雲飛鳥助戰︰{results['home_vs_away3']}")
                    print(f"{config.gendatetime(my, mm, md, mh, mmin)} | 積{config.taiyi_name(results['style'])[0]}數︰{results['ty'].accnum(results['style'], results['tn'])} | \n"
                          f"農曆︰{results['lunard']} | {jieqi.jq(my, mm, md, mh, mmin)} |\n"
                          f"{results['gz']} |\n"
                          f"{config.kingyear(my)} |\n"
                          f"{config.ty_method(results['tn'])}{results['ttext'].get('太乙計', '')} - {results['ty'].kook(results['style'], results['tn']).get('文', '')} "
                          f"({results['ttext'].get('局式', {}).get('年', '')}) 五子元局:{results['wuyuan']} | \n"
                          f"紀元︰{results['ttext'].get('紀元', '')} | 主筭︰{results['homecal']} 客筭︰{results['awaycal']} 定筭︰{results['setcal']} |")
        except Exception as e:
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
