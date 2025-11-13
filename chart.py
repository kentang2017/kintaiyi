# -*- coding: utf-8 -*-

import drawsvg as draw
import math

# ======================  共用顏色設定  ======================
BRANCH_COLORS = {
    '子': 'blue',  '亥': 'blue',
    '丑': 'brown', '未': 'brown', '辰': 'brown', '戌': 'brown',
    '寅': 'green', '卯': 'green',
    '巳': 'red',   '午': 'red',
    '申': 'gold',  '酉': 'gold',
    '乾': 'gold',  '坤': 'brown', '艮': 'brown', '巽': 'green',
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

EIGHT_GATES_COLORS = {
    '景': 'red',
    '驚': 'gold', '開': 'gold',
    '生': 'brown', '死': 'brown',
    '休': 'blue',
    '杜': 'green', '傷': 'green',
}

TEXT_COLORS = {
    'blue':  'white', 'brown': 'white', 'green': 'white',
    'red':   'white', 'gold':  'black', 'orange':'black',
    'silver':'black', 'black': 'white', 'gray':  'white',
}
# =========================================================

def _format_label(raw):
    if isinstance(raw, list):
        return '\n'.join(str(x) for x in raw)
    return str(raw)

def _get_branch_key(raw_label):
    if isinstance(raw_label, list) and raw_label:
        s = str(raw_label[0])
    else:
        s = str(raw_label)
    for c in s:
        if '\u4e00' <= c <= '\u9fff':
            return c
    return ''

def _draw_sector(group, start, end, inner, outer, raw_label,
                 is_16_palace=False, is_28_layer=False, is_second_layer=False):
    sox = outer * math.cos(math.radians(start))
    soy = outer * math.sin(math.radians(start))
    eox = outer * math.cos(math.radians(end))
    eoy = outer * math.sin(math.radians(end))
    six = inner * math.cos(math.radians(start))
    siy = inner * math.sin(math.radians(start))
    eix = inner * math.cos(math.radians(end))
    eiy = inner * math.sin(math.radians(end))

    fill = 'black'
    if is_second_layer:
        text = _format_label(raw_label)
        key = next((c for c in text if '\u4e00' <= c <= '\u9fff'), None)
        fill = EIGHT_GATES_COLORS.get(key, 'gray') if key else 'gray'
    elif is_16_palace:
        key = _get_branch_key(raw_label)
        fill = BRANCH_COLORS.get(key, 'gray')
    elif is_28_layer:
        key = raw_label[0] if isinstance(raw_label, list) and raw_label else str(raw_label)
        fill = CONSTELLATION_COLORS.get(key, 'gray')

    text_fill = TEXT_COLORS.get(fill, 'white')

    p = draw.Path(stroke='white', stroke_width=1.8, fill=fill)
    p.M(six, siy)
    p.L(sox, soy)
    p.A(outer, outer, 0, 0, 1, eox, eoy)
    p.L(eix, eiy)
    p.A(inner, inner, 0, 0, 0, six, siy)
    p.Z()
    group.append(p)

    label_str = _format_label(raw_label)
    mid = (start + end) / 2
    tx = (inner + outer) / 2 * math.cos(math.radians(mid))
    ty = (inner + outer) / 2 * math.sin(math.radians(mid))
    t = draw.Text(label_str, 9, tx, ty, center=1, fill=text_fill,
                  font_family='sans-serif', font_weight='bold')
    group.append(t)

# [其餘 gen_chart / gen_chart_life / gen_chart_day / gen_chart_hour 保持不變，只確保傳 is_second_layer=(layer_idx == 1)]

# ====================  gen_chart_hour (範例) ====================
def gen_chart_hour(first_layer, second_layer, skygeneral, sixth_layer, twentyeight, degrees):
    d = draw.Drawing(400, 400, origin="center")
    inner_radius = 3
    layer_gap = 31.5
    num_divisions = [1, 8, 16, 16, 16, 28]
    rotation_angle = 248

    data = [ [first_layer], second_layer, skygeneral,
        [['巳','大神','楚'], ['午','大威','荊州'], ['未','天道','秦'], ['坤','大武','梁州'],
         ['申','武德','晉'], ['酉','太簇','趙雍'], ['戌','陰主','魯'], ['乾','陰德','冀州'],
         ['亥','大義','衛'], ['子','地主','齊兗'], ['丑','陽德','吳'], ['艮','和德','青州'],
         ['寅','呂申','燕'], ['卯','高叢','徐州'], ['辰','太陽','鄭'], ['巽','大炅','揚州']],
        sixth_layer, twentyeight ]

    cumulative = [0] + [sum(degrees[:i+1]) for i in range(len(degrees))]

    for layer_idx, divs in enumerate(num_divisions):
        layer = draw.Group(id=f'layer{layer_idx+1}')
        for div in range(divs):
            if layer_idx == 5:
                start = cumulative[div] + rotation_angle
                end   = cumulative[div + 1] + rotation_angle
            else:
                start = (360 / divs) * div + rotation_angle
                end   = (360 / divs) * (div + 1) + rotation_angle
            raw = data[layer_idx][div]
            inner = inner_radius + layer_idx * layer_gap
            outer = inner_radius + (layer_idx + 1) * layer_gap
            _draw_sector(layer, start, end, inner, outer, raw,
                         is_16_palace=(layer_idx == 3),
                         is_second_layer=(layer_idx == 1),
                         is_28_layer=(layer_idx == 5))
        d.append(layer)

    return d.as_svg().replace(
        '''<path d="M-1.1238197802477368,-2.781551563700362 L-12.923927472848973,-31.987842982554163 A34.5,34.5,0,0,1,-12.923927472848954,-31.98784298255417 L-1.123819780247735,-2.7815515637003627 A3.0,3.0,0,0,0,-1.1238197802477368,-2.781551563700362 Z" stroke="white" stroke-width="1.8" fill="black" />''', "")

# ====================  測試 ====================
if __name__ == "__main__":
    svg = gen_chart_hour(
        first_layer="太乙",
        second_layer=['休門', '生門', '傷門', '杜門', '景門', '死門', '驚門', '開門'],
        skygeneral=['天1', '天2', '天3', '天4', '天5', '天6', '天7', '天8'],
        sixth_layer=[['巳','大神','楚']] * 16,
        twentyeight=['角']*28,
        degrees=[360/28]*28
    )
    with open("fixed.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("已修正！請查看 fixed.svg")
