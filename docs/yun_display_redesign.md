# 流日卦運 / 太乙大運顯示優化方案

> 針對 kintaiyi Streamlit 介面中「統運入卦 / 十二大運 / 卦象觀象」部分的 UI 重構提案
> 參考對象：iOS App《太乙神數》(App Store ID: 6476464538) 流日卦運 / 太乙大運顯示方式

---

## 一、現狀分析

### 目前問題（基於程式碼 review）

1. **資訊呈現方式：純文字堆疊**
   - `streamlit_app.py:4284-4420` 中，卷十二～十四的統運入卦、十二運立成、卦象觀象、行支編年全部以 `st.markdown` 一行行拼接，用「；」分隔
   - 使用者看到的是一整段密集文字，沒有視覺分隔
   - 十二運立成藏在 `st.expander` 內，以 `· 運名（總年）：卦序→卦序` 的純文字列表呈現

2. **缺乏時間流動感**
   - 統運入卦只顯示「當前年份」的單一結果，看不到在十二運中的位置
   - 十二運立成表是一次性靜態列表，無法感知「現在走到哪」
   - 流年直卦、變卦納甲等子項散落在不同 `st.markdown` 行中

3. **視覺層級扁平**
   - 運名、卦名、爻名、斷語、策數、入卦年數全部同等字級、同等顏色
   - 重要資訊（當前所處運勢）與次要資訊（歷史驗例、觀象期月令）混在一起
   - 吉凶指標（爻位禍福）只是文字描述，無視覺標記

4. **與主圓盤零互動**
   - 統運入卦的卦象資訊與太乙圓盤 SVG 完全分離
   - 使用者無法從圓盤上看出當前所處運勢對應的宮位或卦象
   - 點擊運勢卡片不會高亮圓盤任何元素

5. **美感差距**
   - 已有的 `grok-card-v2` 設計系統（暗色主題、`rgba(255,255,255,0.03)` 卡片背景、`14px` 圓角）在 side panel 使用良好
   - 但統運區段完全沒有使用這套卡片系統，仍是原生 Streamlit markdown
   - 與 iOS App 的差距：缺乏卦象圖示、吉凶色標、時間軸視覺化

---

## 二、設計方向

### 核心理念

> **「時間軸 + 卡片流」雙層結構**

參考《太乙神數》iOS App 的做法，將十二大運以**橫向時間軸**呈現，當前所處運勢以**高亮卡片**置中展示，未來運勢以**折疊卡片**預覽。流日/流年資訊以**垂直卡片流**在時間軸下方展開。

### 2.1 視覺形式

```
┌─────────────────────────────────────────────────────────┐
│  統運入卦 · 第 N 輪大週                                   │
│  ───────────────────────────────────────────────────    │
│  【十二運時間軸】                                          │
│  ◀  天地否泰  男女交親  三陽晶  四陰毛  資育  造化  ...   │
│       720年    2160年   1152   1008   936   1224        │
│              ▲ 当前                                       │
│  ───────────────────────────────────────────────────    │
│  【當前運勢卡片】（高亮、展開）                              │
│  ┌─────────────────────────────────────────┐            │
│  │  男女交親 · 第7卦 · 既濟 ䷾               │            │
│  │  入卦第 47 年 / 入爻九三第 12 年           │            │
│  │  ┌─────┐  爻位禍福：內極災變之限            │            │
│  │  │ ☵☲  │  陽雖失位，天下亦得安靜            │            │
│  │  │既濟  │                                  │            │
│  │  └─────┘  策數：181  週期序：第2輪           │            │
│  └─────────────────────────────────────────┘            │
│  ───────────────────────────────────────────────────    │
│  【流年直卦】（折疊卡片）                                   │
│  ┌─────────────────────────────────────────┐            │
│  │  甲辰年 · 豐 ䷶ · 九三                    │            │
│  │  命爻法：陽年自下而上                      │            │
│  └─────────────────────────────────────────┘            │
│  【變卦納甲】（折疊卡片）                                   │
│  【卦象觀象】（折疊卡片）                                   │
│  【行支編年 · 歷史驗例】（折疊卡片）                          │
└─────────────────────────────────────────────────────────┘
```

### 2.2 讓使用者快速掌握「當前所處運勢」+ 未來變化

- **時間軸**：12 個運以等比或按年數比例排列的橫向條帶，當前位置以脈動光點標示
- **當前卡片**：自動展開、高亮邊框，顯示完整資訊
- **前後預覽**：時間軸可左右捲動，點擊其他運可展開該運的卦序與年數
- **進度條**：當前運內以細條進度條顯示「已過 X 年 / 總 Y 年」

### 2.3 與主太乙圓盤的視覺關聯

- **圓盤外環標記**：在太乙圓盤 SVG 的外圈加一層「統運環」，以 12 段弧線對應十二運，當前運弧段高亮
- **點擊聯動**：點擊時間軸上的某個運 → 圓盤對應弧段發光 + 旋轉至頂部
- **色碼對應**：每個運分配一個低飽和色（天地否泰=深藍、男女交親=深紫、三陽晶=琥珀等），在時間軸和圓盤外環上保持一致

---

## 三、資訊層級與簡約化

### 3.1 每個運 / 流日顯示的核心資訊（一級）

