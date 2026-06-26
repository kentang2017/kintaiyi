# -*- coding: utf-8 -*-
"""
Created on Tue May  9 20:32:01 2023

@author: kentang
"""

import re
import math
import datetime
from itertools import cycle, repeat
import sxtwl
from sxtwl import fromSolar
from . import config

jqmc = ['小寒', '大寒', '立春', '雨水', '驚蟄', '春分', '清明', '穀雨', '立夏', '小滿', '芒種', '夏至', '小暑', '大暑', '立秋', '處暑', '白露', '秋分', '寒露', '霜降', '立冬', '小雪', '大雪', '冬至']
tian_gan = '甲乙丙丁戊己庚辛壬癸'
di_zhi = '子丑寅卯辰巳午未申酉戌亥'


def _safe_datetime(year, month, day, hour=0, minute=0):
    """構建 datetime，支援負數年份。
    Python datetime 不支援 year < 1，所以對 year < 1 的情況使用 sxtwl JD 替代。"""
    if year >= 1:
        try:
            return datetime.datetime(year, month, day, hour, minute)
        except (ValueError, OverflowError):
            pass
    # 對於 year < 1，用 JD 值封裝成一個可比較的物件
    t = sxtwl.Time(year, month, day, hour, minute, 0)
    return _JDEpoch(sxtwl.toJD(t))


class _JDEpoch:
    """Julian Day 封裝物件，用於取代不支援負年份的 datetime.datetime。
    支援比較運算（<, <=, >, >=, ==, !=）。"""
    __slots__ = ('jd',)

    def __init__(self, jd):
        self.jd = jd

    def __le__(self, other):
        return self.jd <= other.jd if isinstance(other, _JDEpoch) else self.jd <= _to_jd(other)

    def __lt__(self, other):
        return self.jd < other.jd if isinstance(other, _JDEpoch) else self.jd < _to_jd(other)

    def __ge__(self, other):
        return self.jd >= other.jd if isinstance(other, _JDEpoch) else self.jd >= _to_jd(other)

    def __gt__(self, other):
        return self.jd > other.jd if isinstance(other, _JDEpoch) else self.jd > _to_jd(other)

    def __eq__(self, other):
        return self.jd == other.jd if isinstance(other, _JDEpoch) else self.jd == _to_jd(other)

    def __repr__(self):
        return f"_JDEpoch({self.jd})"


