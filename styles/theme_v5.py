"""
AnatomySelf V5.0 — Aesthetic System
Deep Dark Mode · Da Vinci Watermark · Bento Grid · Hairline Borders
"""

# ─── Color Palette ────────────────────────────────────────────────────────────
COLORS = {
    "bg_primary":    "#0E1117",
    "bg_secondary":  "#141821",
    "bg_card":       "#181E2A",
    "bg_card_hover": "#1E2535",
    "border":        "rgba(79,142,247,0.15)",
    "border_strong": "rgba(79,142,247,0.35)",
    "medical_blue":  "#4F8EF7",
    "aurora_green":  "#00D4AA",
    "dark_gold":     "#C9A84C",
    "text_primary":  "#E8EAF6",
    "text_secondary":"#8892B0",
    "text_muted":    "#4A5568",
    "danger":        "#E74C3C",
    "warning":       "#F39C12",
    "success":       "#2ECC71",
    "purple":        "#A78BFA",
}

# ─── Da Vinci Anatomy SVG Watermark (inline, base64-encoded style) ────────────
DAVINCI_WATERMARK_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%"
     style="position:fixed;top:0;left:0;pointer-events:none;z-index:0;opacity:0.025;">
  <defs>
    <pattern id="dvPattern" x="0" y="0" width="480" height="480" patternUnits="userSpaceOnUse">
      <!-- Vitruvian Man simplified anatomy sketch lines -->
      <!-- Head circle -->
      <circle cx="240" cy="80" r="38" fill="none" stroke="#C9A84C" stroke-width="0.6"/>
      <!-- Neck -->
      <line x1="228" y1="118" x2="224" y2="140" stroke="#C9A84C" stroke-width="0.5"/>
      <line x1="252" y1="118" x2="256" y2="140" stroke="#C9A84C" stroke-width="0.5"/>
      <!-- Shoulders -->
      <line x1="224" y1="140" x2="160" y2="165" stroke="#C9A84C" stroke-width="0.5"/>
      <line x1="256" y1="140" x2="320" y2="165" stroke="#C9A84C" stroke-width="0.5"/>
      <!-- Torso outline -->
      <path d="M 200 140 Q 195 200 198 260 L 242 268 L 282 260 Q 285 200 280 140 Z"
            fill="none" stroke="#C9A84C" stroke-width="0.5"/>
      <!-- Ribcage lines -->
      <path d="M 210 160 Q 240 155 270 160" fill="none" stroke="#C9A84C" stroke-width="0.4"/>
      <path d="M 207 175 Q 240 170 273 175" fill="none" stroke="#C9A84C" stroke-width="0.4"/>
      <path d="M 205 190 Q 240 185 275 190" fill="none" stroke="#C9A84C" stroke-width="0.4"/>
      <path d="M 204 205 Q 240 200 276 205" fill="none" stroke="#C9A84C" stroke-width="0.4"/>
      <!-- Spine -->
      <line x1="240" y1="140" x2="240" y2="268" stroke="#C9A84C" stroke-width="0.4" stroke-dasharray="3,3"/>
      <!-- Left arm -->
      <line x1="160" y1="165" x2="130" y2="220" stroke="#C9A84C" stroke-width="0.5"/>
      <line x1="130" y1="220" x2="108" y2="270" stroke="#C9A84C" stroke-width="0.5"/>
      <!-- Right arm -->
      <line x1="320" y1="165" x2="350" y2="220" stroke="#C9A84C" stroke-width="0.5"/>
      <line x1="350" y1="220" x2="372" y2="270" stroke="#C9A84C" stroke-width="0.5"/>
      <!-- Pelvis -->
      <path d="M 198 260 Q 200 285 220 290 L 260 290 Q 280 285 282 260"
            fill="none" stroke="#C9A84C" stroke-width="0.5"/>
      <!-- Left leg -->
      <line x1="220" y1="290" x2="210" y2="370" stroke="#C9A84C" stroke-width="0.5"/>
      <line x1="210" y1="370" x2="205" y2="440" stroke="#C9A84C" stroke-width="0.5"/>
      <!-- Right leg -->
      <line x1="260" y1="290" x2="270" y2="370" stroke="#C9A84C" stroke-width="0.5"/>
      <line x1="270" y1="370" x2="275" y2="440" stroke="#C9A84C" stroke-width="0.5"/>
      <!-- Annotation lines (Da Vinci style) -->
      <line x1="100" y1="80" x2="180" y2="80" stroke="#C9A84C" stroke-width="0.3"/>
      <line x1="300" y1="80" x2="380" y2="80" stroke="#C9A84C" stroke-width="0.3"/>
      <line x1="60" y1="200" x2="120" y2="200" stroke="#C9A84C" stroke-width="0.3"/>
      <line x1="360" y1="200" x2="420" y2="200" stroke="#C9A84C" stroke-width="0.3"/>
      <!-- Small measurement marks -->
      <line x1="240" y1="42" x2="240" y2="50" stroke="#C9A84C" stroke-width="0.4"/>
      <line x1="202" y1="118" x2="202" y2="126" stroke="#C9A84C" stroke-width="0.4"/>
      <line x1="278" y1="118" x2="278" y2="126" stroke="#C9A84C" stroke-width="0.4"/>
    </pattern>
  </defs>
  <rect width="100%" height="100%" fill="url(#dvPattern)"/>