| 資訊項 | 來源 | 顯示方式 |
|--------|------|----------|
| 運名 | `tongyun_rugua()["運"]` | 16px 粗體，運色 |
| 卦名 + 卦符 | `tongyun_rugua()["卦"]` + `["卦符"]` | 20px 粗體 + Unicode 卦符 |
| 爻名 | `tongyun_rugua()["爻名"]` | 14px 中字 |
| 吉凶指標 | `_YAO_HUOFU[yao_idx]` 的前半段 | 色標圓點 + 簡短標籤 |
| 入卦年數 / 總年數 | `tongyun_rugua()["入卦年數"]` / segment 年數 | 進度條 + 數字 |

### 3.2 二級資訊（卡片內常駐，小字）

| 資訊項 | 來源 |
|--------|------|
| 週期序 | `tongyun_rugua()["週期序"]` |
| 統運積年 | `tongyun_rugua()["統運積年"]` |
| 爻策 | `tongyun_rugua()["爻策"]` |
| 陽/陰爻 | `tongyun_rugua()["陽爻"]` |

### 3.3 三級資訊（點擊展開 / hover tooltip）

| 資訊項 | 來源 | 展開方式 |
|--------|------|----------|
| 爻位禍福全文 | `tongyun_xingyao_huofu()["所主"]` + `["要訣"]` | 卡片內 `<details>` |
| 流年直卦 | `liunian_zhigua()` | 獨立折疊卡片 |
| 變卦納甲 | `tongyun_bian_gua()` | 獨立折疊卡片 |
| 卦象觀象 | `tongyun_gua_xiang()` | 獨立折疊卡片，含六爻觀象列表 |
| 觀象期十二月直事 | `tongyun_guanxiang_qi()` | 獨立折疊卡片，mini timeline |
| 歷史驗例 | `tongyun_lishi()` / `biannian.for_year()` | 獨立折疊卡片 |
| 災厄首尾 | `tongyun_shouwei()` | 吉凶色標 + tooltip |
| 歲本建子 | `suiben_jianzi_weizheng()` | 獨立折疊卡片 |

### 3.4 吉凶指標設計

基於 `_YAO_HUOFU` 的六爻禍福體系：

```
爻 1 → 建功立德  → 黃色 ●  (變動期)
爻 2 → 時正旺安平 → 綠色 ●  (吉)
爻 3 → 內極災變  → 橙色 ●  (凶-輕)
爻 4 → 待治之限  → 橙色 ●  (凶-中)
爻 5 → 君弱臣強  → 紅色 ●  (凶-重)
爻 6 → 外極災變  → 紅色 ●  (凶-極)
```

色標使用 CSS 變數，與暗色主題和諧：
```css
--yun-ji-fu:   #f59e0b;  /* 建功 · 黃 */
--yun-ji-ji:   #22c55e;  /* 安平 · 綠（複用現有 --success） */
--yun-ji-xiong: #ef4444; /* 災變 · 紅（複用現有 --danger） */
--yun-ji-zai:  #dc2626;  /* 外極 · 深紅 */
```

---

## 四、美學與一致性

### 4.1 配色（與現有暗色主題統一）

沿用 `custom_css.py` 已定義的 CSS 變數：
- 背景：`--bg-elevated: #141414` → 卡片底色
- 邊框：`--border-subtle: rgba(255,255,255,0.08)` → 卡片邊框
- 文字：`--text-primary: #fafafa` / `--text-secondary: #d6d6d6` / `--text-muted: #a8a8a8`
- 圓角：`--radius-md: 12px` → 卡片圓角
- 陰影：`inset 0 1px 0 rgba(255,255,255,0.04)` → 卡片內光

新增十二運色系（低飽和、暗色主題適配）：
```css
--yun-1: #3b5998;  /* 天地否泰 · 深藍 */
--yun-2: #6b4c93;  /* 男女交親 · 深紫 */
--yun-3: #b8860b;  /* 三陽晶守 · 琥珀 */
--yun-4: #4a6741;  /* 四陰毛權衡 · 暗綠 */
--yun-5: #8b6f47;  /* 資育還本 · 土褐 */
--yun-6: #5b7c99;  /* 造化符天 · 青灰 */
--yun-7: #c0706c;  /* 剛中健至 · 暗紅 */
--yun-8: #7d6b8d;  /* 羣愚位賢 · 灰紫 */
--yun-9: #5c8a7a;  /* 德義順命 · 青綠 */
--yun-10: #94695a; /* 惑姤留連 · 赭石 */
--yun-11: #6b8299; /* 寡陽相搏 · 鋼藍 */
--yun-12: #8b7355; /* 物極元終 · 古銅 */
```

### 4.2 字體層級

```
運名      : 16px / 600 / --text-primary / 運色左邊框 3px
卦名+卦符 : 22px / 700 / --text-primary / letter-spacing 0.05em
爻名      : 14px / 500 / --text-secondary
斷語(簡)  : 13px / 400 / --text-muted / line-height 1.6
年數/策數 : 12px / 600 / --text-muted / tabular-nums
一級標題  : 11px / 600 / --text-muted / letter-spacing 0.1em / UPPERCASE
展開內容  : 13px / 400 / --text-secondary / line-height 1.65
```

### 4.3 間距與圓角

