"""Grok-style modern dark theme for 堅太乙 Streamlit UI.

Sidebar: fixed 310px width, non-resizable (see SIDEBAR FIXED WIDTH block).
"""

from __future__ import annotations

import functools


# ── Fixed sidebar width (px) — do not expose resize handle ──────────────
SIDEBAR_WIDTH_PX = 310


@functools.lru_cache(maxsize=1)
def get_custom_css() -> str:
    """Return global CSS injected via st.markdown(unsafe_allow_html=True)."""
    w = SIDEBAR_WIDTH_PX
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;600;700&display=swap');

:root {{
    --bg-base:       #0a0a0a;
    --bg-elevated:   #141414;
    --bg-surface:    #1a1a1a;
    --bg-hover:      #222222;
    --border-subtle: rgba(255, 255, 255, 0.08);
    --border-strong: rgba(255, 255, 255, 0.14);
    /* Brighter grays — readable on #0a0a0a while keeping hierarchy */
    --text-primary:  #fafafa;
    --text-secondary:#d6d6d6;
    --text-muted:    #a8a8a8;
    --accent:        #ffffff;
    --accent-soft:   rgba(255, 255, 255, 0.12);
    --accent-glow:   rgba(255, 255, 255, 0.06);
    --danger:        #ef4444;
    --success:       #22c55e;
    /* Fixed sidebar — must match SIDEBAR_WIDTH_PX */
    --sidebar-width: {w}px;
    --sidebar-collapsed-width: 2.875rem;
    --topnav-height: 38px;
    --font-sans:     'Inter', 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    --radius-sm:     8px;
    --radius-md:     12px;
    --radius-lg:     16px;
    /* 十二運色系 — 低飽和、暗色主題適配 */
    --yun-1:  #3b5998;
    --yun-2:  #6b4c93;
    --yun-3:  #b8860b;
    --yun-4:  #4a6741;
    --yun-5:  #8b6f47;
    --yun-6:  #5b7c99;
    --yun-7:  #c0706c;
    --yun-8:  #7d6b8d;
    --yun-9:  #5c8a7a;
    --yun-10: #94695a;
    --yun-11: #6b8299;
    --yun-12: #8b7355;
    /* 吉凶色標 */
    --yun-ji-fu:    #f59e0b;
    --yun-ji-ji:    #22c55e;
    --yun-ji-xiong: #ef4444;
    --yun-ji-zai:   #dc2626;
    /* 值卦色系 — 與五層計式對應 */
    --hex-year:   #6b4c93;
    --hex-month:  #4a6741;
    --hex-day:    #b8860b;
    --hex-hour:   #5b7c99;
    --hex-minute: #7d6b8d;
}}

/* ── GLOBAL ─────────────────────────────────────────────────────────── */
html, body, .stApp {{
    background-color: var(--bg-base) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-sans) !important;
}}

.stApp {{
    background-image: none !important;
}}

[data-testid="stIconMaterial"] {{
    font-family: 'Material Symbols Rounded' !important;
}}

/* Hide default Streamlit header chrome for cleaner Grok look */
[data-testid="stHeader"] {{
    background: transparent !important;
    border: none !important;
}}

/* ── TOP NAV BAR ────────────────────────────────────────────────────── */
.grok-topnav {{
    position: sticky;
    top: 0;
    z-index: 999;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    min-height: var(--topnav-height);
    padding: 0.35rem 1rem;
    margin: -1rem -1rem 0.3rem -1rem;
    background: rgba(10, 10, 10, 0.92);
    border-bottom: 1px solid var(--border-subtle);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
}}
.grok-topnav-brand {{
    display: flex;
    align-items: center;
    gap: 0.65rem;
    min-width: 0;
}}
.grok-topnav-logo {{
    width: 28px;
    height: 28px;
    border-radius: 8px;
    background: linear-gradient(135deg, #2a2a2a, #0a0a0a);
    border: 1px solid var(--border-strong);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--text-primary);
}}
.grok-topnav-title {{
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--text-primary);
    letter-spacing: 0.02em;
    margin: 0;
    line-height: 1.2;
}}
.grok-topnav-sub {{
    font-size: 0.75rem;
    color: var(--text-secondary);
    margin: 0;
}}
/* ── SIDEBAR BRAND (replaces top navbar) ─────────────────────────────── */
.grok-sidebar-brand {{
    display: flex;
    align-items: center;
    gap: 0.65rem;
    padding: 0.1rem 0.1rem 0.6rem 0.1rem;
    margin-bottom: 0.4rem;
    border-bottom: 1px solid var(--border-subtle);
}}
.grok-sidebar-brand-logo {{
    width: 28px;
    height: 28px;
    flex-shrink: 0;
    border-radius: 8px;
    background: linear-gradient(135deg, #2a2a2a, #0a0a0a);
    border: 1px solid var(--border-strong);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--text-primary);
}}
.grok-sidebar-brand-title {{
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--text-primary);
    letter-spacing: 0.02em;
    margin: 0;
    line-height: 1.2;
}}
/* ── MAIN CONTENT (responsive to sidebar state) ─────────────────────── */
[data-testid="stAppViewContainer"] {{
    width: 100% !important;
    max-width: 100vw !important;
}}
[data-testid="stMain"],
section.main {{
    flex: 1 1 0% !important;
    min-width: 0 !important;
    max-width: 100% !important;
    transition: flex 0.2s ease, width 0.2s ease, max-width 0.2s ease;
}}
.main .block-container,
[data-testid="stMainBlockContainer"] {{
    padding-top: 0.15rem !important;
    padding-bottom: 1rem !important;
    width: 100% !important;
    transition: max-width 0.2s ease, padding 0.2s ease;
}}
html.grok-sb-expanded .main .block-container,
html.grok-sb-expanded [data-testid="stMainBlockContainer"],
[data-testid="stSidebar"][aria-expanded="true"] ~ [data-testid="stMain"] .main .block-container,
[data-testid="stSidebar"][aria-expanded="true"] ~ [data-testid="stMain"] [data-testid="stMainBlockContainer"] {{
    max-width: min(1680px, 100%) !important;
}}
html.grok-sb-collapsed .main .block-container,
html.grok-sb-collapsed [data-testid="stMainBlockContainer"],
[data-testid="stSidebar"][aria-expanded="false"] ~ [data-testid="stMain"] .main .block-container,
[data-testid="stSidebar"][aria-expanded="false"] ~ [data-testid="stMain"] [data-testid="stMainBlockContainer"] {{
    max-width: 100% !important;
    padding-left: 1.25rem !important;
    padding-right: 1.25rem !important;
}}

/* Chart + analysis split on wide screens */
.grok-main-grid marker {{
    display: none;
}}

/* Zero-height host for st.html sidebar cursor-fix script */
[data-testid="stHtml"]:has(#grok-sidebar-cursor-fix) {{
    height: 0 !important;
    min-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
    border: none !important;
}}

/* ── SIDEBAR: FIXED WIDTH, NON-RESIZABLE ───────────────────────────── */
/*
 * Streamlit 1.52+: data-testid="stSidebar" IS the <section> (Resizable as=StyledSidebar).
 * Direct children: [data-testid="stSidebarContent"] + resize-handle div.
 * Only hide the handle — never stSidebarContent.
 */
