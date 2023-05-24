# -*- coding: utf-8 -*-
"""
Created on Tue May  9 14:14:13 2023

@author: kentang
"""

import re
import itertools
from ruler import ruler_data
import cn2an
from cn2an import an2cn
from ephem import Date
from sxtwl import fromSolar
from itertools import cycle, repeat
import jieqi


cnum = list("一二三四五六七八九十")
#干支
tian_gan = '甲乙丙丁戊己庚辛壬癸'
di_zhi = '子丑寅卯辰巳午未申酉戌亥'
#太乙、始擊、四神、天乙、地乙、值符排法
taiyi_pai = "乾乾乾離離離艮艮艮震震震兌兌兌坤坤坤坎坎坎巽巽巽乾乾乾離離離艮艮艮震震震兌兌兌坤坤坤坎坎坎巽巽巽乾乾乾離離離艮艮艮震震震兌兌兌坤坤坤坎坎坎巽巽巽"
sf_list = list("坤戌亥丑寅辰巳坤酉乾丑寅辰午坤酉亥子艮辰巳未申戌亥艮卯巽未丑戌子艮卯巳午坤戌亥丑寅辰巳坤酉乾丑寅辰午坤酉亥子艮辰巳未申戌亥艮卯巽未丑戌子艮卯巳午")
four_god = "乾乾乾離離離艮艮艮震震震中中中兌兌兌坤坤坤坎坎坎巽巽巽巳巳巳申申申寅寅寅"
sky_yi = "兌兌兌坤坤坤坎坎坎巽巽巽巳巳巳申申申寅寅寅乾乾乾離離離艮艮艮震震震中中中"
earth_yi = "巽巽巽巳巳巳申申申寅寅寅乾乾乾離離離艮艮艮震震震中中中兌兌兌坤坤坤坎坎坎"
zhi_fu = "中中中兌兌兌坤坤坤坎坎坎巽巽巽巳巳巳申申申寅寅寅乾乾乾離離離艮艮艮震震震"
officer_base = list("巳巳午午午未未未申申申酉酉酉戌戌戌亥亥亥子子子丑丑丑寅寅寅卯卯卯辰辰辰巳")
su_gong = dict(zip(list("子丑艮寅卯辰巽巳午未坤申酉戌乾亥"), list("虛斗牛尾房亢角翼星鬼井參昴婁奎室")))
#文昌陰陽七十二局分析
skyeyes_summary = {"陽":",始擊擊,,內迫,,,辰迫,,囚,,囚,,,,,,囚,囚,客挾,,,,,,,,囚,囚,始擊擊,,,始擊擊,始擊掩,始擊掩,,,,囚,辰迫,,客挾,客挾,囚,客挾,宮迫,,主挾，宮迫,辰迫,,,,主挾，辰迫,宮迫,宮迫,始擊掩,,,,客挾,,,,,,主挾,辰擊,,始擊掩,始擊擊,始擊擊,囚,始擊擊".split(","),
      "陰":",內辰迫,外辰迫,內辰擊,,,外宮迫,掩、辰迫,掩,掩、辰迫,掩、囚,內宮迫,內宮擊,,,掩、外辰迫,掩,掩,,關客,關客,關客,,外宮擊,,,外宮擊,,,,內宮擊,,關主,關客,,,外辰迫,掩,內辰迫,關客,內辰擊,,掩,內辰迫,內宮迫,掩,外宮迫,外宮迫,外宮擊,內宮擊,,內辰迫,外辰擊,掩,關主,,,外宮擊,掩,內宮擊,內宮迫,外宮擊,,內宮擊,,,,,,,,,".split(",")}
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
sixteen = "子丑艮寅卯辰巽巳午未坤申酉戌乾亥"
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
wangjigua="小畜䷈,大壯䷡,大有䷍,夬䷪,姤䷫,大過䷛,鼎䷱,恆䷟,巽䷸,井䷯,蠱䷑,升䷭,訟䷅,困䷮,未濟䷿,解䷧,渙䷺,蒙䷃,師䷆,遯䷠,咸䷞,旅䷷,小過䷽,漸䷴,蹇䷦,艮䷳,謙䷎,否䷋,萃䷬,晉䷢,豫䷏,觀䷓,比䷇,剝䷖,復䷗,頤䷚,屯䷂,益䷩,震䷲,噬嗑䷔,隨䷐,无妄䷘,明夷䷣,賁䷕,既濟䷾,家人䷤,豐䷶,革䷰,同人䷌,臨䷒,損䷨,節䷻,中孚䷼,歸妹䷵,睽䷥,兌䷹,履䷉,泰䷊,大畜䷙,需䷄".split(",")
ynum = list(range(-2397,4000))
ynum.remove(0)
wangji_yeargua = dict(zip( ynum,cycle(wangjigua)))
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

