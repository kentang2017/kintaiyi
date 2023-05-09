# -*- coding: utf-8 -*-
"""
Created on Sat Aug 27 18:11:44 2022
@author: kentang
"""
import re
import time
import itertools
from itertools import cycle
from ephem import Date
import numpy as np
from cn2an import an2cn
from taiyidict import tengan_shiji, su_dist
import config
import jieqi
from jieqi import jieqi_name
from config import num, su, gong, gong1, gong2, gong3, gua, nayin_wuxing, wuxing_relation_2, jc, jc1, tyjc, kingyear, skyeyes_dict, multi_key_dict_get, jiazi, num2gong, Ganzhiwuxing, di_zhi, gangzhi


class Taiyi():
    """太乙起盤主要函數"""
    def __init__(self, year, month, day, hour, minute):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        #間辰
        self.door = list("開休生傷杜景死驚")
    #計神
    def jigod(self, ji_style):
        """ji_style 年計、月計、日計、時計或分計"""
        return dict(zip(di_zhi, config.new_list(list(reversed(di_zhi)), "寅"))).get(self.taishui(ji_style))
    #太歲
    def taishui(self, ji_style):
        """太歲"""
        gang_zhi =  config.gangzhi(self.year, self.month, self.day, self.hour, self.minute)
        return {0: gang_zhi[0][1], 1: gang_zhi[1][1], 2: gang_zhi[2][1], 3:gang_zhi[3][1], 4:gang_zhi[4][1], 5: gang_zhi[0][1],}.get(ji_style)
    #文昌始擊處境
    def skyeyes_des(self, ji_style, taiyi_acumyear):
        """ji_style 年計、月計、日計、時計或分計；"""
        kook_text = self.kook(ji_style, taiyi_acumyear).get("文")[0]
        kook_num = self.kook(ji_style, taiyi_acumyear).get("數")
        skyeyes_summary = {"陽":",始擊擊,,內迫,,,辰迫,,囚,,囚,,,,,,囚,囚,客挾,,,,,,,,囚,囚,始擊擊,,,始擊擊,始擊掩,始擊掩,,,,囚,辰迫,,客挾,客挾,囚,客挾,宮迫,,主挾，宮迫,辰迫,,,,主挾，辰迫,宮迫,宮迫,始擊掩,,,,客挾,,,,,,主挾,辰擊,,始擊掩,始擊擊,始擊擊,囚,始擊擊".split(","),
              "陰":",內辰迫,外辰迫,內辰擊,,,外宮迫,掩、辰迫,掩,掩、辰迫,掩、囚,內宮迫,內宮擊,,,掩、外辰迫,掩,掩,,關客,關客,關客,,外宮擊,,,外宮擊,,,,內宮擊,,關主,關客,,,外辰迫,掩,內辰迫,關客,內辰擊,,掩,內辰迫,內宮迫,掩,外宮迫,外宮迫,外宮擊,內宮擊,,內辰迫,外辰擊,掩,關主,,,外宮擊,掩,內宮擊,內宮迫,外宮擊,,內宮擊,,,,,,,,,".split(",")}
        return dict(zip(range(1,73), skyeyes_summary.get(kook_text))).get(kook_num)
    #文昌(天目)
    def skyeyes(self, ji_style, taiyi_acumyear):
        """ji_style 年計、月計、日計、時計或分計"""
        return dict(zip(range(1,73),skyeyes_dict.get(self.kook(ji_style, taiyi_acumyear).get("文")[0]))).get(int(self.kook(ji_style, taiyi_acumyear).get("數")))
    #合神
    def hegod(self, ji_style):
        """ji_style 年計、月計、日計、時計或分計"""
        return dict(zip(di_zhi, config.new_list(list(reversed(di_zhi)), "丑"))).get(self.taishui(ji_style))

