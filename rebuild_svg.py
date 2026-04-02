"""
Replace the _render_body_svg function in module_c_symptoms.py with a proper
anatomical SVG silhouette supporting front/back view toggle.
"""

NEW_SVG_FUNCTION = '''def _render_body_svg(selected: str = None, view: str = "front") -> str:
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
        f\'\'\'<svg viewBox="0 0 200 480" xmlns="http://www.w3.org/2000/svg"
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
        \'\'\'
    ]

    if view == "front":
        # ── FRONT VIEW ──────────────────────────────────────────────────────
        # Head region
        f, s, sw, tc, gf = region_style("head")
        parts.append(f\'\'\'
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
        \'\'\')

        # Nose region (overlapping head)
        f, s, sw, tc, gf = region_style("nose")
        parts.append(f\'\'\'
        <!-- NOSE (hotspot) -->
        <g filter="{"url(#glow-sel)" if selected == "nose" else "none"}">
            <ellipse cx="100" cy="57" rx="7" ry="9"
                     fill="{f}" stroke="{s}" stroke-width="{sw}" opacity="0.8"/>
        </g>
        \'\'\')

        # Neck
        f, s, sw, tc, gf = region_style("neck")
        parts.append(f\'\'\'
        <!-- NECK -->
        <g filter="{"url(#glow-sel)" if selected == "neck" else "none"}">
            <path d="M 91 82 L 88 100 L 112 100 L 109 82 Z"
                  fill="{f}" stroke="{s}" stroke-width="{sw}"/>
            <!-- Trachea -->
            <line x1="100" y1="84" x2="100" y2="98" stroke="{s}" stroke-width="0.4" stroke-dasharray="2,2"/>
            <text x="100" y="97" text-anchor="middle" font-size="6" fill="{tc}"
                  font-family="Inter,sans-serif">颈部</text>
        </g>
        \'\'\')

        # Shoulders and arms base
        f_la, s_la, sw_la, tc_la, _ = region_style("left_arm")
        f_ra, s_ra, sw_ra, tc_ra, _ = region_style("right_arm")
        f_lw, s_lw, sw_lw, tc_lw, _ = region_style("left_wrist")
        f_rw, s_rw, sw_rw, tc_rw, _ = region_style("right_wrist")

        # Chest
        f, s, sw, tc, gf = region_style("chest")
        parts.append(f\'\'\'
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
        \'\'\')

        # Abdomen
        f, s, sw, tc, gf = region_style("abdomen")
        parts.append(f\'\'\'
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
        \'\'\')

        # Pelvis / Lower back
        f, s, sw, tc, gf = region_style("lower_back")
        parts.append(f\'\'\'
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
        \'\'\')

        # Left arm
        parts.append(f\'\'\'
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
        \'\'\')

        # Right arm
        parts.append(f\'\'\'
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
        \'\'\')

        # Left knee
        f, s, sw, tc, gf = region_style("left_knee")
        parts.append(f\'\'\'
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
        \'\'\')

        # Right knee
        f, s, sw, tc, gf = region_style("right_knee")
        parts.append(f\'\'\'
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
        \'\'\')

    else:
        # ── BACK VIEW ───────────────────────────────────────────────────────
        # Head (back)
        f, s, sw, tc, _ = region_style("head")
        parts.append(f\'\'\'
        <!-- HEAD BACK -->
        <g filter="{"url(#glow-sel)" if selected == "head" else "none"}">
            <ellipse cx="100" cy="52" rx="28" ry="30"
                     fill="{f}" stroke="{s}" stroke-width="{sw}"/>
            <!-- Occipital line -->
            <path d="M 75 60 Q 100 55 125 60" fill="none" stroke="{s}" stroke-width="0.4"/>
            <text x="100" y="84" text-anchor="middle" font-size="7" fill="{tc}"
                  font-family="Inter,sans-serif" font-weight="500">头部(后)</text>
        </g>
        \'\'\')

        # Neck back
        f, s, sw, tc, _ = region_style("neck")
        parts.append(f\'\'\'
        <!-- NECK BACK -->
        <g filter="{"url(#glow-sel)" if selected == "neck" else "none"}">
            <path d="M 91 82 L 88 100 L 112 100 L 109 82 Z"
                  fill="{f}" stroke="{s}" stroke-width="{sw}"/>
            <!-- Cervical spine -->
            <line x1="100" y1="84" x2="100" y2="98" stroke="{s}" stroke-width="0.6" stroke-dasharray="2,2"/>
            <text x="100" y="97" text-anchor="middle" font-size="6" fill="{tc}"
                  font-family="Inter,sans-serif">颈椎</text>
        </g>
        \'\'\')

        # Upper back / shoulders
        f, s, sw, tc, _ = region_style("chest")
        parts.append(f\'\'\'
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
        \'\'\')

        # Lower back (back view)
        f, s, sw, tc, _ = region_style("lower_back")
        parts.append(f\'\'\'
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
        \'\'\')

        # Arms (back view same as front)
        f_la, s_la, sw_la, tc_la, _ = region_style("left_arm")
        f_ra, s_ra, sw_ra, tc_ra, _ = region_style("right_arm")
        f_lw, s_lw, sw_lw, tc_lw, _ = region_style("left_wrist")
        f_rw, s_rw, sw_rw, tc_rw, _ = region_style("right_wrist")
        parts.append(f\'\'\'
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
        \'\'\')

        # Legs (back view)
        f_lk, s_lk, sw_lk, tc_lk, _ = region_style("left_knee")
        f_rk, s_rk, sw_rk, tc_rk, _ = region_style("right_knee")
        parts.append(f\'\'\'
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
        \'\'\')

    # Bottom decorative line
    parts.append(\'\'\'
    <!-- Bottom hairline -->
    <line x1="20" y1="460" x2="180" y2="460" stroke="url(#goldGrad)" stroke-width="0.5"/>
    </svg>\'\'\')

    return "".join(parts)

'''

# Read the current module_c_symptoms.py
with open('/home/ubuntu/AnatomySelf/modules/module_c_symptoms.py', 'r') as f:
    content = f.read()

# Find and replace the _render_body_svg function
start_marker = 'def _render_body_svg(selected: str =\n None) -> str:'
end_marker = 'def render():'

start_idx = content.find('def _render_body_svg(selected: str =')
end_idx = content.find('def render():', start_idx)

if start_idx == -1:
    print("ERROR: Could not find _render_body_svg function!")
else:
    new_content = content[:start_idx] + NEW_SVG_FUNCTION + '\n' + content[end_idx:]
    with open('/home/ubuntu/AnatomySelf/modules/module_c_symptoms.py', 'w') as f:
        f.write(new_content)
    print(f"SVG function replaced! New function length: {len(NEW_SVG_FUNCTION)} chars")
    print(f"File size: {len(new_content)} chars")
