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

GATE_TO_BRANCH = {
    '休': '子', '生': '丑', '傷': '寅', '杜': '卯',
    '景': '巳', '死': '未', '驚': '申', '開': '酉',
}

# 第五層：關鍵字 → 顏色 + 優先級
FIFTH_LAYER_KEYWORDS = {
    '太乙': 'green', '客參': 'green',           # 木
    '飛符': 'red', '始擊': 'red', '直符': 'red', '計神': 'red',  # 火
    '主大': 'gold', '天乙': 'gold', '大游': 'gold',             # 金
    '主參': 'blue', '客大': 'blue', '小游': 'blue', '四神': 'blue', # 水
    '五福': 'brown', '文昌': 'brown', '地乙': 'brown',
    '君基': 'brown', '臣基': 'brown', '民基': 'brown',           # 土
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
                 is_16_palace=False, is_28_layer=False,
                 is_second_layer=False, is_third_layer=False, is_fifth_layer=False):
    # ---- 座標 ----
    sox = outer * math.cos(math.radians(start))
    soy = outer * math.sin(math.radians(start))
    eox = outer * math.cos(math.radians(end))
    eoy = outer * math.sin(math.radians(end))
    six = inner * math.cos(math.radians(start))
    siy = inner * math.sin(math.radians(start))
    eix = inner * math.cos(math.radians(end))
    eiy = inner * math.sin(math.radians(end))

    # ---- 背景色 ----
    fill = 'black'
    if is_second_layer:
        text = _format_label(raw_label)
        key = next((c for c in text if c in GATE_TO_BRANCH), None)
        if key:
            fill = BRANCH_COLORS.get(GATE_TO_BRANCH[key], 'gray')
        else:
            fill = 'gray'
    elif is_third_layer or is_16_palace:
        key = _get_branch_key(raw_label)
        fill = BRANCH_COLORS.get(key, 'gray')
    elif is_28_layer:
        key = raw_label[0] if isinstance(raw_label, list) and raw_label else str(raw_label)
        fill = CONSTELLATION_COLORS.get(key, 'gray')

    # ---- 文字顏色（第五層：精確匹配 + 優先級）----
    text_fill = TEXT_COLORS.get(fill, 'white')
    if is_fifth_layer:
        candidates = []
        if isinstance(raw_label, list):
            for item in raw_label:
                item_str = str(item)
                if item_str in FIFTH_LAYER_KEYWORDS:
                    candidates.append(item_str)
        else:
            label_str = str(raw_label)
            if label_str in FIFTH_LAYER_KEYWORDS:
                candidates.append(label_str)

        if candidates:
            # 優先級：木 > 火 > 金 > 水 > 土
            priority = [
                ['太乙', '客參'],
                ['飛符', '始擊', '直符', '計神'],
                ['主大', '天乙', '大游'],
                ['主參', '客大', '小游', '四神'],
                ['五福', '文昌', '地乙', '君基', '臣基', '民基']
            ]
            for group in priority:
                for keyword in group:
                    if keyword in candidates:
                        text_fill = FIFTH_LAYER_KEYWORDS[keyword]
                        break
                else:
                    continue
                break

    # ---- 路徑 ----
    p = draw.Path(stroke='white', stroke_width=1.8, fill=fill)
    p.M(six, siy)
    p.L(sox, soy)
    p.A(outer, outer, 0, 0, 1, eox, eoy)
    p.L(eix, eiy)
    p.A(inner, inner, 0, 0, 0, six, siy)
    p.Z()
    group.append(p)

    # ---- 標籤 ----
    label_str = _format_label(raw_label)
    mid = (start + end) / 2
    tx = (inner + outer) / 2 * math.cos(math.radians(mid))
    ty = (inner + outer) / 2 * math.sin(math.radians(mid))
    t = draw.Text(label_str, 9, tx, ty, center=1, fill=text_fill,
                  font_family='sans-serif', font_weight='bold')
    group.append(t)