epochdict = dict(zip([
            ('甲子', '甲午', '乙丑', '乙未', '丙寅', '丙申', '丁卯', '丁酉', '戊辰', '戊戌'),
            ('己巳', '己亥', '庚午', '庚子', '辛未', '辛丑', '壬申', '壬寅', '癸酉', '癸卯'),
            ('甲戌', '甲辰', '乙亥', '乙巳', '丙子', '丙午', '丁丑', '丁未', '戊寅', '戊申'),
            ('己卯', '己酉', '庚辰', '庚戌', '辛巳', '辛亥', '壬午', '壬子', '癸未', '癸丑'),
            ('甲申', '甲寅', '乙酉', '乙卯', '丙戌', '丙辰', '丁亥', '丁巳', '戊子', '戊午'),
            ('己丑', '己未', '庚寅', '庚申', '辛卯', '辛酉', '壬辰', '壬戌', '癸巳', '癸亥')],  list("一二三四五六")))

jiyuan_dict = dict(zip([('甲子', '甲午', '乙丑', '乙未', '丙寅', '丙申', '丁卯', '丁酉', '戊辰', '戊戌', '己巳', '己亥'),
                ('庚午', '庚子', '辛未', '辛丑', '壬申', '壬寅', '癸酉', '癸卯', '甲戌', '甲辰', '乙亥', '乙巳'),
                ('丙子', '丙午', '丁丑', '丁未', '戊寅', '戊申', '己卯', '己酉', '庚辰', '庚戌', '辛巳', '辛亥'),
                ('壬午', '壬子', '癸未', '癸丑', '甲申', '甲寅', '乙酉', '乙卯', '丙戌', '丙辰', '丁亥', '丁巳'),
                ('戊子', '戊午', '己丑', '己未', '庚寅', '庚申', '辛卯', '辛酉', '壬辰', '壬戌', '癸巳', '癸亥')], "甲子,丙子,戊子,庚子,壬子".split(",")))
numdict = {1: "雜陰", 2: "純陰", 3: "純陽", 4: "雜陽", 6: "純陰", 7: "雜陰",
           8: "雜陽", 9: "純陽", 11: "陰中重陽", 12: "下和", 13: "雜重陽",
           14: "上和", 16: "下和", 17: "陰中重陽", 18: "上和", 19: "雜重陽",
           22: "純陰", 23: "次和", 24: "雜重陰", 26: "純陰", 27: "下和",
           28: "雜重陰", 29: "次和", 31: "雜重陽", 32: "次和", 33: "純陽",
           34: "下和", 37: "雜重陽", 38: "下和", 39: "純陽"}

