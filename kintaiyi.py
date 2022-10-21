# -*- coding: utf-8 -*-
"""
Created on Sat Aug 27 18:11:44 2022
@author: kentang
"""

import re, itertools, time, pickle, os
import numpy as np
from math import pi
from sxtwl import fromSolar
from ephem import Sun, Date, Ecliptic, Equatorial, hour
from cn2an import an2cn
from itertools import cycle, repeat
from taiyidict import tengan_shiji, su_dist

def jiazi():
    Gan, Zhi = '甲乙丙丁戊己庚辛壬癸','子丑寅卯辰巳午未申酉戌亥'
    return list(map(lambda x: "{}{}".format(Gan[x % len(Gan)],Zhi[x % len(Zhi)]), list(range(60))))

class Taiyi():
    def __init__(self, year, month, day, hour, minute):
        self.year, self.month, self.day, self.hour, self.minute = year, month, day, hour, minute
        self.taiyiyear  = 10153917
        self.jieqi = re.findall('..', '春分清明穀雨立夏小滿芒種夏至小暑大暑立秋處暑白露秋分寒露霜降立冬小雪大雪冬至小寒大寒立春雨水驚蟄')
        self.num =  [8,3,4,9,2,7,6,1]
        self.su = list('角亢氐房心尾箕斗牛女虛危室壁奎婁胃昴畢觜參井鬼柳星張翼軫')
        #干支
        self.Gan,self.Zhi = '甲乙丙丁戊己庚辛壬癸', '子丑寅卯辰巳午未申酉戌亥'
        #間辰
        self.jc = list("丑寅辰巳未申戌亥")
        self.door = list("開休生傷杜景死驚")
        self.jc1 = list("巽艮坤乾")
        self.tyjc = [1,3,7,9]
        #十六神
        self.sixteengod = dict(zip(re.findall("..", "地主陽德和德呂申高叢太陽大炅大神大威天道大武武德太簇陰主陰德大義"), "子丑艮寅卯辰巽巳午未坤申酉戌乾亥"))
        #陰陽遁定制
        self.gong = dict(zip(list("子丑艮寅卯辰巽巳午未坤申酉戌乾亥"), range(1,17)))
        self.gong1 = list("子丑艮寅卯辰巽巳午未坤申酉戌乾亥")
        #self.gong2 = dict(zip(list("亥子丑艮寅卯辰巽巳午未坤申酉戌乾"), [8,8,3,3,4,4,9,9,2,2,7,7,6,6,1,1]))
  
    #計神
    def jigod(self, ji):
        return dict(zip(self.Zhi, self.new_list(list(reversed(self.Zhi)), "寅"))).get(self.taishui(ji))
        
    #太歲
    def taishui(self, ji):
        gz =  self.gangzhi()
        return {0: gz[0][1], 1:gz[1][1], 2:gz[2][1], 3:gz[3][1], 4:gz[4][1]}.get(ji)

    def kingyear(self):
        def closest(lst, K): 
            return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-K))] 
        data = pickle.load(open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'history.pkl'), "rb")).split(",")
        y =  list(map(lambda x: int(x), data[0::7]))
        period = data[3::7]
        king = data[4::7]
        king_realname = data[5::7]
        preiodname = data[6::7]
        idx = y.index(closest(y, self.lunar_date_d().get("年")))
        year = year = self.lunar_date_d().get("年")

        if year < 1900:
            year = year - y[idx] +1 
            if year == 1:
                cyear = "元"
            else:
                cyear = an2cn(year)
            pn = "{}{}年".format(preiodname[idx],cyear)
            kn = "{}{}{}".format(period[idx], king[idx], king_realname[idx])
            return  "{} {}".format(kn, pn)
        elif year >= 1900 and year <1949:
            year = year - y[idx-1] +1
            pn = "{}{}年".format(preiodname[idx-1], an2cn(year))
            kn = "{}{}{}".format(period[idx-1], king[idx-1], king_realname[idx-1])
            return  "{} {}".format(kn, pn)
        elif year >= 1949:
            year = year - y[idx]
            pn = "{}{}年".format(preiodname[idx], an2cn(year))
            kn = "{}{}{}".format(period[idx], king[idx], king_realname[idx])
            return  "{} {}".format(kn, pn)
 
    def skyeyes_des(self, ji):
        yy = self.kook(ji).get("文")[0]
        k = self.kook(ji).get("數")
        dd = {"陽":",,辰迫,,,,,辰迫,囚,辰迫,囚,辰迫,,,勝,辰迫,囚,囚,客挾,,,,,,,,,,,,,,,,,,,客挾,囚,辰迫,客挾,客挾,囚,,宮迫,,主挾，宮迫,辰迫,,,,主挾，辰迫,宮迫,宮迫,,,,,客挾,,,,,,主挾,,,,,,,".split(","),
              "陰":",辰迫,,,,,,辰迫,囚,辰迫,囚,辰迫,,,,辰迫,囚,囚,,關客,,關客,,,宮迫,,,,,,,,,,,,辰迫,囚,,,,,囚,辰迫,宮迫,,宮迫,辰迫,,,,辰擊,宮迫,辰迫,,,,,,,,,,,,,客目掩,,,,,".split(",")}
        return dict(zip(range(1,73), dd.get(yy))).get(k)
    
    def skyeyes(self, ji):   
        skyeyes_dict = {
            "陽" : list("申酉戌乾乾亥子丑艮寅卯辰巽巳午未坤坤申酉戌乾乾亥子丑艮寅卯辰巽巳午未坤坤申酉戌乾乾亥子丑艮寅卯辰巽巳午未坤坤申酉戌乾乾亥子丑艮寅卯辰巽巳午未坤坤"),
            "陰" : list("寅卯辰巽巽巳午未坤申酉戌乾亥子丑艮艮寅卯辰巽巽巳午未坤申酉戌乾亥子丑艮艮寅卯辰巽巽巳午未坤申酉戌乾亥子丑艮艮寅卯辰巽巽巳午未坤申酉戌乾亥子丑艮艮")}
        return dict(zip(range(1,73),skyeyes_dict.get(self.kook(ji).get("文")[0]))).get(int(self.kook(ji).get("數")))
            
    #合神
    def hegod(self, ji):
        #findji = {"陽":list("寅丑子亥戌酉申未午巳辰卯"), "陰":list("申未午巳辰卯寅丑子亥戌酉")}.get(self.kook(ji).get("文")[0])
        #return dict(zip(self.Zhi, findji )).get(self.taishui(ji))
        return dict(zip(self.Zhi, self.new_list(list(reversed(self.Zhi)), "丑"))).get(self.taishui(ji))

    def new_list(self, olist, o):
        a = olist.index(o)
        res1 = []
        for i in range(len(olist)):
            res1.append( olist[a % len(olist)])
            a = a + 1
        return res1
    
    def repeat_list(self, n, thelist):
        return [repetition for i in thelist for repetition in repeat(i,n) ]
    
    def multi_key_dict_get(self, d, k):
        for keys, v in d.items():
            if k in keys:
                return v
        return None
    
    def Ganzhiwuxing(self, gangorzhi):
        ganzhiwuxing = dict(zip(list(map(lambda x: tuple(x),"甲寅乙卯巽,丙巳丁午,壬亥癸子,庚申辛酉乾,未丑戊己未辰戌坤艮".split(","))), list("木火水金土")))
        return self.multi_key_dict_get(ganzhiwuxing, gangorzhi)
    
     #分干支
    def minutes_jiazi_d(self):
        t = []
        for h in range(0,24):
            for m in range(0,60):
                b = str(h)+":"+str(m)
                t.append(b)
        minutelist = dict(zip(t, cycle(self.repeat_list(2, jiazi()))))
        return minutelist
    #干支
    def gangzhi(self):
        if self.hour == 23:
            d = Date(round((Date("{}/{}/{} {}:00:00.00".format(str(self.year).zfill(4), str(self.month).zfill(2), str(self.day).zfill(2), str(self.hour).zfill(2))) + 1 * hour), 3))
        else:
            d = Date("{}/{}/{} {}:00:00.00".format(str(self.year).zfill(4), str(self.month).zfill(2), str(self.day).zfill(2), str(self.hour).zfill(2) ))
        dd = list(d.tuple())
        cdate = fromSolar(dd[0], dd[1], dd[2])
        yTG,mTG,dTG,hTG = "{}{}".format(self.Gan[cdate.getYearGZ().tg], self.Zhi[cdate.getYearGZ().dz]), "{}{}".format(self.Gan[cdate.getMonthGZ().tg],self.Zhi[cdate.getMonthGZ().dz]), "{}{}".format(self.Gan[cdate.getDayGZ().tg], self.Zhi[cdate.getDayGZ().dz]), "{}{}".format(self.Gan[cdate.getHourGZ(dd[3]).tg], self.Zhi[cdate.getHourGZ(dd[3]).dz])
        gangzhi_minute = self.minutes_jiazi_d().get(str(self.hour)+":"+str(self.minute))
        return [yTG, mTG, dTG, hTG, gangzhi_minute]

