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
    """取出第一個屬於 BRANCH_COLORS 的字元（地支/八卦）"""
    s = _format_label(raw_label)
    for c in s:
        if c in BRANCH_COLORS:
            return c
    return ''


_PRIORITY_TOKENS = ("太乙", "文昌", "始擊", "主大", "客大", "合神", "計神", "天乙", "地乙", "直符")
_SIXTEEN = "巳午未坤申酉戌乾亥子丑艮寅卯辰巽"
_TWELVE = "巳午未申酉戌亥子丑寅卯辰"
_PLANET_RING = "午未申酉戌亥子丑寅卯辰巳"


def _label_parts(raw_label):
    if isinstance(raw_label, list):
        return [str(x).strip() for x in raw_label if str(x).strip()]
    if raw_label is None:
        return []
    s = str(raw_label).strip()
    return [s] if s else []


def _compact_label(parts, layer_role, branch=""):
    if layer_role == "center":
        for p in parts:
            if p and p != " ":
                return p[:2] if len(p) > 1 else p
        return "中"
    if layer_role == "door":
        for p in parts:
            for ch in p:
                if ch in GATE_TO_BRANCH:
                    return ch
        return (parts[0][:1] if parts else "")
    if layer_role in ("palace_template", "branch"):
        return branch or (parts[0][:1] if parts else "")
    if layer_role == "life_palace":
        p = parts[0] if parts else ""
        return p[0] if p else ""
    joined = "".join(parts)
    for tok in _PRIORITY_TOKENS:
        if tok in joined:
            return tok[0]
    for p in parts:
        if p and p not in (" ", "　"):
            return p[0]
    return branch[:1] if branch else ""


def _sector_meta(raw_label, layer_role=""):
    parts = _label_parts(raw_label)
    label_str = _format_label(raw_label)
    branch = ""
    god = ""
    region = ""
    if isinstance(raw_label, list) and raw_label:
        branch = raw_label[0] if raw_label[0] in BRANCH_COLORS else _get_branch_key(raw_label)
        if len(raw_label) > 1:
            god = str(raw_label[1])
        if len(raw_label) > 2:
            region = str(raw_label[2])
    else:
        branch = _get_branch_key(raw_label)
        if layer_role == "door":
            god = parts[0] if parts else ""
    compact = _compact_label(parts, layer_role, branch)
    return {
        "branch": branch,
        "god": god,
        "region": region,
        "compact": compact,
        "full": label_str,
        "role": layer_role,
    }


def _role_for(chart_kind, layer_idx):
    roles = {
        "year": ["center", "door", "palace_template", "palace_content", "star12"],
        "day": ["center", "door", "golden", "palace_template", "palace_content", "star12"],
        "hour": ["center", "door", "skygeneral", "palace_template", "palace_content", "star28", "star12"],
        "life": ["center", "life_palace", "branch", "palace_content", "star12"],
    }.get(chart_kind, [])
    return roles[layer_idx] if layer_idx < len(roles) else ""


def _pos_branch(sector_idx, sector_count, layer_role="", raw_label=None):
    if sector_count == 16 and sector_idx < 16:
        return _SIXTEEN[sector_idx]
    if sector_count == 12 and sector_idx < 12:
        order = _PLANET_RING if layer_role == "star12" else _TWELVE
        return order[sector_idx]
    if sector_count == 8 and layer_role == "door":
        text = _format_label(raw_label)
        key = next((c for c in text if c in GATE_TO_BRANCH), None)
        return GATE_TO_BRANCH.get(key, "")
    return ""


