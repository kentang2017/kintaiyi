import streamlit as st
import datetime, pytz, base64, json, urllib
from io import StringIO
from contextlib import contextmanager, redirect_stdout
from time import sleep
import pendulum as pdlm
import kintaiyi
import cn2an
from cn2an import an2cn
import streamlit.components.v1 as components
from historytext import chistory
from taiyidict import tengan_shiji, su_dist
from taiyimishu import taiyi_yingyang
import config
import jieqi
from streamlit_modal import Modal

def timeline(data, height=800):
    if isinstance(data, str):
        data = json.loads(data)
    json_text = json.dumps(data)
    source_param = 'timeline_json'
    source_block = f'var {source_param} = {json_text};'
    cdn_path = 'https://cdn.knightlab.com/libs/timeline3/latest'
    css_block = f'<link title="timeline-styles" rel="stylesheet" href="{cdn_path}/css/timeline.css">'
    js_block = f'<script src="{cdn_path}/js/timeline.js"></script>'
    htmlcode = css_block + '''
        <div id='timeline-embed' style="width: 95%; height: ''' + str(height) + '''px; margin: 1px;"></div>
        <script type="text/javascript">
            var additionalOptions = { start_at_end: false, is_embed: true, default_bg_color: {r:14, g:17, b:23} }
            ''' + source_block + '''
            timeline = new TL.Timeline('timeline-embed', ''' + source_param + ''', additionalOptions);
        </script>'''
    static_component = components.html(htmlcode, height=height)
    return static_component

def render_svg(svg):
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
    st.write(html, unsafe_allow_html=True)

def get_file_content_as_string(path):
    url = 'https://raw.githubusercontent.com/kentang2017/kintaiyi/master/' + path
    response = urllib.request.urlopen(url)
    return response.read().decode("utf-8")

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

st.set_page_config(layout="wide", page_title="堅太乙 - 太鳦排盘")
tabs = [' 🧮太乙排盤 ', ' 💬使用說明 ', ' 📜局數史例 ', ' 🔥災異統計 ', ' 📚古籍書目 ', ' 🆕更新日誌 ', ' 🚀看盤要領 ', ' 🔗連結 ']
pan, ins, example, disaster, guji, update, tutorial, connect = st.tabs(tabs)

def calculate_taiyi(num, tn, my, mm, md, mh, mmin, sex_o):
    ty = kintaiyi.Taiyi(my, mm, md, mh, mmin)
    ttext = ty.pan(num, tn) if num != 5 else ty.pan(0, 0)
    kook = ty.kook(num, tn) if num != 5 else ty.kook(0, 0)
    kook_num = kook.get("數")
    yingyang = kook.get("文")[0]
    homecal = config.find_cal(yingyang, kook_num)[0]
    awaycal = config.find_cal(yingyang, kook_num)[1]
    setcal = config.find_cal(yingyang, kook_num)[2]
    genchart = ty.gen_gong(num, tn) if num != 5 else ty.gen_life_gong(sex_o)
    sj_su_predict = "始擊落" + ty.sf_num(num, tn) + "宿，" + su_dist.get(ty.sf_num(num, tn))
    tg_sj_su_predict = config.multi_key_dict_get(tengan_shiji, config.gangzhi(my, mm, md, mh, mmin)[0][0]).get(config.Ganzhiwuxing(ty.sf(num, tn)))
    three_door = ty.threedoors(num, tn)
    five_generals = ty.fivegenerals(num, tn)
    home_vs_away1 = ty.wc_n_sj(num, tn)
    ed = ttext.get("八門值事")
    yc = ty.year_chin()
    g = ty.yeargua(tn)
    year_predict = "太歲" + yc + "值宿，" + su_dist.get(yc)
    home_vs_away3 = ttext.get("推太乙風雲飛鳥助戰法")
    tynum = ty.accnum(num, tn) if num != 5 else ty.accnum(0, 0)
    gz = "{}年 {}月 {}日 {}時 {}分".format(*ttext.get("干支"))
    lunard = "{}{}月{}日".format(cn2an.transform(str(config.lunar_date_d(my, mm, md).get("年")) + "年", "an2cn"), an2cn(config.lunar_date_d(my, mm, md).get("月")), an2cn(config.lunar_date_d(my, mm, md).get("日")))
    ch = chistory.get(my, "")
    ts = taiyi_yingyang.get(kook.get('文')[0:2]).get(kook.get('數'))
    r = list(map(lambda x: [x, x + 25], list(range(0, 3000)[0::25])))
    tys = "".join([ts[r[i][0]:r[i][1]] + "\n" for i in range(0, int(len(ts) / 25 + 1))])
    return locals()

