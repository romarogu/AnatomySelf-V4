"""
AnatomySelf（解剖自我）V5.0
主应用入口 — 多租户认证 · 深色模式 · 极简专业设计
State Lock: 所有导航通过 session_state 锁定，禁止页面跳回
"""

import streamlit as st
import database as db
import auth
from datetime import datetime

# ── 页面配置（必须是第一个 Streamlit 调用）──────────────────────────────────
st.set_page_config(
    page_title="AnatomySelf · 解剖自我",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "AnatomySelf V5.0 — Personal Life Lab · 个人生命实验室",

    },
)

# ── 深色主题 CSS ──────────────────────────────────────────────────────────────
DARK_CSS = """<style>
/* ═══════════════════════════════════════════════════════════════════
   AnatomySelf V5.0 — Deep Dark Mode · Da Vinci Watermark · Bento Grid
   ═══════════════════════════════════════════════════════════════════ */

/* ── Google Font Import ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── CSS Variables ── */
:root {
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
}

/* ── Global Reset & Font ── */
html, body, [class*="css"], .stApp {
    font-family: var(--font) !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

/* ── Da Vinci Anatomy Watermark ── */
/* Inject watermark via background-image with low opacity blend */
.stApp {
    background-color: var(--bg) !important;
    background-image: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0ODAiIGhlaWdodD0iNDgwIj4KICA8Y2lyY2xlIGN4PSIyNDAiIGN5PSI3MiIgcj0iNDIiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI0M5QTg0QyIgc3Ryb2tlLXdpZHRoPSIwLjgiLz4KICA8ZWxsaXBzZSBjeD0iMjI4IiBjeT0iNjgiIHJ4PSI1IiByeT0iNyIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjQzlBODRDIiBzdHJva2Utd2lkdGg9IjAuNSIvPgogIDxlbGxpcHNlIGN4PSIyNTIiIGN5PSI2OCIgcng9IjUiIHJ5PSI3IiBmaWxsPSJub25lIiBzdHJva2U9IiNDOUE4NEMiIHN0cm9rZS13aWR0aD0iMC41Ii8+CiAgPHBhdGggZD0iTSAyMzIgODUgUSAyNDAgOTIgMjQ4IDg1IiBmaWxsPSJub25lIiBzdHJva2U9IiNDOUE4NEMiIHN0cm9rZS13aWR0aD0iMC41Ii8+CiAgPGxpbmUgeDE9IjI0MCIgeTE9IjcyIiB4Mj0iMjQwIiB5Mj0iODIiIHN0cm9rZT0iI0M5QTg0QyIgc3Ryb2tlLXdpZHRoPSIwLjQiLz4KICA8bGluZSB4MT0iMjI4IiB5MT0iMTE0IiB4Mj0iMjI0IiB5Mj0iMTM4IiBzdHJva2U9IiNDOUE4NEMiIHN0cm9rZS13aWR0aD0iMC42Ii8+CiAgPGxpbmUgeDE9IjI1MiIgeTE9IjExNCIgeDI9IjI1NiIgeTI9IjEzOCIgc3Ryb2tlPSIjQzlBODRDIiBzdHJva2Utd2lkdGg9IjAuNiIvPgogIDxwYXRoIGQ9Ik0gMjI0IDEzOCBRIDIwMCAxNDUgMTY4IDE1OCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjQzlBODRDIiBzdHJva2Utd2lkdGg9IjAuNyIvPgogIDxwYXRoIGQ9Ik0gMjU2IDEzOCBRIDI4MCAxNDUgMzEyIDE1OCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjQzlBODRDIiBzdHJva2Utd2lkdGg9IjAuNyIvPgogIDxwYXRoIGQ9Ik0gMjAwIDEzOCBDIDE5MiAxNjAgMTg4IDIwMCAxOTAgMjUwIEwgMjAwIDI2OCBMIDI0MCAyNzQgTCAyODAgMjY4IEwgMjkwIDI1MCBDIDI5MiAyMDAgMjg4IDE2MCAyODAgMTM4IFoiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI0M5QTg0QyIgc3Ryb2tlLXdpZHRoPSIwLjgiLz4KICA8bGluZSB4MT0iMjQwIiB5MT0iMTM4IiB4Mj0iMjQwIiB5Mj0iMjY4IiBzdHJva2U9IiNDOUE4NEMiIHN0cm9rZS13aWR0aD0iMC40IiBzdHJva2UtZGFzaGFycmF5PSI0LDMiLz4KICA8cGF0aCBkPSJNIDIxMCAxNTUgUSAyNDAgMTQ4IDI3MCAxNTUiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI0M5QTg0QyIgc3Ryb2tlLXdpZHRoPSIwLjUiLz4KICA8cGF0aCBkPSJNIDIwNyAxNzAgUSAyNDAgMTYzIDI3MyAxNzAiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI0M5QTg0QyIgc3Ryb2tlLXdpZHRoPSIwLjUiLz4KICA8cGF0aCBkPSJNIDIwNSAxODUgUSAyNDAgMTc4IDI3NSAxODUiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI0M5QTg0QyIgc3Ryb2tlLXdpZHRoPSIwLjUiLz4KICA8cGF0aCBkPSJNIDIwNCAyMDAgUSAyNDAgMTkzIDI3NiAyMDAiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI0M5QTg0QyIgc3Ryb2tlLXdpZHRoPSIwLjUiLz4KICA8cGF0aCBkPSJNIDIwNCAyMTUgUSAyNDAgMjA4IDI3NiAyMTUiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI0M5QTg0QyIgc3Ryb2tlLXdpZHRoPSIwLjUiLz4KICA8cGF0aCBkPSJNIDIyNCAxMzggUSAyMTUgMTM1IDIwNSAxNDAiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI0M5QTg0QyIgc3Ryb2tlLXdpZHRoPSIwLjYiLz4KICA8cGF0aCBkPSJNIDI1NiAxMzggUSAyNjUgMTM1IDI3NSAxNDAiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI0M5QTg0QyIgc3Ryb2tlLXdpZHRoPSIwLjYiLz4KICA8cGF0aCBkPSJNIDE2OCAxNTggQyAxNTggMTc1IDE0OCAyMTAgMTM4IDI0MCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjQzlBODRDIiBzdHJva2Utd2lkdGg9IjAuNyIvPgogIDxwYXRoIGQ9Ik0gMTg1IDE1OCBDIDE3NSAxNzUgMTY1IDIxMCAxNTUgMjQwIiBmaWxsPSJub25lIiBzdHJva2U9IiNDOUE4NEMiIHN0cm9rZS13aWR0aD0iMC43Ii8+CiAgPHBhdGggZD0iTSAxMzggMjQwIEMgMTI4IDI2NSAxMTggMjg1IDExMCAzMTAiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI0M5QTg0QyIgc3Ryb2tlLXdpZHRoPSIwLjYiLz4KICA8cGF0aCBkPSJNIDE1NSAyNDAgQyAxNDUgMjY1IDEzNSAyODUgMTI3IDMxMCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjQzlBODRDIiBzdHJva2Utd2lkdGg9IjAuNiIvPgogIDxwYXRoIGQ9Ik0gMzEyIDE1OCBDIDMyMiAxNzUgMzMyIDIxMCAzNDIgMjQwIiBmaWxsPSJub25lIiBzdHJva2U9IiNDOUE4NEMiIHN0cm9rZS13aWR0aD0iMC43Ii8+CiAgPHBhdGggZD0iTSAyOTUgMTU4IEMgMzA1IDE3NSAzMTUgMjEwIDMyNSAyNDAiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI0M5QTg0QyIgc3Ryb2tlLXdpZHRoPSIwLjciLz4KICA8cGF0aCBkPSJNIDM0MiAyNDAgQyAzNTIgMjY1IDM2MiAyODUgMzcwIDMxMCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjQzlBODRDIiBzdHJva2Utd2lkdGg9IjAuNiIvPgogIDxwYXRoIGQ9Ik0gMzI1IDI0MCBDIDMzNSAyNjUgMzQ1IDI4NSAzNTMgMzEwIiBmaWxsPSJub25lIiBzdHJva2U9IiNDOUE4NEMiIHN0cm9rZS13aWR0aD0iMC42Ii8+CiAgPHBhdGggZD0iTSAxOTAgMjUwIFEgMTk1IDI3NSAyMjAgMjg1IEwgMjYwIDI4NSBRIDI4NSAyNzUgMjkwIDI1MCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjQzlBODRDIiBzdHJva2Utd2lkdGg9IjAuOCIvPgogIDxlbGxpcHNlIGN4PSIyNDAiIGN5PSIyNzUiIHJ4PSIzMCIgcnk9IjEyIiBmaWxsPSJub25lIiBzdHJva2U9IiNDOUE4NEMiIHN0cm9rZS13aWR0aD0iMC41Ii8+CiAgPHBhdGggZD0iTSAyMjAgMjg1IEMgMjE1IDMyMCAyMTIgMzYwIDIxMCA0MDAiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI0M5QTg0QyIgc3Ryb2tlLXdpZHRoPSIwLjciLz4KICA8cGF0aCBkPSJNIDIzOCAyODUgQyAyMzMgMzIwIDIzMCAzNjAgMjI4IDQwMCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjQzlBODRDIiBzdHJva2Utd2lkdGg9IjAuNyIvPgogIDxwYXRoIGQ9Ik0gMjYwIDI4NSBDIDI2NSAzMjAgMjY4IDM2MCAyNzAgNDAwIiBmaWxsPSJub25lIiBzdHJva2U9IiNDOUE4NEMiIHN0cm9rZS13aWR0aD0iMC43Ii8+CiAgPHBhdGggZD0iTSAyNDIgMjg1IEMgMjQ3IDMyMCAyNTAgMzYwIDI1MiA0MDAiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI0M5QTg0QyIgc3Ryb2tlLXdpZHRoPSIwLjciLz4KICA8ZWxsaXBzZSBjeD0iMjE5IiBjeT0iNDAyIiByeD0iMTIiIHJ5PSI4IiBmaWxsPSJub25lIiBzdHJva2U9IiNDOUE4NEMiIHN0cm9rZS13aWR0aD0iMC41Ii8+CiAgPGVsbGlwc2UgY3g9IjI2MSIgY3k9IjQwMiIgcng9IjEyIiByeT0iOCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjQzlBODRDIiBzdHJva2Utd2lkdGg9IjAuNSIvPgogIDxwYXRoIGQ9Ik0gMjEwIDQxMCBDIDIwOCA0MzUgMjA3IDQ1NSAyMDggNDcwIiBmaWxsPSJub25lIiBzdHJva2U9IiNDOUE4NEMiIHN0cm9rZS13aWR0aD0iMC42Ii8+CiAgPHBhdGggZD0iTSAyMjggNDEwIEMgMjI2IDQzNSAyMjUgNDU1IDIyNiA0NzAiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI0M5QTg0QyIgc3Ryb2tlLXdpZHRoPSIwLjYiLz4KICA8cGF0aCBkPSJNIDI3MCA0MTAgQyAyNzIgNDM1IDI3MyA0NTUgMjcyIDQ3MCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjQzlBODRDIiBzdHJva2Utd2lkdGg9IjAuNiIvPgogIDxwYXRoIGQ9Ik0gMjUyIDQxMCBDIDI1NCA0MzUgMjU1IDQ1NSAyNTQgNDcwIiBmaWxsPSJub25lIiBzdHJva2U9IiNDOUE4NEMiIHN0cm9rZS13aWR0aD0iMC42Ii8+CiAgPGxpbmUgeDE9IjgwIiB5MT0iNzIiIHgyPSIxOTgiIHkyPSI3MiIgc3Ryb2tlPSIjQzlBODRDIiBzdHJva2Utd2lkdGg9IjAuMyIgc3Ryb2tlLWRhc2hhcnJheT0iMiw0Ii8+CiAgPGxpbmUgeDE9IjgwIiB5MT0iMTM4IiB4Mj0iMTk4IiB5Mj0iMTM4IiBzdHJva2U9IiNDOUE4NEMiIHN0cm9rZS13aWR0aD0iMC4zIiBzdHJva2UtZGFzaGFycmF5PSIyLDQiLz4KICA8bGluZSB4MT0iODAiIHkxPSIyNjgiIHgyPSIxODgiIHkyPSIyNjgiIHN0cm9rZT0iI0M5QTg0QyIgc3Ryb2tlLXdpZHRoPSIwLjMiIHN0cm9rZS1kYXNoYXJyYXk9IjIsNCIvPgogIDxsaW5lIHgxPSI4MCIgeTE9IjI4NSIgeDI9IjE4OCIgeTI9IjI4NSIgc3Ryb2tlPSIjQzlBODRDIiBzdHJva2Utd2lkdGg9IjAuMyIgc3Ryb2tlLWRhc2hhcnJheT0iMiw0Ii8+CiAgPGxpbmUgeDE9Ijc2IiB5MT0iNzIiIHgyPSI3NiIgeTI9IjI4NSIgc3Ryb2tlPSIjQzlBODRDIiBzdHJva2Utd2lkdGg9IjAuMyIvPgogIDxsaW5lIHgxPSI3MiIgeTE9IjcyIiB4Mj0iODAiIHkyPSI3MiIgc3Ryb2tlPSIjQzlBODRDIiBzdHJva2Utd2lkdGg9IjAuMyIvPgogIDxsaW5lIHgxPSI3MiIgeTE9IjI4NSIgeDI9IjgwIiB5Mj0iMjg1IiBzdHJva2U9IiNDOUE4NEMiIHN0cm9rZS13aWR0aD0iMC4zIi8+Cjwvc3ZnPg==") !important;
    background-repeat: repeat !important;
    background-size: 480px 480px !important;
    background-attachment: fixed !important;
    background-blend-mode: luminosity !important;
    opacity: 1 !important;
}

/* Watermark overlay: semi-transparent dark layer to keep watermark subtle */
.stApp::after {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-color: rgba(14, 17, 23, 0.82);
    pointer-events: none;
    z-index: 0;
}

/* Main content above watermark */
.stApp > * {
    position: relative;
    z-index: 1;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div:first-child {
    background-color: var(--surface) !important;
}

/* ── Main content area ── */
.main .block-container {
    background-color: transparent !important;
    padding-top: 1.5rem !important;
    max-width: 1400px !important;
}

/* ── Bento Grid Layout ── */
.bento-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 16px;
    margin: 16px 0;
}

.bento-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.04);
    transition: border-color 0.2s, box-shadow 0.2s;
    position: relative;
    overflow: hidden;
}

.bento-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--medical-blue), transparent);
    opacity: 0.4;
}

.bento-card:hover {
    border-color: var(--border-gold);
    box-shadow: 0 4px 24px rgba(79,142,247,0.12), inset 0 1px 0 rgba(255,255,255,0.06);
}

.bento-card-wide {
    grid-column: span 2;
}

.bento-card-tall {
    grid-row: span 2;
}

/* ── Hairline borders ── */
.hairline {
    border: 0.5px solid var(--border) !important;
}

.hairline-gold {
    border: 0.5px solid var(--border-gold) !important;
}

/* ── Module header ── */
.module-header {
    display: flex;
    align-items: baseline;
    gap: 12px;
    margin-bottom: 4px;
}

.module-title {
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.5px;
}

.module-subtitle {
    font-size: 0.8rem;
    color: var(--dark-gold);
    letter-spacing: 2px;
    text-transform: uppercase;
    font-weight: 500;
}

/* ── Stat cards ── */
.stat-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 20px;
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.stat-label {
    font-size: 11px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600;
}

.stat-value {
    font-size: 28px;
    font-weight: 700;
    color: var(--text);
    line-height: 1;
}

.stat-unit {
    font-size: 12px;
    color: var(--text-sec);
}

/* ── Score badge ── */
.score-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.5px;
}

.score-excellent { background: rgba(0,212,170,0.12); color: #00D4AA; border: 1px solid rgba(0,212,170,0.3); }
.score-good      { background: rgba(46,204,113,0.12); color: #2ECC71; border: 1px solid rgba(46,204,113,0.3); }
.score-warn      { background: rgba(243,156,18,0.12); color: #F39C12; border: 1px solid rgba(243,156,18,0.3); }
.score-bad       { background: rgba(231,76,60,0.12);  color: #E74C3C; border: 1px solid rgba(231,76,60,0.3); }

/* ── Tag cloud ── */
.tag {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 500;
    margin: 3px;
    border: 1px solid;
}

.tag-allergy  { background: rgba(231,76,60,0.1);  color: #E74C3C; border-color: rgba(231,76,60,0.3); }
.tag-chronic  { background: rgba(243,156,18,0.1); color: #F39C12; border-color: rgba(243,156,18,0.3); }
.tag-normal   { background: rgba(79,142,247,0.1); color: #4F8EF7; border-color: rgba(79,142,247,0.3); }

/* ── Divider ── */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
    margin: 16px 0;
}

/* ── Streamlit component overrides ── */
/* Buttons */
.stButton > button {
    background-color: var(--card) !important;
    color: var(--text-sec) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: var(--font) !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
    padding: 6px 16px !important;
}

.stButton > button:hover {
    border-color: var(--medical-blue) !important;
    color: var(--medical-blue) !important;
    background-color: rgba(79,142,247,0.08) !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #3a7ae0, #4F8EF7) !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 2px 8px rgba(79,142,247,0.3) !important;
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #4F8EF7, #6aa3ff) !important;
    box-shadow: 0 4px 16px rgba(79,142,247,0.5) !important;
    transform: translateY(-1px) !important;
}

/* Input fields */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input,
.stSelectbox > div > div > div,
.stMultiSelect > div > div > div {
    background-color: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: var(--font) !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--medical-blue) !important;
    box-shadow: 0 0 0 2px rgba(79,142,247,0.15) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background-color: var(--surface) !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 4px !important;
    border-bottom: none !important;
}

.stTabs [data-baseweb="tab"] {
    background-color: transparent !important;
    color: var(--text-muted) !important;
    border-radius: 8px !important;
    padding: 8px 16px !important;
    border: none !important;
    font-weight: 500 !important;
    font-family: var(--font) !important;
    font-size: 13px !important;
    transition: all 0.2s !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #3a7ae0, #4F8EF7) !important;
    color: white !important;
    box-shadow: 0 2px 8px rgba(79,142,247,0.3) !important;
}

.stTabs [data-baseweb="tab-panel"] {
    background-color: transparent !important;
    padding-top: 16px !important;
}

/* Expander */
.streamlit-expanderHeader {
    background-color: var(--card) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: var(--font) !important;
}

.streamlit-expanderContent {
    background-color: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
}

/* Metric cards */
[data-testid="metric-container"] {
    background-color: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 16px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
}

[data-testid="metric-container"] label {
    color: var(--text-muted) !important;
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    font-weight: 600 !important;
}

[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--text) !important;
    font-size: 28px !important;
    font-weight: 700 !important;
}

/* DataFrames */
.stDataFrame, [data-testid="stDataFrame"] {
    background-color: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}

/* Alerts */
.stAlert { border-radius: 10px !important; }
[data-testid="stAlert"] {
    background-color: var(--card) !important;
    border-radius: 10px !important;
    border: 1px solid var(--border) !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(79,142,247,0.4); }

/* File uploader */
[data-testid="stFileUploader"] {
    background-color: var(--card) !important;
    border: 1.5px dashed var(--border) !important;
    border-radius: 12px !important;
}

/* Headings */
h1, h2, h3, h4, h5, h6 {
    color: var(--text) !important;
    font-family: var(--font) !important;
    font-weight: 600 !important;
    letter-spacing: -0.3px !important;
}

h1 { font-size: 2rem !important; }
h2 { font-size: 1.5rem !important; margin-bottom: 4px !important; }
h3 { font-size: 1.2rem !important; }

p { color: var(--text) !important; font-family: var(--font) !important; }

/* Hide Streamlit branding */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
header[data-testid="stHeader"] { background-color: transparent !important; }

/* Slider */
.stSlider [data-baseweb="slider"] { background-color: var(--border) !important; }
.stSlider [data-baseweb="slider"] [role="slider"] {
    background-color: var(--medical-blue) !important;
    border-color: var(--medical-blue) !important;
}

/* Radio / Checkbox */
.stRadio > div, .stCheckbox > div { color: var(--text) !important; }

/* Divider */
hr { border-color: var(--border) !important; margin: 16px 0 !important; }

/* Code */
code, pre {
    background-color: var(--surface) !important;
    color: #a8d8ea !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    font-size: 12px !important;
}

/* ── Anatomy card (legacy support) ── */
.anatomy-card {
    background: linear-gradient(135deg, var(--card), var(--surface));
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.3);
}

/* ── AI chat bubble ── */
.chat-user {
    background: rgba(79,142,247,0.12);
    border: 1px solid rgba(79,142,247,0.25);
    border-radius: 12px 12px 4px 12px;
    padding: 12px 16px;
    margin: 8px 0;
    color: var(--text);
    font-size: 14px;
    max-width: 85%;
    margin-left: auto;
}

.chat-ai {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px 12px 12px 4px;
    padding: 16px 20px;
    margin: 8px 0;
    color: var(--text);
    font-size: 14px;
    max-width: 95%;
    line-height: 1.7;
}

.chat-ai-header {
    color: var(--aurora-green);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* ── Sidebar nav button active state ── */
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, rgba(79,142,247,0.2), rgba(79,142,247,0.1)) !important;
    color: var(--medical-blue) !important;
    border: 1px solid rgba(79,142,247,0.4) !important;
    box-shadow: none !important;
}

/* ── Date input ── */
.stDateInput > div > div > input {
    background-color: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}

/* ── Progress bar ── */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, var(--medical-blue), var(--aurora-green)) !important;
}

/* ── Select slider ── */
.stSelectSlider > div {
    color: var(--text) !important;
}

/* ── Monospace / Precision Typography ── */
/* 实验室仪器风格：关键数值使用等宽字体 */
.mono, .value-mono {
    font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'SF Mono', monospace !important;
    letter-spacing: 0.02em !important;
    font-variant-numeric: tabular-nums !important;
}

/* 标题字符间距（精密感） */
.module-title {
    letter-spacing: -0.8px !important;
}

.section-label {
    font-size: 10px !important;
    font-weight: 700 !important;
    letter-spacing: 2.5px !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
    margin-bottom: 8px !important;
}

/* 数据卡片数值显示—等宽字体 */
.stat-value {
    font-family: 'JetBrains Mono', 'Fira Code', 'SF Mono', monospace !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.5px !important;
    color: var(--text) !important;
    line-height: 1 !important;
}

/* 健康评分大字体 */
.score-display {
    font-family: 'JetBrains Mono', 'Fira Code', 'SF Mono', monospace !important;
    font-size: 3.5rem !important;
    font-weight: 700 !important;
    letter-spacing: -2px !important;
    line-height: 1 !important;
    background: linear-gradient(135deg, var(--aurora-green), var(--medical-blue));
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
}

/* Lucide 图标容器 */
.lucide-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    flex-shrink: 0;
}

.lucide-icon svg {
    width: 100%;
    height: 100%;
    stroke-width: 1.5;
}

/* 模块标题区域（含 Lucide 图标） */
.module-header-v55 {
    display: flex;
    align-items: center;
    gap: 10px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 20px;
}

.module-header-v55 .icon-wrap {
    width: 36px;
    height: 36px;
    border-radius: 8px;
    background: rgba(79,142,247,0.1);
    border: 1px solid rgba(79,142,247,0.25);
    display: flex;
    align-items: center;
    justify-content: center;
}

.module-header-v55 .icon-wrap svg {
    width: 18px;
    height: 18px;
    stroke: var(--medical-blue);
    stroke-width: 1.5;
    fill: none;
}

.module-header-v55 .title-block .name {
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.5px;
    line-height: 1.2;
}

.module-header-v55 .title-block .sub {
    font-size: 10px;
    color: var(--dark-gold);
    letter-spacing: 2.5px;
    text-transform: uppercase;
    font-weight: 600;
    margin-top: 2px;
}

/* Bento Grid V5.5： Apple Health 风格 */
.bento-v55 {
    background: #161618 !important;
    border: 1px solid #2D2D30 !important;
    border-radius: 12px !important;
    padding: 18px 20px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.03) !important;
    transition: border-color 0.2s ease !important;
}

.bento-v55:hover {
    border-color: rgba(79,142,247,0.35) !important;
}

.bento-v55 .card-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #6E6E73;
    margin-bottom: 6px;
}

.bento-v55 .card-value {
    font-family: 'JetBrains Mono', 'SF Mono', monospace;
    font-size: 2.2rem;
    font-weight: 700;
    color: #F5F5F7;
    letter-spacing: -1px;
    line-height: 1;
}

.bento-v55 .card-unit {
    font-size: 12px;
    color: #6E6E73;
    margin-top: 4px;
}

/* 删除按鈕—危险样式 */
.stButton > button[data-testid*="delete"],
.delete-btn > button {
    background: rgba(231,76,60,0.08) !important;
    color: #E74C3C !important;
    border: 1px solid rgba(231,76,60,0.3) !important;
}

.stButton > button[data-testid*="delete"]:hover,
.delete-btn > button:hover {
    background: rgba(231,76,60,0.15) !important;
    border-color: rgba(231,76,60,0.6) !important;
}
</style>"""

