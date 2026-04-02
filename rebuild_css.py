"""
Rebuild app.py with proper V5.0 CSS including:
- Da Vinci watermark via CSS background-image (not position:fixed SVG)
- Bento Grid layout classes
- Deep dark mode with proper Streamlit selector targeting
"""
import base64
import re

DAVINCI_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" width="480" height="480">
  <circle cx="240" cy="72" r="42" fill="none" stroke="#C9A84C" stroke-width="0.8"/>
  <ellipse cx="228" cy="68" rx="5" ry="7" fill="none" stroke="#C9A84C" stroke-width="0.5"/>
  <ellipse cx="252" cy="68" rx="5" ry="7" fill="none" stroke="#C9A84C" stroke-width="0.5"/>
  <path d="M 232 85 Q 240 92 248 85" fill="none" stroke="#C9A84C" stroke-width="0.5"/>
  <line x1="240" y1="72" x2="240" y2="82" stroke="#C9A84C" stroke-width="0.4"/>
  <line x1="228" y1="114" x2="224" y2="138" stroke="#C9A84C" stroke-width="0.6"/>
  <line x1="252" y1="114" x2="256" y2="138" stroke="#C9A84C" stroke-width="0.6"/>
  <path d="M 224 138 Q 200 145 168 158" fill="none" stroke="#C9A84C" stroke-width="0.7"/>
  <path d="M 256 138 Q 280 145 312 158" fill="none" stroke="#C9A84C" stroke-width="0.7"/>
  <path d="M 200 138 C 192 160 188 200 190 250 L 200 268 L 240 274 L 280 268 L 290 250 C 292 200 288 160 280 138 Z" fill="none" stroke="#C9A84C" stroke-width="0.8"/>
  <line x1="240" y1="138" x2="240" y2="268" stroke="#C9A84C" stroke-width="0.4" stroke-dasharray="4,3"/>
  <path d="M 210 155 Q 240 148 270 155" fill="none" stroke="#C9A84C" stroke-width="0.5"/>
  <path d="M 207 170 Q 240 163 273 170" fill="none" stroke="#C9A84C" stroke-width="0.5"/>
  <path d="M 205 185 Q 240 178 275 185" fill="none" stroke="#C9A84C" stroke-width="0.5"/>
  <path d="M 204 200 Q 240 193 276 200" fill="none" stroke="#C9A84C" stroke-width="0.5"/>
  <path d="M 204 215 Q 240 208 276 215" fill="none" stroke="#C9A84C" stroke-width="0.5"/>
  <path d="M 224 138 Q 215 135 205 140" fill="none" stroke="#C9A84C" stroke-width="0.6"/>
  <path d="M 256 138 Q 265 135 275 140" fill="none" stroke="#C9A84C" stroke-width="0.6"/>
  <path d="M 168 158 C 158 175 148 210 138 240" fill="none" stroke="#C9A84C" stroke-width="0.7"/>
  <path d="M 185 158 C 175 175 165 210 155 240" fill="none" stroke="#C9A84C" stroke-width="0.7"/>
  <path d="M 138 240 C 128 265 118 285 110 310" fill="none" stroke="#C9A84C" stroke-width="0.6"/>
  <path d="M 155 240 C 145 265 135 285 127 310" fill="none" stroke="#C9A84C" stroke-width="0.6"/>
  <path d="M 312 158 C 322 175 332 210 342 240" fill="none" stroke="#C9A84C" stroke-width="0.7"/>
  <path d="M 295 158 C 305 175 315 210 325 240" fill="none" stroke="#C9A84C" stroke-width="0.7"/>
  <path d="M 342 240 C 352 265 362 285 370 310" fill="none" stroke="#C9A84C" stroke-width="0.6"/>
  <path d="M 325 240 C 335 265 345 285 353 310" fill="none" stroke="#C9A84C" stroke-width="0.6"/>
  <path d="M 190 250 Q 195 275 220 285 L 260 285 Q 285 275 290 250" fill="none" stroke="#C9A84C" stroke-width="0.8"/>
  <ellipse cx="240" cy="275" rx="30" ry="12" fill="none" stroke="#C9A84C" stroke-width="0.5"/>
  <path d="M 220 285 C 215 320 212 360 210 400" fill="none" stroke="#C9A84C" stroke-width="0.7"/>
  <path d="M 238 285 C 233 320 230 360 228 400" fill="none" stroke="#C9A84C" stroke-width="0.7"/>
  <path d="M 260 285 C 265 320 268 360 270 400" fill="none" stroke="#C9A84C" stroke-width="0.7"/>
  <path d="M 242 285 C 247 320 250 360 252 400" fill="none" stroke="#C9A84C" stroke-width="0.7"/>
  <ellipse cx="219" cy="402" rx="12" ry="8" fill="none" stroke="#C9A84C" stroke-width="0.5"/>
  <ellipse cx="261" cy="402" rx="12" ry="8" fill="none" stroke="#C9A84C" stroke-width="0.5"/>
  <path d="M 210 410 C 208 435 207 455 208 470" fill="none" stroke="#C9A84C" stroke-width="0.6"/>
  <path d="M 228 410 C 226 435 225 455 226 470" fill="none" stroke="#C9A84C" stroke-width="0.6"/>
  <path d="M 270 410 C 272 435 273 455 272 470" fill="none" stroke="#C9A84C" stroke-width="0.6"/>
  <path d="M 252 410 C 254 435 255 455 254 470" fill="none" stroke="#C9A84C" stroke-width="0.6"/>
  <line x1="80" y1="72" x2="198" y2="72" stroke="#C9A84C" stroke-width="0.3" stroke-dasharray="2,4"/>
  <line x1="80" y1="138" x2="198" y2="138" stroke="#C9A84C" stroke-width="0.3" stroke-dasharray="2,4"/>
  <line x1="80" y1="268" x2="188" y2="268" stroke="#C9A84C" stroke-width="0.3" stroke-dasharray="2,4"/>
  <line x1="80" y1="285" x2="188" y2="285" stroke="#C9A84C" stroke-width="0.3" stroke-dasharray="2,4"/>
  <line x1="76" y1="72" x2="76" y2="285" stroke="#C9A84C" stroke-width="0.3"/>
  <line x1="72" y1="72" x2="80" y2="72" stroke="#C9A84C" stroke-width="0.3"/>
  <line x1="72" y1="285" x2="80" y2="285" stroke="#C9A84C" stroke-width="0.3"/>