def _draw_sector(group, start, end, inner, outer, raw_label,
                 is_16_palace=False, is_28_layer=False,
                 is_second_layer=False, is_third_layer=False,
                 layer_id="", sector_idx=0, layer_role="",
                 sector_count=0):
    """共用繪製扇形 + 標籤（支援第 3 層）"""
    # ---- 座標 ----
    sox = outer * math.cos(math.radians(start))
    soy = outer * math.sin(math.radians(start))
    eox = outer * math.cos(math.radians(end))
    eoy = outer * math.sin(math.radians(end))
    six = inner * math.cos(math.radians(start))
    siy = inner * math.sin(math.radians(start))
    eix = inner * math.cos(math.radians(end))
    eiy = inner * math.sin(math.radians(end))

    # ---- 顏色邏輯（優先順序：第 2 層 > 第 3 層 > 16宮 > 28宿）----
    fill = 'black'   # 預設
    if is_second_layer:                     # 八門 → 五行
        text = _format_label(raw_label)
        key = next((c for c in text if c in GATE_TO_BRANCH), None)
        if key:
            fill = BRANCH_COLORS.get(GATE_TO_BRANCH[key], 'gray')
        else:
            fill = 'gray'
    elif is_third_layer:                    # 第 3 層 → 地支五行
        key = _get_branch_key(raw_label)
        fill = BRANCH_COLORS.get(key, 'gray')
    elif is_16_palace:                      # 16 宮 → 地支五行
        key = _get_branch_key(raw_label)
        fill = BRANCH_COLORS.get(key, 'gray')
    elif is_28_layer:                       # 28 宿 → 宿名
        key = raw_label[0] if isinstance(raw_label, list) and raw_label else str(raw_label)
        fill = CONSTELLATION_COLORS.get(key, 'gray')

    text_fill = TEXT_COLORS.get(fill, 'white')
    meta = _sector_meta(raw_label, layer_role)
    label_str = meta["full"]

    sector_g = draw.Group(id=f"{layer_id}-s{sector_idx}" if layer_id else None)
    sector_g.args["class"] = "taiyi-sector"
    if layer_id:
        sector_g.args["data-layer"] = layer_id
        sector_g.args["data-sector"] = str(sector_idx)
        sector_g.args["data-role"] = layer_role or ""
        sector_g.args["data-compact"] = meta["compact"]
        sector_g.args["data-full"] = label_str
        if meta["branch"]:
            sector_g.args["data-branch"] = meta["branch"]
        pos_branch = _pos_branch(sector_idx, sector_count, layer_role, raw_label)
        if pos_branch:
            sector_g.args["data-pos-branch"] = pos_branch
        if meta["god"]:
            sector_g.args["data-god"] = meta["god"]
        if meta["region"]:
            sector_g.args["data-region"] = meta["region"]
        sector_g.args["data-tooltip-key"] = f"{layer_id}:{sector_idx}"

    p = draw.Path(stroke='white', stroke_width=1.8, fill=fill)
    p.M(six, siy)
    p.L(sox, soy)
    p.A(outer, outer, 0, 0, 1, eox, eoy)
    p.L(eix, eiy)
    p.A(inner, inner, 0, 0, 0, six, siy)
    p.Z()
    sector_g.append(p)

    mid = (start + end) / 2
    tx = (inner + outer) / 2 * math.cos(math.radians(mid))
    ty = (inner + outer) / 2 * math.sin(math.radians(mid))
    t = draw.Text(label_str, 9, tx, ty, center=1, fill=text_fill,
                  font_family='sans-serif', font_weight='bold')
    sector_g.append(t)
    group.append(sector_g)


# ======================  古典美學裝飾  ======================
# 依「美學主義者」視角，為排盤增添古典章法之美：外緣雙線金環、八方珠飾、
# 中央太乙印記，皆為純粹附加之裝飾層，不改動原有宮位座標與 viewBox，
# 故不影響前端轉盤(rotation)與解析邏輯。
_TRIGRAMS = ["☰", "☱", "☲", "☳", "☴", "☵", "☶", "☷"]   # 乾兒離震巴坎艰坤（河圖序）

# 後天八卦方位序：對應十六宮之子(坎)、艰、卯(震)、巴、午(離)、坤、酉(兒)、乾
# 用於最外環「八卦天盤」活盤標記；其方位隨排局旋轉（trigram_rotate）。
_EIGHT_PALACE_TRIGRAMS = ["☵", "☶", "☳", "☴", "☲", "☷", "☱", "☰"]  # 坎艰震巴離坤兒乾
_EIGHT_PALACE_NAMES = ["坎", "艰", "震", "巴", "離", "坤", "兒", "乾"]
_ROTATION_ANGLE = 248  # 與 gen_chart 系列之 rotation_angle 一致

# 三旗顏色（卷十）：青龍旗綠、太陰黑旗黑、害氣赤旗紅
_SANQI_COLORS = {
    "太歲青龍旗": "#2faa5e",
    "太陰黑旗": "#15171f",
    "害氣赤旗": "#c43a2b",
}
# 十六宮／十二宮地支序（供三旗定位角度；扇區序定義見檔案前段 _SIXTEEN / _TWELVE）
# 注意：此序須與 gen_chart 等函式之十六宮扇區資料順序一致（起巳，順行），
# 否則三旗會落在錯誤宮位（舊序起子，導致青旗/黑旗誤落乾、赤旗誤落坤）。