[data-testid="stSidebar"] {{
    position: relative !important;
    background: var(--bg-elevated) !important;
    border-right: 1px solid var(--border-subtle) !important;
    box-shadow: none !important;
    cursor: default !important;
    resize: none !important;
    transition: width 0.2s ease, min-width 0.2s ease, flex-basis 0.2s ease;
}}
@media (min-width: 769px) {{
    [data-testid="stSidebar"][aria-expanded="true"] {{
        width: var(--sidebar-width) !important;
        min-width: var(--sidebar-width) !important;
        max-width: var(--sidebar-width) !important;
        flex: 0 0 var(--sidebar-width) !important;
    }}
    [data-testid="stSidebar"][aria-expanded="false"] {{
        width: var(--sidebar-collapsed-width) !important;
        min-width: var(--sidebar-collapsed-width) !important;
        max-width: var(--sidebar-collapsed-width) !important;
        flex: 0 0 var(--sidebar-collapsed-width) !important;
        overflow: hidden !important;
        /* Streamlit 1.58 applies transform: translateX(-300px) via emotion class
           when collapsed, sliding the sidebar off-screen. Override so the
           collapsed strip stays visible at the left edge. */
        transform: none !important;
    }}
    [data-testid="stSidebar"][aria-expanded="false"] ~ [data-testid="stMain"],
    [data-testid="stSidebar"][aria-expanded="false"] ~ section.main {{
        flex: 1 1 auto !important;
        width: auto !important;
        max-width: 100% !important;
        margin-left: 0 !important;
    }}
}}
[data-testid="stSidebar"][aria-expanded="true"] [data-testid="stSidebarContent"] {{
    width: 100% !important;
    min-width: 100% !important;
    max-width: 100% !important;
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    pointer-events: auto !important;
}}
/* Collapsed sidebar: keep stSidebarContent visible so the expand button
   (stSidebarCollapseButton inside stSidebarHeader) remains clickable.
   Hide only the user content area. */
[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarContent"] {{
    display: block !important;
    visibility: visible !important;
    width: 100% !important;
    min-width: 100% !important;
    max-width: 100% !important;
    opacity: 1 !important;
    pointer-events: auto !important;
    overflow: visible !important;
}}
/* Hide user content when collapsed */
[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarUserContent"] {{
    display: none !important;
}}
/* Center the expand button in the collapsed sidebar strip */
[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarHeader"] {{
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 0 !important;
    height: 100% !important;
    min-height: 2.5rem !important;
}}
[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stLogoSpacer"] {{
    display: none !important;
}}
/* ── COLLAPSE BUTTON: visible on desktop (Streamlit 1.58 hides it by default) ── */
/* Streamlit 1.58 sets visibility:hidden on stSidebarCollapseButton, only showing
   it at max-width:576px. Override so desktop users can collapse the sidebar. */
@media (min-width: 577px) {{
    [data-testid="stSidebar"][aria-expanded="true"] [data-testid="stSidebarCollapseButton"] {{
        visibility: visible !important;
    }}
    [data-testid="stSidebar"][aria-expanded="true"] [data-testid="stSidebarCollapseButton"] button {{
        visibility: visible !important;
        cursor: pointer !important;
    }}
}}
/* Style the expand button to be visible in the narrow strip */
[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarCollapseButton"] {{
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    pointer-events: auto !important;
}}
[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarCollapseButton"] button {{
    cursor: pointer !important;
}}
/* CURSOR FIX — hide only resize handle, keep stSidebarContent visible */
[data-testid="stSidebar"] > div:not([data-testid="stSidebarContent"]),
[data-testid="stSidebar"] > span,
[data-testid="stSidebar"] .react-resizable-handle,
[data-testid="stSidebar"] .react-resizable-handle-e,
[data-testid="stSidebar"] .react-resizable-handle::after,
[data-testid="stSidebarResizeHandle"] {{
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
    height: 0 !important;
    opacity: 0 !important;
    pointer-events: none !important;
    cursor: default !important;
    resize: none !important;
}}
/* Transparent shield over sidebar/main boundary — blocks col-resize hover zone */
/* 手機版「完整參數」區塊優化 */
@media (max-width: 768px) {{
    /* ── 重新排盤按鈕：醒目、大點擊區 ── */
    .mobile-run-top {{
        margin: 0 !important;
        padding: 0 0 0.2rem 0 !important;
    }}
    .mobile-run-top button {{
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        padding: 0.6rem 1rem !important;
        min-height: 3rem !important;
    }}

    /* ── chart-stage-marker：手機版需要上方呼吸空間 ── */
    .chart-stage-marker {{
        padding: 0 !important;
        margin: 0 !important;
    }}
    div[data-testid="stVerticalBlock"]:has(> .chart-stage-marker) {{
        margin-bottom: 0 !important;
        margin-top: 1rem !important;
        padding: 0.6rem 0.5rem 0 !important;
    }}
    /* 緊鄰 chart-stage-marker 的下一個 block：消除上方 margin */
    div[data-testid="stVerticalBlock"]:has(> .chart-stage-marker) + div[data-testid="stVerticalBlock"] {{
        margin-top: 0 !important;
    }}

    /* ── iframe 容器：保留上方 0.5rem 間距讓資訊框與圓盤分離 ── */
    div[data-testid="stVerticalBlock"]:has(iframe),
    div[data-testid="stElementContainer"]:has(iframe) {{
        margin-bottom: 0 !important;
        margin-top: 0.5rem !important;
        padding: 0 !important;
    }}
    iframe {{
        margin-bottom: 0 !important;
    }}

    /* ── chart-mobile-params + chart-explanation-anchor：貼緊（零間隙） ── */
    div[data-testid="stVerticalBlock"]:has(> .chart-mobile-params),
    div[data-testid="stVerticalBlock"]:has(> .chart-explanation-anchor) {{
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }}
    div[data-testid="stVerticalBlock"]:has(> .chart-mobile-params) [data-testid="stExpander"],
    div[data-testid="stVerticalBlock"]:has(> .chart-explanation-anchor) [data-testid="stExpander"] {{
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }}

    .chart-mobile-params {{
        margin-top: 0 !important;     /* 改成 0 */
        margin-bottom: 0 !important;
    }}
    .chart-mobile-params .streamlit-expanderHeader {{
        padding: 8px 12px !important;
        font-size: 0.9rem !important;
    }}
    .chart-mobile-params .streamlit-expanderContent {{
        padding: 8px 12px 12px !important;   /* 增加底部一點呼吸感 */
    }}
    .chart-meta-detail-row-mobile {{
        margin-bottom: 4px !important;
        padding: 4px 0 !important;
    }}
    .chart-mobile-three-five {{
        margin-top: 8px !important;
    }}
    .chart-mobile-param-heading {{
        font-size: 0.85rem !important;
        margin-bottom: 4px !important;
    }}
    .chart-mobile-param-body {{
        font-size: 0.82rem !important;
        line-height: 1.4 !important;
    }}

    /* 新增：徹底消除排盤與完整參數之間的間隙 */
    div[data-testid="stVerticalBlock"] {{
        gap: 0 !important;
    }}
    div[data-testid="stVerticalBlock"]:has(> .chart-stage-marker) {{
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }}
    div[data-testid="stVerticalBlock"]:has(> .chart-mobile-params) {{
        margin-top: 0 !important;
        padding-top: 0 !important;
    }}
    div[data-testid="stVerticalBlock"]:has(iframe),
    div[data-testid="stElementContainer"]:has(iframe) {{
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }}
}}

@media (min-width: 769px) {{
    [data-testid="stSidebar"][aria-expanded="true"]::after {{
        content: "" !important;
        position: fixed !important;
        top: 0 !important;
        bottom: 0 !important;
        left: calc(var(--sidebar-width) - 8px) !important;
        width: 16px !important;
        z-index: 999999 !important;
        cursor: default !important;
        pointer-events: auto !important;
        background: transparent !important;
    }}
}}

[data-testid="stSidebar"],
[data-testid="stSidebar"] [data-testid="stSidebarContent"] {{
    cursor: default !important;
}}
[data-testid="stSidebar"] button,
[data-testid="stSidebar"] [role="button"],
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebar"] a,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] summary,
[data-testid="stSidebar"] [data-baseweb="select"] {{
    cursor: pointer !important;
}}
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea {{
    cursor: text !important;
}}