</svg>'''

encoded = base64.b64encode(DAVINCI_SVG.encode()).decode()
DAVINCI_DATA_URI = f"data:image/svg+xml;base64,{encoded}"

NEW_CSS = f"""<style>
/* ═══════════════════════════════════════════════════════════════════
   AnatomySelf V5.0 — Deep Dark Mode · Da Vinci Watermark · Bento Grid
   ═══════════════════════════════════════════════════════════════════ */

/* ── Google Font Import ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── CSS Variables ── */
:root {{
    --bg:           #0E1117;
    --surface:      #141821;
    --card:         #181E2A;
    --card-hover:   #1E2535;
    --border:       rgba(79,142,247,0.18);
    --border-gold:  rgba(201,168,76,0.25);
    --medical-blue: #4F8EF7;
    --aurora-green: #00D4AA;
    --dark-gold:    #C9A84C;
    --text:         #E8EAF6;
    --text-sec:     #8892B0;
    --text-muted:   #4A5568;
    --danger:       #E74C3C;
    --warning:      #F39C12;
    --success:      #2ECC71;
    --purple:       #A78BFA;
    --font:         'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}}

/* ── Global Reset & Font ── */
html, body, [class*="css"], .stApp {{
    font-family: var(--font) !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}}

/* ── Da Vinci Anatomy Watermark ── */
/* Inject watermark into the main content area via pseudo-element on stApp */
.stApp {{
    background-color: var(--bg) !important;
    background-image: url("{DAVINCI_DATA_URI}") !important;
    background-repeat: repeat !important;
    background-size: 480px 480px !important;
    background-attachment: fixed !important;
    background-blend-mode: normal !important;
    opacity: 1 !important;
}}

/* Overlay to control watermark opacity without affecting content */
.stApp::before {{
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-color: rgba(14, 17, 23, 0.96);
    pointer-events: none;
    z-index: 0;
}}

/* Main content above watermark */
.stApp > * {{
    position: relative;
    z-index: 1;
}}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}}
[data-testid="stSidebar"] > div:first-child {{
    background-color: var(--surface) !important;
}}

/* ── Main content area ── */
.main .block-container {{
    background-color: transparent !important;
    padding-top: 1.5rem !important;
    max-width: 1400px !important;
}}

/* ── Bento Grid Layout ── */
.bento-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 16px;
    margin: 16px 0;
}}

.bento-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.04);
    transition: border-color 0.2s, box-shadow 0.2s;
    position: relative;
    overflow: hidden;
}}

.bento-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--medical-blue), transparent);
    opacity: 0.4;
}}

.bento-card:hover {{
    border-color: var(--border-gold);
    box-shadow: 0 4px 24px rgba(79,142,247,0.12), inset 0 1px 0 rgba(255,255,255,0.06);
}}

.bento-card-wide {{
    grid-column: span 2;
}}

.bento-card-tall {{
    grid-row: span 2;
}}

/* ── Hairline borders ── */
.hairline {{
    border: 0.5px solid var(--border) !important;
}}

.hairline-gold {{
    border: 0.5px solid var(--border-gold) !important;
}}

/* ── Module header ── */
.module-header {{
    display: flex;
    align-items: baseline;
    gap: 12px;
    margin-bottom: 4px;
}}

.module-title {{
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.5px;
}}

.module-subtitle {{
    font-size: 0.8rem;
    color: var(--dark-gold);
    letter-spacing: 2px;
    text-transform: uppercase;
    font-weight: 500;
}}

/* ── Stat cards ── */
.stat-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 20px;
    display: flex;
    flex-direction: column;
    gap: 4px;
}}

.stat-label {{
    font-size: 11px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600;
}}

.stat-value {{
    font-size: 28px;
    font-weight: 700;
    color: var(--text);
    line-height: 1;
}}

.stat-unit {{
    font-size: 12px;
    color: var(--text-sec);
}}

/* ── Score badge ── */
.score-badge {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.5px;
}}

.score-excellent {{ background: rgba(0,212,170,0.12); color: #00D4AA; border: 1px solid rgba(0,212,170,0.3); }}
.score-good      {{ background: rgba(46,204,113,0.12); color: #2ECC71; border: 1px solid rgba(46,204,113,0.3); }}
.score-warn      {{ background: rgba(243,156,18,0.12); color: #F39C12; border: 1px solid rgba(243,156,18,0.3); }}
.score-bad       {{ background: rgba(231,76,60,0.12);  color: #E74C3C; border: 1px solid rgba(231,76,60,0.3); }}

/* ── Tag cloud ── */
.tag {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 500;
    margin: 3px;
    border: 1px solid;
}}

.tag-allergy  {{ background: rgba(231,76,60,0.1);  color: #E74C3C; border-color: rgba(231,76,60,0.3); }}
.tag-chronic  {{ background: rgba(243,156,18,0.1); color: #F39C12; border-color: rgba(243,156,18,0.3); }}
.tag-normal   {{ background: rgba(79,142,247,0.1); color: #4F8EF7; border-color: rgba(79,142,247,0.3); }}

/* ── Divider ── */
.divider {{
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
    margin: 16px 0;
}}

/* ── Streamlit component overrides ── */
/* Buttons */
.stButton > button {{
    background-color: var(--card) !important;
    color: var(--text-sec) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: var(--font) !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
    padding: 6px 16px !important;
}}

.stButton > button:hover {{
    border-color: var(--medical-blue) !important;
    color: var(--medical-blue) !important;
    background-color: rgba(79,142,247,0.08) !important;
}}

.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, #3a7ae0, #4F8EF7) !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 2px 8px rgba(79,142,247,0.3) !important;
}}

.stButton > button[kind="primary"]:hover {{
    background: linear-gradient(135deg, #4F8EF7, #6aa3ff) !important;
    box-shadow: 0 4px 16px rgba(79,142,247,0.5) !important;
    transform: translateY(-1px) !important;
}}

/* Input fields */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input,
.stSelectbox > div > div > div,
.stMultiSelect > div > div > div {{
    background-color: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: var(--font) !important;
}}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
    border-color: var(--medical-blue) !important;
    box-shadow: 0 0 0 2px rgba(79,142,247,0.15) !important;
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
    background-color: var(--surface) !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 4px !important;
    border-bottom: none !important;
}}

.stTabs [data-baseweb="tab"] {{
    background-color: transparent !important;
    color: var(--text-muted) !important;
    border-radius: 8px !important;
    padding: 8px 16px !important;
    border: none !important;
    font-weight: 500 !important;
    font-family: var(--font) !important;
    font-size: 13px !important;
    transition: all 0.2s !important;
}}

.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, #3a7ae0, #4F8EF7) !important;
    color: white !important;
    box-shadow: 0 2px 8px rgba(79,142,247,0.3) !important;
}}

.stTabs [data-baseweb="tab-panel"] {{
    background-color: transparent !important;
    padding-top: 16px !important;
}}

/* Expander */
.streamlit-expanderHeader {{
    background-color: var(--card) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: var(--font) !important;
}}

.streamlit-expanderContent {{
    background-color: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
}}

/* Metric cards */
[data-testid="metric-container"] {{
    background-color: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 16px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
}}

[data-testid="metric-container"] label {{
    color: var(--text-muted) !important;
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    font-weight: 600 !important;
}}

[data-testid="metric-container"] [data-testid="stMetricValue"] {{
    color: var(--text) !important;
    font-size: 28px !important;
    font-weight: 700 !important;
}}

/* DataFrames */
.stDataFrame, [data-testid="stDataFrame"] {{
    background-color: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}}

/* Alerts */
.stAlert {{ border-radius: 10px !important; }}
[data-testid="stAlert"] {{
    background-color: var(--card) !important;
    border-radius: 10px !important;
    border: 1px solid var(--border) !important;
}}

/* Scrollbar */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: var(--bg); }}
::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: rgba(79,142,247,0.4); }}

/* File uploader */
[data-testid="stFileUploader"] {{
    background-color: var(--card) !important;
    border: 1.5px dashed var(--border) !important;
    border-radius: 12px !important;
}}

/* Headings */
h1, h2, h3, h4, h5, h6 {{
    color: var(--text) !important;
    font-family: var(--font) !important;
    font-weight: 600 !important;
    letter-spacing: -0.3px !important;
}}

h1 {{ font-size: 2rem !important; }}
h2 {{ font-size: 1.5rem !important; margin-bottom: 4px !important; }}
h3 {{ font-size: 1.2rem !important; }}

p {{ color: var(--text) !important; font-family: var(--font) !important; }}

/* Hide Streamlit branding */
#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}
[data-testid="stDecoration"] {{ display: none; }}
header[data-testid="stHeader"] {{ background-color: transparent !important; }}

/* Slider */
.stSlider [data-baseweb="slider"] {{ background-color: var(--border) !important; }}
.stSlider [data-baseweb="slider"] [role="slider"] {{
    background-color: var(--medical-blue) !important;
    border-color: var(--medical-blue) !important;
}}

/* Radio / Checkbox */
.stRadio > div, .stCheckbox > div {{ color: var(--text) !important; }}

/* Divider */
hr {{ border-color: var(--border) !important; margin: 16px 0 !important; }}

/* Code */
code, pre {{
    background-color: var(--surface) !important;
    color: #a8d8ea !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    font-size: 12px !important;
}}

/* ── Anatomy card (legacy support) ── */
.anatomy-card {{
    background: linear-gradient(135deg, var(--card), var(--surface));
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.3);
}}

/* ── AI chat bubble ── */
.chat-user {{
    background: rgba(79,142,247,0.12);
    border: 1px solid rgba(79,142,247,0.25);
    border-radius: 12px 12px 4px 12px;
    padding: 12px 16px;
    margin: 8px 0;
    color: var(--text);
    font-size: 14px;
    max-width: 85%;
    margin-left: auto;
}}

.chat-ai {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px 12px 12px 4px;
    padding: 16px 20px;
    margin: 8px 0;
    color: var(--text);
    font-size: 14px;
    max-width: 95%;
    line-height: 1.7;
}}

.chat-ai-header {{
    color: var(--aurora-green);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
}}

/* ── Sidebar nav button active state ── */
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, rgba(79,142,247,0.2), rgba(79,142,247,0.1)) !important;
    color: var(--medical-blue) !important;
    border: 1px solid rgba(79,142,247,0.4) !important;
    box-shadow: none !important;
}}

/* ── Date input ── */
.stDateInput > div > div > input {{
    background-color: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}}

/* ── Progress bar ── */
.stProgress > div > div > div > div {{
    background: linear-gradient(90deg, var(--medical-blue), var(--aurora-green)) !important;
}}

/* ── Select slider ── */
.stSelectSlider > div {{
    color: var(--text) !important;
}}
</style>"""

# Read current app.py
with open('/home/ubuntu/AnatomySelf/app.py', 'r') as f:
    content = f.read()

# Replace the DARK_CSS section
# Find the start and end of DARK_CSS
dark_css_start = content.index('DARK_CSS = """')
dark_css_end = content.index('"""', dark_css_start + 14) + 3

# Replace
new_content = content[:dark_css_start] + f'DARK_CSS = """{NEW_CSS}"""' + content[dark_css_end:]

# Also remove the old DAVINCI_WATERMARK section and its injection
# since we now embed it in CSS
if 'DAVINCI_WATERMARK = """' in new_content:
    dv_start = new_content.index('DAVINCI_WATERMARK = """')
    dv_end = new_content.index('"""', dv_start + 22) + 3
    new_content = new_content[:dv_start] + '# Da Vinci watermark is now embedded in DARK_CSS via background-image\nDAVINCI_WATERMARK = ""  # deprecated\n' + new_content[dv_end:]

# Also remove the st.markdown(DAVINCI_WATERMARK...) call if it's still there
new_content = new_content.replace(
    '    st.markdown(DAVINCI_WATERMARK, unsafe_allow_html=True)\n',
    '    # Da Vinci watermark injected via CSS background-image\n'
)

with open('/home/ubuntu/AnatomySelf/app.py', 'w') as f:
    f.write(new_content)

print("app.py updated successfully!")
print(f"New DARK_CSS length: {len(NEW_CSS)} chars")
