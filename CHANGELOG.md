# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.4] - 2026-04-20

### Added
- `LICENSE` file (MIT) at repository root.
- `CHANGELOG.md` following Keep a Changelog format.
- `CONTRIBUTING.md` with development guidelines.
- `.github/ISSUE_TEMPLATE/` with bug report and feature request forms.
- CI workflow (`.github/workflows/ci.yml`) with ruff lint + pytest + coverage.
- Table of Contents in `README.md`.
- CI status badge in `README.md`.
- PyPI publish workflow (`.github/workflows/publish.yml`) using Trusted Publisher (OIDC).

### Changed
- Moved `app.py` → `apps/streamlit_app.py` and updated all internal paths.
- Moved `history.pkl`, `example.json`, `system_prompts.json`, `icon.jpg`, `icon.png` → `assets/`.
- Moved `kook/` → `assets/kook/`.
- Updated `pyproject.toml`: license field now points to `LICENSE` file; expanded `package-data`.
- Updated `pyproject.toml`: added `License :: OSI Approved :: MIT License` and `Natural Language :: Chinese (Traditional)` classifiers; pinned `numpy>=1.24.0`.
- Updated `README.md` Streamlit launch command to use new `apps/` path.

### Removed
- `tykook/` directory (duplicate of `kook/`).

## [0.2.3] - 2025-12-27

### Added
- Typer-based CLI (`kintaiyi calculate`, `kintaiyi version`).
- `[cli]`, `[app]`, `[web]`, `[dev]` optional dependency extras.
- Cerebras AI integration for automatic board interpretation.
- `examples/basic_usage.py` usage example.
- Wiki pages and auto-sync workflow.
- Bilingual (中文/English) README with badges.

### Changed
- Adopted `src/` layout with `pyproject.toml` as the single build config.
- Added seven celestial bodies (七曜) to the outer ring of the board.
- Refined 28 Lunar Mansions sector mapping (廿八宿分野).
- Expanded colour-customisable regions to four; colours set by Five-Element attributes.
- Corrected Eight Gates prosperity/decline (八門旺衰).

### Fixed
- Fixed modified Taiyi Life Destiny method display (三星同宮/四星同宮/五星同宮).
- Various calculation parameter corrections.

## [0.2.0] - 2024-08-23

### Added
- Daily Taiyi Nine Stars & Eight Gates (日家太乙九星八門) from 金函玉鏡.
- Taiyi Life Method: yearly/monthly/daily/hourly/minute duty hexagrams, Yang-Nine & Bai-Liu travel limits.
- Imperial Inspection period calculation (天子巡狩之期術) and Three Bases analysis (三基所主術).
- Yin-Yang prediction for disaster cycles (推陰陽以占厄會).

### Fixed
- Corrected Taiyi Life Method minute-board parameters.
- Fixed Hour/Minute board 28 Mansions retrograde calculation.

## [0.1.0] - 2023-05-22

### Added
- Initial public release on PyPI.
- Six calculation modes: Year, Month, Day, Hour, Minute, and Life Destiny.
- Four classical methods: Tongzong, Jinjing, Taojin Ge, Taiyi Ju.
- Streamlit web interface with board SVG rendering.
- Complete Chinese dynastic chronology and lunar calendar conversion.
- Historical case examples from 太乙統宗寶鑑 and 太乙淘金歌.
- Seven Military Strategies (七大兵法), Eight Gates distribution, host-guest analysis.
- Huangji Jingshi (皇極經世) yearly hexagram and Taiyi unified hexagram.

[Unreleased]: https://github.com/kentang2017/kintaiyi/compare/v0.2.4...HEAD
[0.2.4]: https://github.com/kentang2017/kintaiyi/compare/v0.2.3...v0.2.4
[0.2.3]: https://github.com/kentang2017/kintaiyi/compare/v0.2.0...v0.2.3
[0.2.0]: https://github.com/kentang2017/kintaiyi/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/kentang2017/kintaiyi/releases/tag/v0.1.0
