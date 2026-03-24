# Output Fields

When you calculate a Taiyi board using `pan()` or the CLI, the result contains a rich set of fields covering all aspects of the divination. This page explains each category of output.

## Result Structure

The result is a Python `dict` (or JSON/Markdown when using CLI output formats) containing the following categories of fields.

### Basic Information (基本資訊)

| Field | Description | Example |
|-------|-------------|---------|
| `太乙計` | Calculation mode used | `"年計"` |
| `太乙公式類別` | Ancient method used | `"太乙金鏡"` |
| `公元日期` | Common Era date and time | `"1552年9月24日0時"` |
| `干支` | Five-pillar Heavenly Stems & Earthly Branches | `["壬子", "庚戌", "丙戌", "戊子", "甲子"]` |
| `農曆` | Lunar calendar date | `{"年": 1552, "月": 9, "日": 7}` |
| `年號` | Historical reign title | `"明世宗朱厚熜 嘉靖三十一年"` |

### Board Formation (局式)

| Field | Description |
|-------|-------------|
| `局式` | Board formation details — includes direction (陰遁/陽遁), board number, accumulated years, and epoch |

The `局式` field is a nested dictionary with sub-fields:
- `文` — Text description (e.g., "陽遁十三局")
- `數` — Numeric board number
- Additional calculation details

### Taiyi Deities (太乙諸神)

| Field | Description |
|-------|-------------|
| `太乙落宮` | Palace where Taiyi deity resides (1–9) |
| `太乙` | Taiyi palace trigram name |
| `天乙` | Heavenly Yi position |
| `地乙` | Earthly Yi position |
| `直符` | Duty Talisman |
| `文昌` | Literary Star position |
| `計神` | Calculating Spirit position |
| `合神` | Combining Spirit position |

### Master-Guest Calculations (主客算)

| Field | Description |
|-------|-------------|
| `主算` | Master calculation number |
| `客算` | Guest calculation number |
| `定算` | Final determination number |
| `推主客相闗法` | Master-Guest victory determination (e.g., "主尅客，主勝") |

The Master-Guest system is central to Taiyi divination, especially for military strategy:
- **Master (主)** — Represents the defending side or the one being asked about
- **Guest (客)** — Represents the attacking side or external forces
- The relationship between Master and Guest numbers determines the outcome

### Eight Gates (八門)

| Field | Description |
|-------|-------------|
| `八門` | Distribution of the eight gates across palaces |

The Eight Gates (八門) are:
1. 開門 (Open) — Auspicious
2. 休門 (Rest) — Auspicious
3. 生門 (Life) — Auspicious
4. 傷門 (Injury) — Inauspicious
5. 杜門 (Block) — Neutral
6. 景門 (Scene) — Neutral
7. 死門 (Death) — Inauspicious
8. 驚門 (Shock) — Inauspicious

### 28 Mansions (二十八宿)

| Field | Description |
|-------|-------------|
| `二十八宿值日` | Daily duty mansion star |

The 28 Mansions (二十八宿) are the traditional Chinese star groupings used for celestial observation and divination.

### Eight Palaces (八宮旺衰)

| Field | Description |
|-------|-------------|
| `八宮旺衰` | Flourishing and declining status of the eight palaces |

### Military Predictions (兵陣預測)

| Field | Description |
|-------|-------------|
| `飛鳥助戰法` | Flying Bird Battle Assistance Method |
| `風雲諸法` | Wind and Cloud Methods |

### Seven Military Strategies (七大兵法)

These are specialized military divination patterns:

| Strategy | Chinese | Description |
|----------|---------|-------------|
| Thunder Duke Enters Water | 雷公入水 | Thunder-related omen |
| Asking the Way at the Ford | 臨津問道 | River-crossing strategy |
| Lion's Reverse Throw | 獅子反擲 | Counter-attack pattern |
| White Cloud Rolls the Sky | 白雲捲空 | Sky-reading omen |
| Fierce Tiger Resistance | 猛虎相拒 | Defensive strategy |
| White Dragon Gets Cloud | 白龍得雲 | Favorable dragon omen |
| Returning Army Silent | 回軍無言 | Retreat indication |

### Four Spirits (四神)

| Field | Description |
|-------|-------------|
| `四神` | Positions of the four directional spirits |

---

## Life Divination Output

When using `taiyi_life()` or `--mode life`, the output contains life-specific fields related to personal destiny reading based on the subject's birth date, time, and sex.

---

## Output Formats (CLI)

The CLI supports three output formats:

### Text (default)
```
太乙計: 年計
太乙公式類別: 太乙金鏡
公元日期: 2026年3月24日12時
...
```

### JSON
```json
{
  "太乙計": "年計",
  "太乙公式類別": "太乙金鏡",
  "公元日期": "2026年3月24日12時"
}
```

### Markdown
```markdown
| 項目 | 內容 |
| --- | --- |
| 太乙計 | 年計 |
| 太乙公式類別 | 太乙金鏡 |
```

## Next Steps

- [[Calculation Modes]] — Learn about each calculation mode
- [[Ancient Methods]] — Understand the four classical methods
- [[Python API]] — API reference
