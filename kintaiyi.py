# -*- coding: utf-8 -*-
"""
Created on Sat May 16 21:50:28 2020

@author: hooki
"""
from config import *
from JDate import *
from SolarTerms import *
import sxtwl
import datetime
import math 

class Taiyi():
    taiyiyear = 10153917
    year_num = 365
    threeki_year = 284287
    circle = 360 #周
    epoch = 60#紀
    rounds = 72#局	
    yuan = 72#元
    
    def __init__(self, year, month, day, hour):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        
    def lunar_date(self):
        lunar = sxtwl.Lunar()  #实例化日历库
        day = lunar.getDayBySolar(self.year, self.month, self.day)
        if day.Lleap:
            ld =  "潤"+ ymc[day.Lmc]+"月"+rmc[day.Ldi]+"日"
        else:
            ld = ymc[day.Lmc]+"月"+ rmc[day.Ldi]+"日"
        return  {"月": r_cnum_dict.get(ymc[day.Lmc].replace("潤", "")), "日":day.Ldi, "日期":ld+self.gangzhi()[3][1]+"時"}
    
    def gangzhi(self):
        lunar = sxtwl.Lunar()
        cdate = lunar.getDayBySolar(self.year, self.month, self.day)
        yy_mm_dd = Gan[cdate.Lyear2.tg]+Zhi[cdate.Lyear2.dz],  Gan[cdate.Lmonth2.tg]+Zhi[cdate.Lmonth2.dz],  Gan[cdate.Lday2.tg]+Zhi[cdate.Lday2.dz]
        timegz = lunar.getShiGz(cdate.Lday2.tg, self.hour)
        new_hh = Gan[timegz.tg]+Zhi[timegz.dz]
        return yy_mm_dd[0], yy_mm_dd[1],  yy_mm_dd[2], new_hh
    
    def jieqi(self):
        jiqilist = paiYue(self.year)
        new_list = []
        jieqi_name = [d for d in list(jiqilist.values())]
        datelist =  list(paiYue(self.year).keys())
        newdatelist = []
        if len(datelist[0]) < 10:
            for i in datelist:
                if len(i) > 0 and len(i) < 2:
                    add = "000"+i
                elif len(i) > 2 and len(i) < 4:
                    add = "00"+i
                elif len(i) > 3:
                    add = "0"+i
                elif len(i) == 4:
                    add = i
                newdatelist.append(add)
            jiqilist_f = dict(zip(newdatelist, jieqi_name))
        else:
            jiqilist_f = jiqilist
    
        for i in list(jiqilist_f.keys()):
            b = datetime.datetime.strptime(i, '%Y-%m-%d')
            new_list.append(b)
        new_jieqi_list = dict(zip(new_list, jieqi_name))
        s_date = list(new_jieqi_list.keys())
        date = datetime.datetime.strptime(str(self.year).zfill(4)+"-"+str(self.month)+"-"+str(self.day), '%Y-%m-%d')
        closest = sorted(s_date, key=lambda d: abs( date  - d))[0]
        test = {True:new_jieqi_list.get(s_date[s_date.index(closest) - 1]), False:new_jieqi_list.get(closest)}
        return test.get(closest>date)

    def dzdistance(self):
        lunar = sxtwl.Lunar()
        ldday = lunar.getDayByLunar(self.year, self.month, self.day)   
        return ldday.cur_dz
    
    def getyuan(self, accnum):
        if round(accnum % self.circle) == 1:
            find_ji_num = 1
        else:
            find_ji_num = int(round((accnum % self.circle) / self.yuan, 0))
        jiyuan = fiveyuen_d.get(find_ji_num) 
        return jiyuan

    def getepoch(self, accnum):
        if round(accnum % self.circle) == 1:
            find_ji_num = 1
        else:
            find_ji_num = round((accnum % self.circle) / self.epoch, 0)
        return "第"+dict(zip(range(1,8), cnum[0:7])).get(find_ji_num)+"紀"
    
    def jiyuan(self, accnum):
        return self.getyuan(accnum)+ "元" + self.getepoch(accnum)
    
    def getround(self, accnum):
        find_ji_num = (accnum % self.circle) % self.rounds
        if find_ji_num == 0:
            find_ji_num = 72
        return find_ji_num
    
    def yinyang_dun(self):
        ld = self.lunar_date()
        dun_dict = {tuple(solarTermsNameList[0:12]+[solarTermsNameList[-1]]):"陽遁", tuple(solarTermsNameList[12:23]):"陰遁"}
        return multi_key_dict_get(dun_dict, self.jieqi())

    def tdate(self):
        return dict(zip(list("年月日時"), [self.taiyiyear + self.year, 
                        (self.taiyiyear + self.year) * 12 - 10 + self.month,  
                        (self.taiyiyear + self.year) * 12 - 10 + self.month + self.dzdistance() + 1,
                        ((self.taiyiyear + self.year) * 12 - 10 + self.month + self.dzdistance()+ 1) * 12 + math.ceil(self.hour / 2 ) + 1
                        ]))
    def yearpan(self):
        pan = "年"
        jiyuan = self.jiyuan(self.tdate().get(pan)) 
        dunkook = self.yinyang_dun() + str(self.getround(self.tdate().get(pan))) + "局"
        return self.execute(pan, jiyuan, dunkook)
    
    def monthpan(self):
        pan = "月"
        jiyuan = self.jiyuan(self.tdate().get("年")-self.tdate().get("月")+self.dzdistance()) 
        dunkook = self.yinyang_dun() + str(self.getround(self.tdate().get("月"))) + "局"
        inCircle = self.tdate().get("月") % self.circle
        inEpoch = self.tdate().get("月") % self.epoch
        return self.execute(pan, jiyuan, dunkook)
    
    def daypan(self):
        pan = "日"
        tmonth_k = self.tdate().get("年") - self.tdate().get("月") + self.tdate().get("日") - 10
        jiyuan = self.jiyuan(self.tdate().get("日")) 
        dunkook = self.yinyang_dun() + str(self.getround(tmonth_k)) + "局"  + self.taiyi_god(pan)[2] 
        return self.execute(pan, jiyuan, dunkook)
    
    def hourpan(self):
        pan = "時"
        jiyuan = self.jiyuan(self.tdate().get("年")- self.tdate().get("月")+self.tdate().get("日")-self.tdate().get("時")) 
        dunkook = self.yinyang_dun() + str(self.getround(self.tdate().get("時"))) + "局  " + self.taiyi_god(pan)[2]
        return self.execute(pan, jiyuan, dunkook)
    
    def execute(self, pan, jiyuan, dunkook):
        tyear = self.tdate().get("年")
        tmonth = self.tdate().get("月")
        tday = self.tdate().get("日")
        thour = self.tdate().get("時")
        if pan == "月" or pan == "年":
            dunkook = "陽遁"
        return {**{"日期":self.lunar_date().get("日期"), pan+"計太乙":{"積年":tyear,"歲積":thour, "紀元":jiyuan, "局數":dunkook + " "+ self.taiyi_god(pan)[1]}}, "八門值事":self.eightdoor_stand(pan), **{"排盤":self.paipan(pan)}}

    def taiyi_god(self, pan):
        accnum = self.tdate().get(pan)
        jiyuan = accnum % 360
        if jiyuan == 0:
            jiyuan = 360
        jiyuancircle = jiyuan // 72
        yuan =  jiyuan % 72
        if yuan == 0:
            jiyuancircle = jiyuancircle - 1
            yuan =  72
        jiyuancircle = jiyuancircle + 1
        taiyi_gong = yuan % 24
        if taiyi_gong == 0:
            taiyi_gong == 24
        
        taiyigong = taiyi_gong // 3
        if taiyi_gong % 3 != 0:
            taiyigong  = taiyigong +1
        
        if taiyigong >= 5:
            taiyigong = taiyigong + 1
        if self.yinyang_dun() == "陽遁":
            taiyigong = 10 - taiyigong 
        taiyistandf = lambda x: "理人" if x == 0 else ("理天" if x == 1 else "理地")
        taiyistand = taiyistandf(taiyi_gong % 3) 
        taiyi = cnum_dict.get(taiyigong)
        if taiyi == "中":
            taiyi = "一"
        return [{taiyi: "太乙"}, taiyistand, taiyigong]
    
    def accnumZhi(self, pan, num):
        accnum = self.tdate().get(pan)
        accnum_h = accnum % num
        if accnum_h == 0:
            accnum_h = num
        return [accnum_h, Zhi_dict.get(accnum_h)]
    #計神
    def jigod(self, pan):
        if self.yinyang_dun() == "陽遁":
            jigod = taiyi_symbols.index("寅") + (-1 * self.accnumZhi(pan, 12)[0] - taiyi_symbols.index("子")) 
        else:
            jigod = taiyi_symbols.index("申") + (-1 * self.accnumZhi(pan, 12)[0] - taiyi_symbols.index("子"))
        return {taiyi_symbols[jigod]:"計神"}
    #合神
    def hegod(self, pan):
        return {taiyi_symbols[taiyi_symbols.index("丑") + (-1 * self.accnumZhi(pan, 12)[0] - taiyi_symbols.index("子"))]: "合神"}
    #天目, 文昌
    def skyeyes(self, pan):
        skyeyes = self.accnumZhi(pan, 18)[0]
        if skyeyes == 0:
            skyeyes = 18 
        if self.yinyang_dun() == "陽遁": 
            wancheong = ("0", "申", "酉", "戌", "乾", "乾", "亥", "子", "丑", "艮", "寅", "卯",
                    "辰", "巽", "巳", "午", "未", "坤", "坤",)[skyeyes]
        else:
            wancheong = ("0", "寅", "卯", "辰", "巽", "巽", "巳", "午", "未", "坤", "申", "酉",
                    "戌", "乾", "亥", "子", "丑", "艮", "艮",)[skyeyes]
        return [{skyeyes:"天目"}, {wancheong:"文昌"}, skyeyes]
    #始擊
    def shiji(self, pan):
        jigod = list(self.jigod(pan).keys())[0]
        wancheong = list(self.skyeyes(pan)[1].keys())[0]
        new_jigod = new_list(taiyi_symbols, jigod) 
        hede = new_jigod.index("艮")
        move_n = new_jigod.index(jigod) - hede
        new_wancheong = new_list(taiyi_symbols, wancheong) 
        return new_jigod[move_n]
    #主大將、主參將
    def home_generals(self, pan):
        wancheong = self.accnumZhi(pan, 18)[0]
        taiyi = self.taiyi_god(pan)[2]
        maincal = 0
        if wancheong == 0:
            maincal = 1
        for i in range(0, 16):
            if wancheong + i == taiyi:
                break
            maincal = maincal + (wancheong + i)
        if taiyi == wancheong:
            maincal = taiyi
        
        home_m_gen_n = maincal % 10
        if home_m_gen_n == 0:
            home_m_gen_n = maincal % 9 
        home_m_gen = cnum_dict.get(home_m_gen_n)
        
        home_s_gen_n = (home_m_gen_n * 3) % 10 
        home_s_gen = cnum_dict.get(home_s_gen_n)
        return [{maincal :"主算"}, {home_m_gen:"主大將"}, {home_s_gen:"主參將"}]
   
    def eightdoor_stand(self, pan):
        eightdoor_year = self.tdate().get(pan) % 240
        if eightdoor_year == 0:
           eightdoor_year = 240
        eightdoorstand = eightdoor_year // 30
        if eightdoor_year % 30 !=30:
            eightdoorstand = eightdoorstand +1 
        taiyigongn = self.taiyi_god(pan)[1]
        taiyigong = gong_dict.get(eightdoorstand)
        if pan == "日":
            eightdoorstand = eightdoorstand - 1 
        elif pan == "時":
            eightdoorstand = eightdoorstand - 1
        return door_dict.get(eightdoorstand)
    
    def paipan(self, pan):
        new_gonglist = {**self.taiyi_god(pan)[0], **self.jigod(pan)}
        return {**{"排盤":taiyi_symbols}, **{"門排盤": new_gonglist}}
    
print(Taiyi(2023,6,27,14).shiji("日"))
#print(YearPan(2020))
