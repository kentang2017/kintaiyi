# FAQ

Frequently asked questions about Kintaiyi.

---

## General

### What is Taiyi Shenshu (太乙神數)?

Taiyi Shenshu is one of the "Three Styles" (三式) of ancient Chinese divination, alongside Qi Men Dun Jia (奇門遁甲) and Da Liu Ren (大六壬). It is a system for predicting celestial phenomena, national fortune, natural disasters, and other large-scale events based on astronomical and calendrical calculations. Its origins date back over 3,000 years.

### What does "Kintaiyi" (堅太乙) mean?

"堅" (kin/jiān) means "steadfast" or "firm." The name "堅太乙" means "steadfastly adhering to the ancient Taiyi methods" — reflecting the project's commitment to faithfully implementing classical algorithms without simplification.

### Is this software accurate?

Kintaiyi strictly follows the algorithms described in classical texts. The repository includes 82+ historical case studies (from 578 BCE to 1704 CE) that have been verified against the software's output. See the [Historical Examples](https://github.com/kentang2017/kintaiyi/blob/master/docs/example.md) documentation for details.

---

## Installation

### What Python version is required?

Python 3.10 or higher is required. The codebase uses modern Python syntax including the `X | Y` union type syntax.

### How do I install just the core library?

```bash
pip install kintaiyi
```

### How do I install the CLI tool?

```bash
pip install kintaiyi[cli]
```

### How do I install the web interface?

```bash
pip install kintaiyi[app]
```

See [[Installation]] for complete details.

---

## Usage

### Can I query dates before the Common Era (BCE)?

Yes! Kintaiyi supports dates before the Common Era. Use negative years in the Python API:

```python
result = Taiyi(-578, 6, 15, 12, 0).pan(ji_style=0, method=1)
```

### What is the difference between `pan()` and `kook()`?

They are the same — `kook()` is an alias for `pan()`. Both calculate a Taiyi divination board with identical parameters and output.

### What is the difference between the four methods?

The four methods (Orthodox, Gold Mirror, Gold Panning Song, Taiyi Bureau) are based on different classical texts and primarily differ in how they compute accumulated years (積年數). This can lead to different board numbers for the same date. See [[Ancient Methods]] for details.

### What is the difference between `--sex male` and `sex="男"`?

The CLI uses English terms (`male`/`female`), while the Python API uses Chinese characters (`"男"`/`"女"`). Both refer to the same parameter for life divination.

### How do I choose between Year, Month, Day, Hour, and Minute modes?

- **Year** — For long-term forecasts (national events, yearly fortune)
- **Month** — For monthly planning
- **Day** — For daily auspiciousness
- **Hour** — For precise timing within a day
- **Minute** — Modern extension for very precise timing

See [[Calculation Modes]] for detailed guidance.

---

## Output

### What format does the output come in?

The Python API returns a Python `dict`. The CLI supports three output formats:
- `text` (default) — Plain text, one field per line
- `json` — Structured JSON
- `markdown` — Markdown table

### What does "主尅客，主勝" mean?

This is the Master-Guest (主客) victory determination. "主尅客" means "Master overcomes Guest" and "主勝" means "Master wins." This is a key military divination result.

### What are the Eight Gates (八門)?

The Eight Gates are spatial-temporal indicators in Taiyi divination:
- 開門 (Open), 休門 (Rest), 生門 (Life) — Auspicious
- 傷門 (Injury), 死門 (Death), 驚門 (Shock) — Inauspicious
- 杜門 (Block), 景門 (Scene) — Neutral

---

## Web Interface

### Where is the live demo?

Visit [https://kintaiyi.streamlitapp.com](https://kintaiyi.streamlitapp.com)

### I can't access the live demo from China. What should I do?

Mainland China users may need a VPN to access Streamlit Cloud. Alternatively, you can run the web interface locally:

```bash
pip install kintaiyi[app]
streamlit run app.py
```

### Does the web interface support English?

Yes! The web interface has a language toggle supporting both Chinese (中文) and English.

---

## Development

### How do I run the tests?

```bash
pip install -e ".[dev]"
pytest
```

### How do I format the code?

```bash
ruff check src/ --fix
ruff format src/
```

### Where can I report bugs?

Open an issue at [GitHub Issues](https://github.com/kentang2017/kintaiyi/issues).

---

## Related Projects

| Project | Description |
|---------|-------------|
| [堅奇門 kinqimen](https://github.com/kentang2017/kinqimen) | Python Qi Men Dun Jia (奇門遁甲) |
| [堅六壬 kinliuren](https://github.com/kentang2017/kinliuren) | Python Da Liu Ren (大六壬) |

Together, these three projects cover all of the "Three Styles" (三式) of ancient Chinese divination as open-source software.

## Still Have Questions?

- 📢 Join the [Telegram Channel](https://t.me/numerology_coding)
- 💬 Message on [Telegram](https://t.me/haizhonggum)
- 🐛 Open a [GitHub Issue](https://github.com/kentang2017/kintaiyi/issues)
