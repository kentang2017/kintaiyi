# Ancient Methods

Kintaiyi implements four classical Taiyi calculation methods (公式), each based on different ancient texts and traditions. The methods primarily differ in how they compute the **accumulated years** (積年數) used to derive the board number (局數).

## Overview

| method | Name | Chinese | Source Text | Chinese Source |
|--------|------|---------|-------------|----------------|
| `0` | Orthodox | 太乙統宗 | *Taiyi Orthodox Collection Precious Mirror* | 《太乙統宗寶鑑》 |
| `1` | Gold Mirror | 太乙金鏡 | *Taiyi Gold Mirror Formula Classic* | 《太乙金鏡式經》 |
| `2` | Gold Panning Song | 太乙淘金歌 | *Taiyi Gold Panning Song* | 《太乙淘金歌》 |
| `3` | Taiyi Bureau | 太乙局 | *Taiyi Bureau* | 《太乙局》 |

---

## Taiyi Orthodox (太乙統宗)

**method = 0**

Based on the 《太乙統宗寶鑑》 (*Taiyi Tongzong Baojian*), compiled during the Yuan Dynasty. This is considered the most comprehensive and systematized version of Taiyi Shenshu, integrating various earlier traditions into a unified framework.

```python
result = Taiyi(2026, 3, 24, 12, 30).pan(ji_style=0, method=0)
```

```bash
kintaiyi calculate --date 2026-03-24 --time 12:30 --method 0
```

---

## Taiyi Gold Mirror (太乙金鏡)

**method = 1**

Based on the 《太乙金鏡式經》 (*Taiyi Jinjing Shijing*), authored by Wang Xi Ming (王希明) during the Tang Dynasty. This is one of the earliest and most authoritative texts on Taiyi Shenshu, and it is the primary reference for many practitioners.

```python
result = Taiyi(2026, 3, 24, 12, 30).pan(ji_style=0, method=1)
```

```bash
kintaiyi calculate --date 2026-03-24 --time 12:30 --method 1
```

---

## Taiyi Gold Panning Song (太乙淘金歌)

**method = 2**

Based on the 《太乙淘金歌》 (*Taiyi Taojin Ge*), a Song Dynasty text that presents the Taiyi system in a mnemonic verse format, making it easier to memorize and apply.

```python
result = Taiyi(2026, 3, 24, 12, 30).pan(ji_style=0, method=2)
```

```bash
kintaiyi calculate --date 2026-03-24 --time 12:30 --method 2
```

---

## Taiyi Bureau (太乙局)

**method = 3**

Based on the 《太乙局》 (*Taiyi Ju*), which presents an alternative calculation framework.

```python
result = Taiyi(2026, 3, 24, 12, 30).pan(ji_style=0, method=3)
```

```bash
kintaiyi calculate --date 2026-03-24 --time 12:30 --method 3
```

---

## Comparing Methods

All four methods produce the same type of board output but may yield different board numbers (局數) for the same date and time due to their different accumulated-year formulas. Researchers often compare results across methods to gain deeper insights.

```python
from kintaiyi.kintaiyi import Taiyi

taiyi = Taiyi(2026, 3, 24, 12, 30)

methods = {
    0: "太乙統宗 (Orthodox)",
    1: "太乙金鏡 (Gold Mirror)",
    2: "太乙淘金歌 (Gold Panning Song)",
    3: "太乙局 (Taiyi Bureau)",
}

for method_id, name in methods.items():
    result = taiyi.pan(ji_style=0, method=method_id)
    print(f"{name}: 局式={result['局式']}")
```

## Classical Text Bibliography

Kintaiyi references an extensive collection of classical texts spanning from the Sui Dynasty to modern times. For a complete bibliography, see the [Ancient Texts Bibliography](https://github.com/kentang2017/kintaiyi/blob/master/docs/guji.md) in the repository documentation.

Notable texts include:
- 《太乙金鏡式經》 — Tang Dynasty, by Wang Xi Ming
- 《太乙統宗寶鑑》 — Yuan Dynasty, comprehensive compilation
- 《太乙淘金歌》 — Song Dynasty, mnemonic verse format
- 《太乙秘書》 — Classic reference with detailed formulas

## Next Steps

- [[Calculation Modes]] — Learn about the six calculation modes
- [[Output Fields]] — Understand board output fields
- [[Python API]] — API reference
