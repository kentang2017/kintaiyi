# Contributing

We welcome all forms of contribution to Kintaiyi! Whether you're fixing bugs, adding features, verifying historical cases, or improving documentation, your help is valued.

## Ways to Contribute

- 🐛 **Bug Reports** — Submit an [Issue](https://github.com/kentang2017/kintaiyi/issues)
- ✨ **New Features** — PRs for new ancient methods, calculation modes, or improvements
- 📚 **Case Verification** — Provide historical case studies to verify algorithm accuracy
- 🌐 **Translation** — Help translate documentation or terminology
- 📖 **Documentation** — Improve wiki pages, code comments, or examples
- ⭐ **Star** — The simplest way to show support!

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/kentang2017/kintaiyi.git
cd kintaiyi
```

### 2. Install Development Dependencies

```bash
pip install -e ".[dev]"
```

This installs the package in editable mode along with development tools (pytest, ruff).

### 3. Run Tests

```bash
pytest
```

### 4. Code Formatting & Linting

```bash
# Check for issues
ruff check src/

# Auto-fix issues
ruff check src/ --fix

# Format code
ruff format src/
```

## Project Structure

```
kintaiyi/
├── src/kintaiyi/           # Core Python package
│   ├── __init__.py         # Package initialization, version
│   ├── kintaiyi.py         # Core Taiyi calculation engine
│   ├── cli.py              # Typer CLI interface
│   ├── config.py           # Configuration and utilities
│   ├── jieqi.py            # Solar terms calculations
│   ├── chart.py            # SVG board rendering
│   ├── taiyidict.py        # Taiyi terminology dictionary
│   ├── taiyimishu.py       # Taiyi formulas and methods
│   ├── taiyi_life_dict.py  # Life divination data
│   ├── historytext.py      # Historical text data
│   ├── ruler.py            # Dynasty/ruler information
│   ├── kinliuren.py        # Liuren integration
│   └── cerebras_client.py  # AI integration
├── app.py                  # Streamlit entry point (delegates to apps/)
├── apps/
│   └── streamlit_app.py    # Streamlit web application
├── docs/                   # Documentation markdown files
├── examples/               # Example scripts
├── tests/                  # Test suite
├── wiki/                   # Wiki pages (GitHub Wiki)
├── pic/                    # Images and diagrams
├── pyproject.toml          # Project metadata
└── requirements.txt        # Streamlit Cloud dependencies
```

## Coding Conventions

- **Internal imports**: Use relative imports within `src/kintaiyi/` (e.g., `from . import config`)
- **External imports**: Use absolute package imports in `apps/streamlit_app.py` (e.g., `from kintaiyi import config`)
- **Python version**: ≥ 3.10 (uses `X | Y` union syntax)
- **Linter**: ruff
- **Tests**: pytest

## Submitting a Pull Request

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Run tests and linting (`pytest && ruff check src/`)
5. Commit your changes (`git commit -m "Add my feature"`)
6. Push to your fork (`git push origin feature/my-feature`)
7. Open a Pull Request on GitHub

## Contact

| Channel | Link |
|---------|------|
| 📢 Telegram Channel | [numerology_coding](https://t.me/numerology_coding) |
| 💬 Telegram DM | [haizhonggum](https://t.me/haizhonggum) |
| 🐛 GitHub Issues | [Submit Issue](https://github.com/kentang2017/kintaiyi/issues) |
| 💰 PayPal Donation | [paypal.me/kinyeah](https://www.paypal.me/kinyeah) |

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
