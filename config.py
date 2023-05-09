# -*- coding: utf-8 -*-
"""
Created on Tue May  9 14:14:13 2023

@author: kentang
"""

import re
import itertools
from ruler import ruler_data
from cn2an import an2cn
from ephem import Date
from sxtwl import fromSolar
from itertools import cycle, repeat
import jieqi

#干支
tian_gan = '甲乙丙丁戊己庚辛壬癸'
di_zhi = '子丑寅卯辰巳午未申酉戌亥'


su = list('角亢氐房心尾箕斗牛女虛危室壁奎婁胃昴畢觜參井鬼柳星張翼軫')
num =  [8,3,4,9,2,7,6,1]
su = list('角亢氐房心尾箕斗牛女虛危室壁奎婁胃昴畢觜參井鬼柳星張翼軫')
#干支
Gan,Zhi = '甲乙丙丁戊己庚辛壬癸', '子丑寅卯辰巳午未申酉戌亥'
#間辰
jc = list("丑寅辰巳未申戌亥")
door = list("開休生傷杜景死驚")
jc1 = list("巽艮坤乾")
tyjc = [1,3,7,9]
#十六神
sixteengod = dict(zip(re.findall("..", "地主陽德和德呂申高叢太陽大炅大神大威天道大武武德太簇陰主陰德大義"), "子丑艮寅卯辰巽巳午未坤申酉戌乾亥"))
#陰陽遁定制
five_elements = dict(zip(re.findall('..', '太乙天乙地乙始擊文昌主將主參客將客參'), list("木火土火土金水水木")))
gong = dict(zip(list("子丑艮寅卯辰巽巳午未坤申酉戌乾亥"), range(1,17)))
gong1 = list("子丑艮寅卯辰巽巳午未坤申酉戌乾亥")
gong2 = dict(zip(list("亥子丑艮寅卯辰巽巳午未坤申酉戌乾"), [8,8,3,3,4,4,9,9,2,2,7,7,6,6,1,1]))
gong3 = list("子丑艮寅卯辰巽巳中午未坤申酉戌乾亥")
wuxing = "火水金火木金水土土木,水火火金金木土水木土,火火金金木木土土水水,火木水金木水土火金土,木火金水水木火土土金"
wuxing_relation_2 = dict(zip(list(map(lambda x: tuple(re.findall("..",x)), wuxing.split(","))), "尅我,我尅,比和,生我,我生".split(",")))
nayin = "甲子乙丑壬申癸酉庚辰辛巳甲午乙未壬寅癸卯庚戌辛亥,丙寅丁卯甲戌乙亥戊子己丑丙申丁酉甲辰乙巳戊午己未,戊辰己巳壬午癸未庚寅辛卯戊戌己亥壬子癸丑庚申辛酉,庚午辛未戊寅己卯丙戌丁亥庚子辛丑戊申己酉丙辰丁巳,甲申乙酉丙子丁丑甲寅乙卯丙午丁未壬戌癸亥壬辰癸巳".split(",")
nayin_wuxing = dict(zip([tuple(re.findall("..", i)) for i in nayin], list("金火木土水")))
gua = dict(zip(range(1,65),"乾䷀,坤䷁,屯䷂,蒙䷃,需䷄,訟䷅,師䷆,比䷇,小畜䷈,履䷉,泰䷊,否䷋,同人䷌,大有䷍,謙䷎,豫䷏,隨䷐,蠱䷑,臨䷒,觀䷓,噬嗑䷔,賁䷕,剝䷖,復䷗,无妄䷘,大畜䷙,頤䷚,大過䷛,坎䷜,離䷝,咸䷞,恆䷟,遯䷠,大壯䷡,晉䷢,明夷䷣,家人䷤,睽䷥,蹇䷦,解䷧,損䷨,益䷩,夬䷪,姤䷫,萃䷬,升䷭,困䷮,井䷯,革䷰,鼎䷱,震䷲,艮䷳,漸䷴,歸妹䷵,豐䷶,旅䷷,巽䷸,兌䷹,渙䷺,節䷻,中孚䷼,小過䷽,既濟䷾,未濟䷿".split(",")))

gzzm ={"甲":{"朝":"小吉", "暮":"大吉"}, 
         tuple(list("戊庚")): {"朝":"大吉", "暮":"小吉"},
        "己":{"朝":"神后", "暮":"傳送"}, "乙":{"朝":"傳送", "暮":"神后"}, 
        "丁":{"朝":"登明", "暮":"從魁"}, "丙":{"朝":"從魁", "暮":"登明"}, 
        "癸":{"朝":"太乙", "暮":"太衝"}, "壬":{"朝":"太衝", "暮":"太乙"}, 
        "辛":{"朝":"功曹", "暮":"勝光"}}
