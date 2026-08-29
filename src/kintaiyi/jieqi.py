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
#from . import config
#import config

jqmc = ['小寒', '大寒', '立春', '雨水', '驚蟄', '春分', '清明', '穀雨', '立夏', '小滿', '芒種', '夏至', '小暑', '大暑', '立秋', '處暑', '白露', '秋分', '寒露', '霜降', '立冬', '小雪', '大雪', '冬至']
tian_gan = '甲乙丙丁戊己庚辛壬癸'
di_zhi = '子丑寅卯辰巳午未申酉戌亥'

# 月柱換月的「節」（非氣）。交節時刻之前仍屬上一個月支。
_MONTH_START_JIEQI = frozenset({
    '立春', '驚蟄', '清明', '立夏', '芒種', '小暑',
    '立秋', '白露', '寒露', '立冬', '大雪', '小寒'
})


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

def find_jieqi_date(year, name):
    """掃描指定年份，找出指定節氣（繁體名）的日期。
    用 sxtwl 逐日掃描，對公元前日期正確。
    返回 (y, m, d) 或 None"""
    import calendar
    days_in_year = 366 if calendar.isleap(year) else 365
    for jd in range(1, days_in_year + 1):
        try:
            day = sxtwl.fromSolar(year, 1, 1).after(jd - 1)
            if day.hasJieQi():
                idx = day.getJieQi()
                t = sxtwl.JD2DD(day.getJieQiJD())
                if jqmc[idx - 1] == name:
                    return (t.Y, t.M, t.D)
        except Exception:
            pass
    return None

