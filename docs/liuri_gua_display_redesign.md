# 流日卦運 / 日計 + 64卦顯示優化方案

> 針對 kintaiyi Streamlit 介面中「值卦（年/月/日/時/分卦）+ 64卦瀏覽 + 古典解讀」部分的 UI 重構提案
> 參考對象：iOS App《太乙神數》(App Store ID: 6476464538) 底部橫向卦象時間軸 + 左側古典解讀區

---

## 一、現狀分析

### 目前問題（基於程式碼 review）

1. **值卦顯示：純文字羅列，無卦象圖示**
   - `streamlit_app.py:4136-4141` 中，年/月/日/時/分卦以五行 `st.markdown` 純文字輸出
   - 只有卦名文字（如「既濟」），沒有 Unicode 卦符（䷾）、沒有六爻視覺、沒有爻位標示
   - 使用者無法一眼看出卦象結構，更無法感知卦隨時間的流動變化

2. **64卦無獨立展示入口**
   - `config.gua` dict（1-64 → 卦名+卦符）存在但未在介面中暴露
   - 使用者無法瀏覽全部64卦、無法點擊查看單卦的象曰/爻辭
   - `gua_xiang.py` 中有卦象全文（象曰、總述、六爻觀象），但只在統運入卦路徑顯示

3. **古典解讀區：密集文字牆**
   - `streamlit_app.py:4186-4380` 的 explanation expander 內容極長
   - 太乙秘書、史事記載、盤局分析、卷三～卷十八全部以 `st.markdown` 逐行堆疊
   - 沒有卡片分組、沒有視覺層級、沒有折疊子區段
   - 與 iOS App 左側「武經總要 / 術數匯考」的卡片式呈現差距極大

4. **與主圓盤零互動**
   - 值卦與圓盤完全分離
   - 點擊卦象不會高亮圓盤任何元素
   - 64卦與太乙十六宮無對應關係展示

5. **缺乏時間流動感**
   - 年/月/日/時/分卦是線性遞進的，但顯示方式是垂直靜態列表
   - 看不出「現在走到哪」、「下一步會變成什麼卦」

---

## 二、設計方向

### 核心理念

> **「底部卦象時間軸 + 64卦滑動面板 + 卡片式解讀區」三層結構**

參考 iOS App 的做法：
- 底部固定一條橫向卦象帶，顯示「年→月→日→時→分」的卦象流動
- 點擊底部某卦 → 展開該卦的詳細解讀卡片
- 64卦以可切換的面板形式呈現，不佔常駐空間

### 2.1 整體佈局

```
┌──────────────────────────────────────────────────────────────┐
│  [太乙圓盤 SVG]              │  [側欄：完整參數 chips]        │
│                              │  [十六宮速覽]                  │
│                              │                                │
├──────────────────────────────┴────────────────────────────────┤
│  [統運十二運時間軸]  ← 已完成（yun_timeline）                  │
├────────────────────────────────────────────────────────────────┤
│  [值卦卦象時間軸]  ← 新增：年月日時分五卦橫向排列               │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                      │
│  │ ䷾  │ │ ䷶  │ │ ䷂  │ │ ䷄  │ │ ䷃  │   ← 點擊展開詳細     │
│  │既濟│ │  豐 │ │  屯 │ │  需 │ │  蒙 │                      │
│  │年卦│ │月卦│ │日卦│ │時卦│ │分卦│                      │
│  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘                      │
│         ▲ 當前                                               │
├────────────────────────────────────────────────────────────────┤
│  [卦象解讀卡片]  ← 點擊時間軸某卦後展開                        │
│  ┌──────────────────────────────────────────────────┐         │
│  │  ䷾ 既濟 · 日卦                                     │         │
│  │  象曰：水在火上，既濟。君子以思患而預防之。          │         │
│  │  ── 六爻 ──────────────────────────────────        │         │
│  │  上六 ││││││  外極災變                            │         │
│  │  九五 ││││││  君弱臣強                            │         │
│  │  六四 ││││││  待治之限                            │         │
│  │  九三 ││││││  內極災變  ← 當前爻                  │         │
│  │  九二 ││││││  安平之限                            │         │
│  │  初九 ││││││  建功立德                            │         │
│  │  ── 古典解讀 ──────────────────────────────        │         │
│  │  【太乙秘書】既濟之卦，陰陽各得其位…                │         │
│  │  【術數匯考】既濟者，水火相交…                      │         │
│  └──────────────────────────────────────────────────┘         │
├────────────────────────────────────────────────────────────────┤
│  [64卦面板]  ← 可切換顯示/隱藏                                 │
│  ┌──┐┌──┐┌──┐┌──┐┌──┐┌──┐┌──┐┌──┐                           │
│  │䷀││䷁││䷂││䷃││䷄││䷅││䷆││䷇│  乾~比 (1-8)             │
│  └──┘└──┘└──┘└──┘└──┘└──┘└──┘└──┘                           │
│  ┌──┐┌──┐┌──┐┌──┐┌──┐┌──┐┌──┐┌──┐                           │
│  │䷈││䷉││䷊││䷋││䷌││䷍││䷎││䷏│  小畜~豫 (9-16)          │
│  └──┘└──┘└──┘└──┘└──┘└──┘└──┘└──┘                           │
│  ...（8x8 網格）                                              │
│  當前盤局對應卦以運色高亮                                      │
└────────────────────────────────────────────────────────────────┘
```