```
卡片間距    : 0.65rem (與現有 .chart-side-panel gap 一致)
卡片內距    : 0.95rem 1.05rem (與 .grok-card-v2 一致)
時間軸高度  : 48px (bar) + 20px (labels) = 68px
時間軸卡片間: 2px gap
圓角        : 卡片 14px / 時間軸段 6px / 色標圓點 50%
陰影        : 僅當前卡片 box-shadow: 0 0 0 1px var(--yun-color), 0 4px 20px rgba(0,0,0,0.3)
```

### 4.4 卦象圖示

使用 Unicode 易經卦符（U+4DC0–U+4DFF）：
```
乾 ䷀  坤 ䷁  否 ䷋  泰 ䷊  震 ䷲  巽 ䷸  ...
```
- 字級 28px，置於卡片左側
- 配合卦名文字，形成「圖 + 文」雙重識別
- 已有 `gua.get(idx, "")` 可直接取得 Unicode 符號

---

## 五、互動與體驗

### 5.1 點擊運勢卡片的反饋

1. **時間軸**：點擊某運段 → 該段放大 + 運色填充 → 下方卡片切換為該運的詳細資訊
2. **圓盤聯動**：點擊運段 → 圓盤外環對應弧段發光（`filter: drop-shadow`）→ 圓盤旋轉至該運方位
3. **卡片展開**：點擊折疊卡片 → `st.expander` 展開（或 custom `<details>` 動畫）
4. **歷史對照**：點擊歷史驗例 → 彈出該年份的太乙盤對比（利用現有 `historical_compare`）

### 5.2 「目前所在運勢」高亮標示

- **時間軸**：當前運段以運色實心填充 + 上下邊框加粗 + 脈動光點動畫
- **卡片**：當前運卡片左邊框 3px 運色 + 微弱外發光
- **進度條**：卡片底部細條，`已過年數 / 總年數` 百分比，運色填充
- **頁面載入時自動滾動**：時間軸自動將當前運段置中

### 5.3 互動實作策略

Streamlit 的限制下，可分兩階段實作：

**Phase 1（純 Streamlit + CSS，無 JS）**：
- 時間軸用 `st.markdown(unsafe_allow_html=True)` 渲染為 HTML/CSS flexbox
- 當前運段 CSS 高亮（基於 server-side 計算的位置）
- 卡片用 `st.markdown` + `<details>` 折疊
- 點擊運段 → 使用 `st.session_state` + `st.button`（每段一個 button）觸發 server-side 切換

**Phase 2（加入 JS interactivity）**：
- 使用 `streamlit.components.v1.html` 注入自訂 JS
- 時間軸點擊 → `postMessage` 到 Streamlit → `st.session_state` 更新
- 圓盤 SVG 內 element 加 `id` → JS 控制高亮和旋轉

---

## 六、實作建議

### 6.1 新模組結構

```
apps/
  yun_timeline.py     ← 新增：十二運時間軸 HTML 組件
  yun_cards.py        ← 新增：運勢卡片 / 流年卡片 / 卦象卡片
  custom_css.py       ← 擴充：加入 yun-timeline / yun-card CSS
  streamlit_app.py    ← 重構：4284-4420 區段改為調用新模組
```

### 6.2 組件結構（HTML）

#### 十二運時間軸

```html
<div class="yun-timeline-container">
  <div class="yun-timeline-header">
    <span class="yun-timeline-label">統運 · 第 <span class="yun-cycle-num">2</span> 輪大週</span>
    <span class="yun-timeline-sub">11,520 年 / 週期</span>
  </div>
  <div class="yun-timeline-track">
    <!-- 每個運一段，按年數比例計算 flex-grow -->
    <button class="yun-timeline-seg" data-yun-idx="0"
            style="flex-grow: 720; --yun-color: var(--yun-1);">
      <span class="yun-timeline-seg-name">天地否泰</span>
      <span class="yun-timeline-seg-years">720年</span>
    </button>
    <button class="yun-timeline-seg yun-current" data-yun-idx="1"
            style="flex-grow: 2160; --yun-color: var(--yun-2);">
      <span class="yun-timeline-seg-name">男女交親</span>
      <span class="yun-timeline-seg-years">2160年</span>
      <span class="yun-timeline-marker">●</span>
    </button>
    <!-- ... 其餘十運 ... -->
  </div>
  <div class="yun-timeline-progress">
    <div class="yun-timeline-progress-bar" style="width: 62%;">
      <span class="yun-timeline-progress-text">已過 1340 / 2160 年</span>
    </div>
  </div>
</div>
```

#### 當前運勢卡片

```html
<article class="yun-card yun-card--current" style="--yun-color: var(--yun-2);">
  <div class="yun-card-header">
    <span class="yun-card-yun-name">男女交親</span>
    <span class="yun-card-ji-badge yun-ji-xiong">● 內極災變</span>
  </div>
  <div class="yun-card-body">
    <div class="yun-card-gua">
      <span class="yun-card-gua-symbol">䷾</span>
      <span class="yun-card-gua-name">既濟</span>
    </div>
    <div class="yun-card-info">
      <div class="yun-card-yao">九三 · 入爻第 12 年</div>
      <div class="yun-card-meta">
        <span>入卦第 47 年</span>
        <span>策 181</span>
        <span>週期第 2 輪</span>
      </div>
      <div class="yun-card-duan">陽雖失位，天下亦得安靜</div>
    </div>
  </div>
  <div class="yun-card-progress">
    <div class="yun-card-progress-fill" style="width: 62%;"></div>
  </div>
  <details class="yun-card-details">
    <summary>展開爻位禍福全文</summary>
    <p class="yun-card-details-body">
      內極災變之限；陽雖失位，天下亦得安靜。
      初建功、二五安平、三內極、四待治、五君弱、六外極；二五得中為上吉。
    </p>
  </details>
</article>
```