def _flag_angle(chen, palace_order=None):
    """地支／八卦宮在宮環上之角度（度）。

    palace_order 預設為十六宮序；命法十二宮圖傳入 _TWELVE。
    """
    order = palace_order if palace_order is not None else _SIXTEEN
    idx = order.index(chen)
    return _ROTATION_ANGLE + (360.0 / len(order)) * (idx + 0.5)


def _draw_flag(d, ang_deg, r_inner, r_outer, color, tang=0.0):
    """繪一面旗：徑向旗桿 + 三角旗旆（tang 為切向偏移以避重疊）。"""
    import math as _m
    a = _m.radians(ang_deg)
    ca, sa = _m.cos(a), _m.sin(a)
    ta, tca = -sa, ca
    bx, by = r_inner * ca + tang * ta, r_inner * sa + tang * tca
    ex, ey = r_outer * ca + tang * ta, r_outer * sa + tang * tca
    d.append(draw.Line(bx, by, ex, ey, stroke="#e9cc88", stroke_width=1.4))
    ph = max(4.0, (r_outer - r_inner) * 0.7)
    W = max(3.5, (r_outer - r_inner) * 0.55)
    r_top, r_bot = r_outer, r_outer - ph
    p1x, p1y = r_top * ca + tang * ta, r_top * sa + tang * tca
    p2x, p2y = r_bot * ca + tang * ta, r_bot * sa + tang * tca
    mr = (r_top + r_bot) / 2.0
    mx, my = mr * ca + tang * ta, mr * sa + tang * tca
    tipx, tipy = mx + W * ta, my + W * tca
    d.append(draw.Lines(p1x, p1y, p2x, p2y, tipx, tipy,
                        close=True, fill=color, stroke="#e9cc88", stroke_width=1.1))


def _add_ornament(d, outer_r, jewels=16, sanqi=None, trigram_rotate=0.0, palace_order=None):
    """古典美學裝飾層（純附加，不改動宮位座標與 viewBox）。

    1. 玄色古典底盤（深靛墨）襯托全局，最外環不再露白，白／米色文字清晰可見；
    2. 外緣雙線金環、八方珠飾；
    3. 三旗行宮旗旆（卷十）：青龍旗(綠)、太陰黑旗(黑)、害氣赤旗(紅)，
       按各旗所落地支宮位之角度顯示於外緣，同宮者切向散開避免重疊；
    4. 八卦天盤活盤：外緣空間足夠(≥26px)時，依後天八卦方位序置八卦，
       並隨排局以 trigram_rotate 旋轉，故不同排局八卦方位不同。
    """
    import math as _m
    from collections import defaultdict
    if palace_order is None:
        palace_order = _SIXTEEN if jewels != 12 else _TWELVE
    half = (d.view_box[2] / 2.0) if getattr(d, "view_box", None) else 250.0
    band = half - outer_r
    # —— 1. 玄色古典底盤 ——
    d.insert(0, draw.Circle(0, 0, half, fill="#141826", stroke="#c79a4e", stroke_width=1.6))
    d.append(draw.Circle(0, 0, 13, stroke="#c79a4e", stroke_width=0.9, fill="none"))
    # —— 2. 外緣雙線金環 + 八方珠飾 ——
    r1 = outer_r + max(2.0, band * 0.30)
    r2 = outer_r + max(5.0, band * 0.62)
    d.append(draw.Circle(0, 0, r1, stroke="#c79a4e", stroke_width=1.3, fill="none"))
    d.append(draw.Circle(0, 0, r2, stroke="#c79a4e", stroke_width=0.9, fill="none"))
    rr = (r1 + r2) / 2.0
    for i in range(jewels):
        ang = _m.radians((360 / jewels) * i + _ROTATION_ANGLE + (360 / jewels) / 2)
        d.append(draw.Circle(rr * _m.cos(ang), rr * _m.sin(ang), 1.7,
                             fill="#e9cc88", stroke="none"))
    # —— 3. 三旗行宮旗旆 ——
    if sanqi:
        items = [("太歲青龍旗", sanqi.get("太歲青龍旗")),
                 ("太陰黑旗", sanqi.get("太陰黑旗")),
                 ("害氣赤旗", sanqi.get("害氣赤旗"))]
        angles = []
        for name, chen in items:
            ang = _flag_angle(chen, palace_order) if (chen and chen in palace_order) else None
            angles.append((name, ang))
        groups = defaultdict(list)
        for k, (name, ang) in enumerate(angles):
            if ang is not None:
                groups[round(ang, 1)].append(k)
        tang_map = {}
        for ks in groups.values():
            n = len(ks)
            for pos, k in enumerate(ks):
                tang_map[k] = (pos - (n - 1) / 2.0) * 6.0
        r_in = max(outer_r - 3.0, 13.0)
        pole_len = min(max(10.0, (half - 1.5) - r_in), 20.0)
        r_out = r_in + pole_len
        for k, (name, ang) in enumerate(angles):
            if ang is None:
                continue
            _draw_flag(d, ang, r_in, r_out, _SANQI_COLORS[name], tang=tang_map.get(k, 0.0))
    # —— 4. 八卦天盤活盤 ——
    if band >= 26:
        tr = r2 + (half - r2) * 0.55
        for i in range(8):
            ang = _m.radians(_ROTATION_ANGLE + (360.0 / 16) * (2 * i + 0.5) + trigram_rotate)
            d.append(draw.Text(_EIGHT_PALACE_TRIGRAMS[i], 12, tr * _m.cos(ang), tr * _m.sin(ang),
                                center=1, fill="#e9cc88", font_family="serif",
                                font_weight="bold"))

