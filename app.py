import streamlit as st
import pendulum as pdlm
from contextlib import contextmanager, redirect_stdout
from io import StringIO
from time import sleep
import streamlit as st
import streamlit.components.v1 as components
from kintaiyi import Taiyi
from historytext import chistory
from taiyimishu import taiyi_yingyang
import base64
import textwrap
import datetime, pytz



def render_svg(svg):
    """Renders the given svg string."""
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
    st.write(html, unsafe_allow_html=True)

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
        
st.set_page_config(layout="wide",page_title="太鳦太乙")
st.title('太鳦太乙排盘')
idate = st.text_input('輸入日期(如: 1997/8/8)', '')
itime = st.text_input('輸入時間(如: 18:30)', '')
option = st.selectbox( '起盤方式', (' 年計太乙 ', ' 月計太乙 ', ' 日計太乙 ', ' 時計太乙 ', ' 分計太乙 '))
num = dict(zip([' 年計太乙 ', ' 月計太乙 ', ' 日計太乙 ', ' 時計太乙 ', ' 分計太乙 '],[0,1,2,3,4])).get(option)
output5 = st.empty()
with st_capture(output5.code):
    col1, col2 = st.columns(2)
    with col1:
        if st.button('手動'):
            p = str(idate).split("/")
            pp = str(itime).replace("：",":").split(":")
            y = int(p[0])
            m = int(p[1])
            d = int(p[2])
            h = int(pp[0])
            min = int(pp[1])
            ty = Taiyi(y,m,d,h,min)
            ttext = Taiyi(y,m,d,h,min).pan(num)
            kook = Taiyi(y,m,d,h,min).kook(num)
            ts = taiyi_yingyang.get(kook.get('文')[0:2]).get(kook.get('數'))
            gz = "{}年 {}月 {}日 {}時".format(ttext.get("干支")[0], ttext.get("干支")[1], ttext.get("干支")[2], ttext.get("干支")[3])
            ch = chistory.get(y)
            r = list(map(lambda x:[x, x+25]  ,list(range(0,3000)[0::25])))
            tys = "".join([ts[r[i][0]:r[i][1]]+"\n" for i in range(0, int(len(ts) / 25+1))])
            #try:
                #cys = "".join([ch[r[i][0]:r[i][1]]+"\n" for i in range(0, int(len(ch) / 25+1))])
            #except (TypeError,IndexError):
                #cys = ""
            if ttext.get("局式").get("文")[0] == "陽":
                yy = "yang"
            else:
                yy = "yin"
            try:
                st.image(open("kook/"+yy+str(ttext.get("局式").get("數"))+".svg").read(), use_column_width=True)
                st.title("《太乙秘書》︰")
                st.markdown(ts)
                st.title("史事記載︰")
                st.markdown(ch)
            except (FileNotFoundError,IndexError, ValueError):
                st.empty()
                st.title("《太乙秘書》︰")
                st.markdown(ts)
                st.title("史事記載︰")
                st.markdown(ch)
            print("{} |\n{} |\n{} |\n太乙{} - {} | 積年數︰{} | \n紀元︰{} | \n\n".format(ttext.get("公元日期"), gz, ttext.get("年號"), ttext.get("太乙計"),  ttext.get("局式").get("文"), ty.accnum(num), ttext.get("紀元")))
            expander = st.expander("原始碼")
            expander.write(str(ttext))
        else:
            st.empty()
    with col2:
         if st.button('即時'):
            now = datetime.datetime.now(pytz.timezone('Asia/Hong_Kong'))
            y = now.year
            m = now.month
            d = now.day
            h = now.hour
            min = now.minute
            ty = Taiyi(y,m,d,h,min)
            ttext = Taiyi(y,m,d,h,min).pan(num)
            kook = Taiyi(y,m,d,h,min).kook(num)
            ts = taiyi_yingyang.get(kook.get('文')[0:2]).get(kook.get('數'))
            gz = "{}年 {}月 {}日 {}時".format(ttext.get("干支")[0], ttext.get("干支")[1], ttext.get("干支")[2], ttext.get("干支")[3])
            ch = chistory.get(y)
            r = list(map(lambda x:[x, x+25]  ,list(range(0,3000)[0::25])))
            tys = "".join([ts[r[i][0]:r[i][1]]+"\n" for i in range(0, int(len(ts) / 25+1))])
            #try:
                #cys = "".join([ch[r[i][0]:r[i][1]]+"\n" for i in range(0, int(len(ch) / 25+1))])
            #except (TypeError,IndexError):
                #cys = ""
            if ttext.get("局式").get("文")[0] == "陽":
                yy = "yang"
            else:
                yy = "yin"
            try:
                render_svg("tykook/typan.svg")
                st.image(open("kook/"+yy+str(ttext.get("局式").get("數"))+".svg").read(), use_column_width=True)
                st.title("《太乙秘書》︰")
                st.markdown(ts)
                st.title("史事記載︰")
                st.markdown(ch)
            except (FileNotFoundError,IndexError, ValueError):
                st.empty()
                st.title("《太乙秘書》︰")
                st.markdown(ts)
                st.title("史事記載︰")
                st.markdown(ch)
            print("{} |\n{} |\n{} |\n太乙{} - {} | 積年數︰{} | \n紀元︰{} | \n\n".format(ttext.get("公元日期"), gz, ttext.get("年號"), ttext.get("太乙計"),  ttext.get("局式").get("文"), ty.accnum(num), ttext.get("紀元")))
            expander = st.expander("原始碼")
            expander.write(str(ttext))
         else:
            st.empty()
    #print(tys+"\n")


#import itertools
#su = list('角亢氐房心尾箕斗牛女虛危室壁奎婁胃昴畢觜參井鬼柳星張翼軫')
#numlist = [13,9,16,5,5,17,10,24,7,11,25,18,17,10,17,13,14,11,16,1,9,30,3,14,7,19,19,18]
#list(itertools.chain.from_iterable([[su[i]]*numlist[i] for i in range(0,28)]))
