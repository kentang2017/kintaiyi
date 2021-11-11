# -*- coding: utf-8 -*-
"""
Created on Sun Nov  7 11:58:46 2021

@author: kentang
"""

from config import *
import sxtwl, re, math, itertools, datetime
import numpy as geek 

#%% 主程式
class Taiyi:
    taiyiyear = 10153917
    year_num = 365
    threeki_year = 284287
    jiajishui = 29277
    circle = 360 #周
    epoch = 60#紀
    rounds = 72#局	
    yuan = 72#元

    def __init__(self, year, month, day, hour):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.ymc = [11,12,1,2,3,4,5,6,7,8,9,10]
        self.rmc = list(range(1,32))
        #十六神
        self.sixtengod = dict(zip(list("子丑艮寅卯巽辰巳午未坤申酉戌乾亥"), re.findall("..","地主陽德和德呂申高叢太陽大炅大神大威天道大武武德太簇陰主陰德大義")))
       
        #陰陽遁定制
        self.yang_sixteen = list("申酉戌乾乾亥子丑艮寅卯辰巽巳午未坤坤")
        self.ying_sixteen = list("寅卯辰巽巽巳午未坤申酉戌乾亥子丑艮艮")
        self.yangji = list("寅丑子亥戌酉申未午巳辰卯")
        self.yingji = list("申未午巳辰卯寅丑子亥戌酉")
        self.findplace = {"陽":self.yang_sixteen, "陰":self.ying_sixteen}.get(self.kook()[0])
        self.findplace_num = dict(zip(self.findplace, range(1,19)))
        self.findji = {"陽":self.yangji, "陰":self.yingji}.get(self.kook()[0])
        #太乙
        self.taiyi = (self.taiyiyear + self.year ) % 24)
        
        #天目
        self.skyeyes_dict = {"陽" : list("未坤申酉戌乾乾亥子丑艮寅卯巽辰巳午未坤坤申酉戌乾乾亥子丑艮寅卯巽辰巳午未坤坤申酉戌乾乾亥子丑艮寅卯巽辰巳午未坤坤申酉戌乾乾亥子丑艮寅卯巽辰巳午未"),
        "陰":list("寅卯巽巽辰巳午未坤申酉戌乾亥子丑艮艮寅卯巽巽辰巳午未坤申酉戌乾亥子丑艮艮寅卯巽巽辰巳午未坤申酉戌乾亥子丑艮艮寅卯巽巽辰巳午未坤申酉戌乾亥子丑艮艮")}
        self.skyeyes = dict(zip(range(1,73), self.skyeyes_dict.get(self.kook()[0])).get(int(self.kook().replace("陰遁", "").replace("陽遁", "").replace("局", "")))
        
        #太歲
        self.taishui = self.gangzhi()[0][1]
        #合神
        self.hegod = dict(zip(list("子寅卯辰巳午丑亥戌酉申未"),list("丑亥戌酉申未子寅卯辰巳午"))).get(self.taishui)
        #文昌
        self.wancheong = dict(zip(range(1,19), self.findplace)).get( (self.taiyiyear + self.year) % 18)
        #計神
        self.jigod = dict(zip(Zhi, self.findji )).get(self.taishui)
        
        
        
    def find_jieqi(self):
        jieqi_list = twentyfourjieqi(self.year)
        s_date = list(jieqi_list.keys())
        date = datetime.strptime(str(self.year)+"-"+str(self.month)+"-"+str(self.day), '%Y-%m-%d').date()
        closest = sorted(s_date, key=lambda d: abs( date  - d))[0]
        test = {True:jieqi_list.get(s_date[s_date.index(closest) - 1]), False:jieqi_list.get(closest)}
        return test.get(closest>date)
    
    #干支
    def gangzhi(self):
        lunar = sxtwl.Lunar()
        cdate = lunar.getDayBySolar(self.year, self.month, self.day)
        yy_mm_dd = Gan[cdate.Lyear2.tg]+Zhi[cdate.Lyear2.dz],  Gan[cdate.Lmonth2.tg]+Zhi[cdate.Lmonth2.dz],  Gan[cdate.Lday2.tg]+Zhi[cdate.Lday2.dz]
        timegz = lunar.getShiGz(cdate.Lday2.tg, self.hour)
        new_hh = Gan[timegz.tg]+Zhi[timegz.dz]
        return yy_mm_dd[0], yy_mm_dd[1],  yy_mm_dd[2], new_hh
    
    def lunar_date_d(self):
        lunar = sxtwl.Lunar()
        day = lunar.getDayBySolar(self.year, self.month, self.day)
        return {"月": self.ymc[day.Lmc], "日":self.rmc[day.Ldi]}
    
    def dzdistance(self):
        lunar = sxtwl.Lunar()
        day = lunar.getDayBySolar(int(self.year), int(self.month), int(self.day) ).cur_dz
        return day
    
    def xzdistance(self):
        lunar = sxtwl.Lunar()
        day = lunar.getDayBySolar(int(self.year), int(self.month), int(self.day) ).cur_xz
        return day
        
    def kook(self):
        dz = self.dzdistance()
        xz = self.xzdistance()
        dz_date = datetime.datetime.strptime(str(self.year)+"/"+str(self.month)+"/"+str(self.day) , '%Y/%m/%d') - datetime.timedelta(days=dz)
        xz_date = datetime.datetime.strptime(str(self.year)+"/"+str(self.month)+"/"+str(self.day) , '%Y/%m/%d') - datetime.timedelta(days=xz)
        current_date = datetime.datetime.strptime(str(self.year)+"/"+str(self.month)+"/"+str(self.day) , '%Y/%m/%d')
        dz_kook = int((29277 + dz_date.year) * 365.2425) * 12 % 360 % 72
        if current_date >= xz_date and self.month >= 6:
            dun = "陰遁"
        else:
            dun = "陽遁"
        if self.hour == 23 and dz_kook + (dz * 12) % 72 == 60:
            kook = 1
            return dun + str(kook) + "局"
        elif self.hour == 23 and dz_kook + (dz * 12) % 72 != 60:
            kook = dz_kook + (dz * 12) % 72 + dict(zip(Zhi,range(1,13))).get(self.gangzhi()[3][1])
            dunkook = kook-60
            if dunkook < 0:
                dunkook = kook + 12
            return dun + str(dunkook) + "局"
        elif self.hour != 23:
            kook = dz_kook + (dz * 12) % 72 + dict(zip(Zhi,range(1,13))).get(self.gangzhi()[3][1])
            if kook > 72:
                kook = kook - 72
            return dun + str(kook) + "局"

    def getyuan(self):
        accnum = self.year + self.taiyiyear
        if round(accnum % self.circle) == 1:
            find_ji_num = 1
        else:
            find_ji_num = int(round((accnum % self.circle) / self.yuan, 0))
        fiveyuen_d = dict(zip(range(1,6), [jiazi()[i] for i in [0,12,24,36,48]]))
        jiyuan = fiveyuen_d.get(find_ji_num) 
        return jiyuan
    
    def getepoch(self):
        accnum = self.year + self.taiyiyear
        if round(accnum % self.circle) == 1:
            find_ji_num = 1
        else:
            find_ji_num = round((accnum % self.circle) / self.epoch, 0)
        cnum = list("一二三四五六七八九十")
        return "第"+dict(zip(range(1,8), cnum[0:7])).get(find_ji_num)+"紀"
    
    def jiyuan(self):
        return self.getyuan()+ "元" + self.getepoch()
    
    def tdate(self):
        return dict(zip(list("年月日時"), [self.taiyiyear + self.year, 
                        (self.taiyiyear + self.year) * 12 - 10 + self.month,  
                        (self.taiyiyear + self.year) * 12 - 10 + self.month + self.dzdistance() + 1,
                        ((self.taiyiyear + self.year) * 12 - 10 + self.month + self.dzdistance()+ 1) * 12 + math.ceil(self.hour / 2 ) + 1
                        ]))
  
    def thaiyi(self):
        arr = geek.arange(10) 
        repetitions = 3
        arrangement = geek.repeat(arr, repetitions) 
        arrangement_r = list(reversed(arrangement))
        yy_dict = {"陽": dict(zip(range(1,73), list(itertools.chain.from_iterable([list(arrangement)[3:15]+ list(arrangement)[18:]] * 3)))),  "陰": dict(zip(range(1,73), list(itertools.chain.from_iterable([list(arrangement_r)[3:15]+ list(arrangement_r)[18:]] * 3))))}
        return yy_dict.get(self.kook()[0]).get(int(self.kook().replace("陰遁", "").replace("陽遁", "").replace("局", "")))
    
if __name__ == '__main__':
    print(Taiyi(2021,11,8,23).wancheong())
