"""Chinese classical UI theme – CSS and hero header HTML for 堅太乙 - 太乙排盤.

Design language:
  主色  深墨黑 #0F0F0F / 朱砂紅 #C8102E / 鎏金 #D4AF37
  輔助  水墨灰 #4A4A4A / 米白 #F8F1E9 / 淡青綠 #8BA38B
  字體  Noto Serif SC（標題）/ Noto Sans SC（正文）
"""


def get_custom_css() -> str:
    """Return the complete custom CSS string (wrapped in <style> tags)."""
    return """
<style>
/* ── FONT IMPORTS ──────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;700;900&family=Noto+Sans+SC:wght@300;400;500&display=swap');

/* ── CSS VARIABLES ─────────────────────────────────────────────────── */
:root {
    --ink-black:    #0F0F0F;
    --dark-surface: #141414;
    --card-bg:      #1A1A1A;
    --gold:         #D4AF37;
    --light-gold:   #E8C84A;
    --bronze:       #BFA46F;
    --dim-gold:     rgba(212, 175, 55, 0.30);
    --vermilion:    #C8102E;
    --dark-red:     #7A000F;
    --rice-white:   #F8F1E9;
    --warm-gray:    #C8BEB4;
    --ink-gray:     #4A4A4A;
    --jade:         #8BA38B;
    --sidebar-bg:   #0D0D0D;
    --font-serif:   'Noto Serif SC', 'STSong', 'SimSun', serif;
    --font-sans:    'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* ── GLOBAL BACKGROUND & TEXT ───────────────────────────────────────── */
html, body, .stApp {
    background-color: var(--ink-black) !important;
    color: var(--rice-white) !important;
}

/* Subtle paper-like texture overlay */
.stApp {
    background-image:
        radial-gradient(ellipse at 15% 15%, rgba(212,175,55,0.04) 0%, transparent 55%),
        radial-gradient(ellipse at 85% 85%, rgba(200,16,46,0.04) 0%, transparent 55%),
        repeating-linear-gradient(
            0deg,
            transparent,
            transparent 3px,
            rgba(255,255,255,0.006) 3px,
            rgba(255,255,255,0.006) 4px
        ) !important;
}

/* ── TYPOGRAPHY ─────────────────────────────────────────────────────── */
* { font-family: var(--font-sans) !important; }

h1, h2, h3, h4, h5, h6 {
    font-family: var(--font-serif) !important;
    color: var(--gold) !important;
    letter-spacing: 0.06em;
}
h1 { font-size: 1.75rem !important; }
h2 { font-size: 1.35rem !important; }
h3 { font-size: 1.15rem !important; }

p, li, span {
    color: var(--rice-white);
}

a {
    color: var(--bronze) !important;
    text-decoration: underline !important;
}
a:hover { color: var(--gold) !important; }

/* ── MAIN CONTENT BLOCK ─────────────────────────────────────────────── */
.main .block-container {
    padding-top: 1rem !important;
    max-width: 1280px !important;
}

/* ── SIDEBAR ────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D0D0D 0%, #111111 100%) !important;
    border-right: 2px solid var(--gold) !important;
    box-shadow: 4px 0 18px rgba(212,175,55,0.10) !important;
}
[data-testid="stSidebar"] > div:first-child {
    background: transparent !important;
}

/* Sidebar headings */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: var(--gold) !important;
    font-family: var(--font-serif) !important;
    border-bottom: 1px solid var(--dim-gold);
    padding-bottom: 0.25rem;
    text-align: center;
}

/* Sidebar labels */
[data-testid="stSidebar"] label {
    color: var(--bronze) !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.04em;
}

/* Sidebar divider */
[data-testid="stSidebar"] hr {
    border-color: var(--dim-gold) !important;
    margin: 0.7rem 0 !important;
}

/* ── INPUT FIELDS ───────────────────────────────────────────────────── */
input[type="number"],
input[type="text"],
textarea,
.stTextInput input,
.stNumberInput input,
.stTextArea textarea {
    background-color: #1A1A1A !important;
    border: 1px solid var(--bronze) !important;
    border-radius: 4px !important;
    color: var(--rice-white) !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
input[type="number"]:focus,
input[type="text"]:focus,
textarea:focus,
.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 8px var(--dim-gold) !important;
    outline: none !important;
}

/* Number-input container border */
.stNumberInput [data-testid="stNumberInputContainer"] {
    background-color: #1A1A1A !important;
    border: 1px solid var(--bronze) !important;
    border-radius: 4px !important;
}

/* ── SELECTBOX ──────────────────────────────────────────────────────── */
.stSelectbox [data-baseweb="select"] > div {
    background-color: #1A1A1A !important;
    border: 1px solid var(--bronze) !important;
    color: var(--rice-white) !important;
    border-radius: 4px !important;
}
.stSelectbox [data-baseweb="select"] svg { fill: var(--bronze) !important; }

/* Dropdown list */
[data-baseweb="popover"] [data-baseweb="menu"] {
    background-color: #1A1A1A !important;
    border: 1px solid var(--bronze) !important;
}
[data-baseweb="popover"] [role="option"] {
    background-color: #1A1A1A !important;
    color: var(--rice-white) !important;
}
[data-baseweb="popover"] [role="option"]:hover {
    background-color: #2A1500 !important;
    color: var(--gold) !important;
}

/* ── BUTTONS ────────────────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #6B0017 0%, #C8102E 50%, #6B0017 100%) !important;
    color: var(--gold) !important;
    border: 1px solid var(--gold) !important;
    border-radius: 4px !important;
    font-family: var(--font-serif) !important;
    font-weight: 700 !important;
    letter-spacing: 0.12em !important;
    transition: all 0.25s ease !important;
    text-shadow: 0 1px 3px rgba(0,0,0,0.6) !important;
    box-shadow: 0 2px 8px rgba(200,16,46,0.30),
                inset 0 1px 0 rgba(212,175,55,0.20) !important;
}
.stButton > button:hover:not(:disabled) {
    background: linear-gradient(135deg, #8B0000 0%, #E61535 50%, #8B0000 100%) !important;
    box-shadow: 0 0 14px rgba(200,16,46,0.60),
                0 0 28px rgba(212,175,55,0.12),
                inset 0 1px 0 rgba(212,175,55,0.30) !important;
    transform: translateY(-1px) !important;
    border-color: var(--light-gold) !important;
}
.stButton > button:active:not(:disabled) {
    transform: translateY(0) !important;
    box-shadow: 0 1px 4px rgba(200,16,46,0.30) !important;
}
.stButton > button:disabled {
    background: #2A1A1A !important;
    color: var(--ink-gray) !important;
    border-color: var(--ink-gray) !important;
    box-shadow: none !important;
}

/* Number-input +/- buttons */
.stNumberInput button {
    background-color: #1E1010 !important;
    border-color: var(--bronze) !important;
    color: var(--bronze) !important;
}
.stNumberInput button:hover {
    background-color: var(--dark-red) !important;
    color: var(--gold) !important;
}

/* ── TABS ───────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background-color: #111111 !important;
    border-bottom: 1px solid var(--dim-gold) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background-color: transparent !important;
    color: var(--warm-gray) !important;
    font-size: 0.87rem !important;
    letter-spacing: 0.03em !important;
    border-radius: 0 !important;
    padding: 0.55rem 0.9rem !important;
    border-bottom: 2px solid transparent !important;
    transition: all 0.2s ease !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--gold) !important;
    background-color: rgba(212,175,55,0.05) !important;
}
.stTabs [aria-selected="true"][data-baseweb="tab"] {
    color: var(--gold) !important;
    border-bottom: 2px solid var(--vermilion) !important;
    background-color: rgba(200,16,46,0.05) !important;
    font-weight: 700 !important;
}
.stTabs [data-baseweb="tab-highlight"] {
    background-color: var(--vermilion) !important;
    height: 2px !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background-color: transparent !important;
    padding-top: 0.8rem !important;
}

/* ── EXPANDERS ──────────────────────────────────────────────────────── */
.stExpander {
    background-color: var(--dark-surface) !important;
    border: 1px solid rgba(212,175,55,0.35) !important;
    border-radius: 4px !important;
    margin-top: 8px !important;
    margin-bottom: 12px !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.50) !important;
}
.stExpander summary {
    color: var(--bronze) !important;
    font-size: 0.9rem !important;
}
.stExpander summary:hover { color: var(--gold) !important; }
.stExpander [data-testid="stExpanderDetails"] {
    background-color: var(--dark-surface) !important;
    border-top: 1px solid var(--dim-gold) !important;
    padding: 1rem !important;
    color: var(--rice-white) !important;
}

/* ── DATAFRAME / TABLE ──────────────────────────────────────────────── */
.stDataFrame, [data-testid="stDataFrame"] {
    border: 1px solid var(--dim-gold) !important;
    border-radius: 4px !important;
}
[data-testid="stDataFrame"] th {
    background-color: #1A1400 !important;
    color: var(--gold) !important;
    font-family: var(--font-serif) !important;
}
[data-testid="stDataFrame"] td {
    background-color: var(--dark-surface) !important;
    color: var(--rice-white) !important;
    border-color: var(--dim-gold) !important;
}

/* ── MARKDOWN CONTENT ───────────────────────────────────────────────── */
.stMarkdown { color: var(--rice-white) !important; }
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: var(--gold) !important; }
.stMarkdown code {
    background-color: #1A1A1A !important;
    color: var(--jade) !important;
    border: 1px solid var(--ink-gray) !important;
    border-radius: 3px !important;
}

/* ── CODE BLOCKS ────────────────────────────────────────────────────── */
.stCodeBlock, pre {
    background-color: #141414 !important;
    border: 1px solid var(--dim-gold) !important;
    border-radius: 4px !important;
    margin-bottom: 10px !important;
}

/* ── CHAT MESSAGES ──────────────────────────────────────────────────── */
[data-testid="stChatMessage"] { margin-bottom: 10px !important; }
[data-testid="stChatMessage"] [data-testid="stChatMessageContent"] {
    background-color: #1A1A1A !important;
    border: 1px solid var(--dim-gold) !important;
    border-radius: 8px !important;
    padding: 12px !important;
    color: var(--rice-white) !important;
}

/* ── ALERTS / INFO BOXES ────────────────────────────────────────────── */
.stAlert { border-radius: 4px !important; }
div[data-baseweb="notification"] {
    background-color: #1A1A1A !important;
    border: 1px solid var(--dim-gold) !important;
}

/* ── SPINNER ────────────────────────────────────────────────────────── */
[data-testid="stSpinner"] { color: var(--gold) !important; }

/* ── METRIC CARDS ───────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background-color: var(--dark-surface) !important;
    border: 1px solid var(--dim-gold) !important;
    border-radius: 4px !important;
    padding: 0.5rem !important;
}
[data-testid="stMetricLabel"] { color: var(--bronze) !important; }
[data-testid="stMetricValue"] {
    color: var(--gold) !important;
    font-family: var(--font-serif) !important;
}

/* ── THINKING CONTENT (AI) ──────────────────────────────────────────── */
.thinking-content {
    background-color: #141414;
    border-left: 3px solid var(--jade);
    padding: 12px 15px;
    border-radius: 4px;
    margin: 10px 0;
    line-height: 1.6;
    max-height: 400px;
    overflow-y: auto;
    color: var(--warm-gray);
}

/* ── SCROLLBAR ──────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--ink-black); }
::-webkit-scrollbar-thumb { background: var(--ink-gray); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--bronze); }

/* ── HERO HEADER ────────────────────────────────────────────────────── */
.taiyi-hero {
    text-align: center;
    padding: 1.4rem 1rem 1.2rem 1rem;
    position: relative;
    overflow: hidden;
    margin-bottom: 0.5rem;
}
.taiyi-hero::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(
        90deg, transparent, var(--gold), var(--vermilion), var(--gold), transparent
    );
}
.taiyi-hero::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, var(--dim-gold), transparent);
}
.taiyi-hero-ornament {
    font-size: 0.85rem;
    color: var(--dim-gold);
    letter-spacing: 0.6em;
    margin-bottom: 0.4rem;
    opacity: 0.75;
}
.taiyi-hero-title {
    font-family: 'Noto Serif SC', 'STSong', serif !important;
    font-size: clamp(2.0rem, 5vw, 3.2rem) !important;
    font-weight: 900 !important;
    color: var(--gold) !important;
    letter-spacing: 0.40em !important;
    text-shadow: 0 0 22px rgba(212,175,55,0.40), 0 2px 5px rgba(0,0,0,0.80);
    margin: 0.15rem 0 !important;
    line-height: 1.2 !important;
}
.taiyi-hero-subtitle {
    font-size: 0.88rem !important;
    color: var(--bronze) !important;
    letter-spacing: 0.35em !important;
    margin: 0.25rem 0 !important;
}
.taiyi-hero-divider {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.75rem;
    margin: 0.55rem 0;
    color: var(--dim-gold);
}
.taiyi-hero-divider::before,
.taiyi-hero-divider::after {
    content: '';
    height: 1px;
    width: 70px;
    background: linear-gradient(90deg, transparent, var(--gold));
}
.taiyi-hero-divider::after {
    background: linear-gradient(90deg, var(--gold), transparent);
}
.taiyi-hero-seal {
    display: inline-block;
    background: var(--vermilion);
    color: #F8F1E9;
    font-family: 'Noto Serif SC', serif;
    font-size: 0.72rem;
    font-weight: 700;
    width: 1.9rem;
    height: 1.9rem;
    line-height: 1.9rem;
    text-align: center;
    border-radius: 3px;
    box-shadow: 0 2px 8px rgba(200,16,46,0.55);
    letter-spacing: 0;
}
.taiyi-hero-tagline {
    font-family: 'Noto Serif SC', serif !important;
    font-size: 0.75rem !important;
    color: rgba(200,190,180,0.45) !important;
    letter-spacing: 0.22em !important;
    margin: 0.35rem 0 0 0 !important;
}

/* ── RESPONSIVE ─────────────────────────────────────────────────────── */
@media (max-width: 768px) {
    .taiyi-hero-title {
        font-size: 1.8rem !important;
        letter-spacing: 0.20em !important;
    }
    .taiyi-hero-divider::before,
    .taiyi-hero-divider::after { width: 35px; }
    .main .block-container {
        padding-left: 0.6rem !important;
        padding-right: 0.6rem !important;
    }
}
</style>
"""


def get_hero_header_html(lang: str = "zh") -> str:
    """Return the hero header HTML block for the main page area."""
    if lang == "en":
        title = "KIN&nbsp;TAI&nbsp;YI"
        subtitle = "Taiyi&nbsp;Divine&nbsp;Number&nbsp;&middot;&nbsp;Divination&nbsp;Chart"
        tagline = "Deducing the changes of Heaven and Earth"
        seal = "乾"
    else:
        title = "堅&nbsp;太&nbsp;乙"
        subtitle = "太&nbsp;乙&nbsp;神&nbsp;數&nbsp;排&nbsp;盤"
        tagline = "推天地之變，演萬事之幾"
        seal = "乾"

    return f"""
<div class="taiyi-hero">
  <div class="taiyi-hero-ornament">✦ ❖ ✦ ❖ ✦ ❖ ✦</div>
  <h1 class="taiyi-hero-title">{title}</h1>
  <p class="taiyi-hero-subtitle">{subtitle}</p>
  <div class="taiyi-hero-divider">
    <span class="taiyi-hero-seal">{seal}</span>
  </div>
  <p class="taiyi-hero-tagline">{tagline}</p>
</div>
"""
