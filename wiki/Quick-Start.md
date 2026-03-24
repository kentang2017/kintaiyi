# Quick Start

Get up and running with Kintaiyi in minutes.

## Python API

### Basic Board Calculation

```python
from kintaiyi.kintaiyi import Taiyi

# Create a Taiyi object with date and time
taiyi = Taiyi(year=2026, month=3, day=24, hour=12, minute=30)

# Calculate a yearly board using Gold Mirror method
result = taiyi.pan(ji_style=0, method=1)

# Access key results
print(result["太乙計"])        # → 年計 (Year calculation)
print(result["局式"])          # → Board formation details
print(result["二十八宿值日"])   # → 28 Mansions daily star
print(result["推主客相闗法"])   # → Master-Guest victory determination
```

### Life Divination

```python
from kintaiyi.kintaiyi import Taiyi

taiyi = Taiyi(year=1990, month=5, day=15, hour=8, minute=0)

# Life divination (sex: "男" for male, "女" for female)
life_result = taiyi.taiyi_life(sex="男")
print(life_result)
```

### Export as JSON

```python
import json
from kintaiyi.kintaiyi import Taiyi

result = Taiyi(2026, 3, 24, 12, 30).pan(ji_style=0, method=1)
print(json.dumps(result, ensure_ascii=False, indent=2))
```

## CLI Quick Examples

```bash
# Year calculation with Gold Mirror method
kintaiyi calculate --date 2026-03-24 --time 12:30 --mode year --method 1

# Day calculation with JSON output
kintaiyi calculate --date 2026-03-24 --time 12:30 --mode day --output json

# Life divination
kintaiyi calculate --date 1990-05-15 --time 08:00 --mode life --sex male

# Markdown table output
kintaiyi calculate --date 2026-03-24 --time 12:30 --mode hour --output markdown
```

## Streamlit Web App

Launch the interactive web interface:

```bash
pip install kintaiyi[app]
streamlit run app.py
```

Or try the live demo: [https://kintaiyi.streamlitapp.com](https://kintaiyi.streamlitapp.com)

## Understanding Parameters

### ji_style (Calculation Mode)

| Value | Mode | Chinese | Description |
|-------|------|---------|-------------|
| `0` | Year | 年計 | Yearly fortune, national trends |
| `1` | Month | 月計 | Monthly fortune and auspiciousness |
| `2` | Day | 日計 | Daily fortune and auspiciousness |
| `3` | Hour | 時計 | Hourly fortune and auspiciousness |
| `4` | Minute | 分計 | Modern extension, precise to the minute |

### method (Ancient Formula)

| Value | Method | Chinese | Source Text |
|-------|--------|---------|-------------|
| `0` | Orthodox | 太乙統宗 | 《太乙統宗寶鑑》 |
| `1` | Gold Mirror | 太乙金鏡 | 《太乙金鏡式經》 |
| `2` | Gold Panning Song | 太乙淘金歌 | 《太乙淘金歌》 |
| `3` | Taiyi Bureau | 太乙局 | 《太乙局》 |

## Next Steps

- [[Python API]] — Detailed API reference
- [[CLI Reference]] — Full CLI documentation
- [[Calculation Modes]] — Deep dive into each calculation mode
- [[Ancient Methods]] — Understanding the four ancient methods
- [[Output Fields]] — Understanding what each output field means
