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

# 定義自定義組件
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
    return "\n\n".join(items)+"\n\n"

def render_svg2(svg):
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    html = f'<img src="data:image/svg+xml;base64,{b64}"/>'
    st.write(html, unsafe_allow_html=True)

def render_svg(svg):
    # 直接嵌入原始 SVG 和互動 JavaScript
    html_content = f"""
    <div>
      <svg id="interactive-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 390 390" width="100%" height="500px" overflow="visible">
        {svg}
      </svg>
       <script>
        const rotations = {{}}; // 儲存每個層的旋轉角度
    
        function rotateLayer(layer) {{
          const id = layer.id;
          if (!rotations[id]) rotations[id] = 0;
          rotations[id] += 30; // 每次點擊旋轉 30 度
          const newRotation = rotations[id] % 360;
    
          // 更新組的旋轉
          layer.setAttribute("transform", `rotate(${{newRotation}})`);
    
          // 調整組內的文字元素保持水平
          layer.querySelectorAll("text").forEach(text => {{
            const angle = newRotation % 360; // 層的角度
            const x = parseFloat(text.getAttribute("x") || 0);
            const y = parseFloat(text.getAttribute("y") || 0);
    
            // 計算新的文字旋轉以補償組的旋轉
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
        rotations[id] += 30; // 旋轉 30 度
        layer.setAttribute(
          "transform",
          `rotate(${{rotations[id]}} 0 0)`
        );
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

# Streamlit 頁面配置
st.set_page_config(layout="wide", page_title="堅太乙 - 太鳦排盘")

# 定義文件內容的基本 URL
BASE_URL_KINTAIYI = 'https://raw.githubusercontent.com/kentang2017/kintaiyi/master/'
BASE_URL_KINLIUREN = 'https://raw.githubusercontent.com/kentang2017/kinliuren/master/'

# 創建標籤頁
tabs = st.tabs(['🧮太乙排盤', '💬使用說明', '📜局數史例', '🔥災異統計', '📚古籍書目', '🆕更新日誌', '🚀看盤要領', '🔗連結'])

# Sidebar 輸入
with st.sidebar:
    now = datetime.datetime.now(pytz.timezone('Asia/Hong_Kong'))
    my = st.number_input('年', min_value=0, max_value=2100, value=now.year)
    mm = st.number_input('月', min_value=1, max_value=12, value=now.month)
    md = st.number_input('日', min_value=1, max_value=31, value=now.day)
    mh = st.number_input('時', min_value=0, max_value=23, value=now.hour)
    mmin = st.number_input('分', min_value=0, max_value=59, value=now.minute)
    option = st.selectbox('起盤方式', ('時計太乙', '年計太乙', '月計太乙', '日計太乙', '分計太乙', '太乙命法'))
    acum = st.selectbox('太乙積年數', ('太乙統宗', '太乙金鏡', '太乙淘金歌', '太乙局'))
    sex_o = st.selectbox('太乙命法性別', ('男', '女'))
    num = {'年計太乙': 0, '月計太乙': 1, '日計太乙': 2, '時計太乙': 3, '分計太乙': 4, '太乙命法': 5}[option]
    tn = {'太乙統宗': 0, '太乙金鏡': 1, '太乙淘金歌': 2, '太乙局': 3}[acum]

    # 使用 HTML/CSS 優化按鈕佈局，實現水平排列
    st.markdown("""
    <div style="display: flex; justify-content: space-between;">
        <button onclick="st.session_state.manual_button = True">手動盤</button>
        <button onclick="st.session_state.instant_button = True">即時盤</button>
    </div>
    """, unsafe_allow_html=True)

    # 通過 session_state 監聽按鈕點擊
    if 'manual_button' in st.session_state and st.session_state.manual_button:
        manual = True
        del st.session_state.manual_button  # 重置狀態
    else:
        manual = False

    if 'instant_button' in st.session_state and st.session_state.instant_button:
        instant = True
        del st.session_state.instant_button  # 重置狀態
    else:
        instant = False

@st.cache_data
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
    if num == 5:
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
    
    if num == 5:
        render_svg(genchart1)
        with st.expander("解釋"):
            st.title("《太乙命法》︰")
            st.markdown("【十二宮分析】")
            st.markdown(lifedisc)
            st.markdown("【太乙十六神落宮】")
            st.markdown(lifedisc2)
            st.markdown("【值卦】")
            st.markdown("年卦：{}".format(ygua))
            st.markdown("月卦：{}".format(mgua))
            st.markdown("日卦：{}".format(dgua))
            st.markdown("時卦：{}".format(hgua))
            st.markdown("分卦：{}".format(mingua))
            st.markdown("【陽九行限】")
            st.markdown(format_text(yjxx))
            st.markdown("【百六行限】")
            st.markdown(format_text(blxx))
            st.title("《太乙秘書》︰")
            st.markdown(ts)
            st.title("史事記載︰")
            st.markdown(ch)
        print(f"{config.gendatetime(my, mm, md, mh, mmin)} {zhao} - {ty.taiyi_life(sex_o).get('性別')} - {config.taiyi_name(0)[0]} - {ty.accnum(0, 0)} | \n農曆︰{lunard} | {jieqi.jq(my, mm, md, mh, mmin)} |\n{gz} |\n{config.kingyear(my)} |\n{ty.kook(0, 0).get('文')} ({ttext.get('局式').get('年')}) | \n紀元︰{ttext.get('紀元')} | 主筭︰{homecal} 客筭︰{awaycal} |\n{yc}禽值年 | {ed}門值事 | \n{g}卦值年 | 太乙統運卦︰{config.find_gua(config.lunar_date_d(my, mm, md).get('年'))}")
    else:
        render_svg(genchart2)
        with st.expander("解釋"):
            st.title("《太乙秘書》︰")
            st.markdown(ts)
            st.title("史事記載︰")
            st.markdown(ch)
            st.title("太乙盤局分析︰")
            st.markdown(f"太歲值宿斷事︰{year_predict}")
            st.markdown(f"始擊值宿斷事︰{sj_su_predict}")
            st.markdown(f"十天干歲始擊落宮預測︰{tg_sj_su_predict}")
            st.markdown(f"推太乙在天外地內法︰{ty.ty_gong_dist(num, tn)}")
            st.markdown(f"三門五將︰{three_door + five_generals}")
            st.markdown(f"推主客相關︰{home_vs_away1}")
            st.markdown(f"推多少以占勝負︰{ttext.get('推多少以占勝負')}")
            st.markdown(f"推孤單以占成敗:{ttext.get('推孤單以占成敗')}")
            st.markdown(f"推陰陽以占厄會︰{ttext.get('推陰陽以占厄會')}")
            st.markdown(f"推太乙風雲飛鳥助戰︰{home_vs_away3}")
            st.markdown(f"明天子巡狩之期術︰{ttext.get('明天子巡狩之期術')}")
            st.markdown(f"明君基太乙所主術︰{ttext.get('明君基太乙所主術')}")
            st.markdown(f"明臣基太乙所主術︰{ttext.get('明臣基太乙所主術')}")
            st.markdown(f"明民基太乙所主術︰{ttext.get('明民基太乙所主術')}")
            st.markdown(f"明五福太乙所主術︰{ttext.get('明五福太乙所主術')}")
            st.markdown(f"明五福吉算所主術︰{ttext.get('明五福吉算所主術')}")
            st.markdown(f"明天乙太乙所主術︰{ttext.get('明天乙太乙所主術')}")
            st.markdown(f"明地乙太乙所主術︰{ttext.get('明地乙太乙所主術')}")
            st.markdown(f"明值符太乙所主術︰{ttext.get('明值符太乙所主術')}")
        print(f"{config.gendatetime(my, mm, md, mh, mmin)} | 積{config.taiyi_name(num)[0]}數︰{ty.accnum(num, tn)} | \n農曆︰{lunard} | {jieqi.jq(my, mm, md, mh, mmin)} |\n{gz} |\n{config.kingyear(my)} |\n{config.ty_method(tn)} - {config.taiyi_name(num)} - {ty.kook(num, tn).get('文')} ({ttext.get('局式').get('年')}) 五子元局:{wuyuan} | \n紀元︰{ttext.get('紀元')} | 主筭︰{homecal} 客筭︰{awaycal} 定筭�：{setcal} |\n{yc}禽值年 | {ed}門值事 | \n{g}卦值年 | 太乙統運卦︰{config.find_gua(config.lunar_date_d(my, mm, md).get('年'))} |")

with tabs[0]:
    output5 = st.empty()
    with st_capture(output5.code):
        try:
            if num != 5:
                sex_o = '男'
            if manual:
                gen_results(my, mm, md, mh, mmin, num, tn, sex_o)
            if instant:
                now = datetime.datetime.now(pytz.timezone('Asia/Hong_Kong'))
                gen_results(now.year, now.month, now.day, now.hour, now.minute, num, tn, sex_o)
        except ValueError:
            st.empty()

# 其他標籤頁內容
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