#%% #節氣
    def ecliptic_lon(self, jd_utc):
        return Ecliptic(Equatorial(Sun(jd_utc).ra,Sun(jd_utc).dec,epoch=jd_utc)).lon
    
    def sta(self, jd):
        return int(self.ecliptic_lon(jd)*180.0/pi/15)
    
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
    
    def find_jq_date(self, year, month, day, hour, jq):
        jd=Date("{}/{}/{} {}:00:00.00".format(str(year).zfill(4), str(month).zfill(2), str(day).zfill(2), str(hour).zfill(2) ))
        e=self.ecliptic_lon(jd)
        n=int(e*180.0/pi/15)+1
        dzlist = []
        for i in range(24):
            if n>=24:
                n-=24
            jd=self.iteration(jd)
            d=Date(jd+1/3).tuple()
            b = {self.jieqi[n]: Date("{}/{}/{} {}:{}:00.00".format(str(d[0]).zfill(4), str(d[1]).zfill(2), str(d[2]).zfill(2), str(d[3]).zfill(2) , str(d[4]).zfill(2)))}
            n+=1
            dzlist.append(b)
        return list(dzlist[list(map(lambda i:list(i.keys())[0], dzlist)).index(jq)].values())[0]
    
    def lunar_date_d(self):
        day = fromSolar(self.year, self.month, self.day)
        return {"年":day.getLunarYear(),  "月": day.getLunarMonth(), "日":day.getLunarDay()}
    
    def xzdistance(self):
        return int(self.find_jq_date(self.year, self.month, self.day, self.hour, "夏至") -  Date("{}/{}/{} {}:00:00.00".format(str(self.year).zfill(4), str(self.month).zfill(2), str(self.day).zfill(2), str(self.hour).zfill(2))))

    def distancejq(self, jq):
        return int( Date("{}/{}/{} {}:00:00.00".format(str(self.year).zfill(4), str(self.month).zfill(2), str(self.day).zfill(2), str(self.hour).zfill(2))) - self.find_jq_date(self.year-1, self.month, self.day, self.hour, jq) )
      
    def fjqs(self, year, month, day, hour):
        jd = Date("{}/{}/{} {}:00:00.00".format(str(year).zfill(4), str(month).zfill(2), str(day).zfill(2), str(hour).zfill(2) ))
        n= int(self.ecliptic_lon(jd)*180.0/pi/15)+1
        c = []
        for i in range(1):
            if n>=24:
                n-=24
            jd = self.iteration(jd)
            d = Date(jd+1/3).tuple()
            c.append([self.jieqi[n], Date("{}/{}/{} {}:{}:00.00".format(str(d[0]).zfill(4), str(d[1]).zfill(2), str(d[2]).zfill(2), str(d[3]).zfill(2) , str(d[4]).zfill(2)))])
        return c[0]
    
    def jq(self, year, month, day, hour):
        ct =  Date("{}/{}/{} {}:00:00.00".format(str(year).zfill(4), str(month).zfill(2), str(day).zfill(2), str(hour).zfill(2) ))
        p = Date(round((ct - 7 ), 3)).tuple()
        pp = Date(round((ct - 21 ), 3)).tuple()
        bf = self.fjqs(p[0], p[1], p[2], p[3])
        bbf = self.fjqs(pp[0], pp[1], pp[2], pp[3])
        if ct < bf[1]:
            return bbf[0]
        else:
            return bf[0]
    
