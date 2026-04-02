"""
Generate the V5.0 CSS with base64 Da Vinci watermark embedded.
Run this to produce the CSS string for app.py
"""
import base64

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
data_uri = f"data:image/svg+xml;base64,{encoded}"
print(data_uri[:100])
print(f"Total: {len(data_uri)} chars")
