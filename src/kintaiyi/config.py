# -*- coding: utf-8 -*-
"""
Created on Tue May  9 14:14:13 2023

@author: kentang
"""

import re
import os
import pickle
import itertools
from itertools import cycle, repeat, starmap
from datetime import date
import datetime
from .ruler import ruler_data
import cn2an
from cn2an import an2cn
from sxtwl import fromSolar
from . import jieqi
from bidict import bidict

base = os.path.abspath(os.path.dirname(__file__))
path = os.path.join(base, 'data.pkl')
data = pickle.load(open(path, "rb"))
sixtyfourgua = bidict(data.get("數字排六十四卦"))
wangji_gua = dict(zip(range(1,61),"復,頤,屯,益,震,噬嗑,隨,无妄,明夷,賁,既濟,家人,豐,革,同人,臨,損,節,中孚,歸妹,睽,兌,履,泰,大畜,需,小畜,大壯,大有,夬,姤,大過,鼎,恆,巽,井,蠱,升,訟,困,未濟,解,渙,蒙,師,遯,咸,旅,小過,漸,蹇,艮,謙,否,萃,晉,豫,觀,比,剝".split(",")))

cmonth = list("一二三四五六七八九十") + ["十一","十二"]
cnum = list("一二三四五六七八九十")
#干支
tian_gan = '甲乙丙丁戊己庚辛壬癸'
di_zhi = '子丑寅卯辰巳午未申酉戌亥'

golden_d = re.findall("..","太乙攝提軒轅招搖天符青龍咸池太陰天乙")
#太乙、始擊、四神、天乙、地乙、值符排法
taiyi_pai = "乾乾乾午午午艮艮艮卯卯卯酉酉酉坤坤坤子子子巽巽巽乾乾乾午午午艮艮艮卯卯卯酉酉酉坤坤坤子子子巽巽巽乾乾乾午午午艮艮艮卯卯卯酉酉酉坤坤坤子子子巽巽巽"
sf_list = list("坤戌亥丑寅辰巳坤酉乾丑寅辰午坤酉亥子艮辰巳未申戌亥艮卯巽未丑戌子艮卯巳午坤戌亥丑寅辰巳坤酉乾丑寅辰午坤酉亥子艮辰巳未申戌亥艮卯巽未丑戌子艮卯巳午")
four_god = "乾乾乾午午午艮艮艮卯卯卯中中中酉酉酉坤坤坤子子子巽巽巽巳巳巳申申申寅寅寅"
sky_yi = "酉酉酉坤坤坤子子子巽巽巽巳巳巳申申申寅寅寅乾乾乾午午午艮艮艮卯卯卯中中中"
earth_yi = "巽巽巽巳巳巳申申申寅寅寅乾乾乾午午午艮艮艮卯卯卯中中中酉酉酉坤坤坤子子子"
zhi_fu = "中中中酉酉酉坤坤坤子子子巽巽巽巳巳巳申申申寅寅寅乾乾乾午午午艮艮艮卯卯卯"
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

cheungsun = dict(zip(list("木火金水土"),list("亥寅巳申申")))
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

#找主客定算
def find_cal(yingyang, num):
    yangcal =[[7,13,13],[6,1,1],[1,40,32],[25,17,10],[25,14,1],[25,10,12],[8,25,9],[1,22,3],[3,15,33],[1,12,25],[4,4,13],[37,1,4],[18,19,19],[10,9,9],[9,7,6],[1,33,26],[7,27,16],[7,26,11],[8,32,14],[7,26,2],[2,17,33],[16,30,1],[16,23,32],[16,17,23],[39,40,40],[32,31,31],[31,28,31],[14,9,38],[13,39,26],[10,32,17],[33,10,34],[25,8,24],[24,3,15],[26,4,11],[25,28,1],[25,27,36],[1,7,7],[6,35,35],[35,34,26],[27,19,12],[27,16,3],[27,12,34],[8,17,1],[23,14,32],[32,7,25],[5,16,29],[4,8,17],[1,5,8],[24,25,25],[16,15,15],[15,13,6],[39,31,24],[38,25,14],[38,24,9],[16,3,22],[15,34,10],[10,25,10],[12,26,27],[12,19,28],[12,13,19],[33,34,34],[26,25,25],[25,22,18],[16,11,7],[15,1,28],[12,34,19],[25,2,26],[17,8,16],[16,32,7],[30,4,15],[29,32,5],[29,31,9]]
    yingcal = [[5,29,7],[4,17,1],[1,16,30],[25,33,2],[25,30,1],[17,26,10],[2,3,3],[1,7,7],[7,33,27],[1,24,25],[6,26,19],[35,23,8],[12,37,12],[12,27,11],[11,25,4],[1,15,24],[3,9,16],[3,8,9],[14,16,16],[13,10,10],[10,1,39],[24,14,1],[24,7,40],[16,1,29],[31,16,32],[30,7,29],[29,4,26],[8,25,32],[7,15,26],[2,8,15],[27,28,28],[27,26,26],[26,18,15],[29,22,9],[25,10,1],[25,9,34],[1,25,3],[4,13,37],[37,12,26],[33,1,10],[33,38,9],[25,34,38],[2,1,1],[39,38,38],[38,31,25],[7,1,31],[6,32,25],[1,29,14],[16,1,17],[16,31,15],[15,29,4],[33,7,16],[32,1,8],[32,8,1],[16,18,18],[15,12,12],[12,3,1],[18,8,35],[18,1,34],[10,35,25],[27,22,28],[26,3,25],[25,4,12],[16,33,3],[15,23,34],[10,16,23],[25,26,26],[25,24,24],[24,16,13],[32,28,15],[31,16,7],[31,15,1]]
    yy = {"陰":yingcal ,"陽":yangcal}.get(yingyang)
    return dict(zip(list(range(1,73)), yy)).get(num)
      
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


def calculate_value_for_year(year):
    initial_value = 126944450
    increment_per_60_years = 3145500
    cycles = (year - 1564) // 60
    value = initial_value + cycles * increment_per_60_years
    return value

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

#農曆
def lunar_date_d(year, month, day):
    lunar_m = ['占位', '正月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '冬月', '腊月']
    day = fromSolar(year, month, day)
    return {"年":day.getLunarYear(),
            "農曆月": lunar_m[int(day.getLunarMonth())],
            "月":day.getLunarMonth(),
            "日":day.getLunarDay()}
#旬
def liujiashun_dict():
    return dict(zip(list(map(lambda x: tuple(x), list(map(lambda x:new_list(jiazi(), x)[0:10] ,jiazi()[0::10])))), jiazi()[0::10]))


def closest(lst, K):
    return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-K))]

def closest1(lst, K):
    return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-K))-1]

def closest2(lst, K):
    return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-K))+1]

def find_gua(year):
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

def divide(num, division_num):
    if not isinstance(num, int) or num <= 0:
        return "請輸入一個正整數"
    while num % division_num == 0:
        num = num // division_num
    return num

def change(g, yao):
    g = list(g)
    y = {6: 5, 5: 4, 4: 3, 3: 2, 2: 1, 1: 0}.get(yao)
    if g[y] == "7":
        a = "8"
    if g[y] == "8":
        a = "7"
    return "".join([a if i == y else g[i] for i in range(len(g))])
      
def wanji_four_gua(year, month, day, hour, minute):
    ygz = gangzhi(year, month, day, hour, minute)[0]
    if year < 0:
        acum_year = 67017 + year + 1
    else:
        acum_year = 67017 + year #積年數
    hui  = acum_year // 10800 +1 #會
    yun = acum_year // 360 +1  #運
    shi = acum_year // 30 + 1 #世
    main_gua = wangji_gua.get(int(round((acum_year / 2160), 0)))#
    mys = list(sixtyfourgua.inverse[main_gua][0].replace("6","8").replace("9","7"))
    if yun % 6 == 0:
        yun_gua_yao = 6
    else:
        yun_gua_yao = yun % 6
    mys1 = change(mys, yun_gua_yao)
    yungua = multi_key_dict_get(sixtyfourgua, mys1)
    shi_yao = shi // 2 % 6  
    shis1 = change(mys1, shi_yao)
    shigua = multi_key_dict_get(sixtyfourgua, change(mys1, shi_yao))
    shi_shun = dict(zip("甲子,甲戌,甲申,甲午,甲辰,甲寅".split(","),range(1,7)))
    shun_yao = shi_shun.get(multi_key_dict_get(liujiashun_dict(), ygz))
    shungua1 = change(shis1,shun_yao)
    shun_gua = multi_key_dict_get(sixtyfourgua, shungua1)
    jiazi_years = [4 - 60 * i for i in range(52)]+[4 + 60 * i for i in range(52)]
    if year < 0:
        close_jiazi_year = closest2(jiazi_years, year)
    else:
        close_jiazi_year = closest1(jiazi_years, year)
    yeargua = dict(zip(list(range(close_jiazi_year, close_jiazi_year+60)), new_list(list(wangji_gua.values()), shigua))).get(year)
    return {"會":hui, "運":yun, "世":shi, "運卦動爻":yun_gua_yao, "世卦動爻": shi_yao, "旬卦動爻":shun_yao ,"正卦":main_gua, "運卦":yungua, "世卦":shigua, "旬卦":shun_gua, "年卦":yeargua } 

def multi_key_dict_get(d, k):
    for keys, v in d.items():
        if k in keys:
            return v
    return None

def new_list(olist, o):
    a = olist.index(o)
    res1 = olist[a:] + olist[:a]
    return res1

def gendatetime(year, month, day, hour, minute):
    return "{}年{}月{}日{}時{}分".format(year, month, day, hour, minute)

def repeat_list(n, thelist):
    return [repetition for i in thelist for repetition in repeat(i,n)]

def num2gong(num):
    return dict(zip(range(1,10), list("乾午艮卯中酉坤子巽"))).get(num)
      
def num2gong_life(num):
    return dict(zip(range(1,10), list("乾午艮卯辰酉坤子巽"))).get(num)

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

#太乙人道命法的積年數
def jiazi_accum(gz):
    return dict(zip(jiazi(), [i*3652425 for i in list(range(1,61))])).get(gz)

def jq_accum(jq):
    return dict(zip(new_list(jieqi.jieqi_name, "冬至"), [3652425,152184.37,304368.75,456553.12,608727.50,760921.87,913106.25,1065290.62,1217475,1369659.37,1522843.75,1674028.12,1826212.50,1978396.87,2130581.25,2282765.62,2434950,2587134.37,2739318.75,2891503.12,3043687.50,3195871.87,3348056.25,3500240.62])).get(jq)

def Ganzhiwuxing(gangorzhi):
    ganzhiwuxing = dict(zip(list(map(lambda x: tuple(x),"甲寅乙卯震巽,丙巳丁午離,壬亥癸子坎,庚申辛酉乾兌,未丑戊己未辰戌艮坤".split(","))), list("木火水金土")))
    return multi_key_dict_get(ganzhiwuxing, gangorzhi)

def calculateAge(birthDate):
    today = datetime.date.today()
    age = today.year - birthDate.year -((today.month, today.day) <(birthDate.month, birthDate.day))
    return age

def Ganzhi_num(gang):
    num = dict(zip(list(map(lambda x: tuple(x),"甲己,乙庚,丙辛,丁壬,戊癸".split(","))), [5,4,1,3,2]))
    return multi_key_dict_get(num, gang)

def Ganzhi_place(gang):
    place = dict(zip(list(map(lambda x: tuple(x),"甲己,乙庚,丙辛,丁壬,戊癸".split(","))), list("午巳申亥寅")))
    return multi_key_dict_get(place, gang)

def generate_ranges(start, n, num_ranges):
    ranges = []
    a = start
    for i in range(num_ranges):
        end = start + n - 1
        ranges.append(f"{start+1}-{end+1}")
        start = end + 1  # The next range starts right after the current end
    return ["1-{}".format(a)]+ranges

def gangzhi_to_num(gangorzhi):
    return dict(zip("金木水火土", [13,11,7,9,15])).get(Ganzhiwuxing(gangorzhi))

def element_to_num(element):
    return dict(zip("金木水火土", [13,11,7,9,15])).get(element)

def find_wx_relation(zhi1, zhi2):
    return multi_key_dict_get(wuxing_relation_2, Ganzhiwuxing(zhi1) + Ganzhiwuxing(zhi2))

#換算干支
def gangzhi1(year, month, day, hour, minute):
    if hour == 23:
        d_year, d_month, d_day, d_hour = year, month, day + 1, 0
    else:
        d_year, d_month, d_day, d_hour = year, month, day, hour
    dd = [d_year, d_month, d_day, d_hour]
    cdate = fromSolar(dd[0], dd[1], dd[2])
    yTG,mTG,dTG,hTG = "{}{}".format(tian_gan[cdate.getYearGZ().tg], di_zhi[cdate.getYearGZ().dz]), "{}{}".format(tian_gan[cdate.getMonthGZ().tg],di_zhi[cdate.getMonthGZ().dz]), "{}{}".format(tian_gan[cdate.getDayGZ().tg], di_zhi[cdate.getDayGZ().dz]), "{}{}".format(tian_gan[cdate.getHourGZ(dd[3]).tg], di_zhi[cdate.getHourGZ(dd[3]).dz])
    if year < 1900:
        mTG1 = find_lunar_month(yTG).get(lunar_date_d(year, month, day).get("月"))
    else:
        mTG1 = mTG
    hTG1 = find_lunar_hour(dTG).get(hTG[1])
    return [yTG, mTG1, dTG, hTG1]
#金函玉鏡
def gpan(year, month, day, hour, minute):
    j_q = jieqi.jq(year,
                month,
                day,
                hour,
                minute)
    dgz = gangzhi(year,
                     month,
                     day,
                     hour,
                     minute)[2]
    dh = multi_key_dict_get({tuple(new_list(jieqi.jieqi_name, "冬至")[0:12]):"冬至",
                             tuple(new_list(jieqi.jieqi_name, "夏至")[0:12]):"夏至"},j_q)
    eg = "坎坤震巽乾兌艮離"
    eight_gua = list("坎坤震巽中乾兌艮離")
    clockwise_eightgua = list("坎艮震巽離坤兌乾")
    door_r = list("休生傷杜景死驚開")
    yy = {"冬至":"陽遁", "夏至":"陰遁"}.get(dh)
    ty_doors = {"冬至": dict(zip(jiazi(),itertools.cycle(list("艮離坎坤震巽中乾兌")))), 
            "夏至": dict(zip(jiazi(),itertools.cycle(list("坤坎離艮兌乾中巽震"))))}
    gong = ty_doors.get(dh).get(dgz)
    rotate_order = {"陽遁":eight_gua, "陰遁":list(reversed(eight_gua))}.get(yy)
    a_gong = new_list(rotate_order, gong)
    star_pai = dict(zip(a_gong, golden_d))
    triple_list = list(map(lambda x: x + x + x, list(range(0,21))))
    b = list(starmap(lambda start, end: tuple(jiazi()[start:end]),  zip(triple_list[:-1], triple_list[1:])))
    rest_door_settings = {"陽遁":dict(zip(b, itertools.cycle(eg))),
                          "陰遁":dict(zip(b, itertools.cycle(list(reversed(eg)))))}.get(yy)
    rest = multi_key_dict_get(rest_door_settings, dgz)
    the_doors = {"陽遁": dict(zip(new_list(clockwise_eightgua, rest), door_r)), 
                 "陰遁": dict(zip(new_list(list(reversed(clockwise_eightgua)), rest), door_r))}.get(yy)
    return {"門":the_doors, "星":star_pai}

def gpan1(year, month, day, hour, minute):
    d = gpan(year, month, day, hour, minute)
    pan_eg = new_list( list("坎艮震巽離坤兌乾"), "離")
    door = [d.get("門").get(i) for i in pan_eg]
    star = [d.get("星").get(i) for i in pan_eg]
    middle = ["中",d.get("星").get("中")]
    return [middle, [[a, b, f'{c}門'] for a, b, c in zip(pan_eg, star, door)]]

#換算干支
def gangzhi(year, month, day, hour, minute):
    if year == 0:
        return ["無效"]
    if year < 0:
        year = year + 1 
    if hour == 23:
        d_year, d_month, d_day, d_hour = year, month, day + 1, 0
    else:
        d_year, d_month, d_day, d_hour = year, month, day, hour
    dd = [d_year, d_month, d_day, d_hour]
    cdate = fromSolar(dd[0], dd[1], dd[2])
    yTG,mTG,dTG,hTG = "{}{}".format(tian_gan[cdate.getYearGZ().tg], di_zhi[cdate.getYearGZ().dz]), "{}{}".format(tian_gan[cdate.getMonthGZ().tg],di_zhi[cdate.getMonthGZ().dz]), "{}{}".format(tian_gan[cdate.getDayGZ().tg], di_zhi[cdate.getDayGZ().dz]), "{}{}".format(tian_gan[cdate.getHourGZ(dd[3]).tg], di_zhi[cdate.getHourGZ(dd[3]).dz])
    if year < 1900:
        mTG1 = find_lunar_month(yTG).get(lunar_date_d(year, month, day).get("月"))
    else:
        mTG1 = mTG
    hTG1 = find_lunar_hour(dTG).get(hTG[1])
    zi = gangzhi1(year, month, day, 0, 0)[3]
    hourminute = str(hour)+":"+str(minute)
    gangzhi_minute = minutes_jiazi_d(zi).get(hourminute)
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
#五狗遁，起子時
def find_lunar_minute(hour):
    fivedogs = {
    tuple(list('甲己')):'甲戌',
    tuple(list('乙庚')):'丙戌',
    tuple(list('丙辛')):'戊戌',
    tuple(list('丁壬')):'庚戌',
    tuple(list('戊癸')):'壬戌'
    }
    if multi_key_dict_get(fivedogs, hour[0]) == None:
        result = multi_key_dict_get(fivedogs, hour[1])
    else:
        result = multi_key_dict_get(fivedogs, hour[0])
    return new_list(jiazi(), result)
#分干支
def minutes_jiazi_d(hour):
    t = [f"{h}:{m}" for h in range(24) for m in range(60)]
    minutelist = dict(zip(t, cycle(repeat_list(1, find_lunar_minute(hour)))))
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
#分計五子元
#五子元局數
def min_five_zi_yuan(taiyiju, gangzhi):
    if gangzhi[1] == "戌":
        gz = gangzhi.replace("戌","申")
    if gangzhi[1] == "子":
        gz = gangzhi.replace("子","戌")
    if gangzhi[1] == "丑":
        gz = gangzhi.replace("丑","亥")
    if gangzhi[1] == "寅":
        gz = gangzhi.replace("寅","子") 
    if gangzhi[1] == "卯":
        gz = gangzhi.replace("卯","丑") 
    if gangzhi[1] == "辰":
        gz = gangzhi.replace("辰","寅")
    if gangzhi[1] == "巳":
        gz = gangzhi.replace("巳","卯")
    if gangzhi[1] == "午":
        gz = gangzhi.replace("午","辰")
    if gangzhi[1] == "未":
        gz = gangzhi.replace("未","巳")
    if gangzhi[1] == "申":
        gz = gangzhi.replace("申","午")
    if gangzhi[1] == "酉":
        gz = gangzhi.replace("酉","未")
    #if gangzhi[1] == "戌":
    #    gz = gangzhi.replace("午","辰")
    if gangzhi[1] == "亥":
        gz = gangzhi.replace("亥","酉")
    a =["甲子","丙子","戊子","庚子","壬子"]
    b = [1,73,145,217,289]
    c = [(new_list(jiazi(),i)*2)[0:72] for  i in a]
    d = [new_list(list(range(i, i+72)), i) for i in b]
    #return dict(zip([c[i][taiyiju-2] for i in range(0,5)], [d[i][taiyiju-1] for i in range(0,5)]))
    return an2cn(dict(zip([c[i][taiyiju-2] for i in range(0,5)], [d[i][taiyiju-1] for i in range(0,5)])).get(gz)) + "局"

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
    elif year < y[idx] and year> 0:
        year = year - y[idx-1] 
        cyear = an2cn(year+1)
        pn = "{}{}年".format(preiodname[idx-1],cyear)
        kn = "{}{}{}".format(period[idx-1], king[idx-1], king_realname[idx-1])
        return  "{} {}".format(kn, pn)
    elif year < 0:
        year = year - y[idx-1] 
        cyear = an2cn(year+2)
        pn = "{}{}年".format(preiodname[idx-1],cyear)
        kn = "{}{}{}".format(period[idx-1], king[idx-1], king_realname[idx-1])
        return  "{} {}".format(kn, pn)