</svg>
"""

# ─── Main CSS ─────────────────────────────────────────────────────────────────
MAIN_CSS = f"""
<style>
/* ── Reset & Base ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: {COLORS['bg_primary']} !important;
    color: {COLORS['text_primary']} !important;
}}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header {{ visibility: hidden; }}
.stDeployButton {{ display: none; }}
[data-testid="stToolbar"] {{ display: none; }}
[data-testid="stDecoration"] {{ display: none; }}
.viewerBadge_container__1QSob {{ display: none; }}

/* ── App container ── */
.stApp {{
    background-color: {COLORS['bg_primary']} !important;
    background-image: none !important;
}}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #0D1219 0%, #111827 100%) !important;
    border-right: 1px solid {COLORS['border']} !important;
    box-shadow: 4px 0 24px rgba(0,0,0,0.4) !important;
}}
[data-testid="stSidebar"] > div:first-child {{
    padding-top: 0 !important;
}}

/* ── Main content area ── */
.main .block-container {{
    padding: 1.5rem 2rem !important;
    max-width: 1400px !important;
    background-color: transparent !important;
}}

/* ── Bento Grid Cards ── */
.bento-card {{
    background: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 16px;
    padding: 20px 24px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.03);
}}
.bento-card:hover {{
    border-color: {COLORS['border_strong']};
    box-shadow: 0 4px 20px rgba(79,142,247,0.12), inset 0 1px 0 rgba(255,255,255,0.05);
}}
.bento-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(79,142,247,0.4), transparent);
}}

/* ── Metric Cards ── */
.metric-card {{
    background: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
    padding: 16px 20px;
    text-align: center;
    position: relative;
    overflow: hidden;
}}
.metric-value {{
    font-size: 28px;
    font-weight: 700;
    color: {COLORS['medical_blue']};
    font-family: 'JetBrains Mono', monospace;
    line-height: 1.2;
}}
.metric-label {{
    font-size: 11px;
    color: {COLORS['text_secondary']};
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 4px;
}}
.metric-unit {{
    font-size: 12px;
    color: {COLORS['text_muted']};
    font-family: 'JetBrains Mono', monospace;
}}

/* ── Section Headers ── */
.section-header {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 1px solid {COLORS['border']};
}}
.section-title {{
    font-size: 15px;
    font-weight: 600;
    color: {COLORS['text_primary']};
    letter-spacing: 0.02em;
}}
.section-icon {{
    width: 20px;
    height: 20px;
    color: {COLORS['medical_blue']};
}}

/* ── Status Badges ── */
.badge {{
    display: inline-flex;
    align-items: center;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.04em;
}}
.badge-normal {{
    background: rgba(0,212,170,0.12);
    color: {COLORS['aurora_green']};
    border: 1px solid rgba(0,212,170,0.25);
}}
.badge-high {{
    background: rgba(231,76,60,0.12);
    color: {COLORS['danger']};
    border: 1px solid rgba(231,76,60,0.25);
}}
.badge-low {{
    background: rgba(243,156,18,0.12);
    color: {COLORS['warning']};
    border: 1px solid rgba(243,156,18,0.25);
}}
.badge-info {{
    background: rgba(79,142,247,0.12);
    color: {COLORS['medical_blue']};
    border: 1px solid rgba(79,142,247,0.25);
}}

/* ── Tag Cloud ── */
.tag {{
    display: inline-flex;
    align-items: center;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    margin: 3px;
    cursor: default;
}}
.tag-allergy {{
    background: rgba(231,76,60,0.1);
    color: #FC8181;
    border: 1px solid rgba(231,76,60,0.2);
}}
.tag-chronic {{
    background: rgba(243,156,18,0.1);
    color: #F6AD55;
    border: 1px solid rgba(243,156,18,0.2);
}}

