
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 27 18:11:44 2022
@author: kentang
Optimized for performance
"""
import re
import time
import itertools
from datetime import date
from ephem import Date
import numpy as np
from cn2an import an2cn
from taiyidict import tengan_shiji, su_dist
#import kinliuren
#from kinliuren import kinliuren
import config
import chart
import jieqi
import taiyi_life_dict
from jieqi import jieqi_name

class Taiyi:
    """憭芯�韏瑞𥿢銝餉��賣彍"""
    def __init__(self, year, month, day, hour, minute):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.door = list("�衤��笔��𨀣艶甇駁�")
        # Cache for expensive computations
        self.cache = {}
        # Precompute static mappings
        self.di_zhi = config.di_zhi
        self.di_zhi_reversed = list(reversed(self.di_zhi))
        self.jiazi_list = config.jiazi()
        self.jigod_map = dict(zip(self.di_zhi, config.new_list(self.di_zhi_reversed, "撖�")))
        self.jigod_map_r = dict(zip(list(reversed(self.di_zhi)), config.new_list(self.di_zhi, "��")))
        self.hegod_map = dict(zip(self.di_zhi, config.new_list(self.di_zhi_reversed, "銝�")))
        self.l_num = [8, 8, 3, 3, 4, 4, 9, 9, 2, 2, 7, 7, 6, 6, 1, 1]

    def _get_gangzhi(self):
        """Cache gangzhi results"""
        if 'gangzhi' not in self.cache:
            self.cache['gangzhi'] = jieqi.gangzhi(self.year, self.month, self.day, self.hour, self.minute)
        return self.cache['gangzhi']

    def _get_lunar_date(self):
        """Cache lunar date results"""
        if 'lunar_date' not in self.cache:
            self.cache['lunar_date'] = config.lunar_date_d(self.year, self.month, self.day)
        return self.cache['lunar_date']

    def jigod(self, ji_style):
        """閮��"""
        yy = self.kook( ji_style,0)["��"][0]
        if yy == "��":
            j = self.jigod_map.get(self.taishui(ji_style))
        if yy == "��":
            j = self.jigod_map_r.get(self.taishui(ji_style))
        return  j

    def taishui(self, ji_style):
        """憭芣革"""
        gang_zhi = self._get_gangzhi()
        return {0: gang_zhi[0][1], 1: gang_zhi[1][1], 2: gang_zhi[2][1], 3: gang_zhi[3][1], 4: gang_zhi[4][1], 5: gang_zhi[0][1]}.get(ji_style)

    def skyeyes_des(self, ji_style, taiyi_acumyear):
        """���憪𧢲��訫�"""
        kook = self.kook(ji_style, taiyi_acumyear)
        return dict(zip(range(1, 73), config.skyeyes_summary.get(kook.get("��")[0]))).get(kook.get("��"))

    def skyeyes(self, ji_style, taiyi_acumyear):
        """���(憭拍𤌍)"""
        kook = self.kook(ji_style, taiyi_acumyear)
        dun = kook.get("��")[0]
        num = kook.get("��")
        # �煾𨘥�文�嚗ōaiyi_acumyear=1嚗㗇𠯫閮���斤��𠰴云銋䠷��∪�蝬瓐�嚯ine55
        # �𣬚蔭蝛齿�嚗䔶誑���銝��鈭�縧銋页�銝滨椘嚗䔶誑憭拍𤌍�冽�����颱�嚗𥕦�銝滨椘嚗�𦶢韏瑟郎敺瘀�������蟡痹�
        #  ��苊敺瑕之甇佗��滨�銝�蝞堒�嚗�朖憭拍𤌍���其�����
        # 憭拍𤌍隞� 蝛齿𠯫 % 72 % 18 摰帋�嚗𠄎KYEYES_DICT �� 18 �冽�銵剁�嚗屸� mod72 摰帋���
        if ji_style == 2 and taiyi_acumyear == 1:
            jiri = self.accnum(2, taiyi_acumyear)
            idx = jiri % 72 % 18
            return config.skyeyes_dict.get(dun)[idx]
        return dict(zip(range(1, 73), config.skyeyes_dict.get(dun))).get(num)

    def hegod(self, ji_style):
        """���"""
        return self.hegod_map.get(self.taishui(ji_style))

    def accnum(self, ji_style, taiyi_acumyear):
        """蝛滚僑�貉�蝞�"""
        cache_key = f'accnum_{ji_style}_{taiyi_acumyear}'
        if cache_key in self.cache:
            return self.cache[cache_key]

        tndict = {0: 10153917, 1: 1936557, 2: 10154193, 3: 10153917}
        tn_c = tndict.get(taiyi_acumyear)
        lunar = self._get_lunar_date()
        lunar_year = lunar.get("撟�")
        lunar_month = lunar.get("��")
        lunar_day = lunar.get("��")

        if ji_style == 0:  # 撟渲�
            result = tn_c + lunar_year + (1 if lunar_year < 0 else 0)
        elif ji_style == 1:  # ���
            accyear = tn_c + lunar_year - 1 + (2 if lunar_year < 0 else 0)
            result = accyear * 12 + 2 + lunar_month
        elif ji_style == 2:  # �亥�
            diff_val = int(Date(f"{self.year:04d}/{self.month:02d}/{self.day:02d} {self.hour:02d}:00:00.00") - Date("1900/06/19 00:00:00.00"))
            config_num = 708011105 - {0: 0, 1: 186, 2: 10153917, 3: 0}.get(taiyi_acumyear, 0)
            result = config_num + diff_val if taiyi_acumyear != 3 else round((lunar_year - 423) * (235 / 19) * 29.5306 + lunar_day, 0)
        elif ji_style == 3:  # ���
            diff_val_two = int(Date(f"{self.year:04d}/{self.month:02d}/{self.day:02d} {self.hour:02d}:00:00.00") - Date("1900/12/21 00:00:00.00"))
            config_num = 708011105 - {0: 0, 1: 10153917, 2: 10153917, 3: 0}.get(taiyi_acumyear, 0)
            accday = config_num + diff_val_two
            result = ((accday - 1) * 12) + (self.hour + 1) // 2 + (1 if taiyi_acumyear != 1 else 13)
            if taiyi_acumyear == 3:
                tiangan = dict(zip([tuple(self.jiazi_list[i:i+6]) for i in range(0, 60, 6)], self.jiazi_list[0::6]))
                dgz = self._get_gangzhi()[2]
                getfut = dict(zip(self.jiazi_list[0::6], [1, 7, 13, 19, 25, 31, 37, 43, 49, 55])).get(config.multi_key_dict_get(tiangan, dgz))
                dgz_num = dict(zip(self.jiazi_list, range(1, 61))).get(dgz)
                zhi_num = dict(zip(self.di_zhi, range(1, 13))).get(self._get_gangzhi()[3][1])
                result = zhi_num if tiangan == dgz_num else ((dgz_num - getfut) * 12) + zhi_num
        elif ji_style == 4:  # ���
            diff_val_two = int(Date(f"{self.year:04d}/{self.month:02d}/{self.day:02d} {self.hour:02d}:{self.minute:02d}:00.00") - Date("1900/12/21 00:00:00.00"))
            config_num = 708011105 - {0: 0, 1: 10153917, 2: 10153917, 3: 0}.get(taiyi_acumyear, 0)
            accday = config_num + diff_val_two
            result = ((accday - 1) * 23) + (self.hour * 10500) + (self.minute + 1)
        else:
            result = None

        self.cache[cache_key] = result
        return result

    def lr(self):
        gz = jieqi.gangzhi(self.year, self.month, self.day, self.hour, self.minute)
        j_q = jieqi.jq(self.year, self.month, self.day, self.hour, self.minute)
        cm = dict(zip(range(1,13), config.cmonth )).get(config.lunar_date_d(self.year, self.month, self.day).get("��") )
        return kinliuren.Liuren(j_q, cm, gz[2], gz[3])

    def taiyi_life_accum(self):
        """憭芯��賣彍蝛齿𠯫��"""
        def calculate_value_for_year(year):
            initial_value = 126944450
            increment_per_60_years = 3145500
            cycles = (year - 1564) // 60
            value = initial_value + cycles * increment_per_60_years
            return value
        
        #憭芯�鈭粹��賣����撟湔彍
        def jiazi_accum(gz):
            return dict(zip(config.jiazi(), [i*3652425 for i in list(range(1,61))])).get(gz)
        
        def jq_accum(jq):
            return dict(zip(config.new_list(jieqi.jieqi_name, "�祈秐"), [3652425,152184.37,304368.75,456553.12,608727.50,760921.87,913106.25,1065290.62,1217475,1369659.37,1522843.75,1674028.12,1826212.50,1978396.87,2130581.25,2282765.62,2434950,2587134.37,2739318.75,2891503.12,3043687.50,3195871.87,3348056.25,3500240.62])).get(jq)

        y = calculate_value_for_year(self.year)
        gz = self._get_gangzhi()
        jie_qi = jieqi.jq(self.year, self.month, self.day, self.hour, self.minute)
        return (jiazi_accum(gz[0]) + y + jq_accum(jie_qi) + (jieqi.jq_count_days(self.year, self.month, self.day, self.hour, self.minute) * 10000)) // 10000

    def three_cai_num(self):
        """銝㗇���"""
        accum_num = self.taiyi_life_accum()
        sky = accum_num % 720
        earth = sky % 72
        ppl = earth % 72
        return sky, earth, ppl

    def yeargua(self, taiyi_acumyear):
        """�澆僑��"""
        num = self.accnum(0, taiyi_acumyear) % 64 or 64
        return config.gua.get(num)

    def daygua(self, taiyi_acumyear):
        """�潭𠯫��"""
        num = self.accnum(1, taiyi_acumyear) % 646464 % 20 or 64
        return config.gua.get(num)

    def hourgua(self, taiyi_acumyear):
        """�潭���"""
        num = self.accnum(3, taiyi_acumyear) % 64 or 64
        return config.gua.get(num)

    def kook(self, ji_style, taiyi_acumyear):
        """憭芯�撅���"""
        cache_key = f'kook_{ji_style}_{taiyi_acumyear}'
        if cache_key in self.cache:
            return self.cache[cache_key]

        alljq = jieqi_name
        j_q = jieqi.jq(self.year, self.month, self.day, self.hour, self.minute)
        dz = config.new_list(alljq, "�祈秐")[:12]
        hz = config.new_list(alljq, "憭讛秐")[:12]
        jqmap = {tuple(dz): "�祈秐", tuple(hz): "憭讛秐"}
        k = self.accnum(ji_style, taiyi_acumyear) % 72 or 72

        # �煾𨘥�文�嚗ōaiyi_acumyear=1嚗㗇�閮��撅��貊眏蝛齿���%60 瘙箏�嚗���� = (蝛齿�%60) - 30
        # �冽�颲啗歲頧㚁�瘥𤩺�颲� +1 撅���苊���撅��� = (蝛齿�%60) - 30嚗�%60=56��26撅���57��27撅���58��28撅�嚗�
        if ji_style == 3 and taiyi_acumyear == 1:
            k = self.accnum(3, 1) % 60 - 30
            if k < 0:
                k += 60
        three_year = {0: "��予", 1: "��𧑐", 2: "��犖"}.get({i: v for i, v in zip(range(1, 73), [0, 1, 2] * 24)}.get(k))
        dun = "�賡�" if ji_style in (0, 1, 5, 2) else {"憭讛秐": "�圈�", "�祈秐": "�賡�"}.get(config.multi_key_dict_get(jqmap, j_q))
        if ji_style == 4:
            gz = self._get_gangzhi()
            if config.multi_key_dict_get(jqmap, j_q) == "�祈秐":
                a = config.multi_key_dict_get(
                    {tuple("�喲��䔶漸摮𣂷�"): "�賡�", tuple("撖�晓颲啣歲��𧊋"): "�圈�"}
                    if gz[2][0] in "�脖��𠰴�憯�" else
                    {tuple("�喲��䔶漸摮𣂷�"): "�圈�", tuple("撖�晓颲啣歲��𧊋"): "�賡�"},
                    gz[3][1]
                )
            else:
                a = config.multi_key_dict_get(
                    {tuple("�喲��䔶漸摮𣂷�"): "�圈�", tuple("撖�晓颲啣歲��𧊋"): "�賡�"}
                    if gz[2][0] in "�脖��𠰴�憯�" else
                    {tuple("�喲��䔶漸摮𣂷�"): "�賡�", tuple("撖�晓颲啣歲��𧊋"): "�圈�"},
                    gz[3][1]
                )
            dun = a

        result = {"��": f"{dun}{an2cn(k)}撅�", "��": k, "撟�": three_year, "蝛�" + config.taiyi_name(ji_style)[0] + "��": self.accnum(ji_style, taiyi_acumyear)}
        self.cache[cache_key] = result
        return result

    def get_five_yuan_kook(self, ji_style, taiyi_acumyear):
        """憭芯�鈭𥪜����"""
        gz = self._get_gangzhi()
        kook = self.kook(ji_style, taiyi_acumyear)
        try:
            return kook.get("��")[:2] + (config.five_zi_yuan(kook.get("��"), gz[ji_style]) if ji_style != 4 else config.min_five_zi_yuan(kook.get("��"), gz[ji_style]))
        except ValueError:
            return ""

    def getepoch(self, ji_style, taiyi_acumyear):
        """瘙�云銋嗵�蝝�"""
        acc_num = self.accnum(ji_style, taiyi_acumyear)
        if ji_style in (0, 1, 2):
            find_ji_num = 1 if acc_num % 360 == 1 else int((acc_num % 360) // 60 + 1)
            find_ji_num2 = int(acc_num % 360 % 72 % 24 / 3) or 1
            if find_ji_num2 > 6:
                find_ji_num2 -= 6
            if find_ji_num > 6:
                find_ji_num -= 6
            return {"��": dict(zip(range(1, 7), config.cnum[:6])).get(find_ji_num2), "蝝�": dict(zip(range(1, 7), config.cnum[:6])).get(find_ji_num)}
        return f"蝚洌config.multi_key_dict_get(config.epochdict, self._get_gangzhi()[2 if ji_style == 3 else 3])}蝝�"

    def getyuan(self, ji_style, taiyi_acumyear):
        """瘙�云銋嗵���"""
        acc_num = self.accnum(ji_style, taiyi_acumyear)
        find_ji_num = 1 if round(acc_num % 360) == 1 else int(round((acc_num % 360) / 72, 0))
        return dict(zip(range(1, 6), self.jiazi_list[0::12])).get(find_ji_num or 1)

    def jiyuan(self, ji_style, taiyi_acumyear):
        """憭芯�蝝���"""
        gang_zhi = self._get_gangzhi()
        if ji_style in (3, 4):
            return f"{self.getepoch(ji_style, taiyi_acumyear)}{config.multi_key_dict_get(config.jiyuan_dict, gang_zhi[3 if ji_style == 4 or taiyi_acumyear == 1 else 2])}��"
        return f"蝚洌self.getepoch(ji_style, taiyi_acumyear).get('蝝�')}蝝�蝚洌self.getepoch(ji_style, taiyi_acumyear).get('��')}{self.getyuan(ji_style, taiyi_acumyear)}��"

    def ty(self, ji_style, taiyi_acumyear):
        """瘙�云銋蹱���"""
        # �煾𨘥�文�嚗ōaiyi_acumyear=1嚗㗇�閮��憭芯��賢悅�寧鍂�斤��𠰴云銋䠷��∪�蝬瓐�卝�䔶����蝘颯�齿綫瘜�
        # �屸蒾��𦶢韏瑚�摰殷����摰殷�銝齿虜銝凋�嚗偦苊��𦶢韏瑚�摰殷�����怠悅嚗䔶����蝘鳴�銝齿虜銝凋�����
        if ji_style == 3 and taiyi_acumyear == 1:
            sj = jieqi.taiyi_shichen_gong(self.year, self.month, self.day, self.hour)
            if sj:
                return sj['gong']
        arrangement = np.repeat(np.arange(10), 3)
        arrangement_r = list(reversed(arrangement))
        yy_dict = {
            "��": dict(zip(range(1, 73), list(itertools.chain.from_iterable([list(arrangement)[3:15] + list(arrangement)[18:]] * 3)))),
            "��": dict(zip(range(1, 73), (arrangement_r[:12] + arrangement_r[15:-3]) * 3))
        }
        kook = self.kook(ji_style, taiyi_acumyear)
        return yy_dict[kook.get("��")[0]].get(kook.get("��"))

    def ty_gong(self, ji_style, taiyi_acumyear):
        """憭芯��賢悅嚗�悅�㵪�"""
        # ���蝡臭��湛��� ty() 瘣𥟇㮾�貉�摰桀�嚗屸��⊥�閮��䔶����蝘颯�齿�摰桀��峕郊頝唾�
        return config.num2gong(self.ty(ji_style, taiyi_acumyear))

    def twenty_eightstar(self, ji_style, taiyi_acumyear):
        """鈭���怠挪"""
        s_f = self.sf_num(ji_style, taiyi_acumyear)
        sf = self.sf(ji_style, taiyi_acumyear)
        su_r = list(reversed(config.su))
        sixteen = config.sixteen
        num = su_r.index(s_f) - sixteen.index(sf) + sixteen.index("撌�") + {
            "��": -2, "��": -3, "鈭�": -5, "撌�": 1, "撖�": 4, "��": 3, "摮�": 6, "��": -1, "��": -2, "��": -4, "��": 4, "撌�": 1, "銝�": 5, "��": 0, "銋�": -5
        }.get(sf, 2)
        num = (num - 28) if num > 28 else (num + 28) if num < 0 else 28 if num == 0 else num
        return config.new_list(su_r, dict(zip(range(1, 29), su_r)).get(num))

    def sf(self, ji_style, taiyi_acumyear):
        """憪𧢲��賢悅"""
        return dict(zip(range(1, 73), config.sf_list)).get(self.kook(ji_style, taiyi_acumyear).get("��"))

    def sf_num(self, ji_style, taiyi_acumyear):
        """憪𧢲���"""
        sf = self.sf(ji_style, taiyi_acumyear)
        sf_z = dict(zip(config.gong, range(1, 17))).get(sf)
        sf_su = config.su_gong.get(sf)
        yc_num = dict(zip(config.su, range(1, 29))).get(self.year_chin())
        total = yc_num + sf_z
        return dict(zip(range(1, 29), config.new_list(config.su, sf_su))).get(total if total <= 28 else total - 28)

    def se(self, ji_style, taiyi_acumyear):
        """摰𡁶𤌍"""
        wc, hg, ts = self.skyeyes(ji_style, taiyi_acumyear), self.hegod(ji_style), self.taishui(ji_style)
        start = config.new_list(config.gong1, hg)
        return config.new_list(config.gong1, wc)[len(start[:start.index(ts) + 1]) - 1]

    def home_cal(self, ji_style, taiyi_acumyear):
        """銝餌�"""
        l_num= [8,8,3,3,4,4,9,9,2,2,7,7,6,6,1,1]
        wancheong = self.skyeyes(ji_style, taiyi_acumyear)
        wc_num= dict(zip(config.new_list(config.sixteen, "鈭�"), l_num)).get(wancheong)
        taiyi = self.ty(ji_style, taiyi_acumyear)
        wc_jc = list(map(lambda x: x == wancheong, config.jc)).count(True)
        ty_jc = list(map(lambda x: x == taiyi, config.tyjc)).count(True)
        wc_jc1  = list(map(lambda x: x == wancheong, config.jc1)).count(True)
        wc_order = config.new_list(config.num, wc_num)
        if wc_jc == 1 and ty_jc != 1 and wc_jc1 !=1 :
            return sum(wc_order[: wc_order.index(taiyi)]) +1
        if wc_jc !=1 and ty_jc != 1 and wc_jc1 ==1:
            return sum(wc_order[: wc_order.index(taiyi)])
        if wc_jc != 1 and ty_jc ==1 and wc_jc1 !=1:
            return sum(wc_order[: wc_order.index(taiyi)])
        if wc_jc ==1 and ty_jc ==1 and wc_jc1 !=1 and wc_jc == ty_jc and wc_jc1 == wc_jc:
            return sum(wc_order[wc_order.index(taiyi):])+1
        if wc_jc ==1 and ty_jc ==1 and wc_jc1 !=1 and wc_jc == ty_jc and wc_jc1 != wc_jc:
            return sum(wc_order[:wc_order.index(taiyi)])+1
        if wc_jc ==1 and ty_jc ==1 and wc_jc1 !=1 and wc_jc != ty_jc:
            return sum(wc_order[wc_order.index(ty_jc):])+1
        if wc_jc !=1 and ty_jc ==1 and wc_jc1 ==1 and taiyi != wc_order[wc_jc] and wc_jc1 != wc_jc:
            return sum(wc_order[: wc_order.index(taiyi)])
        if wc_jc !=1 and ty_jc ==1 and wc_jc1 ==1 and taiyi == wc_order[wc_jc] and wc_jc1 == wc_jc:
            return taiyi
        if wc_jc !=1 and ty_jc !=1 and wc_jc1 !=1 and taiyi != wc_num:
            return sum(wc_order[: wc_order.index(taiyi)])
        if wc_jc !=1 and ty_jc !=1 and wc_jc1 !=1 and taiyi == wc_num:
            return taiyi
        else:
            return taiyi

    def home_general(self, ji_style, taiyi_acumyear):
        """銝餃之撠�"""
        kook = self.kook(ji_style, taiyi_acumyear)
        home_cal = config.find_cal(kook.get("��")[0], kook.get("��"))[0]
        return {
            True: self.home_cal(ji_style, taiyi_acumyear),
            home_cal < 10: home_cal,
            home_cal % 10 == 0: 1,
            10 < home_cal < 20: home_cal - 10,
            20 < home_cal < 30: home_cal - 20,
            30 < home_cal < 40: home_cal - 30
        }.get(True, 1)

    def home_vgen(self, ji_style, taiyi_acumyear):
        """銝餃�撠�"""
        home_vg = self.home_general(ji_style, taiyi_acumyear) * 3 % 10
        return 5 if home_vg == 0 else home_vg

    def away_cal(self, ji_style, taiyi_acumyear):
        """摰Ｙ�"""
        shiji = self.sf(ji_style, taiyi_acumyear)
        sf_num = dict(zip(config.new_list(config.sixteen, "鈭�"), self.l_num)).get(shiji)
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
        """摰Ｗ之撠�"""
        kook = self.kook(ji_style, taiyi_acumyear)
        away_cal = config.find_cal(kook.get("��")[0], kook.get("��"))[1]
        return {
            away_cal == 1: 1,
            away_cal < 10: away_cal,
            away_cal % 10 == 0: 5,
            10 < away_cal < 20: away_cal - 10,
            20 < away_cal < 30: away_cal - 20,
            30 < away_cal < 40: away_cal - 30
        }.get(True, 5)

    def away_vgen(self, ji_style, taiyi_acumyear):
        """摰Ｗ�撠�"""
        away_vg = self.away_general(ji_style, taiyi_acumyear) * 3 % 10
        return 5 if away_vg == 0 else away_vg

    def shensha(self, ji_style, taiyi_acumyear):
        """�典云銋嗵訜���"""
        if ji_style not in (3, 4):
            return "憭芯�����漤＊蝷�"
        general = "鞎港犖,���,�梢�,�剖�,�暸䒰,�㘾�,憭拍征,�質�,憭芸虜,��郎,憭芷苊,憭拙�".split(",")
        tiany = self.ty_gong(ji_style, taiyi_acumyear).replace("撌�", "颲�").replace("��", "��").replace("��", "銝�").replace("銋�", "鈭�")
        return dict(zip(config.new_list(self.di_zhi if self.kook(ji_style, taiyi_acumyear).get("��")[0] == "��" else self.di_zhi_reversed, tiany), general))

    def set_cal(self, ji_style, taiyi_acumyear):
        """摰𡁶�"""
        setcal = self.se(ji_style, taiyi_acumyear)
        se_num = dict(zip(config.new_list(config.sixteen, "鈭�"), self.l_num)).get(setcal)
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
        """摰𡁜之撠�"""
        set_g = self.set_cal(ji_style, taiyi_acumyear) % 10
        return 5 if set_g == 0 else set_g

    def set_vgen(self, ji_style, taiyi_acumyear):
        """摰𡁜�撠�"""
        set_vg = self.set_general(ji_style, taiyi_acumyear) * 3 % 10
        return 5 if set_vg == 0 else set_vg
    def sixteen_gong(self, ji_style, taiyi_acumyear):
        """���摰桀��笔����蝎曉�雿�"""
        if ji_style != 4:
            dict1 = [{self.skyeyes(ji_style, taiyi_acumyear):"���"},
                     {self.taishui(ji_style):"憭芣革"},
                     {self.hegod(ji_style):"���"},
                     {self.jigod(ji_style):"閮��"},
                     {self.sf(ji_style, taiyi_acumyear):"憪𧢲�"},
                     {self.se(ji_style, taiyi_acumyear):"摰朞�"}, 
                     {self.kingbase(ji_style, taiyi_acumyear):"�𥕦抅"}, 
                     {self.officerbase(ji_style, taiyi_acumyear):"��抅"}, 
                     {self.pplbase(ji_style, taiyi_acumyear):"瘞穃抅"},
                     {self.fgd(ji_style, taiyi_acumyear):"�𤤿�"},
                     {self.skyyi(ji_style, taiyi_acumyear):"憭拐�"},
                     {self.earthyi(ji_style, taiyi_acumyear):"�唬�"},
                     {self.zhifu(ji_style, taiyi_acumyear):"�渡泵"},
                     {self.flyfu(ji_style, taiyi_acumyear):"憌𤤿泵"},
                     {config.tian_wang(self.accnum(ji_style,taiyi_acumyear)):"憭拍�"},
                     {config.tian_shi(self.accnum(ji_style,taiyi_acumyear)):"憭拇�"},
                     {config.wuxing(self.accnum(ji_style,taiyi_acumyear)):"鈭磰�"},
                     {config.kingfu(self.accnum(ji_style,taiyi_acumyear)):"撣萘泵"},
                     {config.taijun(self.accnum(ji_style,taiyi_acumyear)):"憭芸�"},
                     {config.num2gong(config.wufu(self.accnum(ji_style,taiyi_acumyear))):"鈭𠉛�"},
                     #{self.ty_gong(ji_style, taiyi_acumyear):"憭芯�"},
                     {config.num2gong(self.home_general(ji_style, taiyi_acumyear)):"銝餃之"},  
                     {config.num2gong(self.home_vgen(ji_style, taiyi_acumyear)):"銝餃�"},
                     {config.num2gong(self.away_general(ji_style, taiyi_acumyear)):"摰Ｗ之"},  
                     {config.num2gong(self.away_vgen(ji_style, taiyi_acumyear)):"摰Ｗ�"},
                     {config.num2gong(config.threewind(self.accnum(ji_style,taiyi_acumyear))):"銝厰◢"},  
                     {config.num2gong(config.fivewind(self.accnum(ji_style,taiyi_acumyear))):"鈭娪◢"},
                     {config.num2gong(config.eightwind(self.accnum(ji_style,taiyi_acumyear))):"�恍◢"},  
                     {config.num2gong(config.flybird(self.accnum(ji_style,taiyi_acumyear))):"憌偦野"},
                     {config.num2gong(config.bigyo(self.accnum(ji_style,taiyi_acumyear))):"憭扳虜"},
                     {config.num2gong(config.smyo(self.accnum(ji_style,taiyi_acumyear))):"撠𤩺虜"},  
                     #{config.leigong(self.ty(ji_style, taiyi_acumyear)):"�瑕�"},  
                     {config.yangjiu(self.year, self.month, self.day):"�賭�"}, 
                     {config.baliu(self.year, self.month, self.day):"�曉�"},
                     #{config.lijin(self.year, self.month, self.day, self.hour, self.minute):"�冽揖"}, 
                     #{config.lion(self.year, self.month, self.day, self.hour, self.minute):"���"}, 
                     #{config.cloud(self.home_general(ji_style, taiyi_acumyear)):"�賡𤩅"},
                     #{config.tiger(self.ty(ji_style, taiyi_acumyear)):"�𥡝�"}, 
                     #{config.returnarmy(self.away_general(ji_style, taiyi_acumyear)):"�噼�"}, 
                     {config.num2gong(self.ty(ji_style, taiyi_acumyear)):"憭芯�"}, 
                     ]
        if ji_style == 4:
            dict1 = [{self.skyeyes(ji_style, taiyi_acumyear):"���"},
                     {self.hegod(ji_style):"���"},
                     {self.jigod(ji_style):"閮��"},
                     {self.sf(ji_style, taiyi_acumyear):"憪𧢲�"},
                     {self.kingbase(ji_style, taiyi_acumyear):"�𥕦抅"}, 
                     {self.officerbase(ji_style, taiyi_acumyear):"��抅"}, 
                     {self.pplbase(ji_style, taiyi_acumyear):"瘞穃抅"},
                     {self.fgd(ji_style, taiyi_acumyear):"�𤤿�"},
                     {self.skyyi(ji_style, taiyi_acumyear):"憭拐�"},
                     {self.earthyi(ji_style, taiyi_acumyear):"�唬�"},
                     {self.zhifu(ji_style, taiyi_acumyear):"�渡泵"},
                     {self.flyfu(ji_style, taiyi_acumyear):"憌𤤿泵"},
                     {config.tian_wang(self.accnum(ji_style,taiyi_acumyear)):"憭拍�"},
                     {config.wuxing(self.accnum(ji_style,taiyi_acumyear)):"鈭磰�"},
                     {config.kingfu(self.accnum(ji_style,taiyi_acumyear)):"撣萘泵"},
                     {config.taijun(self.accnum(ji_style,taiyi_acumyear)):"憭芸�"},
                     {config.num2gong(config.wufu(self.accnum(ji_style,taiyi_acumyear))):"鈭𠉛�"},
                     {config.num2gong(self.home_general(ji_style, taiyi_acumyear)):"銝餃之"},  
                     {config.num2gong(self.home_vgen(ji_style, taiyi_acumyear)):"銝餃�"},
                     {config.num2gong(self.away_general(ji_style, taiyi_acumyear)):"摰Ｗ之"},  
                     {config.num2gong(self.away_vgen(ji_style, taiyi_acumyear)):"摰Ｗ�"},
                     {config.num2gong(config.threewind(self.accnum(ji_style,taiyi_acumyear))):"銝厰◢"},  
                     {config.num2gong(config.fivewind(self.accnum(ji_style,taiyi_acumyear))):"鈭娪◢"},
                     {config.num2gong(config.eightwind(self.accnum(ji_style,taiyi_acumyear))):"�恍◢"},  
                     {config.num2gong(config.flybird(self.accnum(ji_style,taiyi_acumyear))):"憌偦野"},
                     {config.num2gong(self.ty(ji_style, taiyi_acumyear)):"憭芯�"}, 
                     ]
        res = {"撌�":"", "��":"", "��":"", "��":"", "��":"", "��":"", "��":"", "銋�":"", "鈭�":"", "摮�":"", "銝�":"", "��":"","撖�":"", "��":"", "颲�":"", "撌�":"","銝�":""}
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
        """����笔�雿�"""
        dict1 = [{self.skyeyes(ji_style, taiyi_acumyear).replace("撌�","颲�").replace("��","��").replace("��","銝�").replace("銋�","鈭�").replace("銝�", "颲�"):"���"},
                 {self.jigod(ji_style).replace("撌�","颲�").replace("��","��").replace("��","銝�").replace("銋�","鈭�").replace("銝�", "颲�"):"閮��"},
                 {self.sf(ji_style, taiyi_acumyear).replace("撌�","颲�").replace("��","��").replace("��","銝�").replace("銋�","鈭�").replace("銝�", "颲�"):"憪𧢲�"},
                 {self.kingbase(ji_style, taiyi_acumyear).replace("撌�","颲�").replace("��","��").replace("��","銝�").replace("銋�","鈭�"):"�𥕦抅"}, 
                 {self.officerbase(ji_style, taiyi_acumyear).replace("撌�","颲�").replace("��","��").replace("��","銝�").replace("銋�","鈭�").replace("銝�", "颲�"):"��抅"}, 
                 {self.pplbase(ji_style, taiyi_acumyear).replace("撌�","颲�").replace("��","��").replace("��","銝�").replace("銋�","鈭�").replace("銝�", "颲�"):"瘞穃抅"},
                 {self.fgd(ji_style, taiyi_acumyear).replace("撌�","颲�").replace("��","��").replace("��","銝�").replace("銋�","鈭�").replace("銝�", "颲�"):"�𤤿�"},
                 {self.skyyi(ji_style, taiyi_acumyear).replace("撌�","颲�").replace("��","��").replace("��","銝�").replace("銋�","鈭�").replace("銝�", "颲�"):"憭拐�"},
                 {self.earthyi(ji_style, taiyi_acumyear).replace("撌�","颲�").replace("��","��").replace("��","銝�").replace("銋�","鈭�").replace("銝�", "颲�"):"�唬�"},
                 {self.flyfu1(ji_style, taiyi_acumyear).replace("撌�","颲�").replace("��","��").replace("��","銝�").replace("銋�","鈭�").replace("銝�", "颲�"):"憌𤤿泵"},
                 {self.zhifu(ji_style, taiyi_acumyear).replace("撌�","颲�").replace("��","��").replace("��","銝�").replace("銋�","鈭�").replace("銝�", "颲�"):"�渡泵"},
                 {config.num2gong_life(config.wufu(self.accnum(ji_style,taiyi_acumyear))).replace("撌�","颲�").replace("��","��").replace("��","銝�").replace("銋�","鈭�"):"鈭𠉛�"},
                 {config.num2gong_life(self.home_general(ji_style, taiyi_acumyear)).replace("撌�","颲�").replace("��","��").replace("��","銝�").replace("銋�","鈭�"):"銝餃之"},  
                 {config.num2gong_life(self.home_vgen(ji_style, taiyi_acumyear)).replace("撌�","颲�").replace("��","��").replace("��","銝�").replace("銋�","鈭�"):"銝餃�"},
                 {config.num2gong_life(self.away_general(ji_style, taiyi_acumyear)).replace("撌�","颲�").replace("��","��").replace("��","銝�").replace("銋�","鈭�"):"摰Ｗ之"},  
                 {config.num2gong_life(self.away_vgen(ji_style, taiyi_acumyear)).replace("撌�","颲�").replace("��","��").replace("��","銝�").replace("銋�","鈭�"):"摰Ｗ�"},
                 {config.num2gong_life(config.smyo(self.accnum(ji_style,taiyi_acumyear))).replace("撌�","颲�").replace("��","��").replace("��","銝�").replace("銋�","鈭�"):"撠𤩺虜"},  
                 ]
        res = {"撌�":"", "��":"", "��":"", "��":"", "��":"", "��":"", "鈭�":"", "摮�":"", "銝�":"", "撖�":"", "��":"", "颲�":"","銝�":""}
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
        """����笔�雿�"""
        dict1 = [{self.skyeyes(ji_style, taiyi_acumyear).replace("撌�","颲�").replace("��","��").replace("��","銝�").replace("銋�","鈭�").replace("銝�", "颲�"):"���"},
                 {self.jigod(ji_style).replace("撌�","颲�").replace("��","��").replace("��","銝�").replace("銋�","鈭�").replace("銝�", "颲�"):"閮��"},
                 {self.sf(ji_style, taiyi_acumyear).replace("撌�","颲�").replace("��","��").replace("��","銝�").replace("銋�","鈭�").replace("銝�", "颲�"):"憪𧢲�"},
                 {self.kingbase(ji_style, taiyi_acumyear).replace("撌�","颲�").replace("��","��").replace("��","銝�").replace("銋�","鈭�"):"�𥕦抅"}, 
                 {self.officerbase(ji_style, taiyi_acumyear).replace("撌�","颲�").replace("��","��").replace("��","銝�").replace("銋�","鈭�").replace("銝�", "颲�"):"��抅"}, 
                 {self.pplbase(ji_style, taiyi_acumyear).replace("撌�","颲�").replace("��","��").replace("��","銝�").replace("銋�","鈭�").replace("銝�", "颲�"):"瘞穃抅"},
                 {self.fgd(ji_style, taiyi_acumyear).replace("撌�","颲�").replace("��","��").replace("��","銝�").replace("銋�","鈭�").replace("銝�", "颲�"):"�𤤿�"},
                 {self.skyyi(ji_style, taiyi_acumyear).replace("撌�","颲�").replace("��","��").replace("��","銝�").replace("銋�","鈭�").replace("銝�", "颲�"):"憭拐�"},
                 {self.earthyi(ji_style, taiyi_acumyear).replace("撌�","颲�").replace("��","��").replace("��","銝�").replace("銋�","鈭�").replace("銝�", "颲�"):"�唬�"},
                 {self.flyfu1(ji_style, taiyi_acumyear).replace("撌�","颲�").replace("��","��").replace("��","銝�").replace("銋�","鈭�").replace("銝�", "颲�"):"憌𤤿泵"},
                 {config.num2gong_life(config.wufu(self.accnum(ji_style,taiyi_acumyear))).replace("撌�","颲�").replace("��","��").replace("��","銝�").replace("銋�","鈭�"):"鈭𠉛�"},
                 {config.num2gong_life(self.home_general(ji_style, taiyi_acumyear)).replace("撌�","颲�").replace("��","��").replace("��","銝�").replace("銋�","鈭�"):"銝餃之"},  
                 {config.num2gong_life(self.home_vgen(ji_style, taiyi_acumyear)).replace("撌�","颲�").replace("��","��").replace("��","銝�").replace("銋�","鈭�"):"銝餃�"},
                 {config.num2gong_life(self.away_general(ji_style, taiyi_acumyear)).replace("撌�","颲�").replace("��","��").replace("��","銝�").replace("銋�","鈭�"):"摰Ｗ之"},  
                 {config.num2gong_life(self.away_vgen(ji_style, taiyi_acumyear)).replace("撌�","颲�").replace("��","��").replace("��","銝�").replace("銋�","鈭�"):"摰Ｗ�"},
                 {config.num2gong_life(config.smyo(self.accnum(ji_style,taiyi_acumyear))).replace("撌�","颲�").replace("��","��").replace("��","銝�").replace("銋�","鈭�"):"撠𤩺虜"},  
                 ]
        res = {"撌�":"", "��":"", "��":"", "��":"", "��":"", "��":"", "鈭�":"", "摮�":"", "銝�":"", "撖�":"", "��":"", "颲�":"","銝�":""}
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
        """���摰桀��笔�嚗𣬚���移"""
        if ji_style != 4:
            dict1 = [{self.skyeyes(ji_style, taiyi_acumyear):"���"},
                     {self.taishui(ji_style):"憭芣革"},
                     {self.hegod(ji_style):"���"},
                     {self.jigod(ji_style):"閮��"},
                     {self.sf(ji_style, taiyi_acumyear):"憪𧢲�"},
                     {self.se(ji_style, taiyi_acumyear):"摰朞�"}, 
                     {self.kingbase(ji_style, taiyi_acumyear):"�𥕦抅"}, 
                     {self.officerbase(ji_style, taiyi_acumyear):"��抅"}, 
                     {self.pplbase(ji_style, taiyi_acumyear):"瘞穃抅"},
                     {self.fgd(ji_style, taiyi_acumyear):"�𤤿�"},
                     {self.skyyi(ji_style, taiyi_acumyear):"憭拐�"},
                     {self.earthyi(ji_style, taiyi_acumyear):"�唬�"},
                     {self.zhifu(ji_style, taiyi_acumyear):"�渡泵"},
                     {self.flyfu(ji_style, taiyi_acumyear):"憌𤤿泵"},
                     {config.num2gong(config.wufu(self.accnum(ji_style,taiyi_acumyear))):"鈭𠉛�"},
                     #{self.ty_gong(ji_style, taiyi_acumyear):"憭芯�"},
                     {config.num2gong(self.home_general(ji_style, taiyi_acumyear)):"銝餃之"},  
                     {config.num2gong(self.home_vgen(ji_style, taiyi_acumyear)):"銝餃�"},
                     {config.num2gong(self.away_general(ji_style, taiyi_acumyear)):"摰Ｗ之"},  
                     {config.num2gong(self.away_vgen(ji_style, taiyi_acumyear)):"摰Ｗ�"},
                     {config.num2gong(config.bigyo(self.accnum(ji_style,taiyi_acumyear))):"憭扳虜"},
                     {config.num2gong(config.smyo(self.accnum(ji_style,taiyi_acumyear))):"撠𤩺虜"},  
                     #{config.leigong(self.ty(ji_style, taiyi_acumyear)):"�瑕�"},  
                     {config.yangjiu(self.year, self.month, self.day):"�賭�"}, 
                     {config.baliu(self.year, self.month, self.day):"�曉�"},
                     {config.num2gong(self.ty(ji_style, taiyi_acumyear)):"憭芯�"}, 
                     ]
        if ji_style == 4:
            dict1 = [{self.skyeyes(ji_style, taiyi_acumyear):"���"},
                     {self.hegod(ji_style):"���"},
                     {self.jigod(ji_style):"閮��"},
                     {self.sf(ji_style, taiyi_acumyear):"憪𧢲�"},
                     {self.kingbase(ji_style, taiyi_acumyear):"�𥕦抅"}, 
                     {self.officerbase(ji_style, taiyi_acumyear):"��抅"}, 
                     {self.pplbase(ji_style, taiyi_acumyear):"瘞穃抅"},
                     {self.fgd(ji_style, taiyi_acumyear):"�𤤿�"},
                     {self.skyyi(ji_style, taiyi_acumyear):"憭拐�"},
                     {self.earthyi(ji_style, taiyi_acumyear):"�唬�"},
                     {self.zhifu(ji_style, taiyi_acumyear):"�渡泵"},
                     {self.flyfu(ji_style, taiyi_acumyear):"憌𤤿泵"},
                     {config.num2gong(config.wufu(self.accnum(ji_style,taiyi_acumyear))):"鈭𠉛�"},
                     {config.num2gong(self.home_general(ji_style, taiyi_acumyear)):"銝餃之"},  
                     {config.num2gong(self.home_vgen(ji_style, taiyi_acumyear)):"銝餃�"},
                     {config.num2gong(self.away_general(ji_style, taiyi_acumyear)):"摰Ｗ之"},  
                     {config.num2gong(self.away_vgen(ji_style, taiyi_acumyear)):"摰Ｗ�"},
                     {config.num2gong(self.ty(ji_style, taiyi_acumyear)):"憭芯�"}, 
                     ]
        res = {"撌�":"", "��":"", "��":"", "��":"", "��":"", "��":"", "��":"", "銋�":"", "鈭�":"", "摮�":"", "銝�":"", "��":"","撖�":"", "��":"", "颲�":"", "撌�":"","銝�":""}
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
        """�笔��讛膩"""
        alld = self.sixteen_gong(ji_style, taiyi_acumyear)
        return "\n\n".join(f"�𨫆key}�髢n{', '.join(value) if value else '��'}" for key, value in alld.items())

    def year_chin(self):
        """憭芣革蝳賣�"""
        chin_28_stars_code = dict(zip(range(1, 29), config.su))
        lunar = self._get_lunar_date()
        year = lunar.get("撟�")
        month = lunar.get("��")
        if month in ("�����", "�����") and jieqi.jq(self.year, self.month, self.day, self.hour, self.minute) != "蝡𧢲坾":
            get_year_chin_number = (year - 1 + 15) % 28 or 28
        else:
            get_year_chin_number = (year + 15) % 28 or 28
        return chin_28_stars_code.get(get_year_chin_number)

    def kingbase(self, ji_style, taiyi_acumyear):
        """�𥕦抅"""
        king_base = (self.accnum(ji_style, taiyi_acumyear) + 250) % 360 // 30 or 1
        return dict(zip(range(1, 13), config.new_list(self.di_zhi, "��"))).get(int(king_base))

    def officerbase(self, ji_style, taiyi_acumyear):
        """��抅"""
        return dict(zip(range(1, 73), itertools.cycle(config.officer_base))).get(self.kook(ji_style, taiyi_acumyear).get("��"))

    def pplbase(self, ji_style, taiyi_acumyear):
        """瘞穃抅"""
        return dict(zip(range(1, 73), itertools.cycle(config.new_list(self.di_zhi, "��")))).get(self.kook(ji_style, taiyi_acumyear).get("��"))

    def fgd(self, ji_style, taiyi_acumyear):
        """�𤤿�"""
        return dict(zip(range(1, 73), itertools.cycle(config.four_god))).get(self.kook(ji_style, taiyi_acumyear).get("��"))

    def skyyi(self, ji_style, taiyi_acumyear):
        """憭拐�"""
        return dict(zip(range(1, 73), itertools.cycle(config.sky_yi))).get(self.kook(ji_style, taiyi_acumyear).get("��"))

    def earthyi(self, ji_style, taiyi_acumyear):
        """�唬�"""
        return dict(zip(range(1, 73), itertools.cycle(config.earth_yi))).get(self.kook(ji_style, taiyi_acumyear).get("��"))

    def zhifu(self, ji_style, taiyi_acumyear):
        """�渡泵"""
        return dict(zip(range(1, 73), itertools.cycle(config.zhi_fu))).get(self.kook(ji_style, taiyi_acumyear).get("��"))

    def flyfu(self, ji_style, taiyi_acumyear):
        """憌𤤿泵"""
        fly = self.accnum(ji_style, taiyi_acumyear) % 360 % 36 / 3
        fly_fu = dict(zip(range(1, 13), config.new_list(self.di_zhi, "颲�"))).get(int(fly)) or "銝�"
        return fly_fu

    def flyfu1(self, ji_style, taiyi_acumyear):
        """憌𤤿泵 (for sixteen_gong1)"""
        fly = self.accnum(ji_style, taiyi_acumyear) % 360 % 36 / 3
        fly_fu = dict(zip(range(1, 13), config.new_list(self.di_zhi, "颲�"))).get(int(fly)) or "颲�"
        return fly_fu

    def tianzi_go(self, ji_style, taiyi_acumyear):
        """�𤾸予摮𣂼楚�拐��蠘�"""
        wan_c = self.skyeyes(ji_style, taiyi_acumyear)
        return {
            "��": "憭拍𤌍�典之甇血𤪓嚗�枂�埈䲮��",
            "銋�": "憭拍𤌍�券苊敺瑚嗾嚗�枂�望䲮��",
            "��": "憭拍𤌍�典�敺瑁肼嚗�枂�埈䲮��",
            "撌�": "憭拍𤌍�典之��源嚗�枂镼踵䲮��"
        }.get(wan_c, "")

    def gudan(self, ji_style, taiyi_acumyear):
        """�典迨�桐誑�䭾���"""
        ying_yang = {tuple([1, 3, 7, 9]): "�桅蒾", tuple([2, 4, 6, 8]): "�桅苊"}
        homecal = str(self.home_cal(ji_style, taiyi_acumyear))
        awaycal = str(self.away_cal(ji_style, taiyi_acumyear))
        if len(homecal) == 1:
            one_digit = config.multi_key_dict_get(ying_yang, int(homecal))
            return f"銝餌限敺𥗕one_digit}嚗庙'銝滚⏚銝𠺪�銝滚⏚銝颱犖銋麄��' if one_digit == '�桅蒾' else '瘝雴��拐���'}"
        if len(awaycal) == 1:
            one_digit = config.multi_key_dict_get(ying_yang, int(awaycal))
            return f"摰Ｙ限敺𥗕one_digit}嚗庙'瘝雴��拐���' if one_digit == '�桅蒾' else '銝滚⏚銝𠺪�銝滚⏚摰Ｖ犖銋麄��'}"
        for calc, prefix in [(homecal, "銝餌�"), (awaycal, "摰Ｙ�")]:
            if len(calc) == 2:
                two_digit = "摮日蒾" if int(calc[1]) in (1, 3) else "摮日苊"
                first_digit = config.multi_key_dict_get(ying_yang, int(calc[0]))
                if two_digit == "摮日苊" and first_digit == "�桅苊":
                    return f"{prefix}�箏鱓�唬蒂摮日苊嚗𣬚��漤苊��"
                if two_digit == "摮日蒾" and first_digit == "�桅苊":
                    return f"{prefix}�箏鱓�唬蒂摮日蒾嚗峕�銝滚⏚��"
                if two_digit == "摮日苊" and first_digit == "�桅蒾":
                    return f"{prefix}�箏鱓�賭蒂摮日苊嚗峕�銝滚⏚��"
                if two_digit == "摮日蒾" and first_digit == "�桅蒾":
                    return f"{prefix}�箏鱓�賭蒂摮日蒾嚗𣬚��漤蒾��"
        return ""


    def ming_kingbase(self, ji_style, taiyi_acumyear):
        """�𤾸��箏云銋蹱�銝餉�"""
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
            result.append("�𥕦抅���蝳誩�摰殷�����誩𤐄嚗���扳�撖改�摰嗆�蟡亦�嚗𣬚�蟡蹂蒂�嗚��")
        if kingb == officerb:
            result.append("�𥕦抅��竼�箏�摰殷��𥡝竼�𥟇�嚗��撖峕�畾瑯��")
        if kingb == pplb:
            result.append("�𥕦抅����箏�摰殷��躰噙獢穃�嚗𣬚蓡憪㮖�蝛�鞊僐���撌∠𥋘嚗䔶�憭勗�嚗諹�瘞睲�鞊～��")          
        if kingb == ty:
            result.append("�𥕦抅��云銋坔�摰殷��瑕噸摰�𦶢蝺游�嚗峕訽�曆誑敺��蝢抬��方��予摮𣂷��痹�隞亙�銝漤�嚗峕�隞交迫�氬���暺瑟郎憟賣�����堆��𣬚��賢藁�諹�銋麄��")
        if kingb == earthy:
            result.append("�𥕦抅��𧑐銋坔�摰殷�鈭箸�摰𨀣��𨥈��貊屆蝔潘���噸瘞豢�嚗諹��予銝钅◢��𦶢蝬剜鰵���憒�𥅾瘛急�嚗���啁�憒𤥁�嚗𣬚㺭�拍��怠�瘞𤏸��𢞁鈭∩���")
        if kingb == zhifu:
            result.append("�𥕦抅���潛泵��悅嚗䔶犖�𥕦��貊�嚗�³�敹牐�嚗峕�憳∪熄嚗屸��笔�嚗��憸典��躰���蟡亥秐����亙秘憟訾�嚗屸��笔遣嚗���瑟��������押����坿�䔶��拇䲰�䜘��")
        if kingb == fgod:
            result.append("�𥕦抅���蟡𧼮�摰殷�鈭箏�摰𨀣𠽌���隞亙�摰堒�蟡剔����嚗峕�隞仿��圈蒾���蟡硺犖銋麄����亙誥蟡�憭望�嚗諹���蝛∠釆嚗��瞏澆�皞箏��芸�銋麄��")
        if kingb == big:
            result.append("�𥕦抅��之皜詨�摰殷��嗥��嗆�銋麄����其蜓�菟仪��偌�晞��𪆴�����摰靝耨�選��𤾸���恐����祥�吔��賣����鞈血𦶢撠��撣思誑撘梁�����嗉𥅾��睻�萄暒憯怨竼嚗���贝�埈�蝡哨��芰��乩���")
        if kingb == small:
            result.append("�𥕦抅���皜詨�摰殷�鈭箏�摰靝耨敺瘀�撣��嚗峕��𡢅�靽格郎嚗䔶誑敺∪斥撖���")
        return "".join(result)
        
    def ming_officerbase(self, ji_style, taiyi_acumyear):
        """�舘竼�箏云銋蹱�銝餉�"""
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
            result.append("��抅���蝳誩�摰殷��拇䲰頛𥪜扇嚗諹眼璆萎犖���撣貉扛撣嘥漣嚗諹�憭找遙隞亙�瘝颱�嚗峕�隞亥𠪊�澆��𦒘��對�鈭箸�鞊鞟�嚗���箄㘚靽𨳍��")
        if officerb == pplb:
            result.append("��抅����箏�摰殷�鞈Ｚ��銁雿㵪�瘞穃��嗆平嚗峕錇甇���荔��峕�畾瑕熄��")
        if officerb == tiany:
            result.append("��抅��予銋坔�摰殷��㗇帖���蝢抬�靘萄�銋衤�嚗�����鞈𠰴�韏瑯��")
        if officerb  == earthy:
            result.append("��抅��𧑐銋坔�摰殷��嗅��笔極����峕�憭勗���")
        if officerb == zhifu:
            result.append("��抅���潛泵��悅嚗����旨瘜蓥��𠬍�瘞𤑳���甇ｇ��峕��急𨫀��")
        if officerb == fgod:
            result.append("��抅���蟡𧼮�摰殷��嗅�鞈衣換蝔��嚗䔶誑憟芣����峕偌皝扼��")
        if officerb == big:
            result.append("��抅��之皜詨�摰殷�閮�錇銝滚像嚗諹噙憭思��辷�瘞湔𨫀嚗峕��𤤿垠����垍𢥫����")
        if officerb == small:
            result.append("��抅���皜詨�摰殷�銝衤噩銝𠺪��𥕦����頛𥪜扇銝滚⏚嚗�����銝衤��𢛵��")
        return "".join(result)
        
    def ming_pplbase(self, ji_style, taiyi_acumyear):
        """�擧��箏云銋蹱�銝餉�"""
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
            result.append("瘞穃抅���蝳誩�摰殷�瘞穃���ˊ摰塚��箄郭�胯��")
        if pplb == tiany:
            result.append("瘞穃抅��予銋坔�摰殷��嗅��∠��𡜐��券䪸蝛��押��")
        if pplb ==earthy:
            result.append("瘞穃抅��𧑐銋坔�摰殷��嗅��笔極敶嫣�嚗�成颲脩汙銝齿𤣰嚗峕�憭𡁶𢥫�賬��")
        if pplb ==zhifu:
            result.append("瘞穃抅���潛泵��悅嚗������勗�嚗屸��梹��萇���")
        if pplb ==fgod:
            result.append("瘞穃抅���蟡𧼮�摰殷��嗅�瘞湔𨫀憌Ｚ�嚗峕�憭𡁏�敺踺��")
        if pplb == big:
            result.append("瘞穃抅��之皜詨�摰殷��嗅��萇���偌�梧�鈭箸��噼㜃��")
        if pplb == small:
            result.append("瘞穃抅���皜詨�摰殷��嗅�蝳曄釆�𦠜𤣰嚗��敶寞��艾��")
        return "".join(result)

    def ming_wufu(self, ji_style, taiyi_acumyear):
        """�𦒘�蝳誩云銋蹱�銝餉�"""
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
            result.append("鈭𠉛�����箏�摰殷�鈭箏�蝳誩ˊ蟡帋澈嚗����悅�典��颱�憪见�嚗𣬚�鞈Ｗ��������箇㮾銵苷���嚗䔶��蠘�撖���䜘��")
        if wufu == officerb:
            result.append("鈭𠉛���竼�箏�摰殷�蝳誩⏚頛𥪜扇嚗����悅�典��颱�憪页�鞈Ｙ㮾�嗥�鞎港犖銋见振��")
        if wufu == pplb:
            result.append("鈭𠉛�����箏�摰殷��𥟇�璅�平嚗�予銝讠��䕘�憒��摰桀銁�苷漱銋见�嚗�����鞎港犖��䲰�賢�銋见振��")
        if wufu == fgod:
            result.append("鈭𠉛����蟡𧼮�摰殷��箇�皜𥟇�嚗峕��萇�嚗䔶蜓�厩𢥫嚗�緥瘞𤑳��恬��㗇𨫀�埈偌皝改��拙�瞏啜��")
        if wufu == big:
            result.append("鈭𠉛���之皜詨�摰殷��箇�皜𥕦�嚗���𨀣偌�曹��齿�銋卝��")
        if wufu == small:
            result.append("鈭𠉛����皜詨�摰殷��匧噸���嚗𣬚�敺瑁�����")
        return "".join(result)
        
    def wufu_gb(self, ji_style, taiyi_acumyear):
        """�𦒘�蝳誩�蝞埈�銝餉�"""
        homecal = self.home_cal( ji_style, taiyi_acumyear)
        wufu_good = {tuple([1,11,21,31,41]): "蝳誩⏚�澆�銝颯��",
                 tuple([2,12,22,32,42]): "蝳誩⏚�潛��躰竼摰啜��",
                 tuple([3,13,23,33,43]): "蝳誩⏚�澆�憒���",
                 tuple([4,14,24,34,44]): "蝳誩⏚�澆云摮僐��",
                 tuple([5,15,25,35,45]): "蝳誩⏚�澆云摮僐��",
                 tuple([6,16,26,36,46]): "蝳誩⏚�澆葦撣乓��",
                 tuple([7,17,27,37]): "蝳誩⏚�潔�撠����",
                 tuple([8,18,28,38]): "蝳誩⏚�潔葉撠����",
                 tuple([9,19,29,39]): "蝳誩⏚�潔�撠����",
                 tuple([10,20,30,40]): "蝳誩⏚�澆ㄚ�鉝��"}
        return config.multi_key_dict_get(wufu_good, homecal)

    def ming_tiany(self, ji_style, taiyi_acumyear):
        """�𤾸予銋坔云銋蹱�銝餉�"""
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
            result.append("憭拐���云銋坔�摰殷��單��肽�嚗䔶誑�𤏸�瘙箸𪃾銋麄���蟡䂿�銵䔶�����菜�憭扯絲嚗��銝餅𠂔����菜�嚗䔶犖瘞烐�銵�����𢠃��芾�諹��拐���")
        if tiany == earthy:
            result.append("憭拐���𧑐銋坔�摰殷��嗅��菜��澆�撌亥�撱Ｚ噙獢穃��曉�嚗䔶漱�萇��嗘�嚗𣬚�鞈𠰴権�䀝犖瘞烐��啜��")
        if tiany == zhifu:
            result.append("憭拐����潛泵��悅嚗������勗��菟ㄑ擖厩𪆴�啜��")
        if tiany == fgod:
            result.append("憭拐����蟡𧼮�摰殷��嗅�瘞湔�����芥����迎��蠘�銝漤�𡄯��𡏭��𥡝絲��")
        if tiany == big:
            result.append("憭拐���之皜詨�摰殷��嗅��萄𢞁蝳滢�嚗屸ㄑ�菜�鈭～��")
        if tiany == small:
            result.append("憭拐����皜詨�摰殷��嗅�銝见��潔�嚗䔶��拙�鈭卝��")
        return "".join(result)

    def ming_earthy(self, ji_style, taiyi_acumyear):
        """�𤾸𧑐銋坔云銋蹱�銝餉�"""
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
            result.append("�唬����潛泵��悅嚗����之�晞����頣��笔極���鈭箸��㛖�嚗䔶�蝛�銝齿�嚗諹噙鈭箏��啜��")
        if earthy == fgod:
            result.append("�唬����蟡𧼮�摰殷��嗅�瘞湔𨫀銝滩矽嚗峕�憭𡁶��堆���𧑐銝剔�憒𣇉㺭��")
        if earthy == big:
            result.append("�唬���之皜詨�摰殷��嗅��萄𢞁憭找�嚗諹�瘞烐�嚗𣬚�鞈𡃏�韏瑯��")
        if earthy == small:
            result.append("�唬����皜詨�摰殷��嗅���銁�笔極���瘜蓥誘�渲�嚗䔶蜓�萇���")
        return "".join(result)

    def ming_zhifu(self, ji_style, taiyi_acumyear):
        """�𤾸�潛泵憭芯���銝餉�"""
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
            result.append("�潛泵���蟡𧼮�摰殷��嗅��望飧銋曆�����𥟇�憭梁�嚗峕�憌Ｙ𪆴�怠�����萇�皞箸䲰瘞渡����萎�����")
        if zhifu == big:
            result.append("�潛泵��之皜詨�摰殷��嗅��萄𢞁瘞烐�嚗䔶�蝛�銝齿�嚗𣬚�璈急𠂔韏瑯��")
        if zhifu == small:
            result.append("�潛泵���皜詨�摰殷��嗅��怎�����抬�鈭箸�銝滚���")
        return "".join(result)

    def flybird_wl(self,ji_style, taiyi_acumyear):
        """�典云銋䠷◢�脤�曈亙𨭌�唳�"""
        fb = config.flybird(taiyi_acumyear)
        hg = self.home_general(ji_style, taiyi_acumyear)
        ag = self.away_general(ji_style, taiyi_acumyear)
        hvg = self.home_vgen(ji_style, taiyi_acumyear)
        avg = self.away_vgen(ji_style, taiyi_acumyear)
        ty = self.ty(ji_style, taiyi_acumyear)
        wc = config.gong2.get(self.skyeyes(ji_style, taiyi_acumyear))
        sj = config.gong2.get(self.sf(ji_style, taiyi_acumyear))
        if fb == ty:
            return "憭芯����典悅�厰◢�脤�曈亦�靘���潸翰�𠰴云銋躰���憭扳�銋见���"
        elif fb == wc:
            return "敺硺蜓�桐��餅�摰ｇ�銝餃�"
        elif fb == sj:
            return "敺𧼮恥�桐��餅�銝鳴�摰Ｗ�"
        elif fb == hg or fb == hvg:
            return "憌偦野�嗡蜓鈭粹腼���銝颱犖��"
        elif fb == ag or fb == avg:
            return "憌偦野�嗅恥鈭粹腼���摰Ｖ犖��"
        else:
            return "憌偦野�孵�銝齿�蝣綽���"
    
    def tui_danger(self, ji_style, taiyi_acumyear):
        """�券苊�賭誑�惩���"""
        tai_yi = self.ty(ji_style, taiyi_acumyear)
        tyg = config.num2gong(self.ty(ji_style, taiyi_acumyear))
        homecal = self.home_cal( ji_style, taiyi_acumyear) 
        awaycal = self.away_cal( ji_style, taiyi_acumyear) 
        tyd = config.multi_key_dict_get({tuple([8,3,4,9]): "憭芯��券蒾摰柴��", tuple([1,2,6,7]): "憭芯��券苊摰柴��"}, tai_yi)
        if homecal % 2 != 0 and tyd == "憭芯��券蒾摰柴��":
            hr = "憭芯��券蒾摰殷�銝餌限敺堒�嚗𣬚��漤蒾嚗���函�嚗䔶蜓����"
        if homecal % 2 != 0 and tyd != "憭芯��券蒾摰柴��":
            hr = "憭芯��券苊摰殷�銝餌限敺堒�嚗䔶蜓瘝鍦���"
        if homecal % 2 == 0 and tyd != "憭芯��券苊摰柴��":
            hr = "憭芯��券蒾摰殷�銝餌限敺堒�嚗䔶蜓瘝鍦���"
        if homecal % 2 == 0 and tyd == "憭芯��券苊摰柴��":
            hr = "憭芯��券苊摰殷�銝餌限敺堒�嚗𣬚��漤苊嚗���冽偌嚗䔶蜓����"
        if awaycal % 2 != 0 and tyd == "憭芯��券蒾摰柴��":
            ar = "憭芯��券蒾摰殷�摰Ｙ限敺堒�嚗𣬚��漤蒾嚗���函�嚗�恥����"
        if awaycal % 2 != 0 and tyd != "憭芯��券蒾摰柴��":
            ar = "憭芯��券苊摰殷�摰Ｙ限敺堒�嚗�恥瘝鍦���"
        if awaycal % 2 == 0 and tyd != "憭芯��券苊摰柴��":
            ar = "憭芯��券蒾摰殷�摰Ｙ限敺堒�嚗�恥瘝鍦���"
        if awaycal % 2 == 0 and tyd == "憭芯��券苊摰柴��":
            ar = "憭芯��券苊摰殷�摰Ｙ限敺堒�嚗𣬚��漤苊嚗���冽偌嚗�恥����"
        return hr + ar

    def ty_gong_dist(self, ji_style, taiyi_acumyear):
        """憭芯��典予憭硋𧑐�扳�"""
        tai_yi = self.ty(ji_style, taiyi_acumyear)
        tyg = config.num2gong(self.ty(ji_style, taiyi_acumyear))
        return config.multi_key_dict_get({tuple([1,8,3,4]): "憭芯���"+tyg+"嚗�𨭌銝颯��", tuple([9,2,6,7]): "憭芯���"+tyg+"嚗�𨭌摰Ｕ��"}, tai_yi)

    def threedoors(self, ji_style, taiyi_acumyear):
        """�其����瑚���"""
        taiyi = self.ty(ji_style, taiyi_acumyear)
        eightd = self.geteightdoors(ji_style, taiyi_acumyear)
        door = eightd.get(taiyi)
        if door in list("隡𤑳���"):
            return "銝厰�銝滚���"
        return "銝厰��瑯��"

    def fivegenerals(self, ji_style, taiyi_acumyear):
        """�其�撠�䔄銝滨䔄"""
        home_general = self.home_general(ji_style, taiyi_acumyear)
        away_general = self.away_general(ji_style, taiyi_acumyear)
        if self.skyeyes_des(ji_style, taiyi_acumyear) == "" and home_general != 5 and away_general != 5:
            return "鈭𥪜��潦��"
        if home_general == 5:
            return "銝餃�銝餃�銝滚枂銝剝�嚗峕�憛䂿�����"
        if away_general == 5:
            return "摰Ｗ�摰Ｗ�銝滚枂銝剝�嚗峕�憛䂿�����"
        return self.skyeyes_des(ji_style, taiyi_acumyear)+"���撠���潦��"

    def wc_n_sj(self, ji_style, taiyi_acumyear):
        """�其蜓摰Ｙ㮾�埈�"""
        wan_c = self.skyeyes(ji_style, taiyi_acumyear)
        shi_ji = self.sf(ji_style, taiyi_acumyear)
        wc_f = config.Ganzhiwuxing(wan_c)
        sj_f = config.Ganzhiwuxing(shi_ji)
        home_g = self.home_general(ji_style, taiyi_acumyear)
        tai_yi = self.ty(ji_style, taiyi_acumyear)
        hguan = config.multi_key_dict_get(config.nayin_wuxing, jieqi.gangzhi(self.year, self.month, self.day, self.hour, self.minute)[3])
        if hguan == wc_f:
            guan = "銝駁�"
        if hguan == sj_f:
            guan = "摰ａ�"
        else:
            guan = "��"
        relation = config.multi_key_dict_get(config.wuxing_relation_2, wc_f+sj_f)
        if relation == "�穃�" and tai_yi == home_g:
            return "銝餃��𡄯�銝滚⏚銝�"
        if relation == "�穃�" and tai_yi != home_g:
            return  "銝餃�摰ｇ�銝餃�"
        if relation == "撠��":
            return guan + "敺𦯀蜓鈭綽�摰Ｗ�"
        if relation in ["瘥𥪜�","���","�𤑳�"]:
            return guan + relation + "嚗��"

    def geteightdoors(self, ji_style, taiyi_acumyear):
        """�典������"""
        tai_yi = self.ty(ji_style, taiyi_acumyear)
        new_ty_order = config.new_list([8,3,4,9,2,7,6,1], tai_yi)
        doors  = config.new_list(self.door, config.eight_door(self.accnum(ji_style, taiyi_acumyear)))
        if ji_style != 3:
            return dict(zip(new_ty_order, doors))
        if ji_style == 3:
            alljq = jieqi_name
            j_q = jieqi.jq(self.year, self.month, self.day, self.hour, self.minute)
            jqmap = {tuple(config.new_list(alljq, "�祈秐")[0:12]):"�祈秐", tuple(config.new_list(alljq, "憭讛秐")[0:12]):"憭讛秐"}
            num= self.accnum(ji_style, taiyi_acumyear)
            dun = config.multi_key_dict_get(jqmap, j_q)
            if dun == "憭讛秐":    
                num= num% 120 % 30
                if num> 8:
                    num= num%8
                if num==0:
                    num=8
                num= dict(zip(range(1,9), new_ty_order)).get(num)
                return dict(zip(config.new_list(new_ty_order, num), doors)) 
            if dun == "�祈秐":
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
        k = [an2cn(i) for i in list(self.geteightdoors(ji_style, taiyi_acumyear).keys())]
        v = list(self.geteightdoors(ji_style, taiyi_acumyear).values())
        eightdoors = dict(zip(k,v))
        eightddors_status = dict(zip(k, list(jieqi.gong_wangzhuai().values())))
        return [[i,eightdoors.get(i)+"��", eightddors_status.get(i)] for i in config.new_list(list(eightdoors.keys()), "鈭�")]

    #�賭�銵屸�
    def yangjiu_xingxian(self, sex):
        mg = jieqi.gangzhi(self.year, self.month, self.day, self.hour, self.minute)[1][0]
        num= config.Ganzhi_num(mg)
        place = config.Ganzhi_place(mg)
        return dict(zip(config.generate_ranges(num, 10, 11),{"��":config.new_list(self.di_zhi, place), "憟�":config.new_list(list(reversed(self.di_zhi)), place)}.get(sex)))
    #�曉�銵屸�
    def bailiu_xingxian(self, sex):
        sqn = self.souqi_num()
        sqn_gua = dict(zip(range(1,65), config.jiazi())).get(sqn)
        place = config.cheungsun.get(config.Ganzhiwuxing(sqn_gua[1]))
        num= dict(zip(list("�罸�瘞湔銁��"),[5,4,1,3,2])).get(config.Ganzhiwuxing(place))
        return dict(zip(config.generate_ranges(num, 10, 11),{"��":config.new_list(self.di_zhi, place), "憟�":config.new_list(list(reversed(self.di_zhi)), place)}.get(sex)))

    def souqi_num(self):
        gz = jieqi.gangzhi(self.year, self.month, self.day, self.hour, self.minute)
        dg = config.gangzhi_to_num(gz[2][0])
        dz = config.gangzhi_to_num(gz[2][1])
        hg = config.gangzhi_to_num(gz[3][0])
        hz = config.gangzhi_to_num(gz[3][1])
        dny = config.element_to_num(config.multi_key_dict_get(config.nayin_wuxing, gz[2]))
        hny = config.element_to_num(config.multi_key_dict_get(config.nayin_wuxing, gz[3]))
        return (dg + dz + hg + hz + dny + hny + 55) % 60 

    #�箄澈��
    def life_start_gua(self):
        gz = jieqi.gangzhi(self.year, self.month, self.day, self.hour, self.minute)
        y = config.gangzhi_to_num(gz[0][0]) + config.gangzhi_to_num(gz[0][1]) + config.element_to_num(config.multi_key_dict_get(config.nayin_wuxing, gz[0]))
        m = config.gangzhi_to_num(gz[1][0]) + config.gangzhi_to_num(gz[1][1]) + config.element_to_num(config.multi_key_dict_get(config.nayin_wuxing, gz[1]))
        d = config.gangzhi_to_num(gz[2][0]) + config.gangzhi_to_num(gz[2][1]) + config.element_to_num(config.multi_key_dict_get(config.nayin_wuxing, gz[2]))
        h = config.gangzhi_to_num(gz[3][0]) + config.gangzhi_to_num(gz[3][1]) + config.element_to_num(config.multi_key_dict_get(config.nayin_wuxing, gz[3]))
        return [(y + m + d + h + 55) % 64, config.gua.get((y + m + d + h + 55) % 64)]

    def year_gua(self):
        d = date(self.year, self.month, self.day)
        num= self.life_start_gua()[0] + config.calculateAge(d)
        if num> 64:
            return [num, config.gua.get(num% 64)]
        else:
            return [num, config.gua.get(num)]
        
    def month_gua(self):
        year = self.year_gua()[0]
        month = config.lunar_date_d(self.year, self.month, self.day).get("��")
        num= year + 2 + month
        if num> 64:
            return [num, config.gua.get(num% 64)]
        else:
            return [num, config.gua.get(num)]
        
    def day_gua(self):
        month  = self.month_gua()[0]
        day = dict(zip(config.jiazi(), range(1,61))).get(jieqi.gangzhi(self.year, self.month, self.day, self.hour, self.minute)[2])
        num= month + day
        if num> 64:
            return [num, config.gua.get(num% 64)]
        else:
            return [num, config.gua.get(num)]
        
    def hour_gua(self):
        day = self.day_gua()[0]
        hour = dict(zip(self.di_zhi, range(1,13))).get(jieqi.gangzhi(self.year, self.month, self.day, self.hour, self.minute)[3][1])
        num= day + hour
        if num> 64:
            return [num, config.gua.get(num% 64)]
        else:
            return [num, config.gua.get(num)]
        
    def minute_gua(self):
        hour = self.hour_gua()[0]
        minute = dict(zip(config.jiazi(), range(1,61))).get(jieqi.gangzhi(self.year, self.month, self.day, self.hour, self.minute)[4])
        num= hour + minute
        if num> 64:
            return [num, config.gua.get(num% 64)]
        else:
            return [num, config.gua.get(num)]

    def year_chin(self):
        """憭芣革蝳賣�"""
        su = config.su
        chin_28_stars_code = dict(zip(range(1,29), su))
        year = config.lunar_date_d(self.year, self.month, self.day).get("撟�")
        if config.lunar_date_d(self.year, self.month, self.day).get("��") == "�����" or config.lunar_date_d(self.year, self.month, self.day).get("��") == "�����":
            if jieqi.jq(self.year, self.month, self.day, self.hour, self.minute) == "蝡𧢲坾":
                get_year_chin_number = (int(year)+15) % 28 #瘙�僑蝳賭��砍��箄正��僑��15��28銋钅���
                if get_year_chin_number == int(0):
                    get_year_chin_number = int(28)
                year_chin = chin_28_stars_code.get(get_year_chin_number) #撟渡汗
            else:
                get_year_chin_number = (int(year-1)+15) % 28 #瘙�僑蝳賭��砍��箄正��僑��15��28銋钅���
                if get_year_chin_number == int(0):
                    get_year_chin_number = int(28)
                    year_chin = chin_28_stars_code.get(get_year_chin_number) #撟渡汗
        if config.lunar_date_d(self.year, self.month, self.day).get("��") != "�����" or config.lunar_date_d(self.year, self.month, self.day).get("��") == "�����":
            get_year_chin_number = (int(year)+15) % 28 #瘙�僑蝳賭��砍��箄正��僑��15��28銋钅���
            if get_year_chin_number == int(0):
                get_year_chin_number = int(28)
            year_chin = chin_28_stars_code.get(get_year_chin_number) #撟渡汗
        return year_chin

    def gen_gong(self, ji_style, taiyi_acumyear, tenching): #�匧�蝎�1, �∪�蝎�0
        sixteengongs = {0: self.sixteen_gong3( ji_style, taiyi_acumyear), 1:self.sixteen_gong( ji_style, taiyi_acumyear) }.get(tenching)
        if ji_style in [0,1]:
            return chart.gen_chart( list(sixteengongs.values())[-1], self.geteightdoors_text2(ji_style, taiyi_acumyear), list(sixteengongs.values())[:-1])
        if ji_style in [2]:
            dict1 = config.gpan1(self.year, self.month, self.day, self.hour, self.minute)
            middle = dict1[0][1]
            ng = dict1[1]
            return chart.gen_chart_day( list(sixteengongs.values())[-1] + [middle], self.geteightdoors_text2(ji_style, taiyi_acumyear), ng, list(sixteengongs.values())[:-1])
        if ji_style in [3,4]:
            #j_q = jieqi.jq(self.year, self.month, self.day, self.hour, self.minute)
            #d = jieqi.gangzhi(self.year, self.month, self.day, self.hour, self.minute)[2]
            #h = jieqi.gangzhi(self.year, self.month, self.day, self.hour, self.minute)[2]
            #m = config.lunar_date_d(self.year, self.month, self.day).get("��")
            #sg = [ kinliuren.Liuren(j_q, m, d, h).result(0).get("�啗�憭拙�").get(i) for i in list("撌喳��芰𤚗�㗇�鈭亙�銝穃��航劓")]
            earth_sky = self.lr().sky_n_earth_list()
            g = dict(zip(list("鞎渲�����㗲樴滨征�𤾸虜��苊��"), re.findall('..', '鞎港犖����梢��剖��暸䒰�㘾�憭拍征�質�憭芸虜��郎憭芷苊憭拙�')))
            general = self.lr().result(0).get("�啗�憭拙�")
            k = list(general.keys())
            v = list(general.values())
            vnew = [g.get(i) for i in v]
            general = dict(zip(k, vnew))
            #three_passes = [i[0]+self.lr().result(0).get("銝匧�").get(i)[0]+self.lr().result(0).get("銝匧�").get(i)[1][0] for i in ['�嘥�','銝剖�','�怠�']]
            res = {"撌�":" ", "��":" ", "��":" ", "��":" ", "��":" ", "��":" ", "��":" ", "銋�":" ", "鈭�":" ", "摮�":" ", "銝�":" ", "��":" ","撖�":" ", "��":" ", "颲�":" ", "撌�":" "}
            res1 = {"撌�":" ", "��":" ", "��":" ", "��":" ", "��":" ", "��":" ", "��":" ", "銋�":" ", "鈭�":" ", "摮�":" ", "銝�":" ", "��":" ","撖�":" ", "��":" ", "颲�":" ", "撌�":" "}
            res.update(general)
            res1.update(earth_sky)
            sg = [[list(res.values())[i], list(res1.values())[i] ] for i in range(0,len(list(res.values())))]
            return chart.gen_chart_hour( list(sixteengongs.values())[-1]+[" "," "], self.geteightdoors_text2(ji_style, taiyi_acumyear), sg,list(sixteengongs.values())[:-1], self.twenty_eightstar(ji_style, taiyi_acumyear))
#憭芯��賣�
    def gen_life_gong(self, sex):
        res = {"撌�":" ", "��":" ", "��":" ", "��":" ", "��":" ", "��":" ", "鈭�":" ", "摮�":" ", "銝�":" ","撖�":" ", "��":" ", "颲�":" "}
        dict1 = self.taiyi_life(sex).get("����賢悅�鍦�")
        res.update(dict1)
        sg = list(res.values())
        return chart.gen_chart_life( list(self.sixteen_gong11(4,0).values())[-1], sg, [self.sixteen_gong11(4,0).get(i) for i in list(res.keys())])

    def gen_life_gong_list(self, sex):
        res = {"撌�":" ", "��":" ", "��":" ", "��":" ", "��":" ", "��":" ", "鈭�":" ", "摮�":" ", "銝�":" ","撖�":" ", "��":" ", "颲�":" "}
        dict1 = self.taiyi_life(sex).get("����賢悅�鍦�")
        res.update(dict1)
        sg = list(res.values())
        return  list(self.sixteen_gong11(4,0).values())[-1], sg, [self.sixteen_gong11(4,0).get(i) for i in list(res.keys())]

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
                text_output += f"�𨫆key}�髢n{value_str}\n\n"
            else:
                text_output += f"�𨫆key}�髢n{value}\n\n"
        return text_output.replace('[', '').replace(']', '').replace(',', '').replace("'","")

    def gongs_discription_text(self, sex):
        alld = self.gongs_discription_list(sex)
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
        
    def twostar_disc(self, sex):
        a = taiyi_life_dict.twostars
        b = self.gongs_discription_list(sex)
        b = {key: [''.join(value)] for key, value in b.items()}
        c = {}
        for key, values in b.items():
            c[key] = []
            for val in values:
                val_set = set(val)  # 頧㗇����
                sub_dict = [
                    k + "��悅��" + a[k] 
                    for k in a 
                    if set(k) <= val_set  # k �� val_set �����
                ]
                c[key].append(sub_dict)
        for key, values in c.items():
            c[key] = [item for item in values[0] if item]  # Remove empty lists
        return c
        
    def gongs_discription_list(self, sex):
        sixteengongs = self.sixteen_gong11(3,0)
        t = self.gen_life_gong_list(sex)[1]
        stars = self.gen_life_gong_list(sex)[2]
        alld =  dict(zip(t, stars))
        for key, value in alld.items():
            if not value:
                alld[key] = ["蝛箸聢"]
        return alld
    
    def gongs_discription(self, sex):
        alld = self.gongs_discription_list(sex)
        combined_dict = {}
        for category, subcategories in alld.items():
            combined_dict[category] = []
            for subcategory in subcategories:
                if subcategory in taiyi_life_dict.twelve_gong_stars[category]:
                    combined_dict[category].append(taiyi_life_dict.twelve_gong_stars[category][subcategory])
        return combined_dict
    
    
    def sixteen_gong2(self, ji_style, taiyi_acumyear):
        original_dict = self.sixteen_gong1(ji_style, taiyi_acumyear)
        c = "鈭𠉛�,�𥕦抅,��抅,瘞穃抅,���,閮��,撠𤩺虜,銝餃之,摰Ｗ之,銝餃�,摰Ｗ�,憪𧢲�,憌𤤿泵,�𤤿�,憭拐�,�唬�".split(",")
        a = {star: key for key, values in original_dict.items() for star in values if star in c}
        d = dict(zip(self.di_zhi, range(0,13)))
        for star, gong_value in a.items():
            a[star] = d[gong_value]
        return  a
    
    def stars_descriptions(self, ji_style, taiyi_acumyear):
        starszhi = self.sixteen_gong2(ji_style, taiyi_acumyear)
        c = "鈭𠉛�,�𥕦抅,��抅,瘞穃抅,���,閮��,撠𤩺虜,銝餃之,摰Ｗ之,銝餃�,摰Ｗ�,憪𧢲�,憌𤤿泵,�𤤿�,憭拐�,�唬�".split(",")
        allstar = {}
        for i in c:
            try:
                a = {i:taiyi_life_dict.stars_twelve.get(i)[starszhi.get(i)]}
                allstar.update(a)
            except IndexError:
                pass
        return allstar

    def stars_descriptions_text(self, ji_style, taiyi_acumyear):
        alld = self.stars_descriptions(ji_style, taiyi_acumyear)
        text = ""
        for key, value in alld.items():
            text += f"�𨫆key}�髢n{value}\n\n"
        return text
    
    def sixteen_gong_grades(self, ji_style, taiyi_acumyear):
        original_dict = self.sixteen_gong1(ji_style, taiyi_acumyear)
        c = "鈭𠉛�,�𥕦抅,��抅,瘞穃抅,撠𤩺虜,���,銝餃之,銝餃�,閮��,憪𧢲�,摰Ｗ之,摰Ｗ�,�𤤿�,憭拐�,�唬�,�渡泵".split(",")
        a = {star: key for key, values in original_dict.items() for star in values if star in c}
        alld = dict(zip(c,[config.multi_key_dict_get(taiyi_life_dict.sixteen_three_grades.get(i), a.get(i)) for i in c])) 
        text = ""
        for key, value in alld.items():
            text += f"�𨫆key}�髢n{value}\n\n"
        return text
    
    def taiyi_life(self, sex):
        twelve_gongs = "�賢悅,���,憒餃汙,摮𣂼重,鞎∪�,�啣�,摰条正,憟游�,�曉�,蝳誩噸,�貉�,�嗆�".split(",")
        gz = jieqi.gangzhi(self.year, self.month, self.day, self.hour, self.minute)
        yz = gz[0][1]
        mz = gz[1][1]
        dz = gz[2][1]
        hz = gz[3][1]
        self.di_zhi = self.di_zhi
        skypan = dict(zip(config.new_list(self.di_zhi, mz), config.new_list(list(reversed(self.di_zhi)), hz)))
        num= self.di_zhi.index(yz)
        yy = config.multi_key_dict_get({tuple(self.di_zhi[0::2]):"��", tuple(self.di_zhi[1::2]):"��"}, yz)
        direction =  config.multi_key_dict_get({("�琿蒾","憟喲苊"):"��", ("�琿苊", "憟喲蒾"):"��"}, sex+yy)
        zhinum = dict(zip(self.di_zhi,range(1,13)))
        #�賢悅�埝�
        yz_arrange = dict(zip(range(1,13),config.new_list(self.di_zhi,yz)))[zhinum[yz]]
        mz_arrange = dict(zip(range(1,13),config.new_list(self.di_zhi,yz_arrange)))[zhinum[mz]]
        mz_arrange_r = dict(zip(range(1,13),config.new_list(list(reversed(self.di_zhi)),yz_arrange)))[zhinum[mz]]
        #頨怠悅�埝�
        mz1_arrange = dict(zip(range(1,13),config.new_list(self.di_zhi,mz)))[zhinum[mz]]
        dz_arrange =  dict(zip(range(1,13),config.new_list(self.di_zhi,mz1_arrange)))[zhinum[dz]]
        dz_arrange_r = dict(zip(range(1,13),config.new_list(list(reversed(self.di_zhi)),dz_arrange)))[zhinum[dz]]
        d_arrangelist = {"��":config.new_list(self.di_zhi, dz_arrange_r), "��":config.new_list(self.di_zhi, dz_arrange)}.get(direction)
        arrangelist = {"��":config.new_list(self.di_zhi, mz_arrange_r), "��":config.new_list(self.di_zhi, mz_arrange)}.get(direction)
        #�瑞�
        fly_lu = config.multi_key_dict_get({tuple(list("�脖�")):"鈭�", tuple(list("銝嗘�")):"撖�", tuple(list("�𠰴楛")):"��", tuple(list("摨朞�")):"撌�",tuple(list("憯祉烵")):"��" }, gz[0][0])
        fly_horse = config.multi_key_dict_get({tuple(list("�脖�")):"鈭�", tuple(list("銝嗘�")):"撖�", tuple(list("�𠰴楛")):"��", tuple(list("摨朞�")):"撌�",tuple(list("憯祉烵")):"��" }, gz[3][0])
        blackfu = config.multi_key_dict_get(dict(zip(list("�脖�銝嗘��𠰴楛摨朞�憯祉烵"), list("撖�晓摮𣂷漸�屸��單𧊋��歲"))), gz[3][0])
        pan = {
                "�批³�":"{}{}".format(yy,sex),
                "�箇��交�":config.gendatetime(self.year, self.month, self.day, self.hour, self.minute),
                "�箇�撟脫𣈲":jieqi.gangzhi(self.year, self.month, self.day, self.hour, self.minute),
                "颲脫�":config.lunar_date_d(self.year, self.month, self.day),
                "蝝���":self.jiyuan(0,0),
                "憭芣革":self.taishui(0),
                "�賢�":self.kook(0,0),
                "摰匧𦶢摰�":arrangelist[0],
                "摰㕑澈摰�":d_arrangelist[0],
                "憌𤤿正":fly_lu,
                "憌偦收":fly_horse,
                "暺𤑳泵":blackfu,
                "憭拍𥿢":skypan,
                "����賢悅�鍦�":dict(zip(arrangelist, twelve_gongs)),
                "�賭�":config.yangjiu(self.year, self.month, self.day),
                "�曉�":config.baliu(self.year, self.month, self.day),
                "�賭�銵屸�": self.yangjiu_xingxian(sex),
                "�曉�銵屸�": self.bailiu_xingxian(sex),
                "憭芯��賢悅":self.ty(0,0),
                "�箄澈��":self.life_start_gua()[1],
                "撟游㩋":self.year_gua()[1], 
                "��㩋":self.month_gua()[1], 
                "�亙㩋":self.day_gua()[1], 
                "��㩋":self.hour_gua()[1], 
                "��㩋":self.minute_gua()[1], 
                "憭芯�":self.ty_gong(0,0),
                "憭拐�":self.skyyi(0,0),
                "�唬�":self.earthyi(0,0),
                "�𤤿�":self.fgd(0,0),
                "�渡泵":self.zhifu(0,0),
                "���":[self.skyeyes(0,0), self.skyeyes_des(0,0)],
                "憪𧢲�":self.sf(0,0),
                "銝餌�":[self.home_cal(0,0), config.cal_des(self.home_cal(0,0))],
                "銝餃�":self.home_general(0,0),
                "銝餃�":self.home_vgen(0,0),
                "摰Ｙ�":[self.away_cal(0,0), config.cal_des(self.away_cal(0,0))],
                "摰Ｗ�":self.away_general(0,0),
                "摰Ｗ�":self.away_vgen(0,0),
                "摰𡁶�":[self.set_cal(0,0), config.cal_des(self.set_cal(0,0))],
                "���":self.hegod(0),
                "閮��":self.jigod(0),
                "摰𡁶𤌍":self.se(0,0),
                "�𥕦抅":self.kingbase(0,0),
                "��抅":self.officerbase(0,0),
                "瘞穃抅":self.pplbase(0,0),
                "鈭𠉛�":config.wufu(self.accnum(0,0)),
                "撣萘泵":config.kingfu(self.accnum(0,0)),
                "憭芸�":config.taijun(self.accnum(0,0)),
                "憌偦野":config.flybird(self.accnum(0,0)),
                "銝厰◢":config.threewind(self.accnum(0,0)),
                "鈭娪◢":config.fivewind(self.accnum(0,0)),
                "�恍◢":config.eightwind(self.accnum(0,0)),
                "憭扳虜":config.bigyo(self.accnum(0,0)),
                "撠𤩺虜":config.smyo(self.accnum(0,0))}
        return pan
    
    def pan(self, ji_style, taiyi_acumyear):
        """韏瑞𥿢閰喟敦�批捆"""
        return {
                "憭芯�閮�":config.taiyi_name(ji_style),
                "憭芯��砍�憿𧼮³�":config.ty_method(taiyi_acumyear),
                "�砍��交�":config.gendatetime(self.year, self.month, self.day, self.hour, self.minute),
                "撟脫𣈲":jieqi.gangzhi(self.year, self.month, self.day, self.hour, self.minute),
                "颲脫�":config.lunar_date_d(self.year, self.month, self.day),
                "撟渲�":config.kingyear(config.lunar_date_d(self.year, self.month, self.day).get("撟�")),
                "蝝���":self.jiyuan(ji_style, taiyi_acumyear),
                "憭芣革":self.taishui(ji_style),
                "撅�撘�":self.kook(ji_style, taiyi_acumyear),
                "鈭𥪜����":self.get_five_yuan_kook(ji_style, taiyi_acumyear),
                "�賭�":config.yangjiu(self.year, self.month, self.day),
                "�曉�":config.baliu(self.year, self.month, self.day),
                "憭芯��賢悅":self.ty(ji_style, taiyi_acumyear),
                "憭芯�":self.ty_gong(ji_style, taiyi_acumyear),
                "憭拐�":self.skyyi(ji_style, taiyi_acumyear),
                "�唬�":self.earthyi(ji_style, taiyi_acumyear),
                "�𤤿�":self.fgd(ji_style, taiyi_acumyear),
                "�渡泵":self.zhifu(ji_style, taiyi_acumyear),
                "���":[self.skyeyes(ji_style, taiyi_acumyear), self.skyeyes_des(ji_style, taiyi_acumyear)],
                "憪𧢲�":self.sf(ji_style, taiyi_acumyear),
                "銝餌�":[self.home_cal(ji_style, taiyi_acumyear), config.cal_des(self.home_cal(ji_style, taiyi_acumyear))],
                "銝餃�":self.home_general(ji_style, taiyi_acumyear),
                "銝餃�":self.home_vgen(ji_style, taiyi_acumyear),
                "摰Ｙ�":[self.away_cal(ji_style, taiyi_acumyear), config.cal_des(self.away_cal(ji_style, taiyi_acumyear))],
                "摰Ｗ�":self.away_general(ji_style, taiyi_acumyear),
                "摰Ｗ�":self.away_vgen(ji_style, taiyi_acumyear),
                "摰𡁶�":[self.set_cal(ji_style, taiyi_acumyear), config.cal_des(self.set_cal(ji_style, taiyi_acumyear))],
                "���":self.hegod(ji_style),
                "閮��":self.jigod(ji_style),
                "摰𡁶𤌍":self.se(ji_style, taiyi_acumyear),
                "�𥕦抅":self.kingbase(ji_style, taiyi_acumyear),
                "��抅":self.officerbase(ji_style, taiyi_acumyear),
                "瘞穃抅":self.pplbase(ji_style, taiyi_acumyear),
                "鈭𠉛�":config.wufu(self.accnum(ji_style, taiyi_acumyear)),
                "撣萘泵":config.kingfu(self.accnum(ji_style, taiyi_acumyear)),
                "憭芸�":config.taijun(self.accnum(ji_style, taiyi_acumyear)),
                "憌偦野":config.flybird(self.accnum(ji_style, taiyi_acumyear)),
                "銝厰◢":config.threewind(self.accnum(ji_style, taiyi_acumyear)),
                "鈭娪◢":config.fivewind(self.accnum(ji_style, taiyi_acumyear)),
                "�恍◢":config.eightwind(self.accnum(ji_style, taiyi_acumyear)),
                "憭扳虜":config.bigyo(self.accnum(ji_style, taiyi_acumyear)),
                "撠𤩺虜":config.smyo(self.accnum(ji_style, taiyi_acumyear)),
                "�穃遆�厰𨘥":config.gpan(self.year, self.month, self.day, self.hour, self.minute),
                "鈭���怠挪�潭𠯫":config.starhouse(self.year, self.month, self.day, self.hour, self.minute),
                "憭芣革鈭���怠挪":self.year_chin(),
                "憭芣革�澆挪�瑚�": su_dist.get(self.year_chin()),
                "憪𧢲�鈭���怠挪":self.sf_num(ji_style, taiyi_acumyear),
                "憪𧢲��澆挪�瑚�":su_dist.get(self.sf_num(ji_style, taiyi_acumyear)),
                "��予撟脫革憪𧢲��賢悅�鞉葫": config.multi_key_dict_get (tengan_shiji, jieqi.gangzhi(self.year, self.month, self.day, self.hour, self.minute)[0][0]).get(config.Ganzhiwuxing(self.sf(ji_style, taiyi_acumyear))),
                "�恍��潔�":config.eight_door(self.accnum(ji_style, taiyi_acumyear)),
                "�恍����":self.geteightdoors(ji_style, taiyi_acumyear),
                "�怠悅�箄※":jieqi.gong_wangzhuai(),
                "�典云銋嗵訜���": self.shensha(ji_style, taiyi_acumyear),
                "�其����瑚���":self.threedoors(ji_style, taiyi_acumyear),
                "�其�撠�䔄銝滨䔄":self.fivegenerals(ji_style, taiyi_acumyear),
                "�其蜓摰Ｙ㮾�埈�":self.wc_n_sj(ji_style, taiyi_acumyear),
                "�券苊�賭誑�惩���":self.tui_danger(ji_style, taiyi_acumyear),
                "�𤾸予摮𣂼楚�拐��蠘�":self.tianzi_go(ji_style, taiyi_acumyear),
                "�𤾸��箏云銋蹱�銝餉�":self.ming_kingbase(ji_style, taiyi_acumyear),
                "�舘竼�箏云銋蹱�銝餉�":self.ming_officerbase(ji_style, taiyi_acumyear),
                "�擧��箏云銋蹱�銝餉�":self.ming_pplbase(ji_style, taiyi_acumyear),
                "�𦒘�蝳誩云銋蹱�銝餉�":self.ming_wufu(ji_style, taiyi_acumyear),
                "�𦒘�蝳誩�蝞埈�銝餉�":self.wufu_gb(ji_style, taiyi_acumyear),
                "�𤾸予銋坔云銋蹱�銝餉�":self.ming_tiany(ji_style, taiyi_acumyear),
                "�𤾸𧑐銋坔云銋蹱�銝餉�":self.ming_earthy(ji_style, taiyi_acumyear),
                "�𤾸�潛泵憭芯���銝餉�":self.ming_zhifu(ji_style, taiyi_acumyear),
                "�典�撠睲誑�惩�鞎�":config.suenwl(self.home_cal(ji_style, taiyi_acumyear),
                                        self.away_cal(ji_style, taiyi_acumyear),
                                        self.home_general(ji_style, taiyi_acumyear),
                                        self.away_general(ji_style, taiyi_acumyear)),
                "�典云銋䠷◢�脤�曈亙𨭌�唳�": self.flybird_wl(ji_style, taiyi_acumyear),
                "�典迨�桐誑�䭾���":self.gudan(ji_style, taiyi_acumyear), 
                "�券𡺨�砍�瘞�":config.leigong(self.ty(ji_style, taiyi_acumyear)),
                "�刻𠪊瘣亙���":config.lijin(self.year, self.month, self.day, self.hour, self.minute),
                "�函�摮𣂼���":config.lion(self.year, self.month, self.day, self.hour, self.minute),
                "�函蒾�脫㬢蝛�":config.cloud(self.home_general(ji_style, taiyi_acumyear)),
                "�函��𡒊㮾��":config.tiger(self.ty(ji_style, taiyi_acumyear)),
                "�函蒾樴滚���":config.dragon(self.ty(ji_style, taiyi_acumyear)),
                "�典�頠滨�閮�":config.returnarmy(self.away_general(ji_style, taiyi_acumyear)),
                }

if __name__ == '__main__':
    tic = time.perf_counter()
    year = 2025
    month = 7
    day = 13
    hour = 12
    minute = 6
    #print(Taiyi(year, month, day, hour, minute).kingbase(3,0))
    print(Taiyi(year, month, day, hour, minute).twenty_eightstar(3,0))
    #life1 = Taiyi(year, month, day, hour, minute).gongs_discription("��")
    #life2 = Taiyi(year, month, day, hour, minute).twostar_disc("��")
    #print(Taiyi(year, month, day, hour, minute).convert_gongs_text(life1, life2))
    #print(life1)
    #print(Taiyi(year, month, day, hour, minute).taiyi_life("��"))
    #print(Taiyi(year, month, day, hour, minute).gongs_discription("��"))
    #print(Taiyi(year, month, day, hour, minute).gongs_discription_list("��"))
    #print(Taiyi(year, month, day, hour, minute).taiyi_life("��"))
    #print(Taiyi(year, month, day, hour, minute).gen_gong(3,0))
    #print(Taiyi(year, month, day, hour, minute).geteightdoors_text2(2,0))
    #print(Taiyi(year, month, day, hour, minute).yangjiu_xingxian("��"))
    #print(Taiyi(year, month, day, hour, minute).kook(0, 0))
    #print(Taiyi(year, month, day, hour, minute).kook(1, 0))
    #print(Taiyi(year, month, day, hour, minute).kook(2, 0))
    #print(Taiyi(year, month, day, hour, minute).kook(3, 0))
    #print(Taiyi(year, month, day, hour, minute).kook(4, 0))

    toc = time.perf_counter()
    print(f"{toc - tic:0.4f} seconds")
