# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 16:46:02 2023
@author: kentang
"""

import drawsvg as draw
import math

# ======================  共用顏色設定  ======================
SECOND_LAYER_COLORS = {
    '子': 'blue', '亥': 'blue',
    '丑': 'brown', '未': 'brown', '辰': 'brown', '戌': 'brown',
    '坤': 'brown', '艮': 'brown',
    '寅': 'green', '卯': 'green', '巽': 'green',
    '巳': 'red',   '午': 'red',
    '乾': 'gold',  '酉': 'gold', '申': 'gold',
}

TEXT_COLORS = {
    'blue':  'white',
    'brown': 'white',
    'green': 'white',
    'red':   'white',
    'gold':  'black',
    'black': 'white',
    'gray':  'white',
    'orange':'black',
    'silver':'black',
}

CONSTELLATION_COLORS = {
    '角': 'green', '斗': 'green', '奎': 'green', '井': 'green',
    '尾': 'red',   '室': 'red', '觜': 'red', '翼': 'red',
    '亢': 'gold',  '牛': 'gold', '婁': 'gold', '鬼': 'gold',
    '箕': 'blue',  '壁': 'blue', '參': 'blue', '軫': 'blue',
    '氐': 'brown', '女': 'brown', '胃': 'brown', '柳': 'brown',
    '房': 'orange','虛': 'orange','昴': 'orange','星': 'orange',
    '心': 'silver','危': 'silver','畢': 'silver','張': 'silver',
}
# =========================================================

def _format_label(label):
    """把 list → 換行字串，字串直接回傳"""
    if isinstance(label, list):
        return '\n'.join(str(x) for x in label)
    return str(label)

def _draw_sector(group, layer_idx, div, start, end, inner, outer,
                 raw_label, is_second=False, is_28=False):
    """共用繪製扇形 + 標籤（支援 list）"""
    # ---- 座標 ----
    sox = outer * math.cos(math.radians(start))
    soy = outer * math.sin(math.radians(start))
    eox = outer * math.cos(math.radians(end))
    eoy = outer * math.sin(math.radians(end))
    six = inner * math.cos(math.radians(start))
    siy = inner * math.sin(math.radians(start))
    eix = inner * math.cos(math.radians(end))
    eiy = inner * math.sin(math.radians(end))

    # ---- 顏色 ----
    if is_second:
        # 第二層用字串的第一個字（地支/卦）找顏色
        key = raw_label[0] if isinstance(raw_label, list) else raw_label
        fill = SECOND_LAYER_COLORS.get(key, 'gray')
    elif is_28:
        fill = CONSTELLATION_COLORS.get(raw_label, 'gray')
    else:
        fill = 'black'
    text_fill = TEXT_COLORS.get(fill, 'white')

    # ---- 路徑 ----
    p = draw.Path(stroke='white', stroke_width=1.8, fill=fill)
    p.M(six, siy)
    p.L(sox, soy)
    p.A(outer, outer, 0, 0, 1, eox, eoy)
    p.L(eix, eiy)
    p.A(inner, inner, 0, 0, 0, six, siy)
    p.Z()
    group.append(p)

    # ---- 標籤（支援換行）----
    label_str = _format_label(raw_label)
    mid = (start + end) / 2
    tx = (inner + outer) / 2 * math.cos(math.radians(mid))
    ty = (inner + outer) / 2 * math.sin(math.radians(mid))
    t = draw.Text(label_str, 9, tx, ty, center=1, fill=text_fill,
                  font_family='sans-serif')
    group.append(t)

# ====================  gen_chart  ====================
def gen_chart(first_layer, second_layer, sixth_layer):
    d = draw.Drawing(400, 400, origin="center")
    inner_radius = 13
    layer_gap = 45
    num_divisions = [1, 8, 16, 16]

    data = [
        [first_layer],
        second_layer,
        [['巳','大神','楚'], ['午','大威','荊州'], ['未','天道','秦'], ['坤','大武','梁州'],
         ['申','武德','晉'], ['酉','太簇','趙雍'], ['戌','陰主','魯'], ['乾','陰德','冀州'],
         ['亥','大義','衛'], ['子','地主','齊兗'], ['丑','陽德','吳'], ['艮','和德','青州'],
         ['寅','呂申','燕'], ['卯','高叢','徐州'], ['辰','太陽','鄭'], ['巽','大炅','揚州']],
        sixth_layer
    ]
    rotation_angle = 248

    for layer_idx, divs in enumerate(num_divisions):
        layer = draw.Group(id=f'layer{layer_idx+1}')
        for div in range(divs):
            start = (360 / divs) * div + rotation_angle
            end   = (360 / divs) * (div + 1) + rotation_angle
            raw_label = data[layer_idx][div]

            inner = inner_radius + layer_idx * layer_gap
            outer = inner_radius + (layer_idx + 1) * layer_gap

            _draw_sector(layer, layer_idx, div, start, end,
                         inner, outer, raw_label,
                         is_second=(layer_idx == 1))
        d.append(layer)

    return d.as_svg().replace(
        '''<path d="M-4.86988571440686,-12.053390109368236 L-21.72718241812291,-53.776663564873665 A58,58,0,0,1,-21.727182418122876,-53.77666356487368 L-4.869885714406852,-12.053390109368237 A13,13,0,0,0,-4.86988571440686,-12.053390109368236 Z" stroke="white" stroke-width="1.8" fill="black" />''', "")

# ====================  gen_chart_life  ====================
def gen_chart_life(second_layer, twelve, sixth_layer):
    d = draw.Drawing(380, 380, origin="center")
    inner_radius = 12
    layer_gap = 35
    num_divisions = [1, 12, 12, 12]

    data = [
        [second_layer],
        twelve,
        ['巳','午','未','申','酉','戌','亥','子','丑','寅','卯','辰'],
        sixth_layer
    ]
    rotation_angle = 248

    for layer_idx, divs in enumerate(num_divisions):
        layer = draw.Group(id=f'layer{layer_idx+1}')
        for div in range(divs):
            start = (360 / divs) * div + rotation_angle
            end   = (360 / divs) * (div + 1) + rotation_angle
            raw_label = data[layer_idx][div]

            inner = inner_radius + layer_idx * layer_gap
            outer = inner_radius + (layer_idx + 1) * layer_gap

            # 這裡 second_layer 變成第 0 層
            _draw_sector(layer, layer_idx, div, start, end,
                         inner, outer, raw_label,
                         is_second=(layer_idx == 0))
        d.append(layer)

    return d.as_svg().replace(
        '''<path d="M-4.495279120990947,-11.126206254801447 L-17.606509890547876,-43.577641164639005 A47,47,0,0,1,-17.606509890547848,-43.57764116463901 L-4.49527912099094,-11.12620625480145 A12,12,0,0,0,-4.495279120990947,-11.126206254801447 Z" stroke="white" stroke-width="1.8" fill="black" />''', "")

# ====================  gen_chart_day  ====================
def gen_chart_day(first_layer, second_layer, golden, sixth_layer):
    d = draw.Drawing(400, 400, origin="center")
    inner_radius = 3
    layer_gap = 31.5
    num_divisions = [1, 8, 8, 16, 16]

    data = [
        [first_layer],
        second_layer,
        golden,
        [['巳','大神','楚'], ['午','大威','荊州'], ['未','天道','秦'], ['坤','大武','梁州'],
         ['申','武德','晉'], ['酉','太簇','趙雍'], ['戌','陰主','魯'], ['乾','陰德','冀州'],
         ['亥','大義','衛'], ['子','地主','齊兗'], ['丑','陽德','吳'], ['艮','和德','青州'],
         ['寅','呂申','燕'], ['卯','高叢','徐州'], ['辰','太陽','鄭'], ['巽','大炅','揚州']],
        sixth_layer
    ]
    rotation_angle = 248

    for layer_idx, divs in enumerate(num_divisions):
        layer = draw.Group(id=f'layer{layer_idx+1}')
        for div in range(divs):
            start = (360 / divs) * div + rotation_angle
            end   = (360 / divs) * (div + 1) + rotation_angle
            raw_label = data[layer_idx][div]

            inner = inner_radius + layer_idx * layer_gap
            outer = inner_radius + (layer_idx + 1) * layer_gap

            _draw_sector(layer, layer_idx, div, start, end,
                         inner, outer, raw_label,
                         is_second=(layer_idx == 1))
        d.append(layer)

    return d.as_svg().replace(
        '''<path d="M-1.1238197802477368,-2.781551563700362 L-12.923927472848973,-31.987842982554163 A34.5,34.5,0,0,1,-12.923927472848954,-31.98784298255417 L-1.123819780247735,-2.7815515637003627 A3.0,3.0,0,0,0,-1.1238197802477368,-2.781551563700362 Z" stroke="white" stroke-width="1.8" fill="black" />''', "")

# ====================  gen_chart_hour  ====================
def gen_chart_hour(first_layer, second_layer, skygeneral, sixth_layer, twentyeight, degrees):
    d = draw.Drawing(400, 400, origin="center")
    inner_radius = 3
    layer_gap = 31.5
    num_divisions = [1, 8, 16, 16, 16, 28]

    data = [
        [first_layer],
        second_layer,
        skygeneral,
        [['巳','大神','楚'], ['午','大威','荊州'], ['未','天道','秦'], ['坤','大武','梁州'],
         ['申','武德','晉'], ['酉','太簇','趙雍'], ['戌','陰主','魯'], ['乾','陰德','冀州'],
         ['亥','大義','衛'], ['子','地主','齊兗'], ['丑','陽德','吳'], ['艮','和德','青州'],
         ['寅','呂申','燕'], ['卯','高叢','徐州'], ['辰','太陽','鄭'], ['巽','大炅','揚州']],
        sixth_layer,
        twentyeight
    ]
    rotation_angle = 248

    # 28宿累積角度
    cumulative = [0]
    for deg in degrees:
        cumulative.append(cumulative[-1] + deg)

    for layer_idx, divs in enumerate(num_divisions):
        layer = draw.Group(id=f'layer{layer_idx+1}')
        for div in range(divs):
            if layer_idx == 5:   # 28宿
                start = cumulative[div] + rotation_angle
                end   = cumulative[div + 1] + rotation_angle
            else:
                start = (360 / divs) * div + rotation_angle
                end   = (360 / divs) * (div + 1) + rotation_angle

            raw_label = data[layer_idx][div]

            inner = inner_radius + layer_idx * layer_gap
            outer = inner_radius + (layer_idx + 1) * layer_gap

            _draw_sector(layer, layer_idx, div, start, end,
                         inner, outer, raw_label,
                         is_second=(layer_idx == 1),
                         is_28=(layer_idx == 5))
        d.append(layer)

    return d.as_svg().replace(
        '''<path d="M-1.1238197802477368,-2.781551563700362 L-12.923927472848973,-31.987842982554163 A34.5,34.5,0,0,1,-12.923927472848954,-31.98784298255417 L-1.123819780247735,-2.7815515637003627 A3.0,3.0,0,0,0,-1.1238197802477368,-2.781551563700362 Z" stroke="white" stroke-width="1.8" fill="black" />''', "")