zm = {tuple(list("卯辰巳午未申")):"朝", tuple(list("酉戌亥子丑寅")):"暮"}
tz = "登明,河魁,從魁,傳送,小吉,勝光,太乙,天罡,太衝,功曹,大吉,神後".split(",")
skyeyes_dict = {
    "陽" : list("申酉戌乾乾亥子丑艮寅卯辰巽巳午未坤坤申酉戌乾乾亥子丑艮寅卯辰巽巳午未坤坤申酉戌乾乾亥子丑艮寅卯辰巽巳午未坤坤申酉戌乾乾亥子丑艮寅卯辰巽巳午未坤坤"),
    "陰" : list("寅卯辰巽巽巳午未坤申酉戌乾亥子丑艮艮寅卯辰巽巽巳午未坤申酉戌乾亥子丑艮艮寅卯辰巽巽巳午未坤申酉戌乾亥子丑艮艮寅卯辰巽巽巳午未坤申酉戌乾亥子丑艮艮")}

def taiyi_name(ji_style):
    return {0:"年計", 1:"月計", 2:"日計", 3:"時計", 4:"分計"}.get(ji_style)

def ty_method(taiyi_acumyear):
    return  {0:"太乙統宗", 1:"太乙金鏡", 2:"太乙淘金歌", 3:"太乙局", 4: "太乙淘金歌時計捷法"}.get(taiyi_acumyear)


#%% 基本功能函數
def multi_key_dict_get(d, k):
    for keys, v in d.items():
        if k in keys:
            return v
    return None

def new_list(olist, o):
    a = olist.index(o)
    res1 = olist[a:] + olist[:a]
    return res1

def gendatetime(year, month, day, hour):
    return "{}年{}月{}日{}時".format(year, month, day, hour)

def repeat_list(n, thelist):
    return [repetition for i in thelist for repetition in repeat(i,n)]

def num2gong(num):
    return dict(zip(range(1,10), list("乾午艮卯中酉坤子巽"))).get(num)

#%% 甲子
def jiazi():
    Gan, Zhi = '甲乙丙丁戊己庚辛壬癸', '子丑寅卯辰巳午未申酉戌亥'
    return list(map(lambda x: "{}{}".format(Gan[x % len(Gan)], Zhi[x % len(Zhi)]), list(range(60))))

def Ganzhiwuxing(gangorzhi):
    ganzhiwuxing = dict(zip(list(map(lambda x: tuple(x),"甲寅乙卯震巽,丙巳丁午離,壬亥癸子坎,庚申辛酉乾兌,未丑戊己未辰戌艮坤".split(","))), list("木火水金土")))
    return multi_key_dict_get(ganzhiwuxing, gangorzhi)

def find_wx_relation(zhi1, zhi2):
    return multi_key_dict_get(wuxing_relation_2, Ganzhiwuxing(zhi1) + Ganzhiwuxing(zhi2))
#換算干支
def gangzhi(year, month, day, hour, minute):
    if hour == 23:
        d = Date(round((Date("{}/{}/{} {}:00:00.00".format(str(year).zfill(4), str(month).zfill(2), str(day).zfill(2), str(hour).zfill(2))) + 1 * hour), 3))
    else:
        d = Date("{}/{}/{} {}:00:00.00".format(str(year).zfill(4), str(month).zfill(2), str(day).zfill(2), str(hour).zfill(2) ))
    dd = list(d.tuple())
    cdate = fromSolar(dd[0], dd[1], dd[2])
    yTG,mTG,dTG,hTG = "{}{}".format(tian_gan[cdate.getYearGZ().tg], di_zhi[cdate.getYearGZ().dz]), "{}{}".format(tian_gan[cdate.getMonthGZ().tg],di_zhi[cdate.getMonthGZ().dz]), "{}{}".format(tian_gan[cdate.getDayGZ().tg], di_zhi[cdate.getDayGZ().dz]), "{}{}".format(tian_gan[cdate.getHourGZ(dd[3]).tg], di_zhi[cdate.getHourGZ(dd[3]).dz])
    if year < 1900:
        mTG1 = find_lunar_month(yTG).get(lunar_date_d().get("月"))
    else:
        mTG1 = mTG
    hTG1 = find_lunar_hour(dTG).get(hTG[1])
    gangzhi_minute = minutes_jiazi_d().get(str(hour)+":"+str(minute))
    return [yTG, mTG1, dTG, hTG1, gangzhi_minute]
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

#分干支
def minutes_jiazi_d():
    t = [f"{h}:{m}" for h in range(24) for m in range(60)]
    minutelist = dict(zip(t, cycle(repeat_list(2, jiazi()))))
    return minutelist