# ====================  其餘 gen_chart* 函數不變 ====================
def gen_chart_life(second_layer, twelve, sixth_layer):
    d = draw.Drawing(380, 380, origin="center")
    inner_radius = 12
    layer_gap = 35
    num_divisions = [1, 12, 12, 12]          # 第 3 層 = index 2
    rotation_angle = 248

    data = [
        [second_layer],
        twelve,                              # 第 2 層
        ['巳','午','未','申','酉','戌','亥','子','丑','寅','卯','辰'],  # 第 3 層（地支）
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
                         is_16_palace=(layer_idx == 2),   # 第 4 層（index 3）是 16 宮
                         is_second_layer=(layer_idx == 1),
                         is_third_layer=(layer_idx == 2)) # 第 3 層
        d.append(layer)

    return d.as_svg().replace(
        '''<path d="M-4.495279120990947,-11.126206254801447 L-17.606509890547876,-43.577641164639005 A47,47,0,0,1,-17.606509890547848,-43.57764116463901 L-4.49527912099094,-11.12620625480145 A12,12,0,0,0,-4.495279120990947,-11.126206254801447 Z" stroke="white" stroke-width="1.8" fill="black" />''', "")


# ====================  gen_chart_hour ====================
def gen_chart_hour(first_layer, second_layer, skygeneral, sixth_layer,
                   twentyeight, degrees, rotate_28=0):
    d = draw.Drawing(400, 400, origin="center")
    inner_radius = 3
    layer_gap = 31.5
    num_divisions = [1, 8, 16, 16, 16, 28]
    rotation_angle = 248

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

    cumulative = [0]
    for deg in degrees:
        cumulative.append(cumulative[-1] + deg)

    for layer_idx, divs in enumerate(num_divisions):
        layer = draw.Group(id=f'layer{layer_idx+1}')
        for div in range(divs):
            if layer_idx == 5:
                start = cumulative[div] + rotation_angle + rotate_28
                end   = cumulative[div + 1] + rotation_angle + rotate_28
            else:
                start = (360 / divs) * div + rotation_angle
                end   = (360 / divs) * (div + 1) + rotation_angle

            raw = data[layer_idx][div]
            inner = inner_radius + layer_idx * layer_gap
            outer = inner_radius + (layer_idx + 1) * layer_gap

            _draw_sector(layer, start, end, inner, outer, raw,
                         is_16_palace=(layer_idx == 3),
                         is_second_layer=(layer_idx == 1),
                         is_third_layer=(layer_idx == 2),
                         is_fifth_layer=(layer_idx == 4),
                         is_28_layer=(layer_idx == 5))
        d.append(layer)

    return d.as_svg().replace(
        '''<path d="M-1.1238197802477368,-2.781551563700362 L-12.923927472848973,-31.987842982554163 A34.5,34.5,0,0,1,-12.923927472848954,-31.98784298255417 L-1.123819780247735,-2.7815515637003627 A3.0,3.0,0,0,0,-1.1238197802477368,-2.781551563700362 Z" stroke="white" stroke-width="1.8" fill="black" />''', "")


# ====================  動態測試範例 ====================
if __name__ == "__main__":
    constellations = ['角','亢','氐','房','心','尾','箕','斗','牛','女','虛','危',
                     '室','壁','奎','婁','胃','昴','畢','觜','參','井','鬼','柳',
                     '星','張','翼','軫']

    # 動態第五層：包含多五行衝突
    fifth_layer_dynamic = [
        ['巳', '太乙', '飛符'],     # 木+火 → 選木（優先）
        ['午', '五福', '主參'],     # 土+水 → 選水
        ['未', '天乙'],            # 金
        ['坤', '計神', '文昌'],     # 火+土 → 選火
        ['申', '客參'],            # 木
        ['酉', '直符'],            # 火
        ['戌', '君基'],            # 土
        ['乾', '大游'],            # 金
        ['亥', '四神'],            # 水
        ['子', '地乙'],            # 土
        ['丑', '始擊'],            # 火
        ['艮', '小游'],            # 水
        ['寅', '臣基'],            # 土
        ['卯', '民基'],            # 土
        ['辰', '主大'],            # 金
        ['巽', '客大'],            # 水
    ]

    svg = gen_chart_hour(
        first_layer="太乙",
        second_layer=['休門','生門','傷門','杜門','景門','死門','驚門','開門'],
        skygeneral=['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥','子','丑','寅','卯'],
        sixth_layer=fifth_layer_dynamic,
        twentyeight=constellations,
        degrees=[360/28]*28,
        rotate_28=-6
    )
    with open("final_dynamic_priority.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("動態盤局 + 多五行衝突 測試完成！")
    print("優先級：木 > 火 > 金 > 水 > 土")

