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
    sex_o = st.selectbox('太乙命法性別', ('男', '女'))
    
    # 映射起盤方式到數字
    num_dict = {'時計太乙': 4, '年計太乙': 0, '月計太乙': 1, '日計太乙': 2, '分計太乙': 3, '太乙命法': 5}
    num = num_dict[option]
    
    # 映射積年數到 tn
    tn_dict = {'太乙統宗': 0, '太乙金鏡': 1, '太乙淘金歌': 2, '太乙局': 3}
    tn = tn_dict[acum]
    
    # 按鈕佈局
    col1, col2 = st.columns(2)
    with col1:
        manual = st.button('手動盤', use_container_width=True)
    with col2:
        instant = st.button('即時盤', use_container_width=True)

@st.cache_data
def gen_results(my, mm, md, mh, mmin, num, tn, sex_o):
    """生成太乙計算結果"""
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
    wuyuan = ty.get_five_yuan_kook(num, tn) if num != 5 else ""
    homecal, awaycal, setcal = config.find_cal(yingyang, kook_num)
    zhao = {"男": "乾造", "女": "坤造"}.get(sex_o)
    life1 = ty.gongs_discription(sex_o)
    life2 = ty.twostar_disc(sex_o)
    lifedisc = ty.convert_gongs_text(life1, life2)
    lifedisc2 = ty.stars_descriptions_text(4, 0)
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
    yjxx = ty.yangjiu_xingxian(sex_o)
    blxx = ty.bailiu_xingxian(sex_o)
    ygua = ty.year_gua()[1]
    mgua = ty.month_gua()[1]
    dgua = ty.day_gua()[1]
    hgua = ty.hour_gua()[1]
    mingua = ty.minute_gua()[1]
    
    if num == 5:
        start_pt = genchart1[genchart1.index('''viewBox="''')+22:].split(" ")[1]
        render_svg(genchart1, int(start_pt))
        with st.expander("解釋"):
            st.title("《太乙命法》︰")
            st.markdown("【十二宮分析】")
            st.markdown(lifedisc)
            st.markdown("【太乙十六神落宮】")
            st.markdown(lifedisc2)
            st.markdown("【值卦】")
            st.markdown(f"年卦：{ygua}")
            st.markdown(f"月卦：{mgua}")
            st.markdown(f"日卦：{dgua}")
            st.markdown(f"時卦：{hgua}")
            st.markdown(f"分卦：{mingua}")
            st.markdown("【陽九行限】")
            st.markdown(format_text(yjxx))
            st.markdown("【百六行限】")
            st.markdown(format_text(blxx))
            st.title("《太乙秘書》︰")
            st.markdown(ts)
            st.title("史事記載︰")
            st.markdown(ch)
        print(f"{config.gendatetime(my, mm, md, mh, mmin)} {zhao} - {ty.taiyi_life(sex_o).get('性別')} - {config.taiyi_name(0)[0]} - {ty.accnum(0, 0)} | \n農曆︰{lunard} | {jieqi.jq(my, mm, md, mh, mmin)} |\n{gz} |\n{config.kingyear(my)} |\n{ty.kook(0, 0).get('文')} ({ttext.get('局式').get('年')}) | \n紀元︰{ttext.get('紀元')} | 主筭︰{homecal} 客筭︰{awaycal} |")
    else:
        start_pt2 = genchart2[genchart2.index('''viewBox="''')+22:].split(" ")[1]
        render_svg(genchart2, int(start_pt2))
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
            st.markdown(f"推太乙風雲飛鳥助戰︰{home_vs_away3}")
        print(f"{config.gendatetime(my, mm, md, mh, mmin)} | 積{config.taiyi_name(num)[0]}數︰{ty.accnum(num, tn)} | \n農曆︰{lunard} | {jieqi.jq(my, mm, md, mh, mmin)} |\n{gz} |\n{config.kingyear(my)} |\n{config.ty_method(tn)} - {ty.kook(num, tn).get('文')} ({ttext.get('局式').get('年')}) 五子元局:{wuyuan} | \n紀元︰{ttext.get('紀元')} | 主筭︰{homecal} 客筭︰{awaycal} 定筭︰{setcal} |")

# 太乙排盤
with tabs[0]:
    st.markdown("太乙排盤")
    output = st.empty()
    with st_capture(output.code):
        try:
            if manual:
                gen_results(my, mm, md, mh, mmin, num, tn, sex_o)
            elif instant:
                now = datetime.datetime.now(pytz.timezone('Asia/Hong_Kong'))
                gen_results(now.year, now.month, now.day, now.hour, now.minute, num, tn, sex_o)
        except Exception as e:
            st.error(f"生成盤局時發生錯誤：{str(e)}")

    # Add "截圖分享" button and screenshot functionality
    if manual or instant:
        st.button("截圖分享", key="screenshot_share")
        # Inject html2canvas library and JavaScript for screenshot
        screenshot_html = """
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <script>
        document.querySelectorAll('[data-testid="stButton"]').forEach(button => {
            if (button.textContent.includes("截圖分享")) {
                button.addEventListener("click", () => {
                    // Add a delay to ensure the DOM is fully rendered
                    setTimeout(() => {
                        const element = document.getElementById("capture-area");
                        if (!element) {
                            console.error("無法找到 capture-area 元素");
                            alert("無法找到要截圖的區域！");
                            return;
                        }
                        html2canvas(element, {
                            backgroundColor: "#1E1E1E",
                            useCORS: true,
                            allowTaint: true,
                            scale: 2, // Increase resolution for better quality
                            logging: true // Enable logging for debugging
                        }).then(canvas => {
                            const link = document.createElement("a");
                            link.download = "taiyi_screenshot.png";
                            link.href = canvas.toDataURL("image/png");
                            link.click();
                        }).catch(err => {
                            console.error("截圖失敗:", err);
                            alert("截圖失敗，請重試！錯誤信息：" + err.message);
                        });
                    }, 1000); // Delay of 1 second to ensure rendering
                });
            }
        });
        </script>
        """
        st.markdown(screenshot_html, unsafe_allow_html=True)
        
        # Display sharing instructions
        st.markdown("""
        **分享步驟：**
        1. 點擊「截圖分享」按鈕以上載圖片。
        2. 圖片下載後，手動將圖片分享到 WhatsApp 或 WeChat：
        """)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                '<a href="https://api.whatsapp.com/send" target="_blank"><button style="background-color:#25D366;color:white;padding:10px;border-radius:5px;border:none;cursor:pointer;">分享到 WhatsApp</button></a>',
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                '<a href="weixin://dl/chat" target="_blank"><button style="background-color:#7BB32E;color:white;padding:10px;border-radius:5px;border:none;cursor:pointer;">分享到 WeChat</button></a>',
                unsafe_allow_html=True
            )
        st.markdown("**注意：** 點擊分享按鈕後，請在 WhatsApp 或 WeChat 中選擇剛才下載的圖片進行分享。")
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
