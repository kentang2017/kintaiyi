import streamlit as st
import pendulum as pdlm
from contextlib import contextmanager, redirect_stdout
from io import StringIO
from time import sleep
import streamlit as st
import streamlit.components.v1 as components
from kintaiyi import Taiyi

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
with st.sidebar:
    pp_date=st.date_input("日期",pdlm.now(tz='Asia/Shanghai').date())
    pp_time=st.time_input("時間",pdlm.now(tz='Asia/Shanghai').time())
    
    inputy = st.text_input('年', '')
    inputm = st.text_input('月', '')
    inputd = st.text_input('日', '')
    inputh = st.text_input('時', '')
    inputf = st.text_input('分', '')
    option1 = st.selectbox( '起盤方式', (' 年計太乙 ', ' 月計太乙 ', ' 日計太乙 ', ' 時計太乙 ', ' 分計太乙 '))
    num1 = dict(zip([' 年計太乙 ', ' 月計太乙 ', ' 日計太乙 ', ' 時計太乙 ', ' 分計太乙 '],[0,1,2,3,4])).get(option)
    p = str(pp_date).split("-")
    pp = str(pp_time).split(":")
    y = int(p[0])
    m = int(p[1])
    d = int(p[2])
    h = int(pp[0])
    min = int(pp[1])
    if st.button('執行'):
        ttext1 = Taiyi(int(inputy),int(inputm),int(inputd),input(inputh),input(inputf)).pan(num1)
    else:
        print("    ")
    
 
st.header('太乙排盘')
option = st.selectbox( '起盤方式', (' 年計太乙 ', ' 月計太乙 ', ' 日計太乙 ', ' 時計太乙 ', ' 分計太乙 '))
num = dict(zip([' 年計太乙 ', ' 月計太乙 ', ' 日計太乙 ', ' 時計太乙 ', ' 分計太乙 '],[0,1,2,3,4])).get(option)
ttext = Taiyi(y,m,d,h,min).pan(num)
output5 = st.empty()
with st_capture(output5.code):
    print("{} |\n{} |\n太乙{} - {}\n".format(ttext.get("公元日期"), ttext.get("年號"), ttext.get("太乙計"),  ttext.get("局式").get("文")))
    #print(tys+"\n")
expander = st.expander("原始碼")
expander.write(str(ttext))
