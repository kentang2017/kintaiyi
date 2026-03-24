# Web Interface

Kintaiyi includes a full-featured web interface built with [Streamlit](https://streamlit.io/), providing an interactive graphical experience for Taiyi board calculation.

## Live Demo

Try Kintaiyi online without installing anything:

👉 **[https://kintaiyi.streamlitapp.com](https://kintaiyi.streamlitapp.com)**

> 📌 Mainland China users may need a VPN to access the Streamlit Cloud deployment.

## Running Locally

### Installation

```bash
pip install kintaiyi[app]
```

### Launch

```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`.

## Features

### 🌐 Bilingual Interface

The web interface supports both **Chinese (中文)** and **English** languages. Toggle between languages using the language selector in the sidebar.

### 📅 Date & Time Input

- Enter any date and time in the sidebar
- Supports dates before the Common Era
- Click "即時盤" (Instant Board) to use the current date and time

### 🔮 Calculation Options

- Select from all six calculation modes (Year, Month, Day, Hour, Minute, Life)
- Choose from the four ancient methods (Orthodox, Gold Mirror, Gold Panning Song, Taiyi Bureau)
- Life divination mode with male/female selection

### 📊 Board Visualization

The web interface renders a visual Taiyi board as an SVG diagram, showing:
- Nine Palace layout with deity positions
- Eight Gates distribution
- 28 Mansions information
- Seven Luminaries (七曜) on the outer ring
- Color-coded zones based on five elements (五行)

### 🤖 AI Board Interpretation

The web interface integrates **Cerebras AI** for automatic board analysis. The AI can interpret the board pattern and provide insights based on the classical Taiyi principles.

### 📚 Built-in Documentation

The web interface includes several documentation tabs:
- **使用方法** (Instructions) — How to use the software
- **經典課例** (Historical Examples) — 82+ verified historical cases
- **地震水災** (Disasters) — Historical earthquake and flood correlation data
- **古籍書目** (Bibliography) — 99+ classical text references
- **更新記錄** (Update Log) — Version history and changes
- **教學** (Tutorial) — Comprehensive board-reading guide

### 🏯 Historical Reign Data

Built-in complete Chinese dynastic chronology allows cross-referencing calculation results with historical reign titles and events.

## Configuration

The Streamlit configuration is stored in `.streamlit/`:

```
.streamlit/
└── config.toml
```

### AI Configuration

AI system prompts for board interpretation are configured in `system_prompts.json` at the repository root.

## Screenshots

### Taiyi Board

![太乙神數盤圖](https://github.com/kentang2017/kintaiyi/blob/master/pic/Untitled-1.png?raw=true)

### Nine Palace Sector Diagram

![太乙九宮分野圖](https://github.com/kentang2017/kintaiyi/blob/master/pic/%E5%A4%AA%E4%B9%99%E4%B9%9D%E5%AE%AE%E5%88%86%E9%87%8E%E5%9C%96.jpg?raw=true)

## Next Steps

- [[Quick Start]] — Get started with the Python API and CLI
- [[Output Fields]] — Understand the board output fields
- [[FAQ]] — Frequently asked questions
