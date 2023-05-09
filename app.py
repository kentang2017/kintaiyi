import streamlit as st
import pendulum as pdlm
from contextlib import contextmanager, redirect_stdout
from io import StringIO
from time import sleep
import streamlit as st
import streamlit.components.v1 as components
from kintaiyi import Taiyi
from historytext import chistory
from taiyidict import tengan_shiji, su_dist
from taiyimishu import taiyi_yingyang
import base64
import textwrap
import datetime, pytz
import os, urllib
import config
import jieqi

def get_file_content_as_string(path):
    url = 'https://raw.githubusercontent.com/kentang2017/kintaiyi/master/' + path
    response = urllib.request.urlopen(url)
    return response.read().decode("utf-8")

def render_svg(svg):
    """Renders the given svg string."""
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
    st.write(html, unsafe_allow_html=False)

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
        

st.set_page_config(layout="wide",page_title="太鳦 - 太乙排盘")
pan,example,disaster,guji,update,ins,tutorial = st.tabs([' 排盤 ', ' 史例 ', ' 災異 ' ,' 古籍 ',' 日誌 ', ' 說明 ', ' 教學 ' ])
#hide_st_style = """
#            <style>
#            #MainMenu {visibility: hidden;}
#            footer {visibility: hidden;}
#            header {visibility: hidden;}
#            </style>
#            """
#st.markdown(hide_st_style, unsafe_allow_html=True)

with st.sidebar:
    idate = st.text_input('輸入日期(如: 1997/8/8)', '')
    itime = st.text_input('輸入時間(如: 18:30)', '')
    option = st.selectbox( '起盤方式', (' 年計太乙 ', ' 月計太乙 ', ' 日計太乙 ', ' 時計太乙 ', ' 分計太乙 '))
    acum = st.selectbox( '太乙積年數', (' 太乙統宗 ', ' 太乙金鏡 ', ' 太乙淘金歌 ', ' 太乙局 '))
    num = dict(zip([' 年計太乙 ', ' 月計太乙 ', ' 日計太乙 ', ' 時計太乙 ', ' 分計太乙 '],[0,1,2,3,4])).get(option)
    tn = dict(zip([' 太乙統宗 ', ' 太乙金鏡 ', ' 太乙淘金歌 ',' 太乙局 '],[0,1,2,3])).get(acum)
    manual = st.button('手動盤')
    instant = st.button('即時盤')