/* Simplified sidebar shell */
.grok-sidebar-shell {{
    padding: 0.15rem 0 0.5rem 0;
}}
.grok-sidebar-shell [data-testid="stExpander"] {{
    margin: 0.35rem 0 !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-sm) !important;
    background: transparent !important;
}}
.grok-sidebar-shell [data-testid="stExpander"] summary {{
    font-size: 0.84rem !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
    padding: 0.4rem 0.55rem !important;
}}
.grok-sidebar-shell [data-testid="stExpanderDetails"] {{
    padding: 0 0.55rem 0.55rem !important;
    border-top: none !important;
}}
.grok-sidebar-instant .stButton > button {{
    background: transparent !important;
    color: var(--text-secondary) !important;
    border: 1px solid var(--border-subtle) !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    padding: 0.35rem 0.65rem !important;
    transform: none !important;
}}
.grok-sidebar-instant .stButton > button:hover:not(:disabled) {{
    color: var(--text-primary) !important;
    border-color: var(--border-strong) !important;
    opacity: 1 !important;
}}
.grok-run-chart {{
    margin: 0.5rem 0 0.35rem 0;
}}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {{
    font-family: var(--font-sans) !important;
    color: var(--text-primary) !important;
    border: none !important;
    text-align: left !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    letter-spacing: 0;
    padding: 0;
}}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {{
    color: var(--text-secondary) !important;
    font-size: 0.84rem !important;
}}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] span {{
    color: var(--text-primary) !important;
    font-weight: 500 !important;
}}
[data-testid="stSidebar"] hr {{
    border-color: var(--border-subtle) !important;
    margin: 0.65rem 0 !important;
}}

/* ── INPUTS ─────────────────────────────────────────────────────────── */
input, textarea, select,
.stTextInput input, .stNumberInput input, .stTextArea textarea,
.stDateInput input, .stTimeInput input {{
    background-color: var(--bg-surface) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
}}
input:focus, textarea:focus,
.stTextInput input:focus, .stNumberInput input:focus {{
    border-color: var(--border-strong) !important;
    box-shadow: 0 0 0 2px var(--accent-glow) !important;
    outline: none !important;
}}
.stSelectbox [data-baseweb="select"] > div {{
    background-color: var(--bg-surface) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
}}
[data-baseweb="popover"] [data-baseweb="menu"] {{
    background-color: var(--bg-surface) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-sm) !important;
}}
[data-baseweb="popover"] [role="option"] {{
    background-color: var(--bg-surface) !important;
    color: var(--text-primary) !important;
}}
[data-baseweb="popover"] [role="option"]:hover {{
    background-color: var(--bg-hover) !important;
}}

/* ── TOGGLES (Grok-style) ───────────────────────────────────────────── */
[data-testid="stToggle"] label {{
    font-size: 0.82rem !important;
}}
[data-testid="stToggle"] [data-testid="stWidgetLabel"] {{
    color: var(--text-primary) !important;
}}
/* Widget labels app-wide — brighter than Streamlit default fade */
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span,
[data-testid="stWidgetLabel"] label {{
    color: var(--text-secondary) !important;
}}
[data-testid="stWidgetLabel"] {{
    color: var(--text-secondary) !important;
}}
/* Captions / helper text */
[data-testid="stCaptionContainer"],
[data-testid="stCaption"],
.stCaption {{
    color: var(--text-muted) !important;
}}

/* ── BUTTONS ────────────────────────────────────────────────────────── */
/* White buttons: force black text (theme textColor is light on dark base) */
.stButton > button,
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"],
[data-testid="stSidebar"] .stButton > button[kind="primary"],
[data-testid="stSidebar"] .grok-run-chart .stButton > button {{
    background: var(--text-primary) !important;
    color: #0a0a0a !important;
    -webkit-text-fill-color: #0a0a0a !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    font-size: 0.84rem !important;
    letter-spacing: 0.02em !important;
    padding: 0.45rem 0.9rem !important;
    transition: opacity 0.15s ease, transform 0.15s ease !important;
    box-shadow: none !important;
}}
.stButton > button p,
.stButton > button span,
.stButton > button div,
.stButton > button[kind="primary"] p,
.stButton > button[kind="primary"] span,
.stButton > button[kind="primary"] div,
[data-testid="stSidebar"] .grok-run-chart .stButton > button p,
[data-testid="stSidebar"] .grok-run-chart .stButton > button span,
[data-testid="stSidebar"] .grok-run-chart .stButton > button div {{
    color: #0a0a0a !important;
    -webkit-text-fill-color: #0a0a0a !important;
}}
.stButton > button:hover:not(:disabled),
.stButton > button[kind="primary"]:hover:not(:disabled),
[data-testid="stSidebar"] .grok-run-chart .stButton > button:hover:not(:disabled) {{
    color: #0a0a0a !important;
    -webkit-text-fill-color: #0a0a0a !important;
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}}
.stButton > button:hover:not(:disabled) p,
.stButton > button:hover:not(:disabled) span,
.stButton > button:hover:not(:disabled) div {{
    color: #0a0a0a !important;
    -webkit-text-fill-color: #0a0a0a !important;
}}
.stButton > button:active:not(:disabled) {{
    transform: translateY(0) !important;
}}
.stButton > button:disabled {{
    background: var(--bg-hover) !important;
    color: var(--text-muted) !important;
    -webkit-text-fill-color: var(--text-muted) !important;
}}
[data-testid="stSidebar"] .stButton > button[kind="primary"],
[data-testid="stSidebar"] .grok-run-chart .stButton > button {{
    width: 100%;
}}

/* ── TABS ───────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
    background: transparent !important;
    border-bottom: 1px solid var(--border-subtle) !important;
    gap: 0.25rem !important;
    padding-bottom: 0 !important;
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    color: var(--text-secondary) !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    border-radius: var(--radius-sm) var(--radius-sm) 0 0 !important;
    padding: 0.5rem 0.85rem !important;
    border-bottom: 2px solid transparent !important;
}}
.stTabs [data-baseweb="tab"]:hover {{
    color: var(--text-primary) !important;
    background: var(--accent-glow) !important;
}}
.stTabs [aria-selected="true"][data-baseweb="tab"] {{
    color: var(--text-primary) !important;
    border-bottom: 2px solid var(--text-primary) !important;
    font-weight: 600 !important;
}}
.stTabs [data-baseweb="tab-highlight"] {{
    background-color: var(--text-primary) !important;
    height: 2px !important;
}}
.stTabs [data-baseweb="tab-panel"] {{
    background: transparent !important;
    padding-top: 1rem !important;
}}

/* ── EXPANDERS ──────────────────────────────────────────────────────── */
.stExpander {{
    background-color: var(--bg-elevated) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-md) !important;
    margin: 0.5rem 0 !important;
    overflow: hidden;
}}
.stExpander summary {{
    color: var(--text-primary) !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    padding: 0.6rem 0.85rem !important;
    list-style: none;
    transition: background 0.15s ease;
}}
.stExpander summary:hover {{
    background: rgba(255, 255, 255, 0.04) !important;
}}
.stExpander summary::-webkit-details-marker {{
    display: none;
}}
.stExpander [data-testid="stExpanderDetails"] {{
    background: var(--bg-elevated) !important;
    border-top: 1px solid var(--border-subtle) !important;
    color: var(--text-secondary) !important;
    padding: 0.6rem 0.85rem 0.8rem !important;
    font-size: 0.82rem !important;
    line-height: 1.65 !important;
}}

/* ── CARDS / METRICS ────────────────────────────────────────────────── */
.grok-card {{
    background: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 0.85rem 1rem;
    margin-bottom: 0.65rem;
}}
.grok-card-title {{
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-secondary);
    margin: 0 0 0.35rem 0;
}}
.grok-card-body {{
    font-size: 0.86rem;
    color: var(--text-primary);
    line-height: 1.5;
    margin: 0;
}}