#### 折疊子卡片（流年直卦 / 變卦納甲 / 卦象觀象等）

```html
<details class="yun-sub-card">
  <summary class="yun-sub-card-header">
    <span class="yun-sub-card-title">流年直卦</span>
    <span class="yun-sub-card-preview">甲辰 · 豐 ䷶ · 九三</span>
  </summary>
  <div class="yun-sub-card-body">
    <p>干支：甲辰年</p>
    <p>直卦：豐 ䷶ · 九三爻</p>
    <p>命爻法：陽年自下而上</p>
    <p class="yun-sub-card-note">卦為歲之事，爻為歲之時；變卦為後六月</p>
  </div>
</details>

<details class="yun-sub-card">
  <summary class="yun-sub-card-header">
    <span class="yun-sub-card-title">變卦納甲</span>
    <span class="yun-sub-card-preview">既濟 → 屯</span>
  </summary>
  <div class="yun-sub-card-body">
    <p>本卦 既濟 → 變卦 屯（動爻三）</p>
    <p>納甲：戊辰 · 內卦坎 · 正北</p>
    <p>地支分野：鄭·兗州</p>
  </div>
</details>

<details class="yun-sub-card">
  <summary class="yun-sub-card-header">
    <span class="yun-sub-card-title">卦象觀象</span>
    <span class="yun-sub-card-preview">既濟 · 象曰：水在火上...</span>
  </summary>
  <div class="yun-sub-card-body">
    <p class="yun-gua-xiang">象曰：水在火上，既濟。君子以思患而預防之。</p>
    <p class="yun-gua-yao-current">▶ 入爻觀象（九三）：內極災變，陰陽失位</p>
    <div class="yun-gua-yao-list">
      <div class="yun-gua-yao-item yun-gua-yao-active">初九 · 建功立德之限</div>
      <div class="yun-gua-yao-item yun-gua-yao-active">九二 · 時正旺安平</div>
      <div class="yun-gua-yao-item yun-gua-yao-current">▶ 九三 · 內極災變</div>
      <div class="yun-gua-yao-item">六四 · 待治之限</div>
      <div class="yun-gua-yao-item">九五 · 君弱臣強</div>
      <div class="yun-gua-yao-item">上六 · 外極災變</div>
    </div>
  </div>
</details>
```

### 6.3 CSS 建議