#%% 二十八宿
#推二十八星宿
def starhouse(year, month, day, hour, minute):
    numlist = [13,9,16,5,5,17,10,24,7,11,25,18,17,10,17,13,14,11,16,1,9,30,3,14,7,19,19,18]
    alljq = jieqi.jieqi_name
    njq = new_list(alljq, "冬至")
    gensulist =  list(itertools.chain.from_iterable([[su[i]]*numlist[i] for i in range(0,28)]))
    jqsulist = [["斗", 9],["斗",24] ,["女", 8],["危",2],["室", 1],["壁",1] ,["奎", 4],["婁",2] ,["胃", 4],["昴",4] ,["畢", 8],["參",6] ,["井", 1],["井", 27],["柳",8] ,["張", 3],["翼",1] ,["翼", 16],["軫",13] ,["角", 9],["房", 1],["氐",2] ,["尾", 6],["箕",24]]
    njq_list = dict(zip(njq, jqsulist))
    currentjq = jieqi.jq(year, month, day, hour, minute)
    distance_to_cjq = jieqi.distancejq(year, month, day, hour, minute, currentjq)
    num = gensulist.index(njq_list.get(currentjq)[0]) + njq_list.get(currentjq)[1] + distance_to_cjq
    new_num = num -360
    if new_num > 360:
        new_num = new_num -360
    if num >360:
        return new_list(gensulist, njq_list.get(currentjq)[0])[new_num]
    else:
        return gensulist[num]
#%% 太乙十精
#五行
def wuxing(taiyi_acumyear):
    #f = self.accnum(ji_style, taiyi_acumyear) // 5
    f = taiyi_acumyear % 5
    if f == 0:
       fv = divide(taiyi_acumyear, 5)
       return dict(zip(list(range(1,17)),gong1)).get(fv % 5) 
    else:
       return dict(zip(range(1,6), list("乾子艮巽坤"))).get(int(f))
#帝符
def kingfu(taiyi_acumyear):
    #f = self.accnum(ji_style, taiyi_acumyear) % 20
    kingfu_num = taiyi_acumyear % 20
    if kingfu_num == 0:
       kingfu_num = divide(taiyi_acumyear, 20)
       kingfu_num = kingfu_num % 20
    if kingfu_num > 16:
        kingfu_num = kingfu_num - 16
    return dict(zip(range(1,17), new_list(gong1, "戌"))).get(int(kingfu_num))
#天皇
def tian_wang(taiyi_acumyear):
    tw = taiyi_acumyear % 20
    if tw == 0:
        tw = divide(taiyi_acumyear, 20)
        tw_v = tw % 20 
        if tw_v > 16:
            tw_v = tw_v - 16
        return dict(zip(list(range(1,17)),gong1)).get(tw_v)
    else:
       return dict(zip(list(range(1,17)),new_list(gong1, "申"))).get(tw)
#天時
def tian_shi(taiyi_acumyear):
    tw = taiyi_acumyear % 12
    if tw == 0:
       tw = divide(taiyi_acumyear, 12)
       tw_v = tw % 12
       if tw_v > 16:
           tw_v = tw_v - 16
       return dict(zip(list(range(1,17)),gong1)).get(tw_v)
    else:
       return dict(zip(list(range(1,17)),new_list(gong1, "寅"))).get(tw)
#太尊
def taijun(taiyi_acumyear):
    f = taiyi_acumyear % 4
    if f == 0:
       f = divide(taiyi_acumyear, 4)
       f_v = f % 4
       if f_v > 16:
           f_v = f_v - 16
       return dict(zip(list(range(1,17)),gong1)).get(f_v)
    else:
       return dict(zip(range(1,5), list("子午卯酉"))).get(int(f))
#飛鳥
def flybird(taiyi_acumyear):
    f = taiyi_acumyear % 8
    if f == 0:
       return "坤"
    else:
       return dict(zip(range(1,9), [1,8,3,4,9,2,7,6])).get(int(f))

#三風
def threewind(taiyi_acumyear):
    #f = self.accnum(ji_style, taiyi_acumyear) % 9
    f = taiyi_acumyear % 9
    if f == 0:
       fv = divide(taiyi_acumyear, 9)
       return fv % 9 
    else:
       if f % 9 == 0:
           return dict(zip(range(1,9), [7,2,6,1,3,9,4,8])).get(int(f/9))
       elif f % 9 != 0:
           return dict(zip(range(1,9), [7,2,6,1,3,9,4,8])).get(int(f % 9))
    
#五風
def fivewind(taiyi_acumyear):
    f = taiyi_acumyear % 29
    if f == 0:
       fv = divide(taiyi_acumyear, 29)
       return fv % 29 
    else:
       if f % 9 == 0:
           return dict(zip(range(1,10), [1,3,5,7,9,2,4,6,8])).get(int(f / 9 ))
       elif f % 9 != 0:
           return dict(zip(range(1,10), [1,3,5,7,9,2,4,6,8])).get(int(f % 9 ))
#八風
def eightwind(taiyi_acumyear):
    f = taiyi_acumyear % 9
    if f == 0:    
       fv = divide(taiyi_acumyear, 9)
       return fv % 9
    else:
       if f % 9 == 0:
          return dict(zip(range(1,9), [2,3,4,6,7,8,9,1])).get(int(f / 9 ))
       elif f % 9 != 0:
          return dict(zip(range(1,9), [2,3,4,6,7,8,9,1])).get(int(f % 9 ))
#五福
def wufu(taiyi_acumyear):
    f = (taiyi_acumyear + 250) % 225 % 45
    #f = int(self.accnum(ji_style, taiyi_acumyear) + 250) % 225 / 45
    fv =  f % 5
    if fv == None:
        return dict(zip(range(1,6), list("13975"))).get(int(f/5))
    if fv != None and fv !=0:
        return fv
    if fv == 0:
        return 5
    
    
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
    big_yo = (taiyi_acumyear + 34) % 288
    if big_yo < 36:
        big_yo = big_yo
    if big_yo > 36:
        big_yo = big_yo / 36
    if big_yo < 6:
        big_yo = 6
    byv = dict(zip([7,8,9,1,2,3,4,6],range(1,9))).get(int(big_yo))
    return byv
#小游
def smyo(taiyi_acumyear):
    small_yo = taiyi_acumyear % 360
    sm = 0  # Initialize sm here

    if small_yo < 24:
        sm = small_yo % 3
    elif small_yo > 24:
        sm = small_yo % 24
        if small_yo > 10:
            sm = small_yo - 9

        if sm % 3 != 0:
            return dict(zip([1, 2, 3, 4, 6, 7, 8, 9], range(1, 9))).get(int(sm % 3), 1)
        elif sm % 3 == 0:
            a = dict(zip([1, 2, 3, 4, 6, 7, 8, 9], range(1, 9))).get(int(sm / 3))
            return a if a is not None else 1

    return dict(zip([1, 2, 3, 4, 6, 7, 8, 9], range(1, 9))).get(int(sm % 3), 1)

     
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

if __name__ == '__main__':
    print(num2gong_life(bigyo(10155909)))
    print(gpan(2024,8,23,10,7))
    print(gpan1(2024,8,23,10,7))

# ======================  太乙統宗寶鑑 卷十：三旗行宮 + 九宮貴神  ======================
# 以下函式依《太乙統宗寶鑑》卷十「明太乙三旗行宮術」「明太乙九宮貴神術」原文明載之公式實作。
# 三旗者：太歲青龍旗、太陰黑旗、害氣赤旗，乃太乙使星，考治下土以行其罰。
# 九宮貴神者：太乙、攝提、軒轅、招搖、天符、青龍、咸池、太陰、天乙，飛行九宮以占吉凶。

# 洛書九宮名（一坎、二坤、三震、四巽、五中、六乾、七兌、八艮、九離）
_LUOSHU_GONG = {1: "坎", 2: "坤", 3: "震", 4: "巽", 5: "中", 6: "乾", 7: "兌", 8: "艮", 9: "離"}

# 九宮貴神河圖數序：一太乙、二攝提、三軒轅、四招搖、五天符、六青龍、七咸池、八太陰、九天乙
_NINE_GODS = {1: "太乙", 2: "攝提", 3: "軒轅", 4: "招搖", 5: "天符", 6: "青龍", 7: "咸池", 8: "太陰", 9: "天乙"}

# 排盤八門環僅顯示之貴神簡字（太(乙)、(攝)提、(軒)轅、招(搖)、天(符)、青(龍)、(咸)池、太(陰)、(天)乙）
NINE_GOD_CHART_LABEL = {
    "太乙": "乙",
    "攝提": "攝",
    "軒轅": "軒",
    "招搖": "搖",
    "天符": "符",
    "青龍": "龍",
    "咸池": "咸",
    "太陰": "陰",
    "天乙": "天",
}

# 直事貴神入中宮之序（小周餘一至九所直之貴神河圖數）
# 依原文：餘一太乙、餘二天乙、餘三太陰、餘四咸池、餘五青龍、餘六天符、餘七招搖、餘八軒轅、餘九攝提
_DIRECT_ORDER = [1, 9, 8, 7, 6, 5, 4, 3, 2]

# 四孟之辰（寅巳申亥），害氣赤旗逆行所歷
_SIMENG = ["亥", "申", "巳", "寅"]

# 三旗考治分野災祥（依卷十原文五行方位所主）
_SANQI_OWN = {
    "甲乙": "風雨不調，四時失序",
    "丙丁": "燥旱雷雨傷禾",
    "庚辛": "兵盜嚴霜殺物",
    "壬癸": "水湧五谷不登",
    "戊己": "土工興，傷禾稼",
}


def qinglong_flag(jiyoung):
    """太歲青龍旗所在（依《太乙統宗寶鑑》卷十「求太歲青龍旗所在術」）

    原文：置積年，以紀法六十去之，不盡，又以小周法十二除之，
    餘不盡者，命起亥，順行十二辰次。其神一歲一遷，從亥而子，順行十二辰次。
    """
    dz = list(di_zhi)                       # 子丑寅卯辰巳午未申酉戌亥
    order = new_list(dz, "亥")              # 順行起亥：亥子丑寅卯辰巳午未申酉戌
    idx = (jiyoung % 60) % 12
    flag = order[idx]
    return flag


def taiyin_flag(jiyoung):
    """太陰黑旗所在（依《太乙統宗寶鑑》卷十「求太陰黑旗所在術」）

    原文：置積年加邦盈差二十五，以大周法三百六十除之，不盡，以小周法三十六去之，
    不盡，以行邦率三約之，為入邦以來年數。命起亥邦，三年一移，逆行十二辰次。
    三十六年一周。
    """
    dz = list(di_zhi)
    order = list(reversed(dz))              # 逆行起亥：亥戌酉申未午巳辰卯寅丑子
    r = ((jiyoung + 25) % 360) % 36
    inbang = r // 3                         # 行邦率三約之，入邦以來年數
    flag = order[inbang]
    return flag


def haiqi_flag(jiyoung):
    """害氣赤旗所在（依《太乙統宗寶鑑》卷十「求害氣赤旗所在術」）

    原文：置積年加邦盈差一，以大周法四十除之，不盡，以小周法四去之，
    不盡者，命起亥邦，逆行四孟之辰，一年一移。四年一周。
    """
    r = ((jiyoung + 1) % 40) % 4
    flag = _SIMENG[r]                       # 逆行四孟：亥申巳寅
    return flag


def sanqi(jiyoung):
    """太乙三旗行宮合會（青龍旗、太陰黑旗、害氣赤旗）

    依卷十「明太乙三旗行宮合會術」：三旗乃太乙之使星，考治下土以行其罰。
    二神會合災緩，三神會合災急。忌與太乙合會，為殃深重大，則除舊布新。
    """
    ql = qinglong_flag(jiyoung)
    ty = taiyin_flag(jiyoung)
    hq = haiqi_flag(jiyoung)
    flags = [ql, ty, hq]
    # 會合程度：三旗同辰為三會(災急)，二旗同辰為二會(災緩)
    distinct = set(flags)
    meet = "三神會合，災急，除舊布新" if len(distinct) == 1 else (
        "二神會合，災緩" if len(distinct) == 2 else "三旗各居一方，無會合")
    return {
        "太歲青龍旗": ql,
        "太陰黑旗": ty,
        "害氣赤旗": hq,
        "會合": meet,
    }


def nine_palace_gods(jiyoung):
    """太乙九宮貴神（依《太乙統宗寶鑑》卷十「求九宮太乙貴神所在術」）

    原文：置周紀餘，加宮盈差三，以小周法九去之，不盡，命起一宮，逆行九宮，
    筭外即得九宮太乙貴神所在，而為直事者也。
    直事貴神入中宮，餘八神飛出，依次順行河圖九宮，即得鈎宮所臨宮分。
    """
    yu = (jiyoung % 360 + 3) % 9
    if yu == 0:
        yu = 9
    s_num = _DIRECT_ORDER[yu - 1]                 # 直事貴神之河圖數
    offset = (5 - s_num) % 9                       # 鈎宮飛行偏移（直事落中宮五）
    dist = {}
    for n, name in _NINE_GODS.items():
        palace = ((n - 1 + offset) % 9) + 1
        dist[_LUOSHU_GONG[palace]] = name
    return {
        "小周餘": yu,
        "直事貴神": _NINE_GODS[s_num],
        "九宮貴神分布": dist,
    }


# ======================  太乙統宗寶鑑 卷六：太乙九星 + 文昌九星  ======================
# 太乙九星依卷六「明九星行干支造化所主術」：大周九百、小周九十、星周率十，
# 命起天蓬順行九星，算外得直符；六甲之年直符加于年干之宮。
# 文昌九星依卷六「明文昌九星行九宮所主分野術」：大周二千七百、小周二百七十、
# 宮率三十，命起一宮文曲順行，直事再加年干之宮推分野吉凶。

_TAIYI_STARS = ["天蓬", "天芮", "天冲", "天輔", "天禽", "天心", "天柱", "天任", "天英"]
_TAIYI_STAR_INFO = {
    "天蓬": ("招搖", "主撼動不寧、更易之象"),
    "天芮": ("玄戈", "主軍盜賊興廢"),
    "天冲": ("瑤光", "主兵戈殺戮"),
    "天輔": ("闓陽", "主倉廩五谷"),
    "天禽": ("玉衡", "主中央殺伐"),
    "天心": ("權", "主理伐無道"),
    "天柱": ("璣", "主殃禍號令"),
    "天任": ("璇", "主陰刑女主"),
    "天英": ("樞", "主陽德天子"),
}
# 九星定宮（洛書）：一蓬乾、二芮離、三冲艮、四輔震、五禽中、六心兌、七柱坤、八任坎、九英巽
_STAR_FIXED_GONG = {"天蓬": 1, "天芮": 2, "天冲": 3, "天輔": 4, "天禽": 5,
                    "天心": 6, "天柱": 7, "天任": 8, "天英": 9}
# 六甲年干加臨之宮（依卷六伏宮例：六乙加九宮、六丙加八宮…）
_GAN_STAR_GONG = {"甲": 1, "乙": 9, "丙": 8, "丁": 7, "戊": 1, "己": 2,
                  "庚": 3, "辛": 4, "壬": 5, "癸": 6}

_WENCHANG_STARS = ["文曲", "玄鳳", "明維", "昭搖", "立華", "華明", "玄武", "玄冥", "雄明"]
_WENCHANG_FENYE = {
    "文曲": ("乾", "冀州"), "玄鳳": ("離", "荊州"), "明維": ("艮", "青州"),
    "昭搖": ("震", "徐州"), "立華": ("中", "豫州"), "華明": ("兌", "雍州"),
    "玄武": ("坤", "梁益"), "玄冥": ("坎", "兖州"), "雄明": ("巽", "揚州"),
}
_GAN_WENCHANG_GONG = {"甲": 3, "乙": 4, "丙": 9, "丁": 9, "戊": 5, "己": 5,
                      "庚": 7, "辛": 6, "壬": 5, "癸": 8}


def taiyi_nine_stars(jiyoung, year_gan=None):
    """太乙九星直符與分布（依《太乙統宗寶鑑》卷六「明九星行干支造化所主術」）

    原文：置積年，以九星大周法九百除之不盡，再以小周法九十除之不盡為星周；
    餘以星周率十約之為星宮之數，不盡為入星宮以來年數；命起天蓬順行九星。
    六甲之年直符就加于年干之宮（伏宮），餘星依次順行分布九宮。
    """
    yu = (jiyoung % 900) % 90
    if yu == 0:
        yu = 90
    star_idx = (yu - 1) // 10
    years_in = yu % 10 or 10
    zhifu = _TAIYI_STARS[star_idx]
    alias, desc = _TAIYI_STAR_INFO[zhifu]
    base_gong = _GAN_STAR_GONG.get(year_gan, _STAR_FIXED_GONG[zhifu]) if year_gan else _STAR_FIXED_GONG[zhifu]
    dist = {}
    for i, star in enumerate(_TAIYI_STARS):
        gong = ((base_gong - 1 + i) % 9) + 1
        dist[_LUOSHU_GONG[gong]] = star
    return {
        "星周餘": yu if yu < 90 else 0,
        "直符九星": zhifu,
        "入星宮年數": years_in,
        "九星分布": dist,
        "直符所主": f"{alias}——{desc}",
    }


def wenchang_nine_stars(jiyoung, year_gan=None):
    """文昌九星直事與分野（依《太乙統宗寶鑑》卷六「明文昌九星行九宮所主分野術」）

    原文：置積年，以文昌大周法二千七百除之不盡，以小周法二百七十去之不盡為宮周餘；
    以宮率三十約之為宮數，不盡為入宮以來年數；命起一宮文曲順行，直事再加年干之宮。
    """
    yu = (jiyoung % 2700) % 270
    if yu == 0:
        yu = 270
    direct_idx = (yu - 1) // 30
    years_in = yu % 30 or 30
    direct_star = _WENCHANG_STARS[direct_idx]
    dist = {}
    for i, star in enumerate(_WENCHANG_STARS):
        gong = ((direct_idx + i) % 9) + 1
        dist[_WENCHANG_FENYE[star][0]] = star
    if year_gan:
        gong_name = _LUOSHU_GONG[_GAN_WENCHANG_GONG.get(year_gan, 1)]
        fenye = _WENCHANG_FENYE[direct_star][1]
        lin = f"{gong_name}——{fenye}"
    else:
        lin = f"{_WENCHANG_FENYE[direct_star][0]}——{_WENCHANG_FENYE[direct_star][1]}"
    return {
        "宮周餘": yu if yu < 270 else 0,
        "直事文昌星": direct_star,
        "入宮年數": years_in,
        "文昌九星分布": dist,
        "臨宮分野": lin,
    }


# ======================  太乙統宗寶鑑 卷三／卷十：五運六氣 + 五音之數  ======================
# 五運六氣依卷三「明太乙統行五運六氣術」、卷十「明太乙歲會五運六氣術」：
# 以年干定五運、年支定司天在泉，察歲會天符；天目文昌為主氣、始擊為客氣。
# 五音之數依卷三「明五音以推災變術」「明太乙五音之元術」：
# 一二宮、三四徵、五六羽、七八商、九十角；太乙所到之宮及日時支別五音所屬。

_WUYUN_GAN = {
    tuple("甲己"): ("土運", "宮"),
    tuple("乙庚"): ("金運", "商"),
    tuple("丙辛"): ("水運", "羽"),
    tuple("丁壬"): ("木運", "角"),
    tuple("戊癸"): ("火運", "徵"),
}
_WUYUN_CHEN = {
    "木運": ["卯"], "火運": ["午"], "土運": ["辰", "戌", "丑", "未"],
    "金運": ["酉"], "水運": ["子"],
}
_SITIAN = {
    "子": ("少陰", "熱氣"), "午": ("少陰", "熱氣"),
    "丑": ("太陰", "濕氣"), "未": ("太陰", "濕氣"),
    "巳": ("厥陰", "風氣"), "亥": ("厥陰", "風氣"),
    "寅": ("少陽", "相火"), "申": ("少陽", "相火"),
    "卯": ("陽明", "燥氣"), "酉": ("陽明", "燥氣"),
    "辰": ("太陽", "寒氣"), "戌": ("太陽", "寒氣"),
}
_WUYUN_UPPER = {
    "木運": "厥陰", "火運": "少陰", "土運": "太陰", "金運": "陽明", "水運": "太陽",
}
_YANG_GAN = set("甲丙戊庚壬")