#%% 積年
    def accnum(self, ji_style, taiyi_acumyear):
        tndict = {0:10153917, 1:1936557, 2:10154193, 3:10153917 }
        tn_num = tndict.get(taiyi_acumyear)
        year = config.lunar_date_d(self.year, self.month, self.day).get("年")
        if ji_style == 0: #年計
            if year >= 0:
                return tn_num + year
            if year < 0:
                return tn_num + year + 1
        if ji_style ==1: #月計
            if year >= 0:
                accyear = tn_num + year - 1
            if year < 0:
                accyear = tn_num + year + 1
            return accyear * 12 + 2 + config.lunar_date_d(self.year, self.month, self.day).get("月")
        if ji_style ==2:#日計
            if taiyi_acumyear ==0:
                t = 708011105
                return t + int(Date("{}/{}/{} {}:00:00.00".format(str(self.year).zfill(4), str(self.month).zfill(2), str(self.day).zfill(2), str(self.hour).zfill(2))) - Date("1900/06/19 00:00:00.00"))
            if taiyi_acumyear ==2:
                t = 708011105 - 10153917 +tn_num
                return t + int(Date("{}/{}/{} {}:00:00.00".format(str(self.year).zfill(4), str(self.month).zfill(2), str(self.day).zfill(2), str(self.hour).zfill(2))) - Date("1900/06/19 00:00:00.00"))
            if taiyi_acumyear ==1:
                t = 708011105 - 185
                return t + int(Date("{}/{}/{} {}:00:00.00".format(str(self.year).zfill(4), str(self.month).zfill(2), str(self.day).zfill(2), str(self.hour).zfill(2))) - Date("1900/06/19 00:00:00.00"))
            if taiyi_acumyear == 3:
                ly = config.lunar_date_d(self.year, self.month, self.day).get("年")
                ld = config.lunar_date_d(self.year, self.month, self.day).get("日")
                n1 = round((ly - 423 )  * (235 / 19) ,0)
                n2 = round(n1 * 29.5306, 0)
                n3 = n2 + ld
                return int(n3)
        elif ji_style ==3: #時計
            if taiyi_acumyear ==0:
                t = 708011105
                accday = t + int((Date("{}/{}/{} {}:00:00.00".format(str(self.year).zfill(4), str(self.month).zfill(2), str(self.day).zfill(2), str(self.hour).zfill(2))) - Date("1900/12/21 00:00:00.00") ))
                acchr = ((accday -1) * 12) + (self.hour+1)//2 +1
            elif taiyi_acumyear ==2:
                t = 708011105 - 10153917 +tn_num
                accday = t + int((Date("{}/{}/{} {}:00:00.00".format(str(self.year).zfill(4), str(self.month).zfill(2), str(self.day).zfill(2), str(self.hour).zfill(2))) - Date("1900/12/21 00:00:00.00") ))
                acchr = ((accday -1) * 12) + (self.hour+1)//2 +1
            elif taiyi_acumyear ==1:
                t = 708011105 - 10153917 +tn_num
                accday = t + int((Date("{}/{}/{} {}:00:00.00".format(str(self.year).zfill(4), str(self.month).zfill(2), str(self.day).zfill(2), str(self.hour).zfill(2))) - Date("1900/12/21 00:00:00.00") ))
                acchr = ((accday -1) * 12) + (self.hour+1)//2 -11
            elif taiyi_acumyear == 4:
                tiangan = dict(zip([tuple(jiazi()[jiazi().index(i):jiazi().index(i)+6]) for i in jiazi()[0::6]], jiazi()[0::6]))
                getfut = dict(zip(jiazi()[0::6], [1,7,13,19,25,31,37,43,49,55])).get(multi_key_dict_get(tiangan, config.gangzhi(self.year, self.month, self.day, self.hour, self.minute)[2]))
                dgz_num = dict(zip(jiazi(), range(1,61))).get( config.gangzhi(self.year, self.month, self.day, self.hour, self.minute)[2])
                zhi_num = dict(zip(list('子丑寅卯辰巳午未申酉戌亥'), range(1,13))).get(config.gangzhi(self.year, self.month, self.day, self.hour, self.minute)[3][1])
                if tiangan != dgz_num:
                    acchr  =  ((dgz_num- getfut) * 12) + zhi_num
                elif tiangan == dgz_num:
                    acchr = zhi_num
            return acchr
        elif ji_style == 4: #分計
            return int((Date("{}/{}/{} {}:00:00.00".format(str(self.year).zfill(4), str(self.month).zfill(2), str(self.day).zfill(2), str(self.hour).zfill(2))) - Date("1900/06/19 00:00:00.00") - 1)) * 120 + (self.minute + 1 ) // 2 + 1

    def yeargua(self, taiyi_acumyear):
        tynum = self.accnum(0, taiyi_acumyear) % 64
        if tynum == 0:
            tynum = 64
        return gua.get(tynum)

    def kook(self, ji_style, taiyi_acumyear):
        alljq = jieqi_name
        j_q = jieqi.jq(self.year, self.month, self.day, self.hour)
        jqmap = {tuple(config.new_list(alljq, "冬至")[0:12]):"冬至", tuple(config.new_list(alljq, "夏至")[0:12]):"夏至"}
        k = self.accnum(ji_style, taiyi_acumyear)%72
        if k == 0:
            k = 72
        if ji_style == 0 or ji_style == 1 or ji_style ==5 or ji_style ==2:
            dun = "陽遁"
            three_year = {0:"理天", 1:"理地", 2:"理人"}.get(dict(zip(list(range(1,73)), [0,1,2] * 24)).get(k))
            return {"文":"{}{}局".format(dun, an2cn(k)), "數":k, "年":three_year}
        elif ji_style == 3 or ji_style == 4:
            if multi_key_dict_get(jqmap, j_q) == "夏至":
                dun = "陰遁"
            elif multi_key_dict_get(jqmap, j_q) == "冬至":
                dun = "陽遁"
            three_year = {0:"理天", 1:"理地", 2:"理人"}.get(dict(zip(list(range(1,73)), [0,1,2] * 24)).get(k))
            return {"文":"{}{}局".format(dun, an2cn(k)), "數":k, "年":three_year, "積年數":self.accnum(ji_style, taiyi_acumyear) }

    def getepoch(self, ji_style, taiyi_acumyear):
        accnum = self.accnum(ji_style, taiyi_acumyear)
        if ji_style == 0 or ji_style == 1 or ji_style ==2:
            if accnum % 360 == 1:
                find_ji_num = 1
            else:
                find_ji_num = int((accnum % 360) // 60 + 1)
            if find_ji_num == 0:
                find_ji_num = 1
            find_ji_num2 = int(accnum % 360 % 72 % 24 / 3)
            if find_ji_num2 == 0:
                find_ji_num2 = 1
            if find_ji_num2 > 6:
                find_ji_num2 = find_ji_num2  - 6
            if find_ji_num > 6:
                find_ji_num = find_ji_num - 6
            cnum = list("一二三四五六七八九十")
            return {"元":dict(zip(range(1,7), cnum[0:6])).get(find_ji_num2), "紀":dict(zip(range(1,7), cnum[0:6])).get(find_ji_num)}
        elif ji_style == 3:
            epochdict = dict(zip([
                        ('甲子', '甲午', '乙丑', '乙未', '丙寅', '丙申', '丁卯', '丁酉', '戊辰', '戊戌'),
                        ('己巳', '己亥', '庚午', '庚子', '辛未', '辛丑', '壬申', '壬寅', '癸酉', '癸卯'),
                        ('甲戌', '甲辰', '乙亥', '乙巳', '丙子', '丙午', '丁丑', '丁未', '戊寅', '戊申'),
                        ('己卯', '己酉', '庚辰', '庚戌', '辛巳', '辛亥', '壬午', '壬子', '癸未', '癸丑'),
                        ('甲申', '甲寅', '乙酉', '乙卯', '丙戌', '丙辰', '丁亥', '丁巳', '戊子', '戊午'),
                        ('己丑', '己未', '庚寅', '庚申', '辛卯', '辛酉', '壬辰', '壬戌', '癸巳', '癸亥')],  list("一二三四五六")))
            return "第{}紀".format(multi_key_dict_get(epochdict, config.gangzhi(self.year, self.month, self.day, self.hour, self.minute)[2]))

        elif ji_style == 4:
            epochdict = dict(zip([
                        ('甲子', '甲午', '乙丑', '乙未', '丙寅', '丙申', '丁卯', '丁酉', '戊辰', '戊戌'),
                        ('己巳', '己亥', '庚午', '庚子', '辛未', '辛丑', '壬申', '壬寅', '癸酉', '癸卯'),
                        ('甲戌', '甲辰', '乙亥', '乙巳', '丙子', '丙午', '丁丑', '丁未', '戊寅', '戊申'),
                        ('己卯', '己酉', '庚辰', '庚戌', '辛巳', '辛亥', '壬午', '壬子', '癸未', '癸丑'),
                        ('甲申', '甲寅', '乙酉', '乙卯', '丙戌', '丙辰', '丁亥', '丁巳', '戊子', '戊午'),
                        ('己丑', '己未', '庚寅', '庚申', '辛卯', '辛酉', '壬辰', '壬戌', '癸巳', '癸亥')], list("一二三四五六")))
            return "第{}紀".format(multi_key_dict_get(epochdict, config.gangzhi(self.year, self.month, self.day, self.hour, self.minute)[3]))

    def getyuan(self, ji_style, taiyi_acumyear):
        accnum = self.accnum(ji_style, taiyi_acumyear)
        if round(accnum % 360) == 1:
            find_ji_num = 1
        else:
            find_ji_num = int(round((accnum % 360) / 72, 0))
        fiveyuen_d = dict(zip(range(1,6), jiazi()[0::12]))
        if find_ji_num == 0:
            find_ji_num = 1
        jiyuan = fiveyuen_d.get(find_ji_num)
        return jiyuan

    def jiyuan(self, ji_style, taiyi_acumyear):
        if ji_style == 3:
            j = dict(zip([('甲子', '甲午', '乙丑', '乙未', '丙寅', '丙申', '丁卯', '丁酉', '戊辰', '戊戌', '己巳', '己亥'),
                            ('庚午', '庚子', '辛未', '辛丑', '壬申', '壬寅', '癸酉', '癸卯', '甲戌', '甲辰', '乙亥', '乙巳'),
                            ('丙子', '丙午', '丁丑', '丁未', '戊寅', '戊申', '己卯', '己酉', '庚辰', '庚戌', '辛巳', '辛亥'),
                            ('壬午', '壬子', '癸未', '癸丑', '甲申', '甲寅', '乙酉', '乙卯', '丙戌', '丙辰', '丁亥', '丁巳'),
                            ('戊子', '戊午', '己丑', '己未', '庚寅', '庚申', '辛卯', '辛酉', '壬辰', '壬戌', '癸巳', '癸亥')], "甲子,丙子,戊子,庚子,壬子".split(",")))
            if taiyi_acumyear!=1:
                return "{}{}元".format(self.getepoch(ji_style, taiyi_acumyear), multi_key_dict_get(j, config.gangzhi(self.year, self.month, self.day, self.hour, self.minute)[3]))
            else:
                return "{}{}元".format(self.getepoch(ji_style, taiyi_acumyear), multi_key_dict_get(j, config.gangzhi(self.year, self.month, self.day, self.hour, self.minute)[2]))
        elif ji_style == 4:
            j = dict(zip([('甲子', '甲午', '乙丑', '乙未', '丙寅', '丙申', '丁卯', '丁酉', '戊辰', '戊戌', '己巳', '己亥'),
                          ('庚午', '庚子', '辛未', '辛丑', '壬申', '壬寅', '癸酉', '癸卯', '甲戌', '甲辰', '乙亥', '乙巳'),
                          ('丙子', '丙午', '丁丑', '丁未', '戊寅', '戊申', '己卯', '己酉', '庚辰', '庚戌', '辛巳', '辛亥'),
                          ('壬午', '壬子', '癸未', '癸丑', '甲申', '甲寅', '乙酉', '乙卯', '丙戌', '丙辰', '丁亥', '丁巳'),
                          ('戊子', '戊午', '己丑', '己未', '庚寅', '庚申', '辛卯', '辛酉', '壬辰', '壬戌', '癸巳', '癸亥')], "甲子,丙子,戊子,庚子,壬子".split(",")))
            return "{}{}元".format(self.getepoch(ji_style, taiyi_acumyear), multi_key_dict_get(j, config.gangzhi(self.year, self.month, self.day, self.hour, self.minute)[3]))
        else:
            return "第{}紀第{}{}元".format(self.getepoch(ji_style, taiyi_acumyear).get("紀") ,self.getepoch(ji_style, taiyi_acumyear).get("元"), self.getyuan(ji_style, taiyi_acumyear))
    #太乙
    def ty(self, ji_style, taiyi_acumyear):
        arr = np.arange(10)
        repetitions = 3
        arrangement = np.repeat(arr, repetitions)
        arrangement_r = list(reversed(arrangement))
        yy_dict = {"陽": dict(zip(range(1,73), list(itertools.chain.from_iterable([list(arrangement)[3:15]+ list(arrangement)[18:]] * 3)))),  "陰": dict(zip(range(1,73), (list(arrangement_r)[:12] + list(arrangement_r)[15:][:-3]) * 3))}
        return yy_dict.get(self.kook(ji_style, taiyi_acumyear).get("文")[0]).get(self.kook(ji_style, taiyi_acumyear).get("數"))
    #太乙落宮
    def ty_gong(self, ji_style, taiyi_acumyear):
        return dict(zip(range(1,73), list("乾乾乾離離離艮艮艮震震震兌兌兌坤坤坤坎坎坎巽巽巽乾乾乾離離離艮艮艮震震震兌兌兌坤坤坤坎坎坎巽巽巽乾乾乾離離離艮艮艮震震震兌兌兌坤坤坤坎坎坎巽巽巽"))).get(self.kook(ji_style, taiyi_acumyear).get("數"))
    #始擊
    def sf(self, ji_style, taiyi_acumyear):
        sf_list = list("坤戌亥丑寅辰巳坤酉乾丑寅辰午坤酉亥子艮辰巳未申戌亥艮卯巽未丑戌子艮卯巳午坤戌亥丑寅辰巳坤酉乾丑寅辰午坤酉亥子艮辰巳未申戌亥艮卯巽未丑戌子艮卯巳午")
        return dict(zip(range(1,73),sf_list)).get(int(self.kook(ji_style, taiyi_acumyear).get("數")))

    def sf_num(self, ji_style, taiyi_acumyear):
        sf = self.sf(ji_style, taiyi_acumyear)
        sf_z = dict(zip(gong, list(range(1,17)))).get(sf)
        sf_su = dict(zip(list("子丑艮寅卯辰巽巳午未坤申酉戌乾亥"), list("虛斗牛尾房亢角翼星鬼井參昴婁奎室"))).get(sf)
        yc_num = dict(zip(su,list(range(1,29)))).get(self.year_chin())
        total = yc_num + sf_z
        if total > 28:
            a = dict(zip(list(range(1,29)),config.new_list(su, sf_su))).get(28)
            return config.new_list(su, a)[total - 28 -1]
        else:
            return dict(zip(list(range(1,29)),config.new_list(su, sf_su))).get(total)
    #定目
    def se(self, ji_style, taiyi_acumyear):
        wc,hg,ts = self.skyeyes(ji_style, taiyi_acumyear),self.hegod(ji_style),self.taishui(ji_style)
        start = config.new_list(gong1, hg)
        start1 = len(start[:start.index(ts)+1])
        start2 = config.new_list(gong1, wc)[start1-1]
        return  start2
    #主算
    def home_cal(self, ji_style, taiyi_acumyear):
        lnum = [8, 8, 3,  3, 4,4, 9, 9, 2, 2, 7, 7, 6, 6, 1, 1]
        gong = list("亥子丑艮寅卯辰巽巳午未坤申酉戌乾")
        wc = self.skyeyes(ji_style, taiyi_acumyear)
        lg = dict(zip(gong, lnum))
        wc_num = lg.get(wc)
        ty = self.ty(ji_style, taiyi_acumyear)
        wc_jc = list(map(lambda x: x == wc, jc)).count(True)
        ty_jc = list(map(lambda x: x == ty, tyjc)).count(True)
        wc_jc1  = list(map(lambda x: x == wc, jc1)).count(True)
        wc_order = config.new_list(num, wc_num)
        if wc_jc == 1 and ty_jc != 1 and wc_jc1 !=1 :
            return sum(wc_order[: wc_order.index(ty)]) +1
        elif wc_jc !=1 and ty_jc != 1 and wc_jc1 ==1:
            return sum(wc_order[: wc_order.index(ty)])
        elif wc_jc != 1 and ty_jc ==1 and wc_jc1 !=1:
            return sum(wc_order[: wc_order.index(ty)])
        elif wc_jc ==1 and ty_jc ==1 and wc_jc1 !=1 :
            return sum(wc_order[: wc_order.index(ty)])+1
        elif wc_jc !=1 and ty_jc ==1 and wc_jc1 ==1 :
            return sum(wc_order[: wc_order.index(ty)])
        elif wc_jc !=1 and ty_jc !=1 and wc_jc1 !=1 and ty != wc_num:
            return sum(wc_order[: wc_order.index(ty)])
        elif wc_jc !=1 and ty_jc !=1 and wc_jc1 !=1 and ty == wc_num:
            return ty
    #主大將
    def home_general(self, ji_style, taiyi_acumyear):
        if self.home_cal(ji_style, taiyi_acumyear) == 1:
            return self.ty(ji_style, taiyi_acumyear)
        elif self.home_cal(ji_style, taiyi_acumyear) < 10:
            return self.home_cal(ji_style, taiyi_acumyear)
        elif self.home_cal(ji_style, taiyi_acumyear) % 10 == 0:
            return 5
        elif self.home_cal(ji_style, taiyi_acumyear) > 10 and self.home_cal(ji_style, taiyi_acumyear) < 20 :
            return self.home_cal(ji_style, taiyi_acumyear) - 10
        elif self.home_cal(ji_style, taiyi_acumyear) > 20 and self.home_cal(ji_style, taiyi_acumyear) < 30 :
            return self.home_cal(ji_style, taiyi_acumyear) - 20
        elif self.home_cal(ji_style, taiyi_acumyear) > 30 and self.home_cal(ji_style, taiyi_acumyear) < 40 :
            return self.home_cal(ji_style, taiyi_acumyear) - 30

    #主參將
    def home_vgen(self, ji_style, taiyi_acumyear):
        home_vg = self.home_general(ji_style, taiyi_acumyear) *3 % 10
        if home_vg ==0:
            home_vg = 5
        return home_vg
    #客算
    def away_cal(self, ji_style, taiyi_acumyear):
        lnum = [8, 8, 3,  3, 4,4, 9, 9, 2, 2, 7, 7, 6, 6, 1, 1]
        gong = list("亥子丑艮寅卯辰巽巳午未坤申酉戌乾")
        sf = self.sf(ji_style, taiyi_acumyear)
        lg = dict(zip(gong, lnum))
        sf_num = lg.get(sf)
        ty = self.ty(ji_style, taiyi_acumyear)
        sf_jc = list(map(lambda x: x == sf, jc)).count(True)
        ty_jc = list(map(lambda x: x == ty, tyjc)).count(True)
        sf_jc1 = list(map(lambda x: x == sf, jc1)).count(True)
        sf_order = config.new_list(num, sf_num)
        if sf_jc == 1 and ty_jc != 1 and sf_jc1 !=1 :
            return sum(sf_order[: sf_order.index(ty)])+1
        elif sf_jc !=1 and ty_jc != 1 and sf_jc1 ==1:
            return sum(sf_order[: sf_order.index(ty)])
        elif sf_jc != 1 and ty_jc ==1 and sf_jc1 !=1:
            return sum(sf_order[: sf_order.index(ty)])
        elif sf_jc ==1 and ty_jc ==1 and sf_jc1 !=1 :
            return sum(sf_order[: sf_order.index(ty)])+1
        elif sf_jc !=1 and ty_jc ==1 and sf_jc1 ==1 :
            return sum(sf_order[: sf_order.index(ty)])
        elif sf_jc !=1 and ty_jc !=1 and sf_jc1 !=1 and sf_num != ty:
            return sum(sf_order[: sf_order.index(ty)])
        elif sf_jc !=1 and ty_jc !=1 and sf_jc1 !=1 and sf_num == ty:
            return ty
    #客將
    def away_general(self, ji_style, taiyi_acumyear):
        if self.away_cal(ji_style, taiyi_acumyear) == 1:
            return 1
        elif self.away_cal(ji_style, taiyi_acumyear) < 10:
            return self.away_cal(ji_style, taiyi_acumyear)
        elif self.away_cal(ji_style, taiyi_acumyear) % 10 == 0:
            return 5
        elif self.away_cal(ji_style, taiyi_acumyear) > 10 and self.away_cal(ji_style, taiyi_acumyear) < 20 :
            return self.away_cal(ji_style, taiyi_acumyear) - 10
        elif self.away_cal(ji_style, taiyi_acumyear) > 20 and self.away_cal(ji_style, taiyi_acumyear) < 30 :
            return self.away_cal(ji_style, taiyi_acumyear) - 20
        elif self.away_cal(ji_style, taiyi_acumyear) > 30 and self.away_cal(ji_style, taiyi_acumyear) < 40 :
            return self.away_cal(ji_style, taiyi_acumyear) - 30

    def away_vgen(self, ji_style, taiyi_acumyear):
        away_vg = self.away_general(ji_style, taiyi_acumyear) *3 % 10
        if away_vg == 0:
            away_vg = 5
        return away_vg

    #推太乙當時法
    def shensha(self, ji_style, taiyi_acumyear):
        if ji_style ==3:
            general = "天乙,螣蛇,朱雀,六合,勾陳,青龍,天空,白虎,太常,玄武,太陰,天后".split(",")
            tiany = self.skyyi(ji_style, taiyi_acumyear).replace("兌", "酉").replace("坎", "子").replace("震","卯").replace("離","午").replace("艮", "丑")
            kook = self.kook(ji_style, taiyi_acumyear).get("文")[0]
            if kook == "陽":
                return dict(zip(config.new_list(gong3, tiany) , general))
            else:
                return dict(zip(config.new_list(list(reversed(gong3)), tiany), general))
        else:
            return "太乙時計才顯示"
    #定算
    def set_cal(self, ji_style, taiyi_acumyear):
        lnum = [8, 8, 3, 3, 4,4, 9, 9, 2, 2, 7, 7, 6, 6, 1, 1]
        gong = list("亥子丑艮寅卯辰巽巳午未坤申酉戌乾")
        se = self.se(ji_style, taiyi_acumyear)
        lg = dict(zip(gong, lnum))
        se_num = lg.get(se)
        ty = self.ty(ji_style, taiyi_acumyear)
        se_jc = list(map(lambda x: x == se, jc)).count(True)
        ty_jc = list(map(lambda x: x == ty, tyjc)).count(True)
        se_jc1 = list(map(lambda x: x == se, jc1)).count(True)
        se_order = config.new_list(num, se_num)
        if se_jc == 1 and ty_jc != 1 and se_jc1 !=1 :
            if sum(se_order[: se_order.index(ty)]) == 0:
                return 1
            else:
                return sum(se_order[: se_order.index(ty)])+1
        elif se_jc !=1 and ty_jc != 1 and se_jc1 ==1:
            return sum(se_order[: se_order.index(ty)])
        elif se_jc != 1 and ty_jc ==1 and se_jc1 !=1:
            return sum(se_order[: se_order.index(ty)])
        elif se_jc ==1 and ty_jc ==1 and se_jc1 !=1 :
            return sum(se_order[: se_order.index(ty)])+1
        elif se_jc !=1 and ty_jc ==1 and se_jc1 ==1 :
            if sum(se_order[: se_order.index(ty)]) == 0:
                return 1
            else:
                return sum(se_order[: se_order.index(ty)])
        elif se_jc !=1 and ty_jc !=1 and se_jc1 !=1 :
            return sum(se_order[: se_order.index(ty)])
        elif se_jc !=1 and ty_jc !=1 and se_jc1 !=1 and se_num != ty:
            return sum(se_order[: se_order.index(ty)])
        elif se_jc !=1 and ty_jc !=1 and se_jc1 !=1 and se_num == ty:
            return ty

    def cal_des(self, num):
        t = []
        if num > 10 and num % 10 > 5:
            t.append("三才足數")
        if num < 10:
            t.append("無天，二曜虛蝕、五緯失度、慧孛飛流、霜雹為害")
        if num % 10 < 5:
            t.append("無地，有崩地震、川竭蝗蝻之象")
        if num % 10 == 0:
            t.append("無人，口舌妖言更相殘賊，疾疫、遷移、流亡")
        numdict = {1: "雜陰", 2: "純陰", 3: "純陽", 4: "雜陽", 6: "純陰", 7: "雜陰",
                   8: "雜陽", 9: "純陽", 11: "陰中重陽", 12: "下和", 13: "雜重陽",
                   14: "上和", 16: "下和", 17: "陰中重陽", 18: "上和", 19: "雜重陽",
                   22: "純陰", 23: "次和", 24: "雜重陰", 26: "純陰", 27: "下和",
                   28: "雜重陰", 29: "次和", 31: "雜重陽", 32: "次和", 33: "純陽",
                   34: "下和", 37: "雜重陽", 38: "下和", 39: "純陽"}
        t.append(numdict.get(num, None))
        return [i for i in t if i is not None]
    #定大將
    def set_general(self, ji_style, taiyi_acumyear):
        set_g = self.set_cal(ji_style, taiyi_acumyear)  % 10
        if set_g == 0:
            set_g = 5
        return set_g
    #定參將
    def set_vgen(self, ji_style, taiyi_acumyear):
        set_vg =  self.set_general(ji_style, taiyi_acumyear) *3 % 10
        if set_vg == 0:
            set_vg = 5
        return set_vg
    #十六宮
    def sixteen_gong1(self, ji_style, taiyi_acumyear):
        dict1 = [{self.skyeyes(ji_style, taiyi_acumyear):"昌"},{self.hegod(ji_style):"合"},{self.sf(ji_style, taiyi_acumyear):"始"},
                {self.se(ji_style, taiyi_acumyear):"目"}, {self.kingbase(ji_style, taiyi_acumyear):"君"}, {self.officerbase(ji_style, taiyi_acumyear):"臣"}, {self.pplbase(ji_style, taiyi_acumyear):"民"},
                {self.fgd(ji_style, taiyi_acumyear):"四"},{self.skyyi(ji_style, taiyi_acumyear):"乙"},{self.earthyi(ji_style, taiyi_acumyear):"地"},{self.zhifu(ji_style, taiyi_acumyear):"符"},
                {self.flyfu(ji_style, taiyi_acumyear):"飛"},{self.kingfu(ji_style, taiyi_acumyear):"帝"}, {self.wufu(ji_style, taiyi_acumyear):"福"},  {self.jigod(ji_style):"計"}]
        res = {"子":"", "丑":"", "艮":"","寅":"", "卯":"", "辰":"", "巽":"","巳":"", "午":"", "未":"", "申":"", "坤":"", "酉":"", "戌":"", "乾":"", "亥":"", "中":""}
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
        r = str(res.keys())[11:].replace("([","").replace("'","").replace("])","").replace(" ", "").split(",")
        return {r[i]:rrres[i] for i in range(0,16)}

    #十六宮之二
    def sixteen_gong(self, ji_style, taiyi_acumyear):
        dict1 = [{self.skyeyes(ji_style, taiyi_acumyear):"文昌"},{self.taishui(ji_style):"太歲"},{self.hegod(ji_style):"合神"},{self.sf(ji_style, taiyi_acumyear):"始擊"},
                 {self.se(ji_style, taiyi_acumyear):"定目"}, {self.kingbase(ji_style, taiyi_acumyear):"君基"}, {self.officerbase(ji_style, taiyi_acumyear):"臣基"}, {self.pplbase(ji_style, taiyi_acumyear):"民基"},
                 {self.fgd(ji_style, taiyi_acumyear):"四神"},{self.skyyi(ji_style, taiyi_acumyear):"天乙"},{self.earthyi(ji_style, taiyi_acumyear):"地乙"},{self.zhifu(ji_style, taiyi_acumyear):"直符"},
                 {self.flyfu(ji_style, taiyi_acumyear):"飛符"},{self.kingfu(ji_style, taiyi_acumyear):"帝符"},{self.taijun(ji_style, taiyi_acumyear):"太尊"}, {self.wufu(ji_style, taiyi_acumyear):"五福"},
                 {self.ty_gong(ji_style, taiyi_acumyear):"太乙"}, {num2gong(self.home_general(ji_style, taiyi_acumyear)):"主將"},  {num2gong(self.home_vgen(ji_style, taiyi_acumyear)):"主參"},
                 {num2gong(self.away_general(ji_style, taiyi_acumyear)):"客將"},  {num2gong(self.away_vgen(ji_style, taiyi_acumyear)):"客參"},
                 {num2gong(self.threewind(ji_style, taiyi_acumyear)):"三風"},  {num2gong(self.fivewind(ji_style, taiyi_acumyear)):"五風"},
                 {num2gong(self.eightwind(ji_style, taiyi_acumyear)):"八風"},  {num2gong(self.flybird(ji_style, taiyi_acumyear)):"飛鳥"},{num2gong(self.bigyo(ji_style, taiyi_acumyear)):"大游"},
                 {num2gong(self.smyo(ji_style, taiyi_acumyear)):"小游"},  {self.leigong(ji_style, taiyi_acumyear):"雷公"},  {self.yangjiu():"陽九"},  {self.baliu():"百六"},
                 {self.lijin():"臨津"},{self.lion():"獅子"}, {self.cloud(ji_style, taiyi_acumyear):"白雲"}, {self.dragon(ji_style, taiyi_acumyear):"白龍"}, {self.tiger(ji_style, taiyi_acumyear):"猛虎"}, {self.returnarmy(ji_style, taiyi_acumyear):"回軍"}
                 ]
        res = {"子":"", "丑":"", "艮":"","寅":"", "卯":"", "辰":"", "巽":"","巳":"", "午":"", "未":"", "申":"", "坤":"", "酉":"", "戌":"", "乾":"", "亥":"", "中":""}
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
        r = str(res.keys())[11:].replace("([","").replace("'","").replace("])","").replace(" ", "").split(",")
        return {r[i]:rrres[i] for i in range(0,16)}

    #太歲禽星
    def year_chin(self):
        chin_28_stars_code = dict(zip(range(1,29), su))
        if config.lunar_date_d(self.year, self.month, self.day).get("月") == "十二月" or config.lunar_date_d(self.year, self.month, self.day).get("月") == "十一月":
            if self.jq() == "立春":
                get_year_chin_number = (int(self.year)+15) % 28 #求年禽之公式為西元年加15除28之餘數
                if get_year_chin_number == int(0):
                    get_year_chin_number = int(28)
                year_chin = chin_28_stars_code.get(get_year_chin_number) #年禽
            else:
                get_year_chin_number = (int(self.year-1)+15) % 28 #求年禽之公式為西元年加15除28之餘數
                if get_year_chin_number == int(0):
                    get_year_chin_number = int(28)
                    year_chin = chin_28_stars_code.get(get_year_chin_number) #年禽
        elif config.lunar_date_d(self.year, self.month, self.day).get("月") != "十二月" or config.lunar_date_d(self.year, self.month, self.day).get("月") == "十一月":
            get_year_chin_number = (int(self.year)+15) % 28 #求年禽之公式為西元年加15除28之餘數
            if get_year_chin_number == int(0):
                get_year_chin_number = int(28)
            year_chin = chin_28_stars_code.get(get_year_chin_number) #年禽
        return year_chin
    #君基
    def kingbase(self, ji_style, taiyi_acumyear):
        kb = (self.accnum(ji_style, taiyi_acumyear) +250) % 360  / 30
        kb_v = dict(zip(range(0,13), config.new_list(di_zhi, "午"))).get(int(kb))
        return kb_v
    #臣基
    def officerbase(self, ji_style, taiyi_acumyear):
        return dict(zip(range(1,73), cycle(list("巳巳午午午未未未申申申酉酉酉戌戌戌亥亥亥子子子丑丑丑寅寅寅卯卯卯辰辰辰巳")))).get(self.kook(ji_style, taiyi_acumyear).get("數"))
    #民基
    def pplbase(self, ji_style, taiyi_acumyear):
        return dict(zip(range(1,73), cycle(config.new_list(di_zhi,"申")))).get(self.kook(ji_style, taiyi_acumyear).get("數"))
    #大游
    def bigyo(self, ji_style, taiyi_acumyear):
        by = int((self.accnum(ji_style, taiyi_acumyear) +34) % 388)
        if by < 36:
            by = by
        elif by > 36:
            by = by / 36
        byv = dict(zip([7,8,9,1,2,3,4,6],range(1,9))).get(int(by))
        if byv == 0 or byv is None:
            byv = 5
        return byv
    #小游
    def smyo(self, ji_style, taiyi_acumyear):
        sy = int(self.accnum(ji_style, taiyi_acumyear)  % 360)
        if sy < 24:
            sy = sy % 3
        elif sy > 24:
            sy = sy % 24
            if sy > 3:
                sy = sy % 3
        syv = dict(zip([1,2,3,4,6,7,8,9],range(1,9))).get(int(sy))
        if syv == 0 or syv is None:
            syv = 5
        return syv
    #四神
    def fgd(self, ji_style, taiyi_acumyear):
        return dict(zip(range(1,73), cycle(list("乾乾乾離離離艮艮艮震震震中中中兌兌兌坤坤坤坎坎坎巽巽巽巳巳巳申申申寅寅寅")))).get(self.kook(ji_style, taiyi_acumyear).get("數"))
    #天乙
    def skyyi(self, ji_style, taiyi_acumyear):
        return dict(zip(range(1,73), cycle(list("兌兌兌坤坤坤坎坎坎巽巽巽巳巳巳申申申寅寅寅乾乾乾離離離艮艮艮震震震中中中")))).get(self.kook(ji_style, taiyi_acumyear).get("數"))
    #地乙
    def earthyi(self, ji_style, taiyi_acumyear):
        return dict(zip(range(1,73), cycle(list("巽巽巽巳巳巳申申申寅寅寅乾乾乾離離離艮艮艮震震震中中中兌兌兌坤坤坤坎坎坎")))).get(self.kook(ji_style, taiyi_acumyear).get("數"))
    #直符
    def zhifu(self, ji_style, taiyi_acumyear):
        return dict(zip(range(1,73), cycle(list("中中中兌兌兌坤坤坤坎坎坎巽巽巽巳巳巳申申申寅寅寅乾乾乾離離離艮艮艮震震震")))).get(self.kook(ji_style, taiyi_acumyear).get("數"))
    #飛符
    def flyfu(self, ji_style, taiyi_acumyear):
        f = self.accnum(ji_style, taiyi_acumyear) % 360 % 36 / 3
        fv = dict(zip(range(1,13), config.new_list(di_zhi, "辰"))).get(int(f))
        if fv == 0 or fv is None:
            fv = "中"
        return fv
    #太乙在天外地內法
    def ty_gong_dist(self, ji_style, taiyi_acumyear):
        ty = self.ty(ji_style, taiyi_acumyear)
        tyg = num2gong(self.ty(ji_style, taiyi_acumyear))
        return multi_key_dict_get({tuple([1,8,3,4]): "太乙在"+tyg+"，助主。", tuple([9,2,6,7]): "太乙在"+tyg+"，助客。"}, ty)
    #推三門具不具
    def threedoors(self, ji_style, taiyi_acumyear):
        ty = self.ty(ji_style, taiyi_acumyear)
        ed = self.geteightdoors(ji_style, taiyi_acumyear)
        door = ed.get(ty)
        if door in list("休生開"):
            return "三門不具。"
        else:
            return "三門具。"
    #推五將發不發
    def fivegenerals(self, ji_style, taiyi_acumyear):
        hg = self.home_general(ji_style, taiyi_acumyear)
        ag = self.away_general(ji_style, taiyi_acumyear)
        if self.skyeyes_des(ji_style, taiyi_acumyear) == "" and hg != 5 and ag != 5:
            return "五將發。"
        elif hg == 5:
            return "主將主參不出中門，杜塞無門。"
        elif ag == 5:
            return "客將客參不出中門，杜塞無門。"
        else:
            return self.skyeyes_des(ji_style, taiyi_acumyear)+"。五將不發。"
    #推主客相闗法
    def wc_n_sj(self, ji_style, taiyi_acumyear):
        wc = self.skyeyes(ji_style, taiyi_acumyear)
        sj = self.sf(ji_style, taiyi_acumyear)
        wc_f = Ganzhiwuxing(wc)
        sj_f = Ganzhiwuxing(sj)
        hg = self.home_general(ji_style, taiyi_acumyear)
        ty = self.ty(ji_style, taiyi_acumyear)
        hguan = multi_key_dict_get(nayin_wuxing, config.gangzhi(self.year, self.month, self.day, self.hour, self.minute)[3])
        if hguan == wc_f:
            guan = "主關"
        elif hguan == sj_f:
            guan = "客關"
        else:
            guan = "關"
        relation = multi_key_dict_get(wuxing_relation_2, wc_f+sj_f)
        if relation == "我尅" and ty == hg:
            return "主將囚，不利主"
        elif relation == "我尅" and ty != hg:
            return  "主尅客，主勝"
        elif relation == "尅我":
            return guan + "得主人，客勝"
        elif relation == "比和" or "生我" or "我生":
            return guan + relation + "，和"
    #推八門分佈
    def geteightdoors(self, ji_style, taiyi_acumyear):
        ty = self.ty(ji_style, taiyi_acumyear)
        new_ty_order = config.new_list([8,3,4,9,2,7,6,1], ty)
        doors  = config.new_list(self.door, self.eight_door(ji_style, taiyi_acumyear))
        return dict(zip(new_ty_order, doors))
    #陽九
    def yangjiu(self):
        year = config.lunar_date_d(self.year, self.month, self.day).get("年")
        getyj = (year + 12607)%4560%456 % 12
        if getyj>=12:
            getyj = getyj % 12
            return dict(zip(range(1,13),config.new_list(di_zhi, "寅"))).get(getyj)
        elif getyj == 0:
            return dict(zip(range(1,13),config.new_list(di_zhi, "寅"))).get(12)
        else:
            return dict(zip(range(1,13),config.new_list(di_zhi, "寅"))).get(getyj)
    #百六
    def baliu(self):
        year = config.lunar_date_d(self.year, self.month, self.day).get("年")
        getbl = (year + 12607)%4320%288 % 24
        if getbl >12:
            getbl = (getbl - 12) %12
            return dict(zip(range(1,13),config.new_list(di_zhi, "卯"))).get(getbl)
        elif getbl == 0:
            return dict(zip(range(1,13),config.new_list(di_zhi, "酉"))).get(12)
        else:
            return dict(zip(range(1,13),config.new_list(di_zhi, "酉"))).get(getbl)
    #帝符
    def kingfu(self, ji_style, taiyi_acumyear):
        f = self.accnum(ji_style, taiyi_acumyear) % 20
        if f > 16:
            f = f - 16
        fv = dict(zip(range(1,17), config.new_list(gong1, "戌"))).get(int(f))
        if fv == 0 or fv is None:
            fv = "中"
        return fv
    #太尊
    def taijun(self, ji_style, taiyi_acumyear):
        f = self.accnum(ji_style, taiyi_acumyear) % 4
        fv = dict(zip(range(1,5), list("子午卯酉"))).get(int(f))
        if fv == 0  or fv is None:
            fv = "中"
        return fv
    #飛鳥
    def flybird(self, ji_style, taiyi_acumyear):
        f = self.accnum(ji_style, taiyi_acumyear) % 9
        fv = dict(zip(range(1,10), [1,8,3,4,9,2,7,6])).get(int(f))
        if fv == 0 or fv is None:
            fv = 5
        return fv
    #推太乙風雲飛鳥助戰法
    def flybird_wl(self, ji_style, taiyi_acumyear):
        fb = self.flybird(ji_style, taiyi_acumyear)
        hg = self.home_general(ji_style, taiyi_acumyear)
        ag = self.away_general(ji_style, taiyi_acumyear)
        hvg = self.home_vgen(ji_style, taiyi_acumyear)
        avg = self.away_vgen(ji_style, taiyi_acumyear)
        ty = self.ty(ji_style, taiyi_acumyear)
        wc = gong2.get(self.skyeyes(ji_style, taiyi_acumyear))
        sj = gong2.get(self.sf(ji_style, taiyi_acumyear))
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
    #五行
    def wuxing(self, ji_style, taiyi_acumyear):
        f = self.accnum(ji_style, taiyi_acumyear) // 5
        f = f % 5
        fv =  dict(zip(range(1,10), [1,3,5,7,9,2,4,6,8])).get(int(f))
        if fv == 0 or fv is None:
            fv = 5
        return fv
    #三風
    def threewind(self, ji_style, taiyi_acumyear):
        f = self.accnum(ji_style, taiyi_acumyear) % 9
        fv = dict(zip(range(1,9), [7,2,6,1,5,9,4,8])).get(int(f))
        if fv == 0 or fv is None:
            fv = 5
        return fv
    #五風
    def fivewind(self, ji_style, taiyi_acumyear):
        f = self.accnum(ji_style, taiyi_acumyear) % 29
        if f > 10:
            f = f - 9
        fv = dict(zip(range(1,10), [1,3,5,7,9,2,4,6,8])).get(int(f))
        if fv == 0 or fv is None:
            fv = 5
        return fv
    #八風
    def eightwind(self, ji_style, taiyi_acumyear):
        f = self.accnum(ji_style, taiyi_acumyear) % 9
        fv = dict(zip(range(1,9), [2,3,5,6,7,8,9,1])).get(int(f))
        if fv == 0 or fv is None:
            fv = 5
        return fv
    #五福
    def wufu(self, ji_style, taiyi_acumyear):
        f = int(self.accnum(ji_style, taiyi_acumyear) + 250) % 225 / 45
        fv = dict(zip(range(1,6), list("乾艮巽坤中"))).get(int(f))
        if fv == 0 or fv is None:
            fv = 5
        return fv
    #八門
    def eight_door(self, ji_style, taiyi_acumyear):
        acc = self.accnum(ji_style, taiyi_acumyear) % 240
        if acc == 0:
            acc = 120
        eightdoor_zhishi = acc // 30
        if eightdoor_zhishi % 30 != 0:
            eightdoor_zhishi = eightdoor_zhishi + 1
        elif eightdoor_zhishi == 0:
            eightdoor_zhishi = 1
        #ty_gong = self.ty()
        return dict(zip(list(range(1,9)),self.door)).get(eightdoor_zhishi)

    def pan(self, ji_style, taiyi_acumyear):
        return {
                "太乙計":config.taiyi_name(ji_style),
                "太乙公式類別":config.ty_method(taiyi_acumyear), 
                "公元日期":config.gendatetime(self.year, self.month, self.day, self.hour),
                "干支":gangzhi(self.year, self.month, self.day, self.hour, self.minute),
                "農曆":config.lunar_date_d(self.year, self.month, self.day),
                "年號":kingyear(config.lunar_date_d(self.year, self.month, self.day).get("年")),
                "紀元":self.jiyuan(ji_style, taiyi_acumyear),
                "太歲":self.taishui(ji_style),
                "局式":self.kook(ji_style, taiyi_acumyear),
                "陽九":self.yangjiu(),
                "百六":self.baliu(),
                "太乙落宮":self.ty(ji_style, taiyi_acumyear),
                "太乙":self.ty_gong(ji_style, taiyi_acumyear),
                "天乙":self.skyyi(ji_style, taiyi_acumyear),
                "地乙":self.earthyi(ji_style, taiyi_acumyear),
                "四神":self.fgd(ji_style, taiyi_acumyear),
                "直符":self.zhifu(ji_style, taiyi_acumyear),
                "文昌":[self.skyeyes(ji_style, taiyi_acumyear), self.skyeyes_des(ji_style, taiyi_acumyear)],
                "始擊":self.sf(ji_style, taiyi_acumyear),
                "主算":[self.home_cal(ji_style, taiyi_acumyear), self.cal_des(self.home_cal(ji_style, taiyi_acumyear))],
                "主將":self.home_general(ji_style, taiyi_acumyear),
                "主參":self.home_vgen(ji_style, taiyi_acumyear),
                "客算":[self.away_cal(ji_style, taiyi_acumyear), self.cal_des(self.away_cal(ji_style, taiyi_acumyear))],
                "客將":self.away_general(ji_style, taiyi_acumyear),
                "客參":self.away_vgen(ji_style, taiyi_acumyear),
                "定算":[self.set_cal(ji_style, taiyi_acumyear), self.cal_des(self.set_cal(ji_style, taiyi_acumyear))],
                "合神":self.hegod(ji_style),
                "計神":self.jigod(ji_style),
                "定目":self.se(ji_style, taiyi_acumyear),
                "君基":self.kingbase(ji_style, taiyi_acumyear),
                "臣基":self.officerbase(ji_style, taiyi_acumyear),
                "民基":self.pplbase(ji_style, taiyi_acumyear),
                "二十八宿值日":config.starhouse(self.year, self.month, self.day, self.hour),
                "太歲二十八宿":self.year_chin(),
                "太歲值宿斷事": su_dist.get(self.year_chin()),
                "始擊二十八宿":self.sf_num(ji_style, taiyi_acumyear),
                "始擊值宿斷事":su_dist.get(self.sf_num(ji_style, taiyi_acumyear)),
                "十天干歲始擊落宮預測": multi_key_dict_get (tengan_shiji, config.gangzhi(self.year, self.month, self.day, self.hour, self.minute)[0][0]).get(Ganzhiwuxing(self.sf(ji_style, taiyi_acumyear))),
                "八門值事":self.eight_door(ji_style, taiyi_acumyear),
                "八門分佈":self.geteightdoors(ji_style, taiyi_acumyear),
                "八宮旺衰":jieqi.gong_wangzhuai(),
                "推太乙當時法": self.shensha(ji_style, taiyi_acumyear),
                "推三門具不具":self.threedoors(ji_style, taiyi_acumyear),
                "推五將發不發":self.fivegenerals(ji_style, taiyi_acumyear),
                "推主客相闗法":self.wc_n_sj(ji_style, taiyi_acumyear),
                "推多少以占勝負":config.suenwl(self.home_cal(ji_style, taiyi_acumyear),
                                        self.away_cal(ji_style, taiyi_acumyear),
                                        self.home_general(ji_style, taiyi_acumyear),
                                        self.away_general(ji_style, taiyi_acumyear)),
                "推太乙風雲飛鳥助戰法":self.flybird_wl(ji_style, taiyi_acumyear),
                "推雷公入水":config.leigong(self.ty(ji_style, taiyi_acumyear)),
                "推臨津問道":config.lijin(self.year, self.month, self.day, self.hour, self.minute),
                "推獅子反擲":config.lion(self.year, self.month, self.day, self.hour, self.minute),
                "推白雲捲空":config.cloud(self.home_general(ji_style, taiyi_acumyear)),
                "推猛虎相拒":config.tiger(self.ty(ji_style, taiyi_acumyear)),
                "推白龍得雲":config.dragon(self.ty(ji_style, taiyi_acumyear)),
                "推回軍無言":config.returnarmy(self.away_general(ji_style, taiyi_acumyear)),
                }

if __name__ == '__main__':
    tic = time.perf_counter()
    print(Taiyi(2023,4,3,18,43).pan(3,0))
    toc = time.perf_counter()
    print(f"{toc - tic:0.4f} seconds")