/* ── CHART META (desktop right panel + mobile stage overlay) ─────────── */
.chart-summary-desktop {{
    display: flex;
}}
.chart-stage-mobile-meta {{
    display: none;
}}
@media (min-width: 900px) {{
    div[data-testid="stVerticalBlock"]:has(> .chart-stage-mobile-meta) {{
        display: none !important;
    }}
}}
.chart-meta-gz-row {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem;
    margin-bottom: 0.7rem;
}}
.chart-meta-pillar {{
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-width: 3.1rem;
    padding: 0.4rem 0.5rem 0.35rem;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
}}
.chart-meta-pillar-label {{
    font-size: 0.62rem;
    font-weight: 500;
    color: var(--text-muted);
    line-height: 1.2;
    margin-bottom: 0.15rem;
}}
.chart-meta-pillar-value {{
    font-size: 0.92rem;
    font-weight: 600;
    color: var(--text-primary);
    line-height: 1.2;
    letter-spacing: 0.04em;
}}
.chart-meta-secondary {{
    font-size: 0.78rem;
    color: var(--text-muted);
    line-height: 1.5;
    margin: 0.15rem 0 0 0;
}}
.chart-meta-kingyear {{
    margin-top: 0.2rem !important;
}}
.grok-card-v2-bureau-line {{
    font-size: 0.92rem;
    line-height: 1.45;
}}
.chart-side-hero .chart-meta-gz-row {{
    margin-bottom: 0.45rem;
    width: 15% !important;
    min-width: 170px !important;
    max-width: 220px !important;
    flex: 0 0 15% !important;
    box-sizing: border-box;
}}
.chart-meta-detail-row {{
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
    padding: 0.45rem 0 0.55rem;
    border-bottom: 1px solid var(--border-subtle);
    margin-bottom: 0.15rem;
}}
.chart-meta-detail-label {{
    font-size: 0.72rem;
    font-weight: 500;
    color: var(--text-muted);
    letter-spacing: 0.03em;
}}
.chart-meta-detail-value {{
    font-size: 0.84rem;
    color: var(--text-secondary);
    line-height: 1.45;
    word-break: break-word;
}}
.chart-side-params-grid {{
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0 0.75rem;
}}
.chart-side-params .chart-meta-detail-row {{
    border-bottom: 1px solid var(--border-subtle);
    margin-bottom: 0;
}}
.chart-side-params .chart-meta-detail-row:nth-last-child(-n+2) {{
    border-bottom: none;
}}
@media (max-width: 520px) {{
    .chart-side-params-grid {{
        grid-template-columns: 1fr;
    }}
    .chart-side-params .chart-meta-detail-row:nth-last-child(-n+2) {{
        border-bottom: 1px solid var(--border-subtle);
    }}
    .chart-side-params .chart-meta-detail-row:last-child {{
        border-bottom: none;
    }}
}}

/* ── CHART STAGE (P1) ───────────────────────────────────────────────── */
.chart-stage-marker {{
    display: none !important;
    height: 0 !important;
    width: 0 !important;
}}
div[data-testid="stVerticalBlock"]:has(> .chart-stage-marker) {{
    position: relative;
    align-items: center;
    background: transparent;
    border: none;
    border-radius: 0;
    padding: 0.5rem 0.5rem 0;
    margin-bottom: 0;
}}
@media (max-width: 899px) {{
    div[data-testid="stVerticalBlock"]:has(> .chart-stage-marker) {{
        border: none !important;
        background: transparent !important;
        padding: 0.6rem 0.5rem 0 !important;
        margin-bottom: 0 !important;
        margin-top: 0.8rem !important;
    }}
    /* iframe 容器：保留上方 0.5rem 讓資訊框與圓盤分離 */
    div[data-testid="stVerticalBlock"]:has(iframe) {{
        margin-top: 0.5rem !important;
        margin-bottom: 0 !important;
        padding: 0 !important;
        gap: 0 !important;
    }}
    div[data-testid="stElementContainer"]:has(iframe) {{
        margin-bottom: 0 !important;
        margin-top: 0.5rem !important;
        padding: 0 !important;
    }}
    .stHtml {{
        margin: 0 !important;
        padding: 0 !important;
    }}
    /* Tighten the iframe element itself — reduce inherent iframe spacing */
    iframe {{
        margin-bottom: 0 !important;
    }}
    /* chart-mobile-params: zero gap from chart above */
    div[data-testid="stVerticalBlock"]:has(> .chart-mobile-params) {{
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding-top: 0 !important;
    }}
    div[data-testid="stVerticalBlock"]:has(> .chart-mobile-params) [data-testid="stExpander"] {{
        margin-top: 0 !important;
        margin-bottom: 0.15rem !important;
    }}
    div[data-testid="stHorizontalBlock"]:has(.chart-stage-marker) {{
        margin-bottom: 0 !important;
        gap: 0.35rem !important;
    }}
    div[data-testid="stVerticalBlock"]:has(> .chart-explanation-anchor) {{
        margin-top: 0.1rem !important;
        margin-bottom: 0 !important;
    }}
    div[data-testid="stVerticalBlock"]:has(> .chart-explanation-anchor) [data-testid="stExpander"] {{
        margin-top: 0 !important;
        margin-bottom: 0.25rem !important;
    }}
    .chart-mobile-param-heading {{
        font-size: 0.82rem !important;
        font-weight: 600;
        color: var(--text-muted);
        margin: 0.5rem 0 0.25rem 0;
    }}
    .chart-mobile-param-body {{
        font-size: 0.86rem !important;
        color: var(--text-muted);
        line-height: 1.5;
        margin: 0;
        word-break: break-word;
    }}
    /* ── 資訊欄／卡片群：手機版加大字體以提升可讀性 ── */
    .chart-meta-pillar-label {{
        font-size: 0.72rem !important;
    }}
    .chart-meta-pillar-value {{
        font-size: 0.98rem !important;
    }}
    .chart-meta-secondary {{
        font-size: 0.85rem !important;
    }}
    .chart-meta-detail-label {{
        font-size: 0.8rem !important;
    }}
    .chart-meta-detail-value {{
        font-size: 0.9rem !important;
    }}
    .grok-card-v2-title {{
        font-size: 0.82rem !important;
    }}
    .grok-card-v2-value {{
        font-size: 1.05rem !important;
    }}
    .grok-card-v2-lead {{
        font-size: 0.88rem !important;
    }}
    .grok-card-v2-body,
    .grok-card-v2-three-five .grok-card-v2-body {{
        font-size: 0.88rem !important;
    }}
    .grok-card-v2-sub {{
        font-size: 0.84rem !important;
    }}
    .grok-card-v2-badge {{
        font-size: 0.8rem !important;
    }}
    .grok-card-v2-details {{
        font-size: 0.84rem !important;
    }}
    .chart-stage-mobile-meta {{
        display: block;
        position: static;
        width: 100%;
        max-width: 100%;
        margin: 0 0 0.6rem 0 !important;
        padding: 0 0 0.3rem 0 !important;
    }}
    .chart-mobile-params-anchor {{
        display: none !important;
    }}
    .chart-print-meta {{
        font-size: 0.72rem !important;
        line-height: 1.42;
        color: var(--text-secondary);
        white-space: pre-wrap;
        word-break: break-word;
        margin: 0;
        padding: 0.45rem 0.55rem 0.4rem;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-sm);
    }}
    div[data-testid="stVerticalBlock"]:has(> .chart-stage-mobile-meta) + div[data-testid="stVerticalBlock"]:has(> .chart-stage-marker) {{
        margin-top: 0 !important;
    }}
    /* taiyi-chart-seam-anchor: zero height, zero margin */
    .taiyi-chart-seam-anchor {{
        display: none !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    div[data-testid="stVerticalBlock"]:has(> .taiyi-chart-seam-anchor) {{
        margin: 0 !important;
        padding: 0 !important;
        height: 0 !important;
    }}
}}
div[data-testid="stVerticalBlock"]:has(> .chart-stage-marker) iframe {{
    max-width: 100% !important;
    margin-left: auto !important;
    margin-right: auto !important;
    display: block;
}}
div[data-testid="stVerticalBlock"]:has(> .chart-stage-marker) .taiyi-shell {{
    max-width: 100%;
    margin-left: auto;
    margin-right: auto;
}}
/* ── 桌面版：排盤置中，首屏完整可見（無捲動） ── */
@media (min-width: 900px) {{
    .main .block-container,
    [data-testid="stMainBlockContainer"] {{
        padding-bottom: 0.1rem !important;
    }}
    div[data-testid="stVerticalBlock"]:has(> .chart-stage-marker) iframe {{
        max-width: 100% !important;
        width: 100% !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }}
    div[data-testid="stVerticalBlock"]:has(> .chart-stage-marker) .taiyi-shell {{
        max-width: 100%;
        margin-left: auto;
        margin-right: auto;
    }}
    div[data-testid="stVerticalBlock"]:has(> .chart-stage-marker) {{
        padding: 0.1rem 0.1rem 0 !important;
        margin-bottom: 0 !important;
        overflow: visible !important;
    }}
    /* tabs 緊貼 topnav，無間距（桌面版不需要避開 icon）*/
    div[data-testid="stTabs"] {{
        margin-top: 0 !important;
        gap: 0 !important;
    }}
    /* tab 內容區上方無 padding */
    div[data-testid="stTabContent"] {{
        padding-top: 0.1rem !important;
    }}
    /* 隱藏 Streamlit 預設 header */
    [data-testid="stHeader"] {{
        min-height: 0 !important;
        height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        visibility: hidden !important;
    }}
    /* 水平欄位間無 gap */
    div[data-testid="stHorizontalBlock"]:has(.chart-stage-marker) {{
        gap: 0.25rem !important;
        margin-bottom: 0 !important;
    }}
    /* Timeline blocks flush against chart — zero gap */
    div[data-testid="stHorizontalBlock"]:has(.chart-stage-marker) + div[data-testid="stVerticalBlock"] {{
        margin-top: 0 !important;
        padding-top: 0 !important;
    }}
    /* seam anchor 零高度 */
    .taiyi-chart-seam-anchor {{
        display: none !important;
        height: 0 !important;
    }}
    div[data-testid="stVerticalBlock"]:has(> .taiyi-chart-seam-anchor) {{
        margin: 0 !important;
        padding: 0 !important;
        height: 0 !important;
    }}
}}

/* ── CHART SIDE PANEL / CARD V2 ──────────────────────────────────────── */
.chart-side-panel {{
    flex-direction: column;
    gap: 0.65rem;
    padding-top: 0.35rem;
}}
@media (min-width: 900px) {{
    .chart-side-panel {{
        position: sticky;
        top: 4.5rem;
    }}
}}
@media (max-width: 899px) {{
    .chart-summary-desktop {{
        display: none !important;
    }}
}}
.grok-card-v2 {{
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 0.95rem 1.05rem;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
    transition: border-color 0.2s ease, background 0.2s ease;
}}
.grok-card-v2:hover {{
    border-color: rgba(255, 255, 255, 0.14);
    background: rgba(255, 255, 255, 0.045);
}}
.grok-card-v2-title {{
    font-size: 0.74rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    text-transform: none;
    color: var(--text-muted);
    margin: 0 0 0.45rem 0;
}}
.grok-card-v2-pillars {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.35rem;
}}
.grok-card-v2-value {{
    font-size: 1.02rem;
    font-weight: 600;
    color: var(--text-primary);
    line-height: 1.35;
    margin: 0;
}}
.grok-card-v2-lead {{
    font-size: 0.8rem;
    font-weight: 500;
    color: var(--text-primary);
    line-height: 1.45;
    margin: 0 0 0.35rem 0;
}}
.grok-card-v2-body {{
    font-size: 0.8rem;
    color: var(--text-muted);
    line-height: 1.55;
    margin: 0;
    word-break: break-word;
}}
.grok-card-v2-sub {{
    font-size: 0.76rem;
    color: var(--text-muted);
    line-height: 1.4;
    margin: 0.35rem 0 0 0;
}}
.grok-card-v2-badge {{
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--text-secondary);
    padding: 0.15rem 0.45rem;
    border: 1px solid var(--border-subtle);
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.04);
}}
.grok-card-v2-preview {{
    margin-bottom: 0.3rem;
}}
.grok-card-v2-details {{
    font-size: 0.76rem;
    margin-top: 0.2rem;
}}
.grok-card-v2-details summary {{
    color: var(--text-muted);
    cursor: pointer;
    user-select: none;
    list-style: none;
    margin-bottom: 0.3rem;
}}
.grok-card-v2-details summary::-webkit-details-marker {{
    display: none;
}}
.grok-card-v2-three-five .grok-card-v2-body {{
    font-size: 0.78rem;
}}

