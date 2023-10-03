import re
from lunar_python import Solar
from datetime import datetime
import opencc

def new_list(olist, o):
    a = olist.index(o)
    res1 = olist[a:] + olist[:a]
    return res1

jieqi_name = re.findall('..', '冬至小寒大寒立春雨水驚蟄春分清明穀雨立夏小滿芒種夏至小暑大暑立秋處暑白露秋分寒露霜降立冬小雪大雪')

def find_jq(year, month, day, hour, minute): #'{}-{}-{} {}:{}:00'
    lunar = Solar.fromYmd(year, month, day).getLunar()
    jieQi = lunar.getJieQiTable()
    converter = opencc.OpenCC('s2t.json')
    jq_list = [jieQi[k].toYmdHms() for k in lunar.getJieQiList()]
    jq_dict = {jieQi[k].toYmdHms():k for k in lunar.getJieQiList()}
    #'1895-12-22 09:38:44'
    target_datetime_str = '{}-{}-{} {}:{}:00'.format(str(year).zfill(4), str(month).zfill(2), str(day).zfill(2), str(hour).zfill(2), str(minute).zfill(2))
    target_datetime = datetime.strptime(target_datetime_str, '%Y-%m-%d %H:%M:%S')
    datetime_list = [datetime.strptime(s, '%Y-%m-%d %H:%M:%S') for s in jq_list]
    def closest(lst, K): 
        return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-K))] 
    closest_date = closest(datetime_list, target_datetime)
    
    def convert_key_to_value(object):
        jqeng = {"DONG_ZHI":"冬至", "XIAO_HAN":"小寒", "DA_HAN":"大寒", "LI_CHUN":"立春","YU_SHUI":"雨水","JING_ZHE":"驚蟄","DA_XUE":"大雪"}
        if object in jqeng:
            return jqeng[object]
        else:
            return object
    jie_qi = convert_key_to_value(jq_dict.get(str(closest_date)))
    t_o_f = target_datetime > closest_date
    if  t_o_f == True:
        return converter.convert(jie_qi) 
    if t_o_f == False and hour==closest_date.hour and minute!=closest_date.minute:
        return converter.convert(new_list(jieqi_name,jie_qi)[-1])
    if t_o_f == False and hour==closest_date.hour and minute==closest_date.minute:
        return converter.convert(jie_qi)
    if t_o_f == False and hour>closest_date.hour:
        return converter.convert(jie_qi)
    if t_o_f == False and hour<closest_date.hour:
        return converter.convert(new_list(jieqi_name,jie_qi)[-1])
    #if target_datetime > closest_date == False:
    #    return 
    
    