### 2.2 底部卦象時間軸（值卦帶）

**設計形式**：橫向五卡片帶，對應「年→月→日→時→分」五層值卦

每張卡片包含：
- Unicode 卦符（28px，如 ䷾）
- 卦名（14px 粗體，如「既濟」）
- 層級標籤（10px muted，如「日卦」）
- 當前爻位標示（底部小圓點 + 爻名，如「九三」）

**高亮規則**：
- 當前排盤時間最細粒度的卦（通常為分卦）以運色邊框高亮
- 其餘四卦以低飽和度呈現
- 點擊任一卡片 → 下方展開該卦的詳細解讀

**左右切換**：不需要，因為年月日時分是固定五層，不是時間序列滑動。
但可以加入「前一日 / 後一日」的微調按鈕，讓使用者快速查看相鄰日期的日卦變化。

### 2.3 64卦面板

**呈現方式**：可切換顯示/隱藏的折疊面板（`<details>` 或 `st.expander`）

**網格結構**：8列 × 8行，每格一個卦
- 格內顯示：卦符（20px）+ 卦名（10px）
- 當前盤局對應的卦以運色高亮 + 微發光
- 點擊某卦 → 展開該卦的象曰/總述/六爻觀象

**卦象資料來源**：
- `config.gua` dict（1-64 → 卦名+卦符）
- `gua_xiang.py` 的 `tongyun_gua_xiang(gua_name)` → 象曰、總述、六爻觀象
- `config.gua_yao_years` → 各爻年數

**與值卦的關聯**：
- 時間軸上的五個值卦在64卦面板中自動高亮
- 統運入卦也在面板中高亮（不同色標）

---

## 三、資訊層級

### 3.1 值卦卡片（一級 — 常駐顯示）

| 資訊項 | 來源 | 顯示方式 |
|--------|------|----------|
| 卦符 | `config.gua[idx][1]` | 28px Unicode |
| 卦名 | `config.gua[idx][0]` | 14px 粗體 |
| 層級 | year/month/day/hour/minute | 10px muted 標籤 |
| 當前爻 | 太乙值事爻 | 底部小圓點 + 爻名 |

### 3.2 卦象解讀卡片（二級 — 點擊展開）

| 資訊項 | 來源 |
|--------|------|
| 象曰 | `gua_xiang.tongyun_gua_xiang(name)["象曰"]` |
| 總述 | `gua_xiang.tongyun_gua_xiang(name)["總述"]` |
| 六爻觀象 | `gua_xiang._yao_observations(name)` |
| 當前爻標示 | 值卦的直事爻 |
| 吉凶色標 | 爻位 → `_YAO_HUOFU` 映射 |

### 3.3 古典解讀區（三級 — 卡片折疊）

將現有 explanation expander 中的密集文字重組為卡片：

| 卡片 | 內容 | 對應 iOS App |
|------|------|-------------|
| 太乙秘書 | `results["ts"]` | 武經總要 |
| 史事記載 | `results["ch"]` | 歷史驗例 |
| 盤局分析 | 太乙落宮、主客算、三門五將 | 術數匯考 |
| 格局釋義 | `ttext["釋格局"]` | 術數匯考 |
| 分野疆界 | `ttext["卷八"]` | 術數匯考 |
| 軍事戰略 | `ttext["軍事戰略"]` + `ttext["軍事應用"]` | 武經總要 |
| 五運六氣 | `ttext["五運六氣"]` | 術數匯考 |
| 行限推論 | 陽九百六 + 大小遊軌運 | 術數匯考 |

