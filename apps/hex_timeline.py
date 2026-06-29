"""流日卦時間軸 HTML 組件。

橫向卡片推移，顯示當日及未來日子的日卦，動爻著色。
在排盤之下、解釋展開區之上。
"""

from __future__ import annotations

import re
from datetime import date, timedelta
from html import escape as _esc

from kintaiyi import config
from kintaiyi.guiyun_display import chong_gua_row, inner_outer_rows, limit_rows
from kintaiyi.junshi_display import (
    wuzhen_bazhen_svg,
    wuzhen_reference_rows,
    wuzhen_table_rows,
)
from kintaiyi.game_theory import TaiyiGame, 主方策略列 as _gt_主方策略列, 客方策略列 as _gt_客方策略列

# ── 負數年份（公元前）日期支援 ─────────────────────────────
import sxtwl as _sxtwl


def _html_table(rows: list[dict], *, headers: list[str] | None = None) -> str:
    """從 dict list 生成 HTML 表格。"""
    if not rows:
        return ""
    keys = headers or list(rows[0].keys())
    def _cell(v: str) -> str:
        s = str(v) if v is not None else "—"
        return _esc(s)
    head = "".join(f"<th>{_esc(k)}</th>" for k in keys)
    body = ""
    for r in rows:
        body += "<tr>" + "".join(f"<td>{_cell(r.get(k, ''))}</td>" for k in keys) + "</tr>"
    return f'<table class="classic-grid-table"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


class _SafeDate:
    """輕量 date 替代品，支援負數年份。內部使用 sxtwl JD 運算。"""
    __slots__ = ("_year", "_month", "_day")

    def __init__(self, year: int, month: int, day: int):
        self._year = year
        self._month = month
        self._day = day

    @classmethod
    def _from_jd(cls, jd: float) -> "_SafeDate":
        t = _sxtwl.JD2DD(jd)
        return cls(int(t.Y), int(t.M), int(t.D))

    @property
    def year(self) -> int:
        return self._year

    @property
    def month(self) -> int:
        return self._month

    @property
    def day(self) -> int:
        return self._day

    def weekday(self) -> int:
        # 0=Monday ... 6=Sunday  (same as datetime.date.weekday)
        jd = _sxtwl.toJD(_sxtwl.Time(self._year, self._month, self._day, 12, 0, 0))
        # JD 0 = Monday (Julian Day week cycle: JD mod 7 -> 0=Monday)
        return int(jd + 0.5) % 7

    def __add__(self, other: timedelta) -> "_SafeDate":
        jd = _sxtwl.toJD(_sxtwl.Time(self._year, self._month, self._day, 12, 0, 0))
        return self._from_jd(jd + other.days)

    def __radd__(self, other: timedelta) -> "_SafeDate":
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, timedelta):
            jd = _sxtwl.toJD(_sxtwl.Time(self._year, self._month, self._day, 12, 0, 0))
            return self._from_jd(jd - other.days)
        if isinstance(other, _SafeDate):
            jd1 = _sxtwl.toJD(_sxtwl.Time(self._year, self._month, self._day, 12, 0, 0))
            jd2 = _sxtwl.toJD(_sxtwl.Time(other._year, other._month, other._day, 12, 0, 0))
            return timedelta(days=int(round(jd1 - jd2)))
        if isinstance(other, date):
            jd1 = _sxtwl.toJD(_sxtwl.Time(self._year, self._month, self._day, 12, 0, 0))
            jd2 = _sxtwl.toJD(_sxtwl.Time(other.year, other.month, other.day, 12, 0, 0))
            return timedelta(days=int(round(jd1 - jd2)))
        return NotImplemented

    def __eq__(self, other) -> bool:
        if isinstance(other, _SafeDate):
            return self._year == other._year and self._month == other._month and self._day == other._day
        if isinstance(other, date):
            return self._year == other.year and self._month == other.month and self._day == other.day
        return False

    def __hash__(self) -> int:
        return hash((self._year, self._month, self._day))


def _safe_date(year: int, month: int, day: int):
    """構建 date 物件，支援負數年份。year >= 1 時回傳標準 datetime.date。"""
    if year >= 1:
        return date(year, month, day)
    return _SafeDate(year, month, day)

# ── 爻位吉凶 ────────────────────────────────────────────

_JI_COLOR: dict[int, str] = {
    1: "var(--yun-ji-fu)",
    2: "var(--yun-ji-ji)",
    3: "var(--yun-ji-xiong)",
    4: "var(--yun-ji-xiong)",
    5: "var(--yun-ji-zai)",
    6: "var(--yun-ji-zai)",
}

_YAO_NAMES_YANG = ("初九", "九二", "九三", "九四", "九五", "上九")
_YAO_NAMES_YIN = ("初六", "六二", "六三", "六四", "六五", "上六")


# ── 輔助函數 ────────────────────────────────────────────

def _parse_gua_str(gua_str: str) -> tuple[str, str]:
    """解析 '既濟䷾' → ('既濟', '䷾')。"""
    if not gua_str:
        return ("", "")
    m = re.search(r"([\u4dc0-\u4dff])", gua_str)
    if m:
        symbol = m.group(1)
        name = gua_str.replace(symbol, "").strip()
    else:
        symbol = ""
        name = gua_str.strip()
    return (name, symbol)


def _gua_line_bits(gua_name: str) -> list[bool]:
    """取卦六爻陰陽（下初至上），True=陽爻。"""
    return config._gua_line_bits(gua_name)


def _get_yao_name(gua_name: str, yao_idx: int) -> str:
    """取得指定爻的名稱。"""
    bits = _gua_line_bits(gua_name)
    i = yao_idx - 1
    if i < 0 or i > 5:
        return ""
    return (_YAO_NAMES_YANG if bits[i] else _YAO_NAMES_YIN)[i]


