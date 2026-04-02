"""
模块 C：症状与解剖地图 V2.0
交互式 2D 解剖模型（SVG 点击式人体图）+ 实时花粉指数 + AI 关联分析。
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import requests
from datetime import datetime, date
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import database as db
import utils
import agent


# ── 人体部位热区配置 ─────────────────────────────────────────────────────────
BODY_REGIONS = {
    "head":        ("头部",    ["头痛", "偏头痛", "眼痛", "耳鸣", "眩晕"]),
    "nose":        ("鼻部",    ["鼻部瘙痒/过敏", "鼻塞", "打喷嚏", "流涕"]),
    "neck":        ("颈部",    ["颈痛", "落枕", "咽痛", "颈椎病"]),
    "chest":       ("胸部",    ["胸痛", "心悸", "胸闷", "咳嗽", "气短"]),
    "abdomen":     ("腹部",    ["胃痛", "腹痛", "腹胀", "恶心", "腹泻"]),
    "left_arm":    ("左上臂",  ["左肩痛", "左肘痛", "左上臂酸痛"]),
    "right_arm":   ("右上臂",  ["右肩痛", "右肘痛", "右上臂酸痛"]),
    "left_wrist":  ("左手腕",  ["左手腕痛", "左手指麻", "左腕酸痛"]),
    "right_wrist": ("右手腕",  ["右手腕痛", "右手指麻", "右腕酸痛"]),
    "lower_back":  ("腰背部",  ["腰痛", "背痛", "腰肌劳损"]),
    "left_knee":   ("左膝",    ["左膝痛", "左膝关节炎"]),
    "right_knee":  ("右膝",    ["右膝痛", "右膝关节炎"]),
}

REGION_GROUPS = {
    "头面部":   ["head", "nose"],
    "颈肩上肢": ["neck", "left_arm", "right_arm", "left_wrist", "right_wrist"],
    "躯干":     ["chest", "abdomen", "lower_back"],
    "下肢":     ["left_knee", "right_knee"],
}

QUICK_SYMPTOMS = [
    "鼻部瘙痒/过敏", "头痛", "右手腕酸痛", "颈肩痛",
    "胸闷气短", "腹痛腹胀", "腰背酸痛", "膝关节痛",
    "皮肤瘙痒", "疲劳乏力", "心悸", "眼睛干痒",
]

TRIGGER_OPTIONS = [
    "花粉浓度高", "PM2.5 超标", "室外活动", "久坐办公",
    "长时间使用手机", "睡眠不足", "饮食不当", "情绪压力",
    "天气变化", "运动后", "饮酒后", "用药后",
]


def _get_pollen_index() -> dict:
    """获取实时花粉指数（通过 wttr.in 天气 API）。"""
    try:
        city = config.DEFAULT_CITY
        resp = requests.get(f"https://wttr.in/{city}?format=j1", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            weather = data.get("current_condition", [{}])[0]
            humidity = int(weather.get("humidity", 60))
            temp_c = int(weather.get("temp_C", 20))
            wind_speed = int(weather.get("windspeedKmph", 10))
            desc = weather.get("weatherDesc", [{}])[0].get("value", "")
            month = datetime.now().month
            is_pollen_season = month in [3, 4, 5, 9, 10]
            if is_pollen_season and humidity < 70 and wind_speed > 15:
                level, score = "极高", 5
            elif is_pollen_season and humidity < 80:
                level, score = "高", 4
            elif is_pollen_season:
                level, score = "中等", 3
            elif humidity > 85:
                level, score = "低", 2
            else:
                level, score = "极低", 1
            return {"pollen_level": level, "pollen_score": score,
                    "humidity": humidity, "temp_c": temp_c,
                    "wind_speed": wind_speed, "weather_desc": desc,
                    "source": "实时", "location": config.DEFAULT_CITY}
    except Exception:
        pass
    month = datetime.now().month
    if month in [3, 4, 5]:
        return {"pollen_level": "高（春季花粉季）", "pollen_score": 4,
                "humidity": 55, "temp_c": 18, "wind_speed": 12,
                "weather_desc": "春季", "source": "季节估算", "location": "—"}
    elif month in [9, 10]:
        return {"pollen_level": "中等（秋季花粉季）", "pollen_score": 3,
                "humidity": 65, "temp_c": 22, "wind_speed": 10,
                "weather_desc": "秋季", "source": "季节估算", "location": "—"}
    return {"pollen_level": "低", "pollen_score": 1,
            "humidity": 70, "temp_c": 25, "wind_speed": 8,
            "weather_desc": "非花粉季", "source": "季节估算", "location": "—"}


def _render_body_svg(selected: str = None, view: str = "front") -> str:
    """
    生成极简半透明 SVG 矢量人体剪影，支持正面/背面切换。
    使用 path 曲线绘制真实解剖轮廓，选中部位高亮发光。
    """
    # Color palette
    FILL_BASE    = "rgba(79,142,247,0.06)"
    FILL_SEL     = "rgba(79,142,247,0.30)"
    STROKE_BASE  = "rgba(79,142,247,0.35)"
    STROKE_SEL   = "#4F8EF7"
    STROKE_GOLD  = "rgba(201,168,76,0.5)"
    TEXT_BASE    = "rgba(136,146,176,0.8)"
    TEXT_SEL     = "#E8EAF6"
    GLOW_SEL     = "drop-shadow(0 0 6px rgba(79,142,247,0.8))"

    def region_style(rk):
        sel = rk == selected
        return (
            FILL_SEL if sel else FILL_BASE,
            STROKE_SEL if sel else STROKE_BASE,
            "1.2" if sel else "0.6",
            TEXT_SEL if sel else TEXT_BASE,
            GLOW_SEL if sel else "none"
        )

    # SVG canvas: 200 x 480 viewBox
    parts = [
        f'''<svg viewBox="0 0 200 480" xmlns="http://www.w3.org/2000/svg"
            style="width:100%;max-height:520px;background:linear-gradient(180deg,#0E1117,#141821);
                   border-radius:16px;border:1px solid rgba(79,142,247,0.2);
                   box-shadow:0 4px 24px rgba(0,0,0,0.5);">
        <defs>
            <filter id="glow-sel">
                <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
            <filter id="glow-soft">
                <feGaussianBlur stdDeviation="1.5" result="coloredBlur"/>
                <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
            <linearGradient id="bodyGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="rgba(79,142,247,0.12)"/>
                <stop offset="100%" stop-color="rgba(79,142,247,0.04)"/>
            </linearGradient>
            <linearGradient id="goldGrad" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stop-color="transparent"/>
                <stop offset="50%" stop-color="rgba(201,168,76,0.6)"/>
                <stop offset="100%" stop-color="transparent"/>
            </linearGradient>
        </defs>
        <!-- View label -->
        <text x="100" y="18" text-anchor="middle" font-size="9" fill="rgba(201,168,76,0.7)"
              font-family="Inter,sans-serif" letter-spacing="2" font-weight="500">
            {"正面视图" if view == "front" else "背面视图"}
        </text>
        <!-- Center axis (Da Vinci style) -->
        <line x1="100" y1="25" x2="100" y2="455"
              stroke="rgba(201,168,76,0.15)" stroke-width="0.5" stroke-dasharray="4,6"/>
        '''
    ]

    if view == "front":
        # ── FRONT VIEW ──────────────────────────────────────────────────────
        # Head region
        f, s, sw, tc, gf = region_style("head")
        parts.append(f'''
        <!-- HEAD -->
        <g filter="{"url(#glow-sel)" if selected == "head" else "none"}">
            <ellipse cx="100" cy="52" rx="28" ry="30"
                     fill="{f}" stroke="{s}" stroke-width="{sw}"/>
            <!-- Facial guide lines -->
            <line x1="100" y1="28" x2="100" y2="78" stroke="{s}" stroke-width="0.3" stroke-dasharray="2,3"/>
            <ellipse cx="100" cy="55" rx="20" ry="8" fill="none" stroke="{s}" stroke-width="0.3"/>
            <!-- Eyes -->
            <ellipse cx="90" cy="50" rx="4" ry="3" fill="none" stroke="{s}" stroke-width="0.5"/>
            <ellipse cx="110" cy="50" rx="4" ry="3" fill="none" stroke="{s}" stroke-width="0.5"/>
            <!-- Nose bridge -->
            <path d="M 97 50 L 95 60 Q 100 63 105 60 L 103 50"
                  fill="none" stroke="{s}" stroke-width="0.4"/>
            <!-- Mouth -->
            <path d="M 93 67 Q 100 72 107 67" fill="none" stroke="{s}" stroke-width="0.5"/>
            <text x="100" y="84" text-anchor="middle" font-size="7" fill="{tc}"
                  font-family="Inter,sans-serif" font-weight="500">头部</text>
        </g>
        ''')

        # Nose region (overlapping head)
        f, s, sw, tc, gf = region_style("nose")
        parts.append(f'''
        <!-- NOSE (hotspot) -->
        <g filter="{"url(#glow-sel)" if selected == "nose" else "none"}">
            <ellipse cx="100" cy="57" rx="7" ry="9"
                     fill="{f}" stroke="{s}" stroke-width="{sw}" opacity="0.8"/>
        </g>
        ''')

        # Neck
        f, s, sw, tc, gf = region_style("neck")
        parts.append(f'''
        <!-- NECK -->
        <g filter="{"url(#glow-sel)" if selected == "neck" else "none"}">
            <path d="M 91 82 L 88 100 L 112 100 L 109 82 Z"
                  fill="{f}" stroke="{s}" stroke-width="{sw}"/>
            <!-- Trachea -->
            <line x1="100" y1="84" x2="100" y2="98" stroke="{s}" stroke-width="0.4" stroke-dasharray="2,2"/>
            <text x="100" y="97" text-anchor="middle" font-size="6" fill="{tc}"
                  font-family="Inter,sans-serif">颈部</text>
        </g>
        ''')

        # Shoulders and arms base
        f_la, s_la, sw_la, tc_la, _ = region_style("left_arm")
        f_ra, s_ra, sw_ra, tc_ra, _ = region_style("right_arm")
        f_lw, s_lw, sw_lw, tc_lw, _ = region_style("left_wrist")
        f_rw, s_rw, sw_rw, tc_rw, _ = region_style("right_wrist")

        # Chest
        f, s, sw, tc, gf = region_style("chest")
        parts.append(f'''
        <!-- CHEST (thorax) -->
        <g filter="{"url(#glow-sel)" if selected == "chest" else "none"}">
            <path d="M 68 100 C 60 105 56 115 56 130 L 56 165 C 56 170 60 175 68 178
                     L 100 182 L 132 178 C 140 175 144 170 144 165 L 144 130
                     C 144 115 140 105 132 100 Z"
                  fill="{f}" stroke="{s}" stroke-width="{sw}"/>
            <!-- Sternum -->
            <line x1="100" y1="102" x2="100" y2="178" stroke="{s}" stroke-width="0.5" stroke-dasharray="3,3"/>
            <!-- Clavicle left -->
            <path d="M 88 100 Q 75 96 64 102" fill="none" stroke="{s}" stroke-width="0.7"/>
            <!-- Clavicle right -->
            <path d="M 112 100 Q 125 96 136 102" fill="none" stroke="{s}" stroke-width="0.7"/>
            <!-- Ribs -->
            <path d="M 70 115 Q 100 108 130 115" fill="none" stroke="{s}" stroke-width="0.4"/>
            <path d="M 68 128 Q 100 121 132 128" fill="none" stroke="{s}" stroke-width="0.4"/>
            <path d="M 67 141 Q 100 134 133 141" fill="none" stroke="{s}" stroke-width="0.4"/>
            <path d="M 67 154 Q 100 147 133 154" fill="none" stroke="{s}" stroke-width="0.4"/>
            <path d="M 68 167 Q 100 160 132 167" fill="none" stroke="{s}" stroke-width="0.4"/>
            <!-- Heart position indicator -->
            <circle cx="90" cy="138" r="8" fill="rgba(231,76,60,0.08)"
                    stroke="rgba(231,76,60,0.3)" stroke-width="0.5"/>
            <text x="100" y="175" text-anchor="middle" font-size="7" fill="{tc}"
                  font-family="Inter,sans-serif" font-weight="500">胸部</text>
        </g>
        ''')

        # Abdomen
        f, s, sw, tc, gf = region_style("abdomen")
        parts.append(f'''
        <!-- ABDOMEN -->
        <g filter="{"url(#glow-sel)" if selected == "abdomen" else "none"}">
            <path d="M 56 178 C 54 185 53 200 54 215 L 56 240
                     C 58 248 65 255 75 258 L 100 262 L 125 258
                     C 135 255 142 248 144 240 L 146 215
                     C 147 200 146 185 144 178 Z"
                  fill="{f}" stroke="{s}" stroke-width="{sw}"/>
            <!-- Navel -->
            <circle cx="100" cy="218" r="3" fill="none" stroke="{s}" stroke-width="0.6"/>
            <!-- Abdominal lines -->
            <line x1="100" y1="180" x2="100" y2="258" stroke="{s}" stroke-width="0.3" stroke-dasharray="2,4"/>
            <path d="M 62 198 Q 100 192 138 198" fill="none" stroke="{s}" stroke-width="0.3"/>
            <path d="M 60 218 Q 100 212 140 218" fill="none" stroke="{s}" stroke-width="0.3"/>
            <path d="M 60 238 Q 100 232 140 238" fill="none" stroke="{s}" stroke-width="0.3"/>
            <text x="100" y="256" text-anchor="middle" font-size="7" fill="{tc}"
                  font-family="Inter,sans-serif" font-weight="500">腹部</text>
        </g>
        ''')

        # Pelvis / Lower back
        f, s, sw, tc, gf = region_style("lower_back")
        parts.append(f'''
        <!-- PELVIS / LOWER BACK -->
        <g filter="{"url(#glow-sel)" if selected == "lower_back" else "none"}">
            <path d="M 56 258 C 52 265 50 275 52 285
                     Q 60 300 80 305 L 100 308 L 120 305
                     Q 140 300 148 285 C 150 275 148 265 144 258 Z"
                  fill="{f}" stroke="{s}" stroke-width="{sw}"/>
            <!-- Iliac crest -->
            <path d="M 56 270 Q 75 262 100 265 Q 125 262 144 270"
                  fill="none" stroke="{s}" stroke-width="0.5"/>
            <text x="100" y="300" text-anchor="middle" font-size="7" fill="{tc}"
                  font-family="Inter,sans-serif" font-weight="500">腰背部</text>
        </g>
        ''')

        # Left arm
        parts.append(f'''
        <!-- LEFT ARM -->
        <g filter="{"url(#glow-sel)" if selected == "left_arm" else "none"}">
            <path d="M 56 105 C 46 110 38 125 34 145 L 30 175
                     C 28 185 30 195 36 198 L 44 200
                     C 50 202 56 198 58 188 L 62 158
                     C 64 140 64 120 64 108 Z"
                  fill="{f_la}" stroke="{s_la}" stroke-width="{sw_la}"/>
            <text x="38" y="158" text-anchor="middle" font-size="6" fill="{tc_la}"
                  font-family="Inter,sans-serif">左上臂</text>
        </g>
        <!-- LEFT WRIST/HAND -->
        <g filter="{"url(#glow-sel)" if selected == "left_wrist" else "none"}">
            <path d="M 30 198 C 26 205 24 215 26 225 L 28 238
                     C 30 245 36 248 42 246 L 46 244
                     C 52 242 54 236 52 228 L 50 215
                     C 48 207 42 202 36 200 Z"
                  fill="{f_lw}" stroke="{s_lw}" stroke-width="{sw_lw}"/>
            <text x="38" y="228" text-anchor="middle" font-size="6" fill="{tc_lw}"
                  font-family="Inter,sans-serif">左手腕</text>
        </g>
        ''')

        # Right arm
        parts.append(f'''
        <!-- RIGHT ARM -->
        <g filter="{"url(#glow-sel)" if selected == "right_arm" else "none"}">
            <path d="M 144 105 C 154 110 162 125 166 145 L 170 175
                     C 172 185 170 195 164 198 L 156 200
                     C 150 202 144 198 142 188 L 138 158
                     C 136 140 136 120 136 108 Z"
                  fill="{f_ra}" stroke="{s_ra}" stroke-width="{sw_ra}"/>
            <text x="162" y="158" text-anchor="middle" font-size="6" fill="{tc_ra}"
                  font-family="Inter,sans-serif">右上臂</text>
        </g>
        <!-- RIGHT WRIST/HAND -->
        <g filter="{"url(#glow-sel)" if selected == "right_wrist" else "none"}">
            <path d="M 170 198 C 174 205 176 215 174 225 L 172 238
                     C 170 245 164 248 158 246 L 154 244
                     C 148 242 146 236 148 228 L 150 215
                     C 152 207 158 202 164 200 Z"
                  fill="{f_rw}" stroke="{s_rw}" stroke-width="{sw_rw}"/>
            <text x="162" y="228" text-anchor="middle" font-size="6" fill="{tc_rw}"
                  font-family="Inter,sans-serif">右手腕</text>
        </g>
        ''')

        # Left knee
        f, s, sw, tc, gf = region_style("left_knee")
        parts.append(f'''
        <!-- LEFT LEG upper -->
        <path d="M 75 308 C 72 330 70 355 70 375 L 70 390
                 C 70 395 74 398 80 398 L 90 398
                 C 96 398 98 394 98 388 L 96 370
                 C 94 350 92 325 90 308 Z"
              fill="{FILL_BASE}" stroke="{STROKE_BASE}" stroke-width="0.5"/>
        <!-- LEFT KNEE -->
        <g filter="{"url(#glow-sel)" if selected == "left_knee" else "none"}">
            <ellipse cx="84" cy="398" rx="16" ry="10"
                     fill="{f}" stroke="{s}" stroke-width="{sw}"/>
            <!-- Patella -->
            <ellipse cx="84" cy="396" rx="6" ry="5" fill="none" stroke="{s}" stroke-width="0.4"/>
            <text x="84" y="413" text-anchor="middle" font-size="6.5" fill="{tc}"
                  font-family="Inter,sans-serif">左膝</text>
        </g>
        <!-- LEFT LOWER LEG -->
        <path d="M 70 408 C 68 430 68 450 70 465 L 72 470
                 C 74 475 80 476 86 474 L 90 472
                 C 96 470 98 464 96 458 L 94 440
                 C 92 422 90 410 88 408 Z"
              fill="{FILL_BASE}" stroke="{STROKE_BASE}" stroke-width="0.5"/>
        ''')

        # Right knee
        f, s, sw, tc, gf = region_style("right_knee")
        parts.append(f'''
        <!-- RIGHT LEG upper -->
        <path d="M 125 308 C 128 330 130 355 130 375 L 130 390
                 C 130 395 126 398 120 398 L 110 398
                 C 104 398 102 394 102 388 L 104 370
                 C 106 350 108 325 110 308 Z"
              fill="{FILL_BASE}" stroke="{STROKE_BASE}" stroke-width="0.5"/>
        <!-- RIGHT KNEE -->
        <g filter="{"url(#glow-sel)" if selected == "right_knee" else "none"}">
            <ellipse cx="116" cy="398" rx="16" ry="10"
                     fill="{f}" stroke="{s}" stroke-width="{sw}"/>
            <ellipse cx="116" cy="396" rx="6" ry="5" fill="none" stroke="{s}" stroke-width="0.4"/>
            <text x="116" y="413" text-anchor="middle" font-size="6.5" fill="{tc}"
                  font-family="Inter,sans-serif">右膝</text>
        </g>
        <!-- RIGHT LOWER LEG -->
        <path d="M 112 408 C 110 430 110 450 112 465 L 114 470
                 C 116 475 122 476 128 474 L 132 472
                 C 138 470 140 464 138 458 L 136 440
                 C 134 422 132 410 130 408 Z"
              fill="{FILL_BASE}" stroke="{STROKE_BASE}" stroke-width="0.5"/>
        ''')

    else:
        # ── BACK VIEW ───────────────────────────────────────────────────────
        # Head (back)
        f, s, sw, tc, _ = region_style("head")
        parts.append(f'''
        <!-- HEAD BACK -->
        <g filter="{"url(#glow-sel)" if selected == "head" else "none"}">
            <ellipse cx="100" cy="52" rx="28" ry="30"
                     fill="{f}" stroke="{s}" stroke-width="{sw}"/>
            <!-- Occipital line -->
            <path d="M 75 60 Q 100 55 125 60" fill="none" stroke="{s}" stroke-width="0.4"/>
            <text x="100" y="84" text-anchor="middle" font-size="7" fill="{tc}"
                  font-family="Inter,sans-serif" font-weight="500">头部(后)</text>
        </g>
        ''')

        # Neck back
        f, s, sw, tc, _ = region_style("neck")
        parts.append(f'''
        <!-- NECK BACK -->
        <g filter="{"url(#glow-sel)" if selected == "neck" else "none"}">
            <path d="M 91 82 L 88 100 L 112 100 L 109 82 Z"
                  fill="{f}" stroke="{s}" stroke-width="{sw}"/>
            <!-- Cervical spine -->
            <line x1="100" y1="84" x2="100" y2="98" stroke="{s}" stroke-width="0.6" stroke-dasharray="2,2"/>
            <text x="100" y="97" text-anchor="middle" font-size="6" fill="{tc}"
                  font-family="Inter,sans-serif">颈椎</text>
        </g>
        ''')

        # Upper back / shoulders
        f, s, sw, tc, _ = region_style("chest")
        parts.append(f'''
        <!-- UPPER BACK (maps to chest region) -->
        <g filter="{"url(#glow-sel)" if selected == "chest" else "none"}">
            <path d="M 68 100 C 60 105 56 115 56 130 L 56 165 C 56 170 60 175 68 178
                     L 100 182 L 132 178 C 140 175 144 170 144 165 L 144 130
                     C 144 115 140 105 132 100 Z"
                  fill="{f}" stroke="{s}" stroke-width="{sw}"/>
            <!-- Spine -->
            <line x1="100" y1="102" x2="100" y2="178" stroke="{s}" stroke-width="0.7" stroke-dasharray="3,3"/>
            <!-- Scapula left -->
            <path d="M 68 115 Q 80 110 85 130 Q 80 145 68 148 Z"
                  fill="none" stroke="{s}" stroke-width="0.5"/>
            <!-- Scapula right -->
            <path d="M 132 115 Q 120 110 115 130 Q 120 145 132 148 Z"
                  fill="none" stroke="{s}" stroke-width="0.5"/>
            <!-- Thoracic vertebrae marks -->
            <circle cx="100" cy="118" r="2" fill="{s}" opacity="0.5"/>
            <circle cx="100" cy="130" r="2" fill="{s}" opacity="0.5"/>
            <circle cx="100" cy="142" r="2" fill="{s}" opacity="0.5"/>
            <circle cx="100" cy="154" r="2" fill="{s}" opacity="0.5"/>
            <circle cx="100" cy="166" r="2" fill="{s}" opacity="0.5"/>
            <text x="100" y="175" text-anchor="middle" font-size="7" fill="{tc}"
                  font-family="Inter,sans-serif" font-weight="500">上背部</text>
        </g>
        ''')

        # Lower back (back view)
        f, s, sw, tc, _ = region_style("lower_back")
        parts.append(f'''
        <!-- LOWER BACK -->
        <g filter="{"url(#glow-sel)" if selected == "lower_back" else "none"}">
            <path d="M 56 178 C 54 185 53 200 54 215 L 56 258
                     C 58 265 65 272 75 275 L 100 278 L 125 275
                     C 135 272 142 265 144 258 L 146 215
                     C 147 200 146 185 144 178 Z"
                  fill="{f}" stroke="{s}" stroke-width="{sw}"/>
            <!-- Lumbar vertebrae -->
            <circle cx="100" cy="192" r="2.5" fill="{s}" opacity="0.6"/>
            <circle cx="100" cy="206" r="2.5" fill="{s}" opacity="0.6"/>
            <circle cx="100" cy="220" r="2.5" fill="{s}" opacity="0.6"/>
            <circle cx="100" cy="234" r="2.5" fill="{s}" opacity="0.6"/>
            <circle cx="100" cy="248" r="2.5" fill="{s}" opacity="0.6"/>
            <!-- Kidney indicators -->
            <ellipse cx="84" cy="205" rx="10" ry="14"
                     fill="rgba(201,168,76,0.08)" stroke="rgba(201,168,76,0.35)" stroke-width="0.5"/>
            <ellipse cx="116" cy="205" rx="10" ry="14"
                     fill="rgba(201,168,76,0.08)" stroke="rgba(201,168,76,0.35)" stroke-width="0.5"/>
            <text x="100" y="270" text-anchor="middle" font-size="7" fill="{tc}"
                  font-family="Inter,sans-serif" font-weight="500">腰背部</text>
        </g>
        ''')

        # Arms (back view same as front)
        f_la, s_la, sw_la, tc_la, _ = region_style("left_arm")
        f_ra, s_ra, sw_ra, tc_ra, _ = region_style("right_arm")
        f_lw, s_lw, sw_lw, tc_lw, _ = region_style("left_wrist")
        f_rw, s_rw, sw_rw, tc_rw, _ = region_style("right_wrist")
        parts.append(f'''
        <g filter="{"url(#glow-sel)" if selected == "left_arm" else "none"}">
            <path d="M 56 105 C 46 110 38 125 34 145 L 30 175
                     C 28 185 30 195 36 198 L 44 200
                     C 50 202 56 198 58 188 L 62 158
                     C 64 140 64 120 64 108 Z"
                  fill="{f_la}" stroke="{s_la}" stroke-width="{sw_la}"/>
            <text x="38" y="158" text-anchor="middle" font-size="6" fill="{tc_la}"
                  font-family="Inter,sans-serif">左上臂</text>
        </g>
        <g filter="{"url(#glow-sel)" if selected == "right_arm" else "none"}">
            <path d="M 144 105 C 154 110 162 125 166 145 L 170 175
                     C 172 185 170 195 164 198 L 156 200
                     C 150 202 144 198 142 188 L 138 158
                     C 136 140 136 120 136 108 Z"
                  fill="{f_ra}" stroke="{s_ra}" stroke-width="{sw_ra}"/>
            <text x="162" y="158" text-anchor="middle" font-size="6" fill="{tc_ra}"
                  font-family="Inter,sans-serif">右上臂</text>
        </g>
        ''')

        # Legs (back view)
        f_lk, s_lk, sw_lk, tc_lk, _ = region_style("left_knee")
        f_rk, s_rk, sw_rk, tc_rk, _ = region_style("right_knee")
        parts.append(f'''
        <!-- PELVIS BACK -->
        <path d="M 56 278 C 52 285 50 295 52 305
                 Q 60 318 80 322 L 100 325 L 120 322
                 Q 140 318 148 305 C 150 295 148 285 144 278 Z"
              fill="{FILL_BASE}" stroke="{STROKE_BASE}" stroke-width="0.5"/>
        <!-- LEFT LEG BACK -->
        <path d="M 75 325 C 72 348 70 372 70 392 L 70 408
                 C 70 413 74 416 80 416 L 90 416
                 C 96 416 98 412 98 406 L 96 388
                 C 94 368 92 342 90 325 Z"
              fill="{FILL_BASE}" stroke="{STROKE_BASE}" stroke-width="0.5"/>
        <!-- LEFT KNEE BACK -->
        <g filter="{"url(#glow-sel)" if selected == "left_knee" else "none"}">
            <ellipse cx="84" cy="416" rx="16" ry="10"
                     fill="{f_lk}" stroke="{s_lk}" stroke-width="{sw_lk}"/>
            <text x="84" y="431" text-anchor="middle" font-size="6.5" fill="{tc_lk}"
                  font-family="Inter,sans-serif">左膝(后)</text>
        </g>
        <!-- RIGHT LEG BACK -->
        <path d="M 125 325 C 128 348 130 372 130 392 L 130 408
                 C 130 413 126 416 120 416 L 110 416
                 C 104 416 102 412 102 406 L 104 388
                 C 106 368 108 342 110 325 Z"
              fill="{FILL_BASE}" stroke="{STROKE_BASE}" stroke-width="0.5"/>
        <!-- RIGHT KNEE BACK -->
        <g filter="{"url(#glow-sel)" if selected == "right_knee" else "none"}">
            <ellipse cx="116" cy="416" rx="16" ry="10"
                     fill="{f_rk}" stroke="{s_rk}" stroke-width="{sw_rk}"/>
            <text x="116" y="431" text-anchor="middle" font-size="6.5" fill="{tc_rk}"
                  font-family="Inter,sans-serif">右膝(后)</text>
        </g>
        ''')

    # Bottom decorative line
    parts.append('''
    <!-- Bottom hairline -->
    <line x1="20" y1="460" x2="180" y2="460" stroke="url(#goldGrad)" stroke-width="0.5"/>
    </svg>''')

    return "".join(parts)


def render():
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:space-between;
         margin-bottom:24px;padding-bottom:16px;border-bottom:1px solid rgba(79,142,247,0.15);">
      <div>
        <div style="font-size:11px;text-transform:uppercase;letter-spacing:0.1em;color:#8892B0;margin-bottom:4px;">PHYSIOLOGICAL AUDIT LAB</div>
        <div style="font-size:22px;font-weight:700;color:#E8EAF6;">生理审计实验室</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#8892B0;margin-top:-10px;'>"
        "点击解剖图选择部位，AI 自动映射解剖结构并分析致病因子</p>",
        unsafe_allow_html=True
    )

    user_id = st.session_state.get("auth_user_id")
    profiles = db.get_all_profiles(user_id=user_id)
    if not profiles:
        st.warning("请先在「家庭成员驾驶舱」中添加成员档案。")
        return

    profile_options = {f"{p['avatar_emoji']} {p['name']}": p for p in profiles}
    selected_name = st.selectbox("选择成员", list(profile_options.keys()),
                                  key="symptom_profile")
    profile = profile_options[selected_name]

    tab1, tab2 = st.tabs(["🔍 症状分析", "📋 症状日志"])
    with tab1:
        _render_symptom_analysis(profile)
    with tab2:
        _render_symptom_log(profile)


def _render_symptom_analysis(profile: dict):
    """症状分析主界面：左侧 2D 解剖图 + 右侧输入与 AI 分析结果。"""

    # ── 实时花粉指数横幅 ──────────────────────────────────────────────────────
    pollen = _get_pollen_index()
    p_colors = {1: "#2ECC71", 2: "#27AE60", 3: "#F39C12", 4: "#E67E22", 5: "#E74C3C"}
    p_color = p_colors.get(pollen["pollen_score"], "#8892B0")
    st.markdown(
        f"""<div style='background:linear-gradient(135deg,#1a2744,#21253A);
            border:1px solid #2E3250;border-radius:10px;padding:12px 20px;
            margin-bottom:16px;'>
            <div style='display:flex;align-items:center;gap:16px;'>
                <div style='font-size:28px;'>🌿</div>
                <div style='flex:1;'>
                    <div style='color:#E8EAF6;font-size:13px;font-weight:600;'>
                        今日环境指数
                        <span style='color:#8892B0;font-size:11px;'>
                        ({pollen["source"]} · {pollen["location"]})</span></div>
                    <div style='display:flex;gap:20px;margin-top:4px;flex-wrap:wrap;'>
                        <span style='color:{p_color};font-size:12px;font-weight:700;'>
                            🌸 花粉: {pollen["pollen_level"]}</span>
                        <span style='color:#8892B0;font-size:12px;'>
                            💧 湿度: {pollen["humidity"]}%</span>
                        <span style='color:#8892B0;font-size:12px;'>
                            🌡️ 气温: {pollen["temp_c"]}°C</span>
                        <span style='color:#8892B0;font-size:12px;'>
                            💨 风速: {pollen["wind_speed"]} km/h</span>
                    </div>
                </div>
                <div style='background:{p_color}22;border:1px solid {p_color}44;
                    border-radius:8px;padding:8px 16px;text-align:center;'>
                    <div style='color:{p_color};font-size:22px;font-weight:800;'>
                        {pollen["pollen_score"]}/5</div>
                    <div style='color:#8892B0;font-size:10px;'>花粉指数</div>
                </div>
            </div>
        </div>""",
        unsafe_allow_html=True
    )

    # ── 主布局：左侧解剖图 + 右侧输入 ────────────────────────────────────────
    left_col, right_col = st.columns([2, 3])

    with left_col:
        st.markdown(
            """<div style='font-size:13px;font-weight:600;color:#E8EAF6;letter-spacing:0.5px;
            margin-bottom:10px;'>ANATOMY MAP</div>""",
            unsafe_allow_html=True
        )
        # Front/Back view toggle
        _v1, _v2 = st.columns(2)
        with _v1:
            if st.button("正面视图", key="c_view_front", use_container_width=True,
                         type="primary" if st.session_state.get("c_body_view","front")=="front" else "secondary"):
                st.session_state["c_body_view"] = "front"
                st.rerun()
        with _v2:
            if st.button("背面视图", key="c_view_back", use_container_width=True,
                         type="primary" if st.session_state.get("c_body_view","front")=="back" else "secondary"):
                st.session_state["c_body_view"] = "back"
                st.rerun()

        selected_region = st.session_state.get("c_selected_region", None)
        body_view = st.session_state.get("c_body_view", "front")
        svg_html = _render_body_svg(selected_region, view=body_view)
        # Use components.html to properly render SVG without Markdown interference
        components.html(
            f"""<!DOCTYPE html>
<html>
<head>
<style>
body {{ margin:0; padding:0; background:transparent; }}
.svg-container {{ width:100%; display:flex; justify-content:center; }}
</style>
</head>
<body>
<div class="svg-container">
{svg_html}
</div>
</body>
</html>""",
            height=540,
            scrolling=False
        )

        st.markdown("**选择部位**")
        for group_name, region_keys in REGION_GROUPS.items():
            st.markdown(
                f"<div style='color:#8892B0;font-size:10px;margin:6px 0 3px;'>"
                f"{group_name}</div>",
                unsafe_allow_html=True
            )
            btn_cols = st.columns(len(region_keys))
            for i, rk in enumerate(region_keys):
                label, syms = BODY_REGIONS[rk]
                is_sel = rk == selected_region
                with btn_cols[i]:
                    if st.button(label, key=f"c_region_{rk}",
                                  use_container_width=True,
                                  type="primary" if is_sel else "secondary"):
                        st.session_state["c_selected_region"] = rk
                        if syms:
                            st.session_state["c_symptom_text"] = syms[0]
                        st.rerun()

        if selected_region and selected_region in BODY_REGIONS:
            rl, rs = BODY_REGIONS[selected_region]
            st.markdown(
                f"""<div style='background:rgba(79,142,247,0.1);border:1px solid
                    rgba(79,142,247,0.3);border-radius:8px;padding:10px;margin-top:8px;'>
                    <div style='color:#4F8EF7;font-size:12px;font-weight:600;'>
                        ✓ 已选择：{rl}</div>
                    <div style='color:#8892B0;font-size:11px;margin-top:4px;'>
                        常见症状：{" · ".join(rs[:4])}</div>
                </div>""",
                unsafe_allow_html=True
            )

    with right_col:
        st.markdown("#### 📝 症状描述")

        # 快速选择症状
        st.caption("快速选择常见症状")
        if "c_symptom_text" not in st.session_state:
            st.session_state["c_symptom_text"] = ""

        quick_cols = st.columns(4)
        for i, sym in enumerate(QUICK_SYMPTOMS):
            with quick_cols[i % 4]:
                if st.button(sym, key=f"c_quick_{i}", use_container_width=True):
                    st.session_state["c_symptom_text"] = sym
                    st.rerun()

        # 症状文本输入（由 session_state 驱动，不传 value 参数）
        symptom_text = st.text_area(
            "描述您的症状",
            placeholder="例如：右手腕酸痛，长时间使用手机后加重，持续约1小时...",
            height=100,
            key="c_symptom_text",
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            severity = st.slider("严重程度", 1, 10, 5,
                                  help="1=轻微不适，10=无法忍受",
                                  key="c_severity")
        with col2:
            duration = st.number_input("持续时间（分钟）", min_value=0,
                                        value=30, key="c_duration")
        with col3:
            default_loc = ""
            if selected_region and selected_region in BODY_REGIONS:
                default_loc = BODY_REGIONS[selected_region][0]
            body_location = st.text_input("发生部位",
                                           value=default_loc,
                                           placeholder="如：手腕、鼻部",
                                           key="c_body_location")

        triggers = st.multiselect("诱发因素", TRIGGER_OPTIONS, key="c_triggers")
        log_date = st.date_input("发生日期", value=date.today(), key="c_log_date")

        with st.expander("🌍 环境数据（已自动获取）", expanded=False):
            env_col1, env_col2, env_col3 = st.columns(3)
            with env_col1:
                env_pollen = st.text_input("花粉指数",
                                            value=pollen["pollen_level"],
                                            key="c_env_pollen")
            with env_col2:
                env_pm25 = st.number_input("PM2.5", min_value=0,
                                            max_value=500, value=35,
                                            key="c_env_pm25")
            with env_col3:
                env_humidity = st.number_input("湿度%", min_value=0,
                                                max_value=100,
                                                value=pollen["humidity"],
                                                key="c_env_humidity")

        col_btn1, col_btn2 = st.columns([3, 1])
        with col_btn1:
            analyze_btn = st.button("🧠 AI 解剖分析", type="primary",
                                     use_container_width=True,
                                     disabled=not symptom_text,
                                     key="c_analyze_btn")
        with col_btn2:
            save_btn = st.button("💾 保存日志", use_container_width=True,
                                  disabled=not symptom_text,
                                  key="c_save_btn")

        if save_btn and symptom_text:
            env_data = {"pollen": env_pollen, "pm25": env_pm25,
                        "humidity": env_humidity}
            db.add_symptom_log(
                profile["id"], str(log_date), symptom_text,
                body_location, body_location, severity, duration,
                triggers, env_data, "",
                user_id=st.session_state.get("auth_user_id")
            )
            st.success("✅ 症状日志已保存！")

    # ── AI 分析（触发后在下方全宽展示）─────────────────────────────────────
    if analyze_btn and symptom_text:
        recent_records = db.get_latest_abnormal_records(profile["id"], user_id=st.session_state.get("auth_user_id"))
        with st.spinner("🔬 AI 正在分析解剖部位和致病因子..."):
            result = agent.analyze_symptom(
                symptom_text, body_location, profile,
                recent_records, pollen
            )
        st.session_state["c_last_result"] = result
        st.session_state["c_last_symptom"] = symptom_text

    result = st.session_state.get("c_last_result")
    if result and st.session_state.get("c_last_symptom"):
        _render_analysis_result(result)


def _render_analysis_result(result: dict):
    """以卡片形式展示 AI 分析结果。"""
    st.markdown("---")
    st.markdown("### 🔬 AI 解剖分析报告")

    # 解剖映射卡片
    anatomy_list = result.get("anatomy", [])
    if not anatomy_list:
        # 兼容旧格式
        am = result.get("anatomy_mapping", "")
        if am:
            anatomy_list = [{"structure": am,
                             "system": result.get("anatomy_system", ""),
                             "note": ""}]

    if anatomy_list:
        st.markdown("#### 🫀 解剖结构映射")
        anat_cols = st.columns(min(len(anatomy_list), 3))
        for i, anat in enumerate(anatomy_list[:3]):
            with anat_cols[i]:
                st.markdown(
                    f"""<div style='background:linear-gradient(135deg,#1a2744,#21253A);
                        border:1px solid #2E3250;border-radius:10px;padding:14px;
                        text-align:center;'>
                        <div style='font-size:28px;'>🦴</div>
                        <div style='color:#4F8EF7;font-size:13px;font-weight:700;
                            margin-top:6px;'>{anat.get("structure","—")}</div>
                        <div style='color:#8892B0;font-size:11px;margin-top:4px;'>
                            {anat.get("system","—")}</div>
                        <div style='color:#E8EAF6;font-size:11px;margin-top:6px;'>
                            {anat.get("note","")}</div>
                    </div>""",
                    unsafe_allow_html=True
                )

    # 致病因子
    causes = result.get("causes", result.get("possible_causes", []))
    if causes:
        st.markdown("#### 🔍 可能致病因子分析")
        for cause in causes[:4]:
            prob = cause.get("probability", "中")
            pc = ("#E74C3C" if prob == "高" else
                  "#F39C12" if prob == "中" else "#2ECC71")
            st.markdown(
                f"""<div style='background:#21253A;border:1px solid #2E3250;
                    border-left:3px solid {pc};border-radius:8px;
                    padding:12px;margin-bottom:8px;'>
                    <div style='display:flex;justify-content:space-between;
                        align-items:center;'>
                        <div style='color:#E8EAF6;font-size:13px;font-weight:600;'>
                            {cause.get("cause","—")}</div>
                        <span style='background:{pc}22;color:{pc};
                            border:1px solid {pc}44;border-radius:20px;
                            padding:2px 10px;font-size:11px;font-weight:600;'>
                            {prob} 概率</span>
                    </div>
                    <div style='color:#8892B0;font-size:12px;margin-top:6px;'>
                        {cause.get("explanation","")}</div>
                </div>""",
                unsafe_allow_html=True
            )

    # 与体检指标的相关性
    correlations = result.get("lab_correlations", [])
    if correlations:
        st.markdown("#### 🔗 与历史体检指标的相关性")
        for corr in correlations[:3]:
            st.markdown(
                f"""<div style='background:rgba(167,139,250,0.08);
                    border:1px solid rgba
(167,139,250,0.3);border-radius:8px;
                    padding:12px;margin-bottom:8px;'>
                    <div style='color:#A78BFA;font-size:12px;font-weight:600;'>
                        📊 {corr.get("indicator","—")} 与本次症状的关联</div>
                    <div style='color:#E8EAF6;font-size:12px;margin-top:4px;'>
                        {corr.get("explanation","")}</div>
                </div>""",
                unsafe_allow_html=True
            )

    # 红色预警
    flags = result.get("red_flags", [])
    if flags:
        st.markdown("#### 🚨 需要关注的警示信号")
        for flag in flags:
            st.error(f"⚠️ {flag}")

    # 自我护理建议
    self_care = result.get("self_care", [])
    if self_care:
        st.markdown("#### 💊 自我护理建议")
        for tip in self_care[:4]:
            st.markdown(
                f"<div style='color:#E8EAF6;font-size:13px;padding:4px 0;'>"
                f"✅ {tip}</div>",
                unsafe_allow_html=True
            )

    # 综合摘要
    summary = result.get("summary", result.get("analysis_summary", ""))
    if summary:
        st.markdown("---")
        st.markdown(
            f"""<div style='background:linear-gradient(135deg,#1a2744,#21253A);
                border:1px solid #2E3250;border-radius:12px;padding:16px;'>
                <div style='color:#4F8EF7;font-size:12px;font-weight:700;
                    letter-spacing:1px;margin-bottom:10px;'>🤖 AI 综合分析摘要</div>
                <div style='color:#E8EAF6;font-size:13px;line-height:1.7;'>
                    {summary}</div>
            </div>""",
            unsafe_allow_html=True
        )


def _render_symptom_log(profile: dict):
    """症状历史日志 Tab。"""
    st.markdown("### 📋 症状记录历史")

    symptoms = db.get_symptom_logs(profile["id"], user_id=st.session_state.get("auth_user_id"))
    if not symptoms:
        st.info("暂无症状记录。")
        return

    fig = utils.plot_symptom_calendar(symptoms)
    if fig:
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"**共 {len(symptoms)} 条记录**")
    for sym in sorted(symptoms, key=lambda s: s.get("log_date", ""), reverse=True)[:20]:
        severity = sym.get("severity", 0)
        color = ("#E74C3C" if severity >= 7 else
                 "#F39C12" if severity >= 4 else "#2ECC71")
        try:
            triggers_list = json.loads(sym.get("triggers", "[]") or "[]")
        except Exception:
            triggers_list = []
        try:
            env_data = json.loads(sym.get("environmental_data", "{}") or "{}")
        except Exception:
            env_data = {}

        desc = sym.get("symptom_description", "")
        short_desc = desc[:40] + ("..." if len(desc) > 40 else "")
        with st.expander(
            f"📅 {sym.get('log_date','—')} — {short_desc} [严重度 {severity}/10]",
            expanded=False
        ):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"**解剖部位**：{sym.get('anatomy_mapping','未分析')}")
                st.markdown(f"**发生部位**：{sym.get('body_location','未记录')}")
            with c2:
                st.markdown(
                    f"**严重程度**：<span style='color:{color};'>{severity}/10</span>",
                    unsafe_allow_html=True
                )
                st.markdown(f"**持续时间**：{sym.get('duration_minutes',0)} 分钟")
            with c3:
                if env_data:
                    st.markdown(f"**花粉**：{env_data.get('pollen','-')}")
                    st.markdown(f"**PM2.5**：{env_data.get('pm25','-')} μg/m³")
            if triggers_list:
                st.markdown("**诱发因素**：" + "、".join(triggers_list))
            if sym.get("ai_analysis"):
                st.markdown("**AI 分析**：")
                st.markdown(sym["ai_analysis"])