_WUYIN_DIGIT = {
    (1, 2): ("宮", "土", "人君", "占在人君；和則君有福慶，不和囚迫則天變君災"),
    (3, 4): ("徵", "火", "宗廟", "占在宗廟；和則飾神主，不和則宗廟災變"),
    (5, 6): ("羽", "水", "后妃", "占在后妃；和則吉，不和則女主擅權"),
    (7, 8): ("商", "金", "子孫", "占在子孫；和無掩迫則太子成立"),
    (9, 10): ("角", "木", "疾病", "占在疾病；和無囚迫則民安物阜"),
}
_WUYIN_YUAN = {
    "宮": ("天一地二", "土", "人君"),
    "羽": ("天五地六", "水", "后妃"),
    "角": ("天九地十", "木", "疾病"),
    "徵": ("天三地四", "火", "宗廟"),
    "商": ("天七地八", "金", "子孫"),
}
_ZHI_WUYIN = {
    "子": "宮", "午": "宮",
    "丑": "徵", "未": "徵", "寅": "徵", "申": "徵",
    "卯": "羽", "酉": "羽",
    "辰": "商", "戌": "商",
    "巳": "角", "亥": "角",
}
_GONG_REP_ZHI = {
    "乾": "亥", "午": "午", "艮": "寅", "卯": "卯", "中": "辰",
    "酉": "酉", "坤": "未", "子": "子", "巽": "巳",
}


def _wuyun_of_gan(gan):
    for stems, (yun, yin) in _WUYUN_GAN.items():
        if gan in stems:
            return yun, yin
    return None, None


def _cal_digit(num):
    if num is None or num <= 0:
        return 1
    d = int(num) % 10
    return 10 if d == 0 else d


def wuyin_from_calc(num):
    """由算數推五音（依卷三：一二宮、三四徵、五六羽、七八商、九十角）。"""
    d = _cal_digit(num)
    for pair, (yin, wx, subject, desc) in _WUYIN_DIGIT.items():
        if d in pair:
            yuan = _WUYIN_YUAN[yin]
            return {
                "算數": int(num),
                "數位": d,
                "音": yin,
                "比音": d == pair[1],
                "五行": wx,
                "所主": subject,
                "河圖元": yuan[0],
                "元象": yuan[2],
                "斷語": desc,
            }
    return {}


def wuyin_from_zhi(zhi):
    """由地支推五音（依卷十五：子午宮、丑未寅申徵、卯酉羽、辰戌商、巳亥角）。"""
    yin = _ZHI_WUYIN.get(zhi)
    if not yin:
        return {}
    yuan = _WUYIN_YUAN[yin]
    return {"支": zhi, "音": yin, "五行": yuan[1], "河圖元": yuan[0], "元象": yuan[2]}


def wuyin_yuan():
    """太乙五音之元（卷三「明太乙五音之元術」河圖數序）。"""
    return {k: {"河圖": v[0], "五行": v[1], "所象": v[2]} for k, v in _WUYIN_YUAN.items()}


def wuyun_liuqi(year_gan, year_zhi, ty_gong=None, skyeyes=None, shiji=None):
    """太乙統行五運六氣（卷三、卷十）

    以年干推五運、年支推司天在泉，察歲會天符；可附主氣（文昌）客氣（始擊）。
    """
    yun, yin = _wuyun_of_gan(year_gan)
    sitian, hua = _SITIAN.get(year_zhi, ("", ""))
    zhi_order = list(di_zhi)
    zaiquan_idx = (zhi_order.index(year_zhi) + 6) % 12
    zaiquan = zhi_order[zaiquan_idx]
    zaiquan_name, zaiquan_hua = _SITIAN.get(zaiquan, ("", ""))
    tai_over = year_gan in _YANG_GAN

    hui = []
    if yun and sitian:
        if yun == "火運" and sitian == "少陰" and year_zhi == "午":
            hui.append("三合為治（火運少陰臨午）")
        if yun == "土運" and sitian == "太陰" and year_zhi in "丑未":
            hui.append("三合為治（土運太陰臨土旺之辰）")
        if yun == "金運" and sitian == "陽明" and year_zhi == "酉":
            hui.append("三合為治（金運陽明臨酉）")
        if year_zhi in _WUYUN_CHEN.get(yun, []):
            hui.append(f"歲會（{yun}氣值年辰{year_zhi}）")
        if _WUYUN_UPPER.get(yun) == sitian:
            label = "太乙天符" if tai_over else "太乙歲會"
            hui.append(f"{label}（{yun}上見{sitian}）")

    ty_wuyin = {}
    if ty_gong:
        rep = _GONG_REP_ZHI.get(ty_gong if isinstance(ty_gong, str) else num2gong(ty_gong))
        if rep:
            ty_wuyin = wuyin_from_zhi(rep)
            ty_wuyin["太乙宮"] = ty_gong if isinstance(ty_gong, str) else num2gong(ty_gong)

    result = {
        "年干": year_gan,
        "年支": year_zhi,
        "五運": yun,
        "五運音": yin,
        "太過不及": "太過" if tai_over else "不及",
        "司天": sitian,
        "司天化": hua,
        "在泉": zaiquan_name,
        "在泉化": zaiquan_hua,
        "五運所乘": _WUYUN_CHEN.get(yun, []),
        "歲會天符": hui or ["無特殊歲會"],
        "太乙宮五音": ty_wuyin,
    }
    if skyeyes:
        result["主氣"] = f"天目文昌在{skyeyes}（主氣，萬世不易）"
    if shiji:
        result["客氣"] = f"始擊在{shiji}（客氣，隨歲遷移）"
    return result


_PALACE_YANG = frozenset({1, 2, 3, 4, 6, 9})
_WUXING_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}


def wuyun_tianmu_hehui(year_gan, year_zhi, ty, skyeyes, shiji,
                       ty_gong=None, wuyun=None):
    """運氣與太乙天目合會（卷十）：主氣天目、客氣始擊，察掩格生剋。"""
    ty_n = ty if isinstance(ty, int) else gong.get(ty)
    ty_name = num2gong(ty_n) if ty_n else ""
    wq = wuyun or wuyun_liuqi(year_gan, year_zhi, ty_gong or ty_name, skyeyes, shiji)
    sky_g = gong2.get(skyeyes) if skyeyes else None
    shi_g = gong2.get(shiji) if shiji else None
    hehui = []
    if sky_g and ty_n:
        if sky_g == ty_n:
            hehui.append("天目文昌犯太乙宮為掩")
        elif sky_g == _TY_OPP_GONG.get(ty_n):
            hehui.append("天目文昌對太乙為格")
    if sky_g and shi_g:
        mw = _PALACE_WX.get(sky_g, "")
        kw = _PALACE_WX.get(shi_g, "")
        if mw and kw:
            if _WUXING_SHENG.get(mw) == kw:
                hehui.append(f"主氣生客氣（{mw}生{kw}，順勢）")
            elif _WUXING_SHENG.get(kw) == mw:
                hehui.append(f"客氣生主氣（{kw}生{mw}）")
            elif _WUXING_KE.get(mw) == kw:
                hehui.append(f"主氣剋客氣（{mw}剋{kw}）")
            elif _WUXING_KE.get(kw) == mw:
                hehui.append(f"客氣剋主氣（{kw}剋{mw}，逆勢）")
    yang_gan = year_gan in _YANG_GAN
    if ty_n:
        if yang_gan and ty_n in _PALACE_YANG:
            hehui.append("陽干臨陽宮，其氣有餘")
        elif not yang_gan and ty_n not in _PALACE_YANG:
            hehui.append("陰干臨陰宮，其氣不足")
    return {
        **wq,
        "天目": skyeyes,
        "始擊": shiji,
        "太乙宮": ty_name,
        "主氣宮": num2gong(sky_g) if sky_g else "",
        "客氣宮": num2gong(shi_g) if shi_g else "",
        "天目合會": hehui or ["主客氣調，無特殊掩格"],
        "要訣": "天目武德順行為主氣，始擊對宮為客氣；掩格之年災發",
    }


def wuyin_shu(home_cal, away_cal, set_cal=None, ty_gong=None, day_zhi=None, hour_zhi=None):
    """五音之數綜合（卷三「明五音以推災變術」+「明太乙五音之元術」）

    由主客定算推休咎，由太乙宮、日時支推五音所屬。
    """
    result = {
        "五音之元": wuyin_yuan(),
        "主算五音": wuyin_from_calc(home_cal),
        "客算五音": wuyin_from_calc(away_cal),
    }
    if set_cal is not None:
        result["定算五音"] = wuyin_from_calc(set_cal)
    if ty_gong:
        gname = ty_gong if isinstance(ty_gong, str) else num2gong(ty_gong)
        rep = _GONG_REP_ZHI.get(gname)
        if rep:
            result["太乙五音"] = {**wuyin_from_zhi(rep), "太乙宮": gname}
    if day_zhi:
        result["日五音"] = wuyin_from_zhi(day_zhi)
    if hour_zhi:
        result["時五音"] = wuyin_from_zhi(hour_zhi)
    return result


# ======================  太乙統宗寶鑑 卷十五：軍事應用  ======================
# 奇兵伏兵、五陣八陣、五音風、安營置陣、風從八卦、雲氣逆順等。

_EIGHT_ORDER = [1, 2, 3, 4, 6, 7, 8, 9]
_PALACE_WX = {1: "金", 2: "火", 3: "木", 4: "木", 6: "金", 7: "土", 8: "土", 9: "火"}
_WUXING_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
_WUYIN_WX = {"宮": "土", "徵": "火", "羽": "水", "商": "金", "角": "木"}
_WUYIN_SHENG = {"宮": "商", "商": "角", "角": "徵", "徵": "羽", "羽": "宮"}
_ZHEN_RULES = [
    ((1, 8), ("曲陣", "黑旗", "北方")),
    ((3, 7), ("直陣", "青旗", "東方")),
    ((4, 9), ("銳陣", "赤旗", "南方")),
    ((2, 5), ("圓陣", "黃旗", "中央")),
    ((6,), ("方陣", "白旗", "西方")),
]
_CHUBING_XIANG = {
    1: "西北", 2: "正南", 3: "東北", 4: "正東",
    6: "正西", 7: "西南", 8: "正北", 9: "東南",
}
_BAZHEN = ["天", "地", "風", "雲", "龍", "虎", "鳥", "蛇"]
_FENG_BAGUA = {
    1: ("西北乾", "利客，宜先奔為勝"),
    8: ("正北坎", "利客，宜先奔為勝"),
    3: ("東北艮", "利客，宜先奔為勝"),
    4: ("正東震", "利主，宜後奔為勝"),
    9: ("東南巽", "利主，宜後奔為勝"),
    2: ("正南離", "利主，宜後奔為勝"),
    7: ("西南坤", "主客兩不利"),
    6: ("正西兌", "客有伏兵，主宜設備"),
}
_WIND_DIR_YIN = {
    "子": "宮", "午": "宮",
    "丑": "徵", "未": "徵", "寅": "徵", "申": "徵",
    "卯": "羽", "酉": "羽",
    "辰": "商", "戌": "商",
    "巳": "角", "亥": "角",
}
_FENG_JIANG = {
    "宮": "寬和而有信",
    "商": "威猛而好殺",
    "角": "仁恕不可詐欺",
    "徵": "猛烈難與爭鋒",
    "羽": "貪暴多奸詐",
}


def _gong_of_chen(ch):
    return gong2.get(ch)


def _ty_neighbors(ty):
    idx = _EIGHT_ORDER.index(ty)
    return {
        "前一宮": _EIGHT_ORDER[(idx + 1) % 8],
        "後一宮": _EIGHT_ORDER[(idx - 1) % 8],
    }


def _realm_of_gong(ty, g):
    """依太乙宮分內外（卷十七間諜術、tutorial 例）。"""
    if g == 5 or g is None:
        return "中"
    outer_map = {
        1: {6, 7, 2}, 2: {3, 6, 7}, 3: {2, 4, 9}, 4: {3, 9, 2},
        6: {7, 8, 4}, 7: {6, 8, 2}, 8: {6, 7, 4}, 9: {2, 4, 3},
    }
    inner_map = {
        1: {8, 3, 4, 9}, 2: {8, 4, 1, 9}, 3: {6, 7, 8, 1}, 4: {6, 7, 8, 1},
        6: {2, 3, 9, 1}, 7: {3, 4, 1, 9}, 8: {2, 3, 9, 1}, 9: {6, 7, 8, 1},
    }
    if g in outer_map.get(ty, set()):
        return "外"
    if g in inner_map.get(ty, set()):
        return "內"
    if g == ty:
        return "同宮"
    nb = _ty_neighbors(ty)
    if g == nb["前一宮"]:
        return "外"
    if g == nb["後一宮"]:
        return "內"
    return "中"


def _zhen_from_calc(num):
    d = _cal_digit(num)
    for pair, info in _ZHEN_RULES:
        if d in pair:
            return {"算數": int(num), "數位": d, "陣型": info[0], "旗色": info[1], "方位": info[2]}
    return {"算數": int(num), "數位": d, "陣型": "依地形置陣", "旗色": "—", "方位": "—"}


def qibing_fubing(ty, skyeyes, shiji, home_cal, away_cal, geju=None):
    """奇兵伏兵（卷十五「明奇兵伏兵之術」「明出兵戰陣所利術」）"""
    wc_g = _gong_of_chen(skyeyes)
    sj_g = _gong_of_chen(shiji)
    wc_name = num2gong(wc_g) if wc_g else skyeyes
    sj_name = num2gong(sj_g) if sj_g else shiji
    result = {
        "主奇兵位": f"{wc_name}（天目文昌大殺之地）",
        "客奇兵位": f"{sj_name}（始擊大殺之地）",
        "奇兵比例": "百人取三十為奇",
        "奇兵要訣": "居高去敵三里，鼓譟而發，候敵人之便",
    }
    yanpo = False
    if geju:
        yanpo = any("掩" in k or "迫" in k for k in geju)
    if yanpo:
        result["伏兵"] = "掩迫之時，宜隱伏竊發（利申酉戌時）"
    else:
        result["伏兵"] = "待掩迫之時方利設伏"
    d_h = _cal_digit(home_cal)
    d_a = _cal_digit(away_cal)
    if d_h in (11, 21, 31) or d_a in (11, 21, 31):
        result["伏形"] = "羹得單一十一二十一三十一之時，宜伏于山林溝澗"
    return result


def wuzhen_bazhen(home_cal, away_cal):
    """五陣置旗與八陣（卷十五「明太乙置陣斉旗術」「三五八陣之原」）"""
    return {
        "主陣旗": _zhen_from_calc(home_cal),
        "客陣旗": _zhen_from_calc(away_cal),
        "八陣": _BAZHEN,
        "八陣要訣": "起于五而終于八，握機居中，四正四奇分陣",
        "陳兵出鄉": {
            "主": _CHUBING_XIANG.get(_cal_digit(home_cal), "—"),
            "客": _CHUBING_XIANG.get(_cal_digit(away_cal), "—"),
        },
    }


def wuyin_feng(day_zhi, hour_zhi=None, wind_dir_zhi=None):
    """五音風以知盛衰（卷十五）+ 觀風察將"""
    day_yin = wuyin_from_zhi(day_zhi)
    if not day_yin:
        return {}
    result = {"日五音": day_yin}
    if hour_zhi:
        result["時五音"] = wuyin_from_zhi(hour_zhi)
    if wind_dir_zhi:
        wind_yin = _WIND_DIR_YIN.get(wind_dir_zhi, "")
        day_tone = day_yin["音"]
        wx_d = _WUYIN_WX[day_tone]
        wx_w = _WUYIN_WX.get(wind_yin, "")
        parent = {v: k for k, v in _WUYIN_SHENG.items()}.get(day_tone)
        child = _WUYIN_SHENG.get(day_tone)
        verdict = []
        if wx_w and _WUXING_KE.get(wx_w) == wx_d:
            verdict.append(f"風從{wind_dir_zhi}（{wind_yin}音）剋日音，客先鋒大勝")
        elif wx_w and _WUXING_KE.get(wx_d) == wx_w:
            verdict.append(f"日音剋風音，出軍當勝")
        elif wind_yin == parent:
            verdict.append("母來翼子，出軍見成功")
        elif wind_yin == child:
            verdict.append("子來扶母，出軍見成功")
        if wind_yin == "商" and wind_dir_zhi in "辰戌":
            verdict.append("鬼風挾剋，有敗將之禍")
        result["風向五音"] = {"支": wind_dir_zhi, "音": wind_yin}
        result["盛衰"] = "；".join(verdict) if verdict else "風勢和緩天色晴明則大捷"
    result["觀風察將"] = {k: v for k, v in _FENG_JIANG.items()}
    return result


def feng_bagua_zhuke(wind_gong=None):
    """風從八卦分主客（卷十五·李淳風）"""
    if wind_gong is None:
        return {"斷語": "兩敵相當，先明八卦方位，次分主客勝負"}
    info = _FENG_BAGUA.get(wind_gong)
    if not info:
        return {}
    return {"風起宮": num2gong(wind_gong), "方位": info[0], "斷語": info[1]}


def yunqi_nishun(home_cal, away_cal, cloud_from_gong=None):
    """雲氣所起逆順（卷十五）"""
    h_d = _cal_digit(home_cal)
    a_d = _cal_digit(away_cal)
    result = {"主算數位": h_d, "客算數位": a_d}
    if cloud_from_gong is not None:
        c_d = _cal_digit(cloud_from_gong)
        if c_d == h_d or c_d == a_d:
            result["雲氣"] = "從算而來為順，戰勝"
        elif abs(c_d - h_d) == 5 or abs(c_d - a_d) == 5:
            result["雲氣"] = "沖算而來為逆，戰負"
        else:
            result["雲氣"] = "雲氣與算不應，和"
    else:
        result["要訣"] = "雲氣從算而來為順，沖算而來為逆"
    return result


def anying_rishi(ty, skyeyes, shiji, geju=None, three_doors=None, five_gens=None):
    """安營置陣取用日時（卷十五）"""
    wc_g = _gong_of_chen(skyeyes)
    sj_g = _gong_of_chen(shiji)
    ty_side = "右" if ty in (1, 8, 3, 4) else "左"
    eyes_side = "左" if wc_g and sj_g and wc_g < sj_g else "右"
    ok = ty_side != eyes_side
    notes = []
    if ok:
        notes.append("太乙與二目陰陽和順")
    if geju:
        if any("掩" in k or "擊" in k for k in geju if "文昌" in k or k == "掩"):
            notes.append("上目有掩擊挾格，不宜安營")
        if any("囚" in k or "關" in k for k in geju if "始擊" in k or "囚" in k):
            notes.append("下目有關囚迫，不宜安營")
        if any("易絕" in str(v) for v in geju.values()):
            ok = False
    if three_doors == "三門具。" and five_gens == "五將發。":
        notes.append("三門具五將發，可宜安營置陣表轅門")
    elif three_doors or five_gens:
        notes.append(f"{three_doors or ''}{five_gens or ''}")
    return {
        "陰陽和順": ok,
        "太乙方位": f"太乙在{ty_side}",
        "二目方位": f"二目在{eyes_side}",
        "斷語": "；".join(notes) if notes else ("可宜安營置陣" if ok else "未合安營之義"),
    }


def jungshi_shengfu(wind_from_back=False, wuyin_sheng=False, cloud_thick=False):
    """出兵軍勢勝負要訣（卷十五·李淳風摘要）"""
    items = []
    if wind_from_back:
        items.append("風從後來人雄壯，必獲全勝")
    if wuyin_sheng:
        items.append("風從五音相生方位來，軍行勝捷")
    if cloud_thick:
        items.append("雲色濃厚風勢微弱，客勝主負")
    if not items:
        items.append("審風雲飛鳥之勢，詳上文而無差")
    return {"軍勢": items}


_CHENGSHEN = {
    1: {
        "行列": "步卒在前、車騎次之、大將居中",
        "行軍": "出門緩悄，不宜躁急鼓譟",
        "祀方": "北方", "帛色": "皂帛", "面向": "西北再拜",
        "咒": "一宮太乙萬神護吾三軍，令敵自滅，莫敢當我",
    },
    2: {
        "行列": "步卒在前、車騎次之、大將居中",
        "行軍": "出門緩悄，不宜躁急",
        "祀方": "正南方", "帛色": "黃帛", "面向": "正南再拜",
        "咒": "二宮太乙萬神護吾三軍，令敵自驚莫敢當我",
    },
    3: {
        "行列": "步卒在前、車騎次之、大將居中",
        "行軍": "出門緩悄，不宜躁急",
        "祀方": "東北方", "帛色": "青帛", "面向": "東北再拜",
        "咒": "三宮太乙萬神護吾三軍，令敵自伏，莫敢當我",
    },
    4: {
        "行列": "步卒在前、車騎次之、大將居中",
        "行軍": "出門緩悄，不宜躁急",
        "祀方": "正東方", "帛色": "赤帛", "面向": "正東再拜",
        "咒": "四宮太乙萬神護吾三軍，令敵自敗，莫敢當我",
    },
    6: {
        "行列": "車騎在前、步卒次之、大將居中",
        "行軍": "鼓譟急行，不宜緩",
        "祀方": "正西方", "帛色": "白帛", "面向": "正西再拜",
        "咒": "六宮太乙萬神護吾三軍，令敵自傷，莫敢當我",
    },
    7: {
        "行列": "車騎在前、步卒次之、大將居中",
        "行軍": "鼓譟急行",
        "祀方": "西南方", "帛色": "白帛", "面向": "西南再拜",
        "咒": "七宮太乙萬神護吾三軍，令敵自懼，莫敢當我",
    },
    8: {
        "行列": "車騎在前、步卒次之、大將居中",
        "行軍": "鼓譟急行",
        "祀方": "正北方", "帛色": "白帛", "面向": "正北再拜",
        "咒": "八宮太乙萬神護吾三軍，令敵自死，莫敢當我",
    },
    9: {
        "行列": "車騎在前、步卒次之、大將居中",
        "行軍": "鼓譟急行",
        "祀方": "東南方", "帛色": "赤帛", "面向": "東南再拜",
        "咒": "九宮太乙萬神護吾三軍，令敵自潰，莫敢當我",
    },
}