def _to_jd(dt):
    """將 datetime.datetime 轉為 JD 值"""
    if isinstance(dt, _JDEpoch):
        return dt.jd
    if isinstance(dt, datetime.datetime):
        # 將 datetime 轉為 sxtwl.Time 再取 JD
        t = sxtwl.Time(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        return sxtwl.toJD(t)
    return float(dt)

# sxtwl 節氣索引與 jqmc 名稱的對應表
# sxtwl getJieQi() index 0 = 冬至 = jqmc[23]
# sxtwl getJieQi() index N = jqmc[N-1] (N>0)
_NAME_TO_SXTWL = {}
for _idx in range(24):
    _jq_idx = _idx - 1 if _idx > 0 else 23
    _NAME_TO_SXTWL[jqmc[_jq_idx]] = _idx


# %% sxtwl 節氣搜尋輔助函式（取代 ephem 天文計算）
def _find_jieqi_after(year, month, day, jieqi_name):
    """找指定節氣在給定日期之後的最近一次發生時間"""
    target_idx = _NAME_TO_SXTWL[jieqi_name]
    d = fromSolar(year, month, day)
    for i in range(1, 400):
        day_obj = d.after(i)
        if day_obj.hasJieQi() and day_obj.getJieQi() == target_idx:
            t = sxtwl.JD2DD(day_obj.getJieQiJD())
            return _safe_datetime(t.Y, t.M, t.D, int(t.h), round(t.m))
    return None


def _find_jieqi_before(year, month, day, jieqi_name):
    """找指定節氣在給定日期之前的最近一次發生時間"""
    target_idx = _NAME_TO_SXTWL[jieqi_name]
    d = fromSolar(year, month, day)
    for i in range(1, 400):
        day_obj = d.before(i)
        if day_obj.hasJieQi() and day_obj.getJieQi() == target_idx:
            t = sxtwl.JD2DD(day_obj.getJieQiJD())
            return _safe_datetime(t.Y, t.M, t.D, int(t.h), round(t.m))
    return None


#%% 甲子平支
def jiazi():
    return list(map(lambda x: "{}{}".format(tian_gan[x % len(tian_gan)],di_zhi[x % len(di_zhi)]),list(range(60))))


def multi_key_dict_get(d, k):
    for keys, v in d.items():
        if k in keys:
            return v
    return None

def new_list(olist, o):
    a = olist.index(o)
    res1 = olist[a:] + olist[:a]
    return res1
#%% 節氣計算
def get_jieqi_start_date(year, month, day, hour, minute):
    day = sxtwl.fromSolar(year, month, day)
    if day.hasJieQi():
        jq_index = day.getJieQi()
        jd = day.getJieQiJD()
        t = sxtwl.JD2DD(jd)
        return {
            "年": t.Y,
            "月": t.M,
            "日": t.D,
            "時": int(t.h),
            "分": round(t.m),
            "節氣": jqmc[jq_index-1],
            "時間":_safe_datetime(t.Y, t.M, t.D, int(t.h), round(t.m))
        }
    else:
        current_day = day
        while True:
            current_day = current_day.before(1)
            if current_day.hasJieQi():
                jq_index = current_day.getJieQi()
                jd = current_day.getJieQiJD()
                t = sxtwl.JD2DD(jd)
                return {
                    "年": t.Y,
                    "月": t.M,
                    "日": t.D,
                    "時": int(t.h),
                    "分": round(t.m),
                    "節氣": jqmc[jq_index-1],
                    "時間":_safe_datetime(t.Y, t.M, t.D, int(t.h), round(t.m))
                }
            
def get_before_jieqi_start_date(year, month, day, hour, minute):
    day = sxtwl.fromSolar(year, month, day)
    current_day = day.before(15)
    while True:
        if current_day.hasJieQi():
            jq_index = current_day.getJieQi()
            jd = current_day.getJieQiJD()
            t = sxtwl.JD2DD(jd)
            return {
                "年": t.Y,
                "月": t.M,
                "日": t.D,
                "時": int(t.h),
                "分": round(t.m),
                "節氣": jqmc[jq_index-1],
                "時間":_safe_datetime(t.Y, t.M, t.D, int(t.h), round(t.m))
            }
        current_day = current_day.before(1)

def get_next_jieqi_start_date(year, month, day, hour, minute):
    day = sxtwl.fromSolar(year, month, day)
    current_day = day.after(1)
    while True:
        if current_day.hasJieQi():
            jq_index = current_day.getJieQi()
            jd = current_day.getJieQiJD()
            t = sxtwl.JD2DD(jd)
            return {
                "年": t.Y,
                "月": t.M,
                "日": t.D,
                "時": int(t.h),
                "分": round(t.m),
                "節氣": jqmc[jq_index-1],
                "時間":_safe_datetime(t.Y, t.M, t.D, int(t.h), round(t.m))
            }
        current_day = current_day.after(1)


def jq(year, month, day, hour, minute):
    try:
        current_datetime = _safe_datetime(year, month, day, hour, minute)
        jq_start_dict = get_jieqi_start_date(year, month, day, hour, minute)
        next_jq_start_dict = get_next_jieqi_start_date(year, month, day, hour, minute)
        if not (isinstance(jq_start_dict, dict) and isinstance(next_jq_start_dict, dict) and 
                "時間" in jq_start_dict and "時間" in next_jq_start_dict and
                "節氣" in jq_start_dict and "節氣" in next_jq_start_dict):
            raise ValueError(f"Invalid jieqi dictionary format for {year}-{month}-{day} {hour}:{minute}")
        
        jq_start_datetime = jq_start_dict["時間"]
        next_jq_start_datetime = next_jq_start_dict["時間"]
        jq_name = jq_start_dict["節氣"]
        
        if not (isinstance(jq_start_datetime, (datetime.datetime, _JDEpoch)) and isinstance(next_jq_start_datetime, (datetime.datetime, _JDEpoch))):
            raise ValueError(f"Jieqi times are not datetime objects: {jq_start_datetime}, {next_jq_start_datetime}")
        
        # Check if current_datetime is within the current jieqi period
        if jq_start_datetime <= current_datetime < next_jq_start_datetime:
            return jq_name
        # If before the current jieqi start, get the previous jieqi
        elif current_datetime < jq_start_datetime:
            prev_jq_start_dict = get_before_jieqi_start_date(year, month, day, hour, minute)
            if not (isinstance(prev_jq_start_dict, dict) and "節氣" in prev_jq_start_dict):
                raise ValueError(f"Invalid previous jieqi dictionary format for {year}-{month}-{day}")
            return prev_jq_start_dict["節氣"]
        else:
            raise ValueError(f"Current datetime {current_datetime} not within any valid jieqi period")
    except Exception as e:
        raise ValueError(f"Error in jq for {year}-{month}-{day} {hour}:{minute}: {str(e)}")

def ke_jiazi_d(hour):
    t = [f"{h}:{m}0" for h in range(24) for m in range(6)]
    minutelist = dict(zip(t, cycle(repeat_list(1, find_lunar_ke(hour)))))
    return minutelist

def repeat_list(n, thelist):
    return [repetition for i in thelist for repetition in repeat(i,n)]


#五虎遁，起正月
def find_lunar_month(year):
    fivetigers = {
    tuple(list('甲己')):'丙寅',
    tuple(list('乙庚')):'戊寅',
    tuple(list('丙辛')):'庚寅',
    tuple(list('丁壬')):'壬寅',
    tuple(list('戊癸')):'甲寅'
    }
    if multi_key_dict_get(fivetigers, year[0]) == None:
        result = multi_key_dict_get(fivetigers, year[1])
    else:
        result = multi_key_dict_get(fivetigers, year[0])
    return dict(zip(range(1,13),new_list(jiazi(), result)[:12]))

#五鼠遁，起子時
def find_lunar_hour(day):
    fiverats = {
    tuple(list('甲己')):'甲子',
    tuple(list('乙庚')):'丙子',
    tuple(list('丙辛')):'戊子',
    tuple(list('丁壬')):'庚子',
    tuple(list('戊癸')):'壬子'
    }
    if multi_key_dict_get(fiverats, day[0]) == None:
        result = multi_key_dict_get(fiverats, day[1])
    else:
        result = multi_key_dict_get(fiverats, day[0])
    return dict(zip(list(di_zhi), new_list(jiazi(), result)[:12]))

#五馬遁，起子刻
def find_lunar_ke(hour):
    fivehourses = {
    tuple(list('丙辛')):'甲午',
    tuple(list('丁壬')):'丙午',
    tuple(list('戊癸')):'戊午',
    tuple(list('甲己')):'庚午',
    tuple(list('乙庚')):'壬午'
    }
    if multi_key_dict_get(fivehourses, hour[0]) == None:
        result = multi_key_dict_get(fivehourses, hour[1])
    else:
        result = multi_key_dict_get(fivehourses, hour[0])
    return new_list(jiazi(), result)

#農曆
def lunar_date_d(year, month, day):
    lunar_m = ['占位', '正月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '冬月', '腊月']
    day = fromSolar(year, month, day)
    return {"年":day.getLunarYear(),
            "農曆月": lunar_m[int(day.getLunarMonth())],
            "月":day.getLunarMonth(),
            "日":day.getLunarDay()}

#換算干支（用 datetime 取代 ephem.Date）
def gangzhi1(year, month, day, hour, minute):
    if hour == 23:
        d_year, d_month, d_day, d_hour = year, month, day + 1, 0
    else:
        d_year, d_month, d_day, d_hour = year, month, day, hour
    dd = [d_year, d_month, d_day, d_hour]
    cdate = fromSolar(dd[0], dd[1], dd[2])
    yTG,mTG,dTG,hTG = "{}{}".format(
        tian_gan[cdate.getYearGZ().tg],
        di_zhi[cdate.getYearGZ().dz]), "{}{}".format(
            tian_gan[cdate.getMonthGZ().tg],
            di_zhi[cdate.getMonthGZ().dz]), "{}{}".format(
                tian_gan[cdate.getDayGZ().tg],
                di_zhi[cdate.getDayGZ().dz]), "{}{}".format(
                    tian_gan[cdate.getHourGZ(dd[3]).tg],
                    di_zhi[cdate.getHourGZ(dd[3]).dz])
    if year < 1900:
        mTG1 = find_lunar_month(yTG).get(lunar_date_d(year, month, day).get("月"))
    else:
        mTG1 = mTG
    hTG1 = find_lunar_hour(dTG).get(hTG[1])
    return [yTG, mTG1, dTG, hTG1]

def gangzhi(year, month, day, hour, minute):
    if hour == 23:
        d_year, d_month, d_day, d_hour = year, month, day + 1, 0
    else:
        d_year, d_month, d_day, d_hour = year, month, day, hour
    dd = [d_year, d_month, d_day, d_hour]
    cdate = fromSolar(dd[0], dd[1], dd[2])
    yTG,mTG,dTG,hTG = "{}{}".format(
        tian_gan[cdate.getYearGZ().tg],
        di_zhi[cdate.getYearGZ().dz]), "{}{}".format(
            tian_gan[cdate.getMonthGZ().tg],
            di_zhi[cdate.getMonthGZ().dz]), "{}{}".format(
                tian_gan[cdate.getDayGZ().tg],
                di_zhi[cdate.getDayGZ().dz]), "{}{}".format(
                    tian_gan[cdate.getHourGZ(dd[3]).tg],
                    di_zhi[cdate.getHourGZ(dd[3]).dz])
    if year < 1900:
        mTG1 = find_lunar_month(yTG).get(lunar_date_d(year, month, day).get("月"))
    else:
        mTG1 = mTG
    hTG1 = find_lunar_hour(dTG).get(hTG[1])
    zi = gangzhi1(year, month, day, 0, 0)[3]
    if minute < 10 and minute >=0:
        reminute = "00"
    elif minute < 20 and minute >=10:
        reminute = "10"
    elif minute < 30 and minute >=20:
        reminute = "20"
    elif minute < 40 and minute >=30:
        reminute = "30"
    elif minute < 50 and minute >=40:
        reminute = "40"
    else:
        reminute = "50"
    hourminute = str(hour)+":"+str(reminute)
    gangzhi_minute = ke_jiazi_d(zi).get(hourminute)
    return [yTG, mTG1, dTG, hTG1, gangzhi_minute]


jieqi_name = re.findall('..', '春分清明穀雨立夏小滿芒種夏至小暑大暑立秋處暑白露秋分寒露霜降立冬小雪大雪冬至小寒大寒立春雨水驚蟄')


# %% 取代 ephem 天文計算的節氣函式（用 sxtwl）
def find_jq_date(year, month, day, hour, minute, jieqi_name_arg):
    """從給定日期往後搜尋，返回指定節氣的發生時間（datetime 物件）
    原始 ephem 邏輯：先回退30天，取黃道經度決定起始節氣區間（n = 區間+1，即跳過當前節氣），
    再往後遍歷24個節氣。等效於：從30天前位置的「下一個」節氣開始，往後搜24個節氣。
    若指定節氣在此範圍內出現多次，取最後一次（dict覆蓋語意）。"""
    target_idx = _NAME_TO_SXTWL[jieqi_name_arg]
    base_year, base_month, base_day = year, month, day
    # 往前推30天
    base_jd = sxtwl.toJD(sxtwl.Time(year, month, day, hour, minute, 0)) - 30.0
    base_dd = sxtwl.JD2DD(base_jd)
    base_year, base_month, base_day = int(base_dd.Y), int(base_dd.M), int(base_dd.D)
    d = fromSolar(base_year, base_month, base_day)
    # 找到 base 日期之後的第一個節氣（即跳過 base 所在的節氣區間）
    # 然後從那個節氣開始往後搜24個節氣
    jieqi_count = 0
    skipped_first = False
    last_match = None
    for i in range(1, 400):
        day_obj = d.after(i)
        if day_obj.hasJieQi():
            if not skipped_first:
                # 跳過第一個節氣（模擬 ephem 的 n+1 行為）
                skipped_first = True
                continue
            jieqi_count += 1
            if day_obj.getJieQi() == target_idx:
                t = sxtwl.JD2DD(day_obj.getJieQiJD())
                last_match = _safe_datetime(t.Y, t.M, t.D, int(t.h), round(t.m))
            if jieqi_count >= 24:
                break
    return last_match

def _days_diff(early, late):
    """計算兩個日期時間之間的天數差 (late - early)，支援 datetime.datetime 和 _JDEpoch。"""
    jd1 = _to_jd(early)
    jd2 = _to_jd(late)
    return int(jd2 - jd1)


def xzdistance(year, month, day, hour):
    """夏至距離（計算當前日期與最近夏至的天數差）"""
    current = _safe_datetime(year, month, day, hour, 0)
    xz_date = _find_jieqi_before(year, month, day, "夏至")
    return _days_diff(xz_date, current)

def distancejq(year, month, day, hour, minute, jq_name):
    """計算當前日期與上一年搜尋到的指定節氣之間的天數"""
    current = _safe_datetime(year, month, day, hour, minute)
    jq_date = find_jq_date(year - 1, month, day, hour, minute, jq_name)
    return _days_diff(jq_date, current)

def jq_count_days(year, month, day, hour, minute):
    """從當前節氣起始到當前日期的天數"""
    current = _safe_datetime(year, month, day, hour, minute)
    # 取得當前節氣名稱（jq 已正確處理節氣交界時刻）
    jq_name = jq(year, month, day, hour, minute)
    # 取得當前節氣的起始時間
    jq_start = get_jieqi_start_date(year, month, day, hour, minute)
    # 如果 get_jieqi_start_date 回傳的節氣與 jq 不一致，
    # 表示當天有未來節氣，需要往前找當前節氣的起始
    if jq_start["節氣"] != jq_name:
        jq_start = get_before_jieqi_start_date(year, month, day, hour, minute)
    jq_start_dt = jq_start["時間"]
    return _days_diff(jq_start_dt, current) + 1


def gong_wangzhuai(j_q):
    wangzhuai = list("旺相胎沒死囚休廢")
    wangzhuai_num = [3,4,9,2,7,6,1,8]
    wangzhuai_jieqi = {('春分','清明','穀雨'):'春分',
                        ('立夏','小滿','芒種'):'立夏',
                        ('夏至','小暑','大暑'):'夏至',
                        ('立秋','處暑','白露'):'立秋',
                        ('秋分','寒露','霜降'):'秋分',
                        ('立冬','小雪','大雪'):'立冬',
                        ('冬至','小寒','大寒'):'冬至',
                        ('立春','雨水','驚蟄'):'立春'}
    return dict(zip(config.new_list(wangzhuai_num, dict(zip(jieqi_name[0::3],wangzhuai_num )).get(config.multi_key_dict_get(wangzhuai_jieqi, j_q))), wangzhuai))