/* ── YUN TIMELINE + CARDS (統運十二運) ──────────────────────────────── */
.yun-section {{
    margin: 0.5rem 0 0.8rem;
    padding: 0;
}}
.yun-query-note {{
    font-size: 0.78rem;
    color: var(--text-muted);
    padding: 0.4rem 0.65rem;
    margin-bottom: 0.5rem;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
}}

/* ── 十二運時間軸 ──────────────────────────────────── */
.yun-timeline-container {{
    padding: 0.85rem 1rem 0.65rem;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    margin: 0 0 0.35rem 0;
}}
.yun-timeline-header {{
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin-bottom: 0.55rem;
}}
.yun-timeline-label {{
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--text-secondary);
    letter-spacing: 0.04em;
}}
.yun-cycle-num {{
    color: var(--text-primary);
    font-weight: 700;
    font-size: 0.88rem;
}}
.yun-timeline-sub {{
    font-size: 0.72rem;
    color: var(--text-muted);
    font-variant-numeric: tabular-nums;
}}
.yun-timeline-track {{
    display: flex;
    gap: 2px;
    height: 38px;
    border-radius: 6px;
    overflow: hidden;
}}
.yun-timeline-seg {{
    flex-grow: var(--seg-flex, 100);
    flex-shrink: 0;
    flex-basis: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.025);
    border: none;
    border-top: 2px solid transparent;
    border-bottom: 2px solid transparent;
    cursor: pointer;
    transition: background 0.2s ease, border-color 0.2s ease;
    position: relative;
    overflow: hidden;
    padding: 0;
    color: inherit;
    font: inherit;
}}
.yun-timeline-seg:hover {{
    background: rgba(255, 255, 255, 0.06);
}}
.yun-timeline-seg.yun-current {{
    background: color-mix(in srgb, var(--yun-color) 16%, transparent);
    border-top-color: var(--yun-color);
    border-bottom-color: var(--yun-color);
}}
.yun-timeline-seg-name {{
    font-size: 0.66rem;
    font-weight: 600;
    color: var(--text-secondary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100%;
    padding: 0 3px;
}}
.yun-timeline-seg.yun-current .yun-timeline-seg-name {{
    color: var(--text-primary);
}}
.yun-timeline-seg-years {{
    font-size: 0.58rem;
    color: var(--text-muted);
    font-variant-numeric: tabular-nums;
}}
.yun-timeline-marker {{
    position: absolute;
    bottom: 2px;
    left: 50%;
    transform: translateX(-50%);
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--yun-color);
    animation: yun-pulse 2s ease-in-out infinite;
}}
@keyframes yun-pulse {{
    0%, 100% {{ opacity: 0.5; }}
    50% {{ opacity: 1; box-shadow: 0 0 6px var(--yun-color); }}
}}
.yun-timeline-progress {{
    height: 4px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 999px;
    margin-top: 0.5rem;
    overflow: hidden;
    position: relative;
}}
.yun-timeline-progress-bar {{
    height: 100%;
    background: linear-gradient(90deg, var(--yun-color), color-mix(in srgb, var(--yun-color) 60%, transparent));
    border-radius: 999px;
    transition: width 0.4s ease;
    display: flex;
    align-items: center;
    padding-left: 0.5rem;
}}
.yun-timeline-progress-text {{
    font-size: 0.58rem;
    font-weight: 600;
    color: var(--text-primary);
    white-space: nowrap;
    font-variant-numeric: tabular-nums;
}}

/* ── 當前運勢卡片 ──────────────────────────────────── */
.yun-card {{
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--border-subtle);
    border-left: 3px solid var(--yun-color, var(--text-muted));
    border-radius: 14px;
    padding: 0.95rem 1.05rem;
    margin-bottom: 0.65rem;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}}