def _compute_gua(year: int, month: int, day: int, hour: int, minute: int,
                 scale: str) -> tuple[str, str, int]:
    """計算指定時間尺度的卦。

    scale: 'year' | 'month' | 'day' | 'hour' | 'minute'
    Returns (gua_name, gua_symbol, gua_num)
    """
    from kintaiyi.kintaiyi import Taiyi
    ty = Taiyi(year, month, day, hour, minute)
    method = {
        "year": ty.year_gua,
        "month": ty.month_gua,
        "day": ty.day_gua,
        "hour": ty.hour_gua,
        "minute": ty.minute_gua,
    }[scale]
    num, gua_str = method()
    name, symbol = _parse_gua_str(gua_str or "")
    return (name, symbol, num)


def _compute_yao(year: int, month: int, day: int, hour: int, minute: int,
                scale: str) -> int:
    """計算指定時間尺度的動爻（直事爻）。

    每個尺度依其對應干支在六十甲子中的序數 % 6 + 1。
    """
    from kintaiyi.kintaiyi import Taiyi
    ty = Taiyi(year, month, day, hour, minute)
    gz_idx = {"year": 0, "month": 1, "day": 2, "hour": 3, "minute": 4}[scale]
    gz = ty._get_gangzhi()
    gz_str = gz[gz_idx] if len(gz) > gz_idx else ""
    gz_num = dict(zip(config.jiazi(), range(1, 61))).get(gz_str, 1)
    return ((gz_num - 1) % 6) + 1


# ── 向後相容（舊 API）──
def _compute_day_gua(year: int, month: int, day: int) -> tuple[str, str, int]:
    return _compute_gua(year, month, day, 12, 0, "day")

def _compute_day_yao(year: int, month: int, day: int) -> int:
    return _compute_yao(year, month, day, 12, 0, "day")


def _get_gua_xiang(gua_name: str) -> dict | None:
    """取得卦象全文（象曰、總述）。"""
    from kintaiyi.gua_xiang import tongyun_gua_xiang
    return tongyun_gua_xiang(gua_name)


# ── 主入口 ────────────────────────────────────────────

def _generate_time_steps(ty, scale: str) -> list[dict]:
    """根據計式尺度生成時間步階列表。

    每個元素是 {year, month, day, hour, minute, label, sub_label}。
    """
    import datetime as _dt

    y, mo, d, h, mi = ty.year, ty.month, ty.day, ty.hour, ty.minute
    steps = []

    if scale == "year":
        for i in range(12):
            ny = y + i
            try:
                nd = _dt.date(ny, mo, d)
            except ValueError:
                # 處理 2/29 等 — 取該月最後一天
                if mo == 2 and d == 29:
                    nd = _dt.date(ny, 2, 28)
                else:
                    nd = _dt.date(ny, mo, 1)
            steps.append({
                "year": ny, "month": mo, "day": nd.day,
                "hour": h, "minute": mi,
                "label": str(ny), "sub_label": "",
            })

    elif scale == "month":
        cur_y, cur_m = y, mo
        for i in range(12):
            ny, nm = cur_y, cur_m
            # 推進 i 個月
            total = (cur_y * 12 + (cur_m - 1)) + i
            ny, nm = total // 12, (total % 12) + 1
            try:
                nd = _dt.date(ny, nm, min(d, 28))
            except ValueError:
                nd = _dt.date(ny, nm, 1)
            steps.append({
                "year": ny, "month": nm, "day": nd.day,
                "hour": h, "minute": mi,
                "label": f"{ny}/{nm}", "sub_label": "",
            })

    elif scale == "day":
        base = _safe_date(y, mo, d)
        for i in range(15):
            d2 = base + timedelta(days=i)
            wk_labels = ("一", "二", "三", "四", "五", "六", "日")
            steps.append({
                "year": d2.year, "month": d2.month, "day": d2.day,
                "hour": h, "minute": mi,
                "label": f"{d2.month}/{d2.day}",
                "sub_label": wk_labels[d2.weekday()],
            })

    elif scale == "hour":
        for i in range(12):
            # 用 datetime 算出未來小時
            base_dt = _dt.datetime(y, mo, d, h, mi)
            fut = base_dt + _dt.timedelta(hours=i)
            zhi_labels = ("子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥")
            zhi_idx = (fut.hour + 1) % 12  # 23時→子, 1時→丑...
            steps.append({
                "year": fut.year, "month": fut.month, "day": fut.day,
                "hour": fut.hour, "minute": mi,
                "label": f"{fut.hour:02d}:00",
                "sub_label": zhi_labels[zhi_idx] + "時",
            })

    elif scale == "minute":
        for i in range(10):
            base_dt = _dt.datetime(y, mo, d, h, mi)
            fut = base_dt + _dt.timedelta(minutes=i)
            steps.append({
                "year": fut.year, "month": fut.month, "day": fut.day,
                "hour": fut.hour, "minute": fut.minute,
                "label": f"{fut.hour:02d}:{fut.minute:02d}",
                "sub_label": "",
            })

    return steps


# ── 計式 → 尺度對應 ──
_STYLE_SCALE = {
    0: "year",    # 年計太乙
    1: "month",   # 月計太乙
    2: "day",     # 日計太乙
    3: "hour",    # 時計太乙
    4: "minute",  # 分計太乙
}

_SCALE_LAYER = {
    "year": "year",
    "month": "month",
    "day": "day",
    "hour": "hour",
    "minute": "minute",
}