```css
/* ── 十二運時間軸 ──────────────────────────────────── */
.yun-timeline-container {
    margin: 0.5rem 0 1rem;
    padding: 0.85rem 1rem;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
}
.yun-timeline-header {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin-bottom: 0.6rem;
}
.yun-timeline-label {
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--text-secondary);
    letter-spacing: 0.04em;
}
.yun-cycle-num {
    color: var(--text-primary);
    font-weight: 700;
}
.yun-timeline-sub {
    font-size: 0.72rem;
    color: var(--text-muted);
}
.yun-timeline-track {
    display: flex;
    gap: 2px;
    height: 36px;
    border-radius: 6px;
    overflow: hidden;
}
.yun-timeline-seg {
    flex-grow: var(--seg-flex, 100);
    flex-shrink: 0;
    flex-basis: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.03);
    border: none;
    border-top: 2px solid transparent;
    border-bottom: 2px solid transparent;
    cursor: pointer;
    transition: background 0.2s ease, border-color 0.2s ease;
    position: relative;
    overflow: hidden;
    padding: 0;
}
.yun-timeline-seg:hover {
    background: rgba(255, 255, 255, 0.06);
}
.yun-timeline-seg.yun-current {
    background: color-mix(in srgb, var(--yun-color) 18%, transparent);
    border-top-color: var(--yun-color);
    border-bottom-color: var(--yun-color);
}
.yun-timeline-seg-name {
    font-size: 0.68rem;
    font-weight: 600;
    color: var(--text-secondary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100%;
    padding: 0 4px;
}
.yun-timeline-seg.yun-current .yun-timeline-seg-name {
    color: var(--text-primary);
}
.yun-timeline-seg-years {
    font-size: 0.58rem;
    color: var(--text-muted);
    font-variant-numeric: tabular-nums;
}
.yun-timeline-marker {
    position: absolute;
    bottom: -1px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 0.5rem;
    color: var(--yun-color);
    animation: yun-pulse 2s ease-in-out infinite;
}
@keyframes yun-pulse {
    0%, 100% { opacity: 0.6; }
    50% { opacity: 1; text-shadow: 0 0 8px var(--yun-color); }
}

/* ── 當前運勢卡片 ──────────────────────────────────── */
.yun-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--border-subtle);
    border-left: 3px solid var(--yun-color, var(--text-muted));
    border-radius: 14px;
    padding: 0.95rem 1.05rem;
    margin-bottom: 0.65rem;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.yun-card--current {
    box-shadow: 0 0 0 1px color-mix(in srgb, var(--yun-color) 30%, transparent),
                0 4px 20px rgba(0, 0, 0, 0.3);
}
.yun-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.7rem;
}
.yun-card-yun-name {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
}
.yun-card-ji-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    font-size: 0.72rem;
    font-weight: 500;
    padding: 0.15rem 0.5rem;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.04);
}
.yun-ji-fu  { color: #f59e0b; }
.yun-ji-ji  { color: var(--success); }
.yun-ji-xiong { color: var(--danger); }
.yun-ji-zai { color: #dc2626; }

.yun-card-body {
    display: flex;
    gap: 1rem;
    align-items: flex-start;
}
.yun-card-gua {
    display: flex;
    flex-direction: column;
    align-items: center;
    min-width: 3.5rem;
}
.yun-card-gua-symbol {
    font-size: 1.75rem;
    line-height: 1;
    color: var(--text-primary);
    margin-bottom: 0.2rem;
}
.yun-card-gua-name {
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--text-secondary);
}
.yun-card-info {
    flex: 1;
    min-width: 0;
}
.yun-card-yao {
    font-size: 0.88rem;
    font-weight: 500;
    color: var(--text-primary);
    margin-bottom: 0.3rem;
}
.yun-card-meta {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    font-size: 0.72rem;
    color: var(--text-muted);
    font-variant-numeric: tabular-nums;
    margin-bottom: 0.35rem;
}
.yun-card-duan {
    font-size: 0.8rem;
    color: var(--text-secondary);
    line-height: 1.5;
}
.yun-card-progress {
    height: 3px;
    background: rgba(255, 255, 255, 0.06);
    border-radius: 999px;
    margin: 0.7rem 0 0;
    overflow: hidden;
}
.yun-card-progress-fill {
    height: 100%;
    background: var(--yun-color);
    border-radius: 999px;
    transition: width 0.4s ease;
}
.yun-card-details {
    margin-top: 0.6rem;
    font-size: 0.78rem;
}
.yun-card-details summary {
    color: var(--text-muted);
    cursor: pointer;
    user-select: none;
    list-style: none;
}
.yun-card-details summary::-webkit-details-marker { display: none; }
.yun-card-details-body {
    color: var(--text-secondary);
    line-height: 1.65;
    margin: 0.35rem 0 0;
}

/* ── 折疊子卡片 ──────────────────────────────────── */
.yun-sub-card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid var(--border-subtle);
    border-radius: 10px;
    margin-bottom: 0.4rem;
    overflow: hidden;
}
.yun-sub-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.55rem 0.85rem;
    cursor: pointer;
    user-select: none;
    list-style: none;
    transition: background 0.15s ease;
}
.yun-sub-card-header:hover {
    background: rgba(255, 255, 255, 0.03);
}
.yun-sub-card-header::-webkit-details-marker { display: none; }
.yun-sub-card-title {
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--text-secondary);
    letter-spacing: 0.02em;
}
.yun-sub-card-preview {
    font-size: 0.74rem;
    color: var(--text-muted);
    font-variant-numeric: tabular-nums;
}
.yun-sub-card-body {
    padding: 0 0.85rem 0.65rem;
    font-size: 0.78rem;
    color: var(--text-secondary);
    line-height: 1.6;
}
.yun-sub-card-note {
    color: var(--text-muted) !important;
    font-size: 0.72rem !important;
    margin-top: 0.3rem;
}

/* ── 卦象觀象六爻列表 ──────────────────────────────── */
.yun-gua-yao-list {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    margin-top: 0.5rem;
}
.yun-gua-yao-item {
    padding: 0.35rem 0.55rem;
    font-size: 0.76rem;
    color: var(--text-muted);
    background: rgba(255, 255, 255, 0.02);
    border-radius: 6px;
    border-left: 2px solid transparent;
}
.yun-gua-yao-item.yun-gua-yao-active {
    color: var(--text-secondary);
}
.yun-gua-yao-item.yun-gua-yao-current {
    color: var(--text-primary);
    font-weight: 600;
    background: rgba(255, 255, 255, 0.05);
    border-left-color: var(--yun-color, var(--text-primary));
}

/* ── 響應式 ──────────────────────────────────── */
@media (max-width: 768px) {
    .yun-timeline-track { height: 44px; }
    .yun-timeline-seg-name { font-size: 0.6rem; }
    .yun-card-body { flex-direction: column; align-items: center; text-align: center; }
    .yun-card-gua { flex-direction: row; gap: 0.5rem; }
    .yun-card-info { text-align: center; }
    .yun-card-meta { justify-content: center; }
}
```

### 6.4 Python 實作骨架

#### `apps/yun_timeline.py`

