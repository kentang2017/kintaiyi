# -*- coding: utf-8 -*-
import datetime
import re
from itertools import cycle, repeat

import sxtwl
from sxtwl import fromSolar

from . import config

jqmc = ['小寒', '大寒', '立春', '雨水', '驚蟄', '春分', '清明', '穀雨',
        '立夏', '小滿', '芒種', '夏至', '小暑', '大暑', '立秋', '處暑',
        '白露', '秋分', '寒露', '霜降', '立冬', '小雪', '大雪', '冬至']

tian_gan = '甲乙丙丁戊己庚辛壬癸'
di_zhi = '子丑寅卯辰巳午未申酉戌亥'


# ==================== 基礎工具 ====================
def jiazi():
    return list(map(lambda x: "{}{}".format(tian_gan[x % len(tian_gan)], di_zhi[x % len(di_zhi)]), list(range(60))))


def multi_key_dict_get(d, k):
    for keys, v in d.items():
        if k in keys:
            return v
    return None


def new_list(olist, o):
    a = olist.index(o)
    return olist[a:] + olist[:a]


# ==================== 節氣相關（使用 sxtwl） ====================
def get_jieqi_start_date(year, month, day, hour=0, minute=0):
    """取得當前日期所在的節氣開始時間"""
    day = fromSolar(year, month, day)
    if day.hasJieQi():
        jq_index = day.getJieQi()
        jd = day.getJieQiJD()
        t = sxtwl.JD2DD(jd)
        return {
            "年": int(t.Y), "月": int(t.M), "日": int(t.D),
            "時": int(t.h), "分": int(round(t.m)),
            "節氣": jqmc[jq_index - 1],
            "時間": datetime.datetime(int(t.Y), int(t.M), int(t.D), int(t.h), int(round(t.m)))
        }
    else:
        current_day = day
        for _ in range(30):
            current_day = current_day.before(1)
            if current_day.hasJieQi():
                jq_index = current_day.getJieQi()
                jd = current_day.getJieQiJD()
                t = sxtwl.JD2DD(jd)
                return {
                    "年": int(t.Y), "月": int(t.M), "日": int(t.D),
                    "時": int(t.h), "分": int(round(t.m)),
                    "節氣": jqmc[jq_index - 1],
                    "時間": datetime.datetime(int(t.Y), int(t.M), int(t.D), int(t.h), int(round(t.m)))
                }
    return None


def get_next_jieqi_start_date(year, month, day, hour=0, minute=0):
    day = fromSolar(year, month, day)
    current_day = day.after(1)
    for _ in range(30):
        if current_day.hasJieQi():
            jq_index = current_day.getJieQi()
            jd = current_day.getJieQiJD()
            t = sxtwl.JD2DD(jd)
            return {
                "年": int(t.Y), "月": int(t.M), "日": int(t.D),
                "時": int(t.h), "分": int(round(t.m)),
                "節氣": jqmc[jq_index - 1],
                "時間": datetime.datetime(int(t.Y), int(t.M), int(t.D), int(t.h), int(round(t.m)))
            }
        current_day = current_day.after(1)
    return None


def get_before_jieqi_start_date(year, month, day, hour=0, minute=0):
    day = fromSolar(year, month, day)
    current_day = day.before(1)
    for _ in range(30):
        if current_day.hasJieQi():
            jq_index = current_day.getJieQi()
            jd = current_day.getJieQiJD()
            t = sxtwl.JD2DD(jd)
            return {
                "年": int(t.Y), "月": int(t.M), "日": int(t.D),
                "時": int(t.h), "分": int(round(t.m)),
                "節氣": jqmc[jq_index - 1],
                "時間": datetime.datetime(int(t.Y), int(t.M), int(t.D), int(t.h), int(round(t.m)))
            }
        current_day = current_day.before(1)
    return None


def jq(year, month, day, hour, minute):
    """回傳當前時間所在的節氣名稱"""
    current = datetime.datetime(year, month, day, hour, minute)
    jq_now = get_jieqi_start_date(year, month, day, hour, minute)
    jq_next = get_next_jieqi_start_date(year, month, day, hour, minute)

    if not jq_now or not jq_next:
        return None

    if jq_now["時間"] <= current < jq_next["時間"]:
        return jq_now["節氣"]
    elif current < jq_now["時間"]:
        prev = get_before_jieqi_start_date(year, month, day, hour, minute)
        return prev["節氣"] if prev else None
    else:
        return jq_next["節氣"]


# ==================== 干支相關（已移除 ephem） ====================
def gangzhi1(year, month, day, hour, minute):
    if year == 0:
        return ["無效"]
    if year < 0:
        year += 1

    # 使用 datetime 取代 ephem.Date
    if hour == 23:
        dt = datetime.datetime(year, month, day) + datetime.timedelta(days=1)
        dt = dt.replace(hour=0)
        hour_for_gz = 0
    else:
        dt = datetime.datetime(year, month, day, hour)
        hour_for_gz = hour

    cdate = fromSolar(dt.year, dt.month, dt.day)

    yTG = f"{tian_gan[cdate.getYearGZ().tg]}{di_zhi[cdate.getYearGZ().dz]}"
    mTG = f"{tian_gan[cdate.getMonthGZ().tg]}{di_zhi[cdate.getMonthGZ().dz]}"
    dTG = f"{tian_gan[cdate.getDayGZ().tg]}{di_zhi[cdate.getDayGZ().dz]}"
    hTG = f"{tian_gan[cdate.getHourGZ(hour_for_gz).tg]}{di_zhi[cdate.getHourGZ(hour_for_gz).dz]}"

    if year < 1900:
        mTG1 = find_lunar_month(yTG).get(lunar_date_d(year, month, day).get("月"))
    else:
        mTG1 = mTG

    hTG1 = find_lunar_hour(dTG).get(hTG[1])
    return [yTG, mTG1, dTG, hTG1]