gua_yao_years = {
 '乾':[36,36,36,36,36,36],
 '坤':[24,24,24,24,24,24],
 '否':[24,24,24,36,36,36],
 '泰':[36,36,36,24,24,24],
 '震':[36,24,24,36,24,24],
 '巽':[24,36,36,24,36,36],
 '恆':[24,36,36,36,24,24],
 '益':[36,24,24,24,36,36],
 '坎':[24,36,24,24,36,24],
 '離':[36,24,36,36,24,36],
 '既濟':[36,24,36,24,36,24],
 '未濟':[24,36,24,36,24,36],
 '艮':[24,24,36,24,24,36],
 '兌':[36,36,24,36,36,24],
 '損':[36,36,24,24,24,36],
 '咸':[24,24,36,36,36,24],
 '大壯':[36,36,36,36,24,24],
 '無妄':[36,24,24,36,36,36],
 '需':[36,36,36,24,36,24],
 '訟':[24,36,24,36,36,36],
 '大畜':[36,36,36,24,24,36],
 '遯':[24,24,36,36,36,36],
 '觀':[24,24,24,24,36,36],
 '升':[24,36,36,24,24,24],
 '晉':[24,24,24,36,24,36],
 '明夷':[36,24,36,24,24,24],
 '萃':[24,24,24,36,36,24],
 '臨':[36,36,24,24,24,24],
 '豫':[24,24,24,36,24,24],
 '復':[36,24,24,24,24,24],
 '比':[24,24,24,24,36,24],
 '師':[24,36,24,24,24,24],
 '剝':[24,24,24,24,24,36],
 '謙':[24,24,36,24,24,24],
 '小畜':[36,36,36,24,36,36],
 '姤':[24,36,36,36,36,36],
 '同人':[36,24,36,36,36,36],
 '大有':[36,36,36,36,24,36],
 '夬':[36,36,36,36,36,24],
 '履':[36,36,24,36,36,36],
 '解':[24,36,24,36,24,24],
 '屯':[36,24,24,24,36,24],
 '小過':[24,24,36,36,24,24],
 '頤':[36,24,24,24,24,36],
 '家人':[36,24,36,24,36,36],
 '鼎':[24,36,36,36,24,36],
 '中孚':[36,36,24,24,36,36],
 '大過':[24,36,36,36,36,24],
 '豐':[36,24,36,36,24,24],
 '噬嗑':[36,24,24,36,24,36],
 '歸妹':[36,36,24,36,24,24],
 '隨':[36,24,24,36,36,24],
 '節':[36,36,24,24,36,24],
 '困':[24,36,24,36,36,24],
 '渙':[24,36,24,24,36,36],
 '井':[24,36,36,24,36,24],
 '漸':[24,24,36,24,36,36],
 '蠱':[24,36,36,24,24,36],
 '旅':[24,24,36,36,24,36],
 '賁':[36,24,36,24,24,36],
 '蹇':[24,24,36,24,36,24],
 '蒙':[24,36,24,24,24,36],
 '睽':[36,36,24,36,24,36],
 '革':[36,24,36,36,36,24]}

tygua = "乾,坤,否,泰,震,巽,恆,益,坎,離,既濟,未濟,艮,兌,損,咸,大壯,無妄,需,訟,大畜,遯,觀,升,晉,明夷,萃,臨,豫,復,比,師,剝,謙,小畜,姤,同人,大有,夬,履,解,屯,小過,頤,家人,鼎,中孚,大過,豐,噬嗑,歸妹,隨,節,困,渙,井,漸,蠱,旅,賁,蹇,蒙,睽,革".split(",")
tygua_years = [216,144,180,180,168,192,180,180,168,192,180,180,168,192,180,180,192,192,192,192,192,192,168,168,168,168,168,168,156,156,156,156,156,156,204,204,204,204,204,204,168,168,168,168,192,192,192,192,180,180,180,180,180,180,180,180,180,180,180,180,168,168,192,192]
tygua_yun =  "天地否泰之運,男女交親之運,陽晶守政之運,陰毳權衡之運,資育還本之運,造化符天之運,剛中健至之運,德義順命之運,德義順命之運,惑妬留天之運,寡陽相博之運,物極元終之運".split(",")
tygua_dict = dict(zip(tygua, tygua_years))
year_for_gua = [-1197,-981,-837,-657,-477,-309,-117,64,244,412,604,784,964,1132,1324,1504,1684,1876,2068,2260,2452,2644,2836,3004,3172,3340,3508,3676,3844,4000,4156,4312,4468,4624,4780,4984,5188,5392,5596,5800,6004,6172,6340,6508,6676,6868,7060,7252,7444,7624,7804,7984,8164,8344,8524,8704,8884,9064,9244,9424,9604,9772,9940,10132]
year_rep_gua = dict(zip(year_for_gua,tygua))

