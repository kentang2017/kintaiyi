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

st.header('太乙排盘')
idate = st.text_input('輸入日期(如: 1997/8/8)', '')
itime = st.text_input('輸入時間(如: 18:30)', '')
option = st.selectbox( '起盤方式', (' 年計太乙 ', ' 月計太乙 ', ' 日計太乙 ', ' 時計太乙 ', ' 分計太乙 '))
num = dict(zip([' 年計太乙 ', ' 月計太乙 ', ' 日計太乙 ', ' 時計太乙 ', ' 分計太乙 '],[0,1,2,3,4])).get(option)
output5 = st.empty()
with st_capture(output5.code):
    if st.button('執行'):
        p = str(idate).split("/")
        pp = str(itime).split(":")
        y = int(p[0])
        m = int(p[1])
        d = int(p[2])
        h = int(pp[0])
        min = int(pp[1])
        ty = Taiyi(y,m,d,h,min)
        ttext = Taiyi(y,m,d,h,min).pan(num)
        print("{} |\n{} |\n太乙{} - {} | 積年數︰{} \n".format(ttext.get("公元日期"), ttext.get("年號"), ttext.get("太乙計"),  ttext.get("局式").get("文"), ty.accnum(num))
        expander = st.expander("原始碼")
        expander.write(str(ttext))
    else:
        print("    ")
    #print(tys+"\n")