.yun-card--current {{
    box-shadow: 0 0 0 1px color-mix(in srgb, var(--yun-color) 24%, transparent),
                0 4px 18px rgba(0, 0, 0, 0.28);
}}
.yun-card-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.7rem;
}}
.yun-card-yun-name {{
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
}}
.yun-card-ji-badge {{
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    font-size: 0.72rem;
    font-weight: 500;
    padding: 0.18rem 0.55rem;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid var(--border-subtle);
}}
.yun-ji-dot {{
    width: 7px;
    height: 7px;
    border-radius: 50%;
    flex-shrink: 0;
}}
.yun-ji-fu .yun-ji-dot    {{ background: var(--yun-ji-fu); }}
.yun-ji-ji .yun-ji-dot    {{ background: var(--yun-ji-ji); }}
.yun-ji-xiong .yun-ji-dot {{ background: var(--yun-ji-xiong); }}
.yun-ji-zai .yun-ji-dot   {{ background: var(--yun-ji-zai); }}
.yun-ji-fu    {{ color: var(--yun-ji-fu); }}
.yun-ji-ji    {{ color: var(--yun-ji-ji); }}
.yun-ji-xiong {{ color: var(--yun-ji-xiong); }}
.yun-ji-zai   {{ color: var(--yun-ji-zai); }}

.yun-card-body {{
    display: flex;
    gap: 1rem;
    align-items: flex-start;
}}
.yun-card-gua {{
    display: flex;
    flex-direction: column;
    align-items: center;
    min-width: 3.5rem;
    padding: 0.3rem 0.5rem;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
}}
.yun-card-gua-symbol {{
    font-size: 1.75rem;
    line-height: 1;
    color: var(--text-primary);
    margin-bottom: 0.2rem;
}}
.yun-card-gua-name {{
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--text-secondary);
}}
.yun-card-info {{
    flex: 1;
    min-width: 0;
}}
.yun-card-yao {{
    font-size: 0.88rem;
    font-weight: 500;
    color: var(--text-primary);
    margin-bottom: 0.3rem;
}}
.yun-card-meta {{
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    font-size: 0.72rem;
    color: var(--text-muted);
    font-variant-numeric: tabular-nums;
    margin-bottom: 0.35rem;
}}
.yun-card-duan {{
    font-size: 0.8rem;
    color: var(--text-secondary);
    line-height: 1.5;
}}
.yun-card-gua-seq {{
    display: flex;
    gap: 0.25rem;
    flex-wrap: wrap;
    margin-top: 0.45rem;
}}
.yun-card-gua-seq-item {{
    font-size: 0.68rem;
    padding: 0.1rem 0.35rem;
    border-radius: 4px;
    background: rgba(255, 255, 255, 0.03);
    color: var(--text-muted);
    border: 1px solid transparent;
}}
.yun-card-gua-seq-current {{
    color: var(--text-primary);
    font-weight: 600;
    background: color-mix(in srgb, var(--yun-color) 14%, transparent);
    border-color: var(--yun-color);
}}
.yun-card-progress {{
    height: 3px;
    background: rgba(255, 255, 255, 0.06);
    border-radius: 999px;
    margin: 0.7rem 0 0;
    overflow: hidden;
}}
.yun-card-progress-fill {{
    height: 100%;
    background: var(--yun-color);
    border-radius: 999px;
    transition: width 0.4s ease;
}}
.yun-card-details {{
    margin-top: 0.6rem;
    font-size: 0.78rem;
}}
.yun-card-details summary {{
    color: var(--text-muted);
    cursor: pointer;
    user-select: none;
    list-style: none;
    margin-bottom: 0.3rem;
}}
.yun-card-details summary::-webkit-details-marker {{
    display: none;
}}
.yun-card-details-body {{
    color: var(--text-secondary);
    line-height: 1.65;
    margin: 0.35rem 0 0;
}}

/* ── 折疊子卡片 ──────────────────────────────────── */
.yun-sub-card {{
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid var(--border-subtle);
    border-radius: 10px;
    margin-bottom: 0.4rem;
    overflow: hidden;
    transition: background 0.15s ease;
}}
.yun-sub-card[open] {{
    background: rgba(255, 255, 255, 0.035);
}}
.yun-sub-card-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.55rem 0.85rem;
    cursor: pointer;
    user-select: none;
    list-style: none;
    transition: background 0.15s ease;
}}
.yun-sub-card-header:hover {{
    background: rgba(255, 255, 255, 0.03);
}}
.yun-sub-card-header::-webkit-details-marker {{
    display: none;
}}
.yun-sub-card-title {{
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--text-secondary);
    letter-spacing: 0.02em;
}}
.yun-sub-card-preview {{
    font-size: 0.74rem;
    color: var(--text-muted);
    font-variant-numeric: tabular-nums;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 55%;
}}
.yun-sub-card-body {{
    padding: 0 0.85rem 0.65rem;
    font-size: 0.78rem;
    color: var(--text-secondary);
    line-height: 1.6;
}}
.yun-sub-card-body p {{
    margin: 0.15rem 0;
}}
.yun-sub-card-note {{
    color: var(--text-muted) !important;
    font-size: 0.72rem !important;
    margin-top: 0.3rem !important;
}}

/* ── 卦象觀象六爻列表 ──────────────────────────────── */
.yun-gua-xiang {{
    color: var(--text-primary) !important;
    font-size: 0.82rem !important;
    margin-bottom: 0.4rem !important;
}}
.yun-gua-yao-current-line {{
    color: var(--text-primary) !important;
    font-weight: 500;
    font-size: 0.78rem !important;
    margin-bottom: 0.5rem !important;
}}
.yun-gua-yao-list {{
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    margin-top: 0.3rem;
}}
.yun-gua-yao-item {{
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    padding: 0.35rem 0.55rem;
    font-size: 0.76rem;
    color: var(--text-muted);
    background: rgba(255, 255, 255, 0.02);
    border-radius: 6px;
    border-left: 2px solid transparent;
}}
.yun-gua-yao-item.yun-gua-yao-active {{
    color: var(--text-secondary);
}}
.yun-gua-yao-item.yun-gua-yao-current {{
    color: var(--text-primary);
    font-weight: 600;
    background: rgba(255, 255, 255, 0.05);
    border-left-color: var(--yun-color, var(--text-primary));
}}
.yun-gua-yao-idx {{
    color: var(--text-muted);
    font-variant-numeric: tabular-nums;
    min-width: 3.5rem;
    flex-shrink: 0;
}}
.yun-gua-yao-current .yun-gua-yao-idx {{
    color: var(--yun-color, var(--text-primary));
}}

/* ── 觀象期十二月 ──────────────────────────────────── */
.yun-month-grid {{
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 0.3rem;
    margin-top: 0.4rem;
}}
.yun-month-item {{
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 0.3rem 0.2rem;
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid var(--border-subtle);
    font-size: 0.68rem;
}}
.yun-month-ben {{
    border-color: color-mix(in srgb, var(--yun-color) 30%, var(--border-subtle));
}}
.yun-month-bian {{
    opacity: 0.7;
}}
.yun-month-seq {{
    font-weight: 600;
    color: var(--text-primary);
    font-size: 0.62rem;
}}
.yun-month-gua {{
    color: var(--text-secondary);
    font-size: 0.76rem;
    font-weight: 600;
}}
.yun-month-yao {{
    color: var(--text-muted);
    font-size: 0.6rem;
}}

/* ── 歷史驗例 ──────────────────────────────────── */
.yun-hist-item {{
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
    padding: 0.45rem 0;
    border-bottom: 1px solid var(--border-subtle);
}}
.yun-hist-item:last-child {{
    border-bottom: none;
}}
.yun-hist-exact {{
    background: rgba(255, 255, 255, 0.02);
    padding-left: 0.5rem;
    border-left: 2px solid var(--yun-color, var(--text-muted));
    border-radius: 0 4px 4px 0;
}}
.yun-hist-year {{
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-primary);
    font-variant-numeric: tabular-nums;
}}
.yun-hist-gua {{
    font-size: 0.72rem;
    color: var(--text-secondary);
}}
.yun-hist-summary {{
    font-size: 0.72rem;
    color: var(--text-muted);
    line-height: 1.5;
}}

