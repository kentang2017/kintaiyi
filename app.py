import random, re
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import base64
from datetime import datetime
import pytz
from contextlib import contextmanager, redirect_stdout
from io import StringIO

# Attempt to import kintaiyi, handle potential import error
try:
    import kintaiyi
except ImportError as e:
    st.warning(f"Failed to import kintaiyi: {e}. Please ensure the module is installed or in the correct path.")
    kintaiyi = None
import kinqimen2
from tyms_final2 import *
import config
import yincome
import seven
import kinliuren
from cerebras.cloud.sdk import Cerebras
import sys
# Add kintaiyi path if it's a local module (adjust path as needed)
if kintaiyi is None and 'kintaiyi' in locals():
    sys.path.append('/mount/src/shushu/kintaiyi')  # Replace with actual path
    import kintaiyi

# Initialize session state
if 'render_default' not in st.session_state:
    st.session_state.render_default = True

# Set current HKT time as default (11:02 PM PDT on October 24, 2025, converted to HKT)
pdt = pytz.timezone('America/Los_Angeles')
now = datetime.now(pdt).replace(hour=23, minute=2, second=0, microsecond=0)
hkt = pytz.timezone('Asia/Hong_Kong')
current_time = now.astimezone(hkt)
default_date = current_time.date()
default_time = current_time.time()

def render_svg_with_dizhi(svg, dizhi1, dizhi2):
    """Render SVG with only the outermost layer (A160.5,160.5) of two specified 地支 segments (戌 and 申) colored with random distinct colors.
    Returns the HTML content and dynamic height."""
    if not svg or 'svg' not in svg.lower():
        return None, 0  # Return None and 0 height if SVG is invalid
   
    # Valid 地支 list for validation
    valid_dizhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '乾', '坤', '艮', '巽']
   
    # Validate input 地支
    dizhi1 = dizhi1 if dizhi1 in valid_dizhi else None
    dizhi2 = dizhi2 if dizhi2 in valid_dizhi else None
   
    # Helper function to generate a random high-contrast hex color
    def get_random_color():
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        if max(r, g, b) < 200:
            max_idx = random.randint(0, 2)
            if max_idx == 0: r = random.randint(200, 255)
            elif max_idx == 1: g = random.randint(200, 255)
            else: b = random.randint(200, 255)
        return f"#{r:02x}{g:02x}{b:02x}"
   
    # Generate two distinct random colors for 戌 and 申
    color1 = get_random_color()
    color2 = get_random_color()
    while color2 == color1:
        color2 = get_random_color()
   
    # Function to find and color only the outermost path (A160.5,160.5) for a given 地支
    def color_dizhi_path(svg_content, dizhi, color):
        if not dizhi:
            return svg_content
        # Pattern to match text with dy="-0.5em" or "0.0em" containing the dizhi
        text_pattern = r'<text[^>]*>.*?<tspan\s+[^>]*dy="(-0\.5em|0\.0em)"[^>]*>.*?' + re.escape(dizhi) + r'.*?</tspan>.*?</text>'
        text_matches = list(re.finditer(text_pattern, svg_content, re.DOTALL))
        if not text_matches:
            st.warning(f"No matching text found for 地支: {dizhi} with dy='-0.5em' or '0.0em'")
            return svg_content
       
        modified_content = svg_content
        for text_match in text_matches:
            text_start = text_match.start()
            # Look for the preceding paths and target only the outermost (A160.5,160.5)
            path_pattern = r'<path\s+d="[^"]*"\s+stroke="white"\s+stroke-width="1\.8"\s+fill="black"\s*/>'
            path_matches = list(re.finditer(path_pattern, modified_content[:text_start], re.DOTALL))
            if len(path_matches) >= 3:  # Ensure at least 3 paths are available
                # Find the last path with A160.5,160.5
                for i in range(-3, 0):  # Check the last 3 paths
                    path_match = path_matches[i]
                    path_start = path_match.start()
                    path_end = path_match.end()
                    path_content = modified_content[path_start:path_end]
                    if re.search(r'A160\.5,160\.5', path_content):  # Outer section only
                        modified_content = (modified_content[:path_start] +
                                         path_content.replace('fill="black"', f'fill="{color}"') +
                                         modified_content[path_end:])
                        st.write(f"Debug: Colored outermost section for {dizhi} with {color}")
                        break  # Stop after coloring the outermost layer
        return modified_content
   
    # Apply colors only to the outermost layer of 戌 and 申
    modified_svg = svg
    modified_svg = color_dizhi_path(modified_svg, dizhi1, color1)  # 戌
    modified_svg = color_dizhi_path(modified_svg, dizhi2, color2)  # 申
   
    # Extract viewBox from SVG
    viewbox_match = re.search(r'viewBox="([^"]*)"', svg)
    viewbox_str = viewbox_match.group(1) if viewbox_match else "-195.0 -225.0 390 450"
    viewbox_parts = viewbox_str.split()
    viewbox_width = float(viewbox_parts[2])
    viewbox_height = float(viewbox_parts[3])
   
    # No JavaScript for interaction, only initial coloring
    html_content = f"""
    <div style="margin: 0; padding: 0; display: flex; flex-direction: column; align-items: center;">
      <svg id="static-svg" xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox_str}" width="100%" height="auto" preserveAspectRatio="xMidYMid slice" style="margin: 0;">
        {modified_svg}
      </svg>
    </div>
    <style>
      #static-svg {{
        width: 100% !important;
        height: auto !important;
        max-width: 100% !important;
        overflow: visible !important;
      }}
      #static-svg path, #static-svg polygon, #static-svg rect {{
        pointer-events: none !important; /* Disable clicking */
      }}
      .stCodeBlock {{
        margin-bottom: 0 !important;
      }}
    </style>
    """
    dynamic_height = int(viewbox_height * 1.15)  # Increased to 1350px base + 700px buffer = 2050px
    st.write(f"Debug: Calculated dynamic height: {dynamic_height}px")
    st.write(f"Debug: Raw SVG content length: {len(svg)}")  # Debug content length
    return html_content, dynamic_height  # Return both HTML and dynamic height