#%% 基本功能函數
def sumlist(list1):
    list2 = []
    total_sum = 0
    for item in list1:
        total_sum += item
        list2.append(total_sum)
    return list2

def genyao(a):
    if a[0] == 36:
        b = "初九"
    if a[0] == 24:
        b = "初六"
    if a[1] == 36:
        c = "九二"
    if a[1] == 24:
        c = "六二"
    if a[2] == 36:
        d = "九三"
    if a[2] == 24:
        d = "六三"
    if a[3] == 36:
        e = "九四"
    if a[3] == 24:
        e = "六四"
    if a[4] == 36:
        f = "九五"
    if a[4] == 24:
        f = "六五"
    if a[5] == 36:
        g = "上九"
    if a[5] == 24:
        g = "上六"
    return [b,c,d,e,f,g]

def find_gua(year):
    def closest(lst, K):
        return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-K))]
    def closest1(lst, K):
        return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-K))-1]
    a = closest(year_for_gua, year)
    b = closest1(year_for_gua, year)
    if year > a and year > b:
        year_point = max(a,b)
    if year == a:
        year_point = a
    if year < a:
        year_point = b
    year_gua = year_rep_gua.get(year_point)
    y = gua_yao_years.get( year_gua )
    yao_list2 = sumlist(y)
    yao = genyao(y)
    year_diff = year - year_point
    yao_index = yao_list2.index(closest(yao_list2, year_diff))
    return year_gua + "之" + yao[yao_index]

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

def taiyi_name(ji_style):
    return {0:"年計", 1:"月計", 2:"日計", 3:"時計", 4:"分計"}.get(ji_style)

def ty_method(taiyi_acumyear):
    return  {0:"太乙統宗", 1:"太乙金鏡", 2:"太乙淘金歌", 3:"太乙局", 4: "太乙淘金歌時計捷法"}.get(taiyi_acumyear)

def cal_des(num):
    tnum = []
    if num > 10 and num % 10 > 5:
        tnum.append("三才足數")
    if num < 10:
        tnum.append("無天，二曜虛蝕、五緯失度、慧孛飛流、霜雹為害")
    if num % 10 < 5:
        tnum.append("無地，有崩地震、川竭蝗蝻之象")
    if num % 10 == 0:
        tnum.append("無人，口舌妖言更相殘賊，疾疫、遷移、流亡")
    tnum.append(numdict.get(num, None))
    return [i for i in tnum if i is not None]

#%% 甲子平支
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
    if year == 0:
        return ["無效"]
    if year < 0:
        year = year + 1 
    if hour == 23:
        d = Date(round((Date("{}/{}/{} {}:00:00.00".format(str(year).zfill(4), str(month).zfill(2), str(day+1).zfill(2), str(0).zfill(2)))), 3))
    else:
        d = Date("{}/{}/{} {}:00:00.00".format(str(year).zfill(4), str(month).zfill(2), str(day).zfill(2), str(hour).zfill(2) ))
    dd = list(d.tuple())
    cdate = fromSolar(dd[0], dd[1], dd[2])
    yTG,mTG,dTG,hTG = "{}{}".format(tian_gan[cdate.getYearGZ().tg], di_zhi[cdate.getYearGZ().dz]), "{}{}".format(tian_gan[cdate.getMonthGZ().tg],di_zhi[cdate.getMonthGZ().dz]), "{}{}".format(tian_gan[cdate.getDayGZ().tg], di_zhi[cdate.getDayGZ().dz]), "{}{}".format(tian_gan[cdate.getHourGZ(dd[3]).tg], di_zhi[cdate.getHourGZ(dd[3]).dz])
    if year < 1900:
        mTG1 = find_lunar_month(yTG).get(lunar_date_d(year, month, day).get("月"))
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

