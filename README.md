<div align="center">

# 🌟 Python 太乙神數 | Kintaiyi 堅太乙

### 自古君王官臣珍重、上測天文下測國運必用之法 — 最豐富的開源太乙神數排盤工具

*The most authentic open-source Taiyi Shenshu (太乙神數) divination engine in Python*

[![PyPI version](https://img.shields.io/pypi/v/kintaiyi?color=blue&label=PyPI)](https://pypi.org/project/kintaiyi/)
[![Python](https://img.shields.io/pypi/pyversions/kintaiyi?label=Python)](https://pypi.org/project/kintaiyi/)
[![Downloads](https://img.shields.io/pypi/dm/kintaiyi?color=green&label=Downloads)](https://pypi.org/project/kintaiyi/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/kentang2017/kintaiyi?style=social)](https://github.com/kentang2017/kintaiyi)
[![Telegram](https://img.shields.io/badge/Telegram-Channel-blue?logo=telegram)](https://t.me/numerology_coding)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg?logo=paypal&style=flat-square)](https://www.paypal.me/kinyeah)

<br/>

[🚀 **立即在線體驗 Live Demo**](https://kintaiyi.streamlitapp.com) &nbsp;|&nbsp; [🎬 **YouTube 介紹**](https://www.youtube.com/watch?v=FKnPu8FOIlc) &nbsp;|&nbsp; [📦 **PyPI**](https://pypi.org/project/kintaiyi/) &nbsp;|&nbsp; [📖 **Wiki**](https://github.com/kentang2017/kintaiyi/wiki)

<br/>

![太乙神數盤圖](https://github.com/kentang2017/kintaiyi/blob/master/pic/Untitled-1.png?raw=true)

[![YouTube 影片演示](https://github.com/user-attachments/assets/84e345b2-29c9-407d-a2de-808ed407d5b5)](https://www.youtube.com/watch?v=FKnPu8FOIlc)

</div>

---

## ✨ 亮點 Highlights

- 🔮 **六種計法齊備** — 年計、月計、日計、時計、分計、命法，覆蓋所有太乙推算場景
- 📜 **四大古法並存** — 太乙統宗、太乙金鏡、太乙淘金歌、太乙局，正宗古法不簡化
- 📊 **輸出內容豐富** — 干支、局式、神煞、二十八宿、八門、八宮旺衰、兵陣預測、歷史年號對應
- 🏯 **歷史年號對照** — 內建完整中國歷代紀年與農曆換算
- 🖥️ **多種使用方式** — Python API + Typer CLI + Streamlit 圖形介面，各取所需
- 🤖 **AI 智能分析** — 整合 Cerebras AI，可自動解讀盤面

---

## 📖 簡介 Introduction

**太乙神數**，與奇門遁甲、大六壬合稱「三式」，是中國古代最高層次的術數體系之一，專門用於推算天時國運與歷史變化規律。其法源於《易緯·乾鑿度》太乙行九宮法，相傳始於黃帝戰蚩尤之時，延續至今三千餘年。

**Kintaiyi 堅太乙**，取「堅守古法」之意。本套件嚴格依照古籍記載實現演算法，不做簡化、不作省略，旨在為太乙神數的研究者與愛好者提供一套**可驗證、可復現**的開源工具。無論是年運推算、國事預測，還是個人命理，皆可一鍵排盤。

> **Tai Yi Shen Shu** is one of the "Three Styles" (三式) of ancient Chinese divination, alongside Qi Men Dun Jia and Da Liu Ren. This open-source library faithfully implements the classical algorithms without simplification, enabling researchers and enthusiasts to study, verify, and apply this millennia-old wisdom with modern tools.

---

## 🚀 快速開始 Quick Start

### 安裝 Installation

```bash
pip install kintaiyi
```

選裝 CLI 或 Web 界面（Optional extras）：

```bash
pip install kintaiyi[cli]       # 命令列工具 (Typer CLI)
pip install kintaiyi[app]       # Streamlit 圖形介面
pip install kintaiyi[cli,app]   # 全部安裝
```

### Python 程式碼範例

```python
from kintaiyi.kintaiyi import Taiyi

# 排一個年計太乙盤 (Calculate a yearly Taiyi board)
result = Taiyi(2026, 3, 24, 12, 30).pan(ji_style=0, method=1)
print(result["太乙計"])       # → 年計
print(result["局式"])         # → {'文': '陽遁...', '數': ..., ...}
print(result["二十八宿值日"])  # → 二十八宿值日星
print(result["推主客相闗法"])  # → 主客勝負判斷
```

### CLI 命令列範例

```bash
# 年計排盤
kintaiyi calculate --date 2026-03-24 --time 12:30 --mode year --method 1

# 日計排盤，輸出 JSON
kintaiyi calculate --date 2026-03-24 --time 12:30 --mode day --output json

# 命法推算
kintaiyi calculate --date 1990-05-15 --time 08:00 --mode life --sex male
```

### Streamlit 一鍵啟動

```bash
pip install kintaiyi[app]
streamlit run app.py
```

---

## 📋 支援功能 Features

### 計法模式 Calculation Modes

| 模式 Mode | ji_style | 說明 Description |
|-----------|----------|-----------------|
| 年計 Year | `0` | 推算年運、國運大勢 |
| 月計 Month | `1` | 推算月份氣運吉凶 |
| 日計 Day | `2` | 推算日課吉凶 |
| 時計 Hour | `3` | 推算時辰吉凶 |
| 分計 Minute | `4` | 現代延伸，精確至分鐘 |
| 命法 Life | `5` | 個人命理推算 |

### 古法公式 Taiyi Methods

| 方法 Method | method | 來源 Source |
|------------|--------|------------|
| 太乙統宗 | `0` | 《太乙統宗寶鑑》 |
| 太乙金鏡 | `1` | 《太乙金鏡式經》 |
| 太乙淘金歌 | `2` | 《太乙淘金歌》 |
| 太乙局 | `3` | 《太乙局》 |

### 輸出內容 Output Fields

盤面輸出涵蓋以下資訊（Output includes but is not limited to）：

- **基本資訊** — 公元日期、農曆、干支五柱、歷史年號
- **局式** — 陰陽遁、局數、積年數、紀元
- **太乙諸神** — 太乙、天乙、地乙、四神、直符、文昌、計神、合神
- **主客算** — 主算、客算、定算，含三才數與格局判斷
- **八門八宮** — 八門值事與分佈、八宮旺衰
- **二十八宿** — 值日宿、太歲宿、始擊宿及斷事
- **兵陣預測** — 推主客相關法、飛鳥助戰法、風雲諸法
- **七大兵法** — 雷公入水、臨津問道、獅子反擲、白雲捲空、猛虎相拒、白龍得雲、回軍無言

---

## 🖼️ 截圖與演示 Screenshots & Demo

### 線上演示 Live Demo

👉 [**https://kintaiyi.streamlitapp.com**](https://kintaiyi.streamlitapp.com)

> 📌 大陸用戶可能需要使用 VPN 訪問 *(Mainland China users may need a VPN)*

### 盤圖預覽 Board Preview

<div align="center">

![太乙九宮分野圖](https://github.com/kentang2017/kintaiyi/blob/master/pic/%E5%A4%AA%E4%B9%99%E4%B9%9D%E5%AE%AE%E5%88%86%E9%87%8E%E5%9C%96.jpg?raw=true)

*太乙九宮分野圖 — Taiyi Nine Palace Sector Diagram*

</div>

---

## 📦 安裝 Installation

### 環境要求 Requirements

- Python ≥ 3.10

### 基本安裝

```bash
pip install kintaiyi
```

### 可選依賴 Optional Extras

```bash
# CLI 命令列工具（基於 Typer）
pip install kintaiyi[cli]

# Streamlit 圖形介面（完整 Web 應用）
pip install kintaiyi[app]

# Flask Web 後端
pip install kintaiyi[web]

# 開發環境（pytest + ruff）
pip install kintaiyi[dev]
```

### 從源碼安裝 Install from Source

```bash
git clone https://github.com/kentang2017/kintaiyi.git
cd kintaiyi
pip install -e ".[cli,app,dev]"
```

---

## 🔧 進階使用 Advanced Usage

### CLI 完整參數 CLI Options

```
kintaiyi calculate [OPTIONS]
```

| 參數 Option | 縮寫 | 說明 Description | 預設值 Default |
|-------------|------|-----------------|---------------|
| `--year` | `-y` | 公元年 Year | 當前年份 |
| `--month` | `-m` | 月 Month | 當前月份 |
| `--day` | `-d` | 日 Day | 當前日期 |
| `--hour` | `-H` | 時 Hour (0-23) | 當前小時 |
| `--minute` | `-M` | 分 Minute (0-59) | 當前分鐘 |
| `--date` | | 日期 YYYY-MM-DD | — |
| `--time` | | 時間 HH:MM | — |
| `--mode` | | 計法模式 | `year` |
| `--method` | | 古法公式 (0-3) | `0` |
| `--output` | `-o` | 輸出格式 (text/json/markdown) | `text` |
| `--sex` | `-s` | 性別（命法時必填：male/female） | — |

```bash
# 查看版本
kintaiyi version

# 使用個別參數
kintaiyi calculate --year 1552 --month 9 --day 24 --hour 0 --minute 0 --mode year --method 1

# 使用日期字串 + JSON 輸出
kintaiyi calculate --date 2026-03-24 --time 12:30 --mode day --output json

# Markdown 表格輸出
kintaiyi calculate --date 2026-03-24 --time 12:30 --mode hour --output markdown
```

### Python API

```python
from kintaiyi.kintaiyi import Taiyi

# 建立太乙物件
taiyi = Taiyi(year=2026, month=3, day=24, hour=12, minute=30)

# 排盤 — ji_style: 0=年計, 1=月計, 2=日計, 3=時計, 4=分計
#        method:   0=統宗, 1=金鏡, 2=淘金歌, 3=太乙局
result = taiyi.pan(ji_style=0, method=1)

# 命法推算 (Python API 使用中文 "男"/"女"；CLI 使用 male/female)
life_result = taiyi.taiyi_life(sex="男")  # "男" or "女"

# 結果為 dict，可直接轉 JSON
import json
print(json.dumps(result, ensure_ascii=False, indent=2))
```

### 輸出範例 Sample Output

```python
from kintaiyi.kintaiyi import Taiyi

result = Taiyi(1552, 9, 24, 0, 0).pan(ji_style=0, method=1)

# result 為 dict，包含：
# {
#   "太乙計": "年計",
#   "太乙公式類別": "太乙金鏡",
#   "公元日期": "1552年9月24日0時",
#   "干支": ["壬子", "庚戌", "丙戌", "戊子", "甲子"],
#   "農曆": {"年": 1552, "月": 9, "日": 7},
#   "年號": "明世宗朱厚熜 嘉靖三十一年",
#   "局式": {"文": "陽遁十三局", "數": 13, ...},
#   "太乙落宮": 6,
#   "太乙": "兌",
#   "二十八宿值日": "翼",
#   "推主客相闗法": "主尅客，主勝",
#   ...
# }
```

---

## 🤝 貢獻指南 Contributing

我們歡迎所有形式的貢獻！*All contributions are welcome!*

- 🐛 **Bug 回報** — 提交 [Issue](https://github.com/kentang2017/kintaiyi/issues)
- ✨ **新功能** — 歡迎 PR 添加新古法、新計法
- 📚 **課例驗證** — 提供歷史課例以驗證演算法準確性
- 🌐 **翻譯** — 協助翻譯文檔或術語
- ⭐ **Star** — 最簡單的支持方式！

### 開發環境設置

```bash
git clone https://github.com/kentang2017/kintaiyi.git
cd kintaiyi
pip install -e ".[dev]"

# 運行測試
pytest

# 代碼格式化
ruff check src/ --fix
ruff format src/
```

---

## 💬 聯絡與社群 Contact & Community

| 渠道 Channel | 連結 Link |
|-------------|----------|
| 📢 Telegram 頻道 | [numerology_coding](https://t.me/numerology_coding) |
| 💬 Telegram 私訊 | [haizhonggum](https://t.me/haizhonggum) |
| 🐛 GitHub Issues | [提交問題](https://github.com/kentang2017/kintaiyi/issues) |
| 💰 PayPal 捐助 | [paypal.me/kinyeah](https://www.paypal.me/kinyeah) |

### 微信公眾號 WeChat Official Account

<div align="center">

![微信公眾號](https://raw.githubusercontent.com/kentang2017/kinliuren/refs/heads/master/pic/%E5%9C%96%E7%89%87_20260316084147.jpg)

</div>

---

<div align="center">

### ⭐ 喜歡這個專案？請給個 Star 支持！

### *Enjoying Kintaiyi? Give us a ⭐ on GitHub!*

[![Star this repo](https://img.shields.io/github/stars/kentang2017/kintaiyi?style=social)](https://github.com/kentang2017/kintaiyi)

</div>

---

## 📄 License

本專案採用 [MIT License](https://opensource.org/licenses/MIT) 開源協議。

This project is licensed under the MIT License.

---

## 🔗 相關專案 Related Projects

| 專案 Project | 說明 Description | 連結 Link |
|-------------|-----------------|----------|
| 🔮 **堅奇門 kinqimen** | Python 奇門遁甲排盤 — Qi Men Dun Jia | [GitHub](https://github.com/kentang2017/kinqimen) |
| 🎴 **堅六壬 kinliuren** | Python 大六壬排盤 — Da Liu Ren | [GitHub](https://github.com/kentang2017/kinliuren) |

> 三式齊備，古法傳承 — *The Three Styles of Chinese divination, all open-sourced.*