# ====================  gen_chart  ====================
def gen_chart(first_layer, second_layer, sixth_layer, sevenstars, sanqi=None, trigram_rotate=0.0):
    d = draw.Drawing(500, 500, origin="center")
    inner_radius = 13
    layer_gap = 45
    num_divisions = [1, 8, 16, 16, 12]
    rotation_angle = 248

    data = [
        [first_layer],
        second_layer,
        [['巳','大神','楚'], ['午','大威','荊州'], ['未','天道','秦'], ['坤','大武','梁州'],
         ['申','武德','晉'], ['酉','太簇','趙雍'], ['戌','陰主','魯'], ['乾','陰德','冀州'],
         ['亥','大義','衛'], ['子','地主','齊兗'], ['丑','陽德','吳'], ['艮','和德','青州'],
         ['寅','呂申','燕'], ['卯','高叢','徐州'], ['辰','太陽','鄭'], ['巽','大炅','揚州']],
        sixth_layer,
        sevenstars
    ]

    for layer_idx, divs in enumerate(num_divisions):
        layer = draw.Group(id=f'layer{layer_idx+1}')
        for div in range(divs):
            start = (360 / divs) * div + rotation_angle
            end   = (360 / divs) * (div + 1) + rotation_angle
            raw = data[layer_idx][div]
            inner = inner_radius + layer_idx * layer_gap
            outer = inner_radius + (layer_idx + 1) * layer_gap

            lid = f"layer{layer_idx + 1}"
            _draw_sector(layer, start, end, inner, outer, raw,
                         is_16_palace=(layer_idx == 2),
                         is_second_layer=(layer_idx == 1),
                         layer_id=lid, sector_idx=div,
                         layer_role=_role_for("year", layer_idx),
                         sector_count=divs)
        d.append(layer)

    _add_ornament(d, 13 + 5 * 45, jewels=16, sanqi=sanqi, trigram_rotate=trigram_rotate, palace_order=_SIXTEEN)
    return d.as_svg().replace(
        '''<path d="M-4.86988571440686,-12.053390109368236 L-21.72718241812291,-53.776663564873665 A58,58,0,0,1,-21.727182418122876,-53.77666356487368 L-4.869885714406852,-12.053390109368237 A13,13,0,0,0,-4.86988571440686,-12.053390109368236 Z" stroke="white" stroke-width="1.8" fill="black" />''', "")