def display_taiyi_analysis(result):
    render_svg(result['genchart'])
    with st.expander("解釋"):
        if result['num'] == 5:
            st.title("《太乙命法》︰")
            st.markdown("【十二宮分析】")
            st.markdown(result['ty'].convert_gongs_text(result['ty'].gongs_discription(result['sex_o']), result['ty'].twostar_disc(result['sex_o'])))
            st.markdown("【太乙十六神落宮】")
            st.markdown(result['ty'].stars_descriptions_text(4, 0))
        st.title("《太乙秘書》︰")
        st.markdown(result['ts'])
        st.title("史事記載︰")
        st.markdown(result['ch'])
        st.title("太乙盤局分析︰")
        st.markdown("太歲值宿斷事︰" + result['year_predict'])
        st.markdown("始擊值宿斷事︰" + result['sj_su_predict'])
        st.markdown("十天干歲始擊落宮預測︰" + result['tg_sj_su_predict'])
        if result['num'] == 5:
            st.markdown("推太乙在天外地內法︰" + result['ty'].ty_gong_dist(0, 0))
        else:
            st.markdown("推太乙在天外地內法︰" + result['ty'].ty_gong_dist(result['num'], result['tn']))
        st.markdown("三門五將︰" + result['three_door'] + result['five_generals'])
        st.markdown("推主客相關︰" + result['home_vs_away1'])
        st.markdown("推多少以占勝負︰" + result['ttext'].get("推多少以占勝負"))
        st.markdown("推陰陽以占厄會︰" + result['ttext'].get("推陰陽以占厄會"))
        st.markdown("推太乙風雲飛鳥助戰︰" + result['home_vs_away3'])

with st.sidebar:
    idate = st.text_input('輸入日期(如: 1997/8/8)', '')
    itime = st.text_input('輸入時間(如: 18:30)', '').replace("︰", ":")
    option = st.selectbox('起盤方式', ['年計太乙', '月計太乙', '日計太乙', '時計太乙', '分計太乙', '太乙命法'])
    acum = st.selectbox('太乙積年數', ['太乙統宗', '太乙金鏡', '太乙淘金歌', '太乙局'])
    sex_o = st.selectbox('太乙命法性別', ['男', '女'])
    num = dict(zip(['年計太乙', '月計太乙', '日計太乙', '時計太乙', '分計太乙', '太乙命法'], [0, 1, 2, 3, 4, 5]))[option]
    tn = dict(zip(['太乙統宗', '太乙金鏡', '太乙淘金歌', '太乙局'], [0, 1, 2, 3]))[acum]
    manual = st.button('手動盤')
    instant = st.button('即時盤')

    st.markdown("""
        <style>
            div[data-testid="column"] { width: fit-content !important; flex: unset; }
            div[data-testid="column"] * { width: fit-content !important; }
        </style>
    """, unsafe_allow_html=True)

def get_current_datetime():
    now = datetime.datetime.now(pytz.timezone('Asia/Hong_Kong'))
    return now.year, now.month, now.day, now.hour, now.minute

def display_manual_result():
    if len(idate) <= 4:
        idate += "/3/3"
    p = idate.split("/")
    pp = itime.split(":")
    my, mm, md, mh, mmin = int(p[0]), int(p[1]), int(p[2]), int(pp[0]), int(pp[1])
    result = calculate_taiyi(num, tn, my, mm, md, mh, mmin, sex_o)
    display_taiyi_analysis(result)

def display_instant_result():
    my, mm, md, mh, mmin = get_current_datetime()
    result = calculate_taiyi(num, tn, my, mm, md, mh, mmin, sex_o)
    display_taiyi_analysis(result)

with pan:
    output5 = st.empty()
    with st_capture(output5.code):
        try:
            if manual:
                display_manual_result()
            elif instant:
                display_instant_result()
        except ValueError:
            st.error("Invalid input. Please check the date and time format.")

with connect:
    st.header('連結')
    st.markdown(get_file_content_as_string("update.md"), unsafe_allow_html=True)

with example:
    st.header('太乙局數史例')
    with open('example.json', "r") as f:
        data = f.read()
    timeline(data, height=600)
    with st.expander("列表"):
        get_file_content_as_string("example.md")

with tutorial:
    st.header('看盤要領')
    st.markdown(get_file_content_as_string("tutorial.md"), unsafe_allow_html=True)

with guji:
    st.header('古籍書目')
    st.markdown(get_file_content_as_string("guji.md"))

with update:
    st.header('更新日誌')
    st.markdown(get_file_content_as_string("update.md"))

with disaster:
    st.header('災害統計')
    st.markdown(get_file_content_as_string("disaster.md"))

with ins:
    st.header('使用說明')
    st.markdown(get_file_content_as_string("instruction.md"))