/* ── Streamlit Overrides ── */
.stButton > button {{
    background: transparent !important;
    border: 1px solid {COLORS['border_strong']} !important;
    color: {COLORS['text_primary']} !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 8px 16px !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.02em !important;
}}
.stButton > button:hover {{
    background: rgba(79,142,247,0.1) !important;
    border-color: {COLORS['medical_blue']} !important;
    color: {COLORS['medical_blue']} !important;
    box-shadow: 0 0 12px rgba(79,142,247,0.2) !important;
}}
.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, #3B7DD8 0%, #4F8EF7 100%) !important;
    border-color: transparent !important;
    color: white !important;
    box-shadow: 0 2px 12px rgba(79,142,247,0.3) !important;
}}
.stButton > button[kind="primary"]:hover {{
    background: linear-gradient(135deg, #4F8EF7 0%, #6BA3FF 100%) !important;
    box-shadow: 0 4px 20px rgba(79,142,247,0.4) !important;
    color: white !important;
}}

/* ── Input Fields ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div,
.stDateInput > div > div > input {{
    background: {COLORS['bg_secondary']} !important;
    border: 1px solid {COLORS['border']} !important;
    border-radius: 8px !important;
    color: {COLORS['text_primary']} !important;
    font-size: 13px !important;
}}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
    border-color: {COLORS['medical_blue']} !important;
    box-shadow: 0 0 0 2px rgba(79,142,247,0.15) !important;
}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
    background: transparent !important;
    border-bottom: 1px solid {COLORS['border']} !important;
    gap: 4px !important;
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    color: {COLORS['text_secondary']} !important;
    border: none !important;
    border-radius: 8px 8px 0 0 !important;
    padding: 8px 16px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}}
.stTabs [aria-selected="true"] {{
    background: rgba(79,142,247,0.1) !important;
    color: {COLORS['medical_blue']} !important;
    border-bottom: 2px solid {COLORS['medical_blue']} !important;
}}

/* ── Dataframe / Table ── */
.stDataFrame {{
    border: 1px solid {COLORS['border']} !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}}
[data-testid="stDataFrame"] table {{
    background: {COLORS['bg_card']} !important;
}}

/* ── Expander ── */
.streamlit-expanderHeader {{
    background: {COLORS['bg_card']} !important;
    border: 1px solid {COLORS['border']} !important;
    border-radius: 8px !important;
    color: {COLORS['text_primary']} !important;
    font-size: 13px !important;
}}
.streamlit-expanderContent {{
    background: {COLORS['bg_secondary']} !important;
    border: 1px solid {COLORS['border']} !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
}}

/* ── Progress / Slider ── */
.stSlider [data-baseweb="slider"] {{
    background: {COLORS['border']} !important;
}}
.stSlider [data-baseweb="slider"] [role="slider"] {{
    background: {COLORS['medical_blue']} !important;
    border-color: {COLORS['medical_blue']} !important;
}}

/* ── Alerts ── */
.stAlert {{
    border-radius: 10px !important;
    border-left: 3px solid !important;
}}
.stAlert[data-baseweb="notification"][kind="info"] {{
    background: rgba(79,142,247,0.08) !important;
    border-color: {COLORS['medical_blue']} !important;
}}
.stAlert[data-baseweb="notification"][kind="success"] {{
    background: rgba(0,212,170,0.08) !important;
    border-color: {COLORS['aurora_green']} !important;
}}
.stAlert[data-baseweb="notification"][kind="warning"] {{
    background: rgba(243,156,18,0.08) !important;
    border-color: {COLORS['warning']} !important;
}}
.stAlert[data-baseweb="notification"][kind="error"] {{
    background: rgba(231,76,60,0.08) !important;
    border-color: {COLORS['danger']} !important;
}}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: {COLORS['bg_primary']}; }}
::-webkit-scrollbar-thumb {{ background: {COLORS['border_strong']}; border-radius: 2px; }}
::-webkit-scrollbar-thumb:hover {{ background: {COLORS['medical_blue']}; }}

/* ── Tooltip ── */
.tooltip-container {{
    position: relative;
    display: inline-block;
    cursor: help;
}}
.tooltip-content {{
    visibility: hidden;
    opacity: 0;
    background: #1E2535;
    border: 1px solid {COLORS['border_strong']};
    color: {COLORS['text_primary']};
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 12px;
    line-height: 1.6;
    width: 280px;
    position: absolute;
    z-index: 9999;
    bottom: 125%;
    left: 50%;
    transform: translateX(-50%);
    box-shadow: 0 8px 24px rgba(0,0,0,0.5);
    transition: opacity 0.2s ease;
}}
.tooltip-container:hover .tooltip-content {{
    visibility: visible;
    opacity: 1;
}}

/* ── Nav Sidebar Items ── */
.nav-item {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 14px;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.15s ease;
    margin-bottom: 4px;
    border: 1px solid transparent;
    font-size: 13px;
    font-weight: 500;
    color: {COLORS['text_secondary']};
    text-decoration: none;
}}
.nav-item:hover {{
    background: rgba(79,142,247,0.08);
    color: {COLORS['text_primary']};
    border-color: {COLORS['border']};
}}
.nav-item.active {{
    background: rgba(79,142,247,0.12);
    color: {COLORS['medical_blue']};
    border-color: {COLORS['border_strong']};
}}