def shichen_ju(year, month, day, hour):
    """古籍時計局數：局數 = floor(二至後時辰數 / 60) + 1（每 60 時辰＝5 日一局）。
    陰遁從夏至起算，陽遁從冬至起算。與前端 taiyi-jieqi.js 的 shichenJu 一致。
    返回 {'dun': '陰遁'|'陽遁', 'ju': int, 'base': str} 或 None"""
    xz = find_jieqi_date(year, '夏至')
    dz = find_jieqi_date(year, '冬至')
    dz_prev = find_jieqi_date(year - 1, '冬至')
    if not xz or not dz or not dz_prev:
        return None
    cur_jd = _to_jd(_safe_datetime(year, month, day, hour, 0))
    xz_jd = _to_jd(_safe_datetime(xz[0], xz[1], xz[2], 0, 0))
    dz_jd = _to_jd(_safe_datetime(dz[0], dz[1], dz[2], 0, 0))
    dz_prev_jd = _to_jd(_safe_datetime(dz_prev[0], dz_prev[1], dz_prev[2], 0, 0))
    if cur_jd >= xz_jd and cur_jd < dz_jd:
        base, dun = xz, '陰遁'
    elif cur_jd >= dz_prev_jd and cur_jd < xz_jd:
        base, dun = dz_prev, '陽遁'
    else:
        base, dun = dz, '陽遁'
    base_jd = _to_jd(_safe_datetime(base[0], base[1], base[2], 0, 0))
    days = cur_jd - base_jd
    hour_num = (hour + 1) // 2
    shichen = days * 12 + hour_num
    ju = int(shichen // 60) + 1
    return {'dun': dun, 'ju': ju, 'base': f"{base[0]}-{base[1]}-{base[2]}"}

# 古籍《太乙金鏡式經》時計太乙落宮（三時一移）
# 「陽遁命起一宮，順八宮，不游中五；陰遁命起九宮，逆行八宮，三時一移，不游中五。」
_YANG_GONG_ORDER = [1, 2, 3, 4, 6, 7, 8, 9]
_YIN_GONG_ORDER = [9, 8, 7, 6, 4, 3, 2, 1]


def taiyi_shichen_gong(year, month, day, hour):
    """古籍時計太乙落宮（三時一移）。返回 {'dun','gong','shichen','ru_gong'} 或 None"""
    sj = shichen_ju(year, month, day, hour)
    if not sj:
        return None
    dun = sj['dun']
    by, bm, bd = map(int, sj['base'].split('-'))
    cur_jd = _to_jd(_safe_datetime(year, month, day, hour, 0))
    base_jd = _to_jd(_safe_datetime(by, bm, bd, 0, 0))
    days = int(cur_jd - base_jd)
    hour_num = (hour + 1) // 2
    shichen = days * 12 + hour_num  # 二至後時實
    rem = shichen % 24
    gong_idx = rem // 3
    ru_gong = rem % 3
    order = _YANG_GONG_ORDER if dun == '陽遁' else _YIN_GONG_ORDER
    gong = order[gong_idx % 8]
    return {'dun': dun, 'gong': gong, 'shichen': shichen, 'ru_gong': ru_gong}


def _precise_month_gz(year, month, day, hour, minute, fallback_mtg):
    """
    精確計算月干支：僅在「換月節」當日，且當前時刻尚未到達交節時刻時，
    才回退至前一日的月柱。其他情況直接使用 sxtwl 的 fallback_mtg。
    這樣可避免把整個交節日都當成新月柱的誤差
   （例如 2026-09-07 16:30 在白露 22:40 之前，應為丙申月而非丁酉月）。
    """
    try:
        orig = fromSolar(year, month, day)
        if not orig.hasJieQi():
            return fallback_mtg
        jq_index = orig.getJieQi()
        jq_name = jqmc[jq_index - 1] if jq_index > 0 else jqmc[23]
        if jq_name not in _MONTH_START_JIEQI:
            return fallback_mtg
        t = sxtwl.JD2DD(orig.getJieQiJD())
        jq_dt = _safe_datetime(t.Y, t.M, t.D, int(t.h), round(t.m))
        curr_dt = _safe_datetime(year, month, day, hour, minute)
        if curr_dt < jq_dt:
            prev = orig.before(1)
            return "{}{}".format(
                tian_gan[prev.getMonthGZ().tg],
                di_zhi[prev.getMonthGZ().dz]
            )
        return fallback_mtg
    except Exception:
        return fallback_mtg


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

#%% 節氣計算（已修正：精確比較當前時分）
def get_jieqi_start_date(year, month, day, hour, minute):
    """
    回傳「當前時間所屬」節氣的開始時刻（精確到時分）。
    若當天有節氣但當前時刻尚未到達，則回傳上一個節氣。
    """
    current_dt = datetime.datetime(year, month, day, hour, minute)
    day_obj = fromSolar(year, month, day)

    # 當天有節氣時，先判斷是否已過交節時刻
    if day_obj.hasJieQi():
        jq_index = day_obj.getJieQi()
        jd = day_obj.getJieQiJD()
        t = sxtwl.JD2DD(jd)
        jq_dt = datetime.datetime(t.Y, t.M, t.D, int(t.h), round(t.m))
        if current_dt >= jq_dt:
            return {
                "年": t.Y, "月": t.M, "日": t.D,
                "時": int(t.h), "分": round(t.m),
                "節氣": jqmc[jq_index - 1],
                "時間": jq_dt
            }

    # 往前找最近的一個已過去的節氣
    current = day_obj
    while True:
        current = current.before(1)
        if current.hasJieQi():
            jq_index = current.getJieQi()
            jd = current.getJieQiJD()
            t = sxtwl.JD2DD(jd)
            return {
                "年": t.Y, "月": t.M, "日": t.D,
                "時": int(t.h), "分": round(t.m),
                "節氣": jqmc[jq_index - 1],
                "時間": datetime.datetime(t.Y, t.M, t.D, int(t.h), round(t.m))
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
        # 精確交節時刻判斷月柱（換月「節」當日，交節前仍用上月）
        mTG1 = _precise_month_gz(year, month, day, hour, 0, mTG)
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
        # 精確交節時刻判斷月柱（例如 2026-09-07 16:30 在白露前 → 丙申月）
        mTG1 = _precise_month_gz(year, month, day, hour, minute, mTG)
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
    return dict(zip(new_list(wangzhuai_num, dict(zip(jieqi_name[0::3],wangzhuai_num )).get(multi_key_dict_get(wangzhuai_jieqi, j_q))), wangzhuai))

if __name__ == '__main__':
    year = 2026
    month = 9
    day = 7
    hour = 16
    minute = 30
    print(f"{year}-{month}-{day} {hour}:{minute}")
    print("gangzhi:", gangzhi(year, month, day, hour, minute))
    print("jq:", jq(year, month, day, hour, minute))
    print("jieqi start:", get_jieqi_start_date(year, month, day, hour, minute))

    print("\n--- 交節後驗證 ---")
    print("23:00 gangzhi:", gangzhi(2026, 9, 7, 16, 30))
    print("23:00 jq:", jq(2026, 9, 7, 16, 30))