/* ── 響應式 ──────────────────────────────────── */
@media (max-width: 768px) {{
    .yun-timeline-track {{ height: 44px; }}
    .yun-timeline-seg-name {{ font-size: 0.58rem; }}
    .yun-card-body {{ flex-direction: column; align-items: center; text-align: center; }}
    .yun-card-gua {{ flex-direction: row; gap: 0.5rem; }}
    .yun-card-info {{ text-align: center; }}
    .yun-card-meta {{ justify-content: center; }}
    .yun-card-gua-seq {{ justify-content: center; }}
    .yun-month-grid {{ grid-template-columns: repeat(4, 1fr); }}
    .yun-sub-card-preview {{ max-width: 45%; }}
}}

[data-testid="stMetric"] {{
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-sm) !important;
}}
[data-testid="stMetricLabel"] {{ color: var(--text-secondary) !important; }}
[data-testid="stMetricValue"] {{ color: var(--text-primary) !important; }}

/* ── DATA / CHAT ────────────────────────────────────────────────────── */
.stDataFrame, [data-testid="stDataFrame"] {{
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-sm) !important;
}}
[data-testid="stChatMessage"] [data-testid="stChatMessageContent"] {{
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
}}
.stMarkdown,
[data-testid="stMarkdownContainer"] {{
    color: var(--text-secondary) !important;
}}
.stMarkdown p, .stMarkdown li, .stMarkdown td, .stMarkdown th {{
    color: var(--text-secondary) !important;
}}
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {{
    color: var(--text-primary) !important;
    font-family: var(--font-sans) !important;
}}
.stMarkdown strong, .stMarkdown b {{
    color: var(--text-primary) !important;
}}
.stCodeBlock, pre {{
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-sm) !important;
}}

/* ── SCROLLBAR ──────────────────────────────────────────────────────── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: var(--bg-base); }}
::-webkit-scrollbar-thumb {{ background: #333; border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: #444; }}

/* ── RESPONSIVE ─────────────────────────────────────────────────────── */
@media (max-width: 768px) {{
    .grok-topnav {{
        margin: -0.5rem -0.5rem 0.75rem -0.5rem;
        padding: 0.5rem 0.75rem;
        flex-wrap: wrap;
    }}
    .main .block-container {{
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }}
    /* tabs 避開右上角 Streamlit icon 按鈕 */
    div[data-testid="stTabs"] {{
        margin-top: 1.8rem !important;
    }}
    /* Mobile: sidebar overlay when open only */
    [data-testid="stSidebar"][aria-expanded="true"] {{
        width: min(100vw, var(--sidebar-width)) !important;
        max-width: min(100vw, var(--sidebar-width)) !important;
    }}
    [data-testid="stSidebar"][aria-expanded="false"] {{
        width: 0 !important;
        min-width: 0 !important;
        max-width: 0 !important;
        flex: 0 0 0 !important;
        overflow: hidden !important;
        border: none !important;
    }}
    [data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarContent"] {{
        display: none !important;
    }}

    /* ── Mobile gap reduction ──────────────────────────────────── */
    /* Force the chart columns stacked on mobile to use minimal gap
       regardless of gap="large" in st.columns() */
    [data-testid="stHorizontalBlock"] {{
        gap: 0.25rem !important;
        flex-wrap: wrap;
    }}
    /* Reduce vertical spacing between sequential Streamlit elements */
    div[data-testid="stVerticalBlock"] {{
        gap: 0 !important;
    }}
    /* yun section + cards: tighter spacing */
    .yun-section {{
        margin: 0 !important;
    }}
    .yun-timeline-container {{
        padding: 0.5rem 0.6rem 0.45rem !important;
        margin: 0 !important;
    }}
    .yun-card {{
        margin-bottom: 0.35rem !important;
        padding: 0.55rem 0.65rem !important;
    }}
    .yun-sub-card {{
        margin-bottom: 0.3rem !important;
    }}
    /* liuri timeline: tighter */
    .liuri-track {{
        padding: 0.25rem 0.15rem 0.4rem !important;
        gap: 0.35rem !important;
    }}
    .liuri-card {{
        width: 70px !important;
        padding: 0.35rem 0.3rem 0.3rem !important;
    }}
    /* hex detail card: less margin */
    .hex-detail-card {{
        margin-top: 0.35rem !important;
        margin-bottom: 0.35rem !important;
        padding: 0.6rem 0.7rem !important;
    }}
}}
@media (min-width: 900px) {{
    div[data-testid="stVerticalBlock"]:has(> .chart-mobile-params-anchor) {{
        display: none !important;
    }}
}}

/* 立即排盤：白底黑字（覆蓋 theme textColor 與 Streamlit 1.53 primary 按鈕） */
[data-testid="stSidebar"] .grok-run-chart .stButton > button,
[data-testid="stSidebar"] .grok-run-chart .stButton > button[kind="primary"],
[data-testid="stSidebar"] .grok-run-chart .stButton > button[data-testid="baseButton-primary"],
[data-testid="stSidebar"] .grok-run-chart button[data-testid="stBaseButton-primary"] {{
    background: #f5f5f5 !important;
    background-color: #f5f5f5 !important;
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
}}
[data-testid="stSidebar"] .grok-run-chart .stButton > button p,
[data-testid="stSidebar"] .grok-run-chart .stButton > button span,
[data-testid="stSidebar"] .grok-run-chart .stButton > button div,
[data-testid="stSidebar"] .grok-run-chart .stButton > button *,
[data-testid="stSidebar"] .grok-run-chart button[data-testid="stBaseButton-primary"] p,
[data-testid="stSidebar"] .grok-run-chart button[data-testid="stBaseButton-primary"] span,
[data-testid="stSidebar"] .grok-run-chart button[data-testid="stBaseButton-primary"] div,
[data-testid="stSidebar"] .grok-run-chart button[data-testid="stBaseButton-primary"] * {{
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
}}
[data-testid="stSidebar"] .grok-run-chart .stButton > button:hover:not(:disabled),
[data-testid="stSidebar"] .grok-run-chart button[data-testid="stBaseButton-primary"]:hover:not(:disabled) {{
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
    background: #f5f5f5 !important;
    opacity: 0.88 !important;
}}

/* ── 流日卦時間軸 (LIURI) ──────────────────────────────────── */
.liuri-section {{
    margin: 0 !important;
    padding-top: 0.2rem;
}}
/* Anchor wrapper around each liuri card — makes the card clickable
   without st.button.  Strip default link styling. */
.liuri-card-link {{
    display: flex;
    text-decoration: none !important;
    color: inherit !important;
    -webkit-tap-highlight-color: transparent;
}}
.liuri-header {{
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin-bottom: 0.5rem;
    padding: 0 0.2rem;
}}
.liuri-label {{
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--text-secondary);
    letter-spacing: 0.04em;
}}
.liuri-scroll-hint {{
    font-size: 0.65rem;
    color: var(--text-muted);
}}
.liuri-track {{
    display: flex;
    gap: 0.5rem;
    overflow-x: auto;
    overflow-y: hidden;
    padding: 0.4rem 0.2rem 0.6rem;
    scroll-behavior: smooth;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: thin;
    scrollbar-color: var(--border-subtle) transparent;
}}
.liuri-track::-webkit-scrollbar {{
    height: 4px;
}}
.liuri-track::-webkit-scrollbar-track {{
    background: transparent;
}}
.liuri-track::-webkit-scrollbar-thumb {{
    background: var(--border-subtle);
    border-radius: 2px;
}}