---

## 四、美學與一致性

### 4.1 配色

沿用 `custom_css.py` 已有的暗色主題 CSS 變數：
- 卡片背景：`rgba(255, 255, 255, 0.03)`
- 邊框：`var(--border-subtle)`
- 文字：`var(--text-primary)` / `--text-secondary` / `--text-muted`
- 圓角：`var(--radius-md)` = 12px

新增值卦色系（與五層計式對應）：
```css
--hex-year:   #6b4c93;  /* 年卦 · 深紫 */
--hex-month:  #4a6741;  /* 月卦 · 暗綠 */
--hex-day:    #b8860b;  /* 日卦 · 琥珀（主色） */
--hex-hour:   #5b7c99;  /* 時卦 · 青灰 */
--hex-minute: #7d6b8d;  /* 分卦 · 灰紫 */
```

### 4.2 字體層級

```
卦符      : 28px / 400 / --text-primary / letter-spacing 0
卦名      : 14px / 700 / --text-primary
層級標籤  : 10px / 600 / --text-muted / letter-spacing 0.08em / UPPERCASE
爻名      : 11px / 500 / --text-secondary
象曰      : 13px / 400 / --text-secondary / line-height 1.65
解讀正文  : 13px / 400 / --text-secondary / line-height 1.65
卡片標題  : 12px / 600 / --text-muted / letter-spacing 0.06em
```

### 4.3 六爻視覺

使用 CSS 模擬六爻圖形（不依賴 Unicode 卦符的字型渲染差異）：

```html
<div class="hex-lines" data-yao="3">
  <div class="hex-line hex-yang"></div>  <!-- 初九 -->
  <div class="hex-line hex-yang"></div>  <!-- 九二 -->
  <div class="hex-line hex-yin hex-active"></div>  <!-- 六三 ← 當前 -->
  <div class="hex-line hex-yang"></div>  <!-- 六四 -->
  <div class="hex-line hex-yang"></div>  <!-- 九五 -->
  <div class="hex-line hex-yin"></div>   <!-- 上六 -->
</div>
```

- 陽爻：實線長條（`background: var(--text-primary)`）
- 陰爻：兩段短條中間留空
- 當前爻：左側 3px 運色豎條 + 微發光

### 4.4 間距與圓角

```
值卦卡片間距  : 0.5rem
值卦卡片內距  : 0.7rem 0.8rem
值卦卡片寬度  : 等分五列（flex: 1）
64卦格大小    : 48px × 56px
64卦格間距    : 4px
解讀卡片間距  : 0.65rem（與 yun-card 一致）
圓角          : 值卦卡片 10px / 64卦格 6px / 解讀卡片 14px
```

---

## 五、互動與體驗

### 5.1 點擊值卦卡片的反饋

1. **展開解讀**：點擊底部某張值卦卡片 → 下方展開該卦的象曰 + 六爻觀象 + 古典解讀
2. **高亮圓盤**：解讀展開時，圓盤對應宮位發光（需 Phase 2 JS）
3. **64卦聯動**：64卦面板中對應格子高亮

### 5.2 64卦面板的互動

1. **點擊某卦** → 展開該卦的象曰/總述/六爻觀象
2. **高亮標示**：
   - 當前年卦 → 紫色邊框
   - 當前月卦 → 綠色邊框
   - 當前日卦 → 琥珀色邊框
   - 當前時卦 → 青灰色邊框
   - 當前分卦 → 灰紫色邊框
   - 統運入卦 → 運色填充

### 5.3 古典解讀區的互動

- 每個解讀卡片為獨立 `<details>`，可單獨展開/折疊
- 預設只展開「太乙秘書」和「盤局分析」
- 其餘卡片預設折疊，減少初始資訊量

---

## 六、實作建議

### 6.1 新模組結構

```
apps/
  hex_timeline.py     ← 新增：值卦時間軸 + 64卦面板 HTML 組件
  hex_cards.py        ← 新增：卦象解讀卡片 + 古典解讀卡片
  custom_css.py       ← 擴充：加入 hex-timeline / hex-grid / hex-card CSS
  streamlit_app.py    ← 重構：4136-4141 值卦區 + 4186-4380 解讀區
```