/* ── Score Ring ── */
.score-ring {{
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
}}
.score-number {{
    font-size: 32px;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    background: linear-gradient(135deg, {COLORS['medical_blue']}, {COLORS['aurora_green']});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

/* ── Chat Messages ── */
.chat-message {{
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
    align-items: flex-start;
}}
.chat-bubble {{
    max-width: 80%;
    padding: 12px 16px;
    border-radius: 12px;
    font-size: 13px;
    line-height: 1.7;
}}
.chat-bubble-user {{
    background: rgba(79,142,247,0.12);
    border: 1px solid rgba(79,142,247,0.2);
    border-radius: 12px 12px 4px 12px;
    color: {COLORS['text_primary']};
    margin-left: auto;
}}
.chat-bubble-assistant {{
    background: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 12px 12px 12px 4px;
    color: {COLORS['text_primary']};
}}
.chat-avatar {{
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    flex-shrink: 0;
    border: 1px solid {COLORS['border']};
    background: {COLORS['bg_secondary']};
}}

/* ── Hairline Divider ── */
.hairline {{
    height: 1px;
    background: linear-gradient(90deg, transparent, {COLORS['border']}, transparent);
    margin: 16px 0;
    border: none;
}}

/* ── Plotly chart container ── */
.js-plotly-plot {{
    border-radius: 12px !important;
    overflow: hidden !important;
}}

/* ── Sidebar nav button override ── */
[data-testid="stSidebar"] .stButton > button {{
    width: 100% !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 10px 14px !important;
    border-radius: 10px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}}

/* ── File uploader ── */
[data-testid="stFileUploader"] {{
    background: {COLORS['bg_secondary']} !important;
    border: 1px dashed {COLORS['border_strong']} !important;
    border-radius: 12px !important;
}}
[data-testid="stFileUploader"]:hover {{
    border-color: {COLORS['medical_blue']} !important;
    background: rgba(79,142,247,0.04) !important;
}}

/* ── Spinner ── */
.stSpinner > div {{
    border-color: {COLORS['medical_blue']} transparent transparent transparent !important;
}}
</style>
"""

# ─── Lucide Icons (SVG strings) ───────────────────────────────────────────────
ICONS = {
    "hub":        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83"/></svg>',
    "database":   '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>',
    "lab":        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 3H5a2 2 0 0 0-2 2v4m6-6h10a2 2 0 0 1 2 2v4M9 3v11l-4 4h14l-4-4V3"/></svg>',
    "body":       '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a2 2 0 1 0 0 4 2 2 0 0 0 0-4z"/><path d="M7 8h10l-1 7H8L7 8z"/><path d="M9 15l-2 7M15 15l2 7M9 8l-2-3M15 8l2-3"/></svg>',
    "insight":    '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5M2 12l10 5 10-5"/></svg>',
    "user":       '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    "heart":      '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>',
    "activity":   '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
    "upload":     '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>',
    "chart":      '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
    "settings":   '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
    "trash":      '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/></svg>',
    "plus":       '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>',
    "send":       '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>',
    "refresh":    '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>',
    "lock":       '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>',
    "archive":    '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="21 8 21 21 3 21 3 8"/><rect x="1" y="3" width="22" height="5"/><line x1="10" y1="12" x2="14" y2="12"/></svg>',
    "warning":    '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    "check":      '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
    "eye":        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>',
    "calendar":   '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
    "cpu":        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>',
}


def render_watermark():
    """Render Da Vinci anatomy watermark as fixed background."""
    import streamlit as st
    st.markdown(DAVINCI_WATERMARK_SVG, unsafe_allow_html=True)


def bento_card(content: str, span: int = 1, height: str = "auto") -> str:
    """Generate a Bento Grid card HTML wrapper."""
    return f"""<div class="bento-card" style="grid-column: span {span}; min-height: {height};">
{content}
</div>"""


def section_header(title: str, icon_key: str = "activity", subtitle: str = "") -> str:
    """Generate a section header with Lucide icon."""
    icon = ICONS.get(icon_key, "")
    sub = f'<span style="font-size:11px;color:#8892B0;margin-left:8px;">{subtitle}</span>' if subtitle else ""
    return f"""<div class="section-header">
    <span style="color:#4F8EF7;">{icon}</span>
    <span class="section-title">{title}</span>{sub}
</div>"""


def status_badge(status: str) -> str:
    """Generate a status badge HTML."""
    cls = {"正常": "badge-normal", "偏高": "badge-high", "偏低": "badge-low"}.get(status, "badge-info")
    return f'<span class="badge {cls}">{status}</span>'
