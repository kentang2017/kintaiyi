"""Grok-style modern dark theme for 堅太乙 Streamlit UI.

Sidebar: fixed 310px width, non-resizable (see SIDEBAR FIXED WIDTH block).
"""

from __future__ import annotations


# ── Fixed sidebar width (px) — do not expose resize handle ──────────────
SIDEBAR_WIDTH_PX = 310


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
    --topnav-height: 52px;
    --font-sans:     'Inter', 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    --radius-sm:     8px;
    --radius-md:     12px;
    --radius-lg:     16px;
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
    padding: 0.65rem 1.25rem;
    margin: -1rem -1rem 1rem -1rem;
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
    padding-top: 0.5rem !important;
    padding-bottom: 2rem !important;
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
[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarContent"] {{
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
    min-width: 0 !important;
    max-width: 0 !important;
    opacity: 0 !important;
    overflow: hidden !important;
    pointer-events: none !important;
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
}}
.stExpander summary {{
    color: var(--text-primary) !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
}}
.stExpander [data-testid="stExpanderDetails"] {{
    background: var(--bg-elevated) !important;
    border-top: 1px solid var(--border-subtle) !important;
    color: var(--text-primary) !important;
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
    background: radial-gradient(ellipse 78% 58% at 50% 42%, rgba(255, 255, 255, 0.035), transparent 72%);
    border-radius: var(--radius-lg);
    padding: 0.5rem 0.5rem 1.25rem;
    margin-bottom: 0.25rem;
}}
@media (max-width: 899px) {{
    div[data-testid="stVerticalBlock"]:has(> .chart-stage-marker) {{
        border: 1px solid var(--border-subtle);
        padding-bottom: 0.65rem !important;
        margin-bottom: 0.1rem !important;
    }}
    div[data-testid="stVerticalBlock"]:has(iframe) {{
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }}
    div[data-testid="stElementContainer"]:has(iframe) {{
        margin-bottom: 0 !important;
    }}
    div[data-testid="stVerticalBlock"]:has(> .chart-mobile-params-anchor) {{
        margin-top: 0.2rem !important;
        margin-bottom: 0 !important;
    }}
    div[data-testid="stVerticalBlock"]:has(> .chart-mobile-params-anchor) [data-testid="stExpander"] {{
        margin-top: 0 !important;
        margin-bottom: 0.15rem !important;
    }}
    div[data-testid="stHorizontalBlock"]:has(.chart-stage-marker) {{
        margin-bottom: 0.15rem !important;
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
        font-size: 0.72rem;
        font-weight: 600;
        color: var(--text-muted);
        margin: 0.5rem 0 0.25rem 0;
    }}
    .chart-mobile-param-body {{
        font-size: 0.78rem;
        color: var(--text-muted);
        line-height: 1.5;
        margin: 0;
        word-break: break-word;
    }}
    .chart-stage-mobile-meta {{
        display: block;
        position: absolute;
        top: 0.45rem;
        left: 0.5rem;
        z-index: 5;
        max-width: min(92%, 22rem);
        pointer-events: none;
    }}
    .chart-mobile-params-anchor {{
        display: none !important;
    }}
    .chart-print-meta {{
        font-size: 0.58rem;
        line-height: 1.38;
        color: var(--text-secondary);
        white-space: pre-wrap;
        word-break: break-word;
        margin: 0;
        padding: 0.35rem 0.45rem;
        background: rgba(10, 10, 10, 0.78);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-sm);
        backdrop-filter: blur(6px);
        -webkit-backdrop-filter: blur(6px);
    }}
}}
div[data-testid="stVerticalBlock"]:has(> .chart-stage-marker) iframe {{
    max-width: min(92vw, 640px) !important;
    margin-left: auto !important;
    margin-right: auto !important;
    display: block;
}}
div[data-testid="stVerticalBlock"]:has(> .chart-stage-marker) .taiyi-shell {{
    max-width: min(92vw, 640px);
    margin-left: auto;
    margin-right: auto;
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
    div[data-testid="stHorizontalBlock"]:has(.chart-summary-desktop) > div:has(.chart-summary-desktop) {{
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
}}
@media (min-width: 900px) {{
    div[data-testid="stVerticalBlock"]:has(> .chart-mobile-params-anchor) {{
        display: none !important;
    }}
}}
</style>
"""


def get_sidebar_cursor_fix_html() -> str:
    """Lightweight JS: sync html class on sidebar toggle + hide resize handle."""
    return """
<div id="grok-sidebar-cursor-fix" style="display:none;height:0;width:0" aria-hidden="true"></div>
<script>
(function() {
    var lastExpanded = null;
    var pending = false;

    function killHandle(el) {
        el.style.setProperty("display", "none", "important");
        el.style.setProperty("visibility", "hidden", "important");
        el.style.setProperty("width", "0", "important");
        el.style.setProperty("height", "0", "important");
        el.style.setProperty("opacity", "0", "important");
        el.style.setProperty("pointer-events", "none", "important");
        el.style.setProperty("cursor", "default", "important");
    }

    function hideResizeHandles(wrapper) {
        wrapper.querySelectorAll(
            ':scope > div:not([data-testid="stSidebarContent"]), :scope > span, '
            + '.react-resizable-handle, [data-testid="stSidebarResizeHandle"]'
        ).forEach(killHandle);
    }

    function applySidebarState() {
        var wrapper = document.querySelector('[data-testid="stSidebar"]');
        if (!wrapper) return;

        var expanded = wrapper.getAttribute("aria-expanded") === "true";
        if (expanded === lastExpanded) {
            hideResizeHandles(wrapper);
            return;
        }
        lastExpanded = expanded;

        var root = document.documentElement;
        root.classList.remove("grok-sb-expanded", "grok-sb-collapsed");
        root.classList.add(expanded ? "grok-sb-expanded" : "grok-sb-collapsed");
        hideResizeHandles(wrapper);
    }

    function scheduleApply() {
        if (pending) return;
        pending = true;
        requestAnimationFrame(function() {
            pending = false;
            applySidebarState();
        });
    }

    function bindSidebar() {
        var wrapper = document.querySelector('[data-testid="stSidebar"]');
        if (!wrapper || wrapper.dataset.grokLayoutBound === "1") return;
        wrapper.dataset.grokLayoutBound = "1";
        lastExpanded = null;
        applySidebarState();
        new MutationObserver(function(muts) {
            for (var i = 0; i < muts.length; i++) {
                if (muts[i].attributeName === "aria-expanded") {
                    lastExpanded = null;
                    scheduleApply();
                    return;
                }
            }
            hideResizeHandles(wrapper);
        }).observe(wrapper, {
            attributes: true,
            attributeFilter: ["aria-expanded"],
            childList: true,
            subtree: false,
        });
    }

    bindSidebar();
    new MutationObserver(bindSidebar).observe(document.body, {
        childList: true,
        subtree: true,
    });
    window.addEventListener("resize", scheduleApply, { passive: true });
})();
</script>
"""


def get_top_nav_html(lang: str = "zh") -> str:
    """Sticky top navigation bar (Grok-style)."""
    if lang == "en":
        brand = "Kin Taiyi-Taiyi Divine Number Chart"
    else:
        brand = "堅太乙-太乙神數排盤"
    return f"""
<nav class="grok-topnav" aria-label="Main navigation">
  <div class="grok-topnav-brand">
    <div class="grok-topnav-logo" aria-hidden="true">乙</div>
    <p class="grok-topnav-title">{brand}</p>
  </div>
</nav>
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