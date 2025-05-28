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

# Define custom components
@st.cache_data
def get_file_content_as_string(base_url, path):
    url = base_url + path
    response = urllib.request.urlopen(url)
    return response.read().decode("utf-8")

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

def render_svg2(svg):
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    html = f'<img src="data:image/svg+xml;base64,{b64}"/>'
    st.write(html, unsafe_allow_html=True)

def render_svg(svg):
    html_content = f"""
    <div>
      <svg id="interactive-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 390 390" width="100%" height="500px" overflow="visible">
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
    """
    html(html_content, height=600)

def render_svg1(svg):
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    html = f"""
    <img src="data:image/svg+xml;base64,{b64}"/>
        <script>
      const rotations = {{}};
      function rotateLayer(layer) {{
        const id = layer.id;
        if (!rotations[id]) rotations[id] = 0;
        rotations[id] += 30;
        layer.setAttribute("transform", `rotate(${{rotations[id]}} 0 0)`);
      }}
      document.querySelectorAll("g").forEach(group => {{
        group.addEventListener("click", () => rotateLayer(group));
      }});
    </script>
    """
    st.write(html, unsafe_allow_html=True)

def timeline(data, height=800):
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
    with StringIO() as stdout, redirect_stdout(stdout):
        old_write = stdout.write
        def new_write(string):
            ret = old_write(string)
            output_func(stdout.getvalue())
            return ret
        stdout.write = new_write
        yield

# Streamlit Page Configuration
st.set_page_config(layout="wide", page_title="堅太乙 - 太鳦排盘")

# Define base URLs for file content
BASE_URL_KINTAIYI = 'https://raw.githubusercontent.com/kentang2017/kintaiyi/master/'
BASE_URL_KINLIUREN = 'https://raw.githubusercontent.com/kentang2017/kinliuren/master/'

# Create Tabs
tabs = st.tabs(['🧮太乙排盤', '💬使用說明', '📜局數史例', '🔥災異統計', '📚古籍書目', '🆕更新日誌', '🚀看盤要領', '🔗連結'])

# Sidebar Inputs
with st.sidebar:
    my = st.number_input('年', min_value=1900, max_value=2100, value=1997)
    mm = st.number_input('月', min_value=1, max_value=12, value=8)
    md = st.number_input('日', min_value=1, max_value=31, value=8)
    mh = st.number_input('時', min_value=0, max_value=23, value=18)
    mmin = st.number_input('分', min_value=0, max_value=59, value=30)
    option = st.selectbox('起盤方式', ('年計太乙', '月計太乙', '日計太乙', '時計太乙', '分計太乙', '太乙命法'))
    acum = st.selectbox('太乙積年數', ('太乙統宗', '太乙金鏡', '太乙淘金歌', '太乙局'))
    sex_o = st.selectbox('太乙命法性別', ('男', '女'))
    num = {'年計太乙': 0, '月計太乙': 1, '日計太乙': 2, '時計太乙': 3, '分計太乙': 4, '太乙命法': 5}[option]
    tn = {'太乙統宗': 0, '太乙金鏡': 1, '太乙淘金歌': 2, '太乙局': 3}[acum]
    col1, col2 = st.columns(2)
    with col1:
        manual = st.button('手動盤')
    with col2:
        instant = st.button('即時盤')

