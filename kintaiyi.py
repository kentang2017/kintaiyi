# -*- coding: utf-8 -*-
"""
Created on Sun Nov  7 11:58:46 2021

@author: kentang
"""

from config import *
import sxtwl, re, math, itertools, datetime
import numpy as np

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
        self.dz_date = datetime.datetime.strptime(str(self.year)+"/"+str(self.month)+"/"+str(self.day) , '%Y/%m/%d') - datetime.timedelta(days=self.dzdistance())
        self.accHour = int(int((29277 + self.dz_date.year) * 365.2425) * 12) + ((self.dzdistance()-1) * 12) + dict(zip(Zhi,range(1,13))).get(self.gangzhi()[3][1])
        self.ymc = [11,12,1,2,3,4,5,6,7,8,9,10]
        self.num = [8,3,4,9,2,7,6,1]
        self.rmc = list(range(1,32))
        #十六神
        self.sixtengod = dict(zip(list("子丑艮寅卯巽辰巳午未坤申酉戌乾亥"), re.findall("..","地主陽德和德呂申高叢太陽大炅大神大威天道大武武德太簇陰主陰德大義")))
        
        #間辰
        self.jc = list("丑寅辰巳未申戌亥")
        self.jc1 = list("巽艮坤乾")
        self.tyjc = [1,3,7,9]
        
        #陰陽遁定制
        self.gong = dict(zip(list("子丑艮寅卯辰巽巳午未坤申酉戌乾亥"), range(1,17)))
        self.gong1 = list("子丑艮寅卯辰巽巳午未坤申酉戌乾亥")
        self.yang_sixteen = list("申酉戌乾乾亥子丑艮寅卯辰巽巳午未坤坤")
        self.ying_sixteen = list("寅卯辰巽巽巳午未坤申酉戌乾亥子丑艮艮")
        self.yangji = list("寅丑子亥戌酉申未午巳辰卯")
        self.yingji = list("申未午巳辰卯寅丑子亥戌酉")
        self.ying = {"陰":[4,9,2,7,6,1,8,3], "陽":[1,8,3,4,9,2,7,6]}
        self.findplace = {"陽":self.yang_sixteen, "陰":self.ying_sixteen}.get(self.kook()[0])
        self.findplace_num = dict(zip(self.findplace, range(1,19)))
        self.findji = {"陽":self.yangji, "陰":self.yingji}.get(self.kook()[0])
  
        #文昌
        self.skyeyes_dict = {"陽" : list("未坤申酉戌乾乾亥子丑艮寅卯巽辰巳午未坤坤申酉戌乾乾亥子丑艮寅卯巽辰巳午未坤坤申酉戌乾乾亥子丑艮寅卯巽辰巳午未坤坤申酉戌乾乾亥子丑艮寅卯巽辰巳午未"),
        "陰":list("寅卯辰巽巽巳午未坤申酉戌乾亥子丑艮艮寅卯辰巽巽巳午未坤申酉戌乾亥子丑艮艮寅卯辰巽巽巳午未坤申酉戌乾亥子丑艮艮寅卯辰巽巽巳午未坤申酉戌乾亥子丑艮艮")}
        self.skyeyes = dict(zip(range(1,73),self.skyeyes_dict.get(self.kook()[0]))).get(int(self.kook().replace("陰遁", "").replace("陽遁", "").replace("局", "")))
    
        #太歲
        self.taishui = self.gangzhi()[3][1]
        #合神
        self.hegod = dict(zip(list("子寅卯辰巳午丑亥戌酉申未"),list("丑亥戌酉申未子寅卯辰巳午"))).get(self.taishui)
        #計神
        self.jigod = dict(zip(Zhi, self.findji )).get(self.taishui)
        
        
       
    def new_list(self, olist, o):
        zhihead_code = olist.index(o)
        res1 = []
        for i in range(len(olist)):
            res1.append( olist[zhihead_code % len(olist)])
            zhihead_code = zhihead_code + 1
        return res1
        
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
        accHour = int((29277 + dz_date.year) * 365.2425) * 12 
        dz_kook = accHour % 360 % 72
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
    def gakook(self):
        #掩 : 太乙 文昌 同宮 / 始擊 太乙 同宮
        #迫 : 文昌在太乙左右
        #關 : 主客四將同宮
        #囚 : 主客四將 太乙同宮
        #擊 : 始擊在太乙左右
        #格 : 客大、參將 與 太乙 相對
        #對 : 文昌 太乙 所在宮 五行相沖
        #提挾 :  始擊、文昌在太乙左右
        #四郭固 : 文昌 太乙同宮 主大參關 / 始擊 太乙同宮 客大參關
        #四郭杜 : 文昌與客參將同宮，客大，主參將同宮，又逢掩、迫、關、囚
        return 

    def ty(self):
        arr = np.arange(10) 
        repetitions = 3
        arrangement = np.repeat(arr, repetitions) 
        arrangement_r = list(reversed(arrangement))
        yy_dict = {"陽": dict(zip(range(1,73), list(itertools.chain.from_iterable([list(arrangement)[3:15]+ list(arrangement)[18:]] * 3)))),  "陰": dict(zip(range(1,73), (list(arrangement_r)[:12] + list(arrangement_r)[15:][:-3]) * 3))}
        return yy_dict.get(self.kook()[0]).get(int(self.kook().replace("陰遁", "").replace("陽遁", "").replace("局", "")))   
    
    #始擊
    def sf(self):
        wc = self.skyeyes
        jd = self.jigod
        if wc == jd:
            sf = "艮"
            return sf
        elif wc != jd:
            start = self.new_list(self.gong1, jd)
            start1 = len(start[0:start.index("艮")+1])
            start2 = self.new_list(self.gong1, wc)[start1-1]
            return  start2
        
    #定目
    def se(self):
        wc = self.skyeyes
        hg = self.hegod
        ts = self.taishui
        start = self.new_list(self.gong1, hg)
        start1 = len(start[:start.index(ts)+1])
        start2 = self.new_list(self.gong1, wc)[start1-1]
        return  start2
    
       
    def home_cal(self):
        num = self.num
        lnum = [8, 8, 3,  3, 4,4, 9, 9, 2, 2, 7, 7, 6, 6, 1, 1]
        gong = list("亥子丑艮寅卯辰巽巳午未坤申酉戌乾")
        wc = self.skyeyes
        lg = dict(zip(gong, lnum))
        wc_num = lg.get(wc)
        ty = self.ty()
        wc_jc =  [i == wc for i in self.jc].count(True)
        ty_jc = [i == ty for i in self.tyjc].count(True)
        wc_jc1 =  [i == wc for i in self.jc1].count(True)
        wc_order = self.new_list(num, wc_num)
        if wc_jc == 1 and ty_jc != 1 and wc_jc1 !=1 :
            return sum(wc_order[: wc_order.index(ty)])+1
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
        
    def home_general(self):
        return self.home_cal()  % 10
    
    def home_vgen(self):
        return self.home_general() *3 % 10
        
    def away_cal(self):
        num = self.num
        lnum = [8, 8, 3,  3, 4,4, 9, 9, 2, 2, 7, 7, 6, 6, 1, 1]
        gong = list("亥子丑艮寅卯辰巽巳午未坤申酉戌乾")
        sf = self.sf()
        lg = dict(zip(gong, lnum))
        sf_num = lg.get(sf)
        ty = self.ty()
        sf_jc =  [i == sf for i in self.jc].count(True)
        ty_jc = [i == ty for i in self.tyjc].count(True)
        sf_jc1 =  [i == sf for i in self.jc1].count(True)
        sf_order = self.new_list(num, sf_num)
        if sf_jc == 1 and ty_jc != 1 and sf_jc1 !=1 :
            return sum(sf_order[: sf_order.index(ty)])+1
        elif sf_jc !=1 and ty_jc != 1 and sf_jc1 ==1:
            return sum(sf_order[: sf_order.index(ty)])
        elif sf_jc != 1 and ty_jc ==1 and sf_jc1 !=1:
            return sum(sf_order[: sf_order.index(ty)]) 
        elif sf_jc ==1 and ty_jc ==1 and sf_jc1 !=1 :
            return sum(sf_order[: sf_order.index(ty)])
        elif sf_jc !=1 and ty_jc ==1 and sf_jc1 ==1 :
            return sum(sf_order[: sf_order.index(ty)])
        elif sf_jc !=1 and ty_jc !=1 and sf_jc1 !=1 and sf_num != ty:
            return sum(sf_order[: sf_order.index(ty)])
        elif sf_jc !=1 and ty_jc !=1 and sf_jc1 !=1 and sf_num == ty:
            return ty
    
    def away_general(self):
        return self.away_cal()  % 10
    
    def away_vgen(self):
        return self.away_general() *3 % 10
        
    def set_cal(self):
        num = self.num
        lnum = [8, 8, 3,  3, 4,4, 9, 9, 2, 2, 7, 7, 6, 6, 1, 1]
        gong = list("亥子丑艮寅卯辰巽巳午未坤申酉戌乾")
        se = self.se()
        lg = dict(zip(gong, lnum))
        se_num = lg.get(se)
        ty = self.ty()
        se_jc =  [i == se for i in self.jc].count(True)
        ty_jc = [i == ty for i in self.tyjc].count(True)
        se_jc1 =  [i == se for i in self.jc1].count(True)
        se_order = self.new_list(num, se_num)
        if se_jc == 1 and ty_jc != 1 and se_jc1 !=1 :
            return sum(se_order[: se_order.index(ty)])+1
        elif se_jc !=1 and ty_jc != 1 and se_jc1 ==1:
            return sum(se_order[: se_order.index(ty)])
        elif se_jc != 1 and ty_jc ==1 and se_jc1 !=1:
            return sum(se_order[: se_order.index(ty)])
        elif se_jc ==1 and ty_jc ==1 and se_jc1 !=1 :
            return sum(se_order[: se_order.index(ty)])
        elif se_jc !=1 and ty_jc ==1 and se_jc1 ==1 :
            return sum(se_order[: se_order.index(ty)])
        elif se_jc !=1 and ty_jc !=1 and se_jc1 !=1 :
            return sum(se_order[: se_order.index(ty)])
        elif se_jc !=1 and ty_jc !=1 and se_jc1 !=1 and se_num != ty:
            return sum(sf_order[: sf_order.index(ty)])
        elif se_jc !=1 and ty_jc !=1 and se_jc1 !=1 and se_num == ty:
            return ty
    
    def cal_des(self, num):
        t = []
        if num > 10 and num % 10 > 5:
            t.append("三才足數")
        if num < 10:
            t.append("無天")
        if num % 10 < 5:
            t.append("無地")
        if num % 10 == 0:
            t.append("無人")
        numdict = {1: "雜陰", 2: "純陰", 3: "純陽", 4: "雜陽", 6: "純陰", 7: "雜陰", 8: "雜陽", 9: "純陽",
                   11: "陰中重陽", 12: "下和", 13: "雜重陽", 14: "上和", 16: "下和", 17: "陰中重陽", 18: "上和", 19: "雜重陽",
                   22: "純陰", 23: "次和", 24: "雜重陰", 26: "純陰", 27: "下和", 28: "雜重陰", 29: "次和", 31: "雜重陽",
                   32: "次和", 33: "純陽", 34: "下和", 37: "雜重陽", 38: "下和", 39: "純陽"}
        t.append(numdict.get(num, None))
        return [i for i in t if i is not None]
    
    def set_general(self):
        return self.set_cal()  % 10
    
    def set_vgen(self):
        return self.set_general() *3 % 10
    
    def sixteen_gong(self):
        dict1 = [{self.skyeyes:"文昌"},{self.taishui:"太歲"},{self.hegod:"合神"},{"始擊":self.sf()},
                 {self.se():"定目"}, {self.kingbase():"君基"}, {self.officerbase():"臣基"}, {self.pplbase():"民基"},
                 {self.fgd():"四神"},{self.skyyi():"天乙"},{self.earthyi():"地乙"},{self.zhifu():"直符"},
                 {self.flyfu():"飛符"},{self.kingfu():"帝符"},{self.taijun():"太尊"}, {self.wufu():"五福"} ]
        res = {"子":"", "丑":"", "艮":"","寅":"", "卯":"", "辰":"", "巽":"","巳":"", "午":"", "未":"", "申":"", "坤":"", "酉":"", "戌":"", "乾":"", "亥":""}
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
        return res 

    def nine_gong(self):
        dict1 = [{self.home_general():"主將"},{self.home_vgen():"主參"},{self.away_general():"客將"},
                 {self.away_vgen():"客參"},{self.set_general():"定將"},{self.set_vgen():"定參"},
                 {self.ty():"太乙"}, {self.threewind():"三風"},  {self.fivewind():"五風"},
                 {self.eightwind():"八風"},  {self.flybird():"飛鳥"},{self.bigyo():"大游"},
                 {self.smyo():"小游"},]
        res = {8:"", 3:"", 4:"", 9:"", 2:"", 7:"", 6:"", 1:""}
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
        return res 
    
    #君基
    def kingbase(self):
        kb = (self.accHour +250) % 360  / 30
        return dict(zip(range(1,13), self.new_list(Zhi, "午"))).get(int(kb))
    
    #臣基
    def officerbase(self):
        ob = (self.accHour +250) % 360  % 36 / 3
        return dict(zip(range(1,13), self.new_list(Zhi, "午"))).get(int(ob))
    #民基
    def pplbase(self):
        pb = (self.accHour +250) % 360 % 12
        return dict(zip(range(1,13), self.new_list(Zhi, "戌"))).get(int(pb))

    #大游
    def bigyo(self):
        by = int((self.accHour +34) % 388)
        if by < 36:
            by = by
        elif by > 36:
            by = by / 36
        return dict(zip([7,8,9,1,2,3,4,6],range(1,9))).get(int(by))

    #小游
    def smyo(self):
        sy = int(self.accHour  % 360)
        if sy < 24:
            sy = sy % 3 
        elif sy > 24:
            sy = sy % 24
            if sy > 3:
                sy = sy % 3
        return dict(zip([1,2,3,4,6,7,8,9],range(1,9))).get(int(sy))
    
    #四神
    def fgd(self):
        f = self.accHour % 360 % 36 / 3 
        return dict(zip(range(1,13), self.new_list(Zhi, "亥"))).get(int(f))
    
    #天乙
    def skyyi(self):
        f = self.accHour % 360 % 36 / 3 
        return  dict(zip(range(1,13), self.new_list(Zhi, "酉"))).get(int(f))

    #地乙
    def earthyi(self):
        f = self.accHour % 360 % 36 / 3 
        return  dict(zip(range(1,13), self.new_list(Zhi, "巳"))).get(int(f))

    #直符
    def zhifu(self):
        f = self.accHour % 360 % 36 / 3 
        return dict(zip(range(1,14), ["中"]+self.new_list(Zhi, "酉"))).get(int(f))
    
    #飛符
    def flyfu(self):
        f = self.accHour % 360 % 36 / 3 
        return dict(zip(range(1,13), self.new_list(Zhi, "辰"))).get(int(f))
    
    #帝符
    def kingfu(self):
        f = self.accHour  %20
        if f > 16:
            f = f - 16 
        return dict(zip(range(1,17), self.new_list(self.gong1, "戌"))).get(int(f))
    
    #太尊
    def taijun(self):
        f = self.accHour  % 4
        return dict(zip(range(1,5), list("子午卯酉"))).get(int(f))

    #飛鳥
    def flybird(self):
        f = self.accHour  % 9
        return dict(zip(range(1,10), [1,8,3,4,9,2,7,6])).get(int(f))
    
    #五行
    def wuxing(self):
        f = int(self.accHour) // 5
        f = f % 5
        return  dict(zip(range(1,10), [1,3,5,7,9,2,4,6,8])).get(int(f))
    
    #三風
    def threewind(self):
        f = int(self.accHour) % 9
        return  dict(zip(range(1,9), [7,2,6,1,5,9,4,8])).get(int(f))
    
    #五風
    def fivewind(self):
        f = int(self.accHour) % 29
        if f > 10:
            f = f - 9
        return  dict(zip(range(1,10), [1,3,5,7,9,2,4,6,8])).get(int(f))
    
    #八風
    def eightwind(self):
        f = int(self.accHour) % 9
        return  dict(zip(range(1,9), [2,3,5,6,7,8,9,1])).get(int(f))
    
    #五福
    def wufu(self):
        f = int(self.accHour + 250) % 225 / 45 
        return dict(zip(range(1,6), list("乾艮巽坤中"))).get(int(f))
    
    def pan(self):
        return {
                "干支":self.gangzhi(),
                "農曆":self.lunar_date_d(),
                "紀元":self.jiyuan(),
                "時局":self.kook(),
                "太乙":self.ty(),
                "文昌":self.skyeyes,
                "太歲":self.taishui,
                "合神":self.hegod,
                "計神":self.jigod,
                "始擊":self.sf(),
                "定目":self.se(),
                "主算":[self.home_cal(), self.cal_des(self.home_cal())],
                "客算":[self.away_cal(), self.cal_des(self.away_cal())],
                "定算":[self.set_cal(), self.cal_des(self.set_cal())],
                "九宮":self.nine_gong(), 
                "十六宮":self.sixteen_gong(),
                }


if __name__ == '__main__':
    print(Taiyi(2021,11,15,12).pan())
