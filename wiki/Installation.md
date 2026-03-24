# Installation

## Requirements

- **Python ≥ 3.10**

## Basic Installation

Install the core library from PyPI:

```bash
pip install kintaiyi
```

This installs the Python API with all core dependencies for Taiyi board calculation.

## Optional Extras

Kintaiyi provides optional extras for different use cases:

```bash
# CLI command-line tool (powered by Typer)
pip install kintaiyi[cli]

# Streamlit graphical web interface
pip install kintaiyi[app]

# Flask web backend
pip install kintaiyi[web]

# Development tools (pytest + ruff)
pip install kintaiyi[dev]

# Install everything
pip install kintaiyi[cli,app]
```

## Install from Source

For the latest development version or to contribute:

```bash
git clone https://github.com/kentang2017/kintaiyi.git
cd kintaiyi
pip install -e ".[cli,app,dev]"
```

## Core Dependencies

The following packages are automatically installed:

| Package | Purpose |
|---------|---------|
| `pendulum` | Date and time handling |
| `sxtwl` | Lunar calendar conversion |
| `ephem` | Astronomical calculations |
| `cn2an` | Chinese ↔ Arabic number conversion |
| `pytz` | Timezone support |
| `bidict` | Bidirectional dictionary |
| `drawsvg` | SVG board rendering |
| `numpy` | Numeric computation |
| `kerykeion` | Astrological calculations |
| `astropy` | Astronomical computation |

## Verifying Installation

After installation, verify it works:

```bash
# Check version
python -c "import kintaiyi; print(kintaiyi.__version__)"

# If CLI is installed
kintaiyi version
```

## Next Steps

- [[Quick Start]] — Get started with your first Taiyi board
- [[Python API]] — Full Python API reference
- [[CLI Reference]] — Command-line tool usage