# ── 导航配置 ──────────────────────────────────────────────────────────────────
NAV_ITEMS = [
    ("◈", "全景健康中枢",      "module_a"),
    ("⊞", "数据中心",          "module_b"),
    ("⊟", "健康数据档案库",    "module_archive"),
    ("◉", "生理审计实验室",    "module_c"),
    ("◍", "生命律动周报",      "module_d"),
    ("⬡", "生命洞察引擎",      "module_e"),
    ("⊙", "隐私设置",          "module_privacy"),
]


def render_sidebar():
    """渲染侧边栏导航（V2.0：含全名 + 隐私入口）。"""
    with st.sidebar:
        # ── Logo 区域 ──────────────────────────────────────────────────────
        st.markdown(
            """<div style='text-align:center;padding:20px 0 20px;
                border-bottom:1px solid #2E3250;margin-bottom:16px;'>
                <div style='font-size:40px;'>🫀</div>
                <div style='font-size:20px;font-weight:700;color:#E8EAF6;
                    letter-spacing:1px;margin-top:8px;'>AnatomySelf</div>
                <div style='font-size:11px;color:#8892B0;margin-top:4px;
                    letter-spacing:2px;text-transform:uppercase;'>Personal Life Lab V5.0</div>
            </div>""",
            unsafe_allow_html=True
        )

        # ── 当前成员快捷显示（含全名 + 健康状态）──────────────────────────
        user_id = auth.get_current_user_id()
        profiles = db.get_all_profiles(user_id=user_id)
        selected_id = st.session_state.get(
            "selected_profile_id", profiles[0]["id"] if profiles else None
        )
        if selected_id and profiles:
            profile = next((p for p in profiles if p["id"] == selected_id), profiles[0])
            abnormal = db.get_latest_abnormal_records(profile["id"])
            alert_color = "#E74C3C" if abnormal else "#2ECC71"
            alert_text  = f"⚠ {len(abnormal)} 项异常" if abnormal else "✓ 状态良好"
            age = __import__("datetime").datetime.now().year - (profile.get("birth_year") or 1990)

            # 从隐私设置读取是否显示真实姓名
            try:
                from modules.module_privacy import load_privacy_settings
                priv = load_privacy_settings()
                display_name = profile["name"] if priv.get("display_real_name", True) else "***"
            except Exception:
                display_name = profile["name"]

            st.markdown(
                f"""<div style='background:#21253A;border-radius:10px;padding:14px;
                    margin-bottom:16px;border:1px solid #2E3250;'>
                    <div style='display:flex;align-items:center;gap:10px;'>
                        <div style='font-size:32px;'>{profile['avatar_emoji']}</div>
                        <div style='flex:1;'>
                            <div style='color:#E8EAF6;font-weight:700;font-size:15px;
                                letter-spacing:0.5px;'>{display_name}</div>
                            <div style='color:#8892B0;font-size:11px;margin-top:2px;'>
                                {profile.get("relation","本人")} · {age}岁 · {profile.get("gender","—")}</div>
                            <div style='color:{alert_color};font-size:12px;
                                margin-top:4px;font-weight:600;'>{alert_text}</div>
                        </div>
                    </div>
                </div>""",
                unsafe_allow_html=True
            )

        # ── 导航菜单 ───────────────────────────────────────────────────────
        st.markdown(
            "<div style='color:#8892B0;font-size:11px;font-weight:600;"
            "letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px;'>"
            "功能模块</div>",
            unsafe_allow_html=True
        )

        current_page = st.session_state.get("current_page", "module_a")

        for icon, label, page_id in NAV_ITEMS:
            is_active = current_page == page_id
            # State Lock: 用 on_click 回调写入 session_state，避免按钮触发后状态丢失
            def _nav_click(pid=page_id):
                st.session_state["current_page"] = pid
                # 切换页面时清除临时 OCR 预览，防止跨页面状态污染
                st.session_state["b_ocr_pending"] = []
                st.session_state["b_ocr_confirmed"] = False
                # 不清除 archive_highlight_codes，保留高亮直到档案库渲染完成
            st.button(
                f"{icon}  {label}",
                key=f"nav_{page_id}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
                on_click=_nav_click,
            )

        # ── 底部版本信息 ───────────────────────────────────────────────────
        st.markdown(
            """<div style='margin-top:24px;padding-top:16px;
                border-top:1px solid #2E3250;'>
                <div style='color:#8892B0;font-size:11px;text-align:center;'>
                    AnatomySelf <strong style='color:#4F8EF7;'>v5.0.0</strong><br>
                    <span style='color:#A78BFA;'>以身学医，以医护身</span>
                </div>
            </div>""",
            unsafe_allow_html=True
        )


