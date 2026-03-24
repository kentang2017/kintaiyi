# Calculation Modes

Kintaiyi supports six calculation modes (計法), each designed for different divination time scales.

## Overview

| ji_style | CLI Mode | Chinese | Time Scale | Primary Use |
|----------|----------|---------|------------|-------------|
| `0` | `year` | 年計 | Yearly | National fortune, long-term trends |
| `1` | `month` | 月計 | Monthly | Monthly fortune and auspiciousness |
| `2` | `day` | 日計 | Daily | Daily planning and auspiciousness |
| `3` | `hour` | 時計 | Hourly | Hourly fortune, specific timing |
| `4` | `minute` | 分計 | Per minute | Modern extension, precise timing |
| `5` | `life` | 命法 | Lifetime | Personal destiny and life reading |

---

## Year Calculation (年計)

**ji_style = 0** | **CLI: `--mode year`**

The year calculation is the most traditional and widely documented mode. It is used to assess the overall fortune of a year — typically for national events, warfare, natural disasters, and large-scale trends.

```python
result = Taiyi(2026, 3, 24, 12, 30).pan(ji_style=0, method=1)
```

```bash
kintaiyi calculate --date 2026-03-24 --time 12:30 --mode year
```

**Historically used for:**
- Predicting dynastic changes and political events
- Forecasting natural disasters (earthquakes, floods)
- Military strategy and campaign timing

---

## Month Calculation (月計)

**ji_style = 1** | **CLI: `--mode month`**

The month calculation provides a finer temporal resolution, assessing fortune and auspiciousness for a given month.

```python
result = Taiyi(2026, 3, 24, 12, 30).pan(ji_style=1, method=1)
```

```bash
kintaiyi calculate --date 2026-03-24 --time 12:30 --mode month
```

---

## Day Calculation (日計)

**ji_style = 2** | **CLI: `--mode day`**

The day calculation is used for daily planning — choosing auspicious days for important activities.

```python
result = Taiyi(2026, 3, 24, 12, 30).pan(ji_style=2, method=1)
```

```bash
kintaiyi calculate --date 2026-03-24 --time 12:30 --mode day
```

---

## Hour Calculation (時計)

**ji_style = 3** | **CLI: `--mode hour`**

The hour calculation provides even greater precision, using the traditional Chinese two-hour periods (時辰) for timing-sensitive decisions.

```python
result = Taiyi(2026, 3, 24, 12, 30).pan(ji_style=3, method=1)
```

```bash
kintaiyi calculate --date 2026-03-24 --time 12:30 --mode hour
```

> **Note:** This is the default mode for the Streamlit web interface.

---

## Minute Calculation (分計)

**ji_style = 4** | **CLI: `--mode minute`**

A modern extension of the traditional system, the minute calculation offers the finest temporal resolution, precise to the minute.

```python
result = Taiyi(2026, 3, 24, 12, 30).pan(ji_style=4, method=1)
```

```bash
kintaiyi calculate --date 2026-03-24 --time 12:30 --mode minute
```

---

## Life Divination (命法)

**ji_style = 5** | **CLI: `--mode life`**

The life divination mode uses a modified Taiyi method for personal destiny calculation. This requires the subject's birth date, time, and sex.

### Python API

```python
# Note: Python API uses Chinese characters for sex
life = Taiyi(1990, 5, 15, 8, 0).taiyi_life(sex="男")  # "男" or "女"
```

### CLI

```bash
# CLI uses English words for sex
kintaiyi calculate --date 1990-05-15 --time 08:00 --mode life --sex male
```

> **Note:** The `--sex` parameter is required when using life mode. In the Python API, use `"男"` (male) or `"女"` (female). In the CLI, use `male` or `female`.

---

## Choosing the Right Mode

| Scenario | Recommended Mode |
|----------|-----------------|
| Forecasting a year's national events | Year (年計) |
| Planning activities for a specific month | Month (月計) |
| Choosing an auspicious date | Day (日計) |
| Timing a specific action within a day | Hour (時計) |
| Modern precision divination | Minute (分計) |
| Personal destiny reading | Life (命法) |

## Next Steps

- [[Ancient Methods]] — Learn about the four calculation formulas
- [[Output Fields]] — Understand the board output
- [[Python API]] — API reference