# ====================  gen_chart_life  ====================
def gen_chart_life(second_layer, twelve, sixth_layer, sevenstars, sanqi=None, trigram_rotate=0.0):
    d = draw.Drawing(450, 450, origin="center")
    inner_radius = 12
    layer_gap = 35
    num_divisions = [1, 12, 12, 12, 12]          # 第 3 層 = index 2
    rotation_angle = 248

    data = [
        [second_layer],
        twelve,                              # 第 2 層
        ['巳','午','未','申','酉','戌','亥','子','丑','寅','卯','辰'],  # 第 3 層（地支）
        sixth_layer,
        sevenstars
    ]

    for layer_idx, divs in enumerate(num_divisions):
        layer = draw.Group(id=f'layer{layer_idx+1}')
        for div in range(divs):
            start = (360 / divs) * div + rotation_angle
            end   = (360 / divs) * (div + 1) + rotation_angle
            raw = data[layer_idx][div]
            inner = inner_radius + layer_idx * layer_gap
            outer = inner_radius + (layer_idx + 1) * layer_gap

            lid = f"layer{layer_idx + 1}"
            _draw_sector(layer, start, end, inner, outer, raw,
                         is_16_palace=(layer_idx == 2),
                         is_second_layer=(layer_idx == 1),
                         is_third_layer=(layer_idx == 2),
                         layer_id=lid, sector_idx=div,
                         layer_role=_role_for("life", layer_idx),
                         sector_count=divs)
        d.append(layer)

    _add_ornament(d, 12 + 5 * 35, jewels=12, sanqi=sanqi, trigram_rotate=trigram_rotate, palace_order=_TWELVE)
    return d.as_svg().replace(
        '''<path d="M-4.495279120990947,-11.126206254801447 L-17.606509890547876,-43.577641164639005 A47,47,0,0,1,-17.606509890547848,-43.57764116463901 L-4.49527912099094,-11.12620625480145 A12,12,0,0,0,-4.495279120990947,-11.126206254801447 Z" stroke="white" stroke-width="1.8" fill="black" />''', "")


# ====================  gen_chart_day  ====================
def gen_chart_day(first_layer, second_layer, golden, sixth_layer, seven_stars, sanqi=None, trigram_rotate=0.0):
    d = draw.Drawing(500, 500, origin="center")
    inner_radius = 3
    layer_gap = 31.5
    num_divisions = [1, 8, 8, 16, 16, 12]          # 第 3 層 = index 2
    rotation_angle = 248

    data = [
        [first_layer],
        second_layer,
        golden,                               # 第 3 層（可放地支或文字）
        [['巳','大神','楚'], ['午','大威','荊州'], ['未','天道','秦'], ['坤','大武','梁州'],
         ['申','武德','晉'], ['酉','太簇','趙雍'], ['戌','陰主','魯'], ['乾','陰德','冀州'],
         ['亥','大義','衛'], ['子','地主','齊兗'], ['丑','陽德','吳'], ['艮','和德','青州'],
         ['寅','呂申','燕'], ['卯','高叢','徐州'], ['辰','太陽','鄭'], ['巽','大炅','揚州']],
        sixth_layer, 
        seven_stars
    ]

    for layer_idx, divs in enumerate(num_divisions):
        layer = draw.Group(id=f'layer{layer_idx+1}')
        for div in range(divs):
            start = (360 / divs) * div + rotation_angle
            end   = (360 / divs) * (div + 1) + rotation_angle
            raw = data[layer_idx][div]
            inner = inner_radius + layer_idx * layer_gap
            outer = inner_radius + (layer_idx + 1) * layer_gap

            lid = f"layer{layer_idx + 1}"
            _draw_sector(layer, start, end, inner, outer, raw,
                         is_16_palace=(layer_idx == 3),
                         is_second_layer=(layer_idx == 1),
                         is_third_layer=(layer_idx == 2),
                         layer_id=lid, sector_idx=div,
                         layer_role=_role_for("day", layer_idx),
                         sector_count=divs)
        d.append(layer)

    _add_ornament(d, 3 + 6 * 31.5, jewels=16, sanqi=sanqi, trigram_rotate=trigram_rotate, palace_order=_SIXTEEN)
    return d.as_svg().replace(
        '''<path d="M-1.1238197802477368,-2.781551563700362 L-12.923927472848973,-31.987842982554163 A34.5,34.5,0,0,1,-12.923927472848954,-31.98784298255417 L-1.123819780247735,-2.7815515637003627 A3.0,3.0,0,0,0,-1.1238197802477368,-2.781551563700362 Z" stroke="white" stroke-width="1.8" fill="black" />''', "")