```python
"""十二運時間軸 + 運勢卡片 HTML 組件。"""
from __future__ import annotations
from html import escape
from kintaiyi import config

_YUN_COLORS = [
    "--yun-1",  "--yun-2",  "--yun-3",  "--yun-4",
    "--yun-5",  "--yun-6",  "--yun-7",  "--yun-8",
    "--yun-9",  "--yun-10", "--yun-11", "--yun-12",
]

_JI_BADGE = {
    1: ("yun-ji-fu",   "建功立德"),
    2: ("yun-ji-ji",   "安平之限"),
    3: ("yun-ji-xiong", "內極災變"),
    4: ("yun-ji-xiong", "待治之限"),
    5: ("yun-ji-zai",  "君弱臣強"),
    6: ("yun-ji-zai",  "外極災變"),
}


def _locate_current_yun_idx(rugua: dict) -> int:
    """找出當前運在 _TONGYUN_YUN_DEF 中的索引。"""
    for i, (yun, *_rest) in enumerate(config._TONGYUN_YUN_DEF):
        if yun == rugua.get("運"):
            return i
    return 1  # 男女交親是最常見的


def render_yun_timeline(rugua: dict, shier_yun: dict, *, t) -> str:
    """渲染十二運時間軸 HTML。"""
    current_idx = _locate_current_yun_idx(rugua)
    twelve = shier_yun.get("十二運", [])
    
    segs_html = []
    for i, row in enumerate(twelve):
        is_current = i == current_idx
        css_var = _YUN_COLORS[i] if i < len(_YUN_COLORS) else "--yun-2"
        flex = row.get("總年", 100)
        classes = "yun-timeline-seg"
        if is_current:
            classes += " yun-current"
        name = escape(row.get("運", ""))
        years = row.get("總年", 0)
        marker = '<span class="yun-timeline-marker">●</span>' if is_current else ""
        segs_html.append(
            f'<button class="{classes}" data-yun-idx="{i}" '
            f'style="flex-grow: {flex}; --yun-color: var({css_var});">'
            f'<span class="yun-timeline-seg-name">{name}</span>'
            f'<span class="yun-timeline-seg-years">{years}年</span>'
            f'{marker}</button>'
        )
    
    # 進度條
    current_row = twelve[current_idx] if current_idx < len(twelve) else {}
    total = current_row.get("總年", 1)
    # 計算在當前運內的進度（基於 segment 中的位置）
    pos = rugua.get("週期位置", 0)
    seg = config._TONGYUN_SEGMENTS[0]
    for s in config._TONGYUN_SEGMENTS:
        if s["週期起"] <= pos < s["週期迄"]:
            seg = s
            break
    elapsed = pos - seg["週期起"]
    pct = min(100, int(elapsed / max(1, seg["年數"]) * 100))
    
    return f'''
    <div class="yun-timeline-container">
      <div class="yun-timeline-header">
        <span class="yun-timeline-label">統運 · 第 
          <span class="yun-cycle-num">{rugua.get("週期序", "—")}</span> 輪大週
        </span>
        <span class="yun-timeline-sub">{shier_yun.get("大週", 11520)} 年 / 週期</span>
      </div>
      <div class="yun-timeline-track">
        {"".join(segs_html)}
      </div>
      <div class="yun-timeline-progress">
        <div class="yun-timeline-progress-bar" style="width: {pct}%;">
          <span class="yun-timeline-progress-text">已過 {elapsed} / {seg["年數"]} 年</span>
        </div>
      </div>
    </div>
    '''


def render_yun_current_card(rugua: dict, huofu: dict, *, t) -> str:
    """渲染當前運勢卡片 HTML。"""
    current_idx = _locate_current_yun_idx(rugua)
    css_var = _YUN_COLORS[current_idx] if current_idx < len(_YUN_COLORS) else "--yun-2"
    yao_idx = rugua.get("爻", 1)
    ji_class, ji_label = _JI_BADGE.get(yao_idx, ("yun-ji-fu", "—"))
    gua_name = escape(rugua.get("卦", "—"))
    gua_symbol = escape(rugua.get("卦符", ""))
    yao_name = escape(rugua.get("爻名", ""))
    ru_gua_year = rugua.get("入卦年數", "—")
    ru_yao_year = rugua.get("入爻年數", "—")
    ce = rugua.get("爻策", "—")
    zhou = rugua.get("週期序", "—")
    duan_short = (huofu.get("所主") or rugua.get("斷語", "") or "").split("；")[0]
    duan_full = huofu.get("所主", "") + "。" + (huofu.get("要訣", "") or "")
    
    # 進度
    pos = rugua.get("週期位置", 0)
    seg = config._TONGYUN_SEGMENTS[0]
    for s in config._TONGYUN_SEGMENTS:
        if s["週期起"] <= pos < s["週期迄"]:
            seg = s
            break
    elapsed = pos - seg["週期起"]
    pct = min(100, int(elapsed / max(1, seg["年數"]) * 100))
    
    return f'''
    <article class="yun-card yun-card--current" style="--yun-color: var({css_var});">
      <div class="yun-card-header">
        <span class="yun-card-yun-name">{escape(rugua.get("運", "—"))}</span>
        <span class="yun-card-ji-badge {ji_class}">● {ji_label}</span>
      </div>
      <div class="yun-card-body">
        <div class="yun-card-gua">
          <span class="yun-card-gua-symbol">{gua_symbol}</span>
          <span class="yun-card-gua-name">{gua_name}</span>
        </div>
        <div class="yun-card-info">
          <div class="yun-card-yao">{yao_name} · 入爻第 {ru_yao_year} 年</div>
          <div class="yun-card-meta">
            <span>入卦第 {ru_gua_year} 年</span>
            <span>策 {ce}</span>
            <span>週期第 {zhou} 輪</span>
          </div>
          <div class="yun-card-duan">{escape(duan_short)}</div>
        </div>
      </div>
      <div class="yun-card-progress">
        <div class="yun-card-progress-fill" style="width: {pct}%;"></div>
      </div>
      <details class="yun-card-details">
        <summary>展開爻位禍福全文</summary>
        <p class="yun-card-details-body">{escape(duan_full)}</p>
      </details>
    </article>
    '''


def render_yun_sub_cards(
    v12: dict, v13: dict, v14: dict, rugua: dict, *, t
) -> str:
    """渲染流年直卦、變卦納甲、卦象觀象等折疊子卡片。"""
    cards = []
    
    # 流年直卦
    lz = v12.get("流年直卦") or {}
    if lz.get("直卦"):
        gz = escape(lz.get("干支", ""))
        gua = escape(lz.get("直卦", ""))
        sym = escape(lz.get("卦符", ""))
        yao = escape(lz.get("爻名", ""))
        cards.append(f'''
        <details class="yun-sub-card">
          <summary class="yun-sub-card-header">
            <span class="yun-sub-card-title">{t("liunian_zhigua")}</span>
            <span class="yun-sub-card-preview">{gz} · {gua} {sym} · {yao}</span>
          </summary>
          <div class="yun-sub-card-body">
            <p>干支：{gz}年</p>
            <p>直卦：{gua} {sym} · {yao}爻</p>
            <p>命爻法：{escape(lz.get("命爻法", ""))}</p>
            <p class="yun-sub-card-note">{escape(lz.get("要訣", ""))}</p>
          </div>
        </details>
        ''')
    
    # 變卦納甲
    bg = v12.get("變卦納甲") or {}
    if bg.get("變卦"):
        nj = bg.get("納甲", {})
        cards.append(f'''
        <details class="yun-sub-card">
          <summary class="yun-sub-card-header">
            <span class="yun-sub-card-title">{t("bian_gua_najia")}</span>
            <span class="yun-sub-card-preview">
              {escape(bg.get("本卦", ""))} → {escape(bg.get("變卦", ""))}
            </span>
          </summary>
          <div class="yun-sub-card-body">
            <p>本卦 {escape(bg.get("本卦", ""))} → 變卦 {escape(bg.get("變卦", ""))}
               （動爻{escape(bg.get("爻名", ""))}）</p>
            <p>納甲：{escape(nj.get("納甲", ""))} · 
               {escape(nj.get("內外", ""))} · {escape(nj.get("八卦", ""))}</p>
            <p>方位：{escape(nj.get("方位", ""))}；
               地支分野：{escape(nj.get("地支分野", ""))}</p>
          </div>
        </details>
        ''')
    
    # 卦象觀象
    gx = v13.get("統運卦象") or {}
    full = v13.get("卦象全文") or {}
    if gx.get("卦"):
        xiang = (gx.get("象曰", "") or "")[:48]
        yao_obs = gx.get("當前爻觀象", "")
        yao_list_html = ""
        yao_observations = full.get("爻觀象", {}) or {}
        current_yao = gx.get("爻", 0)
        for yi in sorted(yao_observations.keys()):
            cls = "yun-gua-yao-item"
            if yi == current_yao:
                cls += " yun-gua-yao-current"
            elif yi <= current_yao:
                cls += " yun-gua-yao-active"
            yao_list_html += (
                f'<div class="{cls}">第{yi}爻 · '
                f'{escape(yao_observations[yi])}</div>'
            )
        cards.append(f'''
        <details class="yun-sub-card">
          <summary class="yun-sub-card-header">
            <span class="yun-sub-card-title">{t("gua_xiang")}</span>
            <span class="yun-sub-card-preview">
              {escape(gx.get("卦", ""))} · {escape(xiang)}…
            </span>
          </summary>
          <div class="yun-sub-card-body">
            <p class="yun-gua-xiang">象曰：{escape(gx.get("象曰", ""))}</p>
            <p class="yun-gua-yao-current">▶ 入爻觀象（{escape(gx.get("爻名", ""))}）：
               {escape(yao_obs)}</p>
            <div class="yun-gua-yao-list">{yao_list_html}</div>
          </div>
        </details>
        ''')
    
    # 行支編年
    hz = v14.get("行支編年", {}) or {}
    exact = hz.get("當年例", []) or []
    if exact:
        e = exact[0]
        cards.append(f'''
        <details class="yun-sub-card">
          <summary class="yun-sub-card-header">
            <span class="yun-sub-card-title">{t("hangzhi_biannian")}</span>
            <span class="yun-sub-card-preview">
              {escape(e.get("紀年", ""))} · {escape(e.get("卦", ""))}{escape(e.get("爻", ""))}
            </span>
          </summary>
          <div class="yun-sub-card-body">
            <p>{escape(e.get("紀年", ""))}（{escape(str(e.get("年", "")))}年）</p>
            <p>{escape(e.get("運", ""))}·{escape(e.get("卦", ""))}{escape(e.get("爻", ""))}</p>
            <p>{escape(e.get("摘要", ""))}</p>
          </div>
        </details>
        ''')
    
    # 災厄首尾
    sw = v12.get("災厄首尾") or {}
    if sw.get("是否首尾") or sw.get("首尾標記"):
        flags = "、".join(sw.get("首尾標記", []))
        cards.append(f'''
        <details class="yun-sub-card">
          <summary class="yun-sub-card-header">
            <span class="yun-sub-card-title">{t("shouwei")}</span>
            <span class="yun-sub-card-preview">{escape(flags)}</span>
          </summary>
          <div class="yun-sub-card-body">
            <p>{escape(sw.get("斷語", ""))}</p>
            <p class="yun-sub-card-note">{escape(sw.get("要訣", ""))}</p>
          </div>
        </details>
        ''')
    
    return "".join(cards)
```