with pan:
    output5 = st.empty()
    with st_capture(output5.code):
        try:
            if manual:
                p = str(idate).split("/")
                pp = str(itime).replace("：",":").split(":")
                y = int(p[0])
                m = int(p[1])
                d = int(p[2])
                h = int(pp[0])
                min = int(pp[1])
                ty = Taiyi(y,m,d,h,min)
                ttext = ty.pan(num,tn)
                kook = ty.kook(num,tn)
                homecal = ty.home_cal(num, tn)
                awaycal = ty.away_cal(num, tn)
                ed = ty.eight_door(num, tn)
                yc = ty.year_chin()
                day_su = ty.starhouse()
                yj = ty.yangjiu()
                bl = ty.baliu()
                g = ty.yeargua(tn)
                year_predict = "太歲" + yc  +"值宿，"+ su_dist.get(yc)
                sj_su_predict = "始擊落"+ ty.sf_num(num,tn)+ "宿，"+ su_dist.get(ty.sf_num(num,tn))
                tg_sj_su_predict = config.multi_key_dict_get (tengan_shiji, config.gangzhi(y,m,d,h,min)[0][0]).get(config.Ganzhiwuxing(ty.sf(num,tn)))
                three_door = ty.threedoors(num,tn)
                five_generals = ty.fivegenerals(num,tn)
                home_vs_away1 = ty.wc_n_sj(num,tn)
                home_vs_away2 = config.suenwl(num,tn)
                home_vs_away3 = ty.flybird_wl(num,tn)
                ts = taiyi_yingyang.get(kook.get('文')[0:2]).get(kook.get('數'))
                gz = "{}年 {}月 {}日 {}時".format(ttext.get("干支")[0], ttext.get("干支")[1], ttext.get("干支")[2], ttext.get("干支")[3])
                lunard = "{}年{}月{}日".format(config.lunar_date_d(y, m, d).get("年"), config.lunar_date_d(y, m, d).get("月"), config.lunar_date_d(y, m, d).get("日"))
                ch = chistory.get(y)
                if num == 3:
                   tynum = ty.accnum(num,tn)
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
                st.image(open("kook/"+yy+str(ttext.get("局式").get("數"))+".svg").read(), use_column_width=True)
                st.title("《太乙秘書》︰")
                st.markdown(ts)
                st.title("史事記載︰")
                st.markdown(ch)
                st.title("太乙盤局分析︰")
                st.markdown("太歲值宿斷事︰"+ year_predict)
                st.markdown("始擊值宿斷事︰"+ sj_su_predict)
                st.markdown("十天干歲始擊落宮預測︰"+ tg_sj_su_predict)
                st.markdown("推太乙在天外地內法︰"+ty.ty_gong_dist(num, tn))
                st.markdown("三門五將︰"+ three_door+five_generals )
                st.markdown("推主客相關︰"+ home_vs_away1)
                st.markdown("推多少以占勝負︰"+ ttext.get("推多少以占勝負"))
                st.markdown("推太乙風雲飛鳥助戰︰"+ home_vs_away3)
                st.title("九宮分野︰")
                st.image("pic/太乙九宮分野圖.jpg", use_column_width=True)
                print("{} |\n農曆︰{} | {} |\n{} |\n{} |\n{} - {} - {} ({}) | \n積{}數︰{} | \n紀元︰{} | 主筭︰{}  客筭︰{} |\n{}禽值年 | {}門值事 | {}卦值年  |\n 陽九︰{} 百六︰{} |\n{}{}{}\n{} \n\n".format(config.gendatetime(y,m,d,h), lunard, jieqi.jq(y,m,d,h),gz, config.kingyear(y), config.ty_method(tn), config.taiyi_name(num), ty.kook(num, tn).get("文"),  ttext.get("局式").get("年"), ty.taiyi_name(num)[0],tynum, ttext.get("紀元"), homecal, awaycal, yc, ed, g, yj, bl, ty.ty_gong_dist(num, tn), ty.threedoors(num, tn), ty.fivegenerals(num, tn), ty.geteightdoors(num, tn) ))
                expander = st.expander("原始碼")
                expander.write(str(ttext))
            else:
                st.empty()
        except ValueError:
            st.empty()
        
        if instant:
            now = datetime.datetime.now(pytz.timezone('Asia/Hong_Kong'))
            y = now.year
            m = now.month
            d = now.day
            h = now.hour
            min = now.minute
            ty = Taiyi(y,m,d,h,min)
            homecal = ty.home_cal(num, tn)
            awaycal = ty.away_cal(num, tn)
            ed = ty.eight_door(num, tn)
            yc = ty.year_chin()
            g = ty.yeargua(tn)
            ttext = Taiyi(y,m,d,h,min).pan(num,tn)
            kook = Taiyi(y,m,d,h,min).kook(num,tn)
            year_predict = "太歲" + yc  +"值宿，"+ su_dist.get(yc)
            sj_su_predict = "始擊落"+ ty.sf_num(num,tn)+ "宿，"+ su_dist.get(ty.sf_num(num,tn))
            tg_sj_su_predict = config.multi_key_dict_get (tengan_shiji, config.gangzhi(y,m,d,h,min)[0][0]).get(config.Ganzhiwuxing(ty.sf(num,tn)))
            three_door = ty.threedoors(num,tn)
            five_generals = ty.fivegenerals(num,tn)
            home_vs_away1 = ty.wc_n_sj(num,tn)
            home_vs_away2 = config.suenwl(num,tn)
            home_vs_away3 = ty.flybird_wl(num,tn)
            if num == 3:
               tynum = ty.accnum(num,tn)
            else: 
               tynum = ty.accnum(num,tn)
            yj = ty.yangjiu()
            bl = ty.baliu()
            ts = taiyi_yingyang.get(kook.get('文')[0:2]).get(kook.get('數'))
            gz = "{}年 {}月 {}日 {}時".format(ttext.get("干支")[0], ttext.get("干支")[1], ttext.get("干支")[2], ttext.get("干支")[3])
            lunard = "{}年{}月{}日".format(config.lunar_date_d(y, m, d).get("年"), config.lunar_date_d(y, m, d).get("月"), config.lunar_date_d(y, m, d).get("日"))
            ch = chistory.get(y)
            if ch == None:
               ch = ""
            r = list(map(lambda x:[x, x+25]  ,list(range(0,3000)[0::25])))
            tys = "".join([ts[r[i][0]:r[i][1]]+"\n" for i in range(0, int(len(ts) / 25+1))])
            if ttext.get("局式").get("文")[0] == "陽":
                yy = "yang"
            else:
                yy = "yin"
            st.image(open("kook/"+yy+str(ttext.get("局式").get("數"))+".svg").read(), use_column_width=True)
            st.title("《太乙秘書》︰")
            st.markdown(ts)
            st.title("史事記載︰")
            st.markdown(ch)
            st.title("太乙盤局分析︰")
            st.markdown("太歲值宿斷事︰"+ year_predict)
            st.markdown("始擊值宿斷事︰"+ sj_su_predict)
            st.markdown("十天干歲始擊落宮預測︰"+ tg_sj_su_predict)
            st.markdown("推太乙在天外地內法︰"+ty.ty_gong_dist(num, tn))
            st.markdown("三門五將︰"+ three_door+five_generals )
            st.markdown("推主客相關︰"+ home_vs_away1)
            st.markdown("推多少以占勝負︰"+ ttext.get("推多少以占勝負"))
            st.markdown("推太乙風雲飛鳥助戰︰"+ home_vs_away3)
            st.title("九宮分野︰")
            st.image("pic/太乙九宮分野圖.jpg", use_column_width=True)
            print("{} |\n農曆︰{} | {} |\n{} |\n{} |\n{} - {} - {} ({}) | \n積{}數︰{} | \n紀元︰{} | 主筭︰{}  客筭︰{} |\n{}禽值年 | {}門值事 | {}卦值年  |\n 陽九︰{} 百六︰{} |\n{}{}{}\n{} \n\n".format(config.gendatetime(y,m,d,h), lunard, jieqi.jq(y,m,d,h),  gz, config.kingyear(y), config.ty_method(tn), config.taiyi_name(num), ty.kook(num, tn).get("文"),  ttext.get("局式").get("年"), ty.taiyi_name(num)[0],tynum, ttext.get("紀元"), homecal, awaycal, yc, ed, g, yj, bl, ty.ty_gong_dist(num, tn), ty.threedoors(num, tn), ty.fivegenerals(num, tn), ty.geteightdoors(num, tn) ))
            expander = st.expander("原始碼")
            expander.write(str(ttext))
        else:
            st.empty()
        

with example:
    st.header('史例')
    st.markdown(get_file_content_as_string("example.md"))

with tutorial:
    st.header('教學')
    st.markdown(get_file_content_as_string("tutorial.md"))
    
with guji:
    st.header('古籍')
    st.markdown(get_file_content_as_string("guji.md"))
  
with update:
    st.header('更新日誌')
    st.markdown(get_file_content_as_string("update.md"))

with disaster:
    st.header('災害')
    st.markdown(get_file_content_as_string("disaster.md"))
   
with ins:
    st.header('使用說明')
    st.markdown(get_file_content_as_string("instruction.md"))