#五子元局數
def five_zi_yuan(taiyiju, gangzhi):
    a =["甲子","丙子","戊子","庚子","壬子"]
    b = [1,73,145,217,289]
    c = [(new_list(jiazi(),i)*2)[0:72] for  i in a]
    d = [new_list(list(range(i, i+72)), i) for i in b]
    return an2cn(dict(zip([c[i][taiyiju-1] for i in range(0,5)], [d[i][taiyiju-1] for i in range(0,5)])).get(gangzhi)) + "局"

def five_zi_yuan1(taiyiju):
    a =["甲子","丙子","戊子","庚子","壬子"]
    b = [1,73,145,217,289]
    c = [(new_list(jiazi(),i)*2)[0:72] for  i in a]
    d = [new_list(list(range(i, i+72)), i) for i in b]
    return dict(zip([c[i][taiyiju-1] for i in range(0,5)], [d[i][taiyiju-1] for i in range(0,5)]))

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
        cyear = an2cn(year+2)
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

#五行
def wuxing(taiyi_acumyear):
    #f = self.accnum(ji_style, taiyi_acumyear) // 5
    f = taiyi_acumyear // 5
    f = f % 5
    fv =  dict(zip(range(1,10), [1,3,5,7,9,2,4,6,8])).get(int(f))
    if fv == 0 or fv is None:
        fv = 5
    return fv
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

#五福
def wufu(taiyi_acumyear):
    f = (taiyi_acumyear + 250) % 225 / 45
    #f = int(self.accnum(ji_style, taiyi_acumyear) + 250) % 225 / 45
    fv = dict(zip(range(1,6), list("乾艮巽坤中"))).get(int(f))
    if fv == 0 or fv is None:
        fv = 5
    return fv

#陽九
def yangjiu(year, month, day):
    year = lunar_date_d(year, month, day).get("年")
    getyj = (year + 12607)%4560%456 % 12
    if getyj>=12:
        getyj = getyj % 12
        return dict(zip(range(1,13),new_list(di_zhi, "寅"))).get(getyj)
    elif getyj == 0:
        return dict(zip(range(1,13),new_list(di_zhi, "寅"))).get(12)
    else:
        return dict(zip(range(1,13),new_list(di_zhi, "寅"))).get(getyj)
#百六
def baliu(year, month, day):
    year = lunar_date_d(year, month, day).get("年")
    getbl = (year + 12607)%4320%288 % 24
    if getbl >12:
        getbl = (getbl - 12) %12
        return dict(zip(range(1,13),new_list(di_zhi, "卯"))).get(getbl)
    elif getbl == 0:
        return dict(zip(range(1,13),new_list(di_zhi, "酉"))).get(12)
    else:
        return dict(zip(range(1,13),new_list(di_zhi, "酉"))).get(getbl)
#大游
def bigyo(taiyi_acumyear):
    #big_yo = int((self.accnum(ji_style, taiyi_acumyear) +34) % 388)
    big_yo = (taiyi_acumyear + 34) % 388
    if big_yo < 36:
        big_yo = big_yo
    if big_yo > 36:
        big_yo = big_yo / 36
    byv = dict(zip([7,8,9,1,2,3,4,6],range(1,9))).get(int(big_yo))
    if byv == 0 or byv is None:
        byv = 5
    return byv
#小游
def smyo(taiyi_acumyear):
    small_yo = taiyi_acumyear  % 360
    #sy = int(self.accnum(ji_style, taiyi_acumyear)  % 360)
    if small_yo < 24:
        small_yo = small_yo % 3
    if small_yo > 24:
        small_yo = small_yo % 24
        if small_yo > 3:
            small_yo = small_yo % 3
    syv = dict(zip([1,2,3,4,6,7,8,9],range(1,9))).get(int(small_yo))
    if syv == 0 or syv is None:
        syv = 5
    return syv
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
def geteightdoors(ty, doors):
    new_ty_order = new_list([8,3,4,9,2,7,6,1], ty)
    #doors  = new_list(door, eight_door(taiyi_acumyear))
    #doors = new_list(door, eightdoor)
    return dict(zip(new_ty_order, doors))

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