#農曆
def lunar_date_d(year, month, day):
    day = fromSolar(year, month, day)
    return {"年":day.getLunarYear(),  "月": day.getLunarMonth(), "日":day.getLunarDay()}

#中國統治者在位年
def kingyear(year):
    def closest(lst, K):
        return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-K))]
    data = ruler_data
    y =  list(map(lambda x: int(x), data[0::7]))
    period = data[3::7]
    king = data[4::7]
    king_realname = data[5::7]
    preiodname = data[6::7]
    idx = y.index(closest(y, year))
    if year == y[idx]:
        year = "元"
        pn = "{}{}年".format(preiodname[idx], year)
        kn = "{}{}{}".format(period[idx], king[idx], king_realname[idx])
        return  "{} {}".format(kn, pn)
    elif year > y[idx]:
        year = year - y[idx] +1
        cyear = an2cn(year)
        pn = "{}{}年".format(preiodname[idx],cyear)
        kn = "{}{}{}".format(period[idx], king[idx], king_realname[idx])
        return  "{} {}".format(kn, pn)
    elif year < y[idx] and year> -2069:
        year = year - y[idx-1] 
        cyear = an2cn(year+1)
        pn = "{}{}年".format(preiodname[idx-1],cyear)
        kn = "{}{}{}".format(period[idx-1], king[idx-1], king_realname[idx-1])
        return  "{} {}".format(kn, pn)
    elif year < -2068:
        return ""

#%% 二十八宿
#推二十八星宿
def starhouse(year, month, day, hour):
    numlist = [13,9,16,5,5,17,10,24,7,11,25,18,17,10,17,13,14,11,16,1,9,30,3,14,7,19,19,18]
    alljq = jieqi.jieqi_name
    njq = new_list(alljq, "冬至")
    gensulist =  list(itertools.chain.from_iterable([[su[i]]*numlist[i] for i in range(0,28)]))
    jqsulist = [["斗", 9],["斗",24] ,["女", 8],["危",2],["室", 1],["壁",1] ,["奎", 4],["婁",2] ,["胃", 4],["昴",4] ,["畢", 8],["參",6] ,["井", 1],["井", 27],["柳",8] ,["張", 3],["翼",1] ,["翼", 16],["軫",13] ,["角", 9],["房", 1],["氐",2] ,["尾", 6],["箕",24]]
    njq_list = dict(zip(njq, jqsulist))
    currentjq = jieqi.jq(year, month, day, hour)
    distance_to_cjq = jieqi.distancejq(year, month, day, hour, currentjq)
    num = gensulist.index(njq_list.get(currentjq)[0]) + njq_list.get(currentjq)[1] + distance_to_cjq
    if num >360:
        return new_list(gensulist, njq_list.get(currentjq)[0])[num-360]
    else:
        return gensulist[num]
    
    


#%% 太乙十精
#帝符
def kingfu(taiyi_acumyear):
    #f = self.accnum(ji_style, taiyi_acumyear) % 20
    kingfu_num = taiyi_acumyear % 20
    if kingfu_num > 16:
        kingfu_num = kingfu_num - 16
    king_fu = dict(zip(range(1,17), new_list(gong1, "戌"))).get(int(kingfu_num))
    if king_fu == 0 or king_fu is None:
        king_fu = "中"
    return king_fu
#太尊
def taijun(taiyi_acumyear):
    f = taiyi_acumyear % 4
    #f = self.accnum(ji_style, taiyi_acumyear) % 4
    fv = dict(zip(range(1,5), list("子午卯酉"))).get(int(f))
    if fv == 0  or fv is None:
        fv = "中"
    return fv
#飛鳥
def flybird(taiyi_acumyear):
    f = taiyi_acumyear % 9
    #f = self.accnum(ji_style, taiyi_acumyear) % 9
    fv = dict(zip(range(1,10), [1,8,3,4,9,2,7,6])).get(int(f))
    if fv == 0 or fv is None:
        fv = 5
    return fv
#推太乙風雲飛鳥助戰法
def flybird_wl(taiyi_acumyear, fb, hg, ag, hvg, avg, ty, wc, sj):
    #fb = flybird(taiyi_acumyear)
    #hg = self.home_general(ji_style, taiyi_acumyear)
    #ag = self.away_general(ji_style, taiyi_acumyear)
    #hvg = self.home_vgen(ji_style, taiyi_acumyear)
    #avg = self.away_vgen(ji_style, taiyi_acumyear)
    #ty = self.ty(ji_style, taiyi_acumyear)
    #wc = gong2.get(self.skyeyes(ji_style, taiyi_acumyear))
    #sj = gong2.get(self.sf(ji_style, taiyi_acumyear))
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
#三風
def threewind(taiyi_acumyear):
    #f = self.accnum(ji_style, taiyi_acumyear) % 9
    f = taiyi_acumyear % 9
    fv = dict(zip(range(1,9), [7,2,6,1,5,9,4,8])).get(int(f))
    if fv == 0 or fv is None:
        fv = 5
    return fv