def render_hex_timeline(results: dict, *, t) -> str:
    """渲染流卦時間軸（橫向卡片推移），依太乙計式決定尺度。

    時計太乙 → 流時卦（未來12小時，每1小時）
    分計太乙 → 流分卦（未來10分鐘，每1分鐘）
    日計太乙 → 流日卦（未來15日，每1日）
    月計太乙 → 流月卦（未來12月，每1月）
    年計太乙 → 流年卦（未來12年，每1年）
    """
    import streamlit as st

    ty = results.get("ty")
    if ty is None:
        return ""

    style = results.get("style", 3)
    scale = _STYLE_SCALE.get(style, "day")

    # 太乙命法不顯示流卦時間軸
    if style in (5, 6):
        return ""

    steps = _generate_time_steps(ty, scale)
    num = len(steps)

    # 初始化選中
    sel_key = "liuri_selected_offset"
    if st.session_state.get(sel_key) is None:
        st.session_state[sel_key] = 0

    # 讀取 query param 更新選中
    qp = st.query_params
    if "liuri_offset" in qp:
        try:
            new_offset = int(qp["liuri_offset"])
            if 0 <= new_offset < num:
                st.session_state[sel_key] = new_offset
        except (ValueError, TypeError):
            pass
        del st.query_params["liuri_offset"]

    # ── i18n key 對應 ──
    label_key = {
        "year": "liunian_label",
        "month": "liuyue_label",
        "day": "liuri_label",
        "hour": "liushi_label",
        "minute": "liufen_label",
    }[scale]
    hex_label_key = {
        "year": "year_hex",
        "month": "month_hex",
        "day": "day_hex",
        "hour": "hour_hex",
        "minute": "minute_hex",
    }[scale]

    # ── 時間軸卡片帶 ──
    cards_html: list[str] = []
    for i, step in enumerate(steps):
        gua_name, gua_symbol, _ = _compute_gua(
            step["year"], step["month"], step["day"],
            step["hour"], step["minute"], scale,
        )
        if not gua_name:
            continue
        yao_idx = _compute_yao(
            step["year"], step["month"], step["day"],
            step["hour"], step["minute"], scale,
        )
        yao_name = _get_yao_name(gua_name, yao_idx)
        is_selected = (i == st.session_state[sel_key])

        cls = "liuri-card"
        if is_selected:
            cls += " liuri-selected"

        bits = _gua_line_bits(gua_name)
        lines_html = _render_mini_lines(bits, yao_idx, is_selected)

        date_str = step["label"]
        sub_label = step.get("sub_label", "")
        ji_color = _JI_COLOR.get(yao_idx, "var(--text-muted)")
        aria_label = f"{date_str} {sub_label} {_esc(gua_name)} {_esc(yao_name)}".strip()

        sub_html = f'<span class="liuri-weekday">{_esc(sub_label)}</span>' if sub_label else ""

        cards_html.append(
            f'<a class="liuri-card-link" href="?liuri_offset={i}" '
            f'aria-label="{aria_label}">'
            f'<div class="{cls}" data-offset="{i}">'
            f'<span class="liuri-date">{date_str}</span>'
            f'{sub_html}'
            f'<span class="liuri-symbol">{_esc(gua_symbol)}</span>'
            f'<span class="liuri-name">{_esc(gua_name)}</span>'
            f'{lines_html}'
            f'<span class="liuri-yao" style="color: {ji_color};">{_esc(yao_name)}</span>'
            f"</div></a>"
        )

    inner = "".join(cards_html)

    # ── 詳細解讀卡片 ──
    sel_offset = min(st.session_state[sel_key], num - 1)
    sel_step = steps[sel_offset]
    sel_name, sel_symbol, _ = _compute_gua(
        sel_step["year"], sel_step["month"], sel_step["day"],
        sel_step["hour"], sel_step["minute"], scale,
    )
    sel_yao = _compute_yao(
        sel_step["year"], sel_step["month"], sel_step["day"],
        sel_step["hour"], sel_step["minute"], scale,
    )
    detail_html = render_hex_detail_card(
        sel_name, sel_symbol, _SCALE_LAYER[scale],
        t(hex_label_key), sel_yao, t=t,
    )

    section_html = f"""
<section class="liuri-section">
  <div class="liuri-header">
    <span class="liuri-label">{_esc(t(label_key))}</span>
    <span class="liuri-scroll-hint">{_esc(t("liuri_scroll_hint"))}</span>
  </div>
  <div class="liuri-track">
    {inner}
  </div>
  {detail_html}
</section>"""

    # ── 日期選擇按鈕已移除 ──
    # 改為直接點擊上方 HTML 卡片切換日期，
    # 不再生成 15 個白色 st.button。

    return section_html


def render_hex_detail_card(
    gua_name: str,
    gua_symbol: str,
    layer_key: str,
    layer_label: str,
    yao_idx: int = 0,
    *,
    t,
) -> str:
    """渲染單個卦象的詳細解讀卡片（左上角卦符 + 卦象總述）。"""
    if not gua_name:
        return ""

    hex_color_var = f"--hex-{layer_key}"
    xiang = _get_gua_xiang(gua_name)

    yao_name = _get_yao_name(gua_name, yao_idx) if yao_idx else ""
    ji_color = _JI_COLOR.get(yao_idx, "var(--text-muted)")

    # 卦象總述（折疊）— 合併象曰與總述，避免重複顯示
    zongshu_html = ""
    if xiang and xiang.get("總述"):
        zongshu_html = (
            f'<details class="hex-detail-zongshu">'
            f'<summary>{_esc(t("hex_zongshu"))}</summary>'
            f'<p>{_esc(xiang["總述"])}</p>'
            f"</details>"
        )

    # 動爻辭（折疊）— 顯示選中爻的觀象全文
    yao_ci_html = ""
    if xiang and yao_idx and xiang.get("爻觀象"):
        yao_text = xiang["爻觀象"].get(yao_idx, "")
        if yao_text:
            yao_ci_html = (
                f'<details class="hex-detail-zongshu" open>'
                f'<summary>{_esc(t("hex_yao_ci"))} · {_esc(yao_name)}</summary>'
                f'<p>{_esc(yao_text)}</p>'
                f"</details>"
            )

    # 動爻標示
    yao_html = ""
    if yao_name:
        yao_html = (
            f'<span class="hex-detail-yao" style="color: {ji_color};">'
            f'{_esc(yao_name)} · {_esc(layer_label)}'
            f"</span>"
        )

    return f"""
<article class="hex-detail-card" style="--hex-color: var({hex_color_var});">
  <div class="hex-detail-header">
    <span class="hex-detail-symbol">{_esc(gua_symbol)}</span>
    <div class="hex-detail-title">
      <span class="hex-detail-name">{_esc(gua_name)}</span>
      {yao_html}
    </div>
  </div>
  <div class="hex-detail-body">
    {yao_ci_html}
    {zongshu_html}
  </div>
</article>"""