### 6.5 在 `streamlit_app.py` 中的整合方式

將 `streamlit_app.py:4284-4420` 的整段卷十二～十四渲染邏輯替換為：

```python
# —— 卷十二～十四：統運入卦 / 卦象 / 編年 ——
from yun_timeline import (
    render_yun_timeline,
    render_yun_current_card,
    render_yun_sub_cards,
)

_ttext = _display_ttext(results)
_chart_ty = results["ty"]
_tongyun_qy = _resolve_tongyun_year(_chart_ty.year)

if _tongyun_qy != _chart_ty.year:
    st.info(t("tongyun_query_note").format(
        query=_tongyun_qy, chart=_chart_ty.year,
    ))

_v12 = _ttext.get("卷十二", {})
_v13 = _ttext.get("卷十三", {})
_v14 = _ttext.get("卷十四", {})

_rg = _v12.get("統運入卦", {})
_hf = _v12.get("入爻禍福", {})
_sy = _v12.get("十二運立成", {})

if _rg:
    # 時間軸 + 當前卡片 + 子卡片
    st.markdown(
        render_yun_timeline(_rg, _sy, t=t),
        unsafe_allow_html=True,
    )
    st.markdown(
        render_yun_current_card(_rg, _hf, t=t),
        unsafe_allow_html=True,
    )
    st.markdown(
        render_yun_sub_cards(_v12, _v13, _v14, _rg, t=t),
        unsafe_allow_html=True,
    )

# 歷史對照（保留原有 expander）
_render_tongyun_history_compare(_tongyun_qy)
```