def gen_results(my, mm, md, mh, mmin, num, tn, sex_o):
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
    genchart2 = ty.gen_gong(num, tn)
    kook_num = kook.get("數")
    yingyang = kook.get("文")[0]
    if num != 5:
        wuyuan = ty.get_five_yuan_kook(num, tn)
    else:
        wuyuan = ""
    homecal, awaycal, setcal = config.find_cal(yingyang, kook_num)
    zhao = {"男": "乾造", "女": "坤造"}.get(sex_o)
    life1 = ty.gongs_discription(sex_o)
    life2 = ty.twostar_disc(sex_o)
    lifedisc = ty.convert_gongs_text(life1, life2)
    lifedisc2 = ty.stars_descriptions_text(4, 0)
    ed = ttext.get("八門值事")
    yc = ty.year_chin()
    yj = ttext.get("陽九")
    bl = ttext.get("百六")
    g = ty.yeargua(tn)
    year_predict = f"太歲{yc}值宿，{su_dist.get(yc)}"
    home_vs_away3 = ttext.get("推太乙風雲飛鳥助戰法")
    ts = taiyi_yingyang.get(kook.get('文')[0:2]).get(kook.get('數'))
    gz = f"{ttext.get('干支')[0]}年 {ttext.get('干支')[1]}月 {ttext.get('干支')[2]}日 {ttext.get('干支')[3]}時 {ttext.get('干支')[4]}分"
    lunard = f"{cn2an.transform(str(config.lunar_date_d(my, mm, md).get('年')) + '年', 'an2cn')}{an2cn(config.lunar_date_d(my, mm, md).get('月'))}月{an2cn(config.lunar_date_d(my, mm, md).get('日'))}日"
    ch = chistory.get(my, "")
    tys = "".join([ts[i:i+25] + "\n" for i in range(0, len(ts), 25)])
    yy = "yang" if ttext.get("局式").get("文")[0] == "陽" else "yin"
    yjxx = ty.yangjiu_xingxian(sex_o)
    blxx = ty.bailiu_xingxian(sex_o)
    ygua = ty.year_gua()[1]
    mgua = ty.month_gua()[1]
    dgua = ty.day_gua()[1]
    hgua = ty.hour_gua()[1]
    mingua = ty.minute_gua()[1]
    
    return {
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
        "ed": ed,
        "yc": yc,
        "yj": yj,
        "bl": bl,
        "g": g,
        "year_predict": year_predict,
        "home_vs_away3": home_vs_away3,
        "ts": ts,
        "gz": gz,
        "lunard": lunard,
        "ch": ch,
        "tys": tys,
        "yy": yy,
        "yjxx": yjxx,
        "blxx": blxx,
        "ygua": ygua,
        "mgua": mgua,
        "dgua": dgua,
        "hgua": hgua,
        "mingua": mingua,
        "sj_su_predict": sj_su_predict,
        "tg_sj_su_predict": tg_sj_su_predict,
        "three_door": three_door,
        "five_generals": five_generals,
        "home_vs_away1": home_vs_away1
    }

