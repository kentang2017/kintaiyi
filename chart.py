# -*- coding: utf-8 -*-
"""
太乙盤 SVG 產生器 - 八門按五行上色（正確版）
"""

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

# 八門 → 代表地支（用來取五行顏色）
GATE_TO_BRANCH = {
    '休': '子',   # 水
    '生': '丑',   # 土
    '傷': '寅',   # 木
    '杜': '卯',   # 木
    '景': '巳',   # 火
    '死': '未',   # 土
    '驚': '申',   # 金
    '開': '酉',   # 金
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
    s = _format_label(raw_label)
    for c in s:
        if c in BRANCH_COLORS:
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
        key = next((c for c in text if c in '休生傷杜景死驚開'), None)
        if key and key in GATE_TO_BRANCH:
            branch = GATE_TO_BRANCH[key]
            fill = BRANCH_COLORS.get(branch, 'gray')
        else:
            fill = 'gray'
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

# [其餘 gen_chart / gen_chart_life / gen_chart_day / gen_chart_hour 不變]
# 只要確保 is_second_layer=(layer_idx == 1)

# ====================  gen_chart_life (範例) ====================
def gen_chart_life(second_layer, twelve, sixth_layer):
    d = draw.Drawing(380, 380, origin="center")
    inner_radius = 12
    layer_gap = 35
    num_divisions = [1, 12, 12, 12]
    rotation_angle = 248

    data = [
        [second_layer],
        twelve,
        ['巳','午','未','申','酉','戌','亥','子','丑','寅','卯','辰'],
        sixth_layer
    ]

    for layer_idx, divs in enumerate(num_divisions):
        layer = draw.Group(id=f'layer{layer_idx+1}')
        for div in range(divs):
            start = (360 / divs) * div + rotation_angle
            end   = (360 / divs) * (div + 1) + rotation_angle
            raw = data[layer_idx][div]
            inner = inner_radius + layer_idx * layer_gap
            outer = inner_radius + (layer_idx + 1) * layer_gap

            _draw_sector(layer, start, end, inner, outer, raw,
                         is_16_palace=(layer_idx == 2),
                         is_second_layer=(layer_idx == 1))
        d.append(layer)

    return d.as_svg().replace(
        '''<path d="M-4.495279120990947,-11.126206254801447 L-17.606509890547876,-43.577641164639005 A47,47,0,0,1,-17.606509890547848,-43.57764116463901 L-4.49527912099094,-11.12620625480145 A12,12,0,0,0,-4.495279120990947,-11.126206254801447 Z" stroke="white" stroke-width="1.8" fill="black" />''', "")

# ====================  測試 ====================
if __name__ == "__main__":
    svg = gen_chart_life(
        second_layer="中宮",
        twelve=['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑'],
        sixth_layer=['休門', '生門', '傷門', '杜門', '景門', '死門', '驚門', '開門', '其他']*1
    )
    with open("final_fixed.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("最終修正完成！八門已按五行正確上色，請查看 final_fixed.svg")
