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
# 自定義組件定義

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
    """渲染交互式 SVG 圖表"""
    html_content = f"""
    <div style="margin: 0; padding: 0;">
      <svg id="interactive-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {num} {num}" width="100%" height="auto" style="max-height: 400px; display: block; margin: 0 auto;">
        {svg}
      </svg>
      <script>
        const rotations = {{}};
        function rotateLayer(layer) {{
          const id = layer.id;
          if (!rotations[id]) rotations[id] = 0;
          rotations[id] += 30;
          const newRotation = rotations[id] % 360;
          layer.setAttribute("transform", `rotate(${{newRotation}})`);
          layer.querySelectorAll("text").forEach(text => {{
            const angle = newRotation % 360;
            const x = parseFloat(text.getAttribute("x") || 0);
            const y = parseFloat(text.getAttribute("y") || 0);
            const transform = `rotate(${{-angle}}, ${{x}}, ${{y}})`;
            text.setAttribute("transform", transform);
          }});
        }}
        document.querySelectorAll("g").forEach(group => {{
          group.addEventListener("click", () => rotateLayer(group));
        }});
      </script>
    </div>
    <style>
        #interactive-svg {{
            margin-top: 10px;
            margin-bottom: 10px;
        }}
        .stCodeBlock {{
            margin-bottom: 10px !important;
        }}
    </style>
    """
    html(html_content, height=num)  # Reduced height for the HTML component

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
    st.header("輸入參數")
    
    # 使用 st.columns 優化手機端佈局
    col1, col2 = st.columns(2)
    with col1:
        my = st.number_input('年', min_value=0, max_value=2100, value=now.year)
        mm = st.number_input('月', min_value=1, max_value=12, value=now.month)
        md = st.number_input('日', min_value=1, max_value=31, value=now.day)
    with col2:
        mh = st.number_input('時', min_value=0, max_value=23, value=now.hour)
        mmin = st.number_input('分', min_value=0, max_value=59, value=now.minute)
    
    option = st.selectbox('起盤方式', ('時計太乙', '年計太乙', '月計太乙', '日計太乙', '分計太乙', '太乙命法'))
    acum = st.selectbox('太乙積年數', ('太乙統宗', '太乙金鏡', '太乙淘金歌', '太乙局'))
    ten_ching = st.selectbox('太乙十精', ('無','有' ))
    sex_o = st.selectbox('太乙命法性別', ('男', '女'))
    
    # 映射起盤方式到數字
    num_dict = {'時計太乙': 4, '年計太乙': 0, '月計太乙': 1, '日計太乙': 2, '分計太乙': 3, '太乙命法': 5}
    num = num_dict[option]
    
    # 映射積年數到 tn
    tn_dict = {'太乙統宗': 0, '太乙金鏡': 1, '太乙淘金歌': 2, '太乙局': 3}
    tn = tn_dict[acum]
    
    tc_dict = {'有':1, '無':0}
    tc = tc_dict[ten_ching] 
    # 按鈕佈局
    col1, col2 = st.columns(2)
    with col1:
        manual = st.button('手動盤', use_container_width=True)
    with col2:
        instant = st.button('即時盤', use_container_width=True)

@st.cache_data
# Remove @st.cache_data decorator
def gen_results(my, mm, md, mh, mmin, num, tn, sex_o, tc):
    """生成太乙計算結果，返回數據字典"""
    ty = kintaiyi.Taiyi(my, mm, md, mh, mmin)
    if num != 5:
        ttext = ty.pan(num, tn)
        kook = ty.kook(num, tn)
        sj_su_predict = f"始擊落{ty.sf_num(num, tn)}宿，{su_dist.get(ty.sf_num(num, tn))}"
        tg_sj_su_predict = config.multi_key_dict_get(tengan_shiji, config.gangzhi(my, mm, md, mh, mmin)[0][0]).get(config.Ganzhiwuxing(ty.sf(num, tn)))
        three_door = ty.threedoors(num, tn)
        five_generals = ty.fivegenerals(num, tn)
        home_vs_away1 = ty.wc_n_sj(num, tn)
    else:
        tn = 0
        ttext = ty.pan(3, 0)
        kook = ty.kook(3, 0)
        sj_su_predict = f"始擊落{ty.sf_num(3, 0)}宿，{su_dist.get(ty.sf_num(3, 0))}"
        tg_sj_su_predict = config.multi_key_dict_get(tengan_shiji, config.gangzhi(my, mm, md, mh, mmin)[0][0]).get(config.Ganzhiwuxing(ty.sf(3, 0)))
        three_door = ty.threedoors(3, 0)
        five_generals = ty.fivegenerals(3, 0)
        home_vs_away1 = ty.wc_n_sj(3, 0)
    
    genchart1 = ty.gen_life_gong(sex_o)
    genchart2 = ty.gen_gong(num, tn, tc)
    kook_num = kook.get("數")
    yingyang = kook.get("文")[0]
    wuyuan = ty.get_five_yuan_kook(num, tn) if num != 5 else ""
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
    
    # Return all computed data as a dictionary
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
        "num": num,
        "tn": tn,
        "sex_o": sex_o,
        "ty": ty
    }
