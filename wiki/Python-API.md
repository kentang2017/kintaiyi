# Python API

## Taiyi Class

The `Taiyi` class is the core of Kintaiyi. It provides methods for board calculation and life divination.

### Import

```python
from kintaiyi.kintaiyi import Taiyi
```

### Constructor

```python
Taiyi(year, month, day, hour, minute)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `year` | `int` | Year in Common Era (supports negative years for BCE) |
| `month` | `int` | Month (1–12) |
| `day` | `int` | Day (1–31) |
| `hour` | `int` | Hour (0–23) |
| `minute` | `int` | Minute (0–59) |

**Example:**
```python
taiyi = Taiyi(year=2026, month=3, day=24, hour=12, minute=30)
```

> **Note:** Dates before the Common Era can be queried using negative years (e.g., `-578` for 578 BCE).

---

## Methods

### `pan(ji_style, method)`

Calculate a Taiyi divination board.

| Parameter | Type | Description |
|-----------|------|-------------|
| `ji_style` | `int` | Calculation mode: `0`=Year, `1`=Month, `2`=Day, `3`=Hour, `4`=Minute |
| `method` | `int` | Ancient formula: `0`=統宗, `1`=金鏡, `2`=淘金歌, `3`=太乙局 |

**Returns:** `dict` — A dictionary containing all board calculation results.

**Example:**
```python
result = Taiyi(2026, 3, 24, 12, 30).pan(ji_style=0, method=1)
```

See [[Output Fields]] for details on the returned dictionary.

---

### `kook(ji_style, method)`

Alias for `pan()`. Functions identically.

```python
result = Taiyi(1552, 9, 24, 0, 0).kook(ji_style=0, method=1)
```

---

### `taiyi_life(sex)`

Calculate life divination using the modified Taiyi method.

| Parameter | Type | Description |
|-----------|------|-------------|
| `sex` | `str` | `"男"` for male, `"女"` for female |

**Returns:** `dict` — Life divination results.

**Example:**
```python
life = Taiyi(1990, 5, 15, 8, 0).taiyi_life(sex="男")
```

---

## Complete Example

```python
import json
from kintaiyi.kintaiyi import Taiyi

# Create Taiyi object
taiyi = Taiyi(year=1552, month=9, day=24, hour=0, minute=0)

# Calculate yearly board with Gold Mirror method
result = taiyi.pan(ji_style=0, method=1)

# Print formatted JSON
print(json.dumps(result, ensure_ascii=False, indent=2))

# Access specific fields
print(f"計法: {result['太乙計']}")
print(f"公式: {result['太乙公式類別']}")
print(f"年號: {result['年號']}")
print(f"局式: {result['局式']}")
print(f"值日宿: {result['二十八宿值日']}")
print(f"主客: {result['推主客相闗法']}")
```

### Sample Output Structure

```python
{
  "太乙計": "年計",
  "太乙公式類別": "太乙金鏡",
  "公元日期": "1552年9月24日0時",
  "干支": ["壬子", "庚戌", "丙戌", "戊子", "甲子"],
  "農曆": {"年": 1552, "月": 9, "日": 7},
  "年號": "明世宗朱厚熜 嘉靖三十一年",
  "局式": {"文": "陽遁十三局", "數": 13, ...},
  "太乙落宮": 6,
  "太乙": "兌",
  "二十八宿值日": "翼",
  "推主客相闗法": "主尅客，主勝",
  ...
}
```

## Iterating Over Modes and Methods

```python
from kintaiyi.kintaiyi import Taiyi

taiyi = Taiyi(2026, 3, 24, 12, 30)

# All five calculation modes with Gold Mirror method
modes = {0: "Year", 1: "Month", 2: "Day", 3: "Hour", 4: "Minute"}
for ji_style, name in modes.items():
    result = taiyi.pan(ji_style=ji_style, method=1)
    print(f"{name}: 局式={result['局式']}")
```

## Next Steps

- [[Output Fields]] — Understand what each result field means
- [[Calculation Modes]] — Deep dive into each mode
- [[Ancient Methods]] — Learn about the four classical formulas
