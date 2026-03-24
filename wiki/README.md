# Wiki Pages

This directory contains the source files for the [Kintaiyi GitHub Wiki](https://github.com/kentang2017/kintaiyi/wiki).

## How It Works

A GitHub Actions workflow (`.github/workflows/wiki-sync.yml`) automatically publishes changes from this directory to the GitHub Wiki whenever files in `wiki/` are updated on the `master` branch.

## Pages

| File | Wiki Page |
|------|-----------|
| `Home.md` | Wiki home page |
| `_Sidebar.md` | Navigation sidebar |
| `Installation.md` | Installation guide |
| `Quick-Start.md` | Quick start tutorial |
| `Python-API.md` | Python API reference |
| `CLI-Reference.md` | CLI documentation |
| `Web-Interface.md` | Streamlit web app guide |
| `Calculation-Modes.md` | Six calculation modes |
| `Ancient-Methods.md` | Four classical methods |
| `Output-Fields.md` | Output field reference |
| `Contributing.md` | Contribution guidelines |
| `FAQ.md` | Frequently asked questions |

## Editing

Edit the `.md` files in this directory and push to `master`. The wiki will be updated automatically.

### Cross-Page Links

Use `[[Page Name]]` syntax for links between wiki pages (e.g., `[[Installation]]`, `[[Quick Start]]`).