def render_classic_reading(results: dict, *, t) -> str:
    """渲染古典解讀卡片群 — 全部整合（含大小遊軌運、軍事戰略、運籌博弈分析），無重複。

    Returns:
      - html: classic-card HTML string（包含所有解釋內容）

    卡片分類：
      1. 太乙秘書 — 古典斷語
      2. 盤局分析 — 主客算、三門五將、勝負推論
      3. 史事記載 — 歷史驗例
      4. 格局釋義 — 卷四釋格局
      5. 神將所主 — 卷二/七 天目、九宮、八門、天乙地乙等
      6. 星曜分佈 — 卷六 太乙九星、文昌九星、卷十 九宮貴神、十六宮
      7. 軍事戰略 — 卷五 + 卷十五 + 卷十七 + 五陣八陣圖（合併）
      8. 災變分野 — 卷十一 飛符四殺 + 卷八 分野疆界（合併）
      9. 運氣音律 — 卷三 五運六氣 + 五音之數 + 卷十 天目合會 + 卷十八 十精雲氣（合併）
     10. 行限推論 — 陽九百六
     11. 大小遊軌運 — 卷九 軌運入卦、重卦策數、限數
     12. 運籌博弈分析 — Nash 均衡 + 線性規劃
    """
    parts: list[str] = []
    ttext = results.get("ttext") or {}

    # ── 1. 太乙秘書 ──
    ts = results.get("ts") or ""
    if ts:
        parts.append(_classic_card(t("taiyi_mishu"), "", ts, open_by_default=False))

    # ── 2. 盤局分析 ──
    analysis_parts = []
    analysis_parts.append(f"{t('year_star_predict')}{results.get('year_predict', '—')}")
    analysis_parts.append(f"{t('start_star_predict')}{results.get('sj_su_predict', '—')}")
    analysis_parts.append(f"{t('ten_stem_predict')}{results.get('tg_sj_su_predict', '—')}")
    ty = results.get("ty")
    if ty:
        analysis_parts.append(f"{t('sky_ground_method')}{ty.ty_gong_dist(results.get('style', 0), results.get('tn', 0))}")
    analysis_parts.append(f"{t('three_five')}{(results.get('three_door', '') or '') + (results.get('five_generals', '') or '')}")
    analysis_parts.append(f"{t('home_away')}{results.get('home_vs_away1', '—')}")
    analysis_parts.append(f"{t('win_loss')}{ttext.get('推少多以占勝負', '—')}")
    analysis_parts.append(f"{t('wind_cloud')}{results.get('home_vs_away3', '—')}")
    analysis_parts.append(f"{t('solitary')}{ttext.get('推孤單以占成敗', '—')}")
    analysis_parts.append(f"{t('yin_yang_adversity')}{ttext.get('推陰陽以占厄會', '—')}")
    analysis_parts.append(f"{t('emperor_tour')}{ttext.get('明天子巡狩之期術', '—')}")
    analysis_parts.append(f"{t('ruler_base')}{ttext.get('明君基太乙所主術', '—')}")
    analysis_parts.append(f"{t('minister_base')}{ttext.get('明臣基太乙所主術', '—')}")
    analysis_parts.append(f"{t('people_base')}{ttext.get('明民基太乙所主術', '—')}")
    analysis_parts.append(f"{t('five_blessings')}{ttext.get('明五福太乙所主術', '—')}")
    analysis_parts.append(f"{t('five_blessings_calc')}{ttext.get('明五福吉算所主術', '—')}")
    analysis_parts.append(f"{t('heaven_yi')}{ttext.get('明天乙太乙所主術', '—')}")
    analysis_parts.append(f"{t('earth_yi')}{ttext.get('明地乙太乙所主術', '—')}")
    analysis_parts.append(f"{t('zhifu')}{ttext.get('明值符太乙所主術', '—')}")
    analysis_body = "<br>".join(_esc(p) for p in analysis_parts if p)
    parts.append(_classic_card(
        t("chart_analysis"), analysis_parts[0] if analysis_parts else "", analysis_body,
        open_by_default=False, is_html_body=True,
    ))

    # ── 3. 史事記載 ──
    ch = results.get("ch") or ""
    if ch:
        parts.append(_classic_card(t("history_records"), "", ch))

    # ── 4. 格局釋義 ──
    _sg = ttext.get("釋格局", {})
    if _sg:
        sg_text = "；".join([f"{k}——{v}" for k, v in _sg.items()])
        parts.append(_classic_card(t("shi_geju"), "", sg_text))

    # ── 5. 神將所主（卷二/七）──
    _sj = ttext.get("神將所主", {})
    if _sj:
        _16s = _sj.get("十六宮間神", {})
        _tm = _16s.get("天目所臨", {})
        _9g = _sj.get("九宮所主", {})
        _jy = _sj.get("陰陽絕易", {})
        _bm = _sj.get("八門所主", {})
        _ty2 = _sj.get("天乙所主", {})
        _dy2 = _sj.get("地乙所主", {})
        _zf2 = _sj.get("直符所主", {})
        _fs2 = _sj.get("四神所主", {})
        _dyo = _sj.get("大遊所主", {})
        _xyo = _sj.get("小遊所主", {})
        _jy_hits = _jy.get("臨宮", [])
        _jy_txt = (
            "、".join(h["類型"] for h in _jy_hits if isinstance(h, dict))
            if _jy_hits and isinstance(_jy_hits[0], dict)
            else str(_jy_hits[0]) if _jy_hits else "—"
        )
        def _god_part(label, block):
            if not block:
                return ""
            duan = block.get("斷語") or block.get("本象", "")
            if not duan or str(duan) == "None":
                return ""
            return f"{label}（{duan}）；"

        _line1 = (
            f"天目臨{_tm.get('神', '—')}（{_tm.get('所主', '')}）；"
            f"九宮{_9g.get('太乙落宮', '—')}（{_9g.get('所主', '')}）；"
            f"絕易{_jy_txt}；"
            f"值事{_bm.get('值事八門', '—')}門{_bm.get('值事所主', '')}；"
            f"太乙臨{_bm.get('太乙所臨門', '—')}門（{_bm.get('太乙門吉凶', '')}）；"
            f"{_god_part('天乙', _ty2)}"
            f"{_god_part('地乙', _dy2)}"
            f"{_god_part('直符', _zf2)}"
            f"{_god_part('四神', _fs2)}"
        ).rstrip("；")
        sj_lines = [_line1]
        if _dyo or _xyo:
            _dytm = _dyo.get("大遊天目", {})
            _xyo_c = _xyo.get("合宮", []) if _xyo else []
            _xyo_real = [c for c in _xyo_c if c and not str(c).startswith("無特殊")]
            _xyo_txt = (
                "；".join(_xyo_real) if _xyo_real
                else (_xyo.get("本象", "") if _xyo else "")
            )
            _dyo_parts = []
            if _dyo.get("凶筭所主"):
                _dyo_parts.append(f"大遊（{_dyo['凶筭所主']}）")
            if _dytm.get("本象"):
                _dyo_parts.append(f"大遊天目（{_dytm['本象']}）")
            if _xyo_txt:
                _dyo_parts.append(f"小遊（{_xyo_txt}）")
            if _dyo_parts:
                sj_lines.append("；".join(_dyo_parts))
        sj_text = "\n\n".join(sj_lines)
        parts.append(_classic_card(t("shenjiang_suozhu"), "", sj_text))

    # ── 6. 星曜分佈（十六宮 + 太乙九星 + 文昌九星 + 九宮貴神 + 三旗行宮）──
    star_parts = []
    _16dist = ttext.get("十六宮分佈", {})
    if _16dist:
        _16p = [f"{zhi}[{'、'.join(stars)}]" for zhi, stars in _16dist.items() if stars]
        if _16p:
            star_parts.append(f"{t('sixteen_palace')}{'；'.join(_16p)}")
    _ts9 = ttext.get("太乙九星", {})
    if _ts9:
        _ts_dist = _ts9.get("九星分布", {})
        _ts_text = "、".join([f"{g}宮{nm}" for g, nm in _ts_dist.items()])
        star_parts.append(f"{t('taiyi_stars')}直符{_ts9.get('直符九星', '—')}（入宮{_ts9.get('入星宮年數', '—')}年）；{_ts9.get('直符所主', '')}；分布：{_ts_text}")
    _ws9 = ttext.get("文昌九星", {})
    if _ws9:
        _ws_dist = _ws9.get("文昌九星分布", {})
        _ws_text = "、".join([f"{g}宮{nm}" for g, nm in _ws_dist.items()])
        star_parts.append(f"{t('wenchang_stars')}直事{_ws9.get('直事文昌星', '—')}（入宮{_ws9.get('入宮年數', '—')}年）；臨{_ws9.get('臨宮分野', '')}；分布：{_ws_text}")
    _ng = ttext.get("九宮貴神", {})
    if _ng:
        _dist = _ng.get("九宮貴神分布", {})
        _dist_text = "、".join([f"{g}宮{nm}" for g, nm in _dist.items()])
        star_parts.append(f"{t('nine_gods')}直事貴神爲{_ng.get('直事貴神', '—')}（小周餘{_ng.get('小周餘', '—')}）；鈎宮分布：{_dist_text}")
    if star_parts:
        star_text = "\n\n".join(star_parts)
        parts.append(_classic_card(t("star_distribution_label"), "", star_text))

    # ── 7. 軍事戰略（卷五 + 卷十五 + 卷十七，合併）──
    mil_parts = []
    _j5 = ttext.get("軍事戰略", {})
    if _j5:
        _nw = _j5.get("內外占攻擊", {})
        _zk = _j5.get("太乙助主客", {})
        _cd = _j5.get("算長短緩急", {}).get("主算", {})
        _zd = _j5.get("主客動靜", {})
        _fx = _j5.get("輔相賢否", {}).get("我國輔相", {})
        _js5 = _j5.get("將帥賢否", {}).get("我國將帥", {})
        _sz5 = _j5.get("數有所主", {}).get("主算", {})
        mil_parts.append(
            f"{t('junshi_vol5')}{_format_neiwai(_nw)}；{_zk.get('斷語', '')}；"
            f"主算{_cd.get('長短', '—')}{_cd.get('和否', '')}（{_cd.get('斷語', '')}）；{_zd.get('勝負', '')}"
        )
        _line5 = []
        if _fx.get("斷語"):
            _line5.append(f"輔相{_fx.get('賢否', '')}（{_fx['斷語']}）")
        if _js5.get("斷語"):
            _line5.append(f"將帥{_js5.get('賢否', '')}（{_js5['斷語']}）")
        if _sz5.get("斷語"):
            _line5.append(f"主算{_sz5.get('音')}音（{_sz5['斷語']}）")
        if _line5:
            mil_parts.append("；".join(_line5))
    _jy15 = ttext.get("軍事應用", {})
    if _jy15:
        _qb = _jy15.get("奇兵伏兵", {})
        _wz = _jy15.get("五陣置旗", {})
        _hz = _wz.get("主陣旗", {})
        _az = _jy15.get("安營置陣", {})
        _cs15 = _jy15.get("出兵稱神", {}).get("主稱神", {})
        _cx15 = _jy15.get("陳兵出鄉", {}).get("主", {})
        _fh15 = _jy15.get("分合用兵", {})
        _gf15 = _jy15.get("五音觀風察將", {})
        _js15 = _jy15.get("軍勢勝負", {})
        mil_parts.append(
            f"{t('junshi_vol15')}主奇兵{_qb.get('主奇兵位', '—')}、客奇兵{_qb.get('客奇兵位', '—')}；"
            f"{_qb.get('伏兵', '')}；主陣{_hz.get('陣型', '—')}{_hz.get('旗色', '')}、"
            f"出鄉{_cx15.get('出鄉', '—')}；{_az.get('斷語', '')}"
        )
        _line15 = []
        if _cs15.get("咒"):
            _line15.append(f"稱神{_cs15.get('祀方', '')}（{_cs15.get('咒', '')}）")
        if _fh15.get("斷語"):
            _line15.append(f"分合{_fh15['斷語']}")
        if _gf15.get("斷語"):
            _line15.append(f"察將{_gf15['斷語']}")
        if _js15.get("斷語"):
            _line15.append(f"軍勢{_js15['斷語']}")
        if _line15:
            mil_parts.append("；".join(_line15))
    _jz17 = ttext.get("軍事占斷", {})
    if _jz17:
        _dd = _jz17.get("敵國動靜", {})
        _jm = _jz17.get("間諜虛實", {})
        _ds = _jz17.get("敵使虛實", {})
        _dl = _jz17.get("敵兵來方", {})
        _cy = _jz17.get("出兵用時", {})
        mil_parts.append(
            f"{t('junshi_vol17')}{_dd.get('動靜', '—')}（{_dd.get('斷語', '')}）；"
            f"間諜{_jm.get('間諜', '—')}；敵使{_ds.get('虛實', '—')}；"
            f"{_dl.get('方向', '')}{_dl.get('兵勢', '')}；出兵{_cy.get('主方', {}).get('斷語', '')}"
        )
        _jw = _jz17.get("見聞虛實", {})
        _tb = _jz17.get("討捕叛亡", {})
        _zq = _jz17.get("執囚對吏", {})
        _qs = _jz17.get("求索所得", {})
        _sj17 = _jz17.get("時計諸事", {})
        if _jw or _tb or _zq or _qs or _sj17:
            _sj_items = "、".join(_sj17.get("諸事", [])) if _sj17 else ""
            mil_parts.append(
                f"見聞{_jw.get('天目內外', '—')}（{_jw.get('斷語', '')}）；"
                f"討捕{_tb.get('結果', '—')}（{'；'.join(_tb.get('得機', []))}）；"
                f"執囚{'可解' if _zq.get('可解') else '難解'}（{_zq.get('斷語', '')}）；"
                f"求索{'有得' if _qs.get('有得') else '無得'}（{_qs.get('斷語', '')}）；"
                f"時計{_sj_items}"
            )
    _sq = ttext.get("三旗行宮", {})
    if _sq:
        mil_parts.append(
            f"{t('sanqi')}太歲青龍旗{_sq.get('太歲青龍旗', '—')}、"
            f"太陰黑旗{_sq.get('太陰黑旗', '—')}、"
            f"害氣赤旗{_sq.get('害氣赤旗', '—')}（{_sq.get('會合', '')}）"
        )
    # 軍事戰略卡片（含五陣八陣圖）
    _mil_text = ""
    if mil_parts:
        _mil_text = "\n\n".join(mil_parts)
    _wuzhen_data = (ttext.get("軍事應用", {}) or {}).get("五陣置旗")
    if _mil_text or _wuzhen_data:
        _mil_body_parts = []
        if _mil_text:
            _mil_body_parts.append(_esc(_mil_text).replace("\n", "<br>"))
        if _wuzhen_data:
            _mil_body_parts.append(f'<div class="classic-sub-label">{_esc(t("five_formations"))}</div>')
            _mil_body_parts.append(_html_table(wuzhen_table_rows(_wuzhen_data)))
            _mil_body_parts.append(f'<div class="classic-sub-label">{_esc(t("wuzhen_reference"))}</div>')
            _mil_body_parts.append(_html_table(wuzhen_reference_rows()))
            _bazhen_svg = wuzhen_bazhen_svg(
                _wuzhen_data,
                title_five=t("five_formations_short"),
                title_eight=t("eight_formations_short"),
                title_chubing=t("chubing_xiang_title"),
                center_label=t("bazhen_center"),
                home_label=t("side_home"),
                away_label=t("side_away"),
            )
            _mil_body_parts.append(_bazhen_svg)
        parts.append(_classic_card(
            t("junshi_label"), "", "\n".join(_mil_body_parts), is_html_body=True,
        ))

    # ── 8. 災變分野（卷十一 + 卷八，合併）──
    disaster_parts = []
    _v11 = ttext.get("卷十一", {})
    if _v11:
        _ff = _v11.get("飛符四殺", {})
        _zy = _v11.get("州國災變月數", {})
        _eh = _v11.get("城名厄會", {})
        _sn = _v11.get("城名歲內災發", {})
        _bh = _v11.get("十六宮間變化", {})
        disaster_parts.append(
            f"{t('vol11')}飛符{_ff.get('飛符', '—')}，災{_ff.get('災殺', '—')}鬼{_ff.get('鬼殺', '—')}；州國災月{_zy.get('斷語', '—')}"
        )
        _line11 = []
        if _eh.get("斷語"):
            _line11.append(f"城名{_eh.get('城名', '')}{_eh['斷語']}")
        if _sn.get("斷語"):
            _line11.append(_sn["斷語"])
        if _ff.get("城名斷語"):
            _line11.append(_ff["城名斷語"])
        if _bh.get("加神"):
            _line11.append(f"十六神以{_bh['加神']}為樞（{_bh['要訣']}）")
        if _line11:
            disaster_parts.append("；".join(_line11))
    _v8 = ttext.get("卷八", {})
    if _v8:
        _fy = _v8.get("太乙分野", {})
        _line8 = [f"{t('fenye')}{_fy.get('宮名', '—')}宮·{_fy.get('州', '—')}"]
        if _fy.get("城名"):
            _line8.append(f"城名{_fy['城名']}（{_fy.get('城名干支', '')}）")
        if _v8.get("歲建分野", {}).get("國"):
            _sz8 = _v8["歲建分野"]
            _line8.append(f"歲建{_sz8.get('地支', '')}·{_sz8.get('國', '')}分")
        disaster_parts.append("；".join(_line8))
    if disaster_parts:
        disaster_text = "\n\n".join(disaster_parts)
        parts.append(_classic_card(t("disaster_fenye_label"), "", disaster_text))

    # ── 9. 運氣音律（五運六氣 + 五音之數 + 天目合會 + 十精雲氣，合併）──
    qi_parts = []
    _wl = ttext.get("五運六氣", {})
    if _wl:
        _hui = "、".join(_wl.get("歲會天符", []))
        qi_parts.append(
            f"{t('wuyun_liuqi')}{_wl.get('五運', '—')}（{_wl.get('太過不及', '—')}）"
            f"司天{_wl.get('司天', '—')}{_wl.get('司天化', '')}、在泉{_wl.get('在泉', '—')}{_wl.get('在泉化', '')}；"
            f"{_wl.get('主氣', '')}{_wl.get('客氣', '')}；歲會：{_hui}"
        )
    _wy = ttext.get("五音之數", {})
    if _wy:
        _hm = _wy.get("主算五音", {})
        _am = _wy.get("客算五音", {})
        _ty3 = _wy.get("太乙五音", {})
        qi_parts.append(
            f"{t('wuyin_shu')}主算{_hm.get('音', '—')}（{_hm.get('所主', '')}）、"
            f"客算{_am.get('音', '—')}（{_am.get('所主', '')}）、太乙宮{_ty3.get('音', '—')}；"
            f"主斷：{_hm.get('斷語', '')}"
        )
    _v10 = ttext.get("卷十", {})
    if _v10:
        _wq10 = _v10.get("五運六氣", {})
        _hh = _v10.get("天目合會", [])
        qi_parts.append(
            f"{t('vol10_hehui')}{_wq10.get('五運', '—')}·{_wq10.get('司天', '—')}；"
            f"{'、'.join(_hh) if _hh else '主客氣調'}"
        )
    _v18 = ttext.get("卷十八", {})
    if _v18:
        _sj18 = _v18.get("十精數", {})
        _same18 = _v18.get("與太乙同宮", [])
        qi_parts.append(
            f"{t('yunqi')}十精數{_sj18.get('十精數', '—')}·{_sj18.get('斷語', '')}；"
            f"同宮{'、'.join(_same18) if _same18 else '無'}"
        )
        if _v18.get("要訣"):
            qi_parts.append(_v18["要訣"])
    if qi_parts:
        qi_text = "\n\n".join(qi_parts)
        parts.append(_classic_card(t("qi_music_label"), "", qi_text))

    # ── 10. 行限推論（陽九百六）──
    yjxx = results.get("yjxx") or ""
    blxx = results.get("blxx") or ""
    if yjxx or blxx:
        limit_text = f"{t('yang_nine')}\n{yjxx}\n\n{t('bai_liu')}\n{blxx}"
        parts.append(_classic_card(t("xingxian_label"), "", limit_text))

    # ── 11. 大小遊軌運（卷九）──
    _v9 = ttext.get("卷九", {})
    if _v9:
        _dy9 = _v9.get("大遊軌運") or {}
        _xy9 = _v9.get("小遊軌運") or {}
        _gy_parts = []
        if _dy9 or _xy9:
            _gy_parts.append(
                f"{t('guiyun')}"
                f"大遊{_dy9.get('重卦', '—')}{_dy9.get('內爻名', '')}"
                f"（{_dy9.get('內卦', '')}/{_dy9.get('外卦', '')}·策{_dy9.get('總策', '—')}）；"
                f"小遊{_xy9.get('重卦', '—')}{_xy9.get('內爻名', '')}"
                f"（策{_xy9.get('總策', '—')}）；"
                f"落宮{_v9.get('大遊落宮', '—')}/{_v9.get('小遊落宮', '—')}"
            )
            _line9 = []
            if _v9.get("大遊入宮年數") is not None:
                _line9.append(f"{t('guiyun_palace_years')}{_v9['大遊入宮年數']}年")
            if _v9.get("行宮卦異"):
                _line9.append(t("guiyun_gong_diff"))
            _yj9 = _v9.get("陽九限數") or {}
            _bl9 = _v9.get("百六限數") or {}
            if _yj9:
                _line9.append(f"{t('yangjiu_xian')}入限{_yj9.get('入限年數', '—')}年")
            if _bl9:
                _line9.append(f"{t('bailiu_xian')}入限{_bl9.get('入限年數', '—')}年")
            if _v9.get("歲計陽九支") or _v9.get("歲計百六支"):
                _line9.append(
                    f"歲計陽九{_v9.get('歲計陽九支', '—')}／百六{_v9.get('歲計百六支', '—')}"
                )
            if _line9:
                _gy_parts.append("；".join(_line9))
        _xz9 = _v9.get("小遊行爻災祥") or {}
        if _xz9.get("斷語"):
            _gy_parts.append(
                f"{t('guiyun_xingyao')}"
                f"{_xz9.get('重卦', '')}{_xz9.get('爻名', '')}·{_xz9.get('納甲', '')}·"
                f"{_xz9.get('天干分野', '')}{_xz9.get('地支分野', '')}；"
                f"{_xz9['斷語']}"
            )
        # 詳情表格
        _detail_parts = []
        if _dy9 or _xy9:
            _detail_parts.append(f'<div class="classic-sub-label">{_esc(t("guiyun_chong"))}</div>')
            _detail_parts.append(_html_table([
                chong_gua_row(_dy9, scope="大遊"),
                chong_gua_row(_xy9, scope="小遊"),
            ]))
            _detail_parts.append(f'<div class="classic-sub-label">{_esc(t("guiyun_inner_outer"))}·大遊</div>')
            _detail_parts.append(_html_table(inner_outer_rows(_v9.get("大遊內卦"), _v9.get("大遊外卦"), scope="大遊")))
            _detail_parts.append(f'<div class="classic-sub-label">{_esc(t("guiyun_inner_outer"))}·小遊</div>')
            _detail_parts.append(_html_table(inner_outer_rows(_v9.get("小遊內卦"), _v9.get("小遊外卦"), scope="小遊")))
        _limits9 = limit_rows(_v9)
        if _limits9:
            _detail_parts.append(f'<div class="classic-sub-label">{_esc(t("guiyun_limits"))}</div>')
            _detail_parts.append(_html_table(_limits9))
        _ce9 = _v9.get("四象之策") or []
        if _ce9:
            _detail_parts.append(f'<div class="classic-sub-label">{_esc(t("guiyun_ce_ref"))}</div>')
            _detail_parts.append(_html_table([dict(r) for r in _ce9]))
        for _key9 in ("大遊軌運", "小遊軌運"):
            _yj9t = _v9.get(_key9, {})
            if _yj9t.get("要訣"):
                _detail_parts.append(f'<div class="classic-caption">{_esc(_yj9t["要訣"])}</div>')
        if _v9.get("要訣"):
            _detail_parts.append(f'<div class="classic-caption">{_esc(_v9["要訣"])}</div>')
        if _gy_parts:
            _gy_text = "\n\n".join(_gy_parts)
            if _detail_parts:
                _gy_text += "\n" + "\n".join(_detail_parts)
            parts.append(_classic_card(t("guiyun_label"), "", _gy_text, is_html_body=True))

    # ── 12. 運籌博弈分析（Nash 均衡 + 線性規劃）──
    _gt_report = results.get("運籌博弈分析")
    if _gt_report is None:
        try:
            _gt_report = TaiyiGame(ttext).分析報告()
        except Exception:
            _gt_report = None
    if _gt_report:
        _gt_parts = []
        _gt_parts.append(f"**古法推主客相闗：** {_esc(_gt_report.get('古法推主客相闗', '—'))}")
        _gt_parts.append(f"**{t('game_theory_winrate')}：** {_esc(_gt_report.get('主方勝率判斷', '—'))}")
        _gt_parts.append(f"**{t('game_theory_value')}：** `{_gt_report.get('博弈均衡值', '—')}`")
        _gt_parts.append(f"##### {t('game_theory_payoff')}")
        _payoff_rows = []
        _h_strats = _gt_主方策略列
        _a_strats = _gt_客方策略列
        _payoff = _gt_report.get("支付矩陣", [])
        for _hi, _hname in enumerate(_h_strats):
            _row = {"策略": _hname}
            for _ai, _aname in enumerate(_a_strats):
                _row[_aname] = round(_payoff[_hi][_ai], 2) if _hi < len(_payoff) and _ai < len(_payoff[_hi]) else "—"
            _payoff_rows.append(_row)
        _gt_parts.append(_html_table(_payoff_rows))
        _gt_parts.append(f"**{t('game_theory_home_strategy')}**")
        _home_rows = [{"策略": _h, "概率": _p} for _h, _p in zip(_h_strats, _gt_report.get("主方均衡策略", []))]
        _gt_parts.append(_html_table(_home_rows))
        _gt_parts.append(f"**{t('game_theory_away_strategy')}**")
        _away_rows = [{"策略": _a, "概率": _p} for _a, _p in zip(_a_strats, _gt_report.get("客方均衡策略", []))]
        _gt_parts.append(_html_table(_away_rows))
        _lp = _gt_report.get("LP最大勝率", {})
        if _lp:
            _gt_parts.append(f"##### {t('game_theory_lp')}")
            _gt_parts.append(f'<div class="classic-info-box">{_esc(_lp.get("建議文字", ""))}</div>')
        _gt_parts.append(f"**主方最優純策略：** {_esc(_gt_report.get('主方最優純策略', '—'))}")
        _gt_parts.append(f"**客方最優純策略：** {_esc(_gt_report.get('客方最優純策略', '—'))}")
        # 將 markdown 風格轉為 HTML
        _gt_body = "\n".join(_gt_parts)
        _gt_body = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", _gt_body)
        _gt_body = re.sub(r"##### (.+)", r"<h5>\1</h5>", _gt_body)
        parts.append(_classic_card(t("game_theory_header"), "", _gt_body, is_html_body=True))

    if not parts:
        return ""

    inner = "\n".join(parts)
    return f'<div class="classic-reading-section">{inner}</div>'