### 6.6 圓盤聯動（Phase 2）

在 `chart_view.py` 的 SVG 生成函數中，為太乙圓盤外環加入一層統運環：

```python
def build_yun_ring_svg(rugua: dict, radius: float) -> str:
    """在圓盤最外圈加十二運弧段環。"""
    segs = config._TONGYUN_SEGMENTS
    current_pos = rugua.get("週期位置", 0)
    total = config._TONGYUN_CYCLE
    paths = []
    for i, seg in enumerate(segs):
        start_angle = (seg["週期起"] / total) * 360 - 90  # -90 = top
        end_angle = (seg["週期迄"] / total) * 360 - 90
        is_current = seg["週期起"] <= current_pos < seg["週期迄"]
        opacity = "0.8" if is_current else "0.25"
        color = f"var(--yun-{i+1})"
        # SVG arc path...
        paths.append(f'<path d="..." fill="{color}" opacity="{opacity}" '
                     f'class="yun-ring-seg{" yun-ring-current" if is_current else ""}" '
                     f'data-yun-idx="{i}"/>')
    return "".join(paths)
```

JS 點擊聯動：
```javascript
// 點擊時間軸段 → 高亮圓盤對應弧段
document.querySelectorAll('.yun-timeline-seg').forEach(btn => {
  btn.addEventListener('click', () => {
    const idx = btn.dataset.yunIdx;
    // 移除所有高亮
    document.querySelectorAll('.yun-ring-seg').forEach(s => s.classList.remove('yun-ring-current'));
    // 高亮對應弧段
    const seg = document.querySelector(`.yun-ring-seg[data-yun-idx="${idx}"]`);
    if (seg) seg.classList.add('yun-ring-current');
  });
});
```

---

## 七、遷移策略

### Phase 1（可立即實作，不改現有邏輯）
1. 新增 `apps/yun_timeline.py` — 時間軸 + 卡片 HTML 生成
2. 擴充 `apps/custom_css.py` — 加入 `.yun-*` CSS
3. 重構 `streamlit_app.py:4284-4420` — 替換為新組件調用
4. 保持 `st.expander` 歷史對照不變
5. 不改動圓盤 SVG

### Phase 2（圓盤聯動，需要 SVG 修改）
1. 在 `chart_view.py` 中加入 `build_yun_ring_svg()`
2. 在 `streamlit_app.py` 的 `render_svg` / `render_svg1` 中注入統運環
3. 加入 JS 點擊聯動邏輯

### Phase 3（完整互動，需要 Streamlit component）
1. 將時間軸改為 `streamlit.components.v1.html` 自訂元件
2. 支援點擊運段 → `streamlit.setComponentValue` → `st.session_state` 切換
3. 圓盤旋轉動畫至選中運的方位

---

## 八、與 iOS App《太乙神數》的對標

| 特性 | iOS App | 本方案 | 優勢 |
|------|---------|--------|------|
| 十二運呈現 | 靜態列表 + 當前高亮 | 按年數比例的時間軸 + 高亮 | 更直觀的時間流動感 |
| 當前運卡片 | 卡片 + 卦象圖 | 卡片 + Unicode 卦符 + 吉凶色標 + 進度條 | 資訊更豐富但仍簡約 |
| 卦象觀象 | 點擊展開 | `<details>` 折疊 + 六爻列表高亮當前爻 | 同等體驗 |
| 歷史驗例 | 列表 | 折疊卡片 + 歷史對照 expander | 保留原有功能 |
| 吉凶指標 | 文字 | 色標圓點 + 標籤 | 更快速識別 |
| 與盤面聯動 | 有 | Phase 2 實現 | 可達同等水準 |
| 整體美感 | 簡約、有層次 | 暗色主題 + 運色系 + 卡片層級 | 更符合 web 美學 |