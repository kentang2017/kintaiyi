# -*- coding: utf-8 -*-
import drawsvg as draw
import math

from .config import NINE_GOD_CHART_LABEL

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

# 七曜完整名 → 單字（扇區僅 30°，兩字會重疊）
_PLANET_SHORT = {
    "日　": "日", "日": "日",
    "月　": "月", "月": "月",
    "辰星": "辰",
    "太白": "白",
    "熒惑": "熒",
    "歲星": "歲",
    "填星": "填",
    "月孛": "孛",
    "羅睺": "羅",
    "計都": "計",
}


def _label_parts(raw_label):
    if isinstance(raw_label, list):
        return [str(x).strip() for x in raw_label if str(x).strip()]
    if raw_label is None:
        return []
    s = str(raw_label).strip()
    return [s] if s else []


def _short_planet_label(raw_label):
    """七曜環專用：完整星名轉單字，多星以換行堆疊；空格回傳空字串。"""
    parts = _label_parts(raw_label)
    shorts = []
    for p in parts:
        key = p.replace("\u3000", "").strip()
        if not key or key == " ":
            continue
        shorts.append(_PLANET_SHORT.get(key, key[:1]))
    return "\n".join(shorts)


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


def _door_row_parts(raw_label):
    """八門環列：[宮名, 門名(無門字), 旺衰九星, 貴神簡字, 貴神全名]。"""
    if not isinstance(raw_label, list) or len(raw_label) < 2:
        return None
    gong = str(raw_label[0])
    door = str(raw_label[1]).replace("門", "")
    wx_star = str(raw_label[2]) if len(raw_label) > 2 else ""
    god_short = str(raw_label[3]) if len(raw_label) > 3 else ""
    god_full = str(raw_label[4]) if len(raw_label) > 4 else ""
    if not god_full and god_short:
        for name, short in NINE_GOD_CHART_LABEL.items():
            if short == god_short:
                god_full = name
                break
    return gong, door, wx_star, god_short, god_full


def _sector_meta(raw_label, layer_role=""):
    parts = _label_parts(raw_label)
    label_str = _format_label(raw_label)
    branch = ""
    god = ""
    region = ""
    display = label_str
    if layer_role == "door":
        row = _door_row_parts(raw_label)
        if row:
            gong, door, wx_star, god_short, god_full = row
            branch = gong
            god = god_full or door
            region = wx_star
            door_line = f"{door}{god_short}" if god_short else door
            display = "\n".join(x for x in (gong, door_line, wx_star) if x)
            full_lines = [f"{gong}宮", door_line, wx_star]
            if god_full:
                full_lines.append(f"貴神·{god_full}")
            label_str = "\n".join(x for x in full_lines if x)
        elif isinstance(raw_label, str):
            door = raw_label.replace("門", "")
            display = door
            label_str = door
            god = door
    elif isinstance(raw_label, list) and raw_label:
        branch = raw_label[0] if raw_label[0] in BRANCH_COLORS else _get_branch_key(raw_label)
        if len(raw_label) > 1:
            god = str(raw_label[1])
        if len(raw_label) > 2:
            region = str(raw_label[2])
    else:
        branch = _get_branch_key(raw_label)
        if layer_role == "door":
            god = parts[0] if parts else ""
    if layer_role == "door":
        row = _door_row_parts(raw_label)
        compact = _compact_label(
            [row[1]] if row else parts, "door", branch,
        )
    else:
        compact = _compact_label(parts, layer_role, branch)
    return {
        "branch": branch,
        "god": god,
        "region": region,
        "compact": compact,
        "full": label_str,
        "display": display,
        "role": layer_role,
    }