_TERRAIN_ZHEN = {
    "後高前下": ("銳陣", "火", "利以進戰潰敵"),
    "前高後下": ("直陣", "木", "利以近守備禦待敵"),
    "左右勢高": ("曲陣", "水", "利以吞敵"),
    "跨斜不便": ("圓陣", "土", "利以堅守"),
    "地高廣平": ("方陣", "金", "利以速戰"),
}

_TERRAIN_BING = [
    ("山林溝壑茂林積石", "步兵之地，車騎二不當一"),
    ("土山平原四向廣野", "車騎之地，步卒十不當一"),
    ("山谷幽澗仰高臨下", "弓弩之地，短兵百不當一"),
    ("兩陣相近平地淺草", "長戰之地，劍盾三不當一"),
    ("蘆葦竹篠草木朦朧", "矛鋋之地，弓矢三不當一"),
]

_WIND_SOUND_JIANG = {
    "宮風": ("宮", "風勢隆隆如車如雷如擊鼓", "寬和而有信"),
    "商風": ("商", "如金石相擊鐘聲雜珮", "威猛而好殺"),
    "角風": ("角", "肅肅習習如動林木", "仁恕不可詐欺"),
    "徵風": ("徵", "如奔馬炎火烈烈", "猛烈難與爭鋒"),
    "羽風": ("羽", "如流水揚波相雜", "貪暴多奸詐"),
}


def chubing_chengshen(home_cal, away_cal):
    """出兵稱神（卷十五「明太乙出兵稱神術」）。"""
    def _one(cal, role):
        d = _cal_digit(cal)
        if d == 5:
            return {
                "角色": role, "算數位": d,
                "斷語": "算中無五，大小杜塞無門，選兵宜登高地",
            }
        info = _CHENGSHEN.get(d, {})
        return {
            "角色": role,
            "算數位": d,
            "行列": info.get("行列", ""),
            "行軍": info.get("行軍", ""),
            "祀方": info.get("祀方", ""),
            "帛色": info.get("帛色", ""),
            "面向": info.get("面向", ""),
            "咒": info.get("咒", ""),
            "斷語": (
                f"獻牛脯酌酒以祀，{info.get('面向', '')}咒曰：{info.get('咒', '')}"
                if info else ""
            ),
        }
    return {
        "主稱神": _one(home_cal, "主"),
        "客稱神": _one(away_cal, "客"),
        "要訣": "凡興兵必祗神力，布筭運籌明太乙所在；為主明主筭、為客明客筭",
    }


def chenbing_chuxiang(home_cal, away_cal):
    """陳兵必出其鄉（卷十五「明陳兵出鄉術」）。"""
    h, a = _cal_digit(home_cal), _cal_digit(away_cal)
    return {
        "主": {"算數位": h, "出鄉": _CHUBING_XIANG.get(h, "—"),
               "斷語": f"主算得{h}，陳兵必出{_CHUBING_XIANG.get(h, '—')}"},
        "客": {"算數位": a, "出鄉": _CHUBING_XIANG.get(a, "—"),
               "斷語": f"客算得{a}，陳兵必出{_CHUBING_XIANG.get(a, '—')}"},
        "要訣": "陳兵必出其鄉，取出門向算之義；地順其鄉則益吉，地反其鄉則凶",
    }


def xuanjiang_zhi():
    """選將之術（卷十五「明選將之術」）。"""
    return {
        "外貌十不合": [
            "外廉內不誠", "有精無情", "湛湛無為", "好謀不決", "果敢不能",
            "控人不信", "恍惚內忠實", "詭微見功", "外勇內怯", "肅肅易靜",
        ],
        "八微辨賢": [
            "問之以言觀其辭", "窮之以辭觀其變", "與之以謀觀其誠",
            "明白顯問觀其德", "使之以財觀其廉", "試之以色觀其貞",
            "告之以危觀其勇", "醉之以酒觀其態",
        ],
        "斷語": "八微皆備，則賢與不肖之別；將不仁則三軍不親，將不勇則三軍不銳",
    }


def jiaobing_shu():
    """教兵之術（卷十五「明教兵之術」）。"""
    return {
        "金鼓節": "凡領三軍必有金鼓之節，以整齊士眾",
        "教成次第": "教一人成則合十人，十人成則合百人，百人成則合千人，千人成則合萬人，萬人成則合三軍",
        "斷語": "不教民戰是謂棄之；卒不服習器不利，與空手同",
    }


def suidi_zhibian(terrain_shape=None, home_cal=None, away_cal=None):
    """隨地制變、置陣隨地（卷十五）。"""
    result = {
        "地形用兵": [{"地形": t, "所利": v} for t, v in _TERRAIN_BING],
        "置陣隨地": [{"地形": k, "宜陣": v[0], "五行": v[1], "所利": v[2]}
                      for k, v in _TERRAIN_ZHEN.items()],
        "斷語": "因地制宜，知兵之機與地之利；出兵從門置陣順地",
    }
    if terrain_shape and terrain_shape in _TERRAIN_ZHEN:
        z, wx, note = _TERRAIN_ZHEN[terrain_shape]
        result["當前地形"] = terrain_shape
        result["宜陣"] = z
        result["建議"] = note
    if home_cal is not None:
        hz = _zhen_from_calc(home_cal)
        result["主算陣型"] = hz.get("陣型", "")
        result["算陣合地"] = (
            f"主算{hz.get('數位')}宜{hz.get('陣型')}，地順其鄉則益吉"
        )
    return result


def fenhe_yongbing(home_gen, away_gen, home_vgen, away_vgen, geju=None,
                   three_doors=None, five_gens=None):
    """分合用兵（卷十五「明分合用兵之術」）。"""
    notes = ["大戰先定戰日移檄諸將，先期至者賞，後期至者斬，併力合戰"]
    can_split = True
    if geju:
        if any("關" in k for k in geju):
            notes.append("四將同宮為關，分合不利，各宜固守")
            can_split = False
        if any("掩" in k or "擊" in k for k in geju):
            notes.append("有掩擊之時，宜奇伏分合，不可盲併")
    if three_doors == "三門具。" and five_gens == "五將發。":
        notes.append("三門具五將發，宜期會合戰一鼓而下")
    elif three_doors != "三門具。" or five_gens != "五將發。":
        notes.append("門不具或將不發，分兵各守不宜强合")
        can_split = False
    if home_gen and away_gen and home_gen == away_gen and home_gen != 5:
        notes.append("主客大將同宮，可設奇伏分合以破敵")
    if home_vgen and away_vgen and home_vgen == away_vgen and home_vgen != 5:
        notes.append("主客參將同宮，分路合擊須防自相混亂")
    return {
        "宜分合": can_split,
        "斷語": "；".join(notes),
        "要訣": "將若不知分合，不可以語奇伏也",
    }


def guanfeng_chajiang(wuyin_feng_result=None, wind_sound=None):
    """五音觀風察將（卷十五）。"""
    result = {"風音察將": dict(_FENG_JIANG)}
    result["風聲察將"] = {
        k: {"五音": v[0], "風象": v[1], "將德": v[2]}
        for k, v in _WIND_SOUND_JIANG.items()
    }
    if wind_sound and wind_sound in _WIND_SOUND_JIANG:
        _, desc, virtue = _WIND_SOUND_JIANG[wind_sound]
        result["當前風聲"] = wind_sound
        result["斷語"] = f"{wind_sound}（{desc}），其將{virtue}"
    elif wuyin_feng_result:
        wy = wuyin_feng_result.get("風向五音", {}).get("音", "")
        if wy:
            result["斷語"] = f"風從{wy}音方來，將德：{_FENG_JIANG.get(wy, '')}"
        elif wuyin_feng_result.get("盛衰"):
            result["斷語"] = wuyin_feng_result["盛衰"]
        else:
            result["斷語"] = "視風勢與五音以察將帥賢否"
    else:
        result["斷語"] = "視風勢與五音以察將帥賢否"
    return result


def jungshi_shengfu_pan(ty=None, home_cal=None, away_cal=None, wuyin_feng=None,
                        yunqi=None, flybird_gong=None, skyeyes=None, shiji=None,
                        home_gen=None, away_gen=None, geju=None):
    """出兵軍勢勝負（卷十五「明出兵軍勢勝負術」+ 風雲飛鳥）。"""
    items = []
    if wuyin_feng:
        sheng = wuyin_feng.get("盛衰", "")
        if sheng and ("大捷" in sheng or "成功" in sheng or "當勝" in sheng):
            items.append(f"五音風利：{sheng}")
        elif sheng and ("敗" in sheng or "剋" in sheng):
            items.append(f"五音風不利：{sheng}")
    if yunqi:
        cloud = yunqi.get("雲氣", "")
        if cloud:
            items.append(f"雲氣：{cloud}")
    wc_g = _gong_of_chen(skyeyes)
    sj_g = _gong_of_chen(shiji)
    fb = flybird_gong if isinstance(flybird_gong, int) else _chen_gong(flybird_gong)
    if ty and fb:
        if fb == ty:
            items.append("風雲飛鳥衝太乙宮，大凶宜備敵")
        elif fb == wc_g:
            items.append("從主目德方上來，主人急擊所衝之處大勝")
        elif fb == sj_g:
            items.append("從客目德方上來，主人急宜備敵")
        elif home_gen and fb == home_gen:
            items.append("風雲從主大將方來，主勝")
        elif away_gen and fb == away_gen:
            items.append("風雲從客大將方來，客勝")
    if geju and any("掩" in k or "擊" in k for k in geju):
        items.append("有掩擊格局，審風雲而後動")
    h_d, a_d = _cal_digit(home_cal or 0), _cal_digit(away_cal or 0)
    if h_d > a_d:
        items.append("主算長，軍勢稍厚")
    elif a_d > h_d:
        items.append("客算長，軍勢稍厚")
    if not items:
        items.append("風從後來人雄壯旗旄如莽鼓角清和，必獲全勝")
        items.append("雲厚風微客勝主負；風主雲客風勁雲薄主勝")
    return {"軍勢": items, "斷語": "；".join(items)}


# ======================  太乙統宗寶鑑 卷十七：軍事占斷  ======================

def chubing_yongshi(home_cal, away_cal, skyeyes_des, sf_mask, three_doors, five_gens, ty_door=None):
    """出兵舉事用日／用時（卷十七）"""
    def _usable(cal, is_home):
        d = cal % 10
        if d == 0:
            d = 10
        if d == 5:
            return False, "八門杜塞"
        if three_doors != "三門具。":
            return False, three_doors or "三門不具"
        if five_gens != "五將發。":
            return False, five_gens or "五將不發"
        if is_home and skyeyes_des:
            return False, f"主目{skyeyes_des}"
        if not is_home and sf_mask:
            return False, "客目掩擊"
        if ty_door in ("休", "生", "開"):
            return False, f"太乙在{ty_door}門下"
        return True, "利以興師動眾舉用百事"

    h_ok, h_msg = _usable(home_cal, True)
    a_ok, a_msg = _usable(away_cal, False)
    return {
        "主方": {"可用": h_ok, "斷語": h_msg},
        "客方": {"可用": a_ok, "斷語": a_msg},
        "要訣": "冬至用陽局之日時，夏至用陰局之日時；文昌不囚迫、始擊不掩擊、算和將發",
    }


def diguo_dongjing(away_cal, three_doors, five_gens, ty, skyeyes, shiji,
                   home_gen, home_vgen, away_gen, away_vgen, skyeyes_des, geju=None):
    """敵國動靜（卷十七）"""
    d = away_cal % 10
    if d == 0:
        d = 10
    if d == 5:
        return {"動靜": "敵不來", "斷語": "客算得五、十五、二十五、三十五，八門杜塞"}
    bad = (
        five_gens != "五將發。"
        or (skyeyes_des and "掩" in skyeyes_des)
        or (geju and any("格" in k or "迫" in k or "掩" in k for k in geju))
    )
    wc_g = _gong_of_chen(skyeyes)
    sj_g = _gong_of_chen(shiji)
    front = {ty, *_ty_neighbors(ty).values()}
    at_front = sum(1 for g in (wc_g, sj_g, home_gen, home_vgen, away_gen, away_vgen)
                   if g in front or g == 5)
    if not bad and three_doors == "三門具。" and at_front >= 3:
        return {"動靜": "敵來降不為寇盜", "斷語": "三門具五將發，主客俱會太乙宮前，所聞皆吉"}
    if bad:
        return {"動靜": "敵為寇盜", "斷語": "五將不發或陰陽不和，有掩擊挾格，主客不會太乙前"}
    return {"動靜": "未定", "斷語": "當視客目轉行方向：南行為來，北行為不來"}


def jianmie_xushi(ty, shiji, away_gen, skyeyes=None):
    """敵國間諜窺占（卷十七）"""
    sj_g = _gong_of_chen(shiji)
    ag_g = away_gen
    wc_g = _gong_of_chen(skyeyes) if skyeyes else None
    sj_realm = _realm_of_gong(ty, sj_g)
    ag_realm = _realm_of_gong(ty, ag_g)
    av_note = ""
    if wc_g and ag_g == wc_g and sj_realm == "外":
        return {"間諜": "奸細入我境", "斷語": "主目在外宮之地，客大將臨其宮"}
    if sj_realm == "外" and ag_realm == "外":
        return {"間諜": "敵兵盡入我境", "斷語": "客目客大將俱在外地"}
    if sj_realm == "外":
        return {"間諜": "外國遣使窺覘", "斷語": "客目所臨在外，間諜未入我境"}
    return {"間諜": "無大害", "斷語": "客目在內地" + av_note}


def dishi_xushi(ty, shiji, away_gen):
    """敵使虛實（卷十七）"""
    ty_wx = _PALACE_WX.get(ty, "")
    sj_wx = Ganzhiwuxing(shiji) if shiji else ""
    ag_wx = _PALACE_WX.get(away_gen, "")
    if ty_wx and sj_wx and _WUXING_KE.get(ty_wx) == sj_wx:
        return {"虛實": "實", "斷語": "太乙宮制客目，敵使所言皆實可信"}
    if ty_wx and ag_wx and _WUXING_KE.get(ty_wx) == ag_wx:
        return {"虛實": "實", "斷語": "太乙宮制客大將，敵使所言皆實可信"}
    if sj_wx and ty_wx and _WUXING_KE.get(sj_wx) == ty_wx:
        return {"虛實": "虛", "斷語": "客目反制太乙宮，所言皆虛不可信"}
    if ag_wx and ty_wx and _WUXING_KE.get(ag_wx) == ty_wx:
        return {"虛實": "虛", "斷語": "客大將反制太乙宮，所言皆虛不可信"}
    return {"虛實": "未定", "斷語": "當明時計太乙所制以決之"}


def _chen_realm(ty, ch):
    """天目／始擊之辰在太乙前後（卷十七：以前為外、以後為內）。"""
    if not ch:
        return "中"
    gong2chen = {}
    for _ch, _p in gong2.items():
        gong2chen.setdefault(_p, []).append(_ch)
    chens = gong2chen.get(ty, [])
    if len(chens) == 2:
        seq = list(sixteen)
        p0, p1 = seq.index(chens[0]), seq.index(chens[1])
        out_chen = seq[(p1 + 1) % 16]
        in_chen = seq[(p0 - 1) % 16]
        if ch == out_chen:
            return "外"
        if ch == in_chen:
            return "內"
        if ch in chens:
            return "同宮"
    return _realm_of_gong(ty, _gong_of_chen(ch))


def _clamp_guest(geju=None, skyeyes_des=None):
    if skyeyes_des and "客挾" in skyeyes_des:
        return True
    return bool(geju and any("客挾" in v for v in geju.values()))


def _clamp_host(geju=None, skyeyes_des=None):
    if skyeyes_des and "主挾" in skyeyes_des:
        return True
    return bool(geju and any("主挾" in v for v in geju.values()))


def _yang_yin_bundle(ty, skyeyes, shiji, home_gen, home_vgen, away_gen=None, away_vgen=None):
    """主人／客人俱陽或俱陰（卷十七見聞術）。"""
    yang_ty = {8, 3, 4, 9}
    yin_ty = {2, 7, 6, 1}
    wc_g = _gong_of_chen(skyeyes)
    sj_g = _gong_of_chen(shiji)

    def _bundle(gongs, zone):
        gs = [g for g in gongs if g and g != 5]
        if not gs:
            return False
        return all(g in zone for g in gs)

    zone = yang_ty if ty in yang_ty else yin_ty
    host = _bundle((wc_g, home_gen, home_vgen), zone)
    guest = _bundle((sj_g, away_gen, away_vgen), zone)
    if ty in yang_ty and host:
        return "主人俱陽，重陽必有重吉"
    if ty in yin_ty and host:
        return "主人俱陰，重陰必有重凶"
    if ty in yang_ty and guest:
        return "客人俱陽，重陽必有重吉"
    if ty in yin_ty and guest:
        return "客人俱陰，重陰必有重凶"
    return ""


def _gong_wx_state(gong, wangzhuai=None):
    if not wangzhuai or not gong:
        return ""
    return wangzhuai.get(gong, "")


_WX_STATE_MATTER = {
    "旺": "新事",
    "相": "相爭事",
    "胎": "生產婦人事",
    "沒": "溺沒事",
    "死": "死喪事",
    "囚": "刑禁事",
    "休": "疾病，行人營事無成",
    "廢": "廢棄改易恐懼之事",
}


def jianwen_xushi(ty, skyeyes, shiji, skyeyes_des, three_doors, five_gens,
                  geju=None, sf_mask=False, sf_hit=False, home_gen=None, home_vgen=None,
                  away_gen=None, away_vgen=None):
    """見聞占虛實（卷十七）"""
    realm = _chen_realm(ty, skyeyes)
    rules = []
    if sf_mask:
        rules.append("天目掩擊太乙：所聞善事則虛，不善之事則實")
    if sf_hit:
        rules.append("天目擊太乙：所聞多實，行人多阻")
    if three_doors == "三門具。" and five_gens == "五將發。":
        rules.append("三門具五將發：所聞吉事則吉，凶事不凶")
    else:
        rules.append("三門不具或五將不發：所聞吉不吉，聞凶則凶")
    if _clamp_host(geju, skyeyes_des):
        rules.append("主人挾客：所聞凶不凶，聞吉則吉")
    if _clamp_guest(geju, skyeyes_des):
        rules.append("客挾主人：所聞凶則凶，吉事多虛")
    if realm == "內":
        rules.append("天目在內：所聞憂即憂，所聞喜不喜")
    elif realm == "外":
        rules.append("天目在外：所聞憂不憂，所聞喜即喜")
    bundle = _yang_yin_bundle(ty, skyeyes, shiji, home_gen, home_vgen, away_gen, away_vgen)
    if bundle:
        rules.append(bundle)
    return {"天目內外": realm, "斷語": "；".join(rules)}


def taobu_panwang(ty, skyeyes, shiji, home_gen, geju=None, skyeyes_des=None,
                  sf_mask=False, wangzhuai=None):
    """討捕叛亡（卷十七）"""
    wc_realm = _chen_realm(ty, skyeyes)
    sj_realm = _chen_realm(ty, shiji)
    host_realm = _realm_of_gong(ty, home_gen)
    catch = []
    miss = []
    if _clamp_guest(geju, skyeyes_des):
        catch.append("客挾主人")
    if sj_realm == "內":
        catch.append("始擊（上目）在內")
    if host_realm == "同宮" and wc_realm in ("內", "同宮"):
        catch.append("太乙與主將同宮而天目臨之")
    if wc_realm == "內":
        catch.append("天目在內（箕得內）")
    if host_realm == "外":
        miss.append("主將在外")
    if sf_mask:
        miss.append("天目掩太乙，得而復失")
    if wc_realm == "外" and sj_realm == "外":
        miss.append("天目與始擊俱在外")
    hideout = ""
    if geju:
        if any("掩" in k for k in geju):
            hideout = f"叛亡藏匿於始擊{shiji}掩迫之下，往必擒之"
        elif any("迫" in k and "文昌" in k for k in geju):
            hideout = f"叛亡藏匿於文昌{skyeyes}迫之下，往必擒之"
    wx = _gong_wx_state(home_gen, wangzhuai)
    if wx in ("旺", "相"):
        miss.append(f"主將臨{wx}相有氣，不可往討捕，往必被辱")
    if catch and not miss:
        verdict = "捕得"
    elif miss and not catch:
        verdict = "不得"
    elif catch and miss:
        verdict = "得失相半"
    else:
        verdict = "未定"
    return {
        "結果": verdict,
        "得機": catch or ["無明顯得機"],
        "失機": miss or ["無明顯失機"],
        "藏匿": hideout or "當視掩迫之下以定藏匿之所",
    }