# ── 內部渲染函數 ────────────────────────────────────────

def _render_mini_lines(bits: list[bool], yao_idx: int, is_today: bool) -> str:
    """六爻迷你圖（動爻著色）。上爻在前。"""
    lines: list[str] = []
    for i in reversed(range(6)):
        is_yang = bits[i]
        yi = i + 1
        is_active = (yi == yao_idx)
        cls = "liuri-line liuri-yang" if is_yang else "liuri-line liuri-yin"
        if is_active:
            cls += " liuri-line-active"
        if is_yang:
            inner = '<span class="liuri-line-bar"></span>'
        else:
            inner = '<span class="liuri-line-bar liuri-line-bar-l"></span><span class="liuri-line-bar liuri-line-bar-r"></span>'
        lines.append(f'<div class="{cls}">{inner}</div>')
    inner = "\n".join(lines)
    return f'<div class="liuri-lines">{inner}</div>'


def _classic_card(
    title: str,
    preview: str,
    body: str,
    *,
    open_by_default: bool = False,
    is_html_body: bool = False,
) -> str:
    """古典解讀折疊卡片。"""
    open_attr = " open" if open_by_default else ""
    body_html = body if is_html_body else _esc(body)
    return f"""
<details class="classic-card"{open_attr}>
  <summary class="classic-card-header">
    <span class="classic-card-title">{_esc(title)}</span>
    <span class="classic-card-preview">{_esc(preview)}</span>
  </summary>
  <div class="classic-card-body">
    {body_html}
  </div>
</details>"""


def _format_neiwai(nw: dict) -> str:
    """格式化內外占攻擊。"""
    if not nw:
        return "—"
    parts = []
    if nw.get("主"):
        parts.append(f"主{nw['主']}")
    if nw.get("客"):
        parts.append(f"客{nw['客']}")
    return "、".join(parts) if parts else str(nw)