#%% 積年
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
            return accyear * 12 + 2 + self.lunar_date_d().get("月")
        elif ji == 2:#日計
            return int(Date("{}/{}/{} {}:00:00.00".format(str(self.year).zfill(4), str(self.month).zfill(2), str(self.day).zfill(2), str(self.hour).zfill(2))) - Date("1900/06/19 00:00:00.00")) 
            #return (datetime.strptime("{0:04}-{1:02d}-{2:02d} 00:00:00".format(self.year, self.month, self.day), "%Y-%m-%d %H:%M:%S") - datetime.strptime("1900-06-19 00:00:00","%Y-%m-%d %H:%M:%S")).days
        elif ji == 3: #時計
            if self.hour == 0:
                return (int((Date("{}/{}/{} {}:00:00.00".format(str(self.year).zfill(4), str(self.month).zfill(2), str(self.day).zfill(2), str(self.hour).zfill(2))) - Date("1900/06/19 00:00:00.00") - 1)) * 12 + (self.hour + 1 ) // 2 + 1) + 12
            else:
                return int((Date("{}/{}/{} {}:00:00.00".format(str(self.year).zfill(4), str(self.month).zfill(2), str(self.day).zfill(2), str(self.hour).zfill(2))) - Date("1900/06/19 00:00:00.00") - 1)) * 12 + (self.hour + 1 ) // 2 + 1 
            #return ((datetime.strptime("{0:04}-{1:02d}-{2:02d} 00:00:00".format(self.year, self.month, self.day), "%Y-%m-%d %H:%M:%S") - datetime.strptime("1900-06-19 00:00:00","%Y-%m-%d %H:%M:%S")).days - 1 ) * 12 + (self.hour + 1 ) // 2 + 1
        elif ji == 4: #分計
            return int((Date("{}/{}/{} {}:00:00.00".format(str(self.year).zfill(4), str(self.month).zfill(2), str(self.day).zfill(2), str(self.hour).zfill(2))) - Date("1900/06/19 00:00:00.00") - 1)) * 120 + (self.minute + 1 ) // 2 + 1 
            #return ((datetime.strptime("{0:04}-{1:02d}-{2:02d} 00:00:00".format(self.year, self.month, self.day), "%Y-%m-%d %H:%M:%S") - datetime.strptime("1900-06-19 00:00:00","%Y-%m-%d %H:%M:%S")).days - 1 ) * 12 + (self.hour + 1 ) // 2 + 1
     
    
    def kook(self, ji):
        xz = self.xzdistance()
        current_date =  Date("{}/{}/{} {}:00:00.00".format(str(self.year).zfill(4), str(self.month).zfill(2), str(self.day).zfill(2), str(self.hour).zfill(2)))
        xz_date =  current_date - xz
        k = self.accnum(ji)%72
        if k == 0:
            k = 72
        if ji == 0 or ji == 1 or ji ==2:
            dun = "陽遁"
        elif ji == 3 or ji == 4:
            if current_date >= xz_date and self.month >= 6:
                dun = "陰遁"
            else:
                dun = "陽遁"
        return {"文":"{}{}局".format(dun, an2cn(k)), "數":k}
    
    def getyuan(self, ji):
        accnum = self.accnum(ji)
        if round(accnum % 360) == 1:
            find_ji_num = 1
        else:
            find_ji_num = int(round((accnum % 360) / 72, 0))
        fiveyuen_d = dict(zip(range(1,6), jiazi()[0::12]))
        if find_ji_num == 0:
            find_ji_num = 1
        jiyuan = fiveyuen_d.get(find_ji_num) 
        return jiyuan
    
    def getepoch(self, ji):
        accnum = self.accnum(ji)
        if ji == 0 or ji == 1 or ji ==2:
            if round(accnum % 360) == 1:
                find_ji_num = 1
            else:
                find_ji_num = int((accnum % 360) / 60)
            if find_ji_num == 0:
                find_ji_num = 1
            find_ji_num2 = int(accnum % 360 % 72 % 24 / 3)
            if find_ji_num2 == 0:
                find_ji_num2 = 1
            cnum = list("一二三四五六七八九十")
            return {"元":dict(zip(range(1,8), cnum[0:7])).get(find_ji_num), "紀":dict(zip(range(1,8), cnum[0:7])).get(find_ji_num2)}
        elif ji == 3:
            epochdict = dict(zip([
                        ('甲子', '甲午', '乙丑', '乙未', '丙寅', '丙申', '丁卯', '丁酉', '戊辰', '戊戌'), 
                        ('己巳', '己亥', '庚午', '庚子', '辛未', '辛丑', '壬申', '壬寅', '癸酉', '癸卯'),
                        ('甲戌', '甲辰', '乙亥', '乙巳', '丙子', '丙午', '丁丑', '丁未', '戊寅', '戊申'),
                        ('己卯', '己酉', '庚辰', '庚戌', '辛巳', '辛亥', '壬午', '壬子', '癸未', '癸丑'),
                        ('甲申', '甲寅', '乙酉', '乙卯', '丙戌', '丙辰', '丁亥', '丁巳', '戊子', '戊午'),
                        ('己丑', '己未', '庚寅', '庚申', '辛卯', '辛酉', '壬辰', '壬戌', '癸巳', '癸亥')], 
                                 list("一二三四五六")))
            return "第{}紀".format(self.multi_key_dict_get(epochdict, self.gangzhi()[2]))
        elif ji == 4:
            epochdict = dict(zip([
                        ('甲子', '甲午', '乙丑', '乙未', '丙寅', '丙申', '丁卯', '丁酉', '戊辰', '戊戌'), 
                        ('己巳', '己亥', '庚午', '庚子', '辛未', '辛丑', '壬申', '壬寅', '癸酉', '癸卯'),
                        ('甲戌', '甲辰', '乙亥', '乙巳', '丙子', '丙午', '丁丑', '丁未', '戊寅', '戊申'),
                        ('己卯', '己酉', '庚辰', '庚戌', '辛巳', '辛亥', '壬午', '壬子', '癸未', '癸丑'),
                        ('甲申', '甲寅', '乙酉', '乙卯', '丙戌', '丙辰', '丁亥', '丁巳', '戊子', '戊午'),
                        ('己丑', '己未', '庚寅', '庚申', '辛卯', '辛酉', '壬辰', '壬戌', '癸巳', '癸亥')], 
                                 list("一二三四五六")))
            return "第{}紀".format(self.multi_key_dict_get(epochdict, self.gangzhi()[3]))
    
    
    def jiyuan(self, ji):
        if ji == 3:
            j = dict(zip([('甲子', '甲午', '乙丑', '乙未', '丙寅', '丙申', '丁卯', '丁酉', '戊辰', '戊戌', '己巳', '己亥'), 
                                  ('庚午', '庚子', '辛未', '辛丑', '壬申', '壬寅', '癸酉', '癸卯', '甲戌', '甲辰', '乙亥', '乙巳'),
                                  ('丙子', '丙午', '丁丑', '丁未', '戊寅', '戊申', '己卯', '己酉', '庚辰', '庚戌', '辛巳', '辛亥'),
                                  ('壬午', '壬子', '癸未', '癸丑', '甲申', '甲寅', '乙酉', '乙卯', '丙戌', '丙辰', '丁亥', '丁巳'),
                                  ('戊子', '戊午', '己丑', '己未', '庚寅', '庚申', '辛卯', '辛酉', '壬辰', '壬戌', '癸巳', '癸亥')], "甲子,丙子,戊子,庚子,壬子".split(",")))
            
            return "{}{}元".format(self.getepoch(ji), self.multi_key_dict_get(j, self.gangzhi()[2]))
        elif ji == 4:
            j = dict(zip([('甲子', '甲午', '乙丑', '乙未', '丙寅', '丙申', '丁卯', '丁酉', '戊辰', '戊戌', '己巳', '己亥'), 
                                  ('庚午', '庚子', '辛未', '辛丑', '壬申', '壬寅', '癸酉', '癸卯', '甲戌', '甲辰', '乙亥', '乙巳'),
                                  ('丙子', '丙午', '丁丑', '丁未', '戊寅', '戊申', '己卯', '己酉', '庚辰', '庚戌', '辛巳', '辛亥'),
                                  ('壬午', '壬子', '癸未', '癸丑', '甲申', '甲寅', '乙酉', '乙卯', '丙戌', '丙辰', '丁亥', '丁巳'),
                                  ('戊子', '戊午', '己丑', '己未', '庚寅', '庚申', '辛卯', '辛酉', '壬辰', '壬戌', '癸巳', '癸亥')], "甲子,丙子,戊子,庚子,壬子".split(",")))
            
            return "{}{}元".format(self.getepoch(ji), self.multi_key_dict_get(j, self.gangzhi()[3]))
        else:
            return "第{}紀第{}{}元".format(self.getepoch(ji).get("紀") ,self.getepoch(ji).get("元"), self.getyuan(ji))
       
    def ty(self, ji):
        arr = np.arange(10) 
        repetitions = 3
        arrangement = np.repeat(arr, repetitions) 
        arrangement_r = list(reversed(arrangement))
        yy_dict = {"陽": dict(zip(range(1,73), list(itertools.chain.from_iterable([list(arrangement)[3:15]+ list(arrangement)[18:]] * 3)))),  "陰": dict(zip(range(1,73), (list(arrangement_r)[:12] + list(arrangement_r)[15:][:-3]) * 3))}
        return yy_dict.get(self.kook(ji).get("文")[0]).get(self.kook(ji).get("數"))  
    
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
    
    def sf_num(self, ji):
        sf = self.sf(ji)
        sf_z = dict(zip(self.gong, list(range(1,17)))).get(sf)
        sf_su = dict(zip(list("子丑艮寅卯辰巽巳午未坤申酉戌乾亥"), list("虛斗牛尾房亢角翼星鬼井參昴婁奎室"))).get(sf) 
        sf_rank = dict(zip(self.su,list(range(1,29)))).get(sf_su)
        yc_num = dict(zip(self.su,list(range(1,29)))).get(self.year_chin())
        total = yc_num + sf_z +1
        if total > 28:
           a = dict(zip(list(range(1,29)),self.new_list(self.su, sf_su))).get(28)
           return self.new_list(self.su, a)[total - 28 -1]
        else:
           return dict(zip(list(range(1,29)),self.new_list(self.su, sf_su))).get(total)
        

    #定目
    def se(self, ji):
        wc,hg,ts = self.skyeyes(ji),self.hegod(ji),self.taishui(ji)
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
        wc_jc = list(map(lambda x: x == wc, self.jc)).count(True)
        ty_jc = list(map(lambda x: x == ty, self.tyjc)).count(True)
        wc_jc1  = list(map(lambda x: x == wc, self.jc1)).count(True)
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
            return sum(wc_order[: wc_order.index(ty)])+1
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
        sf_jc = list(map(lambda x: x == sf, self.jc)).count(True)
        ty_jc = list(map(lambda x: x == ty, self.tyjc)).count(True)
        sf_jc1 = list(map(lambda x: x == sf, self.jc1)).count(True)
        sf_order = self.new_list(num, sf_num)
        if sf_jc == 1 and ty_jc != 1 and sf_jc1 !=1 :
            return sum(sf_order[: sf_order.index(ty)])+1
        elif sf_jc !=1 and ty_jc != 1 and sf_jc1 ==1:
            return sum(sf_order[: sf_order.index(ty)])
        elif sf_jc != 1 and ty_jc ==1 and sf_jc1 !=1:
            return sum(sf_order[: sf_order.index(ty)]) 
        elif sf_jc ==1 and ty_jc ==1 and sf_jc1 !=1 :
            return sum(sf_order[: sf_order.index(ty)])+1
        elif sf_jc !=1 and ty_jc ==1 and sf_jc1 ==1 :
            if sum(sf_order[: sf_order.index(ty)]) == 0:
                return ty
            else:
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
    
    def shensha(self, ji):
        if ji == 3:
           tz = "登明,河魁,從魁,傳送,小吉,勝光,太乙,天罡,太衝,功曹,大吉,神後".split(",")
           Zhi = list('子丑寅卯辰巳午未申酉戌亥')
           ztz = dict(zip(tz, list(reversed(Zhi))))
           zm = {tuple(list("卯辰巳午未申")):"朝", tuple(list("酉戌亥子丑寅")):"暮"}
           gzzm ={"甲":{"朝":"小吉", "暮":"大吉"}, 
                    tuple(list("戊庚")): {"朝":"大吉", "暮":"小吉"},
                   "己":{"朝":"神后", "暮":"傳送"}, "乙":{"朝":"傳送", "暮":"神后"}, 
                   "丁":{"朝":"登明", "暮":"從魁"}, "丙":{"朝":"從魁", "暮":"登明"}, 
                   "癸":{"朝":"太乙", "暮":"太衝"}, "壬":{"朝":"太衝", "暮":"太乙"}, 
                   "辛":{"朝":"功曹", "暮":"勝光"}}
           general = "天乙,螣蛇,朱雀,六合,勾陳,青龍,天空,白虎,太常,玄武,太陰,天后".split(",")
           tianyi = ztz.get(self.multi_key_dict_get(gzzm, self.gangzhi()[2][0]).get( self.multi_key_dict_get(zm, self.gangzhi()[3][1]) ))
           return dict(zip(self.new_list(self.Zhi,tianyi),general))
        else:
           return "None"
        
    def set_cal(self, ji):
        num = self.num
        lnum = [8, 8, 3,  3, 4,4, 9, 9, 2, 2, 7, 7, 6, 6, 1, 1]
        gong = list("亥子丑艮寅卯辰巽巳午未坤申酉戌乾")
        se = self.se(ji)
        lg = dict(zip(gong, lnum))
        se_num = lg.get(se)
        ty = self.ty(ji)
        se_jc = list(map(lambda x: x == se, self.jc)).count(True)
        ty_jc = list(map(lambda x: x == ty, self.tyjc)).count(True)
        se_jc1 = list(map(lambda x: x == se, self.jc1)).count(True)
        se_order = self.new_list(num, se_num)
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
            t.append("無天")
        if num % 10 < 5:
            t.append("無地")
        if num % 10 == 0:
            t.append("無人")
        numdict = {1: "雜陰", 2: "純陰", 3: "純陽", 4: "雜陽", 6: "純陰", 7: "雜陰",
                   8: "雜陽", 9: "純陽", 11: "陰中重陽", 12: "下和", 13: "雜重陽", 
                   14: "上和", 16: "下和", 17: "陰中重陽", 18: "上和", 19: "雜重陽",
                   22: "純陰", 23: "次和", 24: "雜重陰", 26: "純陰", 27: "下和", 
                   28: "雜重陰", 29: "次和", 31: "雜重陽", 32: "次和", 33: "純陽", 
                   34: "下和", 37: "雜重陽", 38: "下和", 39: "純陽"}
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
    
    def sixteen_gong1(self, ji):
        dict1 = [{self.skyeyes(ji):"昌"},{self.hegod(ji):"合"},{self.sf(ji):"始"},
                {self.se(ji):"目"}, {self.kingbase(ji):"君"}, {self.officerbase(ji):"臣"}, {self.pplbase(ji):"民"},
                {self.fgd(ji):"四"},{self.skyyi(ji):"乙"},{self.earthyi(ji):"地"},{self.zhifu(ji):"符"},
                {self.flyfu(ji):"飛"},{self.kingfu(ji):"帝"}, {self.wufu(ji):"福"},  {self.jigod(ji):"計"}]
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
    
    def sixteen_gong(self, ji):
        dict1 = [{self.skyeyes(ji):"文昌"},{self.taishui(ji):"太歲"},{self.hegod(ji):"合神"},{self.sf(ji):"始擊"},
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
    #九宮
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
    
    #太歲禽星
    def year_chin(self):
        chin_28_stars_code = dict(zip(range(1,29), self.su))
        if self.lunar_date_d().get("月") == "十二月" or self.lunar_date_d().get("月") == "十一月":
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
        elif self.lunar_date_d().get("月") != "十二月" or self.lunar_date_d().get("月") == "十一月":
            get_year_chin_number = (int(self.year)+15) % 28 #求年禽之公式為西元年加15除28之餘數
            if get_year_chin_number == int(0):
                get_year_chin_number = int(28)
            year_chin = chin_28_stars_code.get(get_year_chin_number) #年禽
        return year_chin
    
    
    #君基
    def kingbase(self, ji):
        kb = (self.accnum(ji) +250) % 360  / 30
        kb_v = dict(zip(range(1,13), self.new_list(self.Zhi, "午"))).get(int(kb))
        if kb_v == 0 or kb_v ==None:
            kb_v = "中"
        return kb_v
    
    #臣基
    def officerbase(self, ji):
        return dict(zip(range(1,73), cycle(list("巳巳午午午未未未申申酉酉戌戌戌亥亥亥子子子丑丑寅寅寅卯卯卯辰辰辰巳")))).get(self.kook(ji).get("數"))
    #民基
    def pplbase(self, ji):
        return dict(zip(range(1,73), cycle(self.new_list(self.Zhi,"申")))).get(self.kook(ji).get("數"))
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
        return dict(zip(range(1,73), cycle(list("乾乾乾離離離艮艮艮震震震中中中兌兌兌坤坤坤坎坎坎巽巽巽巳巳巳申申申寅寅寅")))).get(self.kook(ji).get("數"))
    #天乙
    def skyyi(self, ji):
        return dict(zip(range(1,73), cycle(list("兌兌兌坤坤坤坎坎坎巽巽巽巳巳巳申申申寅寅寅乾乾乾離離離艮艮艮震震震中中中")))).get(self.kook(ji).get("數"))   
    #地乙
    def earthyi(self, ji):
        return dict(zip(range(1,73), cycle(list("巽巽巽巳巳巳申申申寅寅寅乾乾乾離離離艮艮艮震震震中中中兌兌兌坤坤坤坎坎坎")))).get(self.kook(ji).get("數"))
    #直符
    def zhifu(self, ji):
        return dict(zip(range(1,73), cycle(list("中中中兌兌兌坤坤坤坎坎坎巽巽巽巳巳巳申申申寅寅寅乾乾乾離離離艮艮艮震震震")))).get(self.kook(ji).get("數"))
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
        acc = self.accnum(ji) % 240
        if acc == 0:
            acc = 120
        eightdoor_zhishi = acc // 30
        if eightdoor_zhishi % 30 != 0:
           eightdoor_zhishi = eightdoor_zhishi + 1
        elif eightdoor_zhishi == 0:
            eightdoor_zhishi = 1
        
        #ty_gong = self.ty()
        return dict(zip(list(range(1,9)),self.door)).get(eightdoor_zhishi)
   
    def starhouse(self):
        numlist = [13,9,16,5,5,17,10,24,7,11,25,18,17,10,17,13,14,11,16,1,9,30,3,14,7,19,19,18]
        alljq = self.jieqi
        njq = self.new_list(alljq, "冬至")
        gensulist =  list(itertools.chain.from_iterable([[self.su[i]]*numlist[i] for i in range(0,28)]))
        jqsulist = [["斗", 9],["斗",24] ,["女", 8],["危",2],["室", 1],["壁",1] ,["奎", 4],["婁",2] ,["胃", 4],["昴",4] ,["畢", 8],["參",6] ,["井", 1],["井", 27],["柳",8] ,["張", 3],["翼",1] ,["翼", 16],["軫",13] ,["角", 9],["房", 1],["氐",2] ,["尾", 6],["箕",24]]
        njq_list = dict(zip(njq, jqsulist))
        currentjq = self.jq(self.year, self.month, self.day, self.hour)
        distance_to_cjq = self.distancejq(currentjq)
        return gensulist[gensulist.index(   njq_list.get(currentjq)[0]  )+  njq_list.get(currentjq)[1]  + distance_to_cjq]
    
    def pan(self, ji):
        return {
                "太乙計":{0:"年計", 1:"月計", 2:"日計", 3:"時計", 4:"分計"}.get(ji), 
                "公元日期":"{}年{}月{}日{}時".format(self.year, self.month, self.day, self.hour),
                "干支":self.gangzhi(),
                "農曆":self.lunar_date_d(),
                "年號":self.kingyear(),
                "紀元":self.jiyuan(ji),
                "太歲":self.taishui(ji),
                "局式":self.kook(ji),
                "二十八宿值日":self.starhouse(),
                "太歲二十八宿":self.year_chin(),
                "太歲值宿斷事": su_dist.get(self.year_chin()),
                "始擊二十八宿":self.sf_num(ji),
                "始擊值宿斷事":su_dist.get(self.sf_num(ji)),
                "八門值事":self.eight_door(ji),
                "太乙":self.ty(ji),
                "文昌":[self.skyeyes(ji), self.skyeyes_des(ji)],
                "主算":[self.home_cal(ji), self.cal_des(self.home_cal(ji))],
                "客算":[self.away_cal(ji), self.cal_des(self.away_cal(ji))],
                "定算":[self.set_cal(ji), self.cal_des(self.set_cal(ji))],
                "合神":self.hegod(ji),
                "計神":self.jigod(ji),
                "始擊":self.sf(ji),
                "定目":self.se(ji),
                "四神":self.fgd(ji),
                "直符":self.zhifu(ji),
                "君基":self.kingbase(ji),
                "臣基":self.officerbase(ji),
                "民基":self.pplbase(ji),
                "九宮":self.nine_gong(ji), 
                "十六宮":self.sixteen_gong(ji),
                "十天干歲始擊落宮預測": self.multi_key_dict_get (tengan_shiji, self.gangzhi()[0][0]).get(self.Ganzhiwuxing(self.sf(ji))),
                }
    
    def html(self, ji):
        text = '''<html><body><table border="0" cellpadding="1" cellspacing="1" style="width:500px">
    	<tbody>
    		<tr>
    			<td colspan="5">
    			<p><span style="font-size:large"><strong>'''+str(self.year)+"年"+str(self.month)+"月"+str(self.day)+"日"+str(self.hour)+"時"+'''<br />
    			干支: '''+self.gangzhi()[0]+"  "+self.gangzhi()[1]+"  "+self.gangzhi()[2]+"  "+self.gangzhi()[3]+'''&nbsp;</strong></span></p>
                <p><span style="font-size:large"><strong>'''+self.kingyear()+'''<br />
                <p><span style="font-size:large"><strong>'''+self.jiyuan(ji)+"  "+self.kook(ji).get("文")+'''<br />
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
    				<tbody>'''+"".join(list(map(lambda i:'''<tr><td>'''+i+'''</td></tr>''', self.pan(ji).get("十六宮").get("申"))))+'''</tbody>
    			</table>
    			</td>
    		</tr>
    		<tr>
    			<td><span style="font-size:large"><strong>卯</strong></span>
    			<table border="0" cellpadding="1" cellspacing="1" style="width:100px">
    				<tbody>'''+"".join(list(map(lambda i:'''<tr><td>'''+i+'''</td></tr>''', self.pan(ji).get("十六宮").get("卯"))))+'''</tbody>
    			</table>
    			</td>
    			<td><span style="font-size:large"><strong>酉</strong></span>
    			<table border="0" cellpadding="1" cellspacing="1" style="width:100px">
    				<tbody>'''+"".join(list(map(lambda i:'''<tr><td>'''+i+'''</td></tr>''', self.pan(ji).get("十六宮").get("酉"))))+'''</tbody>
    			</table>
    			</td>
    		</tr>
    		<tr>
    			<td><span style="font-size:large"><strong>寅</strong></span>
    			<table border="0" cellpadding="1" cellspacing="1" style="width:100px">
    				<tbody>'''+"".join(list(map(lambda i:'''<tr><td>'''+i+'''</td></tr>''', self.pan(ji).get("十六宮").get("寅"))))+'''</tbody>
    			</table>
    			</td>
    			<td><span style="font-size:large"><strong>戌</strong></span>
    			<table border="0" cellpadding="1" cellspacing="1" style="width:100px">
    				<tbody>'''+"".join(list(map(lambda i:'''<tr><td>'''+i+'''</td></tr>''', self.pan(ji).get("十六宮").get("戌"))))+'''</tbody>
    			</table>
    			</td>
    		</tr>
    		<tr>
    			<td><span style="font-size:large"><strong>艮</strong></span>
    			<table border="0" cellpadding="1" cellspacing="1" style="width:100px">
    				<tbody>'''+"".join(list(map(lambda i:'''<tr><td>'''+i+'''</td></tr>''', self.pan(ji).get("十六宮").get("艮"))))+'''</tbody>
    			</table>
    			</td>
    			<td><span style="font-size:large"><strong>丑</strong></span>
    				<table border="0" cellpadding="1" cellspacing="1" style="width:100px">
    				<tbody>'''+"".join(list(map(lambda i:'''<tr><td>'''+i+'''</td></tr>''', self.pan(ji).get("十六宮").get("丑"))))+'''</tbody>
    			</table>
    			</td>
    			<td><span style="font-size:large"><strong>子</strong></span>
    			<table border="0" cellpadding="1" cellspacing="1" style="width:100px">
    				<tbody>'''+"".join(list(map(lambda i:'''<tr><td>'''+i+'''</td></tr>''', self.pan(ji).get("十六宮").get("子"))))+'''</tbody>
    			</table>
    			</td>
    			<td><span style="font-size:large"><strong>亥</strong></span>
    			<table border="0" cellpadding="1" cellspacing="1" style="width:100px">
    				<tbody>'''+"".join(list(map(lambda i:'''<tr><td>'''+i+'''</td></tr>''', self.pan(ji).get("十六宮").get("亥"))))+'''</tbody>
    			</table>
    			</td>
    			<td><span style="font-size:large"><strong>乾</strong></span>
    			<table border="0" cellpadding="1" cellspacing="1" style="width:100px">
    				<tbody>'''+"".join(list(map(lambda i:'''<tr><td>'''+i+'''</td></tr>''', self.pan(ji).get("十六宮").get("乾"))))+'''</tbody>
    			</table>
    			</td>
    		</tr>
    	</tbody>
    </table>
    <p>&nbsp;</p></body></html>''' 
        return text


if __name__ == '__main__':
    tic = time.perf_counter()
    print(Taiyi(2022,6,19,0,0).pan(3) )
    toc = time.perf_counter()
    print(f"{toc - tic:0.4f} seconds")