def zhiqu_duili(ty, skyeyes, home_gen, home_cal, geju=None, sf_mask=False,
                sf_hit=False, wangzhuai=None):
    """執囚對吏（卷十七）"""
    host_realm = _realm_of_gong(ty, home_gen)
    wc_realm = _chen_realm(ty, skyeyes)
    notes = []
    if sf_mask or sf_hit:
        notes.append("天目擊掩太乙，或主將在外，或立旺神，不可入獄對吏")
    wx = _gong_wx_state(home_gen, wangzhuai)
    if wx in ("旺", "相"):
        notes.append(f"主將立{wx}神，不可入獄")
    if host_realm == "同宮" and wc_realm in ("內", "同宮"):
        notes.append("太乙與主將同宮而天目臨之，入獄易出，逢貴人解憂")
    if wc_realm == "內" and host_realm == "內":
        notes.append("主將立內辰，入獄對吏卒難明")
    if home_cal in (16, 26, 36):
        notes.append("算得十六執者，解")
    if not notes:
        notes.append("當視天目與太乙內外以決遲留")
    ok = not any("不可" in n for n in notes)
    return {"可解": ok or home_cal in (16, 26, 36), "斷語": "；".join(notes)}


def _guxu_label(realm: str) -> str:
    """孤虛斷語：外為孤、內為虛（卷五攻擊、卷十七求索同訣）。"""
    if realm == "內":
        return "內為虛"
    if realm == "外":
        return "外為孤"
    return "—"


def qiusuo_suode(ty, skyeyes, home_gen, geju=None, skyeyes_des=None,
                 sf_ge=False, wangzhuai=None):
    """求索有無所得（卷十七）"""
    realm = _chen_realm(ty, skyeyes)
    host_realm = _realm_of_gong(ty, home_gen)
    wx = _gong_wx_state(home_gen, wangzhuai)
    if realm == "內":
        base = "天目在內，可以請謁貴人、干求財物皆有所得"
        found = True
    else:
        base = "天目在外，不可以請謁求索，訪人不見"
        found = False
    notes = [base]
    if _clamp_host(geju, skyeyes_des):
        notes.append("主人挾客，何可請謁")
        found = False
    if _clamp_guest(geju, skyeyes_des):
        notes.append("客人挾主，求索皆得")
        found = True
    if host_realm == "內":
        notes.append("主將在內為得")
    elif host_realm == "外":
        notes.append("主將在外為不得")
        found = False
    if sf_ge:
        notes.append("天目格太乙，見貴請謁詞訟百事上下格之")
        found = False
    if wx in ("旺", "相"):
        notes.append(f"主將立{wx}神，不可往見尊長請謁")
        found = False
    return {
        "天目內外": realm,
        "孤虛": _guxu_label(realm),
        "有得": found,
        "斷語": "；".join(notes),
    }


def shiji_zhanshi(ty, skyeyes, skyeyes_des, three_doors, five_gens, home_cal, away_cal,
                  geju=None, sf_mask=False, sf_hit=False, wangzhuai=None):
    """時計占諸事（卷十七）"""
    wc_g = _gong_of_chen(skyeyes)
    wx_state = _gong_wx_state(wc_g, wangzhuai)
    items = []
    if sf_mask:
        items.append("天目掩太乙：征伐興造買賣百事皆敗失不利")
    if sf_hit:
        items.append("天目擊太乙：行者訶留，客挾主人或得廢算皆凶")
    if three_doors == "三門具。" and five_gens == "五將發。":
        items.append("三門具五將發陰陽和：百事吉")
    else:
        items.append("門不具或將不發或不和：百事凶")
    if _clamp_host(geju, skyeyes_des):
        items.append("主人挾客及關客：可言吏不可言民")
    if _clamp_guest(geju, skyeyes_des):
        items.append("客挾主人及關主：可言民不可言吏")
    if wx_state:
        matter = _WX_STATE_MATTER.get(wx_state, "")
        if matter:
            items.append(f"天目所臨{wx_state}神：主{matter}")
    cal_harmony = (home_cal % 2 == away_cal % 2)
    if three_doors == "三門具。" != (five_gens == "五將發。"):
        items.append("算和而門不具，或門具而算不和，當以消息推之" if not cal_harmony else "算和門具將發，百事可為")
    return {"諸事": items, "財事": _WX_STATE_MATTER.get(wx_state, "視旺相休囚以明")}


def dibing_laifang(ty, away_cal, shiji, yinyang=None):
    """敵來方將卒多寡（卷十七）"""
    d = away_cal % 10
    if d == 0:
        d = 10
    if d == 5:
        return {"來否": "不來", "斷語": "客算得五，八門杜塞"}
    sj_g = _gong_of_chen(shiji)
    realm = _realm_of_gong(ty, sj_g)
    direction = {
        "外": "南來（前）", "內": "北來（後）",
    }.get(realm, "四維")
    if ty in (1, 8, 3, 4):
        yang = away_cal % 2 != 0
    else:
        yang = away_cal % 2 == 0
    has_thief = yang if yinyang is None else yinyang
    if away_cal >= 16:
        scale = "兵眾多，有將有卒"
    elif away_cal <= 15:
        scale = "兵寡鼠竊，無將"
    else:
        scale = "中等"
    left_right = ""
    if sj_g:
        if sj_g in (3, 4, 9):
            left_right = "從東方來"
        elif sj_g in (6, 7, 1):
            left_right = "從西方來"
        elif sj_g in (2,):
            left_right = "從南方來"
        elif sj_g in (8,):
            left_right = "從北方來"
    return {
        "有賊": has_thief,
        "兵勢": scale,
        "方向": left_right or direction,
        "斷語": f"客目臨{num2gong(sj_g) if sj_g else shiji}，算得{away_cal}",
    }


def junshi_yingyong(home_cal, away_cal, ty, skyeyes, shiji, day_zhi=None,
                     hour_zhi=None, geju=None, three_doors=None, five_gens=None,
                     wind_gong=None, wind_dir_zhi=None, cloud_from_gong=None,
                     home_gen=None, away_gen=None, home_vgen=None, away_vgen=None,
                     flybird_gong=None, terrain_shape=None):
    """卷十五軍事應用綜合"""
    wf = wuyin_feng(day_zhi, hour_zhi, wind_dir_zhi) if day_zhi else {}
    yq = yunqi_nishun(home_cal, away_cal, cloud_from_gong)
    return {
        "奇兵伏兵": qibing_fubing(ty, skyeyes, shiji, home_cal, away_cal, geju),
        "五陣置旗": wuzhen_bazhen(home_cal, away_cal),
        "出兵稱神": chubing_chengshen(home_cal, away_cal),
        "陳兵出鄉": chenbing_chuxiang(home_cal, away_cal),
        "選將之術": xuanjiang_zhi(),
        "教兵之術": jiaobing_shu(),
        "隨地制變": suidi_zhibian(terrain_shape, home_cal, away_cal),
        "分合用兵": fenhe_yongbing(
            home_gen, away_gen, home_vgen, away_vgen, geju, three_doors, five_gens),
        "五音風": wf,
        "五音觀風察將": guanfeng_chajiang(wf),
        "安營置陣": anying_rishi(ty, skyeyes, shiji, geju, three_doors, five_gens),
        "風從八卦": feng_bagua_zhuke(wind_gong),
        "雲氣逆順": yq,
        "軍勢勝負": jungshi_shengfu_pan(
            ty, home_cal, away_cal, wf, yq, flybird_gong,
            skyeyes, shiji, home_gen, away_gen, geju),
    }


# ======================  太乙統宗寶鑑 卷五：軍事戰略  ======================
# 內外占攻擊、太乙助主客、算長短、數孤單、數有所主、主客動靜、輔相將帥賢否、諸將旺衰。

_TY_INNER = frozenset((1, 8, 3, 4))
_TY_OUTER = frozenset((9, 2, 6, 7))
_GOOD_WX = frozenset(("旺", "相", "胎"))
_BAD_WX = frozenset(("死", "囚", "休", "廢", "沒"))
_GENERAL_WX = {
    "太乙": "木", "天乙": "火", "地乙": "土", "始擊": "火", "文昌": "土",
    "主將": "土", "主參": "金", "客將": "水", "客參": "木",
}
_WX_REL = {
    ("火", "火"): "旺", ("金", "金"): "旺", ("木", "木"): "旺",
    ("水", "水"): "旺", ("土", "土"): "旺",
    ("土", "金"): "相", ("金", "水"): "相", ("水", "木"): "相",
    ("木", "火"): "相", ("火", "土"): "相",
    ("火", "土"): "休", ("土", "水"): "休", ("水", "金"): "休",
    ("金", "木"): "休", ("木", "土"): "休",
    ("火", "金"): "囚", ("金", "木"): "囚", ("木", "土"): "囚",
    ("土", "水"): "囚", ("水", "火"): "囚",
    ("火", "水"): "死", ("水", "土"): "死", ("土", "木"): "死",
    ("木", "金"): "死", ("金", "火"): "死",
}
_CHENG_XINGSHA = {
    "申子辰": {
        "劫殺": "巳", "災殺": "午", "天殺": "未", "地殺": "申",
        "自刑": "辰", "刑方": "西方",
    },
    "亥卯未": {
        "劫殺": "申", "災殺": "酉", "天殺": "戌", "地殺": "亥",
        "自刑": "亥", "刑方": "北方",
    },
    "巳酉丑": {
        "劫殺": "寅", "災殺": "卯", "天殺": "辰", "地殺": "巳",
        "自刑": "酉", "刑方": "西方",
    },
}


def _rotate_sixteen_gods(anchor_god, anchor_zhi):
    """十六神環旋轉：anchor_god 臨 anchor_zhi。"""
    if not anchor_god or not anchor_zhi:
        return {}
    seq = list(sixteen)
    base = sixteengod.get(anchor_god)
    if not base or anchor_zhi not in seq:
        return {}
    offset = (seq.index(anchor_zhi) - seq.index(base)) % 16
    return {
        god: seq[(seq.index(z) + offset) % 16]
        for god, z in sixteengod.items()
    }


def _zhi_step(zhi, steps=1):
    seq = list(sixteen)
    if zhi not in seq:
        return ""
    return seq[(seq.index(zhi) + steps) % 16]


def _calc_jianbei(num):
    """將吏兵備與算長短（卷五「明數長短占緩急術」）。"""
    n = int(num)
    s = str(n)
    has_jiang = n >= 10 or "0" in s
    has_li = "5" in s
    has_bing = "1" in s
    missing = []
    if not has_jiang:
        missing.append("無將")
    if not has_li:
        missing.append("無吏")
    if not has_bing:
        missing.append("無兵")
    full = not missing
    if n >= 16:
        length = "長"
        harmony = "和" if full else "不和"
        verdict = "箭長而和，將吏兵俱備，宜舉百事" if full else f"箭長而不和，{'、'.join(missing)}，不利興師"
    else:
        length = "短"
        harmony = "不和"
        verdict = f"箭短，{'、'.join(missing) or '將吏兵不具'}，百事皆忌"
    return {
        "算數": n,
        "長短": length,
        "和否": harmony,
        "將吏兵俱備": full,
        "缺": missing,
        "斷語": verdict,
    }


def neiwai_gongji(ty, skyeyes):
    """內外占攻擊（卷五「明內外以占攻擊術」）。"""
    realm = _chen_realm(ty, skyeyes)
    guxu = _guxu_label(realm)
    if realm == "內":
        return {
            "天目內外": "內",
            "孤虛": guxu,
            "宜攻": "外",
            "斷語": "天目在內地，可以攻外",
            "要訣": "外為孤，內為虛",
        }
    if realm == "外":
        return {
            "天目內外": "外",
            "孤虛": guxu,
            "宜攻": "內",
            "斷語": "天目在外地，可以攻內",
            "要訣": "外為孤，內為虛",
        }
    return {
        "天目內外": realm,
        "孤虛": guxu,
        "宜攻": "—",
        "斷語": "天目與太乙同宮或居中，宜審時而動",
        "要訣": "外為孤，內為虛",
    }


def guxu_duizhao(ty, skyeyes, home_gen=None, geju=None, skyeyes_des=None,
                 sf_ge=False, wangzhuai=None):
    """卷五「內外占攻擊」與卷十七「求索所得」孤虛對照。"""
    attack = neiwai_gongji(ty, skyeyes)
    seek = qiusuo_suode(
        ty, skyeyes, home_gen or ty, geju, skyeyes_des, sf_ge, wangzhuai,
    )
    realm = attack["天目內外"]
    guxu = attack["孤虛"]
    base_seek = realm == "內"
    seek_final = seek.get("有得", base_seek)

    if realm == "內":
        align = "同向"
        align_note = "內為虛：宜攻外，請謁干求皆得"
    elif realm == "外":
        align = "同向"
        align_note = "外為孤：宜攻內，不可請謁求索"
    else:
        align = "待定"
        align_note = "天目與太乙同宮或居中，皆宜審格局而動"

    if seek_final != base_seek and realm in ("內", "外"):
        align = "格局修正"
        align_note += (
            f"；求索終判{'有得' if seek_final else '無得'}"
            f"（{seek.get('斷語', '')}）"
        )

    return {
        "天目內外": realm,
        "孤虛": guxu,
        "要訣": "天目在前為內、在後為外；外為孤，內為虛",
        "卷五": {
            "篇目": "明內外以占攻擊術",
            "孤虛": guxu,
            "宜攻": attack.get("宜攻", "—"),
            "斷語": attack.get("斷語", ""),
        },
        "卷十七": {
            "篇目": "明求索有無所得術",
            "孤虛": seek.get("孤虛", _guxu_label(realm)),
            "求索": "有得" if seek_final else "無得",
            "斷語": seek.get("斷語", ""),
        },
        "對照": align,
        "對照斷語": align_note,
    }


def guxu_sectors(ty, skyeyes):
    """孤虛扇區資料：內外辰、天目、宜攻方向（供排盤視覺化）。"""
    attack = neiwai_gongji(ty, skyeyes)
    inner_branches: list[str] = []
    outer_branches: list[str] = []
    seq = list(sixteen)
    gong2chen: dict[int, list[str]] = {}
    for ch, p in gong2.items():
        gong2chen.setdefault(p, []).append(ch)
    chens = gong2chen.get(ty, [])
    if len(chens) == 2 and skyeyes in seq:
        p0, p1 = seq.index(chens[0]), seq.index(chens[1])
        outer_branches = [seq[(p1 + 1) % 16]]
        inner_branches = [seq[(p0 - 1) % 16]]
    else:
        for br in seq:
            g = gong2.get(br)
            realm = _realm_of_gong(ty, g)
            if realm == "內":
                inner_branches.append(br)
            elif realm == "外":
                outer_branches.append(br)
    attack_dir = attack.get("宜攻", "—")
    if attack_dir == "外":
        attack_branches = list(outer_branches)
    elif attack_dir == "內":
        attack_branches = list(inner_branches)
    else:
        attack_branches = []
    return {
        **attack,
        "天目辰": skyeyes,
        "內辰": inner_branches,
        "外辰": outer_branches,
        "宜攻辰": attack_branches,
    }


def ty_zhuzhu_ke(ty, three_doors):
    """太乙內外助主客（卷五「明太乙內外助主客術」）。"""
    doors_ok = three_doors == "三門具。"
    if ty in _TY_INNER:
        zone = "地內"
        helper = "助主人"
        if doors_ok:
            verdict = "太乙在地內、三門具，主客亦平"
            caution = "欲為主，待太乙在地內且門具將發"
        else:
            verdict = "太乙在地內、三門不具，為主人勝"
            caution = "助主之時不可往攻城，對陣不可先起兵"
    elif ty in _TY_OUTER:
        zone = "天外"
        helper = "助客人"
        if doors_ok:
            verdict = "太乙在天外、三門具，主客亦平"
            caution = "欲為客，待太乙在天外之時"
        else:
            verdict = "太乙在天外、三門不具，為客人勝"
            caution = "助客之時不可守野戰，對陣不可後起兵，大利先舉"
    else:
        zone = "中"
        helper = "主客未明"
        verdict = "太乙居中，主客勢均"
        caution = "須審三門五將與算長短"
    return {
        "太乙宮": num2gong(ty),
        "內外": zone,
        "所助": helper,
        "三門": three_doors,
        "斷語": verdict,
        "用兵": caution,
    }


def gudan_zhanlue(gudan_text, home_cal, away_cal):
    """數孤單占成敗（卷五，整合推孤單斷語）。"""
    result = {"主算": {}, "客算": {}, "綜合": gudan_text or ""}
    ying_yang = {1: "單陽", 3: "單陽", 7: "單陽", 9: "單陽",
                 2: "單陰", 4: "單陰", 6: "單陰", 8: "單陰"}
    for label, num in (("主算", home_cal), ("客算", away_cal)):
        s = str(int(num))
        if len(s) == 1:
            kind = ying_yang.get(int(s), "")
            bad = kind == "單陽" if label == "主算" else kind == "單陰"
            result[label] = {
                "類型": kind,
                "不利": bad,
                "斷語": f"{label}得{kind}，{'不利主人' if label == '主算' and bad else '不利客人' if bad else '沒不利'}",
            }
        elif len(s) == 2:
            d0, d1 = int(s[0]), int(s[1])
            gu = "孤陽" if d1 in (1, 3) else "孤陰"
            dan = ying_yang.get(d0, "")
            if dan == "單陽" and gu == "孤陽":
                combo = "重陽"
                note = "重陽厄火，君宜悔過修德"
            elif dan == "單陰" and gu == "孤陰":
                combo = "重陰"
                note = "重陰厄水，君宜悔過修德"
            else:
                combo = f"{dan}並{gu}"
                note = "沒不利"
            result[label] = {"類型": combo, "斷語": note}
    return result


def zhuke_xianhou(home_cal, away_cal, three_doors, five_gens, ty, skyeyes, shiji):
    """主客動靜分先後（卷五「明主客以分先後動靜之術」）。"""
    h = _calc_jianbei(home_cal)
    a = _calc_jianbei(away_cal)
    doors_ok = three_doors == "三門具。"
    gens_ok = five_gens == "五將發。"
    ready = doors_ok and gens_ok
    if ready:
        base = "三門具五將發，陰陽和利以興兵，所向必克"
        if h["長短"] == a["長短"]:
            winner = "算長者勝" if h["算數"] != a["算數"] else "主客旗鼓相當"
        elif h["長短"] == "長":
            winner = "主算長，利主"
        else:
            winner = "客算長，利客"
        field = "野戰旗鼓相望，先動者為客，後應者為主"
        peace = "安居之代，先舉者為主，後應者為客"
    else:
        base = "三門不具或五將不發，陰陽不和，止宜固守；若興兵則敗"
        winner = "後起者勝"
        field = peace = "固守為上"
    dirs = {
        "東": "陰德", "南": "和德", "西": "大炅", "北": "大武",
    }
    wc_g = _gong_of_chen(skyeyes)
    sj_g = _gong_of_chen(shiji)
    return {
        "野戰": field,
        "安居": peace,
        "三門五將": f"{three_doors}{five_gens}",
        "主算": h,
        "客算": a,
        "勝負": winner,
        "主目": {"辰": skyeyes, "宮": _palace_label(wc_g)},
        "客目": {"辰": shiji, "宮": _palace_label(sj_g)},
        "四維所主": dirs,
        "斷語": f"{base}；{winner}",
    }


def _fuxiang_jiang_pan(chen, gong, wangzhuai, role, enemy=False, ty_door=None):
    wx = _gong_wx_state(gong, wangzhuai)
    if wx in _GOOD_WX:
        verdict = f"{role}臨{wx}有氣之方，必智勇堪任" if "將" in role else f"{role}在生旺之方，必有良佐"
        good = True
    elif wx in _BAD_WX:
        verdict = f"{role}在死囚無氣之方，{'無謀必敗' if '將' in role else '邪佞擅權之漸'}"
        good = False
    else:
        verdict = f"{role}旺衰未明（{_palace_label(gong)}），當再審時計"
        good = None
    if enemy and ty_door == "死":
        verdict += "；更在死門下，彼將身亡"
        good = False
    return {
        "所臨": _palace_label(gong) or chen,
        "旺衰": wx or "—",
        "賢否": "賢" if good else "否" if good is False else "未定",
        "斷語": verdict,
    }