def _init_session_state():
    """集中初始化所有 session_state 键，防止 KeyError / TypeError。"""
    defaults = {
        # 认证
        auth.SESSION_LOGGED_IN: False,
        auth.SESSION_USER_ID:   None,
        auth.SESSION_USERNAME:  "",
        auth.SESSION_DISPLAY:   "",
        auth.SESSION_AVATAR:    "🧑‍⚕️",
        # 全局导航
        "current_page": "auth",
        # 全局成员选择（各模块共享）
        "selected_profile_id": None,
        # 模块 B
        "b_just_saved_codes": [],
        "b_just_saved_pid": None,
        "b_ocr_pending": [],       # OCR 识别结果待确认列表
        "b_ocr_confirmed": False,  # 是否已确认入库
        "b_active_tab": 0,         # 当前激活的 Tab 索引（0=手动录入, 1=智能导入, 2=趋势分析）
        "b_jump_to_trend": None,   # 入库后自动跳转趋势图的指标名称
        # 模块 Archive（健康数据档案库）
        "archive_highlight_codes": [],  # OCR 入库后高亮的指标代码列表
        "archive_highlight_pid": None,  # OCR 入库后高亮的成员 ID
        # 模块 C
        "symptom_input": "",
        "c_analysis_result": "",
        "c_pollen_cache": None,
        # 模块 D
        "d_report_cache": "",
        "d_report_pid": None,
        # 模块 E
        "e_selected_exp": "cbc_analysis",
        "e_result_text": "",
        "e_result_figs": [],
        "e_ai_interp": "",
        "e_csv_analysis": "",
        # 通用
        "last_output": "",
        # 模块 E 干支
        "e_bazi_result": "",
        "e_bazi_fig": None,
        "e_clear_flag": False,
    }
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default

    # 确保 selected_profile_id 有效（数据库已初始化后，且已登录）
    if st.session_state["selected_profile_id"] is None and auth.is_logged_in():
        try:
            user_id = auth.get_current_user_id()
            profiles = db.get_all_profiles(user_id=user_id)
            if profiles:
                st.session_state["selected_profile_id"] = profiles[0]["id"]
        except Exception:
            pass