# Helper function to get team official name
def team_official_name(team):
    client = Cerebras(api_key="csk_4kdv53xyfj56dwkd56n3dnwr9px6npc3xf66tc9vrdy3ym4w")
    stream = client.chat.completions.create(
        messages=[{
            "role": "system",
            "content": f"根據英文維基百科網，告訴我足球隊{team}的官方英文名稱長寫是什麼? 你只需回應我英文名稱就可以了。"
        }],
        model="qwen-3-235b-a22b-instruct-2507",
        stream=True,
        max_completion_tokens=20000,
        temperature=0.7,
        top_p=0.8
    )
    result = ""
    for chunk in stream:
        result += chunk.choices[0].delta.content or ""
    return result

# Load data for 太乙讓球
df1 = pd.read_excel("太乙讓球排局_updated.xlsx")

# Animal scores for yanchin_vs
animal_scores = {
    "角": 5, "亢": 6, "氐": 3, "房": 4, "心": 4,
    "尾": 10, "箕": 10, "斗": 6, "牛": 5, "女": 4,
    "虛": 3, "危": 3, "室": 5, "壁": 3, "奎": 10,
    "婁": 8, "胃": 5, "昴": 4, "畢": 10, "觜": 4,
    "參": 3, "井": 11, "鬼": 4, "柳": 3, "星": 7,
    "張": 4, "翼": 4, "軫": 3
}

# Function to compare animal scores
def yanchin_vs(animal1, animal2):
    if animal1 not in animal_scores or animal2 not in animal_scores:
        return "動物名稱無效，請檢查輸入。"
    score1 = animal_scores[animal1]
    score2 = animal_scores[animal2]
    if score1 > score2:
        return "主"
    elif score1 < score2:
        return "客"
    else:
        return "和"

# Context manager to capture output
@contextmanager
def st_capture(output_func):
    with StringIO() as stdout, redirect_stdout(stdout):
        old_write = stdout.write
        def new_write(string):
            ret = old_write(string)
            output_func(stdout.getvalue())
            return ret
        stdout.write = new_write
        yield

# Set page configuration
st.set_page_config(layout="wide", page_title="太鳦的排盤")

# Create tabs
tyhl, horse, kyc, lrh, tdf, qmhilo = st.tabs(['太乙半大小', '占競馬', '堅演禽', '六壬讓球', '太乙讓球', '奇門半大小'])