def fuxiang_xianfou(ty, skyeyes, shiji, year_zhi, wangzhuai=None):
    """內外輔相賢否（卷五「明內外大臣輔相賢否之術」）。"""
    rot = _rotate_sixteen_gods("呂申", year_zhi) if year_zhi else {}
    wc_g = _gong_of_chen(skyeyes)
    sj_g = _gong_of_chen(shiji)
    return {
        "呂申加歲": rot,
        "我國輔相": _fuxiang_jiang_pan(skyeyes, wc_g, wangzhuai, "文昌（輔相）"),
        "他國輔臣": _fuxiang_jiang_pan(shiji, sj_g, wangzhuai, "始擊（他國輔臣）", enemy=True),
        "要訣": "歲月日時四計同；呂申加歲位，視文昌／始擊所臨旺相為賢",
    }


def jiangshuai_xianfou(home_gen, away_gen, year_zhi, wangzhuai=None, ty_door=None):
    """內外將帥賢否（卷五「明內外將帥賢否之術」）。"""
    return {
        "呂申加歲": _rotate_sixteen_gods("呂申", year_zhi) if year_zhi else {},
        "我國將帥": _fuxiang_jiang_pan(None, home_gen, wangzhuai, "主大將"),
        "他國將帥": _fuxiang_jiang_pan(None, away_gen, wangzhuai, "客大將", enemy=True, ty_door=ty_door),
        "要訣": "大將臨生旺有氣之宮必堪重任，死囚無氣則無謀必敗",
    }


def generals_wangzhuai(home_gen, home_vgen, away_gen, away_vgen, wangzhuai=None):
    """諸將宮辰旺衰（卷五「明太乙大小諸將旺相死囚宮辰所在術」）。"""
    items = []
    for name, gong in (
        ("主大將", home_gen), ("主參將", home_vgen),
        ("客大將", away_gen), ("客參將", away_vgen),
    ):
        if not gong or gong == 5:
            continue
        elem = _GENERAL_WX.get(
            {"主大將": "主將", "主參將": "主參", "客大將": "客將", "客參將": "客參"}.get(name, ""),
            "",
        )
        pal_wx = _PALACE_WX.get(gong, "")
        jq_state = _gong_wx_state(gong, wangzhuai)
        rel = _WX_REL.get((elem, pal_wx), "")
        items.append({
            "將": name,
            "宮": num2gong(gong),
            "五行": elem,
            "宮五行": pal_wx,
            "節氣旺衰": jq_state or "—",
            "生克": rel or "—",
            "斷語": f"{name}臨{num2gong(gong)}（{elem}見{pal_wx}為{rel or jq_state}）",
        })
    return items


def junshi_zhanlue(ty, home_cal, away_cal, skyeyes, shiji, three_doors, five_gens,
                   home_gen, away_gen, home_vgen, away_vgen, gudan_text=None,
                   year_zhi=None, wangzhuai=None, ty_door=None):
    """卷五軍事戰略綜合"""
    return {
        "內外占攻擊": neiwai_gongji(ty, skyeyes),
        "孤虛對照": guxu_duizhao(ty, skyeyes, home_gen, wangzhuai=wangzhuai),
        "太乙助主客": ty_zhuzhu_ke(ty, three_doors),
        "算長短緩急": {
            "主算": _calc_jianbei(home_cal),
            "客算": _calc_jianbei(away_cal),
            "要訣": "將吏兵三者缺一不可；主箭不具而客箭得全，客利主凶",
        },
        "數孤單成敗": gudan_zhanlue(gudan_text, home_cal, away_cal),
        "數有所主": {
            "主算": wuyin_from_calc(home_cal),
            "客算": wuyin_from_calc(away_cal),
        },
        "主客動靜": zhuke_xianhou(
            home_cal, away_cal, three_doors, five_gens, ty, skyeyes, shiji),
        "輔相賢否": fuxiang_xianfou(ty, skyeyes, shiji, year_zhi, wangzhuai),
        "將帥賢否": jiangshuai_xianfou(
            home_gen, away_gen, year_zhi, wangzhuai, ty_door),
        "諸將旺衰": generals_wangzhuai(
            home_gen, home_vgen, away_gen, away_vgen, wangzhuai),
    }


# ======================  太乙統宗寶鑑 卷十一  ======================
# 十六宮間變化、州國災變月數、城名厄會、飛符四殺、城名歲內災發、九宮／十干城名

_YUEJIAN = list("寅卯辰巳午未申酉戌亥子丑")
_MONTH_NUM = dict(zip(_YUEJIAN, range(1, 13)))
_CHONG_ZHI = {
    "子": "午", "午": "子", "丑": "未", "未": "丑", "寅": "申", "申": "寅",
    "卯": "酉", "酉": "卯", "辰": "戌", "戌": "辰", "巳": "亥", "亥": "巳",
}
_ZHI_BENQI_GAN = dict(zip(di_zhi, "癸己甲乙戊丙丁己庚辛戊壬"))
_TY_OPP_GONG = {1: 9, 9: 1, 2: 8, 8: 2, 3: 7, 7: 3, 4: 6, 6: 4}
_SIXTEEN_GOD_WX = {
    "地主": "水", "陽德": "土", "和德": "木", "呂申": "木", "高叢": "木",
    "太陽": "土", "大炅": "火", "大神": "火", "大威": "火", "天道": "土",
    "大武": "金", "武德": "金", "太簇": "金", "陰主": "土", "陰德": "金", "大義": "水",
}
_VOL11_GOD_BIANHUA = {
    "地主": "建子之月，陽炁生萬物在下，水性潤下；主動搖語言之事",
    "陽德": "建丑之月，二陽用事，德施普博；主生育萬物之事",
    "和德": "冬盡春初，陰陽氣交，時當溫舒；主和集成就之事",
    "呂申": "建寅之月，天炁大溫，萬物生昌；主運謀主宰之事",
    "高叢": "建卯之月，木神正旺，萬物叢生；主發揮之事",
    "太陽": "建辰之月，五陽得位，斗罡所擊；主厄會兵戈之事",
    "大炅": "春夏光明，萬物潔齊；主申命號令迅速之事",
    "大神": "建巳之月，火德變化，萬物茂盛；主毀折破廢之事",
    "大威": "建午之月，炎月任事，政令明新；主光明烈火焰盛之事",
    "天道": "建未之月，地道施履，天下不逆；主陰私之事",
    "大武": "夏秋氣交，金神司權；主牝牡之事",
    "武德": "建申之月，萬物欲死；主傳送遷徙之事",
    "太簇": "建酉之月，萬物成熟；主更變肅殺之事",
    "陰主": "建戌之月，五陰得位，斗罡所擊；主厄期兵喪之事",
    "陰德": "秋冬炁交，陽德復生；主天符命令之事",
    "大義": "建亥之月，萬物荄始；主計謀毀折廢散之事",
}
_NINE_GONG_CHENG = {
    1: ("冀州", "丁丑"), 2: ("荆州", "丁未"), 3: ("青州", "癸丑"),
    4: ("徐州", "甲辰"), 5: ("豫州", "乙丑"), 6: ("雍州", "甲申"),
    7: ("梁州", "戊戌"), 8: ("兗州", "乙未"), 9: ("揚州", "癸酉"),
}
_EXTRA_GONG_CHENG = {
    "絳宮": ("交州", "壬申"), "明堂": ("益州", "辛丑"), "玉堂": ("幽州", "癸卯"),
}
_TEN_GAN_CHENG = {
    "甲": "寅", "乙": "卯", "丙": "巳", "丁": "午", "戊": "巳",
    "己": "未", "庚": "申", "辛": "酉", "壬": "亥", "癸": "子",
}
_SONGKUN_GAN_NUM = {
    ("甲", "己"): 9, ("乙", "庚"): 8, ("丙", "辛"): 7,
    ("丁", "壬"): 6, ("戊", "癸"): 5, ("己", "亥"): 4,
}


def _rotate_chen(chen, offset):
    seq = list(sixteen)
    if not chen or chen not in seq:
        return ""
    return seq[(seq.index(chen) + offset) % 16]


def _lvchen_offset(gan, zhi):
    """呂申加城名干支：_branch 差 + 陰干進一（李淳風丁未例）。"""
    seq = list(sixteen)
    if zhi not in seq:
        return 0
    base = (seq.index(zhi) - seq.index(sixteengod["呂申"])) % 16
    if gan and gan in "乙丁己辛癸":
        base = (base + 1) % 16
    return base


def _rotate_by_offset(offset):
    seq = list(sixteen)
    return {
        god: seq[(seq.index(z) + offset) % 16]
        for god, z in sixteengod.items()
    }


def _city_god_rotation(city_gz):
    """城名干支併推十六神（卷十一李淳風法）。"""
    if not city_gz or len(city_gz) < 2:
        zhi = city_gz[-1] if city_gz else ""
        return _rotate_sixteen_gods("呂申", zhi) if zhi else {}
    return _rotate_by_offset(_lvchen_offset(city_gz[0], city_gz[-1]))


def _disaster_years(zhi):
    """李淳風法：本氣干配臨支及其六冲支之年。"""
    if not zhi or zhi not in di_zhi:
        return []
    gan = _ZHI_BENQI_GAN.get(zhi, "")
    opp = _CHONG_ZHI.get(zhi, "")
    years = []
    if gan and zhi:
        years.append(f"{gan}{zhi}")
    if gan and opp:
        years.append(f"{gan}{opp}")
    return years


def _yuesha_zhi(month_zhi):
    if not month_zhi:
        return ""
    if month_zhi in "寅卯辰":
        return "酉"
    if month_zhi in "巳午未":
        return "巳"
    if month_zhi:
        return "丑"
    return ""


def _cheng_xingsha(city_zhi):
    for group, info in _CHENG_XINGSHA.items():
        if city_zhi in group:
            return {"三合": group, **info}
    return {}


def _sisha_chain(anchor_zhi, hegod_zhi=None):
    """陰主加時，視地主為災殺；合神加時，災殺下為鬼殺。"""
    if not anchor_zhi:
        return {}
    rot = _rotate_sixteen_gods("陰主", anchor_zhi)
    zai_sha = rot.get("地主", "")
    gui_sha = _zhi_step(zai_sha) if zai_sha else ""
    if hegod_zhi and hegod_zhi in list(sixteen):
        offset = (list(sixteen).index(anchor_zhi) - list(sixteen).index(hegod_zhi)) % 16
        gui_sha = list(sixteen)[(list(sixteen).index(zai_sha) + offset) % 16] if zai_sha else gui_sha
    return {"災殺": zai_sha, "鬼殺": gui_sha}


def feifu_sisha(flyfu_zhi, hegod_zhi, year_zhi=None, month_zhi=None,
                day_zhi=None, hour_zhi=None, city_gz=None):
    """飛符四殺（卷十一「明飛行四殺之術」「刑殺例」）。"""
    anchor = hour_zhi or day_zhi or month_zhi or year_zhi
    chain = _sisha_chain(anchor, hegod_zhi)
    yue_sha = _yuesha_zhi(month_zhi)
    tian_zei = _zhi_step(yue_sha) if yue_sha else ""
    yin_zhi = sixteengod.get("陰主", "")
    tian_shi = _zhi_step(yin_zhi) if yin_zhi else ""
    result = {
        "飛符": flyfu_zhi or "—",
        "占時": anchor or "—",
        "災殺": chain.get("災殺", ""),
        "鬼殺": chain.get("鬼殺", ""),
        "月殺": yue_sha,
        "天賊殺": tian_zei,
        "天史殺": tian_shi,
        "斷語": "此月內即發火凶迍，將帥年命併者不可用兵",
    }
    if flyfu_zhi and chain.get("災殺") and flyfu_zhi == chain["災殺"]:
        result["飛符併災殺"] = True
        result["斷語"] = "城名與飛符四殺併，必有屠城之象"
    if city_gz and len(city_gz) >= 2:
        city_zhi = city_gz[-1]
        city_chain = _sisha_chain(city_zhi, hegod_zhi)
        xing = _cheng_xingsha(city_zhi)
        result["城名"] = city_gz
        result["城名災殺"] = city_chain
        result["城名刑殺"] = xing
        if xing:
            result["城名斷語"] = (
                f"{city_gz}屬{xing.get('三合', '')}，劫殺在{xing.get('劫殺')}、"
                f"災殺在{xing.get('災殺')}、天殺在{xing.get('天殺')}、地殺在{xing.get('地殺')}"
            )
    return result


def sixteen_god_bianhua(anchor_god="呂申"):
    """十六宮間神變化所主（卷十一「明十六宮間神變化所主術」）。"""
    anchor_wx = _SIXTEEN_GOD_WX.get(anchor_god, "")
    table = []
    for god, desc in _VOL11_GOD_BIANHUA.items():
        wx = _SIXTEEN_GOD_WX.get(god, "")
        rel = _WX_REL.get((anchor_wx, wx), "") if anchor_wx and wx else ""
        if god == anchor_god:
            rel = "旺"
        table.append({
            "神": god,
            "五行": wx,
            "所主": desc,
            "變化": rel or "—",
            "臨辰": sixteengod.get(god, ""),
        })
    return {
        "要訣": "同類為旺，生我者為相，克我者為死，我生者為休，我克者為囚",
        "加神": anchor_god,
        "加神五行": anchor_wx,
        "十六神變化": table,
    }


def zhouguo_zaiyue(ty, skyeyes, hegod_zhi):
    """州國災變月數之期（卷十一「明州國災發月數之期」）。"""
    if not hegod_zhi or hegod_zhi not in list(sixteen):
        return {"災月": [], "斷語": "合神未明，不能推月數"}
    seq = list(sixteen)
    base_idx = seq.index(hegod_zhi)
    hits = []
    for month_zhi in _YUEJIAN:
        offset = (seq.index(month_zhi) - base_idx) % 16
        eff_wc = _rotate_chen(skyeyes, offset)
        wc_gong = gong2.get(eff_wc)
        if wc_gong == ty:
            hits.append({
                "月建": month_zhi,
                "月序": _MONTH_NUM[month_zhi],
                "格局": "掩",
                "文昌臨": eff_wc,
                "斷語": f"{_MONTH_NUM[month_zhi]}月天目文昌犯太乙宮為掩，災發之期",
            })
        elif wc_gong == _TY_OPP_GONG.get(ty):
            hits.append({
                "月建": month_zhi,
                "月序": _MONTH_NUM[month_zhi],
                "格局": "格",
                "文昌臨": eff_wc,
                "斷語": f"{_MONTH_NUM[month_zhi]}月天目文昌對太乙為格，災發之期",
            })
    return {
        "合神": hegod_zhi,
        "合神所主": _god_at_chen(hegod_zhi) or "—",
        "天目": skyeyes,
        "太乙宮": num2gong(ty),
        "災月": hits,
        "斷語": (
            "、".join(f"{h['月序']}月{h['格局']}" for h in hits)
            if hits else "本年合神遍加月建，天目文昌無掩格太乙之月"
        ),
    }


def chengming_ehui(city_gz):
    """城名占厄會（卷十一「明城名以占厄會術」）。"""
    if not city_gz or len(city_gz) < 1:
        return {}
    city_zhi = city_gz[-1]
    rot = _city_god_rotation(city_gz)
    taiyang_zhi = rot.get("太陽", "")
    yinzhu_zhi = rot.get("陰主", "")
    bing_yao = _disaster_years(taiyang_zhi)
    ji_yi = _disaster_years(yinzhu_zhi)
    return {
        "城名": city_gz,
        "呂申加城": rot,
        "太陽臨": taiyang_zhi,
        "陰主臨": yinzhu_zhi,
        "兵徭之年": bing_yao,
        "疾疫之年": ji_yi,
        "斷語": (
            f"太陽臨{taiyang_zhi}，{'、'.join(bing_yao)}有兵徭之厄；"
            f"陰主臨{yinzhu_zhi}，{'、'.join(ji_yi)}有疾疫之患"
            if bing_yao or ji_yi else "城名未合厄會"
        ),
    }


def _xingsha_months(city_zhi):
    xing = _cheng_xingsha(city_zhi)
    if not xing:
        return [], {}
    months = []
    for key, label in (
        ("劫殺", "劫殺"), ("災殺", "災殺"), ("天殺", "天殺"),
        ("地殺", "地殺"), ("自刑", "自刑"),
    ):
        z = xing.get(key)
        if z and z in _MONTH_NUM:
            months.append({
                "殺": label,
                "支": z,
                "月序": _MONTH_NUM[z],
                "月名": f"{_MONTH_NUM[z]}月",
            })
    return months, xing


def chengming_suinei(year_gan, year_zhi, city_gz=None):
    """城名歲內災發所在（卷十一「明城名歲內災發所在術」）。"""
    yang_year = year_gan in _YANG_GAN if year_gan else False
    anchor_god = "陽德" if yang_year else "天道"
    rot = _rotate_sixteen_gods(anchor_god, year_zhi)
    taiyang_zhi = rot.get("太陽", "")
    yinzhu_zhi = rot.get("陰主", "")
    result = {
        "陽年" if yang_year else "陰年": True,
        "加神": anchor_god,
        "太歲": year_zhi,
        "太陽臨": taiyang_zhi,
        "陰主臨": yinzhu_zhi,
        "要訣": "陽年陽德加太歲，陰年天道加太歲，視太陽陰主所臨城名之下定災期",
    }
    if city_gz and len(city_gz) >= 2:
        city_zhi = city_gz[-1]
        months, xing = _xingsha_months(city_zhi)
        result["城名"] = city_gz
        result["城名刑殺"] = xing
        result["歲內災月"] = months
        e_hui = city_zhi in (taiyang_zhi, yinzhu_zhi)
        result["城當厄會"] = e_hui
        if months:
            result["斷語"] = (
                f"{city_gz}屬{xing.get('三合', '')}，"
                f"災發之期在{'、'.join(m['月名'] for m in months)}"
                + ("；太陽陰主併城名，厄會尤深" if e_hui else "")
            )
        else:
            result["斷語"] = f"{city_gz}未入三合刑殺表"
    else:
        result["斷語"] = "若知城名干支，可推歲內刑殺應期"
    return result


def songkun_zaiqi(city_gz):
    """宋琨法：城名干支數推災發年月（卷十一附術）。"""
    if not city_gz or len(city_gz) < 2:
        return {}
    gan, zhi = city_gz[0], city_gz[-1]
    num = None
    for pair, n in _SONGKUN_GAN_NUM.items():
        if gan in pair or (len(pair) == 2 and zhi == pair[1]):
            num = n
            break
    if num is None:
        num = Ganzhi_num(gan) or 0
    rot = _city_god_rotation(city_gz)
    taiyang_zhi = rot.get("太陽", "")
    yinzhu_zhi = rot.get("陰主", "")
    steps = 0
    if taiyang_zhi in _MONTH_NUM:
        steps += _MONTH_NUM[taiyang_zhi]
    if yinzhu_zhi in _MONTH_NUM:
        steps += _MONTH_NUM[yinzhu_zhi]
    total = num + steps
    remainder = total % 81
    if remainder == 0:
        remainder = 81
    year_part = remainder // 10 if remainder >= 10 else 0
    month_part = remainder % 10 or 3
    return {
        "城名": city_gz,
        "干支數": num,
        "順行至太陽陰主步數": steps,
        "除九八十一餘": remainder,
        "推災年": year_part,
        "推災月": month_part,
        "斷語": f"滿九八十一除之餘{remainder}，以十去之年{year_part}、餘零因三為月{month_part}",
    }


def nine_palace_chengming():
    """九宮城名所主（卷十一）。"""
    rows = [
        {"宮": num2gong(g), "州國": name, "城名": gz}
        for g, (name, gz) in _NINE_GONG_CHENG.items()
    ]
    rows.extend(
        {"宮": k, "州國": v[0], "城名": v[1]}
        for k, v in _EXTRA_GONG_CHENG.items()
    )
    return rows


def ten_gan_chengming():
    """十干城名所在（卷十一）。"""
    return [{"干": g, "城支": z} for g, z in _TEN_GAN_CHENG.items()]