/* ── 流日卡片 ──────────────────────────────────── */
.liuri-card {{
    flex: 0 0 auto;
    width: 78px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.1rem;
    padding: 0.5rem 0.4rem 0.4rem;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--border-subtle);
    border-radius: 10px;
    cursor: pointer;
    transition: background 0.15s ease, border-color 0.15s ease;
    text-align: center;
}}
.liuri-card:hover {{
    background: rgba(255, 255, 255, 0.06);
    border-color: var(--border-strong);
}}
.liuri-card.liuri-selected {{
    background: color-mix(in srgb, var(--hex-day) 14%, transparent);
    border-color: color-mix(in srgb, var(--hex-day) 50%, var(--border-subtle));
    box-shadow: 0 0 10px color-mix(in srgb, var(--hex-day) 20%, transparent);
}}
.liuri-date {{
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--text-primary);
    font-variant-numeric: tabular-nums;
    line-height: 1;
}}
.liuri-weekday {{
    font-size: 0.58rem;
    color: var(--text-muted);
    line-height: 1;
}}
.liuri-weekday.liuri-weekend {{
    color: var(--yun-ji-xiong);
}}
.liuri-symbol {{
    font-size: 1.5rem;
    line-height: 1.1;
    color: var(--text-primary);
    margin-top: 0.15rem;
}}
.liuri-name {{
    font-size: 0.68rem;
    font-weight: 600;
    color: var(--text-secondary);
    line-height: 1;
}}

/* ── 六爻迷你圖 ──────────────────────────────────── */
.liuri-lines {{
    display: flex;
    flex-direction: column;
    gap: 2px;
    padding: 0.2rem 0;
    width: 100%;
    align-items: center;
}}
.liuri-line {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 3px;
    height: 4px;
    width: 100%;
}}
.liuri-line-bar {{
    width: 70%;
    height: 3px;
    background: var(--text-muted);
    border-radius: 1px;
    opacity: 0.5;
}}
.liuri-line.liuri-yin .liuri-line-bar-l,
.liuri-line.liuri-yin .liuri-line-bar-r {{
    width: 30%;
}}
.liuri-line.liuri-yin .liuri-line-bar-r {{
    margin-left: 3px;
}}
/* 動爻著色 */
.liuri-line.liuri-line-active .liuri-line-bar {{
    background: var(--yun-ji-fu);
    opacity: 1;
    height: 4px;
    box-shadow: 0 0 4px var(--yun-ji-fu);
}}
.liuri-selected .liuri-line.liuri-line-active .liuri-line-bar {{
    background: var(--hex-day);
    box-shadow: 0 0 5px var(--hex-day);
}}

.liuri-yao {{
    font-size: 0.6rem;
    font-weight: 600;
    line-height: 1;
    margin-top: 0.1rem;
}}

/* ── 卦象解讀卡片 ──────────────────────────────────── */
.hex-detail-card {{
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--border-subtle);
    border-left: 3px solid var(--hex-color, var(--text-muted));
    border-radius: 14px;
    padding: 0.95rem 1.05rem;
    margin-top: 0.65rem;
    margin-bottom: 0.65rem;
}}
.hex-detail-header {{
    display: flex;
    align-items: flex-start;
    gap: 0.8rem;
    margin-bottom: 0.5rem;
}}
.hex-detail-symbol {{
    font-size: 2.4rem;
    line-height: 1;
    color: var(--text-primary);
    flex-shrink: 0;
}}
.hex-detail-title {{
    display: flex;
    flex-direction: column;
    gap: 0.1rem;
}}
.hex-detail-name {{
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-primary);
}}
.hex-detail-layer {{
    font-size: 0.65rem;
    font-weight: 600;
    color: var(--text-muted);
    letter-spacing: 0.08em;
    text-transform: uppercase;
}}
.hex-detail-body {{
    display: flex;
    flex-direction: column;
    gap: 0.7rem;
}}
.hex-detail-xiang {{
    padding: 0.5rem 0;
    border-top: 1px solid var(--border-subtle);
    border-bottom: 1px solid var(--border-subtle);
}}
.hex-detail-label {{
    font-size: 0.7rem;
    font-weight: 600;
    color: var(--text-muted);
    letter-spacing: 0.06em;
    display: block;
    margin-bottom: 0.3rem;
}}
.hex-detail-xiang p {{
    font-size: 0.82rem;
    color: var(--text-secondary);
    line-height: 1.65;
    margin: 0;
}}

/* ── 卦象解讀卡片 header（補充動爻標示）── */
.hex-detail-yao {{
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.04em;
}}
.hex-detail-zongshu summary {{
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-muted);
    cursor: pointer;
    padding: 0.3rem 0;
}}
.hex-detail-zongshu p {{
    font-size: 0.8rem;
    color: var(--text-secondary);
    line-height: 1.65;
    margin: 0.4rem 0;
}}

/* ── 古典解讀卡片群 ──────────────────────────────────── */
.classic-reading-section {{
    margin-top: 0.5rem;
}}
.classic-card {{
    background: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    margin: 0.5rem 0;
    overflow: hidden;
}}
.classic-card-header {{
    display: flex;
    align-items: baseline;
    gap: 0.6rem;
    padding: 0.6rem 0.85rem;
    cursor: pointer;
    list-style: none;
    transition: background 0.15s ease;
}}
/* ">" indicator before the title — matches st.expander triangle */
.classic-card-header::before {{
    content: "▶";
    font-size: 0.7rem;
    color: var(--text-muted);
    transition: transform 0.15s ease;
    display: inline-block;
    margin-right: 0.1rem;
}}
.classic-card[open] .classic-card-header::before {{
    transform: rotate(90deg);
}}
.classic-card-header::-webkit-details-marker {{
    display: none;
}}
.classic-card-header:hover {{
    background: rgba(255, 255, 255, 0.04);
}}
.classic-card-title {{
    font-size: 0.88rem;
    font-weight: 500;
    color: var(--text-primary);
    white-space: nowrap;
}}
.classic-card-preview {{
    display: none;
}}
.classic-card-body {{
    padding: 0.6rem 0.85rem 0.8rem;
    border-top: 1px solid var(--border-subtle);
    background: var(--bg-elevated);
    font-size: 0.82rem;
    color: var(--text-secondary);
    line-height: 1.65;
}}
.classic-card-body p {{
    margin: 0.3rem 0;
}}
.classic-card[open] .classic-card-header {{
    border-bottom: 1px solid var(--border-subtle);
}}
</style>
"""


def get_sidebar_cursor_fix_html() -> str:
    """Sidebar cursor fix is handled entirely by CSS (see get_custom_css).
    The JS injection via st.html was causing React error #185 (infinite re-render
    loop) because each Streamlit rerun created a new iframe with a new
    MutationObserver, and multiple observers triggered cascading DOM mutations.
    Return empty string so st.html() is a no-op.
    """
    return ""


def get_top_nav_html(lang: str = "zh") -> str:
    """Top navigation bar — disabled (brand moved to sidebar top)."""
    return ""


def get_sidebar_brand_html(lang: str = "zh") -> str:
    """Brand block rendered at the top of the sidebar."""
    if lang == "en":
        brand = "Kin Taiyi-Taiyi Divine Number Chart"
    else:
        brand = "堅太乙-太乙神數排盤"
    return f"""
<div class="grok-sidebar-brand">
  <div class="grok-sidebar-brand-logo" aria-hidden="true">乙</div>
  <p class="grok-sidebar-brand-title">{brand}</p>
</div>
"""


def sidebar_section(title: str) -> None:
    """Render a sidebar section heading (call from streamlit_app / sidebar_ui)."""
    import streamlit as st
    st.markdown(
        f'<div class="grok-sidebar-section"><p class="grok-sidebar-heading">{title}</p>',
        unsafe_allow_html=True,
    )


def sidebar_section_end() -> None:
    import streamlit as st
    st.markdown("</div>", unsafe_allow_html=True)


def sidebar_hint(text: str) -> None:
    import streamlit as st
    st.markdown(f'<p class="grok-sidebar-hint">{text}</p>', unsafe_allow_html=True)