def _role_for(chart_kind, layer_idx):
    roles = {
        "year": ["center", "door", "palace_template", "palace_content", "star12"],
        "day": ["center", "door", "golden", "palace_template", "palace_content", "star28", "star12"],
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
        row = _door_row_parts(raw_label)
        text = row[1] if row else _format_label(raw_label).replace("門", "")
        key = next((c for c in text if c in GATE_TO_BRANCH), None)
        return GATE_TO_BRANCH.get(key, "")
    return ""


def _draw_sector(group, start, end, inner, outer, raw_label,
                 is_16_palace=False, is_28_layer=False,
                 is_second_layer=False, is_third_layer=False,
                 layer_id="", sector_idx=0, layer_role="",
                 sector_count=0, hide_label=False):
    """共用繪製扇形 + 標籤（支援第 3 層）

    hide_label: 為 True 時不畫文字（例如已有精確七曜標記時，避免雙重重疊）
    """
    # ---- 座標 ----
    sox = outer * math.cos(math.radians(start))
    soy = outer * math.sin(math.radians(start))
    eox = outer * math.cos(math.radians(end))
    eoy = outer * math.sin(math.radians(end))
    six = inner * math.cos(math.radians(start))
    siy = inner * math.sin(math.radians(start))
    eix = inner * math.cos(math.radians(end))
    eiy = inner * math.sin(math.radians(end))

    # ---- 顏色邏輯（優先順序：中心透明 > 第 2 層 > 第 3 層 > 16宮 > 28宿）----
    fill = 'black'   # 預設
    if layer_role == "center":              # 中心圓 → 透明（由 _add_ornament 背景圓負責填色）
        fill = 'none'
    elif is_second_layer:                   # 八門 → 五行
        row = _door_row_parts(raw_label)
        text = row[1] if row else _format_label(raw_label).replace("門", "")
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

    # 七曜環只顯示單字，避免兩字星名在 30° 扇區重疊。
    # 若已有精確黃道標記（hide_label=True），扇區完全不畫字，避免雙重重疊。
    if hide_label:
        label_str = ""
        compact_str = meta["compact"]
    elif layer_role == "star12":
        label_str = _short_planet_label(raw_label)
        compact_str = label_str.replace("\n", "")
    elif layer_role == "door":
        label_str = meta["display"]
        compact_str = meta["compact"]
    else:
        label_str = meta["full"]
        compact_str = meta["compact"]

    sector_g = draw.Group(id=f"{layer_id}-s{sector_idx}" if layer_id else None)
    sector_g.args["class"] = "taiyi-sector"
    if layer_id:
        sector_g.args["data-layer"] = layer_id
        sector_g.args["data-sector"] = str(sector_idx)
        sector_g.args["data-role"] = layer_role or ""
        sector_g.args["data-compact"] = compact_str
        sector_g.args["data-full"] = meta["full"]
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
    # 密集層（28宿等）自動縮小標籤；空字串不畫 Text，減少 SVG 節點
    if label_str:
        _label_size = 6.5 if (is_28_layer or sector_count >= 28) else (8.5 if sector_count <= 8 else 7.5)
        t = draw.Text(label_str, _label_size, tx, ty, center=1, fill=text_fill,
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
    "太陰黑旗": "#1e2438",
    "害氣赤旗": "#c43a2b",
}
_SANQI_FLAG_STROKE = "#e9cc88"
_SANQI_BLACK_STROKE = "#d7bd6f"
_SANQI_FLAG_CLASS = "taiyi-sanqi-flag"
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


def _draw_flag(d, ang_deg, r_inner, r_outer, color, tang=0.0, flag_name=""):
    """繪一面旗：徑向旗桿 + 三角旗旆（tang 為切向偏移以避重疊）。"""
    import math as _m
    a = _m.radians(ang_deg)
    ca, sa = _m.cos(a), _m.sin(a)
    ta, tca = -sa, ca
    bx, by = r_inner * ca + tang * ta, r_inner * sa + tang * tca
    ex, ey = r_outer * ca + tang * ta, r_outer * sa + tang * tca
    is_black = flag_name == "太陰黑旗"
    banner_stroke = _SANQI_BLACK_STROKE if is_black else _SANQI_FLAG_STROKE
    banner_stroke_w = 1.6 if is_black else 1.1
    pole_stroke_w = 1.5 if is_black else 1.4
    kind_class = " taiyi-sanqi-flag-black" if is_black else ""
    pole = draw.Line(bx, by, ex, ey, stroke=banner_stroke, stroke_width=pole_stroke_w)
    pole.args["class"] = f"{_SANQI_FLAG_CLASS} taiyi-sanqi-flag-pole{kind_class}"
    d.append(pole)
    ph = max(4.0, (r_outer - r_inner) * 0.7)
    W = max(3.5, (r_outer - r_inner) * 0.55)
    r_top, r_bot = r_outer, r_outer - ph
    p1x, p1y = r_top * ca + tang * ta, r_top * sa + tang * tca
    p2x, p2y = r_bot * ca + tang * ta, r_bot * sa + tang * tca
    mr = (r_top + r_bot) / 2.0
    mx, my = mr * ca + tang * ta, mr * sa + tang * tca
    tipx, tipy = mx + W * ta, my + W * tca
    banner = draw.Lines(
        p1x, p1y, p2x, p2y, tipx, tipy,
        close=True, fill=color, stroke=banner_stroke, stroke_width=banner_stroke_w,
    )
    banner.args["class"] = f"{_SANQI_FLAG_CLASS} taiyi-sanqi-flag-banner{kind_class}"
    d.append(banner)


def ornament_outer_radius(outer_r: float, view_half: float = 250.0) -> float:
    """外緣單線金環半徑（與 _add_ornament 一致，供 overlay 標記定位）。"""
    band = max(view_half - outer_r, 1.0)
    return outer_r + max(3.5, band * 0.45)


def _add_ornament(d, outer_r, jewels=16, sanqi=None, trigram_rotate=0.0, palace_order=None):
    """古典美學裝飾層（純附加，不改動宮位座標與 viewBox）。

    1. 玄色古典底盤（深靛墨）襯托全局，最外環不再露白，白／米色文字清晰可見；
    2. 外緣單線金環；
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
    bg = draw.Circle(0, 0, half, fill="#141826", stroke="none")
    bg.args["class"] = "taiyi-chart-bg"
    d.insert(0, bg)
    # —— 2. 外緣單線金環 ——
    r_outer = ornament_outer_radius(outer_r, half)
    ring = draw.Circle(0, 0, r_outer, stroke="#c79a4e", stroke_width=0.9, fill="none")
    ring.args["class"] = "taiyi-ornament-ring"
    d.append(ring)
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
            _draw_flag(
                d, ang, r_in, r_out, _SANQI_COLORS[name],
                tang=tang_map.get(k, 0.0), flag_name=name,
            )
    # —— 4. 八卦天盤活盤 ——
    if band >= 26:
        tr = r_outer + (half - r_outer) * 0.55
        for i in range(8):
            ang = _m.radians(_ROTATION_ANGLE + (360.0 / 16) * (2 * i + 0.5) + trigram_rotate)
            d.append(draw.Text(_EIGHT_PALACE_TRIGRAMS[i], 12, tr * _m.cos(ang), tr * _m.sin(ang),
                                center=1, fill="#e9cc88", font_family="serif",
                                font_weight="bold"))

# ====================  gen_chart  ====================
def gen_chart(first_layer, second_layer, sixth_layer, sevenstars, sanqi=None, trigram_rotate=0.0):
    d = draw.Drawing(660, 660, origin="center")
    inner_radius = 16
    layer_gap = 55
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
        if layer_idx == 0:
            continue   # 跳過中心層的 sector，避免 degenerate arc 產生白線
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

    _add_ornament(d, 16 + 5 * 55, jewels=16, sanqi=sanqi, trigram_rotate=trigram_rotate, palace_order=_SIXTEEN)
    return d.as_svg()



# ====================  gen_chart_life  ====================
def gen_chart_life(
    second_layer,
    twelve,
    sixth_layer,
    sevenstars,
    sanqi=None,
    trigram_rotate=0.0,
    *,
    center_lines=None,
    branch_tags=None,
):
    d = draw.Drawing(560, 560, origin="center")
    inner_radius = 15
    layer_gap = 42
    num_divisions = [1, 12, 12, 12, 12]          # 第 3 層 = index 2
    rotation_angle = 248
    branch_tags = branch_tags or {}
    branches = ['巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑', '寅', '卯', '辰']

    data = [
        [second_layer],
        twelve,
        branches,
        sixth_layer,
        sevenstars,
    ]

    for layer_idx, divs in enumerate(num_divisions):
        if layer_idx == 0:
            continue   # 跳過中心層的 sector，避免 degenerate arc 產生白線
        layer = draw.Group(id=f'layer{layer_idx + 1}')
        if layer_idx == 0:
            continue   # 跳過中心層的 sector，避免 degenerate arc 產生白線
        for div in range(divs):
            start = (360 / divs) * div + rotation_angle
            end   = (360 / divs) * (div + 1) + rotation_angle
            raw = data[layer_idx][div]
            inner = inner_radius + layer_idx * layer_gap
            outer = inner_radius + (layer_idx + 1) * layer_gap
            lid = f"layer{layer_idx + 1}"

            if layer_idx == 0 and center_lines:
                center_g = draw.Group(id=f"{lid}-s{div}")
                center_g.args["class"] = "taiyi-sector"
                center_g.args["data-layer"] = lid
                center_g.args["data-sector"] = str(div)
                center_g.args["data-role"] = "center"
                center_g.args["data-tooltip-key"] = f"{lid}:{div}"
                center_g.append(draw.Circle(0, 0, inner_radius, fill="#141826", stroke="#c79a4e", stroke_width=1))
                center_g.append(
                    draw.Text(
                        "\n".join(center_lines),
                        8,
                        0,
                        0,
                        center=1,
                        fill="#e9cc88",
                        font_family="serif",
                        font_weight="bold",
                    )
                )
                layer.append(center_g)
                continue

            if layer_idx == 2 and branch_tags:
                br = branches[div]
                tag = branch_tags.get(br, "")
                if tag:
                    raw = f"{br}\n{tag}"

            _draw_sector(layer, start, end, inner, outer, raw,
                         is_16_palace=(layer_idx == 2),
                         is_second_layer=(layer_idx == 1),
                         is_third_layer=(layer_idx == 2),
                         layer_id=lid, sector_idx=div,
                         layer_role=_role_for("life", layer_idx),
                         sector_count=divs)
        d.append(layer)

    _add_ornament(d, 15 + 5 * 42, jewels=12, sanqi=sanqi, trigram_rotate=trigram_rotate, palace_order=_TWELVE)
    return d.as_svg()



# 天文二十八宿順序（黃道經度 → 入宿查表用，與太乙盤面排列無關）
_XIU_SEQ = list("角亢氐房心尾箕斗牛女虛危室壁奎婁胃昴畢觜參井鬼柳星張翼軫")
# 入宿校準常數（唯一設定點；kintaiyi 透過 chart.XIU_OFFSET 引用）
# 元祐元年月犯氐／畢折中，可再微調 110～120
XIU_OFFSET = 112.0


def _lon_to_xiu(lon, offset, width_by_name):
    """黃道經度 → (宿名, 宿內比例 0~1)。width_by_name: {宿名: 度數}"""
    adj = (float(lon) - float(offset)) % 360.0
    cum = 0.0
    for name in _XIU_SEQ:
        w = float(width_by_name.get(name, 360.0 / 28.0))
        if cum <= adj < cum + w:
            frac = (adj - cum) / w if w > 0 else 0.5
            return name, max(0.0, min(1.0, frac))
        cum += w
    # 浮點邊界：落在最後一宿
    last = _XIU_SEQ[-1]
    return last, 1.0


# 二十八宿 → 十二次（與 kintaiyi 一致，對齊七政四餘）
_XIU_TO_BRANCH_CHART = {
    "角": "辰", "亢": "辰", "氐": "卯", "房": "卯", "心": "卯",
    "尾": "寅", "箕": "寅", "斗": "丑", "牛": "丑",
    "女": "子", "虛": "子", "危": "子", "室": "亥", "壁": "亥",
    "奎": "戌", "婁": "戌", "胃": "酉", "昴": "酉", "畢": "酉",
    "觜": "申", "參": "申", "井": "未", "鬼": "未",
    "柳": "午", "星": "午", "張": "午", "翼": "巳", "軫": "巳",
}
_XIU_SEQ_CHART = list("角亢氐房心尾箕斗牛女虛危室壁奎婁胃昴畢觜參井鬼柳星張翼軫")


def _draw_planet_markers(d, planet_angles, inner, outer, rotation_angle=248, **_kwargs):
    """在七曜環上繪製行星單字標記，同宿／同角時自動散開避免重疊。

    優先使用廿八宿座標系（xiu_order + xiu_degrees + rotate_28），
    使標記落在實際宿扇區內；若無則回退十二次地支 30° 扇區。
    多星同角時：徑向 + 小幅角度雙重散開，確保可辨識。
    """
    from collections import defaultdict

    mid_r = (inner + outer) / 2.0
    ring_half = max(4.0, (outer - inner) / 2.0 - 2.0)
    BRANCH_ORDER_12 = ["午", "未", "申", "酉", "戌", "亥", "子", "丑", "寅", "卯", "辰", "巳"]
    offset = float(_kwargs.get("offset", XIU_OFFSET))
    rotate_28 = float(_kwargs.get("rotate_28", 0.0))
    xiu_order = _kwargs.get("xiu_order")  # 盤面廿八宿順序（已 rearrange）
    xiu_degrees = _kwargs.get("xiu_degrees")  # 與 xiu_order 同序的度數

    # 宿名 → 度數（黃道經度入宿查表必須用天文順序）
    if xiu_order and xiu_degrees and len(xiu_order) == 28 and len(xiu_degrees) == 28:
        width_by_name = {str(n): float(w) for n, w in zip(xiu_order, xiu_degrees)}
    else:
        width_by_name = {n: 360.0 / 28.0 for n in _XIU_SEQ_CHART}
        xiu_order = None
        xiu_degrees = None

    # 盤面累積角度（僅在有 xiu_order 時）
    chart_cum = None
    if xiu_order is not None:
        chart_cum = [0.0]
        for w in xiu_degrees:
            chart_cum.append(chart_cum[-1] + float(w))

    # 1) 先算出每顆星的基準角度與宿
    placed = []  # (label, base_angle, xiu, branch)
    for label, lon in planet_angles:
        lon = float(lon) % 360.0
        xiu, frac = _lon_to_xiu(lon, offset, width_by_name)
        branch = _XIU_TO_BRANCH_CHART.get(xiu, "午")

        if chart_cum is not None and xiu in xiu_order:
            idx = xiu_order.index(xiu)
            # 落在該宿扇區內（用 frac，避免整宿中點全擠在一起）
            base_angle = (
                rotation_angle + rotate_28 + chart_cum[idx]
                + float(xiu_degrees[idx]) * max(0.15, min(0.85, frac))
            ) % 360.0
        else:
            ring_idx = BRANCH_ORDER_12.index(branch) if branch in BRANCH_ORDER_12 else 0
            base_angle = (rotation_angle + ring_idx * 30 + 15) % 360.0

        placed.append((str(label), base_angle, xiu, branch))

    # 2) 按角度分組（±2° 視為同位置）
    groups = defaultdict(list)
    for item in placed:
        key = round(item[1] / 2.0) * 2.0  # 2° 量化
        groups[key].append(item)

    # 3) 同組散開後繪製
    for _key, group in groups.items():
        n = len(group)
        ang_step = 0.0 if n <= 1 else min(5.5, 16.0 / n)   # 角度散開
        r_step = 0.0 if n <= 1 else min(6.5, ring_half * 0.9)  # 徑向散開

        for i, (label, base_angle, xiu, branch) in enumerate(group):
            offset_i = i - (n - 1) / 2.0
            ang = (base_angle + offset_i * ang_step) % 360.0
            r = mid_r + offset_i * r_step
            fsize = 8 if n <= 2 else (7 if n <= 4 else 6)

            rad = math.radians(ang)
            tx = r * math.cos(rad)
            ty = r * math.sin(rad)
            t = draw.Text(
                label, fsize, tx, ty, center=1, fill="#e8c44d",
                font_family="sans-serif", font_weight="bold",
            )
            t.args["class"] = "taiyi-planet-marker"
            t.args["data-branch"] = branch
            t.args["data-xiu"] = xiu
            d.append(t)


# ====================  gen_chart_day  ====================
def gen_chart_day(first_layer, second_layer, golden, sixth_layer, twentyeight, seven_stars,
                  degrees=None, rotate_28=0, sanqi=None, trigram_rotate=0.0, planet_angles=None):
    """
    rotate_28: 28宿旋轉角度（度）
               正數 → 逆時針（擰後）
               負數 → 順時針（擰前）
    """
    d = draw.Drawing(660, 660, origin="center")
    inner_radius = 5
    layer_gap = 38
    num_divisions = [1, 8, 8, 16, 16, 28, 12]      # 第 3 層 = index 2
    rotation_angle = 248
    degrees = degrees or [360 / 28] * 28

    data = [
        [first_layer],
        second_layer,
        golden,                               # 第 3 層（可放地支或文字）
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
        if layer_idx == 0:
            continue   # 跳過中心層的 sector，避免 degenerate arc 產生白線
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
            role = _role_for("day", layer_idx)
            # 已有精確黃道標記時，七曜扇區不再畫字，避免與 marker 雙重重疊
            _hide = bool(planet_angles) and role == "star12"
            _draw_sector(layer, start, end, inner, outer, raw,
                         is_16_palace=(layer_idx == 3),
                         is_second_layer=(layer_idx == 1),
                         is_third_layer=(layer_idx == 2),
                         is_28_layer=(layer_idx == 5),
                         layer_id=lid, sector_idx=div,
                         layer_role=role,
                         sector_count=divs,
                         hide_label=_hide)
        d.append(layer)

    _add_ornament(d, 5 + 7 * 38, jewels=16, sanqi=sanqi, trigram_rotate=trigram_rotate, palace_order=_SIXTEEN)
    if planet_angles:
        # 與廿八宿環共用座標系，使七曜標記落在對應宿扇區上
        _draw_planet_markers(
            d, planet_angles, 5 + 6 * 38, 5 + 7 * 38,
            xiu_order=twentyeight, xiu_degrees=degrees,
            rotate_28=rotate_28, offset=XIU_OFFSET,
        )
    return d.as_svg()



# ====================  gen_chart_hour（支援 rotate_28） ====================
def gen_chart_hour(first_layer, second_layer, skygeneral, sixth_layer,
                   twentyeight, seven_stars, degrees, rotate_28=0, sanqi=None, trigram_rotate=0.0, planet_angles=None):
    """
    rotate_28: 28宿旋轉角度（度）
               正數 → 逆時針（擰後）
               負數 → 順時針（擰前）
    """
    d = draw.Drawing(720, 720, origin="center")
    inner_radius = 5
    layer_gap = 38
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
        if layer_idx == 0:
            continue   # 跳過中心層的 sector，避免 degenerate arc 產生白線
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
            role = _role_for("hour", layer_idx)
            _hide = bool(planet_angles) and role == "star12"
            _draw_sector(layer, start, end, inner, outer, raw,
                         is_16_palace=(layer_idx == 3),
                         is_second_layer=(layer_idx == 1),
                         is_third_layer=(layer_idx == 2),
                         is_28_layer=(layer_idx == 5),
                         layer_id=lid, sector_idx=div,
                         layer_role=role,
                         sector_count=divs,
                         hide_label=_hide)
        d.append(layer)

    _add_ornament(d, 5 + 7 * 38, jewels=16, sanqi=sanqi, trigram_rotate=trigram_rotate, palace_order=_SIXTEEN)
    if planet_angles:
        _draw_planet_markers(
            d, planet_angles, 5 + 6 * 38, 5 + 7 * 38,
            xiu_order=twentyeight, xiu_degrees=degrees,
            rotate_28=rotate_28, offset=XIU_OFFSET,
        )
    return d.as_svg()


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