# ── Da Vinci Watermark ───────────────────────────────────────────────────────
# Da Vinci watermark is now embedded in DARK_CSS via background-image
DAVINCI_WATERMARK = ""  # deprecated



def main():
    """主函数：初始化数据库，认证守卫，渲染页面。"""
    st.markdown(DARK_CSS, unsafe_allow_html=True)
    # 达芬奇手稿风格解剖水印（直接注入 SVG 元素，绕过 CSS 背景图限制）
    st.markdown("""
    <div style="
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        pointer-events: none;
        z-index: 0;
        overflow: hidden;
        opacity: 0.06;
    ">
        <svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%">
            <defs>
                <pattern id="davinci-pattern" x="0" y="0" width="480" height="480" patternUnits="userSpaceOnUse">
                    <!-- Da Vinci style anatomical sketch -->
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
                    <path d="M 168 158 C 158 175 148 210 138 240" fill="none" stroke="#C9A84C" stroke-width="0.7"/>
                    <path d="M 185 158 C 175 175 165 210 155 240" fill="none" stroke="#C9A84C" stroke-width="0.7"/>
                    <path d="M 138 240 C 128 265 118 285 110 310" fill="none" stroke="#C9A84C" stroke-width="0.6"/>
                    <path d="M 312 158 C 322 175 332 210 342 240" fill="none" stroke="#C9A84C" stroke-width="0.7"/>
                    <path d="M 295 158 C 305 175 315 210 325 240" fill="none" stroke="#C9A84C" stroke-width="0.7"/>
                    <path d="M 342 240 C 352 265 362 285 370 310" fill="none" stroke="#C9A84C" stroke-width="0.6"/>
                    <path d="M 190 250 Q 195 275 220 285 L 260 285 Q 285 275 290 250" fill="none" stroke="#C9A84C" stroke-width="0.8"/>
                    <ellipse cx="240" cy="275" rx="30" ry="12" fill="none" stroke="#C9A84C" stroke-width="0.5"/>
                    <path d="M 220 285 C 215 320 212 360 210 400" fill="none" stroke="#C9A84C" stroke-width="0.7"/>
                    <path d="M 260 285 C 265 320 268 360 270 400" fill="none" stroke="#C9A84C" stroke-width="0.7"/>
                    <ellipse cx="219" cy="402" rx="12" ry="8" fill="none" stroke="#C9A84C" stroke-width="0.5"/>
                    <ellipse cx="261" cy="402" rx="12" ry="8" fill="none" stroke="#C9A84C" stroke-width="0.5"/>
                    <path d="M 210 410 C 208 435 207 455 208 470" fill="none" stroke="#C9A84C" stroke-width="0.6"/>
                    <path d="M 270 410 C 272 435 273 455 272 470" fill="none" stroke="#C9A84C" stroke-width="0.6"/>
                    <!-- Measurement lines (Da Vinci style) -->
                    <line x1="80" y1="72" x2="198" y2="72" stroke="#C9A84C" stroke-width="0.3" stroke-dasharray="2,4"/>
                    <line x1="80" y1="138" x2="198" y2="138" stroke="#C9A84C" stroke-width="0.3" stroke-dasharray="2,4"/>
                    <line x1="80" y1="268" x2="188" y2="268" stroke="#C9A84C" stroke-width="0.3" stroke-dasharray="2,4"/>
                    <line x1="76" y1="72" x2="76" y2="285" stroke="#C9A84C" stroke-width="0.3"/>
                    <line x1="72" y1="72" x2="80" y2="72" stroke="#C9A84C" stroke-width="0.3"/>
                    <line x1="72" y1="285" x2="80" y2="285" stroke="#C9A84C" stroke-width="0.3"/>
                    <!-- Golden ratio spiral hint -->
                    <path d="M 380 20 Q 420 20 420 60 Q 420 100 380 100 Q 340 100 340 60" fill="none" stroke="#C9A84C" stroke-width="0.4" opacity="0.6"/>
                    <!-- Latin annotation style text -->
                    <text x="30" y="460" font-size="7" fill="#C9A84C" font-family="serif" opacity="0.8" transform="rotate(-15, 30, 460)">Homo Vitruvianus</text>
                </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#davinci-pattern)"/>
        </svg>
    </div>
    """, unsafe_allow_html=True)
    db.init_db()

    # 集中初始化所有 session_state
    _init_session_state()

    # ── 认证守卫：未登录则跳转认证页 ────────────────────────────────────────
    if not auth.is_logged_in():
        st.session_state["current_page"] = "auth"
        try:
            from modules.module_auth import render as render_auth
            render_auth()
        except Exception as e:
            import traceback
            st.error(f"认证模块加载失败：{e}")
            st.code(traceback.format_exc())
        return

    render_sidebar()

    current_page = st.session_state.get("current_page", "module_a")

    try:
        if current_page == "module_a":
            from modules.module_a_dashboard import render
            render()
        elif current_page == "module_b":
            from modules.module_b_indicators import render
            render()
        elif current_page == "module_c":
            from modules.module_c_symptoms import render
            render()
        elif current_page == "module_d":
            from modules.module_d_weekly import render
            render()
        elif current_page == "module_e":
            from modules.module_e_insight import render
            render()
        elif current_page == "module_archive":
            from modules.module_archive import render
            render()
        elif current_page == "module_privacy":
            from modules.module_privacy import render
            render()
        elif current_page == "module_c_sym":
            # 症状空间映射单独入口（导航到症状模块）
            from modules.module_c_symptoms import render
            render()
        elif current_page == "auth":
            # 已登录但页面还是 auth，跳转首页
            st.session_state["current_page"] = "module_a"
            st.rerun()
    except Exception as e:
        import traceback
        st.error(f"模块加载出错：{e}")
        with st.expander("查看详细错误信息"):
            st.code(traceback.format_exc())
        if st.button("🔄 返回首页", type="primary"):
            st.session_state["current_page"] = "module_a"
            st.rerun()


if __name__ == "__main__":
    main()