### 6.2 值卦時間軸 HTML 結構

```html
<div class="hex-timeline-container">
  <div class="hex-timeline-header">
    <span class="hex-timeline-label">值卦 · 五層流變</span>
  </div>
  <div class="hex-timeline-track">
    <button class="hex-card" data-layer="year" style="--hex-color: var(--hex-year);">
      <span class="hex-symbol">䷾</span>
      <span class="hex-name">既濟</span>
      <span class="hex-layer">年卦</span>
      <span class="hex-yao-dot" data-yao="3"></span>
    </button>
    <button class="hex-card" data-layer="month" style="--hex-color: var(--hex-month);">
      <span class="hex-symbol">䷶</span>
      <span class="hex-name">豐</span>
      <span class="hex-layer">月卦</span>
    </button>
    <button class="hex-card hex-current" data-layer="day" style="--hex-color: var(--hex-day);">
      <span class="hex-symbol">䷂</span>
      <span class="hex-name">屯</span>
      <span class="hex-layer">日卦</span>
      <span class="hex-yao-dot" data-yao="2"></span>
    </button>
    <button class="hex-card" data-layer="hour" style="--hex-color: var(--hex-hour);">
      <span class="hex-symbol">䷄</span>
      <span class="hex-name">需</span>
      <span class="hex-layer">時卦</span>
    </button>
    <button class="hex-card" data-layer="minute" style="--hex-color: var(--hex-minute);">
      <span class="hex-symbol">䷃</span>
      <span class="hex-name">蒙</span>
      <span class="hex-layer">分卦</span>
    </button>
  </div>
</div>
```

### 6.3 64卦面板 HTML 結構

```html
<details class="hex-grid-panel">
  <summary class="hex-grid-toggle">六十四卦總覽</summary>
  <div class="hex-grid">
    <!-- 64 個格子，每格： -->
    <button class="hex-grid-cell hex-grid-current-year" data-gua-idx="1">
      <span class="hex-grid-symbol">䷀</span>
      <span class="hex-grid-name">乾</span>
    </button>
    <!-- ... 依此類推 64 個 ... -->
  </div>
</details>
```

### 6.4 卦象解讀卡片 HTML 結構

```html
<article class="hex-detail-card" style="--hex-color: var(--hex-day);">
  <div class="hex-detail-header">
    <span class="hex-detail-symbol">䷂</span>
    <div class="hex-detail-title">
      <span class="hex-detail-name">屯</span>
      <span class="hex-detail-layer">日卦</span>
    </div>
  </div>
  <div class="hex-detail-body">
    <div class="hex-lines" data-yao="2">
      <!-- 六爻視覺條 -->
    </div>
    <div class="hex-detail-xiang">
      <span class="hex-detail-label">象曰</span>
      <p>雲雷屯，君子以經綸。</p>
    </div>
    <div class="hex-detail-yao-list">
      <div class="hex-yao-row hex-yao-active">
        <span class="hex-yao-idx">初九</span>
        <span class="hex-yao-text">建功立德</span>
      </div>
      <div class="hex-yao-row hex-yao-current">
        <span class="hex-yao-idx">九二</span>
        <span class="hex-yao-text">安平之限 ←</span>
      </div>
      <!-- ... 其餘四爻 ... -->
    </div>
  </div>
  <details class="hex-detail-classic">
    <summary>古典解讀</summary>
    <div class="hex-classic-card">
      <span class="hex-classic-source">太乙秘書</span>
      <p>屯者，物之始生也…</p>
    </div>
    <div class="hex-classic-card">
      <span class="hex-classic-source">術數匯考</span>
      <p>屯卦坎上震下，動乎險中…</p>
    </div>
  </details>
</article>
```

### 6.5 古典解讀區重組

將 `streamlit_app.py:4186-4380` 的 explanation expander 內容拆分為獨立卡片：

