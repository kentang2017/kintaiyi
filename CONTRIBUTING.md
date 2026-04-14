# Contributing to Kintaiyi 堅太乙

We welcome all forms of contribution! 我們歡迎所有形式的貢獻！

## Ways to Contribute

- 🐛 **Bug Reports** — Submit an [Issue](https://github.com/kentang2017/kintaiyi/issues) with steps to reproduce.
- ✨ **New Features** — PRs welcome for new classical methods, calculation modes, or UI improvements.
- 📚 **Historical Verification** — Provide historical case examples to verify algorithm accuracy.
- 🌐 **Translation** — Help translate documentation or divination terminology.
- ⭐ **Star** — The easiest way to show your support!

## Development Setup

```bash
git clone https://github.com/kentang2017/kintaiyi.git
cd kintaiyi
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest
```

## Code Style

This project uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting.

```bash
# Lint
ruff check src/ tests/

# Auto-fix lint issues
ruff check src/ tests/ --fix

# Format
ruff format src/ tests/
```

## Pull Request Process

1. Fork the repository and create a feature branch from `master`.
2. Make your changes — keep commits focused and well-described.
3. Ensure all tests pass (`pytest`) and linting is clean (`ruff check`).
4. Open a Pull Request with a clear description of the change and **why** it's needed.
5. A maintainer will review and provide feedback.

## Reporting Bugs

Please include:
- Python version and OS.
- Steps to reproduce the issue.
- Expected vs. actual output.
- If the bug is about a divination calculation, include the input date/time and parameters.

## Code of Conduct

Be respectful and constructive. We are here to preserve and share knowledge of ancient Chinese divination systems.

---

Thank you for contributing! 感謝你的貢獻！ 🙏