with tabs[0]:
    output5 = st.empty()
    with st_capture(output5.code):
        try:
            # Default execution with current time, num=3, tn=0, sex_o="男"
            now = datetime.datetime.now(pytz.timezone('Asia/Hong_Kong'))
            result = gen_results(now.year, now.month, now.day, now.hour, now.minute, 3, 0, "男")
            
            # Render SVG based on num
            if 5 == 3:  # Adjusted condition to match num=3 case
                render_svg(result["genchart2"])
                with st.expander("解釋"):
                    st.title("《太乙秘書》︰")
                    st.markdown(result["ts"])
                    st.title("史事記載︰")
                    st.markdown(result["ch"])
                    st.title("太乙盤局分析︰")
                    st.markdown(f"太歲值宿斷事︰{result['year_predict']}")
                    st.markdown(f"始擊值宿斷事︰{result['sj_su_predict']}")
                    st.markdown(f"十天干歲始擊落宮預測︰{result['tg_sj_su_predict']}")
                    st.markdown(f"推太乙在天外地內法︰{kintaiyi.Taiyi(now.year, now.month, now.day, now.hour, now.minute).ty_gong_dist(3, 0)}")
                    st.markdown(f"三門五將︰{result['three_door'] + result['five_generals']}")
                    st.markdown(f"推主客相關︰{result['home_vs_away1']}")
                    st.markdown(f"推多少以占勝負︰{result.get('推多少以占勝負', '')}")
                    st.markdown(f"推孤單以占成敗:{result.get('推孤單以占成敗', '')}")
                    st.markdown(f"推陰陽以占厄會︰{result.get('推陰陽以占厄會', '')}")
                    st.markdown(f"推太乙風雲飛鳥助戰︰{result['home_vs_away3']}")
                    st.markdown(f"明天子巡狩之期術︰{result.get('明天子巡狩之期術', '')}")
                    st.markdown(f"明君基太乙所主術︰{result.get('明君基太乙所主術', '')}")
                    st.markdown(f"明臣基太乙所主術︰{result.get('明臣基太乙所主術', '')}")
                    st.markdown(f"明民基太乙所主術︰{result.get('明民基太乙所主術', '')}")
                    st.markdown(f"明五福太乙所主術︰{result.get('明五福太乙所主術', '')}")
                    st.markdown(f"明五福吉算所主術︰{result.get('明五福吉算所主術', '')}")
                    st.markdown(f"明天乙太乙所主術︰{result.get('明天乙太乙所主術', '')}")
                    st.markdown(f"明地乙太乙所主術︰{result.get('明地乙太乙所主術', '')}")
                    st.markdown(f"明值符太乙所主術︰{result.get('明值符太乙所主術', '')}")
            else:
                render_svg(result["genchart1"])
                with st.expander("解釋"):
                    st.title("《太乙命法》︰")
                    st.markdown("【十二宮分析】")
                    st.markdown(result["lifedisc"])
                    st.markdown("【太乙十六神落宮】")
                    st.markdown(result["lifedisc2"])
                    st.markdown("【值卦】")
                    st.markdown(f"年卦：{result['ygua']}")
                    st.markdown(f"月卦：{result['mgua']}")
                    st.markdown(f"日卦：{result['dgua']}")
                    st.markdown(f"時卦：{result['hgua']}")
                    st.markdown(f"分卦：{result['mingua']}")
                    st.markdown("【陽九行限】")
                    st.markdown(format_text(result["yjxx"]))
                    st.markdown("【百六行限】")
                    st.markdown(format_text(result["blxx"]))
                    st.title("《太乙秘書》︰")
                    st.markdown(result["ts"])
                    st.title("史事記載︰")
                    st.markdown(result["ch"])

            # Additional executions based on button clicks
            if num != 5:
                sex_o = '男'
            if manual:
                result = gen_results(my, mm, md, mh, mmin, num, tn, sex_o)
                if num == 5:
                    render_svg(result["genchart1"])
                    with st.expander("解釋"):
                        st.title("《太乙命法》︰")
                        st.markdown("【十二宮分析】")
                        st.markdown(result["lifedisc"])
                        st.markdown("【太乙十六神落宮】")
                        st.markdown(result["lifedisc2"])
                        st.markdown("【值卦】")
                        st.markdown(f"年卦：{result['ygua']}")
                        st.markdown(f"月卦：{result['mgua']}")
                        st.markdown(f"日卦：{result['dgua']}")
                        st.markdown(f"時卦：{result['hgua']}")
                        st.markdown(f"分卦：{result['mingua']}")
                        st.markdown("【陽九行限】")
                        st.markdown(format_text(result["yjxx"]))
                        st.markdown("【百六行限】")
                        st.markdown(format_text(result["blxx"]))
                        st.title("《太乙秘書》︰")
                        st.markdown(result["ts"])
                        st.title("史事記載︰")
                        st.markdown(result["ch"])
                else:
                    render_svg(result["genchart2"])
                    with st.expander("解釋"):
                        st.title("《太乙秘書》︰")
                        st.markdown(result["ts"])
                        st.title("史事記載︰")
                        st.markdown(result["ch"])
                        st.title("太乙盤局分析︰")
                        st.markdown(f"太歲值宿斷事︰{result['year_predict']}")
                        st.markdown(f"始擊值宿斷事︰{result['sj_su_predict']}")
                        st.markdown(f"十天干歲始擊落宮預測︰{result['tg_sj_su_predict']}")
                        st.markdown(f"推太乙在天外地內法︰{kintaiyi.Taiyi(my, mm, md, mh, mmin).ty_gong_dist(num, tn)}")
                        st.markdown(f"三門五將︰{result['three_door'] + result['five_generals']}")
                        st.markdown(f"推主客相關︰{result['home_vs_away1']}")
                        st.markdown(f"推多少以占勝負︰{result.get('推多少以占勝負', '')}")
                        st.markdown(f"推孤單以占成敗:{result.get('推孤單以占成敗', '')}")
                        st.markdown(f"推陰陽以占厄會︰{result.get('推陰陽以占厄會', '')}")
                        st.markdown(f"推太乙風雲飛鳥助戰︰{result['home_vs_away3']}")
                        st.markdown(f"明天子巡狩之期術︰{result.get('明天子巡狩之期術', '')}")
                        st.markdown(f"明君基太乙所主術︰{result.get('明君基太乙所主術', '')}")
                        st.markdown(f"明臣基太乙所主術︰{result.get('明臣基太乙所主術', '')}")
                        st.markdown(f"明民基太乙所主術︰{result.get('明民基太乙所主術', '')}")
                        st.markdown(f"明五福太乙所主術︰{result.get('明五福太乙所主術', '')}")
                        st.markdown(f"明五福吉算所主術︰{result.get('明五福吉算所主術', '')}")
                        st.markdown(f"明天乙太乙所主術︰{result.get('明天乙太乙所主術', '')}")
                        st.markdown(f"明地乙太乙所主術︰{result.get('明地乙太乙所主術', '')}")
                        st.markdown(f"明值符太乙所主術︰{result.get('明值符太乙所主術', '')}")
            if instant:
                now = datetime.datetime.now(pytz.timezone('Asia/Hong_Kong'))
                result = gen_results(now.year, now.month, now.day, now.hour, now.minute, num, tn, sex_o)
                if num == 5:
                    render_svg(result["genchart1"])
                    with st.expander("解釋"):
                        st.title("《太乙命法》︰")
                        st.markdown("【十二宮分析】")
                        st.markdown(result["lifedisc"])
                        st.markdown("【太乙十六神落宮】")
                        st.markdown(result["lifedisc2"])
                        st.markdown("【值卦】")
                        st.markdown(f"年卦：{result['ygua']}")
                        st.markdown(f"月卦：{result['mgua']}")
                        st.markdown(f"日卦：{result['dgua']}")
                        st.markdown(f"時卦：{result['hgua']}")
                        st.markdown(f"分卦：{result['mingua']}")
                        st.markdown("【陽九行限】")
                        st.markdown(format_text(result["yjxx"]))
                        st.markdown("【百六行限】")
                        st.markdown(format_text(result["blxx"]))
                        st.title("《太乙秘書》︰")
                        st.markdown(result["ts"])
                        st.title("史事記載︰")
                        st.markdown(result["ch"])
                else:
                    render_svg(result["genchart2"])
                    with st.expander("解釋"):
                        st.title("《太乙秘書》︰")
                        st.markdown(result["ts"])
                        st.title("史事記載︰")
                        st.markdown(result["ch"])
                        st.title("太乙盤局分析︰")
                        st.markdown(f"太歲值宿斷事︰{result['year_predict']}")
                        st.markdown(f"始擊值宿斷事︰{result['sj_su_predict']}")
                        st.markdown(f"十天干歲始擊落宮預測︰{result['tg_sj_su_predict']}")
                        st.markdown(f"推太乙在天外地內法︰{kintaiyi.Taiyi(now.year, now.month, now.day, now.hour, now.minute).ty_gong_dist(num, tn)}")
                        st.markdown(f"三門五將︰{result['three_door'] + result['five_generals']}")
                        st.markdown(f"推主客相關︰{result['home_vs_away1']}")
                        st.markdown(f"推多少以占勝負︰{result.get('推多少以占勝負', '')}")
                        st.markdown(f"推孤單以占成敗:{result.get('推孤單以占成敗', '')}")
                        st.markdown(f"推陰陽以占厄會︰{result.get('推陰陽以占厄會', '')}")
                        st.markdown(f"推太乙風雲飛鳥助戰︰{result['home_vs_away3']}")
                        st.markdown(f"明天子巡狩之期術︰{result.get('明天子巡狩之期術', '')}")
                        st.markdown(f"明君基太乙所主術︰{result.get('明君基太乙所主術', '')}")
                        st.markdown(f"明臣基太乙所主術︰{result.get('明臣基太乙所主術', '')}")
                        st.markdown(f"明民基太乙所主術︰{result.get('明民基太乙所主術', '')}")
                        st.markdown(f"明五福太乙所主術︰{result.get('明五福太乙所主術', '')}")
                        st.markdown(f"明五福吉算所主術︰{result.get('明五福吉算所主術', '')}")
                        st.markdown(f"明天乙太乙所主術︰{result.get('明天乙太乙所主術', '')}")
                        st.markdown(f"明地乙太乙所主術︰{result.get('明地乙太乙所主術', '')}")
                        st.markdown(f"明值符太乙所主術︰{result.get('明值符太乙所主術', '')}")
        except ValueError:
            st.empty()

# Additional Tabs Content
with tabs[7]:
    st.header('連結')
    st.markdown(get_file_content_as_string(BASE_URL_KINLIUREN, "update.md"), unsafe_allow_html=True)

with tabs[2]:
    st.header('太乙局數史例')
    with open('example.json', "r") as f:
        data = f.read()
    timeline(data, height=600)
    with st.expander("列表"):
        st.markdown(get_file_content_as_string(BASE_URL_KINTAIYI, "example.md"))

with tabs[6]:
    st.header('看盤要領')
    st.markdown(get_file_content_as_string(BASE_URL_KINTAIYI, "tutorial.md"), unsafe_allow_html=True)

with tabs[4]:
    st.header('古籍書目')
    st.markdown(get_file_content_as_string(BASE_URL_KINTAIYI, "guji.md"))

with tabs[5]:
    st.header('更新日誌')
    st.markdown(get_file_content_as_string(BASE_URL_KINTAIYI, "update.md"))

with tabs[3]:
    st.header('災害統計')
    st.markdown(get_file_content_as_string(BASE_URL_KINTAIYI, "disaster.md"))

with tabs[1]:
    st.header('使用說明')
    st.markdown(get_file_content_as_string(BASE_URL_KINTAIYI, "instruction.md"))