```html
<div class="classic-reading-section">
  <details class="classic-card" open>
    <summary class="classic-card-header">
      <span class="classic-card-title">太乙秘書</span>
      <span class="classic-card-preview">既濟之卦，陰陽各得其位…</span>
    </summary>
    <div class="classic-card-body">
      <p>既濟之卦，陰陽各得其位，剛柔正而位當也…</p>
    </div>
  </details>

  <details class="classic-card">
    <summary class="classic-card-header">
      <span class="classic-card-title">盤局分析</span>
      <span class="classic-card-preview">太乙在三宮，主算三十一…</span>
    </summary>
    <div class="classic-card-body">
      <!-- 主客算、三門五將、主客勝負等 -->
    </div>
  </details>

  <details class="classic-card">
    <summary class="classic-card-header">
      <span class="classic-card-title">史事記載</span>
    </summary>
    <div class="classic-card-body">
      <!-- results["ch"] -->
    </div>
  </details>

  <details class="classic-card">
    <summary class="classic-card-header">
      <span class="classic-card-title">格局釋義</span>
    </summary>
    <div class="classic-card-body">
      <!-- ttext["釋格局"] -->
    </div>
  </details>

  <details class="classic-card">
    <summary class="classic-card-header">
      <span class="classic-card-title">分野疆界</span>
    </summary>
    <div class="classic-card-body">
      <!-- ttext["卷八"] -->
    </div>
  </details>

  <details class="classic-card">
    <summary class="classic-card-header">
      <span class="classic-card-title">軍事戰略</span>
    </summary>
    <div class="classic-card-body">
      <!-- 軍事戰略 + 軍事應用 -->
    </div>
  </details>

  <details class="classic-card">
    <summary class="classic-card-header">
      <span class="classic-card-title">五運六氣</span>
    </summary>
    <div class="classic-card-body">
      <!-- 五運六氣 + 五音之數 -->
    </div>
  </details>

  <details class="classic-card">
    <summary class="classic-card-header">
      <span class="classic-card-title">行限推論</span>
    </summary>
    <div class="classic-card-body">
      <!-- 陽九百六 + 大小遊軌運 -->
    </div>
  </details>
</div>
```

### 6.6 實作策略

**Phase 1（純 Streamlit + CSS，無 JS）**：
- `hex_timeline.py`：`render_hex_timeline(results, t=t)` → 值卦時間軸 HTML
- `hex_timeline.py`：`render_hex_grid(results, t=t)` → 64卦面板 HTML
- `hex_timeline.py`：`render_hex_detail(gua_name, layer, yao_idx, t=t)` → 卦象解讀卡片
- `hex_timeline.py`：`render_classic_reading(results, t=t)` → 古典解讀卡片群
- CSS 加入 `custom_css.py`
- `streamlit_app.py` 中替換 4136-4141 和 4186-4380

**Phase 2（JS 互動）**：
- 點擊值卦卡片 → `postMessage` → `st.session_state` 更新 → 展開對應解讀
- 64卦面板點擊 → 彈出該卦詳情
- 圓盤 SVG 高亮聯動

### 6.7 與現有 yun_timeline 的關係

```
排盤結果
  ├── 太乙圓盤 SVG
  ├── 完整參數 chips
  ├── [統運十二運時間軸]     ← yun_timeline.py（已完成）
  ├── [值卦卦象時間軸]       ← hex_timeline.py（新增）
  ├── [64卦面板]             ← hex_timeline.py（新增）
  ├── [卦象解讀卡片]         ← hex_timeline.py（新增）
  └── [古典解讀卡片群]       ← hex_timeline.py（新增）
```

統運時間軸展示的是「太乙統運 → 十二大運 → 入卦入爻」的宏觀時間流（11520年大週期）；
值卦時間軸展示的是「當前排盤時刻 → 年月日時分五層值卦」的微觀時間切片。
兩者互補，不重複。

---

## 七、資料流

### 7.1 值卦資料來源

```python
# streamlit_app.py gen_results() 已有：
results["ygua"] = ty.year_gua()[1]    # "既濟䷾"
results["mgua"] = ty.month_gua()[1]
results["dgua"] = ty.day_gua()[1]
results["hgua"] = ty.hour_gua()[1]
results["mingua"] = ty.minute_gua()[1]

# hex_timeline.py 需要解析：
# "既濟䷾" → ("既濟", "䷾")
# 並從 config.gua 反查卦序索引
```

### 7.2 卦象解讀資料來源

```python
from kintaiyi.gua_xiang import tongyun_gua_xiang
# tongyun_gua_xiang("既濟") → {"象曰": "...", "總述": "...", "爻觀象": {1: "...", ...}}
```

### 7.3 64卦完整列表

```python
from kintaiyi.config import gua, _KING_WEN_64
# gua = {1: "乾䷀", 2: "坤䷁", ... 64: "未濟䷿"}
# _KING_WEN_64 = "乾坤屯蒙需訟師比..."
```