def vol11_zonghe(ty, skyeyes, hegod_zhi, flyfu_zhi, year_gan, year_zhi,
                 month_zhi=None, day_zhi=None, hour_zhi=None, city_gz=None):
    """卷十一綜合：十六宮間變化、州國災變、城名厄會、飛符四殺、歲內災發。"""
    result = {
        "十六宮間變化": sixteen_god_bianhua(),
        "州國災變月數": zhouguo_zaiyue(ty, skyeyes, hegod_zhi),
        "飛符四殺": feifu_sisha(
            flyfu_zhi, hegod_zhi, year_zhi, month_zhi, day_zhi, hour_zhi, city_gz),
        "九宮城名": nine_palace_chengming(),
        "十干城名": ten_gan_chengming(),
    }
    if city_gz:
        result["城名厄會"] = chengming_ehui(city_gz)
        result["城名歲內災發"] = chengming_suinei(year_gan, year_zhi, city_gz)
        result["宋琨災期"] = songkun_zaiqi(city_gz)
    else:
        result["城名歲內災發"] = chengming_suinei(year_gan, year_zhi)
    return result


# ======================  太乙統宗寶鑑 卷十二：統運入卦  ======================
# 統運八卦紀年、入運入卦入爻、行爻禍福、流年太歲直卦、十二運立成、歷史入爻例。

_TONGYUN_EPOCH = -476          # 周敬王四十三年（古籍繫年）
_TONGYUN_YINGCHA = 300         # 卦盈差
_TONGYUN_CYCLE = 11520         # 大周法策
_TONGYUN_CAL = 421             # 校正：敬王四十三年入運二震卦初九

_KING_WEN_64 = (
    "乾坤屯蒙需訟師比小畜履泰否同人大有謙豫隨蠱臨觀噬嗑賁剝復"
    "无妄大畜頤大過坎離咸恆遯大壯晉明夷家人睽蹇解損益夬姤萃升"
    "困井革鼎震艮漸歸妹豐旅巽兌渙節中孚小過既濟未濟"
)
_YANG_GUA_LINE = frozenset("79")
_YAO_NAMES_YANG = ("初九", "九二", "九三", "九四", "九五", "上九")
_YAO_NAMES_YIN = ("初六", "六二", "六三", "六四", "六五", "上六")

_TONGYUN_YUN_DEF = [
    ("天地否泰", 720, ["乾", "坤", "否", "泰"], [216, 144, 180, 180]),
    ("男女交親", 2160,
     ["震", "巽", "恆", "益", "坎", "離", "既濟", "未濟", "艮", "兌", "損", "咸"],
     [168, 192, 200, 160, 168, 192, 181, 179, 178, 118, 212, 190]),
    ("三陽晶守政", 1152, ["大壯", "无妄", "需", "訟", "大畜", "遯"], None),
    ("四陰毛權衡", 1008, ["觀", "晉", "明夷", "萃", "臨"], None),
    ("資育還本", 936, ["豫", "復", "比", "剝", "謙"], None),
    ("造化符天", 1224, ["小畜", "同人", "大有", "履", "夬"], None),
    ("剛中健至", 672, ["解", "屯", "頤", "遇"], None),
    ("羣愚位賢", 768, ["家人", "鼎", "中孚", "大過"], None),
    ("德義順命", 1080, ["豐", "噬嗑", "歸妹", "隨", "節", "困"], None),
    ("惑姤留連", 1080, ["渙", "井", "漸", "蠱", "旅", "賁"], None),
    ("寡陽相搏", 336, ["蹇", "蒙"], None),
    ("物極元終", 384, ["睽", "革"], None),
]

_TONGYUN_HISTORY = [
    {"年": -476, "紀年": "周敬王四十三年甲子", "運": "男女交親", "卦": "震", "爻": "初九"},
    {"年": -308, "紀年": "周赧王六年壬子", "運": "男女交親", "卦": "巽", "爻": "初六"},
    {"年": -116, "紀年": "漢武帝元鼎元年甲子", "運": "男女交親", "卦": "恆", "爻": "初六"},
    {"年": 84, "紀年": "漢明帝永平七年甲子", "運": "男女交親", "卦": "益", "爻": "初九"},
    {"年": 244, "紀年": "魏邵陵公正始五年甲子", "運": "男女交親", "卦": "坎", "爻": "初六"},
    {"年": 412, "紀年": "晉安帝義熙八年壬子", "運": "男女交親", "卦": "離", "爻": "初九"},
    {"年": 604, "紀年": "隋文帝仁壽四年甲子", "運": "男女交親", "卦": "既濟", "爻": "初九"},
    {"年": 785, "紀年": "唐德宗興元二年甲子", "運": "男女交親", "卦": "未濟", "爻": "初九"},
    {"年": 964, "紀年": "宋太祖乾德二年甲子", "運": "男女交親", "卦": "艮", "爻": "初六"},
    {"年": 1142, "紀年": "金太宗會寧十年壬子", "運": "男女交親", "卦": "兌", "爻": "初九"},
    {"年": 1260, "紀年": "元大定元年甲子", "運": "男女交親", "卦": "損", "爻": "初九"},
    {"年": 1384, "紀年": "明洪武十七年甲子", "運": "男女交親", "卦": "損", "爻": "六三"},
    {"年": 1444, "紀年": "明正統九年甲子", "運": "男女交親", "卦": "損", "爻": "六五"},
    {"年": 1468, "紀年": "明成化四年戊子", "運": "男女交親", "卦": "損", "爻": "上九"},
    {"年": 1504, "紀年": "明弘治十七年甲子", "運": "男女交親", "卦": "咸", "爻": "初六"},
    {"年": 1528, "紀年": "明嘉靖七年戊子", "運": "男女交親", "卦": "咸", "爻": "九二"},
]

_YAO_HUOFU = {
    1: "建功立德之限；革命相繼而立，災變尚輕",
    2: "時之正旺，歷數綿遠，安平之限",
    3: "內極災變之限；陽雖失位，天下亦得安靜",
    4: "凶亂後待治之限",
    5: "君弱臣強，后妃外戚專政，近外極之限",
    6: "外極災變之限；重者失地亡國",
}


def _gua_line_bits(gua_name):
    """取卦六爻陰陽（下初至上），7/9為陽、6/8為陰。"""
    for code, name in sixtyfourgua.items():
        if name != gua_name:
            continue
        bits = tuple(code) if isinstance(code, tuple) else (code,)
        for b in bits:
            if len(b) == 6:
                return [c in _YANG_GUA_LINE for c in b]
    return [True, True, True, True, True, True]


def _build_tongyun_segments():
    segs = []
    pos = 0
    for yun, total, guas, durations in _TONGYUN_YUN_DEF:
        if not durations:
            base = total // len(guas)
            durations = [base] * len(guas)
            durations[-1] += total - sum(durations)
        for gua, years in zip(guas, durations):
            segs.append({
                "運": yun, "卦": gua, "年數": years,
                "週期起": pos, "週期迄": pos + years,
            })
            pos += years
    return segs


_TONGYUN_SEGMENTS = _build_tongyun_segments()


def _tongyun_cycle_pos(year):
    jinian = year - _TONGYUN_EPOCH
    return (jinian - 1 + _TONGYUN_YINGCHA + _TONGYUN_CAL) % _TONGYUN_CYCLE


def _locate_tongyun(pos):
    for seg in _TONGYUN_SEGMENTS:
        if seg["週期起"] <= pos < seg["週期迄"]:
            return seg, pos - seg["週期起"]
    return _TONGYUN_SEGMENTS[-1], 0


def _yao_weights(gua_name):
    weights = gua_yao_years.get(gua_name)
    if weights:
        return weights
    lines = _gua_line_bits(gua_name)
    return [36 if y else 24 for y in lines]


def _locate_yao(gua_name, offset_in_gua):
    weights = _yao_weights(gua_name)
    lines = _gua_line_bits(gua_name)
    total = sum(weights)
    if offset_in_gua >= total:
        i = 5
        yang = lines[i]
        name = (_YAO_NAMES_YANG if yang else _YAO_NAMES_YIN)[i]
        return i + 1, name, yang, weights[i], offset_in_gua - sum(weights[:i]) + 1
    acc = 0
    for i, w in enumerate(weights):
        if acc + w > offset_in_gua:
            yang = lines[i]
            name = (_YAO_NAMES_YANG if yang else _YAO_NAMES_YIN)[i]
            return i + 1, name, yang, w, offset_in_gua - acc + 1
        acc += w
    i = 5
    yang = lines[i]
    return 6, (_YAO_NAMES_YANG if yang else _YAO_NAMES_YIN)[i], yang, weights[i], 1


def tongyun_shier_yun():
    """十二運立成表（卷十二「明太乙統運紀元立成術」）。"""
    rows = []
    for yun, total, guas, durations in _TONGYUN_YUN_DEF:
        if not durations:
            base = total // len(guas)
            durations = [base] * len(guas)
            durations[-1] += total - sum(durations)
        rows.append({
            "運": yun,
            "總年": total,
            "卦數": len(guas),
            "卦序": guas,
            "各卦年數": dict(zip(guas, durations)),
        })
    return {
        "大週": _TONGYUN_CYCLE,
        "起運": "天地否泰（乾坤否泰）",
        "終運": "物極元終（睽革）",
        "十二運": rows,
    }


def tongyun_rugua(year):
    """統運入卦紀年（卷十二「明太乙統運八卦紀年術」）。"""
    pos = _tongyun_cycle_pos(year)
    seg, gua_off = _locate_tongyun(pos)
    yao_idx, yao_name, yang, yao_total, yao_off = _locate_yao(seg["卦"], gua_off)
    zhou = pos // _TONGYUN_CYCLE
    return {
        "公元年": year,
        "統運積年": year - _TONGYUN_EPOCH,
        "週期位置": pos,
        "週期序": zhou + 1,
        "運": seg["運"],
        "卦": seg["卦"],
        "卦符": gua.get(_KING_WEN_64.index(seg["卦"]) + 1, ""),
        "入卦年數": gua_off + 1,
        "爻": yao_idx,
        "爻名": yao_name,
        "陽爻": yang,
        "入爻年數": yao_off,
        "爻策": yao_total,
        "斷語": _YAO_HUOFU.get(yao_idx, ""),
    }


def tongyun_xingyao_huofu(yao_idx):
    """入運行爻禍福（卷十二「明太乙入運行爻，災變禎祥」）。"""
    return {
        "爻位": yao_idx,
        "所主": _YAO_HUOFU.get(yao_idx, ""),
        "要訣": "初建功、二五安平、三內極、四待治、五君弱、六外極；二五得中為上吉",
    }


def tongyun_lishi():
    """行運入卦歷史例（卷十二「明太乙行運八卦紀年術」）。"""
    return list(_TONGYUN_HISTORY)


def liunian_zhigua(year, year_gan=None, year_zhi=None):
    """流年太歲直卦（卷十二「明太乙數流年太歲直卦術」）。"""
    if year_gan is None or year_zhi is None:
        gz = gangzhi(year, 6, 15, 12, 0)
        year_gan, year_zhi = gz[0][0], gz[0][1]
    upper = _KING_WEN_64.index("乾") + 1
    for i, name in enumerate(_KING_WEN_64, start=1):
        if name == "乾":
            upper = i
            break
    idx = (year - 4) % 64
    if idx < 0:
        idx += 64
    gua_idx = idx + 1
    gua_name = _KING_WEN_64[idx]
    lines = _gua_line_bits(gua_name)
    yang_year = year_gan in _YANG_GAN
    yang_pos = [i for i, y in enumerate(lines) if y]
    yin_pos = [i for i, y in enumerate(lines) if not y]
    zhi_order = list(di_zhi)
    zhi_idx = zhi_order.index(year_zhi)
    if yang_year:
        active = yang_pos[zhi_idx % len(yang_pos)] if yang_pos else 0
        direction = "陽年自下而上"
    else:
        active = yin_pos[zhi_idx % len(yin_pos)] if yin_pos else 0
        direction = "陰年自上而下"
    yao_name = (_YAO_NAMES_YANG if lines[active] else _YAO_NAMES_YIN)[active]
    return {
        "年": year,
        "干支": f"{year_gan}{year_zhi}",
        "陽年": yang_year,
        "直卦": gua_name,
        "卦符": gua.get(gua_idx, ""),
        "直事爻": active + 1,
        "爻名": yao_name,
        "命爻法": direction,
        "要訣": "卦為歲之事，爻為歲之時；變卦為後六月",
    }


def vol12_zonghe(year, year_gan=None, year_zhi=None, month=1, day=15):
    """卷十二綜合：統運入卦、入爻禍福、十二運立成、流年直卦、歷史例、首尾變卦觀象期。"""
    from .tongyun_extras import vol12_extended
    rugua = tongyun_rugua(year)
    ext = vol12_extended(year, year_gan, year_zhi, month, day)
    return {
        "統運入卦": rugua,
        "十二運立成": tongyun_shier_yun(),
        "入爻禍福": tongyun_xingyao_huofu(rugua["爻"]),
        "流年直卦": liunian_zhigua(year, year_gan, year_zhi),
        "歷史入爻": tongyun_lishi(),
        "災厄首尾": ext["災厄首尾"],
        "變卦納甲": ext["變卦納甲"],
        "觀象期": ext["觀象期"],
        "歲本建子": ext["歲本建子"],
        "要訣": (
            f"自周敬王四十三年起算，加卦盈差{_TONGYUN_YINGCHA}，"
            f"{_TONGYUN_CYCLE}年一週；當前入{rugua['運']}之{rugua['卦']}{rugua['爻名']}；"
            f"變卦{ext['變卦納甲']['變卦']}"
        ),
    }


def biannian_zonghe(year):
    """統運八卦行支編年、歷史驗例。"""
    from .biannian import zonghe
    return zonghe(year)


def gua_xiang_zonghe(year):
    """統十二運卦象、當年入卦觀象。"""
    from .gua_xiang import zonghe
    return zonghe(year)


def fenye_zonghe(ty, year_zhi=None):
    """九宮十二分野、絳宮明堂玉堂。"""
    from .fenye import zonghe
    return zonghe(ty, year_zhi)


def guiyun_zonghe(taiyi_acumyear, year=None, month=1, day=15):
    """大小遊軌運、重卦策數、陽九百六限數。"""
    from .guiyun import zonghe
    return zonghe(taiyi_acumyear, year, month, day)


def vol10_zonghe(year_gan, year_zhi, ty, skyeyes, shiji, taiyi_acumyear=0):
    """卷十綜合：五運六氣、天目合會、九宮貴神歲會。"""
    ty_n = ty if isinstance(ty, int) else gong.get(ty)
    ty_name = num2gong(ty_n) if ty_n else ""
    wq = wuyun_tianmu_hehui(year_gan, year_zhi, ty_n, skyeyes, shiji, ty_name)
    gods = nine_palace_gods(taiyi_acumyear % 360)
    hui = list(wq.get("歲會天符", []))
    dist = gods.get("九宮貴神分布", {})
    if ty_name and ty_name in dist:
        hui.append(f"直事貴神臨{ty_name}（{dist[ty_name]}，歲會）")
    return {
        "五運六氣": wq,
        "九宮貴神": gods,
        "天目合會": wq.get("天目合會", []),
        "歲會天符": hui,
        "要訣": wq.get("要訣", ""),
    }


def yunqi_zonghe(taiyi_acumyear, ty):
    """十精所主、雲氣合會。"""
    from .yunqi import zonghe
    ty_n = ty if isinstance(ty, int) else gong.get(ty)
    return zonghe(taiyi_acumyear, ty_n)


def junshi_zhanduan(ty, home_cal, away_cal, skyeyes, shiji, skyeyes_des,
                    home_gen, home_vgen, away_gen, away_vgen,
                    three_doors, five_gens, geju=None, sf_mask=False, ty_door=None,
                    sf_hit=False, sf_ge=False, wangzhuai=None):
    """卷十七軍事占斷綜合"""
    return {
        "出兵用時": chubing_yongshi(
            home_cal, away_cal, skyeyes_des, sf_mask, three_doors, five_gens, ty_door),
        "敵國動靜": diguo_dongjing(
            away_cal, three_doors, five_gens, ty, skyeyes, shiji,
            home_gen, home_vgen, away_gen, away_vgen, skyeyes_des, geju),
        "間諜虛實": jianmie_xushi(ty, shiji, away_gen, skyeyes),
        "敵使虛實": dishi_xushi(ty, shiji, away_gen),
        "敵兵來方": dibing_laifang(ty, away_cal, shiji),
        "見聞虛實": jianwen_xushi(
            ty, skyeyes, shiji, skyeyes_des, three_doors, five_gens,
            geju, sf_mask, sf_hit, home_gen, home_vgen, away_gen, away_vgen),
        "討捕叛亡": taobu_panwang(
            ty, skyeyes, shiji, home_gen, geju, skyeyes_des, sf_mask, wangzhuai),
        "執囚對吏": zhiqu_duili(
            ty, skyeyes, home_gen, home_cal, geju, sf_mask, sf_hit, wangzhuai),
        "求索所得": qiusuo_suode(
            ty, skyeyes, home_gen, geju, skyeyes_des, sf_ge, wangzhuai),
        "孤虛對照": guxu_duizhao(
            ty, skyeyes, home_gen, geju, skyeyes_des, sf_ge, wangzhuai),
        "時計諸事": shiji_zhanshi(
            ty, skyeyes, skyeyes_des, three_doors, five_gens,
            home_cal, away_cal, geju, sf_mask, sf_hit, wangzhuai),
    }


# ======================  太乙統宗寶鑑 卷二／卷七：神將所主斷語  ======================
# 十六宮間神（卷二）、八門所主（卷二）、天乙／地乙／直符／四神（卷七）

_SIXTEEN_GOD_SUOZHU = {
    "地主": "建子之月，陽氣初動，萬物在下，水性潤下",
    "陽德": "建丑之月，二陽用事，龍見于田，布育萬物",
    "和德": "春夏將交，陰陽氣和，群物萌生，主和集成就",
    "呂申": "建寅之月，陽氣大申，草木甲拆，主運謀主宰",
    "高叢": "建卯之月，木氣大旺，萬物皆自地發生",
    "太陽": "建辰之月，五陽正盛，飛龍在天，主厄會兵戈",
    "大炅": "春夏將交，光明發越，萬物潔齊，主號令迅速",
    "大神": "建巳之月，六陽大備，火神司權，萬物長盛",
    "大威": "建午之月，陽謝陰生，火神炳化，刑暴始行",
    "天道": "夏秋之交，天道運行，萬物將成",
    "大武": "夏秋之交，陰氣敷施，萬物有戕傷之兆",
    "武德": "建申之月，金氣始旺，肅殺司權",
    "太簇": "建酉之月，萬物成熟，大有品類",
    "陰主": "建戌之月，五陰正盛，萬物告成",
    "陰德": "秋冬將交，陰中胎陽，大有其德",
    "大義": "建亥之月，六陰大備，水神司權，萬物懷妊",
}

_GOOD_DOORS = frozenset("開休生")

_EIGHT_DOOR_WIND = {
    "開": "不周風", "休": "廣莫風", "生": "調風", "傷": "民庶風",
    "杜": "清明風", "景": "景風", "死": "涼風", "驚": "闔闔風",
}

_EIGHT_DOOR_SUOZHU = {
    "開": {
        "方位": "乾宮西北",
        "門名": "天啟開門",
        "八風": "不周風",
        "所主": "宜遠行拓土、所向通達，凡舉百事皆吉",
        "吉凶": "大吉",
    },
    "休": {
        "方位": "坎宮正北",
        "門名": "建章休門",
        "八風": "廣莫風",
        "所主": "宜進賢聚衆、安息休兵、收貯財寶，以北行戰勝大獲",
        "吉凶": "大吉",
    },
    "生": {
        "方位": "艮宮東北",
        "門名": "物戶生門",
        "八風": "調風",
        "所主": "宜拜將求賢、結和百群，征伐宜出東北",
        "吉凶": "大吉",
    },
    "傷": {
        "方位": "震宮正東",
        "門名": "雷霆傷門",
        "八風": "民庶風",
        "所主": "主災傷疾病，宜漁獵捕利，向東行道逢盜賊見血光",
        "吉凶": "大凶",
    },
    "杜": {
        "方位": "巽宮東南",
        "門名": "耀武杜門",
        "八風": "清明風",
        "所主": "主閉塞固守安行，凡舉百事皆凶",
        "吉凶": "大凶",
    },
    "景": {
        "方位": "離宮正南",
        "門名": "赤帝景門",
        "八風": "景風",
        "所主": "主鬼怪遺亡，宜講明理亂、犒勞將卒、突陣破圍",
        "吉凶": "小吉",
    },
    "死": {
        "方位": "坤宮西南",
        "門名": "審順死門",
        "八風": "涼風",
        "所主": "主死喪奠埋，宜捕獵行刑，西南方不宜出兵",
        "吉凶": "大凶",
    },
    "驚": {
        "方位": "兌宮正西",
        "門名": "武雷驚門",
        "八風": "闔闔風",
        "所主": "主驚恐奔走，宜掩捕攻擊伏兵，凡百舉事憂禍隨之",
        "吉凶": "小凶",
    },
}

