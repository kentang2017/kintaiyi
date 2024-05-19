import streamlit as st
import pendulum as pdlm
import base64
import textwrap
import datetime, pytz
from contextlib import contextmanager, redirect_stdout
from io import StringIO
from time import sleep
import streamlit as st
import cn2an
from cn2an import an2cn
import streamlit.components.v1 as components
import kintaiyi
from historytext import chistory
from taiyidict import tengan_shiji, su_dist
from taiyimishu import taiyi_yingyang
import os, urllib
import config
import jieqi
from streamlit_modal import Modal
import json
#from streamlit_timeline import timeline
from streamlit_date_picker import date_range_picker, date_picker, PickerType

def timeline(data, height=800):
    if isinstance(data, str):
        data = json.loads(data)
    json_text = json.dumps(data) 
    source_param = 'timeline_json'
    source_block = f'var {source_param} = {json_text};'
    cdn_path = 'https://cdn.knightlab.com/libs/timeline3/latest'
    css_block = f'<link title="timeline-styles" rel="stylesheet" href="{cdn_path}/css/timeline.css">'
    js_block  = f'<script src="{cdn_path}/js/timeline.js"></script>'
    htmlcode = css_block + ''' 
    ''' + js_block + '''
        <div id='timeline-embed' style="width: 95%; height: '''+str(height)+'''px; margin: 1px;  "></div>
        <script type="text/javascript">
            var additionalOptions = {
                start_at_end: false, is_embed:true, default_bg_color: {r:14, g:17, b:23}
            }
            '''+source_block+'''
            timeline = new TL.Timeline('timeline-embed', '''+source_param+''', additionalOptions);
        </script>'''
    static_component = components.html(htmlcode, height=height,)
    return static_component

def render_svg(svg):
    """Renders the given svg string."""
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
    st.write(html, unsafe_allow_html=True)
    
def get_file_content_as_string(path):
    url = 'https://raw.githubusercontent.com/kentang2017/kintaiyi/master/' + path
    response = urllib.request.urlopen(url)
    return response.read().decode("utf-8")

def get_file_content_as_string1(path):
    url = 'https://raw.githubusercontent.com/kentang2017/kinliuren/master/' + path
    response = urllib.request.urlopen(url)
    return response.read().decode("utf-8")

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
       
st.set_page_config(layout="wide",page_title="堅太乙 - 太鳦排盘")
pan,ins,example,disaster,guji,update,tutorial,connect = st.tabs([' 🧮太乙排盤 ', ' 💬使用說明 ', ' 📜局數史例 ', ' 🔥災異統計 ' ,' 📚古籍書目 ',' 🆕更新日誌 ',' 🚀看盤要領 ', ' 🔗連結 '  ])

with st.sidebar:
    idate = st.text_input('輸入日期(如: 1997/8/8)', '')
    itime = st.text_input('輸入時間(如: 18:30)', '').replace("︰",":")
    #itime=st.time_input("時間",pdlm.now(tz='Asia/Shanghai').time())
    default_value = datetime.now()
    select_date = date_picker(picker_type=PickerType.time, value=default_value, key='date_picker')
    option = st.selectbox( '起盤方式', (' 年計太乙 ', ' 月計太乙 ', ' 日計太乙 ', ' 時計太乙 ', ' 分計太乙 ', ' 太乙命法 '))
    acum = st.selectbox( '太乙積年數', (' 太乙統宗 ', ' 太乙金鏡 ', ' 太乙淘金歌 ', ' 太乙局 '))
    sex_o = st.selectbox( '太乙命法性別', ('男', '女'))
    num = dict(zip([' 年計太乙 ', ' 月計太乙 ', ' 日計太乙 ', ' 時計太乙 ', ' 分計太乙 ', ' 太乙命法 '],[0,1,2,3,4,5])).get(option)
    tn = dict(zip([' 太乙統宗 ', ' 太乙金鏡 ', ' 太乙淘金歌 ',' 太乙局 ' ],[0,1,2,3])).get(acum)
    manual = st.button('手動盤')
    instant = st.button('即時盤')