def gangzhi(year, month, day, hour, minute):
    if year == 0:
        return ["無效"]
    if year < 0:
        year += 1

    if hour == 23:
        dt = datetime.datetime(year, month, day) + datetime.timedelta(days=1)
        dt = dt.replace(hour=0)
        hour_for_gz = 0
    else:
        dt = datetime.datetime(year, month, day, hour)
        hour_for_gz = hour

    cdate = fromSolar(dt.year, dt.month, dt.day)

    yTG = f"{tian_gan[cdate.getYearGZ().tg]}{di_zhi[cdate.getYearGZ().dz]}"
    mTG = f"{tian_gan[cdate.getMonthGZ().tg]}{di_zhi[cdate.getMonthGZ().dz]}"
    dTG = f"{tian_gan[cdate.getDayGZ().tg]}{di_zhi[cdate.getDayGZ().dz]}"
    hTG = f"{tian_gan[cdate.getHourGZ(hour_for_gz).tg]}{di_zhi[cdate.getHourGZ(hour_for_gz).dz]}"

    if year < 1900:
        mTG1 = find_lunar_month(yTG).get(lunar_date_d(year, month, day).get("月"))
    else:
        mTG1 = mTG

    hTG1 = find_lunar_hour(dTG).get(hTG[1])

    zi = gangzhi1(year, month, day, 0, 0)[3]

    # 分鐘干支
    if minute < 10:
        reminute = "00"
    elif minute < 20:
        reminute = "10"
    elif minute < 30:
        reminute = "20"
    elif minute < 40:
        reminute = "30"
    elif minute < 50:
        reminute = "40"
    else:
        reminute = "50"

    hourminute = f"{hour}:{reminute}"
    gangzhi_minute = ke_jiazi_d(zi).get(hourminute)

    return [yTG, mTG1, dTG, hTG1, gangzhi_minute]


# ==================== 其他原有函式（保留） ====================
def find_lunar_month(year):
    fivetigers = {
        tuple(list('甲己')): '丙寅',
        tuple(list('乙庚')): '戊寅',
        tuple(list('丙辛')): '庚寅',
        tuple(list('丁壬')): '壬寅',
        tuple(list('戊癸')): '甲寅'
    }
    result = multi_key_dict_get(fivetigers, year[0]) or multi_key_dict_get(fivetigers, year[1])
    return dict(zip(range(1, 13), new_list(jiazi(), result)[:12]))


def find_lunar_hour(day):
    fiverats = {
        tuple(list('甲己')): '甲子',
        tuple(list('乙庚')): '丙子',
        tuple(list('丙辛')): '戊子',
        tuple(list('丁壬')): '庚子',
        tuple(list('戊癸')): '壬子'
    }
    result = multi_key_dict_get(fiverats, day[0]) or multi_key_dict_get(fiverats, day[1])
    return dict(zip(list(di_zhi), new_list(jiazi(), result)[:12]))


def lunar_date_d(year, month, day):
    lunar_m = ['占位', '正月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '冬月', '腊月']
    day = fromSolar(year, month, day)
    return {
        "年": day.getLunarYear(),
        "農曆月": lunar_m[int(day.getLunarMonth())],
        "月": day.getLunarMonth(),
        "日": day.getLunarDay()
    }


def ke_jiazi_d(hour):
    t = [f"{h}:{m}0" for h in range(24) for m in range(6)]
    return dict(zip(t, cycle(repeat_list(1, find_lunar_ke(hour)))))


def repeat_list(n, thelist):
    return [repetition for i in thelist for repetition in repeat(i, n)]


def find_lunar_ke(hour):
    fivehourses = {
        tuple(list('丙辛')): '甲午',
        tuple(list('丁壬')): '丙午',
        tuple(list('戊癸')): '戊午',
        tuple(list('甲己')): '庚午',
        tuple(list('乙庚')): '壬午'
    }
    result = multi_key_dict_get(fivehourses, hour[0]) or multi_key_dict_get(fivehourses, hour[1])
    return new_list(jiazi(), result)


# ==================== 其餘工具函式 ====================
jieqi_name = re.findall('..', '春分清明穀雨立夏小滿芒種夏至小暑大暑立秋處暑白露秋分寒露霜降立冬小雪大雪冬至小寒大寒立春雨水驚蟄')


def gong_wangzhuai(j_q):
    wangzhuai = list("旺相胎沒死囚休廢")
    wangzhuai_num = [3, 4, 9, 2, 7, 6, 1, 8]
    wangzhuai_jieqi = {
        ('春分', '清明', '穀雨'): '春分',
        ('立夏', '小滿', '芒種'): '立夏',
        ('夏至', '小暑', '大暑'): '夏至',
        ('立秋', '處暑', '白露'): '立秋',
        ('秋分', '寒露', '霜降'): '秋分',
        ('立冬', '小雪', '大雪'): '立冬',
        ('冬至', '小寒', '大寒'): '冬至',
        ('立春', '雨水', '驚蟄'): '立春'
    }
    key = config.multi_key_dict_get(wangzhuai_jieqi, j_q)
    return dict(zip(config.new_list(wangzhuai_num, dict(zip(jieqi_name[0::3], wangzhuai_num)).get(key)), wangzhuai))