_NINE_PALACE_SUOZHU = {
    1: {
        "宮名": "乾", "別名": "天門", "分野": "冀州、并州",
        "所主": "太乙初判引一函三，乾為天為首",
        "通變": "文昌關囚，必有迫挾君父之象",
        "觸發": "wc_trap",
    },
    2: {
        "宮名": "離", "別名": "明堂", "分野": "文明之位",
        "所主": "人君居明堂審順逆察奸邪，有兵戈獄訟之象",
        "通變": "太乙臨之，君誅將相",
        "觸發": "ty_here",
    },
    3: {
        "宮名": "艮", "別名": "", "分野": "青州",
        "所主": "三陽交泰萬物咸成，主后妃",
        "通變": "始擊臨之，嬖寵進中宮，兵革興",
        "觸發": "sj_here",
    },
    4: {
        "宮名": "震", "別名": "", "分野": "徐州",
        "所主": "陽氣壯盛，長男主器好施以仁",
        "通變": "始擊臨之，西戎兵侵",
        "觸發": "sj_here",
    },
    5: {
        "宮名": "中", "別名": "樞紐", "分野": "",
        "所主": "天之樞紐斡旋八方，太乙行考治而不居",
        "通變": "",
        "觸發": None,
    },
    6: {
        "宮名": "兌", "別名": "", "分野": "雍州",
        "所主": "陰氣敷施，萬物有戕傷之兆",
        "通變": "客大臨之，南楚兵侵",
        "觸發": "ad_here",
    },
    7: {
        "宮名": "坤", "別名": "", "分野": "西南州郡",
        "所主": "陽化純陰，陰氣溫舒",
        "通變": "客大所臨，其應在衝",
        "觸發": "ad_here",
    },
    8: {
        "宮名": "坎", "別名": "端門", "分野": "兗州",
        "所主": "坐坎離朝南北之正，上應紫微",
        "通變": "太乙臨也大臣受誅；二目因對大臣伏誅",
        "觸發": "ty_here",
    },
    9: {
        "宮名": "巽", "別名": "", "分野": "揚州",
        "所主": "天傾西北地缺東南，乾健巽入",
        "通變": "客大臨之，北狄兵侵",
        "觸發": "ad_here",
    },
}

_JUEYI_PALACES = {
    "絕陽": {1},
    "絕陰": {9},
    "絕氣": {4, 6},
    "易氣": {2, 8},
}

_DAYOU_TM_PATH = [
    "未", "坤", "坤", "申", "酉", "戌", "乾", "乾", "亥", "子",
    "丑", "艮", "寅", "卯", "辰", "巽", "巳", "午",
]

_DAYOU_TM_BASE = (
    "大遊天目土神，巡行下土主威利訪察；敷德惠恤軍民納規諫則無傾危，"
    "惰政黜忠興徭役則傾覆不旋踵"
)

_DAYOU_XIONG = {
    1: "不利于君王",
    2: "不利于王侯臣宰",
    3: "不利于后妃",
    4: "不利于太子",
    5: "不利于民",
    6: "不利于師帥",
}

_XIAOYOU_BASE = "小遊太乙主飢饉、兵革、水旱流亡"

_TIANYI_BASE = "天乙金神，馭六宮金炁，主兵革殺戮；臨之即有勝負，兵戈大起，人民流血千里"
_DIYI_BASE = "地乙土神，掌地方域浮載而行；臨無道之邦主飛蝗疾疫、五穀不登、庶民流亡"
_ZHIFU_BASE = "直符火神，天帝使者觀察治道；臨失道之邦主火光旱涸、兵革疾疫、飢饉大作"
_SIGOD_BASE = "四神水神，紀綱有道則昌、無道則殃；臨克戰之邦主水旱兵荒、盜賊侵掠"


def _god_at_chen(chen):
    if not chen:
        return None
    for god, z in sixteengod.items():
        if z == chen:
            return god
    return None


def sixteen_god_zhu(chen):
    """單一辰位所臨十六宮間神所主（卷二）。"""
    god = _god_at_chen(chen)
    if not god:
        return {}
    return {
        "辰": chen,
        "神": god,
        "所主": _SIXTEEN_GOD_SUOZHU.get(god, ""),
    }


def sixteen_gods_table():
    """十六宮間神定局（卷二「明太乙十六宮間之神」）。"""
    return [
        {"辰": z, "神": god, "所主": _SIXTEEN_GOD_SUOZHU.get(god, "")}
        for god, z in sixteengod.items()
    ]


def _chen_gong(chen):
    if not chen:
        return None
    if isinstance(chen, int):
        return chen
    if chen == "中":
        return 5
    return gong2.get(chen)


def _palace_label(pos):
    """間辰或九宮序數 → 顯示用宮名。"""
    if pos is None or pos == "":
        return ""
    if isinstance(pos, int):
        return num2gong(pos) or ""
    return str(pos)


def _same_palace(a, b):
    if a is None or b is None:
        return False
    if a == b:
        return True
    ga, gb = _chen_gong(a), _chen_gong(b)
    return bool(ga and gb and ga == gb)


def _god_duanyu(block):
    """神將所主顯示斷語：有合宮則取合宮，否則取本象。"""
    if not block:
        return ""
    combo = block.get("合宮") or []
    real = [c for c in combo if c and not str(c).startswith("無特殊")]
    if real:
        return "；".join(real)
    return block.get("本象", "")


def _door_good(door):
    return door in _GOOD_DOORS if door else False


def nine_palace_suozhu(ty, skyeyes=None, shiji=None, home_gen=None, away_gen=None,
                       skyeyes_des=None, geju=None):
    """九宮所主與通變（卷二「明太乙九宮所主術」「明太乙九宮通變術」）。"""
    if not ty:
        return {}
    base = _NINE_PALACE_SUOZHU.get(ty, {})
    sj_g = _chen_gong(shiji)
    ad_g = away_gen if away_gen and away_gen != 5 else None
    triggered = []
    trap = geju and any("關囚" in k for k in geju)
    if ty == 1 and trap:
        triggered.append(base.get("通變", ""))
    elif base.get("觸發") == "ty_here":
        triggered.append(base.get("通變", ""))
    elif base.get("觸發") == "sj_here" and sj_g == ty:
        triggered.append(base.get("通變", ""))
    elif base.get("觸發") == "ad_here" and ad_g == ty:
        triggered.append(base.get("通變", ""))
    note = "關囚掩迫格擊對挾杜固之年驗之必矣；三才美和無囚迫則所主為輕"
    return {
        "太乙落宮": num2gong(ty),
        "宮名": base.get("宮名", ""),
        "分野": base.get("分野", ""),
        "所主": base.get("所主", ""),
        "通變": triggered or ["本局無特殊通變"],
        "九宮定局": [
            {"宮": num2gong(g), **{k: v for k, v in info.items() if k != "觸發"}}
            for g, info in _NINE_PALACE_SUOZHU.items()
        ],
        "要訣": note,
    }


def yinyang_jueyi(ty, skyeyes=None, shiji=None, home_gen=None, away_gen=None,
                  home_vgen=None, away_vgen=None, geju=None):
    """陰陽絕易之宮（卷二「明太乙在陰陽絕易之宮術」）。"""
    entities = {
        "太乙": ty,
        "天目": _chen_gong(skyeyes),
        "始擊": _chen_gong(shiji),
        "主大": home_gen if home_gen != 5 else None,
        "主參": home_vgen if home_vgen != 5 else None,
        "客大": away_gen if away_gen != 5 else None,
        "客參": away_vgen if away_vgen != 5 else None,
    }
    hits = []
    for label, kind, note in (
        ("絕陽", "絕陽", "一宮陰極絕於陽，歲計大凶"),
        ("絕陰", "絕陰", "九宮陽極絕於陰，歲計大凶"),
        ("絕氣", "絕氣", "四六宮氣交而漸衰，有凶變"),
        ("易氣", "易氣", "二八宮陰陽氣交，舉事皆慎"),
    ):
        palaces = _JUEYI_PALACES[kind]
        names = [n for n, g in entities.items() if g in palaces]
        if names:
            hits.append({
                "類型": label,
                "臨神": names,
                "宮位": [num2gong(p) for p in palaces],
                "斷語": note,
            })
    bad = bool(geju)
    cautions = []
    if hits and bad:
        cautions.append("更會掩迫囚擊格挾杜固之年，禍患深重，除舊更新")
    elif hits:
        cautions.append("遇凶格局則災重；三才美和則災尚輕，凡百舉事慎而勿用")
    return {
        "臨宮": hits or ["本局諸神不臨絕易之宮"],
        "有凶格局": bad,
        "斷語": "；".join(cautions) if cautions else "無絕易臨宮",
    }


def _door_menju(doors, ty, skyeyes, shiji, home_gen, away_gen):
    """八門門具（卷二「明太乙八門通變術」）。"""
    if not doors:
        return {}
    sky_g = _chen_gong(skyeyes)
    sj_g = _chen_gong(shiji)
    items = {}
    if sky_g and not _door_good(doors.get(sky_g)):
        items["太乙門具"] = f"天目在{num2gong(sky_g)}臨{doors.get(sky_g)}門，不在開休生下"
    ty_d = doors.get(ty, "")
    wc_d = doors.get(sky_g, "") if sky_g else ""
    if home_gen and home_gen != 5 and not _door_good(ty_d) and not _door_good(wc_d):
        items["主門具"] = f"太乙天目不在開休生三門下（太乙{ty_d}、天目{wc_d}）"
    sj_d = doors.get(sj_g, "") if sj_g else ""
    if away_gen and away_gen != 5 and not _door_good(ty_d) and not _door_good(sj_d):
        items["客門具"] = f"太乙始擊不在開休生三門下（太乙{ty_d}、始擊{sj_d}）"
    return items


def eight_door_suozhu(doors, ty, door_value=None, wangzhuai=None,
                      skyeyes=None, shiji=None, home_gen=None, away_gen=None):
    """八門所主、通變與分布（卷二「明太乙八門所主術」「明太乙八門通變術」）。"""
    if not doors:
        return {}
    items = []
    for gong, d in doors.items():
        info = _EIGHT_DOOR_SUOZHU.get(d, {})
        wx = wangzhuai.get(gong, "") if wangzhuai else ""
        items.append({
            "宮": num2gong(gong),
            "門": d,
            "門名": info.get("門名", ""),
            "八風": info.get("八風", _EIGHT_DOOR_WIND.get(d, "")),
            "所主": info.get("所主", ""),
            "吉凶": info.get("吉凶", ""),
            "旺衰": wx,
        })
    ty_door = doors.get(ty)
    ty_info = _EIGHT_DOOR_SUOZHU.get(ty_door, {}) if ty_door else {}
    val_info = _EIGHT_DOOR_SUOZHU.get(door_value, {}) if door_value else {}
    menju = _door_menju(doors, ty, skyeyes, shiji, home_gen, away_gen)
    tongbian = []
    for gong, d in doors.items():
        wx = wangzhuai.get(gong, "") if wangzhuai else ""
        info = _EIGHT_DOOR_SUOZHU.get(d, {})
        if d in "死傷驚" and wx in ("旺", "相"):
            tongbian.append(f"{num2gong(gong)}臨{d}門旺相，兵喪疾疫血光之災倍之")
        elif d in "死傷驚" and wx in ("囚", "死"):
            tongbian.append(f"{num2gong(gong)}臨{d}門受制，災減半")
    if shiji and home_gen and home_gen != 5:
        sj_g = _chen_gong(shiji)
        if sj_g == home_gen and doors.get(home_gen) in "杜死驚":
            tongbian.append("始擊同主大在杜死驚門下，主口舌妖言")
    return {
        "值事八門": door_value,
        "值事所主": val_info.get("所主", ""),
        "太乙所臨門": ty_door,
        "太乙門所主": ty_info.get("所主", ""),
        "太乙門吉凶": ty_info.get("吉凶", ""),
        "八門分布": items,
        "門具": menju or {"無": "三門皆具"},
        "通變": tongbian or ["吉門臨旺相則福倍，凶門臨旺相則禍倍"],
        "要訣": "遇開休生三門大吉，景門小吉；杜傷死大凶，驚門小凶",
    }


def bigyo_years_in(taiyi_acumyear):
    """大遊入宮年數（三十六為一宮）。"""
    rem = (taiyi_acumyear + 34) % 288
    years = rem % 36
    return years or 36


def bigyo_tianmu(taiyi_acumyear):
    """大遊天目（卷七「明大遊天目所主術」）。"""
    rem = (taiyi_acumyear + 214) % 180
    shen_rem = rem % 18 or 18
    chen = _DAYOU_TM_PATH[shen_rem - 1]
    return {
        "落辰": chen,
        "神": _god_at_chen(chen),
        "入神年數": shen_rem,
        "本象": _DAYOU_TM_BASE,
    }


def dayou_suozhu(taiyi_acumyear, ty, big, tiany=None, earthy=None, fgod=None,
                 zhifu=None, small=None, wufu=None):
    """大遊所主、凶筭與合宮（卷七）。"""
    years = bigyo_years_in(taiyi_acumyear)
    cat = (years - 1) % 6 + 1
    xiong = _DAYOU_XIONG[cat]
    if big == ty:
        xiong = f"與太乙同行，{xiong}"
    rules = [
        (wufu, "五福", "兵革之災降于對沖之分"),
        (tiany, "天乙", "大兵革為害災變怪異"),
        (earthy, "地乙", "盜賊飛蝗、草木不生"),
        (zhifu, "直符", "刀兵大旱"),
        (fgod, "四神", "水旱飢饉、人民流移"),
        (small, "小游", "兵喪水旱凶暴大作"),
    ]
    combo = _combo_notes(big, ty, earthy, fgod, zhifu, big, small, rules)
    tm = bigyo_tianmu(taiyi_acumyear)
    return {
        "落宮": num2gong(big) if big else "",
        "入宮年數": years,
        "滿宮": years == 36,
        "凶筭": years if years < 36 else None,
        "凶筭所主": xiong if years < 36 else "滿三十六算，不論凶筭",
        "大遊天目": tm,
        "合宮": combo or ["無特殊合宮"],
    }


def xiaoyou_suozhu(small, fgod=None, zhifu=None, tiany=None, earthy=None,
                   wufu=None, kingbase=None, officerbase=None, pplbase=None):
    """小遊所主（卷七「明小遊太乙所主術」）。"""
    kb = _chen_gong(kingbase)
    ob = _chen_gong(officerbase)
    pb = _chen_gong(pplbase)
    rules = [
        (fgod, "四神", "主飢荒"),
        (zhifu, "直符", "兵戈大起"),
        (tiany, "天乙", "天降災于民"),
        (earthy, "地乙", "大旱寸草不生"),
        (wufu, "五福", "災變為福"),
        (kb, "君基", "其分君有災，不宜奔兵"),
        (ob, "臣基", "卿大夫不利，有兵厄"),
        (pb, "民基", "其分民有災疾"),
    ]
    combo = _combo_notes(small, None, earthy, fgod, zhifu, None, small, rules)
    block = {
        "落宮": _palace_label(small),
        "本象": _XIAOYOU_BASE,
        "合宮": combo or ["無特殊合宮"],
    }
    block["斷語"] = _god_duanyu(block)
    return block


def _combo_notes(entity, ty, earthy, fgod, zhifu, big, small, rules):
    notes = []
    for other, key, text in rules:
        if _same_palace(entity, other):
            notes.append(f"與{key}同宮（{_palace_label(other)}）：{text}")
    if ty and _same_palace(entity, ty):
        notes.append(f"與太乙同宮（{_palace_label(ty)}）：即有勝負變化，兵戈大起")
    return notes


def tianyi_suozhu(tiany, ty=None, earthy=None, fgod=None, zhifu=None, big=None, small=None):
    """天乙金神所主（卷七）。"""
    rules = [
        (earthy, "地乙", "兵戈發土工，廢農桑，盜賊凶攘，人民愁困"),
        (zhifu, "直符", "大旱刀兵飢饉，人民愁困疫病"),
        (fgod, "四神", "水澇霜雪，兵喪舟車不通，盜賊四起"),
        (big, "大游", "兵喪禍亂，飢兵流亡"),
        (small, "小游", "下凌於上，不利其事"),
    ]
    combo = _combo_notes(tiany, ty, earthy, fgod, zhifu, big, small, rules)
    block = {
        "落宮": _palace_label(tiany),
        "本象": _TIANYI_BASE,
        "合宮": combo or ["無特殊合宮，主兵革之事"],
    }
    block["斷語"] = _god_duanyu(block)
    return block


def diyi_suozhu(earthy, zhifu=None, fgod=None, big=None, small=None):
    """地乙土神所主（卷七）。"""
    rules = [
        (zhifu, "直符", "大旱兵盜土工興，人民受病，五穀不成"),
        (fgod, "四神", "水旱不調，民多病困，地生妖異"),
        (big, "大游", "兵喪大作，荒民流，盜賊蜂起"),
        (small, "小游", "土木興，法令暴虐，主兵盜"),
    ]
    combo = _combo_notes(earthy, None, earthy, fgod, zhifu, big, small, rules)
    block = {
        "落宮": _palace_label(earthy),
        "本象": _DIYI_BASE,
        "合宮": combo or ["無特殊合宮，主方域載行"],
    }
    block["斷語"] = _god_duanyu(block)
    return block


def zhifu_suozhu(zhifu, fgod=None, big=None, small=None):
    """直符火神所主（卷七）。"""
    rules = [
        (fgod, "四神", "旱涸乾不均，四時失節，民飢疾疫，兵盜水火刀兵之厄"),
        (big, "大游", "兵喪民流，五穀不成，災橫暴起"),
        (small, "小游", "火發兵革，人民不安"),
    ]
    combo = _combo_notes(zhifu, None, None, fgod, zhifu, big, small, rules)
    block = {
        "落宮": _palace_label(zhifu),
        "本象": _ZHIFU_BASE,
        "合宮": combo or ["無特殊合宮，主察治道理政"],
    }
    block["斷語"] = _god_duanyu(block)
    return block


def sigod_suozhu(fgod, tiany=None, earthy=None, zhifu=None, big=None, small=None):
    """四神水神所主（卷七）。"""
    rules = [
        (tiany, "天乙", "天降大雨為災"),
        (earthy, "地乙", "河走地陷大水為災"),
        (zhifu, "直符", "水旱兵革飢饉之事"),
        (big, "大游", "兵喪飢饉，人民流亡"),
        (small, "小游", "人民不安，多主水澇疾疫"),
    ]
    combo = _combo_notes(fgod, None, earthy, fgod, zhifu, big, small, rules)
    block = {
        "落宮": _palace_label(fgod),
        "本象": _SIGOD_BASE,
        "合宮": combo or ["無特殊合宮，水神紀綱之道"],
    }
    block["斷語"] = _god_duanyu(block)
    return block


def shenjiang_suozhu(ty, skyeyes, shiji, se, tiany, earthy, fgod, zhifu,
                     doors, door_value=None, wangzhuai=None, big=None, small=None,
                     accnum=None, skyeyes_des=None, home_gen=None, away_gen=None,
                     home_vgen=None, away_vgen=None, geju=None, wufu=None,
                     kingbase=None, officerbase=None, pplbase=None):
    """神將所主綜合（卷二、卷七）。"""
    geju = geju or {}
    return {
        "十六宮間神": {
            "天目所臨": sixteen_god_zhu(skyeyes),
            "始擊所臨": sixteen_god_zhu(shiji),
            "定目所臨": sixteen_god_zhu(se),
            "十六神定局": sixteen_gods_table(),
        },
        "九宮所主": nine_palace_suozhu(
            ty, skyeyes, shiji, home_gen, away_gen, skyeyes_des, geju),
        "陰陽絕易": yinyang_jueyi(
            ty, skyeyes, shiji, home_gen, away_gen, home_vgen, away_vgen, geju),
        "八門所主": eight_door_suozhu(
            doors, ty, door_value, wangzhuai, skyeyes, shiji, home_gen, away_gen),
        "天乙所主": tianyi_suozhu(tiany, ty, earthy, fgod, zhifu, big, small),
        "地乙所主": diyi_suozhu(earthy, zhifu, fgod, big, small),
        "直符所主": zhifu_suozhu(zhifu, fgod, big, small),
        "四神所主": sigod_suozhu(fgod, tiany, earthy, zhifu, big, small),
        "大遊所主": dayou_suozhu(
            accnum, ty, big, tiany, earthy, fgod, zhifu, small, wufu) if accnum else {},
        "小遊所主": xiaoyou_suozhu(
            small, fgod, zhifu, tiany, earthy, wufu, kingbase, officerbase, pplbase),
    }