with pan:
    output5 = st.empty()  
    with st_capture(output5.code):
        try:
            if manual:
                if num == 0 & len(idate) <= 4:
                    idate = idate + "/3/3"
                p = str(idate).split("/")
                pp = str(itime).split(":")
                my = int(p[0])
                mm = int(p[1])
                md = int(p[2])
                mh = int(pp[0])
                mmin = int(pp[1])
                ty = kintaiyi.Taiyi(my,mm,md,mh,mmin)
                accum_value = ty.accnum(4,0)
                if num != 5:
                    ttext = ty.pan(num,tn)
                    kook = ty.kook(num,tn)
                    kook_num = kook.get("數")
                    yingyang = kook.get("文")[0]
                    #homecal = ty.home_cal(num, tn)
                    #awaycal = ty.away_cal(num, tn)
                    homecal = config.find_cal(yingyang, kook_num)[0]
                    awaycal =  config.find_cal(yingyang, kook_num)[1]
                    setcal =  config.find_cal(yingyang, kook_num)[2]
                    sj_su_predict = "始擊落"+ ty.sf_num(num,tn)+ "宿，"+ su_dist.get(ty.sf_num(num,tn))
                    tg_sj_su_predict = config.multi_key_dict_get (tengan_shiji, config.gangzhi(my,mm,md,mh,min)[0][0]).get(config.Ganzhiwuxing(ty.sf(num,tn)))
                    three_door = ty.threedoors(num,tn)
                    five_generals = ty.fivegenerals(num,tn)
                    home_vs_away1 = ty.wc_n_sj(num,tn)
                genchart = ty.gen_gong(num, tn)
                if num == 5:
                    ttext = ty.pan(0,0)
                    kook = ty.kook(0,0)
                    kook_num = kook.get("數")
                    yingyang = kook.get("文")[0]
                    #homecal = ty.home_cal(num, tn)
                    #awaycal = ty.away_cal(num, tn)
                    homecal = config.find_cal(yingyang, kook_num)[0]
                    awaycal =  config.find_cal(yingyang, kook_num)[1]
                    setcal =  config.find_cal(yingyang, kook_num)[2]
                    genchart = ty.gen_life_gong(sex_o)
                    sj_su_predict = "始擊落"+ ty.sf_num(0, 0)+ "宿，"+ su_dist.get(ty.sf_num(0, 0))
                    tg_sj_su_predict = config.multi_key_dict_get (tengan_shiji, config.gangzhi(my,mm,md,mh,min)[0][0]).get(config.Ganzhiwuxing(ty.sf(0,0)))
                    three_door = ty.threedoors(0, 0)
                    five_generals = ty.fivegenerals(0, 0)
                    home_vs_away1 = ty.wc_n_sj(0, 0)
                    zhao = {"男":"乾造","女":"坤造"}.get(sex_o)
                    life1 = ty.gongs_discription(sex_o)
                    life2 = ty.twostar_disc(sex_o)
                    lifedisc = ty.convert_gongs_text(life1, life2)
                    lifedisc2 = ty.stars_descriptions_text(4,0)
                    
                ed = ttext.get("八門值事")
                yc = ty.year_chin()
                yj = ttext.get("陽九")
                bl = ttext.get("百六")
                g = ty.yeargua(tn)
                year_predict = "太歲" + yc  +"值宿，"+ su_dist.get(yc)
                home_vs_away3 = ttext.get("推太乙風雲飛鳥助戰法")
                ts = taiyi_yingyang.get(kook.get('文')[0:2]).get(kook.get('數'))
                gz = "{}年 {}月 {}日 {}時 {}分".format(ttext.get("干支")[0], ttext.get("干支")[1], ttext.get("干支")[2], ttext.get("干支")[3], ttext.get("干支")[4])
                lunard = "{}{}月{}日".format(  cn2an.transform(str(config.lunar_date_d(my, mm, md).get("年"))+"年", "an2cn"), an2cn(config.lunar_date_d(my, mm, md).get("月")), an2cn(config.lunar_date_d(my, mm, md).get("日")))
                ch = chistory.get(my)
                if num == 3:
                   tynum = ty.accnum(num,tn)
                if num == 5:
                   tynum = ty.accnum(0,0)
                else: 
                   tynum = ty.accnum(num,tn)
                if ch == None:
                   ch = ""
                r = list(map(lambda x:[x, x+25]  ,list(range(0,3000)[0::25])))
                tys = "".join([ts[r[i][0]:r[i][1]]+"\n" for i in range(0, int(len(ts) / 25+1))])
                if ttext.get("局式").get("文")[0] == "陽":
                    yy = "yang"
                else:
                    yy = "yin"
                render_svg(genchart)
                with st.expander("解釋"):
                    if num == 5:
                        st.title("《太乙命法》︰")
                        st.markdown("【十二宮分析】")
                        st.markdown(lifedisc)
                        st.markdown("【太乙十六神落宮】")
                        st.markdown(lifedisc2)
                    st.title("《太乙秘書》︰")
                    st.markdown(ts)
                    st.title("史事記載︰")
                    st.markdown(ch)
                    st.title("太乙盤局分析︰")
                    #st.markdown("推雷公入水︰"+ttext.get("推雷公入水"))
                    #st.markdown("推臨津問道︰"+ttext.get("推臨津問道"))
                    #st.markdown("推獅子反擲︰"+ttext.get("推獅子反擲"))
                    #st.markdown("推白雲捲空︰"+ttext.get("推白雲捲空"))
                    #st.markdown("推猛虎相拒︰"+ttext.get("推猛虎相拒"))
                    #st.markdown("推白龍得雲︰"+ttext.get("推白龍得雲"))
                    #st.markdown("推回軍無言︰"+ttext.get("推回軍無言"))
                    st.markdown("太歲值宿斷事︰"+ year_predict)
                    st.markdown("始擊值宿斷事︰"+ sj_su_predict)
                    st.markdown("十天干歲始擊落宮預測︰"+ tg_sj_su_predict)
                    if num == 5:
                        st.markdown("推太乙在天外地內法︰"+ty.ty_gong_dist(0, 0))
                    if num != 5:
                        st.markdown("推太乙在天外地內法︰"+ty.ty_gong_dist(num, tn))
                    st.markdown("三門五將︰"+ three_door+five_generals )
                    st.markdown("推主客相關︰"+ home_vs_away1)
                    st.markdown("推多少以占勝負︰"+ ttext.get("推多少以占勝負"))
                    st.markdown("推陰陽以占厄會︰"+ ttext.get("推陰陽以占厄會"))
                    st.markdown("推太乙風雲飛鳥助戰︰"+ home_vs_away3)
                    #st.title("九宮分野︰")
                    #st.image("pic/太乙九宮分野圖.jpg", use_column_width=True)
                if num != 5:
                    print("{} | 積{}數︰{} | \n農曆︰{} | {} |\n{} |\n{} |\n{} - {} - {} ({}) | \n紀元︰{} | 主筭︰{} 客筭︰{} 定筭︰{} |\n{}禽值年 | {}門值事 | \n{}卦值年 | 太乙統運卦︰{} | \n ".format(config.gendatetime(my,mm,md,mh,mmin), config.taiyi_name(num)[0],tynum, lunard, jieqi.jq(my,mm,md,mh,mmin),gz, config.kingyear(my), config.ty_method(tn), config.taiyi_name(num), ty.kook(num, tn).get("文") ,ttext.get("局式").get("年"),   ttext.get("紀元"), homecal, awaycal, setcal, yc, ed, g, config.find_gua(config.lunar_date_d(my, mm, md).get("年"))  ))
                    st.markdown("""
                                <style>
                                    div[data-testid="column"] {
                                        width: fit-content !important;
                                        flex: unset;
                                    }
                                    div[data-testid="column"] * {
                                        width: fit-content !important;
                                    }
                                </style>
                                """, unsafe_allow_html=True)
                    col1, col2, col3 = st.columns([1,1,1])
                    with col1:
                       st.button('1')
                    with col2:
                       st.button('2')
                    with col3:
                       st.button('3')
                if num == 5:
                    print("{} {}-{} | \n積{}數︰{} | \n農曆︰{} | {} |\n{} |\n{} |\n太乙人道命法 - {} ({}) | \n紀元︰{} | 主筭︰{} 客筭︰{} |\n{}禽值年 | {}門值事 | \n{}卦值年 | 太乙統運卦︰{} | \n".format(config.gendatetime(my,mm,md,mh,mmin), zhao,ty.taiyi_life(sex_o).get("性別") ,config.taiyi_name(0)[0],tynum, lunard, jieqi.jq(my,mm,md,mh,mmin),gz, config.kingyear(my), ty.kook(0,0).get("文") ,ttext.get("局式").get("年"),   ttext.get("紀元"), homecal, awaycal, yc, ed, g, config.find_gua(config.lunar_date_d(my, mm, md).get("年")) ))
            else:
                output5 = st.empty()
        except ValueError:
            output5 = st.empty()
            now = datetime.datetime.now(pytz.timezone('Asia/Hong_Kong'))
            y = now.year
            m = now.month
            d = now.day
            h = now.hour
            min = now.minute
            ty = kintaiyi.Taiyi(y,m,d,h,min)
            num = 0
            ttext = ty.pan(num,tn)
            kook = ty.kook(num,tn)
            kook_num = kook.get("數")
            yingyang = kook.get("文")[0]
            homecal = config.find_cal(yingyang, kook_num)[0]
            awaycal =  config.find_cal(yingyang, kook_num)[1]
            setcal =  config.find_cal(yingyang, kook_num)[2]
            #homecal = ty.home_cal(num, tn)
            #awaycal = ty.away_cal(num, tn)
            genchart = ty.gen_gong(num, tn)
            sj_su_predict = "始擊落"+ ty.sf_num(num,tn)+ "宿，"+ su_dist.get(ty.sf_num(num,tn))
            tg_sj_su_predict = config.multi_key_dict_get (tengan_shiji, config.gangzhi(y,m,d,h,min)[0][0]).get(config.Ganzhiwuxing(ty.sf(num,tn)))
            three_door = ty.threedoors(num,tn)
            five_generals = ty.fivegenerals(num,tn)
            home_vs_away1 = ty.wc_n_sj(num,tn)
            ed = ttext.get("八門值事")
            yc = ty.year_chin()
            g = ty.yeargua(tn)
            year_predict = "太歲" + yc  +"值宿，"+ su_dist.get(yc)
            home_vs_away3 = ttext.get("推太乙風雲飛鳥助戰法")
            if num == 3:
               tynum = ty.accnum(num,tn)
            if num == 5:
               tynum = ty.accnum(0,0)
            else: 
               tynum = ty.accnum(num,tn)
            yj = ttext.get("陽九")
            bl = ttext.get("百六")
            ts = taiyi_yingyang.get(kook.get('文')[0:2]).get(kook.get('數'))
            gz = "{}年 {}月 {}日 {}時 {}分".format(ttext.get("干支")[0], ttext.get("干支")[1], ttext.get("干支")[2], ttext.get("干支")[3], ttext.get("干支")[4])
            lunard = "{}{}月{}日".format(  cn2an.transform(str(config.lunar_date_d(y, m, d).get("年"))+"年", "an2cn"), an2cn(config.lunar_date_d(y, m, d).get("月")), an2cn(config.lunar_date_d(y, m, d).get("日")))
            ch = chistory.get(y)
            if ch == None:
               ch = ""
            r = list(map(lambda x:[x, x+25]  ,list(range(0,3000)[0::25])))
            tys = "".join([ts[r[i][0]:r[i][1]]+"\n" for i in range(0, int(len(ts) / 25+1))])
            if ttext.get("局式").get("文")[0] == "陽":
                yy = "yang"
            else:
                yy = "yin"
            render_svg(genchart)
            with st.expander("解釋"):
            # Create a button to trigger the pop-up
            #st.image("https://raw.githubusercontent.com/kentang2017/kintaiyi/a76abf4958ea48accb1f3b8b8c7cfd96710ea67f/kook/"+yy+str(ttext.get("局式").get("數"))+".svg")
                st.title("《太乙秘書》︰")
                st.markdown(ts)
                st.title("史事記載︰")
                st.markdown(ch)
                st.title("太乙盤局分析︰")
                #st.markdown("推雷公入水︰"+ttext.get("推雷公入水"))
                #st.markdown("推臨津問道︰"+ttext.get("推臨津問道"))
                #st.markdown("推獅子反擲︰"+ttext.get("推獅子反擲"))
                #st.markdown("推白雲捲空︰"+ttext.get("推白雲捲空"))
                #st.markdown("推猛虎相拒︰"+ttext.get("推猛虎相拒"))
                #st.markdown("推白龍得雲︰"+ttext.get("推白龍得雲"))
                #st.markdown("推回軍無言︰"+ttext.get("推回軍無言"))
                st.markdown("太歲值宿斷事︰"+ year_predict)
                st.markdown("始擊值宿斷事︰"+ sj_su_predict)
                st.markdown("十天干歲始擊落宮預測︰"+ tg_sj_su_predict)
                if num == 5:
                    st.markdown("推太乙在天外地內法︰"+ty.ty_gong_dist(0, 0))
                if num != 5:
                    st.markdown("推太乙在天外地內法︰"+ty.ty_gong_dist(num, tn))
                st.markdown("三門五將︰"+ three_door+five_generals )
                st.markdown("推主客相關︰"+ home_vs_away1)
                st.markdown("推多少以占勝負︰"+ ttext.get("推多少以占勝負"))
                st.markdown("推陰陽以占厄會︰"+ ttext.get("推陰陽以占厄會"))
                st.markdown("推太乙風雲飛鳥助戰︰"+ home_vs_away3)
                

                #st.title("九宮分野︰")
                #st.image("pic/太乙九宮分野圖.jpg", use_column_width=True)
            if num != 5:
                print("{} | 積{}數︰{} |\n農曆︰{} | {} |\n{} |\n{} |\n{} - {} - {} ({}) |\n紀元︰{} | 主筭︰{} 客筭︰{} 定筭︰{} |\n{}禽值年 | {}門值事 | \n{}卦值年 | 太乙統運卦︰{} | \n".format(config.gendatetime(y,m,d,h,min),config.taiyi_name(num)[0],tynum, lunard, jieqi.jq(y,m,d,h,min), gz, config.kingyear(y), config.ty_method(tn), config.taiyi_name(num), ty.kook(num, tn).get("文"), ttext.get("局式").get("年"),  ttext.get("紀元"), homecal, awaycal, setcal, yc, ed, g, config.find_gua(config.lunar_date_d(y, m, d).get("年")) ))
            if num == 5:
                print("{} {}-{}| \n積{}數︰{} |\n農曆︰{} | {} |\n{} |\n{} |\n太乙人道命法 - {} ({}) |\n紀元︰{} | 主筭︰{} 客筭︰{} 定筭︰{} |\n{}禽值年 | {}門值事 | \n{}卦值年 | 太乙統運卦︰{} | \n{}".format(config.gendatetime(y,m,d,h,min),config.taiyi_name(0)[0], zhao,ty.taiyi_life(sex_o).get("性別") ,tynum, lunard, jieqi.jq(y,m,d,h,min), gz, config.kingyear(y), ty.kook(0, 0).get("文"), ttext.get("局式").get("年"),  ttext.get("紀元"), homecal, awaycal, setcal, yc, ed, g, config.find_gua(config.lunar_date_d(y, m, d).get("年"))))

        
        if instant:
            output5 = st.empty()
            now = datetime.datetime.now(pytz.timezone('Asia/Hong_Kong'))
            y = now.year
            m = now.month
            d = now.day
            h = now.hour
            min = now.minute
            ty = kintaiyi.Taiyi(y,m,d,h,min)
            if num != 5:
                ttext = ty.pan(num,tn)
                kook = ty.kook(num,tn)
                kook_num = kook.get("數")
                yingyang = kook.get("文")[0]
                homecal = config.find_cal(yingyang, kook_num)[0]
                awaycal =  config.find_cal(yingyang, kook_num)[1]
                setcal =  config.find_cal(yingyang, kook_num)[2]
                #homecal = ty.home_cal(num, tn)
                #awaycal = ty.away_cal(num, tn)
                sj_su_predict = "始擊落"+ ty.sf_num(num,tn)+ "宿，"+ su_dist.get(ty.sf_num(num,tn))
                tg_sj_su_predict = config.multi_key_dict_get (tengan_shiji, config.gangzhi(y,m,d,h,min)[0][0]).get(config.Ganzhiwuxing(ty.sf(num,tn)))
                three_door = ty.threedoors(num,tn)
                five_generals = ty.fivegenerals(num,tn)
                home_vs_away1 = ty.wc_n_sj(num,tn)
            genchart = ty.gen_gong(num, tn)
            if num == 5:
                ttext = ty.pan(0,0)
                kook = ty.kook(0,0)
                #homecal = ty.home_cal(0, 0)
                #awaycal = ty.away_cal(0, 0)
                kook_num = kook.get("數")
                yingyang = kook.get("文")[0]
                homecal = config.find_cal(yingyang, kook_num)[0]
                awaycal =  config.find_cal(yingyang, kook_num)[1]
                setcal =  config.find_cal(yingyang, kook_num)[2]
                genchart = ty.gen_life_gong(sex_o)
                sj_su_predict = "始擊落"+ ty.sf_num(0, 0)+ "宿，"+ su_dist.get(ty.sf_num(0, 0))
                tg_sj_su_predict = config.multi_key_dict_get (tengan_shiji, config.gangzhi(y,m,d,h,min)[0][0]).get(config.Ganzhiwuxing(ty.sf(0,0)))
                three_door = ty.threedoors(0, 0)
                five_generals = ty.fivegenerals(0, 0)
                home_vs_away1 = ty.wc_n_sj(0, 0)
                zhao = {"男":"乾造","女":"坤造"}.get(sex_o)
                life1 = ty.gongs_discription(sex_o)
                life2 = ty.twostar_disc(sex_o)
                lifedisc = ty.convert_gongs_text(life1, life2)
                lifedisc2 = ty.stars_descriptions_text(3,0)
            ed = ttext.get("八門值事")
            yc = ty.year_chin()
            g = ty.yeargua(tn)
            year_predict = "太歲" + yc  +"值宿，"+ su_dist.get(yc)
            home_vs_away3 = ttext.get("推太乙風雲飛鳥助戰法")
            if num == 3:
               tynum = ty.accnum(num,tn)
            if num == 5:
               tynum = ty.accnum(0,0)
            else: 
               tynum = ty.accnum(num,tn)
            yj = ttext.get("陽九")
            bl = ttext.get("百六")
            ts = taiyi_yingyang.get(kook.get('文')[0:2]).get(kook.get('數'))
            gz = "{}年 {}月 {}日 {}時 {}分".format(ttext.get("干支")[0], ttext.get("干支")[1], ttext.get("干支")[2], ttext.get("干支")[3], ttext.get("干支")[4])
            lunard = "{}{}月{}日".format(  cn2an.transform(str(config.lunar_date_d(y, m, d).get("年"))+"年", "an2cn"), an2cn(config.lunar_date_d(y, m, d).get("月")), an2cn(config.lunar_date_d(y, m, d).get("日")))
            ch = chistory.get(y)
            if ch == None:
               ch = ""
            r = list(map(lambda x:[x, x+25]  ,list(range(0,3000)[0::25])))
            tys = "".join([ts[r[i][0]:r[i][1]]+"\n" for i in range(0, int(len(ts) / 25+1))])
            if ttext.get("局式").get("文")[0] == "陽":
                yy = "yang"
            else:
                yy = "yin"
            render_svg(genchart)
            with st.expander("解釋"):
            # Create a button to trigger the pop-up
            #st.image("https://raw.githubusercontent.com/kentang2017/kintaiyi/a76abf4958ea48accb1f3b8b8c7cfd96710ea67f/kook/"+yy+str(ttext.get("局式").get("數"))+".svg")
                if num == 5:
                    st.title("《太乙命法》︰")
                    st.markdown("【十二宮分析】")
                    st.markdown(lifedisc)
                    st.markdown("【太乙十六神落宮】")
                    st.markdown(lifedisc2)
                st.title("《太乙秘書》︰")
                st.markdown(ts)
                st.title("史事記載︰")
                st.markdown(ch)
                st.title("太乙盤局分析︰")
                #st.markdown("推雷公入水︰"+ttext.get("推雷公入水"))
                #st.markdown("推臨津問道︰"+ttext.get("推臨津問道"))
                #st.markdown("推獅子反擲︰"+ttext.get("推獅子反擲"))
                #st.markdown("推白雲捲空︰"+ttext.get("推白雲捲空"))
                #st.markdown("推猛虎相拒︰"+ttext.get("推猛虎相拒"))
                #st.markdown("推白龍得雲︰"+ttext.get("推白龍得雲"))
                #st.markdown("推回軍無言︰"+ttext.get("推回軍無言"))
                st.markdown("太歲值宿斷事︰"+ year_predict)
                st.markdown("始擊值宿斷事︰"+ sj_su_predict)
                st.markdown("十天干歲始擊落宮預測︰"+ tg_sj_su_predict)
                if num == 5:
                    st.markdown("推太乙在天外地內法︰"+ty.ty_gong_dist(0, 0))
                if num != 5:
                    st.markdown("推太乙在天外地內法︰"+ty.ty_gong_dist(num, tn))
                st.markdown("三門五將︰"+ three_door+five_generals )
                st.markdown("推主客相關︰"+ home_vs_away1)
                st.markdown("推多少以占勝負︰"+ ttext.get("推多少以占勝負"))
                st.markdown("推陰陽以占厄會︰"+ ttext.get("推陰陽以占厄會"))
                st.markdown("推太乙風雲飛鳥助戰︰"+ home_vs_away3)
                

                #st.title("九宮分野︰")
                #st.image("pic/太乙九宮分野圖.jpg", use_column_width=True)
            if num != 5:
                print("{} | 積{}數︰{} |\n農曆︰{} | {} |\n{} |\n{} |\n{} - {} - {} ({}) |\n紀元︰{} | 主筭︰{} 客筭︰{} |\n{}禽值年 | {}門值事 | \n{}卦值年 | 太乙統運卦︰{} | \n".format(config.gendatetime(y,m,d,h,min),config.taiyi_name(num)[0],tynum, lunard, jieqi.jq(y,m,d,h,min), gz, config.kingyear(y), config.ty_method(tn), config.taiyi_name(num), ty.kook(num, tn).get("文"), ttext.get("局式").get("年"),  ttext.get("紀元"), homecal, awaycal, yc, ed, g, config.find_gua(config.lunar_date_d(y, m, d).get("年")) ))
            if num == 5:
                print("{} {}-{}| \n積{}數︰{} |\n農曆︰{} | {} |\n{} |\n{} |\n太乙人道命法 - {} ({}) |\n紀元︰{} | 主筭︰{} 客筭︰{} |\n{}禽值年 | {}門值事 | \n{}卦值年 | 太乙統運卦︰{} | \n{}".format(config.gendatetime(y,m,d,h,min),config.taiyi_name(0)[0], zhao,ty.taiyi_life(sex_o).get("性別") ,tynum, lunard, jieqi.jq(y,m,d,h,min), gz, config.kingyear(y), ty.kook(0, 0).get("文"), ttext.get("局式").get("年"),  ttext.get("紀元"), homecal, awaycal, yc, ed, g, config.find_gua(config.lunar_date_d(y, m, d).get("年"))))

        
with connect:
    st.header('連結')
    st.markdown(get_file_content_as_string1("update.md"), unsafe_allow_html=True)
            
with example:
    st.header('太乙局數史例')
    with open('example.json', "r") as f:
        data = f.read()
    # render timeline
    timeline(data, height=600)
    with st.expander("列表"):
        get_file_content_as_string("example.md")

with tutorial:
    st.header('看盤要領')
    st.markdown(get_file_content_as_string("tutorial.md"),  unsafe_allow_html=True)
    
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
