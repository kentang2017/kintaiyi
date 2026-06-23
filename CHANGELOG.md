# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- 依《太乙統宗寶鑑》卷四「釋掩迫關囚擊格對提挾執提四郭固四郭社」，新增 `Taiyi.shi_geju()` 動態推算十一格局，並整合至 `pan()` 輸出鍵 `釋格局`。
- 依卷十「三旗行宮」原文公式，新增 `config.sanqi()`（太歲青龍旗、太陰黑旗、害氣赤旗及會合），整合至 `pan()` 輸出鍵 `三旗行宮`。
- 依卷十「九宮貴神」原文公式，新增 `config.nine_palace_gods()`（直事貴神與鈎宮飛行分布），整合至 `pan()` 輸出鍵 `九宮貴神`；鈎宮分布經原書太陰直事之例驗證完全吻合。
- Streamlit 介面於排盤說明中加入釋格局、三旗行宮、九宮貴神之呈現（中英 i18n）。
- 排盤 SVG 新增古典美學裝飾層：外緣雙線金環、八方珠飾、四正方位八卦標記（純附加，不影響座標與轉盤解析）。
- `README.md` 輸出內容列表補入卷四、卷十新增古典項目。
- 排盤 SVG 美學修正：於所有圖層之下鋪一層「玄色」古典底盤（深靛墨 `#141826`），
  最外環不再露出白色頁面底色，盤內白色／米色文字一律清晰可見；外緣金環、珠飾、
  八卦標記重新定位於 viewBox 內（空間足夠方置八卦，避免裁切）。
- Streamlit 排盤主題 CSS 再優化：根容器改為深靛徑向漸層底，各環填色加深飽和度，
  整體 UI 古典統一、米色文字對比提升。
- 排盤 SVG 新增「三旗行宮」旗旆圖案（卷十）：青龍旗(綠)、太陰黑旗(黑)、害氣赤旗(紅)，
  依各旗所落地支宮位之角度顯示於外緣，同宮者切向散開避免重疊。
- 最外環「八卦天盤」改為活盤：依後天八卦方位序置八卦，並隨排局以 `trigram_rotate`
  旋轉（依太乙落宮序位×45°，陰遁再加 180°），故不同排局八卦方位不同，非固定裝飾。


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
