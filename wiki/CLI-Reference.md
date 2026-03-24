# CLI Reference

Kintaiyi includes a command-line interface powered by [Typer](https://typer.tiangolo.com/).

## Installation

```bash
pip install kintaiyi[cli]
```

## Commands

### `kintaiyi calculate`

Calculate a Taiyi Shenshu divination board.

```
kintaiyi calculate [OPTIONS]
```

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--year` | `-y` | int | Current year | Year (公元年) |
| `--month` | `-m` | int | Current month | Month (月) |
| `--day` | `-d` | int | Current day | Day (日) |
| `--hour` | `-H` | int | Current hour | Hour (時, 0–23) |
| `--minute` | `-M` | int | Current minute | Minute (分, 0–59) |
| `--date` | | str | — | Date in `YYYY-MM-DD` format |
| `--time` | | str | — | Time in `HH:MM` format |
| `--mode` | | str | `year` | Calculation mode |
| `--method` | | int | `0` | Taiyi method (0–3) |
| `--output` | `-o` | str | `text` | Output format |
| `--sex` | `-s` | str | — | Sex for life mode |

#### Mode Values

| Mode | Description |
|------|-------------|
| `year` | Year calculation (年計) |
| `month` | Month calculation (月計) |
| `day` | Day calculation (日計) |
| `hour` | Hour calculation (時計) |
| `minute` | Minute calculation (分計) |
| `life` | Life divination (命法) |

#### Method Values

| Value | Method | Source |
|-------|--------|--------|
| `0` | 太乙統宗 (Orthodox) | 《太乙統宗寶鑑》 |
| `1` | 太乙金鏡 (Gold Mirror) | 《太乙金鏡式經》 |
| `2` | 太乙淘金歌 (Gold Panning Song) | 《太乙淘金歌》 |
| `3` | 太乙局 (Taiyi Bureau) | 《太乙局》 |

#### Output Formats

| Format | Description |
|--------|-------------|
| `text` | Plain text, one field per line (default) |
| `json` | JSON with Chinese keys |
| `markdown` | Markdown table format |

### `kintaiyi version`

Display the installed version of Kintaiyi.

```bash
kintaiyi version
# Output: kintaiyi 0.2.3
```

## Usage Examples

### Basic Year Calculation

```bash
kintaiyi calculate --date 2026-03-24 --time 12:30 --mode year --method 1
```

### Using Individual Date Components

```bash
kintaiyi calculate --year 1552 --month 9 --day 24 --hour 0 --minute 0 --mode year --method 1
```

### Day Calculation with JSON Output

```bash
kintaiyi calculate --date 2026-03-24 --time 12:30 --mode day --output json
```

### Markdown Table Output

```bash
kintaiyi calculate --date 2026-03-24 --time 12:30 --mode hour --output markdown
```

### Life Divination

```bash
# Using English
kintaiyi calculate --date 1990-05-15 --time 08:00 --mode life --sex male

# Using Chinese
kintaiyi calculate --date 1990-05-15 --time 08:00 --mode life --sex 男
```

### Current Time (Default)

```bash
# Uses current date and time
kintaiyi calculate
```

### Piping JSON to Other Tools

```bash
# Pretty-print with jq
kintaiyi calculate --date 2026-03-24 --time 12:30 --output json | jq .

# Save to file
kintaiyi calculate --date 2026-03-24 --time 12:30 --output json > result.json
```

## Next Steps

- [[Python API]] — Use Kintaiyi as a Python library
- [[Output Fields]] — Understand the calculation results
- [[Calculation Modes]] — Learn about each calculation mode
