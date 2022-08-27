# -*- coding: utf-8 -*-
"""
Created on Sat Aug 27 18:11:44 2022

@author: kentang
"""

import sxtwl, re, math, itertools, datetime, time, ephem
import numpy as np

def jiazi():
    Gan = '甲乙丙丁戊己庚辛壬癸'
    Zhi = '子丑寅卯辰巳午未申酉戌亥'
    jiazi = [Gan[x % len(Gan)] + Zhi[x % len(Zhi)] for x in range(60)]
    return jiazi

class Taiyi():
    def __init__(self, year, month, day, hour, minute):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.taiyiyear = 10153917
        self.year_num = 365
        self.threeki_year = 284287
        self.jiajishui = 29277
        self.circle = 360 #周
        self.epoch = 60#紀
        self.rounds = 72#局	
        self.yuan = 72#元
        self.jieqi = re.findall('..', '春分清明穀雨立夏小滿芒種夏至小暑大暑立秋處暑白露秋分寒露霜降立冬小雪大雪冬至小寒大寒立春雨水驚蟄')
        self.rujiyuan = (self.taiyiyear + self.year) % 360
        self.ruyuanzhou = self.rujiyuan // 72
        self.ymc = [11,12,1,2,3,4,5,6,7,8,9,10]
        self.num = [8,3,4,9,2,7,6,1]
        self.rmc = list(range(1,32))
        #干支
        self.Gan = '甲乙丙丁戊己庚辛壬癸'
        self.Zhi = '子丑寅卯辰巳午未申酉戌亥'
        #十六神
        self.sixtengod = dict(zip(list("子丑艮寅卯巽辰巳午未坤申酉戌乾亥"), re.findall("..","地主陽德和德呂申高叢太陽大炅大神大威天道大武武德太簇陰主陰德大義")))
        #間辰
        self.jc = list("丑寅辰巳未申戌亥")
        self.jc1 = list("巽艮坤乾")
        self.tyjc = [1,3,7,9]
        #陰陽遁定制
        self.gong = dict(zip(list("子丑艮寅卯辰巽巳午未坤申酉戌乾亥"), range(1,17)))
        self.gong1 = list("子丑艮寅卯辰巽巳午未坤申酉戌乾亥")
        self.gong2 = dict(zip(list("亥子丑艮寅卯辰巽巳午未坤申酉戌乾"), [8,8,3,3,4,4,9,9,2,2,7,7,6,6,1,1]))
        self.yang_sixteen = list("申酉戌乾乾亥子丑艮寅卯辰巽巳午未坤坤")
        self.ying_sixteen = list("寅卯辰巽巽巳午未坤申酉戌乾亥子丑艮艮")
        self.yangji = list("寅丑子亥戌酉申未午巳辰卯")
        self.yingji = list("申未午巳辰卯寅丑子亥戌酉")
        self.ying = {"陰":[4,9,2,7,6,1,8,3], "陽":[1,8,3,4,9,2,7,6]}
        #文昌
        self.skyeyes_dict = {"陽" : list("未坤申酉戌乾乾亥子丑艮寅卯巽辰巳午未坤坤申酉戌乾乾亥子丑艮寅卯巽辰巳午未坤坤申酉戌乾乾亥子丑艮寅卯巽辰巳午未坤坤申酉戌乾乾亥子丑艮寅卯巽辰巳午未"),
        "陰":list("寅卯辰巽巽巳午未坤申酉戌乾亥子丑艮艮寅卯辰巽巽巳午未坤申酉戌乾亥子丑艮艮寅卯辰巽巽巳午未坤申酉戌乾亥子丑艮艮寅卯辰巽巽巳午未坤申酉戌乾亥子丑艮艮")}
        
        #太歲
        self.taishui = self.gangzhi()[3][1]
        #合神
        self.hegod = dict(zip(list("子寅卯辰巳午丑亥戌酉申未"),list("丑亥戌酉申未子寅卯辰巳午"))).get(self.taishui)
        #八門
        self.ed = list("開休生傷杜景死驚")
        self.dz_date = datetime.datetime.strptime(str(self.year)+"/"+str(self.month)+"/"+str(self.day) , '%Y/%m/%d') - datetime.timedelta(days=self.dzdistance())

    def skyeyes(self, ji):
        findplace = {"陽":self.yang_sixteen, "陰":self.ying_sixteen}.get(self.kook(ji)[0])
        findplace_num = dict(zip(findplace, range(1,19)))    
        return dict(zip(range(1,73),self.skyeyes_dict.get(self.kook(ji)[0]))).get(int(self.kook(ji).replace("陰遁", "").replace("陽遁", "").replace("局", "")))

    #計神
    def jigod(self, ji):
        findji = {"陽":self.yangji, "陰":self.yingji}.get(self.kook(ji)[0])
        return dict(zip(self.Zhi, findji )).get(self.taishui)


    def new_list(self, olist, o):
        zhihead_code = olist.index(o)
        res1 = []
        for i in range(len(olist)):
            res1.append( olist[zhihead_code % len(olist)])
            zhihead_code = zhihead_code + 1
        return res1
    #干支
    def gangzhi(self):
        if self.hour == 23:
            d = datetime.datetime.strptime(str(self.year)+"-"+str(self.month)+"-"+str(self.day)+"-"+str(self.hour)+":00:00", "%Y-%m-%d-%H:%M:%S") + datetime.timedelta(hours=1)
        else:
            d = datetime.datetime.strptime(str(self.year)+"-"+str(self.month)+"-"+str(self.day)+"-"+str(self.hour)+":00:00", "%Y-%m-%d-%H:%M:%S") 
        cdate = sxtwl.fromSolar(d.year, d.month, d.day)
        yTG = self.Gan[cdate.getYearGZ().tg] + self.Zhi[cdate.getYearGZ().dz]
        mTG = self.Gan[cdate.getMonthGZ().tg] + self.Zhi[cdate.getMonthGZ().dz]
        dTG  = self.Gan[cdate.getDayGZ().tg] + self.Zhi[cdate.getDayGZ().dz]
        hTG = self.Gan[cdate.getHourGZ(d.hour).tg] + self.Zhi[cdate.getHourGZ(d.hour).dz]
        return [yTG, mTG, dTG, hTG]
    #節氣
    def ecliptic_lon(self, jd_utc):
        s = ephem.Sun(jd_utc)
        return ephem.Ecliptic(ephem.Equatorial(s.ra,s.dec,epoch=jd_utc)).lon
    
    def sta(self, jd):
        return int(self.ecliptic_lon(jd)*180.0/math.pi/15)
    
    def iteration(self, jd):
        s1=self.sta(jd)
        s0=s1
        dt=1.0
        while True:
            jd+=dt
            s=self.sta(jd)
            if s0!=s:
                s0=s
                dt=-dt/2
            if abs(dt)<0.0000001 and s!=s1:
                break
        return jd
    
    def fjqs(self, year, month, day, hour):
        jd = ephem.Date( str(year)+"/"+str(month).zfill(2)+"/"+str(day).zfill(2)+" "+str(hour).zfill(2)+":00:00.00")
        ct = datetime.datetime.strptime(str(year)+"-"+str(month)+"-"+str(day)+"-"+str(hour)+":00:00", "%Y-%m-%d-%H:%M:%S")
        n=int(self.ecliptic_lon(jd)*180.0/math.pi/15)+1
        c = []
        for i in range(1):
            if n>=24:
                n-=24
            jd = self.iteration(jd)
            d = ephem.Date(jd+1/3).tuple()
            b = [self.jieqi[n], datetime.datetime.strptime(str(d[0])+"-"+str(d[1])+"-"+str(d[2])+"-"+str(d[3])+":00:00", "%Y-%m-%d-%H:%M:%S")]
            c.append(b)
        return c[0]

    def find_jq_date(self, year, month, day, hour, jq):
        jd=ephem.Date( str(year)+"/"+str(month).zfill(2)+"/"+str(day).zfill(2)+" "+str(hour).zfill(2)+":00:00.00")
        e=self.ecliptic_lon(jd)
        n=int(e*180.0/math.pi/15)+1
        dzlist = []
        for i in range(24):
            if n>=24:
                n-=24
            jd=self.iteration(jd)
            d=ephem.Date(jd+1/3).tuple()
            d1=ephem.Date(jd+1/3)
            b = {self.jieqi[n]: datetime.datetime(d[0], d[1], d[2],d[3], d[4], int(d[5]))}
            n+=1
            dzlist.append(b)
        return list(dzlist[[list(i.keys())[0] for i in dzlist].index(jq)].values())[0]
    
    def lunar_date_d(self):
        day = sxtwl.fromSolar(self.year, self.month, self.day)
        return {"月": day.getLunarMonth(), "日":day.getLunarDay()}
    
    def dzdistance(self):
        return [self.find_jq_date(self.year, self.month, self.day, self.hour, "冬至") -  datetime.datetime(self.year,self.month, self.day, self.hour, 0,0)][0].days                                                                                  
    
    def xzdistance(self):
        return [self.find_jq_date(self.year, self.month, self.day, self.hour, "夏至") -  datetime.datetime(self.year,self.month, self.day, self.hour, 0,0)][0].days           
            
    def accnum(self, ji):
        if ji == 0: #年計
            if self.year >= 0:
                return self.taiyiyear + self.year 
            elif self.year < 0:
                return self.taiyiyear + self.year + 1 
        elif ji == 1: #月計
            if self.year >= 0:
                accyear = self.taiyiyear + self.year - 1
            elif self.year < 0:
                accyear = self.taiyiyear + self.year + 1 
            return accyear * 12 + 2 + self.month
        elif ji == 2:#日計
            return (datetime.datetime.strptime(
            "{0:04}-{1:02d}-{2:02d} 00:00:00".format(self.year, self.month, self.day),
            "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime("1900-06-19 00:00:00",
                                            "%Y-%m-%d %H:%M:%S")).days
        elif ji == 3: #時計
            return ((datetime.datetime.strptime(
            "{0:04}-{1:02d}-{2:02d} 00:00:00".format(self.year, self.month, self.day),
            "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime("1900-06-19 00:00:00",
                                            "%Y-%m-%d %H:%M:%S")).days - 1 ) * 12 + (self.hour + 1 ) // 2 + 1
    def kook(self, ji):
        dz = self.dzdistance()
        xz = self.xzdistance()
        dz_date = datetime.datetime.strptime(str(self.year)+"/"+str(self.month)+"/"+str(self.day) , '%Y/%m/%d') - datetime.timedelta(days=dz)
        xz_date = datetime.datetime.strptime(str(self.year)+"/"+str(self.month)+"/"+str(self.day) , '%Y/%m/%d') - datetime.timedelta(days=xz)
        current_date = datetime.datetime.strptime(str(self.year)+"/"+str(self.month)+"/"+str(self.day) , '%Y/%m/%d')
        if ji == 0 or ji == 1 or ji ==2:
            dun = "陽遁"
            return dun + str(self.accnum(ji)%72) + "局"
        elif ji == 3:
            if current_date >= xz_date and self.month >= 6:
                dun = "陰遁"
            else:
                dun = "陽遁"
            return dun + str(self.accnum(ji)%72) + "局"
    
    def getyuan(self, ji):
        accnum = self.accnum(ji)
        if round(accnum % self.circle) == 1:
            find_ji_num = 1
        else:
            find_ji_num = int(round((accnum % self.circle) / self.yuan, 0))
        fiveyuen_d = dict(zip(range(1,6), jiazi()[0::12]))
        jiyuan = fiveyuen_d.get(find_ji_num) 
        return jiyuan
    
    def getepoch(self, ji):
        accnum = self.accnum(ji)
        if round(accnum % self.circle) == 1:
            find_ji_num = 1
        else:
            find_ji_num = round((accnum % self.circle) / self.epoch, 0)
        cnum = list("一二三四五六七八九十")
        return "第"+dict(zip(range(1,8), cnum[0:7])).get(find_ji_num)+"紀"
    
    def jiyuan(self, ji):
        return self.getyuan(ji)+ "元" + self.getepoch(ji)
    
    def tdate(self):
        return dict(zip(list("年月日時"), [self.taiyiyear + self.year, 
                        (self.taiyiyear + self.year) * 12 - 10 + self.month,  
                        (self.taiyiyear + self.year) * 12 - 10 + self.month + self.dzdistance() + 1,
                        ((self.taiyiyear + self.year) * 12 - 10 + self.month + self.dzdistance()+ 1) * 12 + math.ceil(self.hour / 2 ) + 1
                        ]))
    def gakook(self):
        ty = self.ty()
        wc = self.gong2.get(self.skyeyes)
        sf = self.gong2.get(self.sf())
        hg = self.gong2.get(self.home_general())
        ag = self.gong2.get(self.away_general())
        hvg = self.gong2.get(self.home_vgen())
        avg = self.gong2.get(self.away_vgen())
        sg = self.gong2.get(self.set_general())
        svg = self.gong2.get(self.set_vgen())
        if ty == wc:
            gk = self.skyeyes + "掩太乙"
        elif ty == sf:
            gk = self.sf() + "掩太乙"
        elif self.num.index(ty) - self.num.index(wc) == 1 or -1 or 7 or -7:
            gk = self.skyeyes + "迫太乙"
        elif self.num.index(ty) - self.num.index(sf) == 1 or -1 or 7 or -7:
            gk = self.sf() + "提挾太乙"
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

    def ty(self, ji):
        arr = np.arange(10) 
        repetitions = 3
        arrangement = np.repeat(arr, repetitions) 
        arrangement_r = list(reversed(arrangement))
        yy_dict = {"陽": dict(zip(range(1,73), list(itertools.chain.from_iterable([list(arrangement)[3:15]+ list(arrangement)[18:]] * 3)))),  "陰": dict(zip(range(1,73), (list(arrangement_r)[:12] + list(arrangement_r)[15:][:-3]) * 3))}
        return yy_dict.get(self.kook(ji)[0]).get(int(self.kook(ji).replace("陰遁", "").replace("陽遁", "").replace("局", "")))   
    
    #始擊
    def sf(self, ji):
        wc = self.skyeyes(ji)
        jd = self.jigod(ji)
        if wc == jd:
            sf = "艮"
            return sf
        elif wc != jd:
            start = self.new_list(self.gong1, jd)
            start1 = len(start[0:start.index("艮")+1])
            start2 = self.new_list(self.gong1, wc)[start1-1]
            return  start2
        
    #定目
    def se(self, ji):
        wc = self.skyeyes(ji)
        hg = self.hegod
        ts = self.taishui
        start = self.new_list(self.gong1, hg)
        start1 = len(start[:start.index(ts)+1])
        start2 = self.new_list(self.gong1, wc)[start1-1]
        return  start2

    def home_cal(self, ji):
        num = self.num
        lnum = [8, 8, 3,  3, 4,4, 9, 9, 2, 2, 7, 7, 6, 6, 1, 1]
        gong = list("亥子丑艮寅卯辰巽巳午未坤申酉戌乾")
        wc = self.skyeyes(ji)
        lg = dict(zip(gong, lnum))
        wc_num = lg.get(wc)
        ty = self.ty(ji)
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
        
    def home_general(self, ji):
        home_g = self.home_cal(ji)  % 10
        if home_g == 0:
            home_g = 5
        return home_g
    
    def home_vgen(self, ji):
        home_vg = self.home_general(ji) *3 % 10
        if home_vg ==0:
            home_vg = 5
        return home_vg
        
    def away_cal(self, ji):
        num = self.num
        lnum = [8, 8, 3,  3, 4,4, 9, 9, 2, 2, 7, 7, 6, 6, 1, 1]
        gong = list("亥子丑艮寅卯辰巽巳午未坤申酉戌乾")
        sf = self.sf(ji)
        lg = dict(zip(gong, lnum))
        sf_num = lg.get(sf)
        ty = self.ty(ji)
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
    
    def away_general(self, ji):
        away_g = self.away_cal(ji)  % 10
        if away_g == 0:
            away_g = 5
        return away_g
    
    def away_vgen(self, ji):
        away_vg = self.away_general(ji) *3 % 10
        if away_vg == 0:
            away_vg = 5
        return away_vg
        
    def set_cal(self, ji):
        num = self.num
        lnum = [8, 8, 3,  3, 4,4, 9, 9, 2, 2, 7, 7, 6, 6, 1, 1]
        gong = list("亥子丑艮寅卯辰巽巳午未坤申酉戌乾")
        se = self.se(ji)
        lg = dict(zip(gong, lnum))
        se_num = lg.get(se)
        ty = self.ty(ji)
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
            return sum(se_order[: se_order.index(ty)])
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
    
    def set_general(self, ji):
        set_g = self.set_cal(ji)  % 10
        if set_g == 0:
            set_g = 5
        return set_g
    
    def set_vgen(self, ji):
        set_vg =  self.set_general(ji) *3 % 10
        if set_vg == 0:
            set_vg = 5
        return set_vg
    
    def sixteen_gong(self, ji):
        dict1 = [{self.skyeyes(ji):"文昌"},{self.taishui:"太歲"},{self.hegod:"合神"},{self.sf(ji):"始擊"},
                 {self.se(ji):"定目"}, {self.kingbase(ji):"君基"}, {self.officerbase(ji):"臣基"}, {self.pplbase(ji):"民基"},
                 {self.fgd(ji):"四神"},{self.skyyi(ji):"天乙"},{self.earthyi(ji):"地乙"},{self.zhifu(ji):"直符"},
                 {self.flyfu(ji):"飛符"},{self.kingfu(ji):"帝符"},{self.taijun(ji):"太尊"}, {self.wufu(ji):"五福"} ]
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

    def nine_gong(self, ji):
        dict1 = [{self.home_general(ji):"主將"},{self.home_vgen(ji):"主參"},{self.away_general(ji):"客將"},
                 {self.away_vgen(ji):"客參"},{self.set_general(ji):"定將"},{self.set_vgen(ji):"定參"},
                 {self.ty(ji):"太乙"}, {self.threewind(ji):"三風"},  {self.fivewind(ji):"五風"},
                 {self.eightwind(ji):"八風"},  {self.flybird(ji):"飛鳥"},{self.bigyo(ji):"大游"},
                 {self.smyo(ji):"小游"},]
        res = {8:"", 3:"", 4:"", 9:"",5:"", 2:"", 7:"", 6:"", 1:""}
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
    def kingbase(self, ji):
        kb = (self.accnum(ji) +250) % 360  / 30
        kb_v = dict(zip(range(1,13), self.new_list(self.Zhi, "午"))).get(int(kb))
        if kb_v == 0 or kb_v ==None:
            kb_v = "中"
        return kb_v
    
    #臣基
    def officerbase(self, ji):
        ob = (self.accnum(ji)  +250) % 360  % 36 / 3
        ob_v =  dict(zip(range(1,13), self.new_list(self.Zhi, "午"))).get(int(ob))
        if ob_v == 0 or ob_v ==None:
            ob_v = "中"
        return ob_v
    #民基
    def pplbase(self, ji):
        pb = (self.accnum(ji)  +250) % 360 % 12
        pb_v = dict(zip(range(1,13), self.new_list(self.Zhi, "戌"))).get(int(pb))
        if pb_v == 0 or pb_v ==None:
            pb_v = "中"
        return  pb_v
    #大游
    def bigyo(self, ji):
        by = int((self.accnum(ji) +34) % 388)
        if by < 36:
            by = by
        elif by > 36:
            by = by / 36
        byv = dict(zip([7,8,9,1,2,3,4,6],range(1,9))).get(int(by))
        if byv == 0 or byv ==None:
            byv = 5
        return byv
    #小游
    def smyo(self, ji):
        sy = int(self.accnum(ji)  % 360)
        if sy < 24:
            sy = sy % 3 
        elif sy > 24:
            sy = sy % 24
            if sy > 3:
                sy = sy % 3
        syv = dict(zip([1,2,3,4,6,7,8,9],range(1,9))).get(int(sy))
        if syv == 0 or syv == None:
            syv = 5
        return syv
    #四神
    def fgd(self, ji):
        f = self.accnum(ji)  % 360 % 36 / 3 
        fv = dict(zip(range(1,13), self.new_list(self.Zhi, "亥"))).get(int(f))
        if fv == 0 or fv == None:
            fv = "中"
        return fv
    #天乙
    def skyyi(self, ji):
        f = self.accnum(ji)  % 360 % 36 / 3 
        fv = dict(zip(range(1,13), self.new_list(self.Zhi, "酉"))).get(int(f))
        if fv == 0 or fv == None:
            fv = "中"
        return fv
    #地乙
    def earthyi(self, ji):
        f = self.accnum(ji)  % 360 % 36 / 3
        fv = dict(zip(range(1,13), self.new_list(self.Zhi, "巳"))).get(int(f))
        if fv == 0 or fv == None:
            fv = "中"
        return fv
    #直符
    def zhifu(self, ji):
        f = self.accnum(ji)  % 360 % 36 / 3
        fv = dict(zip(range(1,14), ["中"]+self.new_list(self.Zhi, "酉"))).get(int(f))
        if fv == 0 or fv == None:
            fv = "中"
        return fv
    #飛符
    def flyfu(self, ji):
        f = self.accnum(ji) % 360 % 36 / 3
        fv = dict(zip(range(1,13), self.new_list(self.Zhi, "辰"))).get(int(f))
        if fv == 0 or fv == None:
            fv = "中"
        return fv
    #帝符
    def kingfu(self, ji):
        f = self.accnum(ji)  %20
        if f > 16:
            f = f - 16
        fv = dict(zip(range(1,17), self.new_list(self.gong1, "戌"))).get(int(f))
        if fv == 0 or fv== None:
            fv = "中"
        return fv
    #太尊
    def taijun(self, ji):
        f = self.accnum(ji)   % 4
        fv = dict(zip(range(1,5), list("子午卯酉"))).get(int(f))
        if fv == 0  or fv == None:
            fv = "中"
        return fv
    #飛鳥
    def flybird(self, ji):
        f = self.accnum(ji)   % 9
        fv = dict(zip(range(1,10), [1,8,3,4,9,2,7,6])).get(int(f))
        if fv == 0 or fv ==None:
            fv = 5
        return fv
    #五行
    def wuxing(self, ji):
        f = self.accnum(ji) // 5
        f = f % 5
        fv =  dict(zip(range(1,10), [1,3,5,7,9,2,4,6,8])).get(int(f))
        if fv == 0 or fv ==None:
            fv = 5
        return fv
    #三風
    def threewind(self, ji):
        f = self.accnum(ji)  % 9
        fv = dict(zip(range(1,9), [7,2,6,1,5,9,4,8])).get(int(f))
        if fv == 0 or fv == None:
            fv = 5
        return fv
    #五風
    def fivewind(self, ji):
        f = self.accnum(ji)  % 29
        if f > 10:
            f = f - 9
        fv = dict(zip(range(1,10), [1,3,5,7,9,2,4,6,8])).get(int(f))
        if fv == 0 or fv == None:
            fv = 5
        return fv
    #八風
    def eightwind(self, ji):
        f = self.accnum(ji)  % 9
        fv = dict(zip(range(1,9), [2,3,5,6,7,8,9,1])).get(int(f))
        if fv == 0 or fv == None:
            fv = 5
        return fv
    #五福
    def wufu(self, ji):
        f = int(self.accnum(ji)  + 250) % 225 / 45 
        fv = dict(zip(range(1,6), list("乾艮巽坤中"))).get(int(f))
        if fv == 0 or fv ==None:
            fv = 5
        return fv
    #八門
    def eight_door(self, ji):
        acc = self.accnum(ji) % 120
        if acc == 0:
            acc = 120
        eightdoor_zhishi = acc // 30
        if eightdoor_zhishi % 30 != 0:
           eightdoor_zhishi = eightdoor_zhishi + 1
        if self.kook()[0] == "陽":
            fdoor = [1,8,3,6]
        elif self.kook()[0] == "陰":
            fdoor = [9,2,7,4]
        #ty_gong = self.ty()
        return self.new_list(self.num, fdoor[eightdoor_zhishi]), eightdoor_zhishi
    
    def pan(self, ji):
        return {
                "太乙計":{0:"年計", 1:"月計", 2:"日計", 3:"時計"}.get(ji), 
                "干支":self.gangzhi(),
                "農曆":self.lunar_date_d(),
                "紀元":self.jiyuan(ji),
                "時局":self.kook(ji),
                "太乙":self.ty(ji),
                "文昌":self.skyeyes(ji),
                "太歲":self.taishui,
                "合神":self.hegod,
                "計神":self.jigod(ji),
                "始擊":self.sf(ji),
                "定目":self.se(ji),
                "主算":[self.home_cal(ji), self.cal_des(self.home_cal(ji))],
                "客算":[self.away_cal(ji), self.cal_des(self.away_cal(ji))],
                "定算":[self.set_cal(ji), self.cal_des(self.set_cal(ji))],
                "九宮":self.nine_gong(ji), 
                "十六宮":self.sixteen_gong(ji),
                }
    
   def html(self, ji):
       text = '''<html><body><table border="0" cellpadding="1" cellspacing="1" style="width:500px">
    	<tbody>
    		<tr>
    			<td colspan="5">
    			<p><span style="font-size:large"><strong>'''+str(self.year)+"年"+str(self.month)+"月"+str(self.day)+"日"+str(self.hour)+"時"+'''<br />
    			干支: '''+self.gangzhi()[0]+"  "+self.gangzhi()[1]+"  "+self.gangzhi()[2]+"  "+self.gangzhi()[3]+'''&nbsp;</strong></span></p>
    			<p><span style="font-size:large"><strong>'''+self.jiyuan(ji)+"  "+self.kook(ji)+'''<br />
    			主算:'''+str(self.home_cal(ji))+"".join(self.cal_des(self.home_cal(ji)))+'''<br />
    			客算:'''+str(self.away_cal(ji))+"".join(self.cal_des(self.away_cal(ji)))+'''<br />
    			定算:'''+str(self.set_cal(ji))+"".join(self.cal_des(self.set_cal(ji)))+'''</strong></span></p>
    			</td>
    		</tr>
    		<tr>
    			<td><span style="font-size:large"><strong>巽</strong></span>
    			<table border="0" cellpadding="1" cellspacing="1" style="width:100px">
    				<tbody>'''+"".join(['''<tr><td>'''+i+'''</td></tr>''' for i in self.pan(ji).get("十六宮").get("巽")])+'''</tbody>
    			</table>
    			</td>
    			<td><span style="font-size:large"><strong>巳</strong></span>
    			<table border="0" cellpadding="1" cellspacing="1" style="width:100px">
    				<tbody>'''+"".join(['''<tr><td>'''+i+'''</td></tr>''' for i in self.pan(ji).get("十六宮").get("巳")])+'''</tbody>
    			</table>
    			</td>
    			<td><span style="font-size:large"><strong>午</strong></span>
    			<table border="0" cellpadding="1" cellspacing="1" style="width:100px">
    				<tbody>'''+"".join(['''<tr><td>'''+i+'''</td></tr>''' for i in self.pan(ji).get("十六宮").get("午")])+'''</tbody>
    			</table>
    			</td>
    			<td><span style="font-size:large"><strong>未&nbsp;</strong></span>
    			<table border="0" cellpadding="1" cellspacing="1" style="width:100px">
    				<tbody>'''+"".join(['''<tr><td>'''+i+'''</td></tr>''' for i in self.pan(ji).get("十六宮").get("未")])+'''</tbody>
    			</table>
    			</td>
    			<td><span style="font-size:large"><strong>坤</strong></span>
    			<table border="0" cellpadding="1" cellspacing="1" style="width:100px">
    				<tbody>'''+"".join(['''<tr><td>'''+i+'''</td></tr>''' for i in self.pan(ji).get("十六宮").get("坤")])+'''</tbody>
    			</table>
    			</td>
    		</tr>
    		<tr>
    			<td><span style="font-size:large"><strong>辰</strong></span>
    			<table border="0" cellpadding="1" cellspacing="1" style="width:100px">
    				<tbody>'''+"".join(['''<tr><td>'''+i+'''</td></tr>''' for i in self.pan(ji).get("十六宮").get("辰")])+'''</tbody>
    			</table>
    			</td>
    			<td colspan="3" rowspan="3">&nbsp;</td>
    			<td><span style="font-size:large"><strong>申</strong></span>
    			<table border="0" cellpadding="1" cellspacing="1" style="width:100px">
    				<tbody>'''+"".join(['''<tr><td>'''+i+'''</td></tr>''' for i in self.pan(ji).get("十六宮").get("申")])+'''</tbody>
    			</table>
    			</td>
    		</tr>
    		<tr>
    			<td><span style="font-size:large"><strong>卯</strong></span>
    			<table border="0" cellpadding="1" cellspacing="1" style="width:100px">
    				<tbody>'''+"".join(['''<tr><td>'''+i+'''</td></tr>''' for i in self.pan(ji).get("十六宮").get("卯")])+'''</tbody>
    			</table>
    			</td>
    			<td><span style="font-size:large"><strong>酉</strong></span>
    			<table border="0" cellpadding="1" cellspacing="1" style="width:100px">
    				<tbody>'''+"".join(['''<tr><td>'''+i+'''</td></tr>''' for i in self.pan(ji).get("十六宮").get("酉")])+'''</tbody>
    			</table>
    			</td>
    		</tr>
    		<tr>
    			<td><span style="font-size:large"><strong>寅</strong></span>
    			<table border="0" cellpadding="1" cellspacing="1" style="width:100px">
    				<tbody>'''+"".join(['''<tr><td>'''+i+'''</td></tr>''' for i in self.pan(ji).get("十六宮").get("寅")])+'''</tbody>
    			</table>
    			</td>
    			<td><span style="font-size:large"><strong>戌</strong></span>
    			<table border="0" cellpadding="1" cellspacing="1" style="width:100px">
    				<tbody>'''+"".join(['''<tr><td>'''+i+'''</td></tr>''' for i in self.pan(ji).get("十六宮").get("戌")])+'''</tbody>
    			</table>
    			</td>
    		</tr>
    		<tr>
    			<td><span style="font-size:large"><strong>艮</strong></span>
    			<table border="0" cellpadding="1" cellspacing="1" style="width:100px">
    				<tbody>'''+"".join(['''<tr><td>'''+i+'''</td></tr>''' for i in self.pan(ji).get("十六宮").get("艮")])+'''</tbody>
    			</table>
    			</td>
    			<td><span style="font-size:large"><strong>丑</strong></span>
    				<table border="0" cellpadding="1" cellspacing="1" style="width:100px">
    				<tbody>'''+"".join(['''<tr><td>'''+i+'''</td></tr>''' for i in self.pan(ji).get("十六宮").get("丑")])+'''</tbody>
    			</table>
    			</td>
    			<td><span style="font-size:large"><strong>子</strong></span>
    			<table border="0" cellpadding="1" cellspacing="1" style="width:100px">
    				<tbody>'''+"".join(['''<tr><td>'''+i+'''</td></tr>''' for i in self.pan(ji).get("十六宮").get("子")])+'''</tbody>
    			</table>
    			</td>
    			<td><span style="font-size:large"><strong>亥</strong></span>
    			<table border="0" cellpadding="1" cellspacing="1" style="width:100px">
    				<tbody>'''+"".join(['''<tr><td>'''+i+'''</td></tr>''' for i in self.pan(ji).get("十六宮").get("亥")])+'''</tbody>
    			</table>
    			</td>
    			<td><span style="font-size:large"><strong>乾</strong></span>
    			<table border="0" cellpadding="1" cellspacing="1" style="width:100px">
    				<tbody>'''+"".join(['''<tr><td>'''+i+'''</td></tr>''' for i in self.pan(ji).get("十六宮").get("乾")])+'''</tbody>
    			</table>
    			</td>
    		</tr>
    	</tbody>
    </table>
    
    <p>&nbsp;</p></body></html>

         ''' 
        return text



if __name__ == '__main__':
    tic = time.perf_counter()
    print(Taiyi(2022,8,27,18,14).pan(3))
    toc = time.perf_counter()
    print(f"{toc - tic:0.4f} seconds")
    
#太乙有阴阳遁局，年、月、日用阳遁；时则采用阴遁、阳遁，冬至后阳遁局，夏至后用阴遁局。
