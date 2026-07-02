
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 27 18:11:44 2022
@author: kentang
Optimized for performance
"""
import re
import os
import time
import math
import json
import itertools
import datetime
from datetime import date
from cn2an import an2cn, cn2an
from .taiyidict import tengan_shiji, su_dist
from . import kinliuren
from . import config
from . import chart
from . import jieqi
from . import taiyi_life_dict
from .jieqi import jieqi_name

_BASE = os.path.abspath(os.path.dirname(__file__))
_SIGN_TO_BRANCH = dict(zip(range(12), "戌酉申未午巳辰卯寅丑子亥"))

# 預計算資料表（取代 astropy/ephem 的天文計算）
with open(os.path.join(_BASE, "data", "xiu_degrees_data.json"), encoding="utf-8") as _f:
    _XIU_DEGREES_TABLE = json.load(_f)
with open(os.path.join(_BASE, "data", "stars_data.json"), encoding="utf-8") as _f:
    _STARS_TABLE = json.load(_f)

_STARS_KEYS = ["日　", "月　", "辰星", "太白", "熒惑", "歲星", "填星"]


def get_xiu_degrees(year):
    """二十八宿度數：使用預計算表 + 線性插值（取代 astropy FK5 歲差轉換）"""
    table = _XIU_DEGREES_TABLE
    keys = sorted(int(k) for k in table)
    # 找到包圍 year 的兩個最近10年點
    if year <= keys[0]:
        return table[str(keys[0])]
    if year >= keys[-1]:
        return table[str(keys[-1])]
    lo = max(k for k in keys if k <= year)
    hi = min(k for k in keys if k >= year)
    if lo == hi:
        return table[str(lo)]
    lo_vals = table[str(lo)]
    hi_vals = table[str(hi)]
    frac = (year - lo) / (hi - lo)
    return [round(lo_vals[i] + (hi_vals[i] - lo_vals[i]) * frac, 2) for i in range(28)]


def find_stars(year, month, day, hour, minute):
    """七曜落宮：使用預計算表查詢（取代 ephem 天體位置計算）。
    1900年以後以每日精度查詢；1900年以前以每月精度查詢（月初值）。"""
    key = f"{year:04d}-{month:02d}-{day:02d}"
    compact = _STARS_TABLE.get(key)
    if compact is None:
        # 回退到該月最近的可用日期
        key = f"{year:04d}-{month:02d}-01"
        compact = _STARS_TABLE.get(key)
    if compact is None:
        # 再回退：找該年最近的月份
        for m in range(1, 13):
            key = f"{year:04d}-{m:02d}-01"
            compact = _STARS_TABLE.get(key)
            if compact is not None:
                break
    if compact is None:
        return {}
    return dict(zip(_STARS_KEYS, list(compact)))


def _days_between(year, month, day, hour, minute, ref_year, ref_month, ref_day):
    """計算兩個日期之間的天數差，支援負數年份（公元前）。
    使用 sxtwl.toJD 取代 datetime.datetime，因為 Python datetime 不支援 year < 1。"""
    import sxtwl
    t1 = sxtwl.Time(year, month, day, hour, minute, 0)
    t2 = sxtwl.Time(ref_year, ref_month, ref_day, 0, 0, 0)
    return int(sxtwl.toJD(t1) - sxtwl.toJD(t2))



class Taiyi:
    """太乙起盤主要函數"""
    def __init__(self, year, month, day, hour, minute):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.door = list("開休生傷杜景死驚")
        # Cache for expensive computations
        self.cache = {}
        # Precompute static mappings
        self.di_zhi = config.di_zhi
        self.di_zhi_reversed = list(reversed(self.di_zhi))
        self.jiazi_list = config.jiazi()
        self.jigod_map = dict(zip(self.di_zhi, config.new_list(self.di_zhi_reversed, "寅")))
        self.jigod_map_r = dict(zip(list(reversed(self.di_zhi)), config.new_list(self.di_zhi, "酉")))
        self.hegod_map = dict(zip(self.di_zhi, config.new_list(self.di_zhi_reversed, "丑")))
        self.l_num = [8, 8, 3, 3, 4, 4, 9, 9, 2, 2, 7, 7, 6, 6, 1, 1]

    def _get_gangzhi(self):
        """Cache gangzhi results"""
        if 'gangzhi' not in self.cache:
            self.cache['gangzhi'] = config.gangzhi(self.year, self.month, self.day, self.hour, self.minute)
        return self.cache['gangzhi']

    def _get_lunar_date(self):
        """Cache lunar date results"""
        if 'lunar_date' not in self.cache:
            self.cache['lunar_date'] = config.lunar_date_d(self.year, self.month, self.day)
        return self.cache['lunar_date']

    def jigod(self, ji_style):
        """計神"""
        yy = self.kook( ji_style,0)["文"][0]
        if yy == "陽":
            j = self.jigod_map.get(self.taishui(ji_style))
        if yy == "陰":
            j = self.jigod_map_r.get(self.taishui(ji_style))
        return  j

    def taishui(self, ji_style):
        """太歲"""
        gang_zhi = self._get_gangzhi()
        return {0: gang_zhi[0][1], 1: gang_zhi[1][1], 2: gang_zhi[2][1], 3: gang_zhi[3][1], 4: gang_zhi[4][1], 5: gang_zhi[0][1]}.get(ji_style)

    def skyeyes_des(self, ji_style, taiyi_acumyear):
        """文昌始擊處境"""
        kook = self.kook(ji_style, taiyi_acumyear)
        return dict(zip(range(1, 73), config.skyeyes_summary.get(kook.get("文")[0]))).get(kook.get("數"))

    def skyeyes(self, ji_style, taiyi_acumyear):
        """文昌(天目)"""
        kook = self.kook(ji_style, taiyi_acumyear)
        return dict(zip(range(1, 73), config.skyeyes_dict.get(kook.get("文")[0]))).get(kook.get("數"))

    def hegod(self, ji_style):
        """合神"""
        return self.hegod_map.get(self.taishui(ji_style))

    def accnum(self, ji_style, taiyi_acumyear):
        """積年數計算"""
        cache_key = f'accnum_{ji_style}_{taiyi_acumyear}'
        if cache_key in self.cache:
            return self.cache[cache_key]

        tndict = {0: 10153917, 1: 1936557, 2: 10154193, 3: 10153917}
        tn_c = tndict.get(taiyi_acumyear)
        lunar = self._get_lunar_date()
        lunar_year = lunar.get("年")
        lunar_month = lunar.get("月")
        lunar_day = lunar.get("日")

        if ji_style == 0:  # 年計
            result = tn_c + lunar_year + (1 if lunar_year < 0 else 0)
        elif ji_style == 1:  # 月計
            accyear = tn_c + lunar_year - 1 + (2 if lunar_year < 0 else 0)
            result = accyear * 12 + 2 + lunar_month
        elif ji_style == 2:  # 日計
            diff_val = _days_between(self.year, self.month, self.day, self.hour, 0, 1900, 6, 19)
            #config_num = 708011105 - {0: 0, 1: 185, 2: 10153917, 3: 0}.get(taiyi_acumyear, 0)
            config_num = 708011105 - taiyi_acumyear - {0: 185, 1: 184, 2: 183, 3: 182}.get(taiyi_acumyear)
            result = config_num + diff_val if taiyi_acumyear != 3 else round((lunar_year - 423) * (235 / 19) * 29.5306 + lunar_day, 0)
        elif ji_style == 3:  # 時計
            diff_val_two = _days_between(self.year, self.month, self.day, self.hour, 0, 1900, 12, 21)
            config_num = 708011105 - {0: 0, 1: 10153917, 2: 10153917, 3: 0}.get(taiyi_acumyear)
            accday = config_num + diff_val_two
            result = ((accday - 1) * 12) + (self.hour + 1) // 2 + (1 if taiyi_acumyear != 1 else -11)
            if taiyi_acumyear == 3:
                tiangan = dict(zip([tuple(self.jiazi_list[i:i+6]) for i in range(0, 60, 6)], self.jiazi_list[0::6]))
                dgz = self._get_gangzhi()[2]
                getfut = dict(zip(self.jiazi_list[0::6], [1, 7, 13, 19, 25, 31, 37, 43, 49, 55])).get(config.multi_key_dict_get(tiangan, dgz))
                dgz_num = dict(zip(self.jiazi_list, range(1, 61))).get(dgz)
                zhi_num = dict(zip(self.di_zhi, range(1, 13))).get(self._get_gangzhi()[3][1])
                result = zhi_num if tiangan == dgz_num else ((dgz_num - getfut) * 12) + zhi_num
        elif ji_style == 4:  # 分計
            diff_val_two = _days_between(self.year, self.month, self.day, self.hour, self.minute, 1900, 12, 21)
            config_num = 708011105 - {0: 0, 1: 10153917, 2: 10153917, 3: 0}.get(taiyi_acumyear)
            accday = config_num + diff_val_two
            #result = ((accday - 1) * 23) + (self.hour * 10500) + (self.minute + 1)
            base_result = ((accday - 1) * 23) + (self.hour * 10500) + (self.minute + 1)
            gz = self._get_gangzhi()
            minute_gz = gz[4]  # 分干支
            jiazi_idx = dict(zip(self.jiazi_list, range(1, 61))).get(minute_gz, 1)
            # 調整使 result % 60 == jiazi_idx （保持大數值穩定）
            current_mod = base_result % 60
            adjustment = (jiazi_idx - current_mod) % 60
            result = base_result + adjustment
        else:
            result = None

        self.cache[cache_key] = result
        return result

    def lr(self):
        gz = config.gangzhi(self.year, self.month, self.day, self.hour, self.minute)
        j_q = jieqi.jq(self.year, self.month, self.day, self.hour, self.minute)
        cm = dict(zip(range(1,13), config.cmonth )).get(config.lunar_date_d(self.year, self.month, self.day).get("月") )
        return kinliuren.Liuren(j_q, cm, gz[2], gz[3])

    def taiyi_life_accum(self):
        """太乙命數積日數"""
        def calculate_value_for_year(year):
            initial_value = 126944450
            increment_per_60_years = 3145500
            cycles = (year - 1564) // 60
            value = initial_value + cycles * increment_per_60_years
            return value
        
        #太乙人道命法的積年數
        def jiazi_accum(gz):
            return dict(zip(config.jiazi(), [i*3652425 for i in list(range(1,61))])).get(gz)
        
        def jq_accum(jq):
            return dict(zip(config.new_list(jieqi.jieqi_name, "冬至"), [3652425,152184.37,304368.75,456553.12,608727.50,760921.87,913106.25,1065290.62,1217475,1369659.37,1522843.75,1674028.12,1826212.50,1978396.87,2130581.25,2282765.62,2434950,2587134.37,2739318.75,2891503.12,3043687.50,3195871.87,3348056.25,3500240.62])).get(jq)

        y = calculate_value_for_year(self.year)
        gz = self._get_gangzhi()
        jie_qi = jieqi.jq(self.year, self.month, self.day, self.hour, self.minute)
        return (jiazi_accum(gz[0]) + y + jq_accum(jie_qi) + (jieqi.jq_count_days(self.year, self.month, self.day, self.hour, self.minute) * 10000)) // 10000

    def three_cai_num(self):
        """三才數"""
        accum_num = self.taiyi_life_accum()
        sky = accum_num % 720
        earth = sky % 72
        ppl = earth % 72
        return sky, earth, ppl

    def yeargua(self, taiyi_acumyear):
        """值年卦"""
        num = self.accnum(0, taiyi_acumyear) % 64 or 64
        return config.gua.get(num)

    def daygua(self, taiyi_acumyear):
        """值日卦"""
        num = self.accnum(1, taiyi_acumyear) % 646464 % 20 or 64
        return config.gua.get(num)

    def hourgua(self, taiyi_acumyear):
        """值時卦"""
        num = self.accnum(3, taiyi_acumyear) % 64 or 64
        return config.gua.get(num)

    def kook(self, ji_style, taiyi_acumyear):
        """太乙局數"""
        cache_key = f'kook_{ji_style}_{taiyi_acumyear}'
        if cache_key in self.cache:
            return self.cache[cache_key]

        alljq = jieqi_name
        j_q = jieqi.jq(self.year, self.month, self.day, self.hour, self.minute)
        dz = config.new_list(alljq, "冬至")[:12]
        hz = config.new_list(alljq, "夏至")[:12]
        jqmap = {tuple(dz): "冬至", tuple(hz): "夏至"}
        k = self.accnum(ji_style, taiyi_acumyear) % 72 or 72
        three_year = {0: "理天", 1: "理地", 2: "理人"}.get({i: v for i, v in zip(range(1, 73), [0, 1, 2] * 24)}.get(k))
        dun = "陽遁" if ji_style in (0, 1, 5, 2) else {"夏至": "陰遁", "冬至": "陽遁"}.get(config.multi_key_dict_get(jqmap, j_q))
        if ji_style == 4:
            gz = self._get_gangzhi()
            if config.multi_key_dict_get(jqmap, j_q) == "冬至":
                a = config.multi_key_dict_get(
                    {tuple("申酉戌亥子丑"): "陽遁", tuple("寅卯辰巳午未"): "陰遁"}
                    if gz[2][0] in "甲丙戊庚壬" else
                    {tuple("申酉戌亥子丑"): "陰遁", tuple("寅卯辰巳午未"): "陽遁"},
                    gz[3][1]
                )
            else:
                a = config.multi_key_dict_get(
                    {tuple("申酉戌亥子丑"): "陰遁", tuple("寅卯辰巳午未"): "陽遁"}
                    if gz[2][0] in "甲丙戊庚壬" else
                    {tuple("申酉戌亥子丑"): "陽遁", tuple("寅卯辰巳午未"): "陰遁"},
                    gz[3][1]
                )
            dun = a

        result = {"文": f"{dun}{an2cn(k)}局", "數": k, "年": three_year, "積" + config.taiyi_name(ji_style)[0] + "數": self.accnum(ji_style, taiyi_acumyear)}
        self.cache[cache_key] = result
        return result

    def get_five_yuan_kook(self, ji_style, taiyi_acumyear):
        """太乙五子元局"""
        gz = self._get_gangzhi()
        kook = self.kook(ji_style, taiyi_acumyear)
        try:
            return kook.get("文")[:2] + (config.five_zi_yuan(kook.get("數"), gz[ji_style]) if ji_style != 4 else config.min_five_zi_yuan(kook.get("數"), gz[ji_style]))
        except ValueError:
            return ""

    def getepoch(self, ji_style, taiyi_acumyear):
        """求太乙的紀"""
        acc_num = self.accnum(ji_style, taiyi_acumyear)
        if ji_style in (0, 1, 2):
            find_ji_num = 1 if acc_num % 360 == 1 else int((acc_num % 360) // 60 + 1)
            find_ji_num2 = int(acc_num % 360 % 72 % 24 / 3) or 1
            if find_ji_num2 > 6:
                find_ji_num2 -= 6
            if find_ji_num > 6:
                find_ji_num -= 6
            return {"元": dict(zip(range(1, 7), config.cnum[:6])).get(find_ji_num2), "紀": dict(zip(range(1, 7), config.cnum[:6])).get(find_ji_num)}
        return f"第{config.multi_key_dict_get(config.epochdict, self._get_gangzhi()[2 if ji_style == 3 else 3])}紀"

    def getyuan(self, ji_style, taiyi_acumyear):
        """求太乙的元"""
        acc_num = self.accnum(ji_style, taiyi_acumyear)
        find_ji_num = 1 if round(acc_num % 360) == 1 else int(round((acc_num % 360) / 72, 0))
        return dict(zip(range(1, 6), self.jiazi_list[0::12])).get(find_ji_num or 1)

    def jiyuan(self, ji_style, taiyi_acumyear):
        """太乙紀元"""
        gang_zhi = self._get_gangzhi()
        if ji_style in (3, 4):
            return f"{self.getepoch(ji_style, taiyi_acumyear)}{config.multi_key_dict_get(config.jiyuan_dict, gang_zhi[3 if ji_style == 4 or taiyi_acumyear == 1 else 2])}元"
        return f"第{self.getepoch(ji_style, taiyi_acumyear).get('紀')}紀第{self.getepoch(ji_style, taiyi_acumyear).get('元')}{self.getyuan(ji_style, taiyi_acumyear)}元"

    def ty(self, ji_style, taiyi_acumyear):
        """求太乙所在"""
        arrangement = [x for x in range(10) for _ in range(3)]
        arrangement_r = list(reversed(arrangement))
        yy_dict = {
            "陽": dict(zip(range(1, 73), list(itertools.chain.from_iterable([list(arrangement)[3:15] + list(arrangement)[18:]] * 3)))),
            "陰": dict(zip(range(1, 73), (arrangement_r[:12] + arrangement_r[15:-3]) * 3))
        }
        kook = self.kook(ji_style, taiyi_acumyear)
        return yy_dict[kook.get("文")[0]].get(kook.get("數"))

    def ty_gong(self, ji_style, taiyi_acumyear):
        """太乙落宮"""
        return dict(zip(range(1, 73), config.taiyi_pai)).get(self.kook(ji_style, taiyi_acumyear).get("數"))

    def twenty_eightstar(self, ji_style, taiyi_acumyear):
        """二十八宿"""
        s_f = self.sf_num(ji_style, taiyi_acumyear)
        sf = self.sf(ji_style, taiyi_acumyear)
        su_r = list(reversed(config.su))
        sixteen = config.sixteen
        num = su_r.index(s_f) - sixteen.index(sf) + sixteen.index("巳") + {
            "坤": -2, "酉": -3, "亥": -5, "巳": 1, "寅": 4, "卯": 3, "子": 6, "未": -1, "申": -2, "戌": -4, "艮": 4, "巽": 1, "丑": 5, "午": 0, "乾": -5
        }.get(sf, 2)
        num = (num - 28) if num > 28 else (num + 28) if num < 0 else 28 if num == 0 else num
        return config.new_list(su_r, dict(zip(range(1, 29), su_r)).get(num))

    def sf(self, ji_style, taiyi_acumyear):
        """始擊落宮"""
        return dict(zip(range(1, 73), config.sf_list)).get(self.kook(ji_style, taiyi_acumyear).get("數"))

    def su_obj_num(self, ji_style, taiyi_acumyear, obj):
        if obj!="中":
            #sf = self.sf(ji_style, taiyi_acumyear)
            sf_z = dict(zip(config.gong, range(1, 17))).get(obj)
            sf_su = config.su_gong.get(obj)
            yc_num = dict(zip(config.su, range(1, 29))).get(self.year_chin())
            total = yc_num + sf_z
            return dict(zip(range(1, 29), config.new_list(config.su, sf_su))).get(total if total <= 28 else total - 28)
        else:
            return "中"
    
    def sf_num(self, ji_style, taiyi_acumyear):
        """始擊值"""
        sf = self.sf(ji_style, taiyi_acumyear)
        sf_z = dict(zip(config.gong, range(1, 17))).get(sf)
        sf_su = config.su_gong.get(sf)
        yc_num = dict(zip(config.su, range(1, 29))).get(self.year_chin())
        total = yc_num + sf_z
        return dict(zip(range(1, 29), config.new_list(config.su, sf_su))).get(total if total <= 28 else total - 28)

    def se(self, ji_style, taiyi_acumyear):
        """定目"""
        wc, hg, ts = self.skyeyes(ji_style, taiyi_acumyear), self.hegod(ji_style), self.taishui(ji_style)
        start = config.new_list(config.gong1, hg)
        return config.new_list(config.gong1, wc)[len(start[:start.index(ts) + 1]) - 1]

    def home_cal(self, ji_style, taiyi_acumyear):
        """主算"""
        l_num= [8,8,3,3,4,4,9,9,2,2,7,7,6,6,1,1]
        wancheong = self.skyeyes(ji_style, taiyi_acumyear)
        wc_num= dict(zip(config.new_list(config.sixteen, "亥"), l_num)).get(wancheong)
        taiyi = self.ty(ji_style, taiyi_acumyear)
        wc_jc = list(map(lambda x: x == wancheong, config.jc)).count(True)
        ty_jc = list(map(lambda x: x == taiyi, config.tyjc)).count(True)
        wc_jc1  = list(map(lambda x: x == wancheong, config.jc1)).count(True)
        wc_order = config.new_list(config.num, wc_num)
        #if wc_jc == 1 and ty_jc != 1 and wc_jc1 !=1 :
        #    return sum(wc_order[: wc_order.index(taiyi)]) +1
        #if wc_jc !=1 and ty_jc != 1 and wc_jc1 ==1:
        #    return sum(wc_order[: wc_order.index(taiyi)])
        #if wc_jc != 1 and ty_jc ==1 and wc_jc1 !=1:
        #    return sum(wc_order[: wc_order.index(taiyi)])
        #if wc_jc ==1 and ty_jc ==1 and wc_jc1 !=1 and wc_jc == ty_jc and wc_jc1 == wc_jc:
        #    return sum(wc_order[wc_order.index(taiyi):])+1
        #if wc_jc ==1 and ty_jc ==1 and wc_jc1 !=1 and wc_jc == ty_jc and wc_jc1 != wc_jc:
        #    return sum(wc_order[:wc_order.index(taiyi)])+1
        #if wc_jc ==1 and ty_jc ==1 and wc_jc1 !=1 and wc_jc != ty_jc:
        #    return sum(wc_order[wc_order.index(ty_jc):])+1
        #if wc_jc !=1 and ty_jc ==1 and wc_jc1 ==1 and taiyi != wc_order[wc_jc] and wc_jc1 != wc_jc:
        #    return sum(wc_order[: wc_order.index(taiyi)])
        #if wc_jc !=1 and ty_jc ==1 and wc_jc1 ==1 and taiyi == wc_order[wc_jc] and wc_jc1 == wc_jc:
        #    return taiyi
        #if wc_jc !=1 and ty_jc !=1 and wc_jc1 !=1 and taiyi != wc_num:
        #    return sum(wc_order[: wc_order.index(taiyi)])
        #if wc_jc !=1 and ty_jc !=1 and wc_jc1 !=1 and taiyi == wc_num:
            #return taiyi
        #else:
        #    return taiyi
        return sum(wc_order[: wc_order.index(taiyi)])
    def home_general(self, ji_style, taiyi_acumyear):
        """主大將"""
        kook = self.kook(ji_style, taiyi_acumyear)
        home_cal = config.find_cal(kook.get("文")[0], kook.get("數"))[0]
        return {
            True: self.home_cal(ji_style, taiyi_acumyear),
            home_cal < 10: home_cal,
            home_cal % 10 == 0: 1,
            10 < home_cal < 20: home_cal - 10,
            20 < home_cal < 30: home_cal - 20,
            30 < home_cal < 40: home_cal - 30
        }.get(True, 1)

    def home_vgen(self, ji_style, taiyi_acumyear):
        """主參將"""
        home_vg = self.home_general(ji_style, taiyi_acumyear) * 3 % 10
        return 5 if home_vg == 0 else home_vg

    def away_cal(self, ji_style, taiyi_acumyear):
        """客算"""
        shiji = self.sf(ji_style, taiyi_acumyear)
        sf_num = dict(zip(config.new_list(config.sixteen, "亥"), self.l_num)).get(shiji)
        taiyi = self.ty(ji_style, taiyi_acumyear)
        sf_jc = shiji in config.jc
        ty_jc = taiyi in config.tyjc
        sf_jc1 = shiji in config.jc1
        sf_order = config.new_list(config.num, sf_num)

        logic_map = {
            (True, False, False): lambda: sum(sf_order[:sf_order.index(taiyi)]) + 1 if sf_jc == ty_jc else sum(sf_order[:config.jc.index(shiji) + 1]) + 1,
            (False, False, True): lambda: sum(sf_order[taiyi - 2:]) if sf_jc == ty_jc and 5 < taiyi < 7 else sum(sf_order[:taiyi + 1]) if sf_jc == ty_jc and taiyi < 5 else sum(sf_order[:sf_order.index(taiyi)]),
            (False, True, False): lambda: sum(sf_order[sf_order.index(taiyi):]) if sf_jc == ty_jc else sum(sf_order[:sf_order.index(config.tyjc[0])] if ty_jc else sf_order[:sf_order.index(taiyi)]),
            (True, True, False): lambda: sum(sf_order[:sf_order.index(taiyi)]) + 1 if sf_jc == ty_jc else sum(sf_order[:taiyi]),
            (False, True, True): lambda: sum(sf_order[:sf_order.index(taiyi)]),
            (False, False, False): lambda: taiyi if sf_num == taiyi else sum(sf_order[:sf_order.index(taiyi)])
        }
        return logic_map.get((sf_jc, ty_jc, sf_jc1), lambda: taiyi)()

    def away_general(self, ji_style, taiyi_acumyear):
        """客大將"""
        kook = self.kook(ji_style, taiyi_acumyear)
        away_cal = config.find_cal(kook.get("文")[0], kook.get("數"))[1]
        return {
            away_cal == 1: 1,
            away_cal < 10: away_cal,
            away_cal % 10 == 0: 5,
            10 < away_cal < 20: away_cal - 10,
            20 < away_cal < 30: away_cal - 20,
            30 < away_cal < 40: away_cal - 30
        }.get(True, 5)

    def away_vgen(self, ji_style, taiyi_acumyear):
        """客參將"""
        away_vg = self.away_general(ji_style, taiyi_acumyear) * 3 % 10
        return 5 if away_vg == 0 else away_vg

    def shensha(self, ji_style, taiyi_acumyear):
        """推太乙當時法"""
        if ji_style not in (3, 4):
            return "太乙時計才顯示"
        general = "貴人,螣蛇,朱雀,六合,勾陳,青龍,天空,白虎,太常,玄武,太陰,天后".split(",")
        tiany = self.ty_gong(ji_style, taiyi_acumyear).replace("巽", "辰").replace("坤", "申").replace("艮", "丑").replace("乾", "亥")
        return dict(zip(config.new_list(self.di_zhi if self.kook(ji_style, taiyi_acumyear).get("文")[0] == "陽" else self.di_zhi_reversed, tiany), general))

    def set_cal(self, ji_style, taiyi_acumyear):
        """定算"""
        setcal = self.se(ji_style, taiyi_acumyear)
        se_num = dict(zip(config.new_list(config.sixteen, "亥"), self.l_num)).get(setcal)
        taiyi = self.ty(ji_style, taiyi_acumyear)
        se_jc = setcal in config.jc
        ty_jc = taiyi in config.tyjc
        se_jc1 = setcal in config.jc1
        se_order = config.new_list(config.num, se_num)

        logic_map = {
            (True, False, False): lambda: 1 if sum(se_order[:se_order.index(taiyi)]) == 0 else sum(se_order[:se_order.index(taiyi)]) + 1,
            (False, False, True): lambda: sum(se_order[:se_order.index(taiyi)]),
            (False, True, False): lambda: sum(se_order[:se_order.index(taiyi)]),
            (True, True, False): lambda: sum(se_order[:se_order.index(taiyi)]) + 1,
            (False, True, True): lambda: 1 if sum(se_order[:se_order.index(taiyi)]) == 0 else sum(se_order[:se_order.index(taiyi)]),
            (False, False, False): lambda: taiyi if se_num == taiyi else sum(se_order[:se_order.index(taiyi)])
        }
        return logic_map.get((se_jc, ty_jc, se_jc1), lambda: sum(se_order[:se_order.index(taiyi)]))()

    def set_general(self, ji_style, taiyi_acumyear):
        """定大將"""
        set_g = self.set_cal(ji_style, taiyi_acumyear) % 10
        return 5 if set_g == 0 else set_g

    def set_vgen(self, ji_style, taiyi_acumyear):
        """定參將"""
        set_vg = self.set_general(ji_style, taiyi_acumyear) * 3 % 10
        return 5 if set_vg == 0 else set_vg
    def sixteen_gong(self, ji_style, taiyi_acumyear):
        """十六宮各星將與十精分佈"""
        if ji_style != 4:
            dict1 = [{self.skyeyes(ji_style, taiyi_acumyear):"文昌"},
                     {self.taishui(ji_style):"太歲"},
                     {self.hegod(ji_style):"合神"},
                     {self.jigod(ji_style):"計神"},
                     {self.sf(ji_style, taiyi_acumyear):"始擊"},
                     {self.se(ji_style, taiyi_acumyear):"定計"}, 
                     {self.kingbase(ji_style, taiyi_acumyear):"君基"}, 
                     {self.officerbase(ji_style, taiyi_acumyear):"臣基"}, 
                     {self.pplbase(ji_style, taiyi_acumyear):"民基"},
                     {self.fgd(ji_style, taiyi_acumyear):"四神"},
                     {self.skyyi(ji_style, taiyi_acumyear):"天乙"},
                     {self.earthyi(ji_style, taiyi_acumyear):"地乙"},
                     {self.zhifu(ji_style, taiyi_acumyear):"直符"},
                     {self.flyfu(ji_style, taiyi_acumyear):"飛符"},
                     {config.tian_wang(self.accnum(ji_style,taiyi_acumyear)):"天皇"},
                     {config.tian_shi(self.accnum(ji_style,taiyi_acumyear)):"天時"},
                     {config.wuxing(self.accnum(ji_style,taiyi_acumyear)):"五行"},
                     {config.kingfu(self.accnum(ji_style,taiyi_acumyear)):"帝符"},
                     {config.taijun(self.accnum(ji_style,taiyi_acumyear)):"太尊"},
                     {config.num2gong(config.wufu(self.accnum(ji_style,taiyi_acumyear))):"五福"},
                     #{self.ty_gong(ji_style, taiyi_acumyear):"太乙"},
                     {config.num2gong(self.home_general(ji_style, taiyi_acumyear)):"主大"},  
                     {config.num2gong(self.home_vgen(ji_style, taiyi_acumyear)):"主參"},
                     {config.num2gong(self.away_general(ji_style, taiyi_acumyear)):"客大"},  
                     {config.num2gong(self.away_vgen(ji_style, taiyi_acumyear)):"客參"},
                     {config.num2gong(config.threewind(self.accnum(ji_style,taiyi_acumyear))):"三風"},  
                     {config.num2gong(config.fivewind(self.accnum(ji_style,taiyi_acumyear))):"五風"},
                     {config.num2gong(config.eightwind(self.accnum(ji_style,taiyi_acumyear))):"八風"},  
                     {config.num2gong(config.flybird(self.accnum(ji_style,taiyi_acumyear))):"飛鳥"},
                     {config.num2gong(config.bigyo(self.accnum(ji_style,taiyi_acumyear))):"大游"},
                     {config.num2gong(config.smyo(self.accnum(ji_style,taiyi_acumyear))):"小游"},  
                     #{config.leigong(self.ty(ji_style, taiyi_acumyear)):"雷公"},  
                     {config.yangjiu(self.year, self.month, self.day):"陽九"}, 
                     {config.baliu(self.year, self.month, self.day):"百六"},
                     #{config.lijin(self.year, self.month, self.day, self.hour, self.minute):"臨津"}, 
                     #{config.lion(self.year, self.month, self.day, self.hour, self.minute):"獅子"}, 
                     #{config.cloud(self.home_general(ji_style, taiyi_acumyear)):"白雲"},
                     #{config.tiger(self.ty(ji_style, taiyi_acumyear)):"猛虎"}, 
                     #{config.returnarmy(self.away_general(ji_style, taiyi_acumyear)):"回軍"}, 
                     {config.num2gong(self.ty(ji_style, taiyi_acumyear)):"太乙"}, 
                     ]
        if ji_style == 4:
            dict1 = [{self.skyeyes(ji_style, taiyi_acumyear):"文昌"},
                     {self.hegod(ji_style):"合神"},
                     {self.jigod(ji_style):"計神"},
                     {self.sf(ji_style, taiyi_acumyear):"始擊"},
                     {self.kingbase(ji_style, taiyi_acumyear):"君基"}, 
                     {self.officerbase(ji_style, taiyi_acumyear):"臣基"}, 
                     {self.pplbase(ji_style, taiyi_acumyear):"民基"},
                     {self.fgd(ji_style, taiyi_acumyear):"四神"},
                     {self.skyyi(ji_style, taiyi_acumyear):"天乙"},
                     {self.earthyi(ji_style, taiyi_acumyear):"地乙"},
                     {self.zhifu(ji_style, taiyi_acumyear):"直符"},
                     {self.flyfu(ji_style, taiyi_acumyear):"飛符"},
                     {config.tian_wang(self.accnum(ji_style,taiyi_acumyear)):"天皇"},
                     {config.wuxing(self.accnum(ji_style,taiyi_acumyear)):"五行"},
                     {config.kingfu(self.accnum(ji_style,taiyi_acumyear)):"帝符"},
                     {config.taijun(self.accnum(ji_style,taiyi_acumyear)):"太尊"},
                     {config.num2gong(config.wufu(self.accnum(ji_style,taiyi_acumyear))):"五福"},
                     {config.num2gong(self.home_general(ji_style, taiyi_acumyear)):"主大"},  
                     {config.num2gong(self.home_vgen(ji_style, taiyi_acumyear)):"主參"},
                     {config.num2gong(self.away_general(ji_style, taiyi_acumyear)):"客大"},  
                     {config.num2gong(self.away_vgen(ji_style, taiyi_acumyear)):"客參"},
                     {config.num2gong(config.threewind(self.accnum(ji_style,taiyi_acumyear))):"三風"},  
                     {config.num2gong(config.fivewind(self.accnum(ji_style,taiyi_acumyear))):"五風"},
                     {config.num2gong(config.eightwind(self.accnum(ji_style,taiyi_acumyear))):"八風"},  
                     {config.num2gong(config.flybird(self.accnum(ji_style,taiyi_acumyear))):"飛鳥"},
                     {config.num2gong(self.ty(ji_style, taiyi_acumyear)):"太乙"}, 
                     ]
        res = {"巳":"", "午":"", "未":"", "坤":"", "申":"", "酉":"", "戌":"", "乾":"", "亥":"", "子":"", "丑":"", "艮":"","寅":"", "卯":"", "辰":"", "巽":"","中":""}
        for dict in dict1:
            for list in dict:
                if list in res:
                    try:
                        res[list] += (dict[list])
                    except TypeError:
                        pass
                else:
                    try:
                        res[list] = dict[list]
                    except TypeError:
                        pass
        rres = str(res.values())[11:].replace("([","").replace("'","").replace("])","").replace(" ", "").split(",")
        rrres = [re.findall("..", i) for i in rres]
        overall = str(res.keys())[11:].replace("([","").replace("'","").replace("])","").replace(" ", "").split(",")
        return {overall[i]:rrres[i] for i in range(0,17)}

    def sixteen_gong1(self, ji_style, taiyi_acumyear):
        """十六星分佈"""
        dict1 = [{self.skyeyes(ji_style, taiyi_acumyear).replace("巽","辰").replace("坤","申").replace("艮","丑").replace("乾","亥").replace("中", "辰"):"文昌"},
                 {self.jigod(ji_style).replace("巽","辰").replace("坤","申").replace("艮","丑").replace("乾","亥").replace("中", "辰"):"計神"},
                 {self.sf(ji_style, taiyi_acumyear).replace("巽","辰").replace("坤","申").replace("艮","丑").replace("乾","亥").replace("中", "辰"):"始擊"},
                 {self.kingbase(ji_style, taiyi_acumyear).replace("巽","辰").replace("坤","申").replace("艮","丑").replace("乾","亥"):"君基"}, 
                 {self.officerbase(ji_style, taiyi_acumyear).replace("巽","辰").replace("坤","申").replace("艮","丑").replace("乾","亥").replace("中", "辰"):"臣基"}, 
                 {self.pplbase(ji_style, taiyi_acumyear).replace("巽","辰").replace("坤","申").replace("艮","丑").replace("乾","亥").replace("中", "辰"):"民基"},
                 {self.fgd(ji_style, taiyi_acumyear).replace("巽","辰").replace("坤","申").replace("艮","丑").replace("乾","亥").replace("中", "辰"):"四神"},
                 {self.skyyi(ji_style, taiyi_acumyear).replace("巽","辰").replace("坤","申").replace("艮","丑").replace("乾","亥").replace("中", "辰"):"天乙"},
                 {self.earthyi(ji_style, taiyi_acumyear).replace("巽","辰").replace("坤","申").replace("艮","丑").replace("乾","亥").replace("中", "辰"):"地乙"},
                 {self.flyfu1(ji_style, taiyi_acumyear).replace("巽","辰").replace("坤","申").replace("艮","丑").replace("乾","亥").replace("中", "辰"):"飛符"},
                 {self.zhifu(ji_style, taiyi_acumyear).replace("巽","辰").replace("坤","申").replace("艮","丑").replace("乾","亥").replace("中", "辰"):"直符"},
                 {config.num2gong_life(config.wufu(self.accnum(ji_style,taiyi_acumyear))).replace("巽","辰").replace("坤","申").replace("艮","丑").replace("乾","亥"):"五福"},
                 {config.num2gong_life(self.home_general(ji_style, taiyi_acumyear)).replace("巽","辰").replace("坤","申").replace("艮","丑").replace("乾","亥"):"主大"},  
                 {config.num2gong_life(self.home_vgen(ji_style, taiyi_acumyear)).replace("巽","辰").replace("坤","申").replace("艮","丑").replace("乾","亥"):"主參"},
                 {config.num2gong_life(self.away_general(ji_style, taiyi_acumyear)).replace("巽","辰").replace("坤","申").replace("艮","丑").replace("乾","亥"):"客大"},  
                 {config.num2gong_life(self.away_vgen(ji_style, taiyi_acumyear)).replace("巽","辰").replace("坤","申").replace("艮","丑").replace("乾","亥"):"客參"},
                 {config.num2gong_life(config.smyo(self.accnum(ji_style,taiyi_acumyear))).replace("巽","辰").replace("坤","申").replace("艮","丑").replace("乾","亥"):"小游"},  
                 ]
        res = {"巳":"", "午":"", "未":"", "申":"", "酉":"", "戌":"", "亥":"", "子":"", "丑":"", "寅":"", "卯":"", "辰":"","中":""}
        for dict in dict1:
            for list in dict:
                if list in res:
                    try:
                        res[list] += (dict[list])
                    except TypeError:
                        pass
                else:
                    try:
                        res[list] = dict[list]
                    except TypeError:
                        pass
        rres = str(res.values())[11:].replace("([","").replace("'","").replace("])","").replace(" ", "").split(",")
        rrres = [re.findall("..", i) for i in rres]
        overall = str(res.keys())[11:].replace("([","").replace("'","").replace("])","").replace(" ", "").split(",")
        return {overall[i]:rrres[i] for i in range(0,13)}

    def sixteen_gong11(self, ji_style, taiyi_acumyear):
        """十六星分佈"""
        dict1 = [{self.skyeyes(ji_style, taiyi_acumyear).replace("巽","辰").replace("坤","申").replace("艮","丑").replace("乾","亥").replace("中", "辰"):"文昌"},
                 {self.jigod(ji_style).replace("巽","辰").replace("坤","申").replace("艮","丑").replace("乾","亥").replace("中", "辰"):"計神"},
                 {self.sf(ji_style, taiyi_acumyear).replace("巽","辰").replace("坤","申").replace("艮","丑").replace("乾","亥").replace("中", "辰"):"始擊"},
                 {self.kingbase(ji_style, taiyi_acumyear).replace("巽","辰").replace("坤","申").replace("艮","丑").replace("乾","亥"):"君基"}, 
                 {self.officerbase(ji_style, taiyi_acumyear).replace("巽","辰").replace("坤","申").replace("艮","丑").replace("乾","亥").replace("中", "辰"):"臣基"}, 
                 {self.pplbase(ji_style, taiyi_acumyear).replace("巽","辰").replace("坤","申").replace("艮","丑").replace("乾","亥").replace("中", "辰"):"民基"},
                 {self.fgd(ji_style, taiyi_acumyear).replace("巽","辰").replace("坤","申").replace("艮","丑").replace("乾","亥").replace("中", "辰"):"四神"},
                 {self.skyyi(ji_style, taiyi_acumyear).replace("巽","辰").replace("坤","申").replace("艮","丑").replace("乾","亥").replace("中", "辰"):"天乙"},
                 {self.earthyi(ji_style, taiyi_acumyear).replace("巽","辰").replace("坤","申").replace("艮","丑").replace("乾","亥").replace("中", "辰"):"地乙"},
                 {self.flyfu1(ji_style, taiyi_acumyear).replace("巽","辰").replace("坤","申").replace("艮","丑").replace("乾","亥").replace("中", "辰"):"飛符"},
                 {config.num2gong_life(config.wufu(self.accnum(ji_style,taiyi_acumyear))).replace("巽","辰").replace("坤","申").replace("艮","丑").replace("乾","亥"):"五福"},
                 {config.num2gong_life(self.home_general(ji_style, taiyi_acumyear)).replace("巽","辰").replace("坤","申").replace("艮","丑").replace("乾","亥"):"主大"},  
                 {config.num2gong_life(self.home_vgen(ji_style, taiyi_acumyear)).replace("巽","辰").replace("坤","申").replace("艮","丑").replace("乾","亥"):"主參"},
                 {config.num2gong_life(self.away_general(ji_style, taiyi_acumyear)).replace("巽","辰").replace("坤","申").replace("艮","丑").replace("乾","亥"):"客大"},  
                 {config.num2gong_life(self.away_vgen(ji_style, taiyi_acumyear)).replace("巽","辰").replace("坤","申").replace("艮","丑").replace("乾","亥"):"客參"},
                 {config.num2gong_life(config.smyo(self.accnum(ji_style,taiyi_acumyear))).replace("巽","辰").replace("坤","申").replace("艮","丑").replace("乾","亥"):"小游"},  
                 ]
        res = {"巳":"", "午":"", "未":"", "申":"", "酉":"", "戌":"", "亥":"", "子":"", "丑":"", "寅":"", "卯":"", "辰":"","中":""}
        for dict in dict1:
            for list in dict:
                if list in res:
                    try:
                        res[list] += (dict[list])
                    except TypeError:
                        pass
                else:
                    try:
                        res[list] = dict[list]
                    except TypeError:
                        pass
        rres = str(res.values())[11:].replace("([","").replace("'","").replace("])","").replace(" ", "").split(",")
        rrres = [re.findall("..", i) for i in rres]
        overall = str(res.keys())[11:].replace("([","").replace("'","").replace("])","").replace(" ", "").split(",")
        return {overall[i]:rrres[i] for i in range(0,13)}
    
    def sixteen_gong3(self, ji_style, taiyi_acumyear):
        """十六宮各星將，無十精"""
        if ji_style != 4:
            dict1 = [{self.skyeyes(ji_style, taiyi_acumyear):"文昌"},
                     {self.taishui(ji_style):"太歲"},
                     {self.hegod(ji_style):"合神"},
                     {self.jigod(ji_style):"計神"},
                     {self.sf(ji_style, taiyi_acumyear):"始擊"},
                     {self.se(ji_style, taiyi_acumyear):"定計"}, 
                     {self.kingbase(ji_style, taiyi_acumyear):"君基"}, 
                     {self.officerbase(ji_style, taiyi_acumyear):"臣基"}, 
                     {self.pplbase(ji_style, taiyi_acumyear):"民基"},
                     {self.fgd(ji_style, taiyi_acumyear):"四神"},
                     {self.skyyi(ji_style, taiyi_acumyear):"天乙"},
                     {self.earthyi(ji_style, taiyi_acumyear):"地乙"},
                     {self.zhifu(ji_style, taiyi_acumyear):"直符"},
                     {self.flyfu(ji_style, taiyi_acumyear):"飛符"},
                     {config.num2gong(config.wufu(self.accnum(ji_style,taiyi_acumyear))):"五福"},
                     #{self.ty_gong(ji_style, taiyi_acumyear):"太乙"},
                     {config.num2gong(self.home_general(ji_style, taiyi_acumyear)):"主大"},  
                     {config.num2gong(self.home_vgen(ji_style, taiyi_acumyear)):"主參"},
                     {config.num2gong(self.away_general(ji_style, taiyi_acumyear)):"客大"},  
                     {config.num2gong(self.away_vgen(ji_style, taiyi_acumyear)):"客參"},
                     {config.num2gong(config.bigyo(self.accnum(ji_style,taiyi_acumyear))):"大游"},
                     {config.num2gong(config.smyo(self.accnum(ji_style,taiyi_acumyear))):"小游"},  
                     #{config.leigong(self.ty(ji_style, taiyi_acumyear)):"雷公"},  
                     {config.yangjiu(self.year, self.month, self.day):"陽九"}, 
                     {config.baliu(self.year, self.month, self.day):"百六"},
                     {config.num2gong(self.ty(ji_style, taiyi_acumyear)):"太乙"}, 
                     ]
        if ji_style == 4:
            dict1 = [{self.skyeyes(ji_style, taiyi_acumyear):"文昌"},
                     {self.hegod(ji_style):"合神"},
                     {self.jigod(ji_style):"計神"},
                     {self.sf(ji_style, taiyi_acumyear):"始擊"},
                     {self.kingbase(ji_style, taiyi_acumyear):"君基"}, 
                     {self.officerbase(ji_style, taiyi_acumyear):"臣基"}, 
                     {self.pplbase(ji_style, taiyi_acumyear):"民基"},
                     {self.fgd(ji_style, taiyi_acumyear):"四神"},
                     {self.skyyi(ji_style, taiyi_acumyear):"天乙"},
                     {self.earthyi(ji_style, taiyi_acumyear):"地乙"},
                     {self.zhifu(ji_style, taiyi_acumyear):"直符"},
                     {self.flyfu(ji_style, taiyi_acumyear):"飛符"},
                     {config.num2gong(config.wufu(self.accnum(ji_style,taiyi_acumyear))):"五福"},
                     {config.num2gong(self.home_general(ji_style, taiyi_acumyear)):"主大"},  
                     {config.num2gong(self.home_vgen(ji_style, taiyi_acumyear)):"主參"},
                     {config.num2gong(self.away_general(ji_style, taiyi_acumyear)):"客大"},  
                     {config.num2gong(self.away_vgen(ji_style, taiyi_acumyear)):"客參"},
                     {config.num2gong(self.ty(ji_style, taiyi_acumyear)):"太乙"}, 
                     ]
        res = {"巳":"", "午":"", "未":"", "坤":"", "申":"", "酉":"", "戌":"", "乾":"", "亥":"", "子":"", "丑":"", "艮":"","寅":"", "卯":"", "辰":"", "巽":"","中":""}
        for dict in dict1:
            for list in dict:
                if list in res:
                    try:
                        res[list] += (dict[list])
                    except TypeError:
                        pass
                else:
                    try:
                        res[list] = dict[list]
                    except TypeError:
                        pass
        rres = str(res.values())[11:].replace("([","").replace("'","").replace("])","").replace(" ", "").split(",")
        rrres = [re.findall("..", i) for i in rres]
        overall = str(res.keys())[11:].replace("([","").replace("'","").replace("])","").replace(" ", "").split(",")
        return {overall[i]:rrres[i] for i in range(0,17)}

    def stars_descriptions_text(self, ji_style, taiyi_acumyear):
        """星將描述"""
        alld = self.sixteen_gong(ji_style, taiyi_acumyear)
        return "\n\n".join(f"【{key}】\n{', '.join(value) if value else '無'}" for key, value in alld.items())

    def year_chin(self):
        """太歲禽星"""
        chin_28_stars_code = dict(zip(range(1, 29), config.su))
        lunar = self._get_lunar_date()
        year = lunar.get("年")
        month = lunar.get("月")
        if month in ("十二月", "十一月") and jieqi.jq(self.year, self.month, self.day, self.hour, self.minute) != "立春":
            get_year_chin_number = (year - 1 + 15) % 28 or 28
        else:
            get_year_chin_number = (year + 15) % 28 or 28
        return chin_28_stars_code.get(get_year_chin_number)

    def kingbase(self, ji_style, taiyi_acumyear):
        """君基"""
        king_base = (self.accnum(ji_style, taiyi_acumyear) + 250) % 360 // 30 or 1
        return dict(zip(range(1, 13), config.new_list(self.di_zhi, "午"))).get(int(king_base))

    def officerbase(self, ji_style, taiyi_acumyear):
        """臣基"""
        return dict(zip(range(1, 73), itertools.cycle(config.officer_base))).get(self.kook(ji_style, taiyi_acumyear).get("數"))

    def pplbase(self, ji_style, taiyi_acumyear):
        """民基"""
        return dict(zip(range(1, 73), itertools.cycle(config.new_list(self.di_zhi, "申")))).get(self.kook(ji_style, taiyi_acumyear).get("數"))

    def fgd(self, ji_style, taiyi_acumyear):
        """四神"""
        return dict(zip(range(1, 73), itertools.cycle(config.four_god))).get(self.kook(ji_style, taiyi_acumyear).get("數"))

    def skyyi(self, ji_style, taiyi_acumyear):
        """天乙"""
        return dict(zip(range(1, 73), itertools.cycle(config.sky_yi))).get(self.kook(ji_style, taiyi_acumyear).get("數"))

    def earthyi(self, ji_style, taiyi_acumyear):
        """地乙"""
        return dict(zip(range(1, 73), itertools.cycle(config.earth_yi))).get(self.kook(ji_style, taiyi_acumyear).get("數"))

    def zhifu(self, ji_style, taiyi_acumyear):
        """直符"""
        return dict(zip(range(1, 73), itertools.cycle(config.zhi_fu))).get(self.kook(ji_style, taiyi_acumyear).get("數"))

    def flyfu(self, ji_style, taiyi_acumyear):
        """飛符"""
        fly = self.accnum(ji_style, taiyi_acumyear) % 360 % 36 / 3
        fly_fu = dict(zip(range(1, 13), config.new_list(self.di_zhi, "辰"))).get(int(fly)) or "中"
        return fly_fu

    def flyfu1(self, ji_style, taiyi_acumyear):
        """飛符 (for sixteen_gong1)"""
        fly = self.accnum(ji_style, taiyi_acumyear) % 360 % 36 / 3
        fly_fu = dict(zip(range(1, 13), config.new_list(self.di_zhi, "辰"))).get(int(fly)) or "辰"
        return fly_fu

    def tianzi_go(self, ji_style, taiyi_acumyear):
        """明天子巡狩之期術"""
        wan_c = self.skyeyes(ji_style, taiyi_acumyear)
        return {
            "坤": "天目在大武坤，出北方。",
            "乾": "天目在陰德乾，出東方。",
            "艮": "天目在和德艮，出南方。",
            "巽": "天目在大靈巽，出西方。"
        }.get(wan_c, "")

    def gudan(self, ji_style, taiyi_acumyear):
        """推孤單以占成敗"""
        ying_yang = {tuple([1, 3, 7, 9]): "單陽", tuple([2, 4, 6, 8]): "單陰"}
        homecal = str(self.home_cal(ji_style, taiyi_acumyear))
        awaycal = str(self.away_cal(ji_style, taiyi_acumyear))
        if len(homecal) == 1:
            one_digit = config.multi_key_dict_get(ying_yang, int(homecal))
            return f"主筭得{one_digit}，{'不利上，不利主人也。' if one_digit == '單陽' else '沒不利也。'}"
        if len(awaycal) == 1:
            one_digit = config.multi_key_dict_get(ying_yang, int(awaycal))
            return f"客筭得{one_digit}，{'沒不利也。' if one_digit == '單陽' else '不利上，不利客人也。'}"
        for calc, prefix in [(homecal, "主算"), (awaycal, "客算")]:
            if len(calc) == 2:
                two_digit = "孤陽" if int(calc[1]) in (1, 3) else "孤陰"
                first_digit = config.multi_key_dict_get(ying_yang, int(calc[0]))
                if two_digit == "孤陰" and first_digit == "單陰":
                    return f"{prefix}為單陰並孤陰，為重陰。"
                if two_digit == "孤陽" and first_digit == "單陰":
                    return f"{prefix}為單陰並孤陽，沒不利。"
                if two_digit == "孤陰" and first_digit == "單陽":
                    return f"{prefix}為單陽並孤陰，沒不利。"
                if two_digit == "孤陽" and first_digit == "單陽":
                    return f"{prefix}為單陽並孤陽，為重陽。"
        return ""


    def ming_kingbase(self, ji_style, taiyi_acumyear):
        """明君基太乙所主術"""
        kingb = self.kingbase(ji_style, taiyi_acumyear)
        officerb = self.officerbase(ji_style, taiyi_acumyear)
        pplb =  self.pplbase(ji_style, taiyi_acumyear)
        wufu = config.num2gong(config.wufu(self.accnum(ji_style, taiyi_acumyear)))
        ty = self.ty_gong(ji_style, taiyi_acumyear)
        tiany = self.skyyi(ji_style, taiyi_acumyear)
        earthy = self.earthyi(ji_style, taiyi_acumyear)
        fgod = self.fgd(ji_style, taiyi_acumyear)
        zhifu = self.zhifu(ji_style, taiyi_acumyear)
        big = config.num2gong(config.bigyo(self.accnum(ji_style, taiyi_acumyear)))
        small = config.num2gong(config.smyo(self.accnum(ji_style, taiyi_acumyear)))
        result = []
        if kingb == wufu:
            result.append("君基與五福同宮，皇國鞏固，宇內清寧，家有祥瑞，福祿並慶。")
        if kingb == officerb:
            result.append("君基與臣基同宮，君臣際會，國富民殷。")
        if kingb == pplb:
            result.append("君基與民基同宮，務農桑安，百姓五穀豐。有巡狩，不失序，視民之象。")          
        if kingb == ty:
            result.append("君基與太乙同宮，敷德宣命練兵，敵眾以征不義，古者天子伏鉞，以征不道，所以止暴。其黷武好戰則變異，而火災口舌興也。")
        if kingb == earthy:
            result.append("君基與地乙同宮，人民宜愛君，勸穡稼，則德永昌，而天下風和命維新矣，如若淫慢，則地生妖言，異物病疫傷民而喪亡也。")
        if kingb == zhifu:
            result.append("君基與值符同宮，人君定典章，別忠佞，明嫡庶，重功勛，則風化熙而嘉祥至矣，若寵奸佞，邪營建，吏酷民愁，則火早、災荒而不利於君。")
        if kingb == fgod:
            result.append("君基與四神同宮，人君宜抵肅，以奉宗廟祭祀先王，所以順陰陽而和神人也。其若廢祀失時，而傷穡稼，則潼川溺咎自君也。")
        if kingb == big:
            result.append("君基與大游同宮，其神凶惡也。所臨主兵革、水旱、疾病、君宜修政，明刑、宣文、治化，施恩者，賦命將率師以弱災患，其若與甲兵危士臣，則國耗民竭，喪無日也。")
        if kingb == small:
            result.append("君基與小游同宮，人君宜修德，布恩，明刑，修武，以御奸寇。")
        return "".join(result)
        
    def ming_officerbase(self, ji_style, taiyi_acumyear):
        """明臣基太乙所主術"""
        kingb = self.kingbase(ji_style, taiyi_acumyear)
        officerb = self.officerbase(ji_style, taiyi_acumyear)
        pplb =  self.pplbase(ji_style, taiyi_acumyear)
        wufu = config.num2gong(config.wufu(self.accnum(ji_style, taiyi_acumyear)))
        ty = self.ty_gong(ji_style, taiyi_acumyear)
        tiany = self.skyyi(ji_style, taiyi_acumyear)
        earthy = self.earthyi(ji_style, taiyi_acumyear)
        fgod = self.fgd(ji_style, taiyi_acumyear)
        zhifu = self.zhifu(ji_style, taiyi_acumyear)
        big = config.num2gong(config.bigyo(self.accnum(ji_style, taiyi_acumyear)))
        small = config.num2gong(config.smyo(self.accnum(ji_style, taiyi_acumyear)))
        result = []
        if officerb == wufu:
            result.append("臣基與五福同宮，利於輔宰，貴極人臣，常親帝座，能大任以定治亂，所以臨於分野之方，人民豐稔，其出英俊。")
        if officerb == pplb:
            result.append("臣基與民基同宮，賢者在位，民安其業，政正訟息，而民殷庶。")
        if officerb == tiany:
            result.append("臣基與天乙同宮，有橫逆不義，侵君之位，其分盜賊兵起。")
        if officerb  == earthy:
            result.append("臣基與地乙同宮，其分土工興，而民失務。")
        if officerb == zhifu:
            result.append("臣基與值符同宮，其分禮法不明，民無所止，而有火旱。")
        if officerb == fgod:
            result.append("臣基與四神同宮，其分賦紫稅重，以奪民時而水湧。")
        if officerb == big:
            result.append("臣基與大游同宮，訟政不平，農夫不務，水旱，民力竭而兵荒疫病。")
        if officerb == small:
            result.append("臣基與小游同宮，下侵上，君囚臣，輔宰不利，其分上下不協。")
        return "".join(result)
        
    def ming_pplbase(self, ji_style, taiyi_acumyear):
        """明民基太乙所主術"""
        kingb = self.kingbase(ji_style, taiyi_acumyear)
        officerb = self.officerbase(ji_style, taiyi_acumyear)
        pplb =  self.pplbase(ji_style, taiyi_acumyear)
        wufu = config.num2gong(config.wufu(self.accnum(ji_style, taiyi_acumyear)))
        ty = self.ty_gong(ji_style, taiyi_acumyear)
        tiany = self.skyyi(ji_style, taiyi_acumyear)
        earthy = self.earthyi(ji_style, taiyi_acumyear)
        fgod = self.fgd(ji_style, taiyi_acumyear)
        zhifu = self.zhifu(ji_style, taiyi_acumyear)
        big = config.num2gong(config.bigyo(self.accnum(ji_style, taiyi_acumyear)))
        small = config.num2gong(config.smyo(self.accnum(ji_style, taiyi_acumyear)))
        result = []
        if pplb == wufu:
            result.append("民基與五福同宮，民富而壽家，出賢良。")
        if pplb == tiany:
            result.append("民基與天乙同宮，其分無盜荒，雨雪穀物。")
        if pplb ==earthy:
            result.append("民基與地乙同宮，其分土工役作，妨農禾不收，民多疫災。")
        if pplb ==zhifu:
            result.append("民基與值符同宮，其分火旱傷，飛蝗，兵盜。")
        if pplb ==fgod:
            result.append("民基與四神同宮，其分水旱飢荒，民多流徙。")
        if pplb == big:
            result.append("民基與大游同宮，其分兵火、水旱，人民勞苦。")
        if pplb == small:
            result.append("民基與小游同宮，其分禾稼半收，兵役民苦。")
        return "".join(result)

    def ming_wufu(self, ji_style, taiyi_acumyear):
        """明五福太乙所主術"""
        kingb = self.kingbase(ji_style, taiyi_acumyear)
        officerb = self.officerbase(ji_style, taiyi_acumyear)
        pplb =  self.pplbase(ji_style, taiyi_acumyear)
        wufu = config.num2gong(config.wufu(self.accnum(ji_style, taiyi_acumyear)))
        ty = self.ty_gong(ji_style, taiyi_acumyear)
        tiany = self.skyyi(ji_style, taiyi_acumyear)
        earthy = self.earthyi(ji_style, taiyi_acumyear)
        fgod = self.fgd(ji_style, taiyi_acumyear)
        zhifu = self.zhifu(ji_style, taiyi_acumyear)
        big = config.num2gong(config.bigyo(self.accnum(ji_style, taiyi_acumyear)))
        small = config.num2gong(config.smyo(self.accnum(ji_style, taiyi_acumyear)))
        result = []
        if wufu == kingb:
            result.append("五福與君基同宮，人君福壽祚享，如同宮在初爻之始合，生賢儲。如遇君基相衝之所，乃生草寇之君。")
        if wufu == officerb:
            result.append("五福與臣基同宮，福利輔宰，如同宮在初爻之始，賢相當生貴人之家。")
        if wufu == pplb:
            result.append("五福與民基同宮，四民樂業，天下熙和，如同宮在初交之始，其分富貴人生於白屋之家。")
        if wufu == fgod:
            result.append("五福與四神同宮，為福減損，有兵盜，主有疫，厲民災火，有旱蝗水湧，兩川潰。")
        if wufu == big:
            result.append("五福與大游同宮，為福減半，兵盜水旱不免有之。")
        if wufu == small:
            result.append("五福與小游同宮，有德者昌，無德者殃。")
        return "".join(result)
        
    def wufu_gb(self, ji_style, taiyi_acumyear):
        """明五福吉算所主術"""
        homecal = self.home_cal( ji_style, taiyi_acumyear)
        wufu_good = {tuple([1,11,21,31,41]): "福利於君主。",
                 tuple([2,12,22,32,42]): "福利於王候臣宰。",
                 tuple([3,13,23,33,43]): "福利於后妃。",
                 tuple([4,14,24,34,44]): "福利於太子。",
                 tuple([5,15,25,35,45]): "福利於太子。",
                 tuple([6,16,26,36,46]): "福利於師帥。",
                 tuple([7,17,27,37]): "福利於上將軍。",
                 tuple([8,18,28,38]): "福利於中將軍。",
                 tuple([9,19,29,39]): "福利於下將軍。",
                 tuple([10,20,30,40]): "福利於士卒。"}
        return config.multi_key_dict_get(wufu_good, homecal)

    def ming_tiany(self, ji_style, taiyi_acumyear):
        """明天乙太乙所主術"""
        kingb = self.kingbase(ji_style, taiyi_acumyear)
        officerb = self.officerbase(ji_style, taiyi_acumyear)
        pplb =  self.pplbase(ji_style, taiyi_acumyear)
        wufu = config.num2gong(config.wufu(self.accnum(ji_style, taiyi_acumyear)))
        ty = self.ty_gong(ji_style, taiyi_acumyear)
        tiany = self.skyyi(ji_style, taiyi_acumyear)
        earthy = self.earthyi(ji_style, taiyi_acumyear)
        fgod = self.fgd(ji_style, taiyi_acumyear)
        zhifu = self.zhifu(ji_style, taiyi_acumyear)
        big = config.num2gong(config.bigyo(self.accnum(ji_style, taiyi_acumyear)))
        small = config.num2gong(config.smyo(self.accnum(ji_style, taiyi_acumyear)))
        result = []
        if tiany == ty:
            result.append("天乙與太乙同宮，即有勝負，以金能決斷也。其神經行之分，兵戈大起，多主暴。金兵戮，人民流血千里及霜雪而肅物也。")
        if tiany == earthy:
            result.append("天乙與地乙同宮，其分兵戈發土工興廢農桑傷百姓，交兵結雙仇，盜賊凶攘人民愁困。")
        if tiany == zhifu:
            result.append("天乙與值符同宮，其分火旱刀兵飢饉疾困。")
        if tiany == fgod:
            result.append("天乙與四神同宮，其分水澇、霜雪、兵喪，舟車不通，盜賊四起。")
        if tiany == big:
            result.append("天乙與大游同宮，其分兵喪禍亂，飢兵流亡。")
        if tiany == small:
            result.append("天乙與小游同宮，其分下凌於上，不利其事。")
        return "".join(result)

    def ming_earthy(self, ji_style, taiyi_acumyear):
        """明地乙太乙所主術"""
        kingb = self.kingbase(ji_style, taiyi_acumyear)
        officerb = self.officerbase(ji_style, taiyi_acumyear)
        pplb =  self.pplbase(ji_style, taiyi_acumyear)
        wufu = config.num2gong(config.wufu(self.accnum(ji_style, taiyi_acumyear)))
        ty = self.ty_gong(ji_style, taiyi_acumyear)
        tiany = self.skyyi(ji_style, taiyi_acumyear)
        earthy = self.earthyi(ji_style, taiyi_acumyear)
        fgod = self.fgd(ji_style, taiyi_acumyear)
        zhifu = self.zhifu(ji_style, taiyi_acumyear)
        big = config.num2gong(config.bigyo(self.accnum(ji_style, taiyi_acumyear)))
        small = config.num2gong(config.smyo(self.accnum(ji_style, taiyi_acumyear)))
        result = []
        if earthy == zhifu:
            result.append("地乙與值符同宮，其分大旱、兵盜，土工興，人民受病，五穀不成，農人受困。")
        if earthy == fgod:
            result.append("地乙與四神同宮，其分水旱不調，民多病困，而地中生妖異。")
        if earthy == big:
            result.append("地乙與大游同宮，其分兵喪大作，荒民流，盜賊蜂起。")
        if earthy == small:
            result.append("地乙與小游同宮，其分土木土工興，法令暴虐，主兵盜。")
        return "".join(result)

    def ming_zhifu(self, ji_style, taiyi_acumyear):
        """明值符太乙所主術"""
        kingb = self.kingbase(ji_style, taiyi_acumyear)
        officerb = self.officerbase(ji_style, taiyi_acumyear)
        pplb =  self.pplbase(ji_style, taiyi_acumyear)
        wufu = config.num2gong(config.wufu(self.accnum(ji_style, taiyi_acumyear)))
        ty = self.ty_gong(ji_style, taiyi_acumyear)
        tiany = self.skyyi(ji_style, taiyi_acumyear)
        earthy = self.earthyi(ji_style, taiyi_acumyear)
        fgod = self.fgd(ji_style, taiyi_acumyear)
        zhifu = self.zhifu(ji_style, taiyi_acumyear)
        big = config.num2gong(config.bigyo(self.accnum(ji_style, taiyi_acumyear)))
        small = config.num2gong(config.smyo(self.accnum(ji_style, taiyi_acumyear)))
        result = []
        if zhifu == fgod:
            result.append("值符與四神同宮，其分旱涸乾不均，四時失節，民飢疾疫多生，兵盜溺於水火刀兵之厄。")
        if zhifu == big:
            result.append("值符與大游同宮，其分兵喪民流，五穀不成，突橫暴起。")
        if zhifu == small:
            result.append("值符與小游同宮，其分火炎、兵革，人民不安。")
        return "".join(result)

    def flybird_wl(self,ji_style, taiyi_acumyear):
        """推太乙風雲飛鳥助戰法"""
        fb = config.flybird(taiyi_acumyear)
        hg = self.home_general(ji_style, taiyi_acumyear)
        ag = self.away_general(ji_style, taiyi_acumyear)
        hvg = self.home_vgen(ji_style, taiyi_acumyear)
        avg = self.away_vgen(ji_style, taiyi_acumyear)
        ty = self.ty(ji_style, taiyi_acumyear)
        wc = config.gong2.get(self.skyeyes(ji_style, taiyi_acumyear))
        sj = config.gong2.get(self.sf(ji_style, taiyi_acumyear))
        if fb == ty:
            return "太乙所在宮有風雲飛鳥等來衝格迫擊太乙者，大敗之兆。"
        elif fb == wc:
            return "從主目上去擊客，主勝"
        elif fb == sj:
            return "從客目上去擊主，客勝"
        elif fb == hg or fb == hvg:
            return "飛鳥扶主人陣者，主人勝"
        elif fb == ag or fb == avg:
            return "飛鳥扶客人陣者，客人勝"
        else:
            return "飛鳥方向不明確，和"
    
    def tui_danger(self, ji_style, taiyi_acumyear):
        """推陰陽以占厄會"""
        tai_yi = self.ty(ji_style, taiyi_acumyear)
        tyg = config.num2gong(self.ty(ji_style, taiyi_acumyear))
        homecal = self.home_cal( ji_style, taiyi_acumyear) 
        awaycal = self.away_cal( ji_style, taiyi_acumyear) 
        tyd = config.multi_key_dict_get({tuple([8,3,4,9]): "太乙在陽宮。", tuple([1,2,6,7]): "太乙在陰宮。"}, tai_yi)
        if homecal % 2 != 0 and tyd == "太乙在陽宮。":
            hr = "太乙在陽宮，主筭得奇，為重陽，厄在火，主厄。"
        if homecal % 2 != 0 and tyd != "太乙在陽宮。":
            hr = "太乙在陰宮，主筭得奇，主沒厄。"
        if homecal % 2 == 0 and tyd != "太乙在陰宮。":
            hr = "太乙在陽宮，主筭得偶，主沒厄。"
        if homecal % 2 == 0 and tyd == "太乙在陰宮。":
            hr = "太乙在陰宮，主筭得偶，為重陰，厄在水，主厄。"
        if awaycal % 2 != 0 and tyd == "太乙在陽宮。":
            ar = "太乙在陽宮，客筭得奇，為重陽，厄在火，客厄。"
        if awaycal % 2 != 0 and tyd != "太乙在陽宮。":
            ar = "太乙在陰宮，客筭得奇，客沒厄。"
        if awaycal % 2 == 0 and tyd != "太乙在陰宮。":
            ar = "太乙在陽宮，客筭得偶，客沒厄。"
        if awaycal % 2 == 0 and tyd == "太乙在陰宮。":
            ar = "太乙在陰宮，客筭得偶，為重陰，厄在水，客厄。"
        return hr + ar

    def ty_gong_dist(self, ji_style, taiyi_acumyear):
        """太乙在天外地內法"""
        tai_yi = self.ty(ji_style, taiyi_acumyear)
        tyg = config.num2gong(self.ty(ji_style, taiyi_acumyear))
        return config.multi_key_dict_get({tuple([1,8,3,4]): "太乙在"+tyg+"，助主。", tuple([9,2,6,7]): "太乙在"+tyg+"，助客。"}, tai_yi)

    def threedoors(self, ji_style, taiyi_acumyear):
        """推三門具不具"""
        taiyi = self.ty(ji_style, taiyi_acumyear)
        eightd = self.geteightdoors(ji_style, taiyi_acumyear)
        door = eightd.get(taiyi)
        if door in list("休生開"):
            return "三門不具。"
        return "三門具。"

    def fivegenerals(self, ji_style, taiyi_acumyear):
        """推五將發不發"""
        home_general = self.home_general(ji_style, taiyi_acumyear)
        away_general = self.away_general(ji_style, taiyi_acumyear)
        if self.skyeyes_des(ji_style, taiyi_acumyear) == "" and home_general != 5 and away_general != 5:
            return "五將發。"
        if home_general == 5:
            return "主將主參不出中門，杜塞無門。"
        if away_general == 5:
            return "客將客參不出中門，杜塞無門。"
        return self.skyeyes_des(ji_style, taiyi_acumyear)+"。五將不發。"

    def wc_n_sj(self, ji_style, taiyi_acumyear):
        """推主客相闗法"""
        wan_c = self.skyeyes(ji_style, taiyi_acumyear)
        shi_ji = self.sf(ji_style, taiyi_acumyear)
        wc_f = config.Ganzhiwuxing(wan_c)
        sj_f = config.Ganzhiwuxing(shi_ji)
        home_g = self.home_general(ji_style, taiyi_acumyear)
        tai_yi = self.ty(ji_style, taiyi_acumyear)
        hguan = config.multi_key_dict_get(config.nayin_wuxing, config.gangzhi(self.year, self.month, self.day, self.hour, self.minute)[3])
        if hguan == wc_f:
            guan = "主關"
        if hguan == sj_f:
            guan = "客關"
        else:
            guan = "關"
        relation = config.multi_key_dict_get(config.wuxing_relation_2, wc_f+sj_f)
        if relation == "我尅" and tai_yi == home_g:
            return "主將囚，不利主"
        if relation == "我尅" and tai_yi != home_g:
            return  "主尅客，主勝"
        if relation == "尅我":
            return guan + "得主人，客勝"
        if relation in ["比和","生我","我生"]:
            return guan + relation + "，和"

    def geteightdoors(self, ji_style, taiyi_acumyear):
        """推八門分佈"""
        tai_yi = self.ty(ji_style, taiyi_acumyear)
        new_ty_order = config.new_list([8,3,4,9,2,7,6,1], tai_yi)
        doors  = config.new_list(self.door, config.eight_door(self.accnum(ji_style, taiyi_acumyear)))
        if ji_style != 3:
            return dict(zip(new_ty_order, doors))
        if ji_style == 3:
            alljq = jieqi_name
            j_q = jieqi.jq(self.year, self.month, self.day, self.hour, self.minute)
            jqmap = {tuple(config.new_list(alljq, "冬至")[0:12]):"冬至", tuple(config.new_list(alljq, "夏至")[0:12]):"夏至"}
            num= self.accnum(ji_style, taiyi_acumyear)
            dun = config.multi_key_dict_get(jqmap, j_q)
            if dun == "夏至":    
                num= num% 120 % 30
                if num> 8:
                    num= num%8
                if num==0:
                    num=8
                num= dict(zip(range(1,9), new_ty_order)).get(num)
                return dict(zip(config.new_list(new_ty_order, num), doors)) 
            if dun == "冬至":
                num= num% 240 % 30
                if num> 8:
                    num= num%8
                if num==0:
                    num=8
                num= dict(zip(range(1,9), new_ty_order)).get(num)
                return dict(zip(config.new_list(new_ty_order, num), doors)) 

    def geteightdoors_text(self, ji_style, taiyi_acumyear):
        k = [an2cn(i) for i in list(self.geteightdoors(ji_style, taiyi_acumyear).keys())]
        v = list(self.geteightdoors(ji_style, taiyi_acumyear).values())
        eightdoors = dict(zip(k,v))
        return str(eightdoors)[1:-1].replace("'", "").replace(",", " |")

    def geteightdoors_text2(self, ji_style, taiyi_acumyear):
        doors = self.geteightdoors(ji_style, taiyi_acumyear)
        k = [an2cn(i) for i in doors.keys()]
        v = list(doors.values())
        eightdoors = dict(zip(k, v))
        wang_map = jieqi.gong_wangzhuai(
            jieqi.jq(self.year, self.month, self.day, self.hour, self.minute)
        )
        eightddors_status = dict(zip(k, list(wang_map.values())))
        year_gan = config.gangzhi(
            self.year, self.month, self.day, self.hour, self.minute,
        )[0][0]
        star_dist = config.taiyi_nine_stars(
            self.accnum(ji_style, taiyi_acumyear), year_gan,
        ).get("九星分布", {})
        god_dist = config.nine_palace_gods(
            self.accnum(ji_style, taiyi_acumyear),
        ).get("九宮貴神分布", {})
        rows = []
        for gong_cn in config.new_list(list(eightdoors.keys()), "二"):
            gong_num = cn2an(gong_cn)
            luoshu = config._LUOSHU_GONG.get(gong_num, "")
            star_full = star_dist.get(luoshu, "")
            star_short = star_full[1:] if star_full.startswith("天") else star_full
            wx = eightddors_status.get(gong_cn, "")
            wx_star = f"{wx}{star_short}" if wx and star_short else (wx or star_short)
            door = eightdoors.get(gong_cn)
            god_full = god_dist.get(luoshu, "")
            god_short = config.NINE_GOD_CHART_LABEL.get(god_full, "")
            rows.append([gong_cn, door, wx_star, god_short, god_full])
        return rows

    #陽九行限
    def yangjiu_xingxian(self, sex):
        mg = config.gangzhi(self.year, self.month, self.day, self.hour, self.minute)[1][0]
        num= config.Ganzhi_num(mg)
        place = config.Ganzhi_place(mg)
        return dict(zip(config.generate_ranges(num, 10, 11),{"男":config.new_list(self.di_zhi, place), "女":config.new_list(list(reversed(self.di_zhi)), place)}.get(sex)))
    #百六行限
    def shouqi_ganzhi(self):
        """受氣干支：日時納音策餘，自生日逆行（卷二十）。"""
        gz = config.gangzhi(self.year, self.month, self.day, self.hour, self.minute)
        jz = config.jiazi()
        day_idx = jz.index(gz[2])
        rem = self.souqi_num() or 60
        return jz[(day_idx - rem + 1) % 60]

    def bailiu_xingxian(self, sex):
        sqn_gua = self.shouqi_ganzhi()
        place = config.Ganzhi_place(sqn_gua[0])
        num = dict(zip(list("土金水木火"), [5, 4, 1, 3, 2])).get(
            config.Ganzhiwuxing(sqn_gua[0])
        )
        return dict(zip(
            config.generate_ranges(num, 10, 11),
            {
                "男": config.new_list(self.di_zhi, place),
                "女": config.new_list(list(reversed(self.di_zhi)), place),
            }.get(sex),
        ))

    def souqi_num(self):
        gz = config.gangzhi(self.year, self.month, self.day, self.hour, self.minute)
        dg = config.gangzhi_to_num(gz[2][0])
        dz = config.gangzhi_to_num(gz[2][1])
        hg = config.gangzhi_to_num(gz[3][0])
        hz = config.gangzhi_to_num(gz[3][1])
        dny = config.element_to_num(config.multi_key_dict_get(config.nayin_wuxing, gz[2]))
        hny = config.element_to_num(config.multi_key_dict_get(config.nayin_wuxing, gz[3]))
        return (dg + dz + hg + hz + dny + hny + 55) % 60 

    #出身卦
    def life_start_gua(self):
        gz = config.gangzhi(self.year, self.month, self.day, self.hour, self.minute)
        y = config.gangzhi_to_num(gz[0][0]) + config.gangzhi_to_num(gz[0][1]) + config.element_to_num(config.multi_key_dict_get(config.nayin_wuxing, gz[0]))
        m = config.gangzhi_to_num(gz[1][0]) + config.gangzhi_to_num(gz[1][1]) + config.element_to_num(config.multi_key_dict_get(config.nayin_wuxing, gz[1]))
        d = config.gangzhi_to_num(gz[2][0]) + config.gangzhi_to_num(gz[2][1]) + config.element_to_num(config.multi_key_dict_get(config.nayin_wuxing, gz[2]))
        h = config.gangzhi_to_num(gz[3][0]) + config.gangzhi_to_num(gz[3][1]) + config.element_to_num(config.multi_key_dict_get(config.nayin_wuxing, gz[3]))
        return [(y + m + d + h + 55) % 64, config.gua.get((y + m + d + h + 55) % 64)]

    def year_gua(self):
        if self.year >= 1:
            d = date(self.year, self.month, self.day)
        else:
            d = date(1, 1, 1)
        num= self.life_start_gua()[0] + config.calculateAge(d)
        if num> 64:
            return [num, config.gua.get(num% 64)]
        else:
            return [num, config.gua.get(num)]
        
    def month_gua(self):
        year = self.year_gua()[0]
        month = config.lunar_date_d(self.year, self.month, self.day).get("月")
        num= year + 2 + month
        if num> 64:
            return [num, config.gua.get(num% 64)]
        else:
            return [num, config.gua.get(num)]
        
    def day_gua(self):
        month  = self.month_gua()[0]
        day = dict(zip(config.jiazi(), range(1,61))).get(config.gangzhi(self.year, self.month, self.day, self.hour, self.minute)[2])
        num= month + day
        if num> 64:
            return [num, config.gua.get(num% 64)]
        else:
            return [num, config.gua.get(num)]
        
    def hour_gua(self):
        day = self.day_gua()[0]
        hour = dict(zip(self.di_zhi, range(1,13))).get(config.gangzhi(self.year, self.month, self.day, self.hour, self.minute)[3][1])
        num= day + hour
        if num> 64:
            return [num, config.gua.get(num% 64)]
        else:
            return [num, config.gua.get(num)]
        
    def minute_gua(self):
        hour = self.hour_gua()[0]
        minute = dict(zip(config.jiazi(), range(1,61))).get(config.gangzhi(self.year, self.month, self.day, self.hour, self.minute)[4])
        num= hour + minute
        if num> 64:
            return [num, config.gua.get(num% 64)]
        else:
            return [num, config.gua.get(num)]

    def year_chin(self):
        """太歲禽星"""
        su = config.su
        chin_28_stars_code = dict(zip(range(1,29), su))
        year = config.lunar_date_d(self.year, self.month, self.day).get("年")
        if config.lunar_date_d(self.year, self.month, self.day).get("月") == "十二月" or config.lunar_date_d(self.year, self.month, self.day).get("月") == "十一月":
            if jieqi.jq(self.year, self.month, self.day, self.hour, self.minute) == "立春":
                get_year_chin_number = (int(year)+15) % 28 #求年禽之公式為西元年加15除28之餘數
                if get_year_chin_number == int(0):
                    get_year_chin_number = int(28)
                year_chin = chin_28_stars_code.get(get_year_chin_number) #年禽
            else:
                get_year_chin_number = (int(year-1)+15) % 28 #求年禽之公式為西元年加15除28之餘數
                if get_year_chin_number == int(0):
                    get_year_chin_number = int(28)
                    year_chin = chin_28_stars_code.get(get_year_chin_number) #年禽
        if config.lunar_date_d(self.year, self.month, self.day).get("月") != "十二月" or config.lunar_date_d(self.year, self.month, self.day).get("月") == "十一月":
            get_year_chin_number = (int(year)+15) % 28 #求年禽之公式為西元年加15除28之餘數
            if get_year_chin_number == int(0):
                get_year_chin_number = int(28)
            year_chin = chin_28_stars_code.get(get_year_chin_number) #年禽
        return year_chin

    def gen_gong(self, ji_style, taiyi_acumyear, tenching): #有十精1, 無十精0
        res2 = { "午":" ", "未":" ", "申":" ", "酉":" ", "戌":" ", "亥":" ", "子":" ", "丑":" ","寅":" ", "卯":" ", "辰":" ", "巳":" "}
        stars = find_stars(self.year, self.month, self.day, self.hour, self.minute)
        sixteengongs = {0: self.sixteen_gong3( ji_style, taiyi_acumyear), 1:self.sixteen_gong( ji_style, taiyi_acumyear) }.get(tenching)
        for planet, zhi in stars.items():
            if res2[zhi] == " ":           # 原本是空的
                res2[zhi] = planet
            else:                          # 已有行星，追加
                res2[zhi] += planet        # 或 res2[zhi] += " " + planet
        ss = [list(res2.values())]
        # 定義所有可能的行星名稱（按長度從長到短排序，避免錯拆）
        planets = ['日　', '月　', '辰星', '太白', '熒惑', '歲星', '填星', '月孛', '羅睺','計都']
        
        # 轉換函數
        def split_planets(cell):
            if cell == ' ' or not cell:
                return []
            # 依序嘗試匹配最長的行星名
            result = []
            remaining = cell
            while remaining:
                matched = False
                for p in planets:
                    if remaining.startswith(p):
                        result.append(p)
                        remaining = remaining[len(p):]
                        matched = True
                        break
                if not matched:
                    # 如果有意外字元（理論上不會），直接中斷
                    break
            return result
        
        # 應用到整個結構
        ss1 = [[split_planets(cell) for cell in row] for row in ss]
        # —— 三旗行宮旗旆（卷十）+ 八卦天盤活盤旋轉（隨太乙落宮）——
        _sanqi = config.sanqi(self.accnum(ji_style, taiyi_acumyear))
        _ty_v = self.ty(ji_style, taiyi_acumyear)
        _eight_order = [1, 2, 3, 4, 6, 7, 8, 9]
        _ty_idx = _eight_order.index(_ty_v) if _ty_v in _eight_order else 0
        _yun = self.kook(ji_style, taiyi_acumyear).get("文", ["陽"])[0]
        _trigram_rotate = _ty_idx * 45.0 + (180.0 if _yun == "陰" else 0.0)
        if ji_style in [0,1]:
            return chart.gen_chart( list(sixteengongs.values())[-1], self.geteightdoors_text2(ji_style, taiyi_acumyear), list(sixteengongs.values())[:-1], ss1[0], sanqi=_sanqi, trigram_rotate=_trigram_rotate)
        if ji_style in [2]:
            dict1 = config.gpan1(self.year, self.month, self.day, self.hour, self.minute)
            middle = dict1[0][1]
            ng = dict1[1]
            return chart.gen_chart_day( list(sixteengongs.values())[-1] + [middle], self.geteightdoors_text2(ji_style, taiyi_acumyear), ng, list(sixteengongs.values())[:-1], ss1[0], sanqi=_sanqi, trigram_rotate=_trigram_rotate)
        if ji_style in [3,4]:
            #j_q = jieqi.jq(self.year, self.month, self.day, self.hour, self.minute)
            #d = config.gangzhi(self.year, self.month, self.day, self.hour, self.minute)[2]
            #h = config.gangzhi(self.year, self.month, self.day, self.hour, self.minute)[2]
            #m = config.lunar_date_d(self.year, self.month, self.day).get("月")
            #sg = [ kinliuren.Liuren(j_q, m, d, h).result(0).get("地轉天將").get(i) for i in list("巳午未申酉戌亥子丑寅卯辰")]
            earth_sky = self.lr().sky_n_earth_list()
            g = dict(zip(list("貴蛇雀合勾龍空虎常玄陰后"), re.findall('..', '貴人螣蛇朱雀六合勾陳青龍天空白虎太常玄武太陰天后')))
            general = self.lr().result(0).get("地轉天將")
            k = list(general.keys())
            v = list(general.values())
            vnew = [g.get(i) for i in v]
            general = dict(zip(k, vnew))
            #three_passes = [i[0]+self.lr().result(0).get("三傳").get(i)[0]+self.lr().result(0).get("三傳").get(i)[1][0] for i in ['初傳','中傳','末傳']]
            res = {"巳":" ", "午":" ", "未":" ", "坤":" ", "申":" ", "酉":" ", "戌":" ", "乾":" ", "亥":" ", "子":" ", "丑":" ", "艮":" ","寅":" ", "卯":" ", "辰":" ", "巽":" "}
            res1 = {"巳":" ", "午":" ", "未":" ", "坤":" ", "申":" ", "酉":" ", "戌":" ", "乾":" ", "亥":" ", "子":" ", "丑":" ", "艮":" ","寅":" ", "卯":" ", "辰":" ", "巽":" "}
            
            
            res.update(general)
            res1.update(earth_sky)
            
            sg = [[list(res.values())[i], list(res1.values())[i] ] for i in range(0,len(list(res.values())))]
            star_degrees = dict(zip(config.su,get_xiu_degrees(self.year)))
            new_degrees = [star_degrees.get(i) for i in self.twenty_eightstar(ji_style, taiyi_acumyear)]
            return chart.gen_chart_hour( list(sixteengongs.values())[-1]+[" "," "], self.geteightdoors_text2(ji_style, taiyi_acumyear), sg,list(sixteengongs.values())[:-1], self.twenty_eightstar(ji_style, taiyi_acumyear), ss1[0], new_degrees, sanqi=_sanqi, trigram_rotate=_trigram_rotate)
#太乙命法
    def gen_life_gong(self, sex, ji_style: int = 4):
        stars = find_stars(self.year, self.month, self.day, self.hour, self.minute)
        res2 = { "午":" ", "未":" ", "申":" ", "酉":" ", "戌":" ", "亥":" ", "子":" ", "丑":" ","寅":" ", "卯":" ", "辰":" ", "巳":" "}
        res = {"巳":" ", "午":" ", "未":" ", "申":" ", "酉":" ", "戌":" ", "亥":" ", "子":" ", "丑":" ","寅":" ", "卯":" ", "辰":" "}
        for planet, zhi in stars.items():
            if res2[zhi] == " ":           # 原本是空的
                res2[zhi] = planet
            else:                          # 已有行星，追加
                res2[zhi] += planet        # 或 res2[zhi] += " " + planet
        ss = [list(res2.values())]
        # 定義所有可能的行星名稱（按長度從長到短排序，避免錯拆）
        planets = ['日', '月', '辰星', '太白', '熒惑', '歲星', '填星', '月孛', '羅睺','計都']
        
        # 轉換函數
        def split_planets(cell):
            if cell == ' ' or not cell:
                return []
            # 依序嘗試匹配最長的行星名
            result = []
            remaining = cell
            while remaining:
                matched = False
                for p in planets:
                    if remaining.startswith(p):
                        result.append(p)
                        remaining = remaining[len(p):]
                        matched = True
                        break
                if not matched:
                    # 如果有意外字元（理論上不會），直接中斷
                    break
            return result
        
        # 應用到整個結構
        ss1 = [[split_planets(cell) for cell in row] for row in ss]
        res.update(self._twelve_palace_map(sex))
        sg = list(res.values())
        _sanqi = config.sanqi(self.accnum(0, 0))
        _ty_v = self.ty(ji_style, 0)
        _eight_order = [1, 2, 3, 4, 6, 7, 8, 9]
        _ty_idx = _eight_order.index(_ty_v) if _ty_v in _eight_order else 0
        _trigram_rotate = _ty_idx * 45.0
        _sixteen = self.sixteen_gong11(ji_style, 0)
        from .mingfa import life_chart_annotations  # noqa: PLC0415

        ann = life_chart_annotations(self, sex, plate_ji=ji_style)
        return chart.gen_chart_life(
            list(_sixteen.values())[-1], sg,
            [_sixteen.get(i) for i in list(res.keys())],
            ss1[0],
            sanqi=_sanqi,
            trigram_rotate=_trigram_rotate,
            center_lines=ann.get("center_lines"),
            branch_tags=ann.get("branch_tags"),
        )

    def _twelve_palace_map(self, sex):
        """十二命宮地支→宮名（供命法排盤，避免 gen_life_gong_list 遞迴 taiyi_life）。"""
        twelve_gongs = "命宮,兄弟,妻妾,子孫,財帛,田宅,官祿,奴僕,疾厄,福德,相貌,父母".split(",")
        gz = config.gangzhi(self.year, self.month, self.day, self.hour, self.minute)
        yz, mz = gz[0][1], gz[1][1]
        yy = config.multi_key_dict_get({tuple(self.di_zhi[0::2]): "陽", tuple(self.di_zhi[1::2]): "陰"}, yz)
        direction = config.multi_key_dict_get({("男陽", "女陰"): "順", ("男陰", "女陽"): "逆"}, sex + yy)
        zhinum = dict(zip(self.di_zhi, range(1, 13)))
        yz_arrange = dict(zip(range(1, 13), config.new_list(self.di_zhi, yz)))[zhinum[yz]]
        mz_arrange = dict(zip(range(1, 13), config.new_list(self.di_zhi, yz_arrange)))[zhinum[mz]]
        mz_arrange_r = dict(zip(range(1, 13), config.new_list(list(reversed(self.di_zhi)), yz_arrange)))[zhinum[mz]]
        arrangelist = {"順": config.new_list(self.di_zhi, mz_arrange_r), "逆": config.new_list(self.di_zhi, mz_arrange)}.get(direction)
        return dict(zip(arrangelist, twelve_gongs))

    def gen_life_gong_list(self, sex, plate_ji: int = 4):
        res = {"巳":" ", "午":" ", "未":" ", "申":" ", "酉":" ", "戌":" ", "亥":" ", "子":" ", "丑":" ","寅":" ", "卯":" ", "辰":" "}
        dict1 = self._twelve_palace_map(sex)
        res.update(dict1)
        sg = list(res.values())
        sixteen = self.sixteen_gong11(plate_ji, 0)
        return list(sixteen.values())[-1], sg, [sixteen.get(i) for i in list(res.keys())]

    def convert_gongs_text(self, a, b):
        c = {}
        for key in set(a.keys()).union(b.keys()):
            value_a = a.get(key, [])
            value_b = b.get(key, [])
            if isinstance(value_a, list) and isinstance(value_b, list):
                c[key] = value_a + [value_b]
            else:
                c[key] = value_a if value_a else value_b
        text_output = ""
        for key, value in c.items():
            if isinstance(value, list):
                value_str = ', '.join(map(str, value))
                text_output += f"【{key}】\n{value_str}\n\n"
            else:
                text_output += f"【{key}】\n{value}\n\n"
        return text_output.replace('[', '').replace(']', '').replace(',', '').replace("'","")

    def gongs_discription_text(self, sex, plate_ji: int = 4):
        alld = self.gongs_discription_list(sex, plate_ji)
        combined_dict = {}
        for category, subcategories in alld.items():
            combined_dict[category] = []
            for subcategory in subcategories:
                if subcategory in taiyi_life_dict.twelve_gong_stars[category]:
                    combined_dict[category].append(taiyi_life_dict.twelve_gong_stars[category][subcategory])
        formatted_text = ""
        for key, value in combined_dict.items():
            formatted_text += f"{key}:\n"
            if value:
                formatted_text += "\n".join([f"{line}\n" for line in value])
            formatted_text += "\n"
        return formatted_text
        
    def twostar_disc(self, sex, plate_ji: int = 4):
        a = taiyi_life_dict.twostars
        b = self.gongs_discription_list(sex, plate_ji)
        b = {key: [''.join(value)] for key, value in b.items()}
        c = {}
        for key, values in b.items():
            c[key] = []
            for val in values:
                val_set = set(val)  # 轉成集合
                sub_dict = [
                    k + "同宮。" + a[k] 
                    for k in a 
                    if set(k) <= val_set  # k 是 val_set 的子集
                ]
                c[key].append(sub_dict)
        for key, values in c.items():
            c[key] = [item for item in values[0] if item]  # Remove empty lists
        return c
        
    def gongs_discription_list(self, sex, plate_ji: int = 4):
        _, t, stars = self.gen_life_gong_list(sex, plate_ji)
        alld = dict(zip(t, stars))
        for key, value in alld.items():
            if not value:
                alld[key] = ["空格"]
        return alld
    
    def gongs_discription(self, sex, plate_ji: int = 4):
        alld = self.gongs_discription_list(sex, plate_ji)
        combined_dict = {}
        for category, subcategories in alld.items():
            combined_dict[category] = []
            for subcategory in subcategories:
                if subcategory in taiyi_life_dict.twelve_gong_stars[category]:
                    combined_dict[category].append(taiyi_life_dict.twelve_gong_stars[category][subcategory])
        return combined_dict
    
    
    def sixteen_gong2(self, ji_style, taiyi_acumyear, *, life_ring: bool = False):
        original_dict = (
            self.sixteen_gong11(ji_style, taiyi_acumyear)
            if life_ring
            else self.sixteen_gong1(ji_style, taiyi_acumyear)
        )
        c = "五福,君基,臣基,民基,文昌,計神,小游,主大,客大,主參,客參,始擊,飛符,四神,天乙,地乙".split(",")
        a = {star: key for key, values in original_dict.items() for star in values if star in c}
        d = dict(zip(self.di_zhi, range(0, 13)))
        for star, gong_value in a.items():
            a[star] = d[gong_value]
        return a

    def stars_descriptions(self, ji_style, taiyi_acumyear, *, life_ring: bool = False):
        starszhi = self.sixteen_gong2(ji_style, taiyi_acumyear, life_ring=life_ring)
        c = "五福,君基,臣基,民基,文昌,計神,小游,主大,客大,主參,客參,始擊,飛符,四神,天乙,地乙".split(",")
        allstar = {}
        for i in c:
            try:
                a = {i:taiyi_life_dict.stars_twelve.get(i)[starszhi.get(i)]}
                allstar.update(a)
            except IndexError:
                pass
        return allstar

    def stars_descriptions_text(self, ji_style, taiyi_acumyear, *, life_ring: bool = False):
        alld = self.stars_descriptions(ji_style, taiyi_acumyear, life_ring=life_ring)
        text = ""
        for key, value in alld.items():
            text += f"【{key}】\n{value}\n\n"
        return text

    def sixteen_gong_grades(self, ji_style, taiyi_acumyear, *, life_ring: bool = False):
        original_dict = (
            self.sixteen_gong11(ji_style, taiyi_acumyear)
            if life_ring
            else self.sixteen_gong1(ji_style, taiyi_acumyear)
        )
        c = (
            "五福,君基,臣基,民基,小游,文昌,主大,主參,計神,始擊,客大,客參,四神,天乙,地乙"
            if life_ring
            else "五福,君基,臣基,民基,小游,文昌,主大,主參,計神,始擊,客大,客參,四神,天乙,地乙,直符"
        ).split(",")
        a = {star: key for key, values in original_dict.items() for star in values if star in c}
        alld = {
            star: config.multi_key_dict_get(taiyi_life_dict.sixteen_three_grades[star], a.get(star))
            for star in c
            if star in taiyi_life_dict.sixteen_three_grades
        }
        text = ""
        for key, value in alld.items():
            text += f"【{key}】\n{value}\n\n"
        return text
    
    def taiyi_life(self, sex, plate_ji: int = 4):
        gz = config.gangzhi(self.year, self.month, self.day, self.hour, self.minute)
        yz = gz[0][1]
        mz = gz[1][1]
        dz = gz[2][1]
        hz = gz[3][1]
        self.di_zhi = self.di_zhi
        skypan = dict(zip(config.new_list(self.di_zhi, mz), config.new_list(list(reversed(self.di_zhi)), hz)))
        yy = config.multi_key_dict_get({tuple(self.di_zhi[0::2]):"陽", tuple(self.di_zhi[1::2]):"陰"}, yz)
        direction =  config.multi_key_dict_get({("男陽","女陰"):"順", ("男陰", "女陽"):"逆"}, sex+yy)
        zhinum = dict(zip(self.di_zhi,range(1,13)))
        palace_map = self._twelve_palace_map(sex)
        arrangelist = list(palace_map.keys())
        #身宮排法
        mz1_arrange = dict(zip(range(1,13),config.new_list(self.di_zhi,mz)))[zhinum[mz]]
        dz_arrange =  dict(zip(range(1,13),config.new_list(self.di_zhi,mz1_arrange)))[zhinum[dz]]
        dz_arrange_r = dict(zip(range(1,13),config.new_list(list(reversed(self.di_zhi)),dz_arrange)))[zhinum[dz]]
        d_arrangelist = {"順":config.new_list(self.di_zhi, dz_arrange_r), "逆":config.new_list(self.di_zhi, dz_arrange)}.get(direction)
        #長生
        fly_lu = config.multi_key_dict_get({tuple(list("甲乙")):"亥", tuple(list("丙丁")):"寅", tuple(list("戊己")):"午", tuple(list("庚辛")):"巳",tuple(list("壬癸")):"申" }, gz[0][0])
        fly_horse = config.multi_key_dict_get({tuple(list("甲乙")):"亥", tuple(list("丙丁")):"寅", tuple(list("戊己")):"午", tuple(list("庚辛")):"巳",tuple(list("壬癸")):"申" }, gz[3][0])
        blackfu = config.multi_key_dict_get(dict(zip(list("甲乙丙丁戊己庚辛壬癸"), list("寅卯子亥戌酉申未午巳"))), gz[3][0])
        pan = {
                "性別":"{}{}".format(yy,sex),
                "出生日期":config.gendatetime(self.year, self.month, self.day, self.hour, self.minute),
                "出生干支":config.gangzhi(self.year, self.month, self.day, self.hour, self.minute),
                "農曆":config.lunar_date_d(self.year, self.month, self.day),
                "紀元":self.jiyuan(0,0),
                "太歲":self.taishui(0),
                "命局":self.kook(0,0),
                "安命宮":arrangelist[0],
                "安身宮":d_arrangelist[0],
                "飛祿":fly_lu,
                "飛馬":fly_horse,
                "黑符":blackfu,
                "天盤":skypan,
                "十二命宮排列": palace_map,
                "陽九":config.yangjiu(self.year, self.month, self.day),
                "百六":config.baliu(self.year, self.month, self.day),
                "陽九行限": self.yangjiu_xingxian(sex),
                "百六行限": self.bailiu_xingxian(sex),
                "太乙落宮":self.ty(0,0),
                "出身卦":self.life_start_gua()[1],
                "年卦":self.year_gua()[1], 
                "月卦":self.month_gua()[1], 
                "日卦":self.day_gua()[1], 
                "時卦":self.hour_gua()[1], 
                "分卦":self.minute_gua()[1], 
                "太乙":self.ty_gong(0,0),
                "天乙":self.skyyi(0,0),
                "地乙":self.earthyi(0,0),
                "四神":self.fgd(0,0),
                "直符":self.zhifu(0,0),
                "文昌":[self.skyeyes(0,0), self.skyeyes_des(0,0)],
                "始擊":self.sf(0,0),
                "主算":[self.home_cal(0,0), config.cal_des(self.home_cal(0,0))],
                "主將":self.home_general(0,0),
                "主參":self.home_vgen(0,0),
                "客算":[self.away_cal(0,0), config.cal_des(self.away_cal(0,0))],
                "客將":self.away_general(0,0),
                "客參":self.away_vgen(0,0),
                "定算":[self.set_cal(0,0), config.cal_des(self.set_cal(0,0))],
                "合神":self.hegod(0),
                "計神":self.jigod(0),
                "定目":self.se(0,0),
                "君基":self.kingbase(0,0),
                "臣基":self.officerbase(0,0),
                "民基":self.pplbase(0,0),
                "五福":config.wufu(self.accnum(0,0)),
                "帝符":config.kingfu(self.accnum(0,0)),
                "太尊":config.taijun(self.accnum(0,0)),
                "飛鳥":config.flybird(self.accnum(0,0)),
                "三風":config.threewind(self.accnum(0,0)),
                "五風":config.fivewind(self.accnum(0,0)),
                "八風":config.eightwind(self.accnum(0,0)),
                "大游":config.bigyo(self.accnum(0,0)),
                "小游":config.smyo(self.accnum(0,0)),
                }
        from .mingfa import zonghe as mingfa_zonghe  # noqa: PLC0415
        from .shiti_jinfu import match_life  # noqa: PLC0415
        pan["十提金賦"] = match_life(self, sex, life=pan, plate_ji=plate_ji)
        pan["十二宮星斷"] = self.gongs_discription(sex, plate_ji)
        pan["雙星同宮論"] = self.twostar_disc(sex, plate_ji)
        pan["諸星上中下三等"] = self.sixteen_gong_grades(plate_ji, 0, life_ring=True)
        pan["卷二十"] = mingfa_zonghe(self, sex, plate_ji=plate_ji)
        return pan

    def shiti_jinfu(self, sex, plate_ji: int = 4):
        """太乙十提金賦（卷二十）：依命身宮及十二宮星曜匹配賦文。"""
        from .shiti_jinfu import match_life  # noqa: PLC0415
        return match_life(self, sex, plate_ji=plate_ji)

    def shiti_jinfu_text(self, sex, plate_ji: int = 4):
        from .shiti_jinfu import format_text, match_life  # noqa: PLC0415
        return format_text(match_life(self, sex, plate_ji=plate_ji))
    
    def shi_geju(self, ji_style, taiyi_acumyear):
        """釋格局：依《太乙統宗寶鑑》卷四「釋掩迫關囚擊格對提挾執提四郭固四郭社」

        動態推算太乙與文昌、始擊、定目、主客四將、八門之間的十一種格局，
        補足原 pan() 僅以查表(skyeyes_des)呈現文昌格局之不足。
        各格局定義皆依卷四原文：
          掩＝始擊臨太乙宮；囚＝文昌或諸將與太乙同宮；關＝主客四將同宮；
          格＝客目始擊或客二將在太乙對宮；對＝文昌與太乙相對；
          迫＝二目四將定計在太乙前一辰/前一宮(外)或後(內)；
          擊＝始擊在太乙前一辰/前一宮(外)或後(內)；
          提挾＝二目與四將挾太乙；執提＝太乙與開生門合(執)或衝(提格)；
          四郭固＝文昌囚太乙宮且主二將相關，或客目臨太乙宮且客主二將相關。
        """
        sixteen = list(config.sixteen)
        chen2gong = config.gong2
        gong2chen = {}
        for _ch, _p in chen2gong.items():
            gong2chen.setdefault(_p, []).append(_ch)
        eight_order = [1, 2, 3, 4, 6, 7, 8, 9]   # 太乙順行八宮序
        opp = {1: 9, 9: 1, 2: 8, 8: 2, 3: 7, 7: 3, 4: 6, 6: 4}

        def gong_of_chen(ch):
            return chen2gong.get(ch)

        ty = self.ty(ji_style, taiyi_acumyear)
        wc = self.skyeyes(ji_style, taiyi_acumyear)
        sj = self.sf(ji_style, taiyi_acumyear)
        se = self.se(ji_style, taiyi_acumyear)
        hd = self.home_general(ji_style, taiyi_acumyear)
        hv = self.home_vgen(ji_style, taiyi_acumyear)
        ad = self.away_general(ji_style, taiyi_acumyear)
        av = self.away_vgen(ji_style, taiyi_acumyear)
        generals = [("主大", hd), ("主參", hv), ("客大", ad), ("客參", av)]
        results = {}

        # 釋掩：始擊臨太乙宮為掩
        if gong_of_chen(sj) == ty:
            results["掩"] = "始擊臨太乙宮，陰盛陽衰、君弱臣強之象"

        # 釋囚：文昌與太乙同宮為關囚；諸將與太乙同宮為囚
        if gong_of_chen(wc) == ty:
            results["關囚(文昌)"] = "文昌與太乙同宮，拘繫執正，不利為主"
        for nm, g in generals:
            if g == ty and g != 5:
                results[f"囚({nm})"] = f"{nm}與太乙同宮為囚，下犯上之象"

        # 釋關：主客四將同宮為關
        for i in range(len(generals)):
            for j in range(i + 1, len(generals)):
                if generals[i][1] == generals[j][1] and generals[i][1] != 5:
                    results[f"關({generals[i][0]}、{generals[j][0]})"] = "主客四將同宮，相持爭鋒，不利有為"

        # 釋格：客目始擊與客二將在太乙對宮為格
        opp_ty = opp.get(ty)
        if opp_ty:
            if gong_of_chen(sj) == opp_ty:
                results["格(始擊)"] = "始擊在太乙對宮，政事上下相格、盜侮其君"
            if ad == opp_ty:
                results["格(客大)"] = "客大在太乙對宮為格"
            if av == opp_ty:
                results["格(客參)"] = "客參在太乙對宮為格"

        # 釋對：文昌所臨與太乙相當(對宮)為對
        if opp_ty and gong_of_chen(wc) == opp_ty:
            results["對"] = "文昌與太乙相對，大臣懷二、將吏挾奸"

        # 釋迫／釋擊之辰、宮鄰接計算
        prev_g = eight_order[(eight_order.index(ty) - 1) % 8]   # 後一宮(內)
        next_g = eight_order[(eight_order.index(ty) + 1) % 8]   # 前一宮(外)
        chens = gong2chen.get(ty, [])
        out_chen = in_chen = None
        if len(chens) == 2:
            p0 = sixteen.index(chens[0])
            p1 = sixteen.index(chens[1])
            out_chen = sixteen[(p1 + 1) % 16]   # 太乙前一辰(外)
            in_chen = sixteen[(p0 - 1) % 16]    # 太乙後一辰(內)

        # 釋迫：二目及定計目在太乙前後辰／宮
        for nm, ch in [("文昌", wc), ("始擊", sj), ("定目", se)]:
            if gong_of_chen(ch) == ty:
                continue  # 同宮屬囚，不論迫
            if ch == out_chen:
                results[f"辰迫(外、{nm})"] = f"{nm}在太乙前一辰，外辰迫，災急而重"
            elif ch == in_chen:
                results[f"辰迫(內、{nm})"] = f"{nm}在太乙後一辰，內辰迫，災尤速"
            og = gong_of_chen(ch)
            if og == next_g:
                results[f"宮迫(外、{nm})"] = f"{nm}在太乙前一宮，外宮迫，災緩而輕"
            elif og == prev_g:
                results[f"宮迫(內、{nm})"] = f"{nm}在太乙後一宮，內宮迫".format(nm)
        # 將之宮迫
        for nm, g in generals:
            if g == 5 or g == ty:
                continue
            if g == next_g:
                results[f"宮迫(外、{nm})"] = f"{nm}在太乙前一宮，外宮迫".format(nm)
            elif g == prev_g:
                results[f"宮迫(內、{nm})"] = f"{nm}在太乙後一宮，內宮迫"

        # 釋擊：始擊在太乙前後辰／宮
        if gong_of_chen(sj) != ty:
            if sj == out_chen:
                results["擊(外辰)"] = "始擊在太乙前一辰，外辰擊，諸侯侵凌"
            elif sj == in_chen:
                results["擊(內辰)"] = "始擊在太乙後一辰，內辰擊，親王后妃憑凌"
            if gong_of_chen(sj) == next_g:
                results["擊(外宮)"] = "始擊在太乙前一宮，外宮擊"
            elif gong_of_chen(sj) == prev_g:
                results["擊(內宮)"] = "始擊在太乙後一宮，內宮擊"

        # 釋提挾：二目分居太乙宮兩側而挾之
        if gong_of_chen(wc) != ty and gong_of_chen(sj) != ty and len(chens) == 2:
            ty_mid = (sixteen.index(chens[0]) + sixteen.index(chens[1])) / 2.0
            def _side(idx):
                d = (idx - ty_mid) % 16
                return "外" if 0 < d < 8 else ("內" if d > 8 else "中")
            swc = _side(sixteen.index(wc))
            ssj = _side(sixteen.index(sj))
            if swc != "中" and ssj != "中" and swc != ssj:
                results["提挾"] = "二目(文昌、始擊)挾太乙，政由大臣、下專權之象"

        # 釋執提：太乙與開生二門合(同宮)為執，衝(對宮)為提格
        doors = self.geteightdoors(ji_style, taiyi_acumyear)
        kai_gong = next((g for g, d in doors.items() if d == "開"), None)
        sheng_gong = next((g for g, d in doors.items() if d == "生"), None)
        for g in [kai_gong, sheng_gong]:
            if g is None:
                continue
            if g == ty:
                results["執(開生門合)"] = "太乙與開生門合，執提之象，不可舉事"
            elif opp.get(ty) and g == opp.get(ty):
                results["提格(開生門衝)"] = "太乙與開生門衝，提格之象"

        # 釋四郭固：文昌囚太乙宮且主二將相關；或客目臨太乙宮且客主二將相關
        if gong_of_chen(wc) == ty and hd == hv and hd != 5:
            results["四郭固"] = "文昌囚太乙宮、主二將相關，堅壁固守，不可有為"
        elif gong_of_chen(sj) == ty and ad != 5 and (ad in (av, hd) or av == hv):
            results["四郭固"] = "客目臨太乙宮、客主二將相關，四郭固，宜固守"

        if not results:
            results["無格局"] = "太乙無掩迫關囚擊格對提挾諸格局，主客清明"
        return results

    def pan(self, ji_style, taiyi_acumyear, enable_game_theory: bool = False):
        """起盤詳細內容

        參數
        ----
        ji_style : int
            太乙計式 (0=年計, 1=月計, 2=日計, 3=時計, 4=分計)。
        taiyi_acumyear : int
            太乙積年法 (0=統宗, 1=金鏡, 2=淘金歌, 3=太乙局)。
        enable_game_theory : bool, optional
            若為 True，則附加「運籌博弈分析」鍵到回傳 dict（預設 False）。
            分析結果由 TaiyiGame 類別生成，以古法「推主客相闗法」及「七大兵法格局」
            為本，輔以現代零和博弈論 Nash 均衡與線性規劃運籌博弈原理。
        """
        _geju = self.shi_geju(ji_style, taiyi_acumyear)
        _three_doors = self.threedoors(ji_style, taiyi_acumyear)
        _five_gens = self.fivegenerals(ji_style, taiyi_acumyear)
        _ty = self.ty(ji_style, taiyi_acumyear)
        _doors = self.geteightdoors(ji_style, taiyi_acumyear)
        _ty_door = _doors.get(_ty)
        _gz = config.gangzhi(self.year, self.month, self.day, self.hour, self.minute)
        _sf_hit = any(k.startswith("擊") for k in _geju)
        _sf_ge = "格(始擊)" in _geju
        _wq = jieqi.gong_wangzhuai(jieqi.jq(self.year, self.month, self.day, self.hour, self.minute))
        result = {
                "太乙計":config.taiyi_name(ji_style),
                "太乙公式類別":config.ty_method(taiyi_acumyear),
                "公元日期":config.gendatetime(self.year, self.month, self.day, self.hour, self.minute),
                "干支":config.gangzhi(self.year, self.month, self.day, self.hour, self.minute),
                "農曆":config.lunar_date_d(self.year, self.month, self.day),
                "年號":config.kingyear(config.lunar_date_d(self.year, self.month, self.day).get("年")),
                "紀元":self.jiyuan(ji_style, taiyi_acumyear),
                "太歲":self.taishui(ji_style),
                "局式":self.kook(ji_style, taiyi_acumyear),
                "五子元局":self.get_five_yuan_kook(ji_style, taiyi_acumyear),
                "陽九":config.yangjiu(self.year, self.month, self.day),
                "百六":config.baliu(self.year, self.month, self.day),
                "太乙落宮":self.ty(ji_style, taiyi_acumyear),
                "太乙":self.ty_gong(ji_style, taiyi_acumyear),
                "天乙":self.skyyi(ji_style, taiyi_acumyear),
                "地乙":self.earthyi(ji_style, taiyi_acumyear),
                "四神":self.fgd(ji_style, taiyi_acumyear),
                "直符":self.zhifu(ji_style, taiyi_acumyear),
                "文昌":[self.skyeyes(ji_style, taiyi_acumyear), self.skyeyes_des(ji_style, taiyi_acumyear)],
                "始擊":self.sf(ji_style, taiyi_acumyear),
                "主算":[self.home_cal(ji_style, taiyi_acumyear), config.cal_des(self.home_cal(ji_style, taiyi_acumyear))],
                "主將":self.home_general(ji_style, taiyi_acumyear),
                "主參":self.home_vgen(ji_style, taiyi_acumyear),
                "客算":[self.away_cal(ji_style, taiyi_acumyear), config.cal_des(self.away_cal(ji_style, taiyi_acumyear))],
                "客將":self.away_general(ji_style, taiyi_acumyear),
                "客參":self.away_vgen(ji_style, taiyi_acumyear),
                "定算":[self.set_cal(ji_style, taiyi_acumyear), config.cal_des(self.set_cal(ji_style, taiyi_acumyear))],
                "合神":self.hegod(ji_style),
                "計神":self.jigod(ji_style),
                "定目":self.se(ji_style, taiyi_acumyear),
                "君基":self.kingbase(ji_style, taiyi_acumyear),
                "臣基":self.officerbase(ji_style, taiyi_acumyear),
                "民基":self.pplbase(ji_style, taiyi_acumyear),
                "五福":config.wufu(self.accnum(ji_style, taiyi_acumyear)),
                "帝符":config.kingfu(self.accnum(ji_style, taiyi_acumyear)),
                "太尊":config.taijun(self.accnum(ji_style, taiyi_acumyear)),
                "飛鳥":config.flybird(self.accnum(ji_style, taiyi_acumyear)),
                "三風":config.threewind(self.accnum(ji_style, taiyi_acumyear)),
                "五風":config.fivewind(self.accnum(ji_style, taiyi_acumyear)),
                "八風":config.eightwind(self.accnum(ji_style, taiyi_acumyear)),
                "大游":config.bigyo(self.accnum(ji_style, taiyi_acumyear)),
                "小游":config.smyo(self.accnum(ji_style, taiyi_acumyear)),
                "金函玉鏡":config.gpan(self.year, self.month, self.day, self.hour, self.minute),
                "二十八宿值日":config.starhouse(self.year, self.month, self.day, self.hour, self.minute),
                "太歲二十八宿":self.year_chin(),
                "太歲值宿斷事": su_dist.get(self.year_chin()),
                "始擊二十八宿":self.sf_num(ji_style, taiyi_acumyear),
                "始擊值宿斷事":su_dist.get(self.sf_num(ji_style, taiyi_acumyear)),
                "十天干歲始擊落宮預測": config.multi_key_dict_get (tengan_shiji, config.gangzhi(self.year, self.month, self.day, self.hour, self.minute)[0][0]).get(config.Ganzhiwuxing(self.sf(ji_style, taiyi_acumyear))),
                "八門值事":config.eight_door(self.accnum(ji_style, taiyi_acumyear)),
                "八門分佈":self.geteightdoors(ji_style, taiyi_acumyear),
                # 《太乙統宗寶鑑》卷二：十六宮各星將與十精分佈
                "十六宮分佈": self.sixteen_gong(ji_style, taiyi_acumyear),
                "八宮旺衰":jieqi.gong_wangzhuai(jieqi.jq(self.year, self.month, self.day, self.hour, self.minute)),
                "推太乙當時法": self.shensha(ji_style, taiyi_acumyear),
                "推三門具不具":self.threedoors(ji_style, taiyi_acumyear),
                "推五將發不發":self.fivegenerals(ji_style, taiyi_acumyear),
                "推主客相闗法":self.wc_n_sj(ji_style, taiyi_acumyear),
                "推陰陽以占厄會":self.tui_danger(ji_style, taiyi_acumyear),
                "明天子巡狩之期術":self.tianzi_go(ji_style, taiyi_acumyear),
                "明君基太乙所主術":self.ming_kingbase(ji_style, taiyi_acumyear),
                "明臣基太乙所主術":self.ming_officerbase(ji_style, taiyi_acumyear),
                "明民基太乙所主術":self.ming_pplbase(ji_style, taiyi_acumyear),
                "明五福太乙所主術":self.ming_wufu(ji_style, taiyi_acumyear),
                "明五福吉算所主術":self.wufu_gb(ji_style, taiyi_acumyear),
                "明天乙太乙所主術":self.ming_tiany(ji_style, taiyi_acumyear),
                "明地乙太乙所主術":self.ming_earthy(ji_style, taiyi_acumyear),
                "明值符太乙所主術":self.ming_zhifu(ji_style, taiyi_acumyear),
                "推多少以占勝負":config.suenwl(self.home_cal(ji_style, taiyi_acumyear),
                                        self.away_cal(ji_style, taiyi_acumyear),
                                        self.home_general(ji_style, taiyi_acumyear),
                                        self.away_general(ji_style, taiyi_acumyear)),
                "推太乙風雲飛鳥助戰法": self.flybird_wl(ji_style, taiyi_acumyear),
                "推孤單以占成敗":self.gudan(ji_style, taiyi_acumyear), 
                "推雷公入水":config.leigong(self.ty(ji_style, taiyi_acumyear)),
                "推臨津問道":config.lijin(self.year, self.month, self.day, self.hour, self.minute),
                "推獅子反擲":config.lion(self.year, self.month, self.day, self.hour, self.minute),
                "推白雲捲空":config.cloud(self.home_general(ji_style, taiyi_acumyear)),
                "推猛虎相拒":config.tiger(self.ty(ji_style, taiyi_acumyear)),
                "推白龍得雲":config.dragon(self.ty(ji_style, taiyi_acumyear)),
                "推回軍無言":config.returnarmy(self.away_general(ji_style, taiyi_acumyear)),
                # 《太乙統宗寶鑑》卷四：釋掩迫關囚擊格對提挾執提四郭固
                "釋格局":_geju,
                # 《太乙統宗寶鑑》卷十：三旗行宮 + 九宮貴神
                "三旗行宮":config.sanqi(self.accnum(ji_style, taiyi_acumyear)),
                "九宮貴神":config.nine_palace_gods(self.accnum(ji_style, taiyi_acumyear)),
                # 《太乙統宗寶鑑》卷六：太乙九星 + 文昌九星
                "太乙九星":config.taiyi_nine_stars(
                    self.accnum(ji_style, taiyi_acumyear),
                    config.gangzhi(self.year, self.month, self.day, self.hour, self.minute)[0][0]),
                "文昌九星":config.wenchang_nine_stars(
                    self.accnum(ji_style, taiyi_acumyear),
                    config.gangzhi(self.year, self.month, self.day, self.hour, self.minute)[0][0]),
                # 《太乙統宗寶鑑》卷三／卷十：五運六氣 + 五音之數
                "五運六氣":config.wuyun_liuqi(
                    config.gangzhi(self.year, self.month, self.day, self.hour, self.minute)[0][0],
                    config.gangzhi(self.year, self.month, self.day, self.hour, self.minute)[0][1],
                    config.num2gong(self.ty(ji_style, taiyi_acumyear)),
                    self.skyeyes(ji_style, taiyi_acumyear),
                    self.sf(ji_style, taiyi_acumyear)),
                "五音之數":config.wuyin_shu(
                    self.home_cal(ji_style, taiyi_acumyear),
                    self.away_cal(ji_style, taiyi_acumyear),
                    self.set_cal(ji_style, taiyi_acumyear),
                    config.num2gong(self.ty(ji_style, taiyi_acumyear)),
                    _gz[2][1],
                    _gz[3][1]),
                # 《太乙統宗寶鑑》卷五：軍事戰略
                "軍事戰略": config.junshi_zhanlue(
                    _ty,
                    self.home_cal(ji_style, taiyi_acumyear),
                    self.away_cal(ji_style, taiyi_acumyear),
                    self.skyeyes(ji_style, taiyi_acumyear),
                    self.sf(ji_style, taiyi_acumyear),
                    _three_doors,
                    _five_gens,
                    self.home_general(ji_style, taiyi_acumyear),
                    self.away_general(ji_style, taiyi_acumyear),
                    self.home_vgen(ji_style, taiyi_acumyear),
                    self.away_vgen(ji_style, taiyi_acumyear),
                    self.gudan(ji_style, taiyi_acumyear),
                    _gz[0][1],
                    _wq,
                    _ty_door),
                # 《太乙統宗寶鑑》卷十二：統運入卦、十二運立成、入爻禍福、流年直卦
                "卷十二": config.vol12_zonghe(
                    self.year,
                    _gz[0][0],
                    _gz[0][1],
                    self.month,
                    self.day),
                # 《太乙統宗寶鑑》卷十三：統十二運卦象、六爻觀象
                "卷十三": config.gua_xiang_zonghe(self.year),
                # 《太乙統宗寶鑑》卷十四：統運八卦行支編年
                "卷十四": config.biannian_zonghe(self.year),
                # 《太乙統宗寶鑑》卷八：九宮十二分野、絳宮明堂玉堂
                "卷八": config.fenye_zonghe(_ty, _gz[0][1]),
                # 《太乙統宗寶鑑》卷九：大小遊軌運、重卦策數、陽九百六限數
                "卷九": config.guiyun_zonghe(
                    self.accnum(ji_style, taiyi_acumyear),
                    self.year, self.month, self.day),
                # 《太乙統宗寶鑑》卷十：五運六氣、天目合會、九宮貴神歲會
                "卷十": config.vol10_zonghe(
                    _gz[0][0], _gz[0][1], _ty,
                    self.skyeyes(ji_style, taiyi_acumyear),
                    self.sf(ji_style, taiyi_acumyear),
                    self.accnum(ji_style, taiyi_acumyear)),
                # 《太乙統宗寶鑑》卷十八：十精所主、雲氣合會
                "卷十八": config.yunqi_zonghe(
                    self.accnum(ji_style, taiyi_acumyear), _ty),
                # 《太乙統宗寶鑑》卷十一：十六宮間變化、州國災變、城名厄會、飛符四殺、歲內災發
                "卷十一": config.vol11_zonghe(
                    _ty,
                    self.skyeyes(ji_style, taiyi_acumyear),
                    self.hegod(ji_style),
                    self.flyfu(ji_style, taiyi_acumyear),
                    _gz[0][0],
                    _gz[0][1],
                    _gz[1][1],
                    _gz[2][1],
                    _gz[3][1],
                    config._NINE_GONG_CHENG.get(_ty, (None, None))[1]),
                # 《太乙統宗寶鑑》卷十五：軍事應用
                "軍事應用":config.junshi_yingyong(
                    self.home_cal(ji_style, taiyi_acumyear),
                    self.away_cal(ji_style, taiyi_acumyear),
                    _ty,
                    self.skyeyes(ji_style, taiyi_acumyear),
                    self.sf(ji_style, taiyi_acumyear),
                    _gz[2][1],
                    _gz[3][1],
                    _geju,
                    _three_doors,
                    _five_gens,
                    home_gen=self.home_general(ji_style, taiyi_acumyear),
                    away_gen=self.away_general(ji_style, taiyi_acumyear),
                    home_vgen=self.home_vgen(ji_style, taiyi_acumyear),
                    away_vgen=self.away_vgen(ji_style, taiyi_acumyear),
                    flybird_gong=config.flybird(self.accnum(ji_style, taiyi_acumyear))),
                # 《太乙統宗寶鑑》卷十七：軍事占斷
                "軍事占斷":config.junshi_zhanduan(
                    _ty,
                    self.home_cal(ji_style, taiyi_acumyear),
                    self.away_cal(ji_style, taiyi_acumyear),
                    self.skyeyes(ji_style, taiyi_acumyear),
                    self.sf(ji_style, taiyi_acumyear),
                    self.skyeyes_des(ji_style, taiyi_acumyear),
                    self.home_general(ji_style, taiyi_acumyear),
                    self.home_vgen(ji_style, taiyi_acumyear),
                    self.away_general(ji_style, taiyi_acumyear),
                    self.away_vgen(ji_style, taiyi_acumyear),
                    _three_doors,
                    _five_gens,
                    _geju,
                    "掩" in _geju,
                    _ty_door,
                    _sf_hit,
                    _sf_ge,
                    _wq),
                # 《太乙統宗寶鑑》卷二／卷七：十六宮間神、八門、天乙地乙直符四神所主
                "神將所主": config.shenjiang_suozhu(
                    _ty,
                    self.skyeyes(ji_style, taiyi_acumyear),
                    self.sf(ji_style, taiyi_acumyear),
                    self.se(ji_style, taiyi_acumyear),
                    self.skyyi(ji_style, taiyi_acumyear),
                    self.earthyi(ji_style, taiyi_acumyear),
                    self.fgd(ji_style, taiyi_acumyear),
                    self.zhifu(ji_style, taiyi_acumyear),
                    _doors,
                    config.eight_door(self.accnum(ji_style, taiyi_acumyear)),
                    _wq,
                    config.bigyo(self.accnum(ji_style, taiyi_acumyear)),
                    config.smyo(self.accnum(ji_style, taiyi_acumyear)),
                    accnum=self.accnum(ji_style, taiyi_acumyear),
                    skyeyes_des=self.skyeyes_des(ji_style, taiyi_acumyear),
                    home_gen=self.home_general(ji_style, taiyi_acumyear),
                    away_gen=self.away_general(ji_style, taiyi_acumyear),
                    home_vgen=self.home_vgen(ji_style, taiyi_acumyear),
                    away_vgen=self.away_vgen(ji_style, taiyi_acumyear),
                    geju=_geju,
                    wufu=config.wufu(self.accnum(ji_style, taiyi_acumyear)),
                    kingbase=self.kingbase(ji_style, taiyi_acumyear),
                    officerbase=self.officerbase(ji_style, taiyi_acumyear),
                    pplbase=self.pplbase(ji_style, taiyi_acumyear)),
                }
        if enable_game_theory:
            # 此處以古法「推主客相闗法」及「七大兵法格局」為本，
            # 輔以現代零和博弈論 Nash 均衡與線性規劃運籌博弈原理，附加博弈分析結果。
            from .game_theory import TaiyiGame  # noqa: PLC0415
            result["運籌博弈分析"] = TaiyiGame(result).分析報告()
        return result

if __name__ == '__main__':
    tic = time.perf_counter()
    year = 2025
    month = 12
    day = 26
    hour = 22
    minute = 6
    #print(Taiyi(year, month, day, hour, minute).kingbase(3,0))
    #print(Taiyi(year, month, day, hour, minute).pan(3,0))
    #life1 = Taiyi(year, month, day, hour, minute).gongs_discription("男")
    #life2 = Taiyi(year, month, day, hour, minute).twostar_disc("男")
    #print(Taiyi(year, month, day, hour, minute).convert_gongs_text(life1, life2))
    #print(life1)
    #print(Taiyi(year, month, day, hour, minute).taiyi_life("男"))
    #print(Taiyi(year, month, day, hour, minute).gongs_discription("男"))
    #print(Taiyi(year, month, day, hour, minute).gongs_discription_list("男"))
    #print(Taiyi(year, month, day, hour, minute).taiyi_life("男"))
    print(Taiyi(year, month, day, hour, minute).gen_gong(4,0,0))
    #print(Taiyi(year, month, day, hour, minute).geteightdoors_text2(2,0))
    #print(Taiyi(year, month, day, hour, minute).yangjiu_xingxian("男"))
    #print(Taiyi(year, month, day, hour, minute).kook(0, 0))
    #print(Taiyi(year, month, day, hour, minute).kook(1, 0))
    #print(Taiyi(year, month, day, hour, minute).kook(2, 0))
    #print(Taiyi(year, month, day, hour, minute).kook(3, 0))
    #print(Taiyi(year, month, day, hour, minute).kook(4, 0))

    toc = time.perf_counter()
    print(f"{toc - tic:0.4f} seconds")