# 太乙半大小 Tab
with tyhl:
    st.header('太乙半大小')
    with st.form("ty_form"):
        hometeam_1stchar = st.text_input("輸入主隊名稱首個字：")
        date1 = st.date_input("選擇日期：", min_value=datetime(1900, 1, 1), max_value=datetime(2100, 12, 31), value=default_date)
        time1 = st.time_input("選擇時間：", value=default_time)
        match_number1 = st.number_input("輸入場次（0為單場，1、2、3...為多場順序）：", min_value=0, value=0)
        submitted1 = st.form_submit_button("預測一下")
        if submitted1:
            yy1, mm1, dd1 = date1.year, date1.month, date1.day
            hh1, hmin1 = time1.hour, time1.minute
            output20 = st.empty()
            with st_capture(output20.code):
                t = ty_hilo.taiyi_half_hilo(yy1, mm1, dd1, hh1, hmin1, hometeam_1stchar, match_number1)
                print("")
                print("")
                print(t)

# 奇門半大小 Tab
with qmhilo:
    st.title("奇門半大小")
    with st.form("qmhilo_form"):
        date4 = st.date_input("選擇日期：", min_value=datetime(1900, 1, 1), max_value=datetime(2100, 12, 31), value=default_date)
        time4 = st.time_input("選擇時間：", value=default_time)
        matchno = st.number_input("輸入比賽場次：", min_value=0, value=0)
        submitted4 = st.form_submit_button("測一下大小")
        if submitted4:
            yy4, mm4, dd4 = date4.year, date4.month, date4.day
            hh4, hmin4 = time4.hour, time4.minute
            output11 = st.empty()
            with st_capture(output11.code):
                prediction2 = kinqimen2.Qimen(yy4, mm4, dd4, hh4, hmin4).getbs1(matchno)
                print(f"{yy4}年 {mm4}月 {dd4}日 {hh4}時 {hmin4}分")
                print(prediction2[0])
                print(prediction2[1])

# 太乙讓球 Tab
with tdf:
    st.title("太乙讓球")
    with st.form("tdf_form", clear_on_submit=False):
        col1, col2 = st.columns([1, 1])
        with col1:
            date3 = st.date_input("選擇日期：", min_value=datetime(1900, 1, 1), max_value=datetime(2100, 12, 31), value=default_date)
            time3 = st.time_input("選擇時間：", value=default_time)
        with col2:
            input_home_y3 = st.text_input("輸入主隊名(一個中文/英文字)：")
            input_away_y3 = st.text_input("輸入客隊名(一個中文/英文字)：")
            input_home_strong_or_weak = st.selectbox("主隊(強/弱)", ("強", "弱"))
            input_away_strong_or_weak = st.selectbox("客隊(強/弱)", ("強", "弱"))
        submitted3 = st.form_submit_button("估一下", help="Click to predict the outcome")
        if submitted3 and kintaiyi is not None:
            yy3, mm3, dd3 = date3.year, date3.month, date3.day
            hh3, hmin3 = time3.hour, time3.minute
            output10 = st.empty()
            with st_capture(output10.code):
                prediction1 = rank_twoteams(
                    yy3, mm3, dd3, hh3, hmin3,
                    input_home_y3, input_away_y3,
                    {"強": 1, "弱": 0}.get(input_home_strong_or_weak),
                    {"強": 1, "弱": 0}.get(input_away_strong_or_weak)
                )
                genchart2 = kintaiyi.Taiyi(yy3, mm3, dd3, hh3, hmin3).gen_gong(4, 0, 0)
                h = prediction1[3]["主隊"][0]  # 戌
                a = prediction1[3]["客隊"][0]  # 申
                k = prediction1[3]["局數"]
                r = df1[(df1["局"] == k) & (df1["宮1"] == h) & (df1["宮2"] == a)]
                # Render SVG with colored outermost layer of 戌 and 申
                html_content, dynamic_height = render_svg_with_dizhi(genchart2, h, a)
                if html_content:
                    # Minimize gap and ensure full display with debugging
                    with st.container():
                        st.write("Debug: Rendering SVG with dynamic height:", dynamic_height, "px")
                        st.write("Debug: Raw SVG content length:", len(genchart2))  # Debug content length
                        components.html(html_content, height=dynamic_height, scrolling=True)  # Use calculated height
                else:
                    st.error("Failed to generate SVG content due to invalid input.")
                print(f"{yy3}年 {mm3}月 {dd3}日 {hh3}時 {hmin3}分")
                print(r)
                print(prediction1[0:3])
                print(prediction1[3].get("局數"))
                print(prediction1[3].get("主隊"))
                print(prediction1[3].get("客隊"))
                print(prediction1[3].get("太乙四將分佈"))
        elif not kintaiyi:
            st.error("kintaiyi module is not available. Please install or check the path.")