# ====================  gen_chart_hour（支援 rotate_28） ====================
def gen_chart_hour(first_layer, second_layer, skygeneral, sixth_layer,
                   twentyeight, seven_stars, degrees, rotate_28=0, sanqi=None, trigram_rotate=0.0):
    """
    rotate_28: 28宿旋轉角度（度）
               正數 → 逆時針（擰後）
               負數 → 順時針（擰前）
    """
    d = draw.Drawing(500, 500, origin="center")
    inner_radius = 3
    layer_gap = 31.5
    num_divisions = [1, 8, 16, 16, 16, 28, 12]   # 第 3 層 = index 2
    rotation_angle = 248

    data = [
        [first_layer],
        second_layer,
        skygeneral,                           # 第 3 層（可放地支）
        [['巳','大神','楚'], ['午','大威','荊州'], ['未','天道','秦'], ['坤','大武','梁州'],
         ['申','武德','晉'], ['酉','太簇','趙雍'], ['戌','陰主','魯'], ['乾','陰德','冀州'],
         ['亥','大義','衛'], ['子','地主','齊兗'], ['丑','陽德','吳'], ['艮','和德','青州'],
         ['寅','呂申','燕'], ['卯','高叢','徐州'], ['辰','太陽','鄭'], ['巽','大炅','揚州']],
        sixth_layer,
        twentyeight,
        seven_stars
    ]

    cumulative = [0]
    for deg in degrees:
        cumulative.append(cumulative[-1] + deg)

    for layer_idx, divs in enumerate(num_divisions):
        layer = draw.Group(id=f'layer{layer_idx+1}')
        for div in range(divs):
            if layer_idx == 5:   # 28 宿
                start = cumulative[div] + rotation_angle + rotate_28
                end   = cumulative[div + 1] + rotation_angle + rotate_28
            else:
                start = (360 / divs) * div + rotation_angle
                end   = (360 / divs) * (div + 1) + rotation_angle

            raw = data[layer_idx][div]
            inner = inner_radius + layer_idx * layer_gap
            outer = inner_radius + (layer_idx + 1) * layer_gap

            lid = f"layer{layer_idx + 1}"
            _draw_sector(layer, start, end, inner, outer, raw,
                         is_16_palace=(layer_idx == 3),
                         is_second_layer=(layer_idx == 1),
                         is_third_layer=(layer_idx == 2),
                         is_28_layer=(layer_idx == 5),
                         layer_id=lid, sector_idx=div,
                         layer_role=_role_for("hour", layer_idx),
                         sector_count=divs)
        d.append(layer)

    _add_ornament(d, 3 + 7 * 31.5, jewels=16, sanqi=sanqi, trigram_rotate=trigram_rotate, palace_order=_SIXTEEN)
    return d.as_svg().replace(
        '''<path d="M-1.1238197802477368,-2.781551563700362 L-12.923927472848973,-31.987842982554163 A34.5,34.5,0,0,1,-12.923927472848954,-31.98784298255417 L-1.123819780247735,-2.7815515637003627 A3.0,3.0,0,0,0,-1.1238197802477368,-2.781551563700362 Z" stroke="white" stroke-width="1.8" fill="black" />''', "")


# ====================  完整測試範例 ====================
if __name__ == "__main__":
    constellations = [
        '角','亢','氐','房','心','尾','箕','斗','牛','女','虛','危',
        '室','壁','奎','婁','胃','昴','畢','觜','參','井','鬼','柳',
        '星','張','翼','軫'
    ]

    # ---------- 測試 gen_chart_hour（第 3 層放地支） ----------
    svg_hour = gen_chart_hour(
        first_layer="太乙",
        second_layer=['休門','生門','傷門','杜門','景門','死門','驚門','開門'],
        skygeneral=['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥','子','丑','寅','卯'],  # 16 個地支（可自行調整）
        sixth_layer=[['巳','大神','楚']]*16,
        twentyeight=constellations,
        degrees=[360/28]*28,
        rotate_28=-6
    )
    with open("test_hour_third_layer.svg", "w", encoding="utf-8") as f:
        f.write(svg_hour)
    print("已產生 test_hour_third_layer.svg（第 3 層已按地支五行上色）")

    # ---------- 測試 gen_chart_life ----------
    svg_life = gen_chart_life(
        second_layer="中宮",
        twelve=['寅','卯','辰','巳','午','未','申','酉','戌','亥','子','丑'],
        sixth_layer=['休門','生門','傷門','杜門','景門','死門','驚門','開門'] + ['其他']*4
    )
    with open("test_life_third_layer.svg", "w", encoding="utf-8") as f:
        f.write(svg_life)
    print("已產生 test_life_third_layer.svg（第 3 層為地支，已上色）")






