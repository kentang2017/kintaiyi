import streamlit as st
import pendulum as pdlm
import base64
import datetime, pytz
from contextlib import contextmanager, redirect_stdout
from io import StringIO
import aiohttp
import asyncio
import cn2an
from cn2an import an2cn
import streamlit.components.v1 as components
import kintaiyi
from historytext import chistory
from taiyidict import tengan_shiji, su_dist
from taiyimishu import taiyi_yingyang
import config
import jieqi
import json
from streamlit_modal import Modal
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor

# Define custom components
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

def render_svg(svg):
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    html = f'<img src="data:image/svg+xml;base64,{b64}"/>'
    st.write(html, unsafe_allow_html=True)

async def fetch_content(base_url, path):
    url = base_url + path
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

def get_file_content_as_string(base_url, path):
    content = asyncio.run(fetch_content(base_url, path))
    return content

def render_svg_example(html):
    render_svg(html)

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
    idate = st.text_input('輸入日期(如: 1997/8/8)', '')
    itime = st.text_input('輸入時間(如: 18:30)', '').replace("︰", ":")
    option = st.selectbox('起盤方式', ('年計太乙', '月計太乙', '日計太乙', '時計太乙', '分計太乙', '太乙命法'))
    acum = st.selectbox('太乙積年數', ('太乙統宗', '太乙金鏡', '太乙淘金歌', '太乙局'))
    sex_o = st.selectbox('太乙命法性別', ('男', '女'))
    num = {'年計太乙': 0, '月計太乙': 1, '日計太乙': 2, '時計太乙': 3, '分計太乙': 4, '太乙命法': 5}[option]
    tn = {'太乙統宗': 0, '太乙金鏡': 1, '太乙淘金歌': 2, '太乙局': 3}[acum]
    manual = st.button('手動盤')
    instant = st.button('即時盤')

@lru_cache(maxsize=128)
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
    if num == 5:
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
    r = [(x, x + 25) for x in range(0, 3000, 25)]
    tys = "".join([ts[r[i][0]:r[i][1]] + "\n" for i in range((len(ts) // 25) + 1)])
    yy = "yang" if ttext.get("局式").get("文")[0] == "陽" else "yin"
    if num == 5:
        render_svg(genchart1)
        with st.expander("解釋"):
            st.title("《太乙命法》︰")
            st.markdown("【十二宮分析】")
            st.markdown(lifedisc)
            st.markdown("【太乙十六神落宮】")
            st.markdown(lifedisc2)

# Define custom components
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

def render_svg(svg):
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    html = f'<img src="data:image/svg+xml;base64,{b64}"/>'
    st.write(html, unsafe_allow_html=True)

async def fetch_content(base_url, path):
    url = base_url + path
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

def get_file_content_as_string(base_url, path):
    return asyncio.run(fetch_content(base_url, path))

def render_svg_example(html):
    render_svg(html)

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
    idate = st.text_input('輸入日期(如: 1997/8/8)', '')
    itime = st.text_input('輸入時間(如: 18:30)', '').replace("︰", ":")
    option = st.selectbox('起盤方式', ('年計太乙', '月計太乙', '日計太乙', '時計太乙', '分計太乙', '太乙命法'))
    acum = st.selectbox('太乙積年數', ('太乙統宗', '太乙金鏡', '太乙淘金歌', '太乙局'))
    sex_o = st.selectbox('太乙命法性別', ('男', '女'))
    num = {'年計太乙': 0, '月計太乙': 1, '日計太乙': 2, '時計太乙': 3, '分計太乙': 4, '太乙命法': 5}[option]
    tn = {'太乙統宗': 0, '太乙金鏡': 1, '太乙淘金歌': 2, '太乙局': 3}[acum]
    manual = st.button('手動盤')
    instant = st.button('即時盤')

@lru_cache(maxsize=128)
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
    if num == 5:
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
    lunard = f"{cn2an.transform(str(config.lunar_date_d(my, mm, md).get('年')) + '年', 'an2cn')}{an2cn(config.lunar_date_d(my, mm, md).get('月