# 太乙排盤
with tabs[0]:
    output = st.empty()
    with st_capture(output.code):
        try:
            if manual:
                # Use sidebar inputs for manual calculation
                results = gen_results(my, mm, md, mh, mmin, num, tn, sex_o, tc)
                st.session_state.render_default = False
            elif instant:
                # Use current time for instant calculation
                now = datetime.datetime.now(pytz.timezone('Asia/Hong_Kong'))
                results = gen_results(now.year, now.month, now.day, now.hour, now.minute, num, tn, sex_o, tc)
                st.session_state.render_default = False
            elif st.session_state.render_default:
                # Default: Run with current time and specified parameters
                now = datetime.datetime.now(pytz.timezone('Asia/Hong_Kong'))
                results = gen_results(now.year, now.month, now.day, now.hour, now.minute, 3, 0, "男", 0)
            else:
                # Prevent rendering if sidebar changes but no button is clicked
                results = None

            if results:
                # Render UI elements based on results
                if results["num"] == 5:
                    start_pt = results["genchart1"][results["genchart1"].index('''viewBox="''')+22:].split(" ")[1]
                    render_svg(results["genchart1"], int(start_pt))
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
                    print(f"{config.gendatetime(my, mm, md, mh, mmin)} {results['zhao']} - {results['ty'].taiyi_life(results['sex_o']).get('性別')} - {config.taiyi_name(0)[0]} - {results['ty'].accnum(0, 0)} | \n農曆︰{results['lunard']} | {jieqi.jq(my, mm, md, mh, mmin)} |\n{results['gz']} |\n{config.kingyear(my)} |\n{results['ty'].kook(0, 0).get('文')} ({results['ttext'].get('局式').get('年')}) | \n紀元︰{results['ttext'].get('紀元')} | 主筭︰{results['homecal']} 客筭︰{results['awaycal']} |")
                else:
                    start_pt2 = results["genchart2"][results["genchart2"].index('''viewBox="''')+22:].split(" ")[1]
                    render_svg(results["genchart2"], int(start_pt2))
                    with st.expander("解釋"):
                        st.title("《太乙秘書》︰")
                        st.markdown(results["ts"])
                        st.title("史事記載︰")
                        st.markdown(results["ch"])
                        st.title("太乙盤局分析︰")
                        st.markdown(f"太歲值宿斷事︰{results['year_predict']}")
                        st.markdown(f"始擊值宿斷事︰{results['sj_su_predict']}")
                        st.markdown(f"十天干歲始擊落宮預測︰{results['tg_sj_su_predict']}")
                        st.markdown(f"推太乙在天外地內法︰{results['ty'].ty_gong_dist(results['num'], results['tn'])}")
                        st.markdown(f"三門五將︰{results['three_door'] + results['five_generals']}")
                        st.markdown(f"推主客相關︰{results['home_vs_away1']}")
                        st.markdown(f"推少多以占勝負︰{results['ttext'].get('推少多以占勝負')}")
                        st.markdown(f"推太乙風雲飛鳥助戰︰{results['home_vs_away3']}")
                    print(f"{config.gendatetime(my, mm, md, mh, mmin)} | 積{config.taiyi_name(results['num'])[0]}數︰{results['ty'].accnum(results['num'], results['tn'])} | \n農曆︰{results['lunard']} | {jieqi.jq(my, mm, md, mh, mmin)} |\n{results['gz']} |\n{config.kingyear(my)} |\n{config.ty_method(results['tn'])} - {results['ty'].kook(results['num'], results['tn']).get('文')} ({results['ttext'].get('局式').get('年')}) 五子元局:{results['wuyuan']} | \n紀元︰{results['ttext'].get('紀元')} | 主筭︰{results['homecal']} 客筭︰{results['awaycal']} 定筭︰{results['setcal']} |")
        except Exception as e:
            st.error(f"生成盤局時發生錯誤：{str(e)}")

#使用說明
with tabs[1]:
    st.markdown(get_file_content_as_string(BASE_URL_KINTAIYI, "instruction.md"))
#太乙局數史例
with tabs[2]:
    with open('example.json', "r") as f:
        data = f.read()
    timeline(data, height=600)
    with st.expander("列表"):
        st.markdown(get_file_content_as_string(BASE_URL_KINTAIYI, "example.md"))
#災害統計
with tabs[3]:
    st.markdown(get_file_content_as_string(BASE_URL_KINTAIYI, "disaster.md"))
#古籍書目
with tabs[4]:
    st.markdown(get_file_content_as_string(BASE_URL_KINTAIYI, "guji.md"))
#更新日誌
with tabs[5]:
    st.markdown(get_file_content_as_string(BASE_URL_KINTAIYI, "update.md"))
#看盤要領
with tabs[6]:
    st.markdown(get_file_content_as_string(BASE_URL_KINTAIYI, "tutorial.md"), unsafe_allow_html=True)

with tabs[7]:
    st.markdown(get_file_content_as_string(BASE_URL_KINLIUREN, "update.md"), unsafe_allow_html=True)