#五風
def fivewind(taiyi_acumyear):
    f = taiyi_acumyear % 29
    #f = self.accnum(ji_style, taiyi_acumyear) % 29
    if f > 10:
        f = f - 9
    fv = dict(zip(range(1,10), [1,3,5,7,9,2,4,6,8])).get(int(f))
    if fv == 0 or fv is None:
        fv = 5
    return fv
#八風
def eightwind(taiyi_acumyear):
    f = taiyi_acumyear % 9
    #f = self.accnum(ji_style, taiyi_acumyear) % 9
    fv = dict(zip(range(1,9), [2,3,5,6,7,8,9,1])).get(int(f))
    if fv == 0 or fv is None:
        fv = 5
    return fv

#%% 三門五將

#八門值事
def eight_door(taiyi_acumyear):
    acc = taiyi_acumyear % 240
    #acc = self.accnum(ji_style, taiyi_acumyear) % 240
    if acc == 0:
        acc = 120
    eightdoor_zhishi = acc // 30
    if eightdoor_zhishi % 30 != 0:
        eightdoor_zhishi = eightdoor_zhishi + 1
    elif eightdoor_zhishi == 0:
        eightdoor_zhishi = 1
    #ty_gong = self.ty()
    return dict(zip(list(range(1,9)),door)).get(eightdoor_zhishi)

#推八門分佈
def geteightdoors(ty, eightdoor):
    new_ty_order = new_list([8,3,4,9,2,7,6,1], ty)
    #doors  = new_list(door, eight_door(taiyi_acumyear))
    doors = new_list(door, eightdoor)
    return dict(zip(new_ty_order, doors))

#推三門具不具
def threedoors(ty, ed):
    #ty = self.ty(ji_style, taiyi_acumyear)
    #ed = self.geteightdoors(ji_style, taiyi_acumyear)
    door = ed.get(ty)
    if door in list("休生開"):
        return "三門不具。"
    else:
        return "三門具。"
#推五將發不發
def fivegenerals(wc_status, home_general, away_general):
    if wc_status == "" and home_general != 5 and away_general != 5:
    #if self.skyeyes_des(ji_style, taiyi_acumyear) == "" and hg != 5 and ag != 5:
        return "五將發。"
    elif home_general == 5:
        return "主將主參不出中門，杜塞無門。"
    elif away_general == 5:
        return "客將客參不出中門，杜塞無門。"
    else:
        return wc_status+"。五將不發。"

#%% 太乙七式
#推雷公入水
def leigong(ty):
    find_ty = dict(zip([1,2,3,4,6,7,8,9],list("乾午艮卯酉坤子巽"))).get(ty)
    new_order = new_list(gong1, find_ty)
    return dict(zip(range(1,17),new_order)).get(1+4)
#推臨津問道
def lijin(year, month, day, hour, minute):
    year = dict(zip(di_zhi, range(1,13))).get(gangzhi(year, month, day, hour, minute)[0][1])
    return new_list(gong1, "寅")[year]
#推獅子反擲
def lion(year, month, day, hour, minute):
    return new_list(gong1, gangzhi(year, month, day, hour, minute)[0][1])[4]
#推白雲捲空
def cloud(hg_num):
    return new_list(list(reversed(gong1)), "寅")[hg_num]
#推猛虎相拒
def tiger(ty):
    new_order = new_list(gong1, "寅")
    return new_order[ty]
#推白龍得云
def dragon(ty):
    new_order = new_list(list(reversed(gong1)), "寅")
    return new_order[ty]
#推回軍無言
def returnarmy(ag_num):
    return new_list(gong1, "寅")[ag_num]
#推多少以占勝負  客以多筭臨少主人敗客以少筭臨多主人勝也
def suenwl(homecal, awaycal, home_general, away_general ):
    if awaycal < homecal and home_general != 5:
        return "客以少筭臨多，主人勝也。"
    elif awaycal < homecal and home_general == 5:
        return "雖客以少筭臨多，惟主人不出中門，主客俱不利，和。"
    elif awaycal > homecal and away_general != 5:
        return "客以多筭臨少，主人敗也。"
    elif awaycal > homecal and away_general == 5:
        return "雖客以多筭臨少，惟客人不出中門，主客俱不利，和。"
    else:
        return "主客旗鼓相當。"