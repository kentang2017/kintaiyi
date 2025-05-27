import streamlit as st
import datetime, pytz
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
from st_screen_stats import WindowQueryHelper
import uuid

# Ensure set_page_config is called only once
if not hasattr(st, "_page_config_set"):
    st.set_page_config(
        layout="wide",
        page_title="堅太乙 - 太乙排盤",
        initial_sidebar_state="expanded",
        page_icon="🧮"
    )
    st._page_config_set = True  # Set flag to prevent multiple calls

# Apply custom CSS for better styling and mobile responsiveness
st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css');
    body {
        font-family: 'Noto Sans', sans-serif;
    }
    .stButton>button {
        background-color: #1f2937;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.375rem;
        width: 100%;
        font-size: 1rem;
    }
    .stButton>button:hover {
        background-color: #374151;
    }
    .stTextInput input {
        border-radius: 0.375rem;
        padding: 0.5rem;
        font-size: 1rem;
    }
    .stSelectbox select {
        border-radius: 0.375rem;
        padding: 0.5rem;
        font-size: 1rem;
    }
    .st-expander {
        border-radius: 0.375rem;
        margin-bottom: 1rem;
    }
    @media (max-width: 480px) {
        .stButton>button, .stTextInput input, .stSelectbox select {
            font-size: 0.9rem;
            padding: 0.4rem;
        }
        .stMarkdown, .stHeader {
            font-size: 0.95rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Device detection
with st.container(height=1, border=False):
    helper_screen_stats = WindowQueryHelper()
    window_width = helper_screen_stats.get_window_width()
    
    if window_width <= 480:
        device = "mobile"
        kpi_columns = 1
        number_of_kpi_per_row = 1
        chart_columns = 1
        number_of_charts_per_row = 1
        total_number_of_charts = 4
    elif 481 <= window_width <= 768:
        device = "tablet"
        kpi_columns = 3
        number_of_kpi_per_row = 2
        chart_columns = 2
        number_of_charts_per_row = 2
        total_number_of_charts = 4
    elif 769 <= window_width <= 1024:
        device = "laptop"
        kpi_columns = 4
        number_of_kpi_per_row = 2
        chart_columns = 2
        number_of_charts_per_row = 2
        total_number_of_charts = 4
    else:
        device = "large_screen"
        kpi_columns = 6
        number_of_kpi_per_row = 6
        chart_columns = 4
        number_of_charts_per_row = 4
        total_number_of_charts = 4

@st.cache_data
def get_file_content_as_string(base_url, path):
    try:
        url = base_url + path
        response = urllib.request.urlopen(url)
        return response.read().decode("utf-8")
    except Exception as e:
        st.error(f"Error loading content: {str(e)}")
        return ""

@st.cache_data
def format_text(d, parent_key=""):
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

@st.cache_data
def render_svg(svg, height=500):
    try:
        b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
        html_content = f"""
        <div class="flex justify-center">
            <img src="data:image/svg+xml;base64,{b64}" style="width: 100%; max-width: {height}px; height: auto;" />
        </div>
        <script>
            const rotations = {{}};
            function rotateLayer(layer) {{
                const id = layer.id || 'layer-' + Math.random().toString(36).substr(2, 9);
                if (!rotations[id]) rotations[id] = 0;
                rotations[id] += 30;
                const newRotation = rotations[id] % 360;
                layer.setAttribute("transform", `rotate(${{newRotation}})`);
                layer.querySelectorAll("text").forEach(text => {{
                    const angle = newRotation % 360;
                    const x = parseFloat(text.getAttribute("x") || 0);
                    const y = parseFloat(text.getAttribute("y") || 0);
                    text.setAttribute("transform", `rotate(${{-angle}}, ${{x}}, ${{y}})`);
                }});
            }}
            document.querySelectorAll("g").forEach(group => {{
                group.addEventListener("click", () => rotateLayer(group));
                group.addEventListener("touchstart", () => rotateLayer(group));
            }});
        </script>
        """
        html(html_content, height=height + 50)
    except Exception as e:
        st.error(f"Error rendering SVG: {str(e)}")

@st.cache_data
def timeline(data, height=600):
    try:
        if isinstance(data, str):
            data = json.loads(data)
        json_text = json.dumps(data)
        source_param = f'timeline_json_{uuid.uuid4().hex}'
        cdn_path = 'https://cdn.knightlab.com/libs/timeline3/latest'
        css_block = f'<link title="timeline-styles" rel="stylesheet" href="{cdn_path}/css/timeline.css">'
        js_block = f'<script src="{cdn_path}/js/timeline.js"></script>'
        htmlcode = f'''
            {css_block}
            {js_block}
            <div id='timeline-embed' class="w-full" style="height: {height}px; margin: 1px;"></div>
            <script type="text/javascript">
                var additionalOptions = {{ start_at_end: false, is_embed: true, default_bg_color: {{r:14, g:17, b:23}} }};
                var {source_param} = {json_text};
                new TL.Timeline('timeline-embed', {source_param}, additionalOptions);
            </script>
        '''
        components.html(htmlcode, height=height)
    except Exception as e:
        st.error(f"Error rendering timeline: {str(e)}")

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

# Base URLs
BASE_URL_KINTAIYI = 'https://raw.githubusercontent.com/kentang2017/kintaiyi/master/'
BASE_URL_KINLIUREN = 'https://raw.githubusercontent.com/kentang2017/kinliuren/master/'

# Tabs
tabs = st.tabs(['🧮 太乙排盤', '💬 使用說明', '📜 局數史例', '🔥 災異統計', '📚 古籍書目', '🆕 更新日誌', '🚀 看盤要領', '🔗 連結'])

# Sidebar Inputs
with st.sidebar:
    st.header("輸入參數")
    idate = st.text_input('日期 (如: 1997/8/8)', placeholder="YYYY/MM/DD")
    itime = st.text_input('時間 (如: 18:30)', placeholder="HH:MM").replace("︰", ":")
    option = st.selectbox('起盤方式', ('年計太乙', '月計太乙', '日計太乙', '時計太乙', '分計太乙', '太乙命法'))
    acum = st.selectbox('太乙積年數', ('太乙統宗', '太乙金鏡', '太乙淘金歌', '太乙局'))
    sex_o = st.selectbox('太乙命法性別', ('男', '女'), disabled=option != '太乙命法')
    num = {'年計太乙': 0, '月計太乙': 1, '日計太乙': 2, '時計太乙': 3, '分計太乙': 4, '太乙命法': 5}[option]
    tn = {'太乙統宗': 0, '太乙金鏡': 1, '太乙淘金歌': 2, '太乙局': 3}[acum]
    col1, col2 = st.columns(2)
    with col1:
        manual = st.button('手動盤', use_container_width=True)
    with col2:
        instant = st.button('即時盤', use_container_width=True)

@st.cache_data
def gen_results(my, mm, md, mh, mmin, num Johanna, tn, sex_o):
    try:
        ty = kintaiyi.Taiyi(my, mm, md, mh, mmin)
        if num != 5:
            ttext = ty.pan(num, tn)
            kook = ty.kook(num, tn)
            sj_su_predict = f"始擊落{ty.sf_num(num, tn)}宿，{su_dist.get(ty.sf_num(num, tn))}"
            tg_sj_su_predict = config.multi_key_dict_get(tengan_shiji, config.gangzhi(my, mm, md, mh, mmin)[0][0]).get(config.Ganzhiwuxing(ty.sf(num, tn)))
            three_door = ty.threedoors(num, tn)
            five_generals = ty.fivegenerals(num, tn)
            home_vs_away1 = ty.wc_n_sj(num, tn)
            genchart = ty.gen_gong(num, tn)
        else:
            tn = 0
            ttext = ty.pan(3, 0)
            kook = ty.kook(3, 0)
            sj_su_predict = f"始擊落{ty.sf_num(3, 0)}宿，{su_dist.get(ty.sf_num(3, 0))}"
            tg_sj_su_predict = config.multi_key_dict_get(tengan_shiji, config.gangzhi(my, mm, md, mh, mmin)[0][0]).get(config.Ganzhiwuxing(ty.sf(3, 0)))
            three_door = ty.threedoors(3, 0)
            five_generals = ty.fivegenerals(3, 0)
            home_vs_away1 = ty.wc_n_sj(3, 0)
            genchart = ty.gen_life_gong(sex_o)

        kook_num = kook.get("數")
        yingyang = kook.get("文")[0]
        wuyuan = ty.get_five_yuan_kook(num, tn) if num != 5 else ""
        homecal, awaycal, setcal = config.find_cal(yingyang, kook_num)
        zhao = {"男": "乾造", "女": "坤造"}.get(sex_o)
        life1 = ty.gongs_discription(sex_o) if num == 5 else {}
        life2 = ty.twostar_disc(sex_o) if num == 5 else {}
        lifedisc = ty.convert_gongs_text(life1, life2) if num == 5 else ""
        lifedisc2 = ty.stars_descriptions_text(4, 0) if num == 5 else ""
        ed = ttext.get("八門值事")
        yc = ty.year_chin()
        g = ty.yeargua(tn)
        year_predict = f"太歲{yc}值宿，{su_dist.get(yc)}"
        home_vs_away3 = ttext.get("推太乙風雲飛鳥助戰法")
        ts = taiyi_yingyang.get(kook.get('文')[0:2]).get(kook.get('數'))
        gz = f"{ttext.get('干支')[0]}年 {ttext.get('干支')[1]}月 {ttext.get('干支')[2]}日 {ttext.get('干支')[3]}時 {ttext.get('干支')[4]}分"
        lunard = f"{cn2an.transform(str(config.lunar_date_d(my, mm, md).get('年')) + '年', 'an2cn')}{an2cn(config.lunar_date_d(my, mm, md).get('月'))}月{an2cn(config.lunar_date_d(my, mm, md).get('日'))}日"
        ch = chistory.get(my, "")
        tys = "".join([ts[i:i+25] + "\n" for i in range(0, len(ts), 25)])
        yjxx = ty.yangjiu_xingxian(sex_o) if num == 5 else {}
        blxx = ty.bailiu_xingxian(sex_o) if num == 5 else {}
        ygua = ty.year_gua()[1] if num == 5 else ""
        mgua = ty.month_gua()[1] if num == 5 else ""
        dgua = ty.day_gua()[1] if num == 5 else ""
        hgua = ty.hour_gua()[1] if num == 5 else ""
        mingua = ty.minute_gua()[1] if num == 5 else ""
        ltext_info = (f"{config.gendatetime(my, mm, md, mh, mmin)} {zhao} - {ty.taiyi_life(sex_o).get('性別')} - "
                     f"{config.taiyi_name(0)[0]} - {ty.accnum(0, 0)} | \n農曆︰{lunard} | {jieqi.jq(my, mm, md, mh, mmin)} |\n"
                     f"{gz} |\n{config.kingyear(my)} |\n{ty.kook(0, 0).get('文')} ({ttext.get('局式').get('年')}) | \n"
                     f"紀元︰{ttext.get('紀元')} | 主筭︰{homecal} 客筭︰{awaycal} |\n{yc}禽值年 | {ed}門值事 | \n"
                     f"{g}卦值年 | 太乙統運卦︰{config.find_gua(config.lunar_date_d(my, mm, md).get('年'))}")
        text_info = (f"{config.gendatetime(my, mm, md, mh, mmin)} | 積{config.taiyi_name(num)[0]}數︰{ty.accnum(num, tn)} | \n"
                    f"農曆︰{lunard} | {jieqi.jq(my, mm, md, mh, mmin)} |\n{gz} |\n{config.kingyear(my)} |\n"
                    f"{config.ty_method(tn)} - {config.taiyi_name(num)} - {ty.kook(num, tn).get('文')} ({ttext.get('局式').get('年')}) "
                    f"五子元局:{wuyuan} | \n紀元︰{ttext.get('紀元')} | 主筭︰{homecal} 客筭︰{awaycal} 定筭︰{setcal} |\n"
                    f"{yc}禽值年 | {ed}門值事 | \n{g}卦值年 | 太乙統運卦︰{config.find_gua(config.lunar_date_d(my, mm, md).get('年'))} |")

        return {
            "genchart": genchart,
            "text_info": text_info,
            "ltext_info": ltext_info,
            "tys": tys,
            "ch": ch,
            "year_predict": year_predict,
            "sj_su_predict": sj_su_predict,
            "tg_sj_su_predict": tg_sj_su_predict,
            "three_door": three_door,
            "five_generals": five_generals,
            "home_vs_away1": home_vs_away1,
            "home_vs_away3": home_vs_away3,
            "ttext": ttext,
            "lifedisc": lifedisc,
            "lifedisc2": lifedisc2,
            "ygua": ygua,
            "mgua": mgua,
            "dgua": dgua,
            "hgua": hgua,
            "mingua": mingua,
            "yjxx": yjxx,
            "blxx": blxx
        }
    except Exception as e:
        st.error(f"Error generating results: {str(e)}")
        return None

# Main Tab
with tabs[0]:
    output5 = st.empty()
    with st_capture(output5.code):
        try:
            if manual or instant:
                if num != 5:
                    sex_o = '男'
                if manual:
                    if num == 0 and len(idate) <= 4:
                        idate += "/3/3"
                    p = [int(x) for x in idate.split("/")]
                    pp = [int(x) for x in itime.split(":")]
                    if len(p) != 3 or len(pp) != 2:
                        raise ValueError("Invalid date or time format")
                    my, mm, md = p
                    mh, mmin = pp
                else:
                    now = datetime.datetime.now(pytz.timezone('Asia/Hong_Kong'))
                    my, mm, md, mh, mmin = now.year, now.month, now.day, now.hour, now.minute
                results = gen_results(my, mm, md, mh, mmin, num, tn, sex_o)
                if results:
                    render_svg(results["genchart"], height=400 if device == "mobile" else 500)
                    st.markdown(results["ltext_info" if num == 5 else "text_info"], unsafe_allow_html=True)
                    with st.expander("解釋", expanded=device != "mobile"):
                        if num == 5:
                            st.subheader("《太乙命法》")
                            st.markdown("**十二宮分析**")
                            st.markdown(results["lifedisc"])
                            st.markdown("**太乙十六神落宮**")
                            st.markdown(results["lifedisc2"])
                            st.markdown("**值卦**")
                            st.markdown(f"年卦：{results['ygua']}")
                            st.markdown(f"月卦：{results['mgua']}")
                            st.markdown(f"日卦：{results['dgua']}")
                            st.markdown(f"時卦：{results['hgua']}")
                            st.markdown(f"分卦：{results['mingua']}")
                            st.markdown("**陽九行限**")
                            st.markdown(format_text(results["yjxx"]))
                            st.markdown("**百六行限**")
                            st.markdown(format_text(results["blxx"]))
                            st.subheader("《太乙秘書》")
                            st.markdown(results["tys"])
                            st.subheader("史事記載")
                            st.markdown(results["ch"])
                        else:
                            st.subheader("《太乙秘書》")
                            st.markdown(results["tys"])
                            st.subheader("史事記載")
                            st.markdown(results["ch"])
                            st.subheader("太乙盤局分析")
                            st.markdown(f"**太歲值宿斷事**：{results['year_predict']}")
                            st.markdown(f"**始擊值宿斷事**：{results['sj_su_predict']}")
                            st.markdown(f"**十天干歲始擊落宮預測**：{results['tg_sj_su_predict']}")
                            st.markdown(f"**推太乙在天外地內法**：{ty.ty_gong_dist(num, tn)}")
                            st.markdown(f"**三門五將**：{results['three_door'] + results['five_generals']}")
                            st.markdown(f"**推主客相關**：{results['home_vs_away1']}")
                            st.markdown(f"**推多少以占勝負**：{results['ttext'].get('推多少以占勝負')}")
                            st.markdown(f"**推孤單以占成敗**：{results['ttext'].get('推孤單以占成敗')}")
                            st.markdown(f"**推陰陽以占厄會**：{results['ttext'].get('推陰陽以占厄會')}")
                            st.markdown(f"**推太乙風雲飛鳥助戰**：{results['home_vs_away3']}")
                            for key in ['明天子巡狩之期術', '明君基太乙所主術', '明臣基太乙所主術', '明民基太乙所主術', 
                                       '明五福太乙所主術', '明五福吉算所主術', '明天乙太乙所主術', '明地乙太乙所主術', '明值符太乙所主術']:
                                st.markdown(f"**{key}**：{results['ttext'].get(key)}")
        except ValueError as e:
            st.error(f"輸入格式錯誤：{str(e)}")
        except Exception as e:
            st.error(f"處理錯誤：{str(e)}")

# Additional Tabs
with tabs[1]:
    st.header('使用說明', divider='blue')
    st.markdown(get_file_content_as_string(BASE_URL_KINTAIYI, "instruction.md"), unsafe_allow_html=True)

with tabs[2]:
    st.header('太乙局數史例', divider='blue')
    try:
        with open('example.json', "r") as f:
            data = f.read()
        timeline(data, height=500 if device == "mobile" else 600)
        with st.expander("列表", expanded=device != "mobile"):
            st.markdown(get_file_content_as_string(BASE_URL_KINTAIYI, "example.md"), unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading examples: {str(e)}")

with tabs[3]:
    st.header('災害統計', divider='blue')
    st.markdown(get_file_content_as_string(BASE_URL_KINTAIYI, "disaster.md"), unsafe_allow_html=True)

with tabs[4]:
    st.header('古籍書目', divider='blue')
    st.markdown(get_file_content_as_string(BASE_URL_KINTAIYI, "guji.md"), unsafe_allow_html=True)

with tabs[5]:
    st.header('更新日誌', divider='blue')
    st.markdown(get_file_content_as_string(BASE_URL_KINTAIYI, "update.md"), unsafe_allow_html=True)

with tabs[6]:
    st.header('看盤要領', divider='blue')
    st.markdown(get_file_content_as_string(BASE_URL_KINTAIYI, "tutorial.md"), unsafe_allow_html=True)

with tabs[7]:
    st.header('連結', divider='blue')
    st.markdown(get_file_content_as_string(BASE_URL_KINLIUREN, "update.md"), unsafe_allow_html=True)