# 六壬讓球 Tab
with lrh:
    st.title("六壬讓球")
    with st.form("lrh_form"):
        date2 = st.date_input("選擇日期：", min_value=datetime(1900, 1, 1), max_value=datetime(2100, 12, 31), value=default_date)
        time2 = st.time_input("選擇時間：", value=default_time)
        input_home_y2 = st.text_input("輸入主隊名：")
        input_away_y2 = st.text_input("輸入客隊名：")
        submitted2 = st.form_submit_button("估計")
        if submitted2:
            yy2, mm2, dd2 = date2.year, date2.month, date2.day
            hh2, hmin2 = time2.hour, time2.minute
            output9 = st.empty()
            with st_capture(output9.code):
                predict = kinliuren.fliuren(yy2, mm2, dd2, hh2, hmin2).result1(input_home_y2, input_away_y2)
                kk = kinliuren.fliuren(yy2, mm2, dd2, hh2, hmin2).vs(input_home_y2, input_away_y2)
                gz = config.gangzhi(yy2, mm2, dd2, hh2, hmin2)
                print(f"{yy2}年 {mm2}月 {dd2}日 {hh2}時 {hmin2}分")
                print(f"{gz[2]}日{gz[3]}時 | 節氣: {jieqi.jq(yy2, mm2, dd2, hh2, hmin2)}")
                print(f"{input_home_y2} vs {input_away_y2}")
                print(f"預測讓球︰{predict} | {kk[16]}{kk[17]}")
                print(" ")
                print("主　　客")
                print(f"{kk[4]}　　{kk[5]}")
                print(f"{kk[8]}　　{kk[9]}")
                print(f"{kk[6]}　　{kk[7]}")
                print(f"{kk[0]}　　{kk[1]}")
                print(f"{kk[2]}　　{kk[3]}")
                print(f"{kk[10]},{kk[11]},{kk[18]},{kk[19]}")

# 堅演禽 Tab
with kyc:
    st.title("堅演禽")
    with st.form("kyc_form"):
        date1 = st.date_input("選擇日期：", min_value=datetime(1900, 1, 1), max_value=datetime(2100, 12, 31), value=default_date)
        time1 = st.time_input("選擇時間：", value=default_time)
        submitted_kyc = st.form_submit_button("找禽")
        if submitted_kyc:
            yy2, mm2, dd2 = date1.year, date1.month, date1.day
            hh2, hmin2 = time1.hour, time1.minute
            output6 = st.empty()
            try:
                with st_capture(output6.code):
                    home_chin1 = yincome.Yincome(yy2, mm2, dd2, hh2, hmin2).doujiang_min(0)
                    away_chin1 = yincome.Yincome(yy2, mm2, dd2, hh2, hmin2).canfan_chin_min(0)
                    hc_sopo1 = yincome.Yincome(yy2, mm2, dd2, hh2, hmin2).doujiang_min_sopo(0)
                    ac_sopo1 = yincome.Yincome(yy2, mm2, dd2, hh2, hmin2).canfan_chin_min_sopo(0)
                    st.write(f"【堅演禽】：主倒將：{home_chin1}({hc_sopo1})　客翻禽：{away_chin1}({ac_sopo1})")
            except Exception as e:
                st.error(f"Error in 堅演禽 calculation: {e}")

# 占競馬 Tab
with horse:
    st.title("競馬")
    with st.form("horse_form"):
        date_h = st.date_input("選擇日期：", min_value=datetime(1900, 1, 1), max_value=datetime(2100, 12, 31), value=default_date)
        time_h = st.time_input("選擇時間：", value=default_time)
        submitted_horse = st.form_submit_button("找數字")
        if submitted_horse:
            yy1, mm1, dd1 = date_h.year, date_h.month, date_h.day
            hh1, hmin1 = time_h.hour, time_h.minute
            output3 = st.empty()
            with st_capture(output3.code):
                getnum = seven.find_hour_minute(yy1, mm1, dd1, hh1, hmin1)
                print("留意數目包括︰")
                print(f"傳統︰{getnum.get('原始版')}")
