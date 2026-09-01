"""
styles.py
All CSS strings, dynamic background selector with rotating Unsplash images, and reusable HTML helpers.
"""

from __future__ import annotations
import random


def clean_html(html_str: str) -> str:
    """Strips leading line indentation to prevent Markdown from turning HTML into code blocks."""
    return "\n".join(line.strip() for line in html_str.splitlines())


# ── Dynamic Background Image Pools (3 images per condition) ──────────────────

_BG_IMAGES = {
    "clear_d": [
        "https://images.unsplash.com/photo-1622396481328-9b1b78cdd9fd?q=80&w=1920&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?q=80&w=1920&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1470240731273-7821a6eeb6bd?q=80&w=1920&auto=format&fit=crop",
    ],
    "clear_n": [
        "https://images.unsplash.com/photo-1509114397022-ed747cca3f65?q=80&w=1920&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?q=80&w=1920&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1532978379173-523e16f371f2?q=80&w=1920&auto=format&fit=crop",
    ],
    "fewclouds_d": [
        "https://images.unsplash.com/photo-1534088568595-a066f410bcda?q=80&w=1920&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1501630834273-4b5604d2ee31?q=80&w=1920&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1517685352821-92cf88aee5a5?q=80&w=1920&auto=format&fit=crop",
    ],
    "fewclouds_n": [
        "https://images.unsplash.com/photo-1513002749550-c59d786b8e6c?q=80&w=1920&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1920&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1499346030926-9a72daac6c63?q=80&w=1920&auto=format&fit=crop",
    ],
    "overcast_d": [
        "https://images.unsplash.com/photo-1534088568595-a066f410bcda?q=80&w=1920&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1499346030926-9a72daac6c63?q=80&w=1920&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1513002749550-c59d786b8e6c?q=80&w=1920&auto=format&fit=crop",
    ],
    "overcast_n": [
        "https://images.unsplash.com/photo-1499346030926-9a72daac6c63?q=80&w=1920&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1920&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1513002749550-c59d786b8e6c?q=80&w=1920&auto=format&fit=crop",
    ],
    "rain_d": [
        "https://images.unsplash.com/photo-1519692933481-e162a57d6721?q=80&w=1920&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1534274988757-a28bf1a57c17?q=80&w=1920&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1428592953211-077101b2021b?q=80&w=1920&auto=format&fit=crop",
    ],
    "rain_n": [
        "https://images.unsplash.com/photo-1508873696983-2df515122519?q=80&w=1920&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1515694346937-94d85e41e6f0?q=80&w=1920&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1501999635878-71cb5379c2d4?q=80&w=1920&auto=format&fit=crop",
    ],
    "thunder_d": [
        "https://images.unsplash.com/photo-1605727216801-e27ce1d0cc28?q=80&w=1920&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1511289081-d06d54790e06?q=80&w=1920&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1594156596782-656c93e4d504?q=80&w=1920&auto=format&fit=crop",
    ],
    "thunder_n": [
        "https://images.unsplash.com/photo-1605727216801-e27ce1d0cc28?q=80&w=1920&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1511289081-d06d54790e06?q=80&w=1920&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1509114397022-ed747cca3f65?q=80&w=1920&auto=format&fit=crop",
    ],
    "snow_d": [
        "https://images.unsplash.com/photo-1483664852095-d6cc6870702d?q=80&w=1920&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1517299321531-479908092017?q=80&w=1920&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1491002052546-bf38f186af56?q=80&w=1920&auto=format&fit=crop",
    ],
    "snow_n": [
        "https://images.unsplash.com/photo-1418985991508-e47386d96a71?q=80&w=1920&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1518241353330-0f7941c2d9b5?q=80&w=1920&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1483664852095-d6cc6870702d?q=80&w=1920&auto=format&fit=crop",
    ],
    "fog_d": [
        "https://images.unsplash.com/photo-1487621167305-5d248087c724?q=80&w=1920&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1509803874385-db7c23652552?q=80&w=1920&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1485236715568-ddc5ee6ca227?q=80&w=1920&auto=format&fit=crop",
    ],
    "fog_n": [
        "https://images.unsplash.com/photo-1487621167305-5d248087c724?q=80&w=1920&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1509803874385-db7c23652552?q=80&w=1920&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1513002749550-c59d786b8e6c?q=80&w=1920&auto=format&fit=crop",
    ],
}


def get_background_css(condition_id: int, icon: str) -> str:
    """Map OWM condition code + icon suffix to a random background image URL from its pool."""
    n = "n" if icon.endswith("n") else "d"

    if condition_id == 800:
        key = f"clear_{n}"
    elif condition_id in (801, 802):
        key = f"fewclouds_{n}"
    elif condition_id in (803, 804):
        key = f"overcast_{n}"
    elif 200 <= condition_id <= 232:
        key = f"thunder_{n}"
    elif 300 <= condition_id <= 531:
        key = f"rain_{n}"
    elif 600 <= condition_id <= 622:
        key = f"snow_{n}"
    elif 700 <= condition_id <= 781:
        key = f"fog_{n}"
    else:
        key = f"overcast_{n}"

    images = _BG_IMAGES.get(key, _BG_IMAGES["clear_d"])
    img_url = random.choice(images)

    return f"""<style>
    .stApp {{
        background: linear-gradient(rgba(0, 0, 0, 0.45), rgba(0, 0, 0, 0.45)), url("{img_url}") !important;
        background-size: cover !important;
        background-position: center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
    }}
    </style>"""


# ── Base CSS ─────────────────────────────────────────────────────────────────

def get_base_css() -> str:
    return """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Reset Streamlit chrome ────────────────────────────── */
#MainMenu, footer, header,
[data-testid="stToolbar"],
.stDeployButton { display:none !important; visibility:hidden !important }

.stApp {
    font-family: -apple-system, "SF Pro Display", "Inter", "Segoe UI", Helvetica, sans-serif;
    color: #fff;
}

/* Remove all default backgrounds */
[data-testid="stAppViewContainer"],
[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"],
[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="column"],
[data-testid="stMainBlockContainer"],
.stMarkdown, .element-container {
    background: transparent !important;
}

/* ── Sidebar ───────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: rgba(20,25,40,0.88) !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
    border-right: 1px solid rgba(255,255,255,0.08);
}
[data-testid="stSidebar"] * { color: #e0e4ea !important; }

[data-testid="stSidebar"] .stTextInput > div > div > input {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: #fff !important;
    border-radius: 10px !important;
}

[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.10) !important;
    color: #fff !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 10px !important;
    transition: background 0.2s;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.18) !important;
}

/* Toggle */
[data-testid="stSidebar"] .stToggle label span { color: #ccc !important; }

/* ── Cards ─────────────────────────────────────────────── */
.wcard {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.12);
    padding: 18px 20px;
    color: #fff;
    min-height: 170px;
    box-sizing: border-box;
    transition: background 0.3s;
}
.wcard:hover { background: rgba(255,255,255,0.11); }

.wcard-sm { min-height: 140px; }
.wcard-lg { min-height: 300px; }

.wcard-hdr {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.55);
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 5px;
}
.wcard-val {
    font-size: 38px;
    font-weight: 300;
    line-height: 1.1;
    margin-bottom: 2px;
}
.wcard-lbl {
    font-size: 18px;
    font-weight: 500;
    margin-bottom: 8px;
}
.wcard-sub {
    font-size: 13px;
    color: rgba(255,255,255,0.6);
    line-height: 1.4;
}

/* ── Header ────────────────────────────────────────────── */
.dash-header {
    text-align: center;
    padding: 30px 0 10px;
}
.dash-header .city {
    font-size: 14px;
    font-weight: 500;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.7);
}
.dash-header .city-name {
    font-size: 38px;
    font-weight: 300;
    margin: 2px 0;
}
.dash-header .big-temp {
    font-size: 72px;
    font-weight: 200;
    line-height: 1;
    margin-bottom: 6px;
}
.dash-header .summary {
    font-size: 14px;
    color: rgba(255,255,255,0.75);
    max-width: 520px;
    margin: 0 auto;
}

/* ── Hourly strip ──────────────────────────────────────── */
.hourly-wrap {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.12);
    padding: 14px 6px;
    margin: 14px 0 20px;
    overflow-x: auto;
}
.hourly-strip {
    display: flex;
    gap: 0;
    min-width: max-content;
}
.hourly-item {
    flex: 0 0 68px;
    text-align: center;
    padding: 6px 2px;
}
.hourly-item .h-time {
    font-size: 12px;
    font-weight: 500;
    color: rgba(255,255,255,0.75);
    margin-bottom: 4px;
}
.hourly-item .h-icon img {
    width: 32px;
    height: 32px;
}
.hourly-item .h-pop {
    font-size: 10px;
    color: #5ac8fa;
    font-weight: 600;
    min-height: 14px;
}
.hourly-item .h-temp {
    font-size: 15px;
    font-weight: 500;
}

/* ── Hourly scrollbar ──────────────────────────────────── */
.hourly-wrap::-webkit-scrollbar { height: 4px; }
.hourly-wrap::-webkit-scrollbar-track { background: transparent; }
.hourly-wrap::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 2px; }

/* ── Forecast ──────────────────────────────────────────── */
.fc-row {
    display: flex;
    align-items: center;
    padding: 9px 0;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    gap: 8px;
}
.fc-row:last-child { border-bottom: none; }
.fc-day { width: 50px; font-size: 14px; font-weight: 500; }
.fc-icon img { width: 28px; height: 28px; }
.fc-pop { width: 36px; font-size: 11px; color: #5ac8fa; text-align: right; font-weight: 600; }
.fc-lo { width: 32px; font-size: 14px; color: rgba(255,255,255,0.5); text-align: right; }
.fc-bar-wrap {
    flex: 1;
    height: 5px;
    background: rgba(255,255,255,0.10);
    border-radius: 3px;
    position: relative;
    margin: 0 4px;
}
.fc-bar {
    position: absolute;
    height: 100%;
    border-radius: 3px;
    background: linear-gradient(90deg, #5ac8fa, #34c759, #ffd60a, #ff9f0a, #ff453a);
}
.fc-hi { width: 32px; font-size: 14px; font-weight: 500; }

/* ── AQI bar ───────────────────────────────────────────── */
.aqi-bar {
    height: 6px;
    border-radius: 3px;
    background: linear-gradient(90deg, #4caf50, #8bc34a, #ffc107, #ff9800, #f44336, #7e0023);
    position: relative;
    margin: 12px 0 8px;
}
.aqi-marker {
    position: absolute;
    top: -4px;
    width: 14px;
    height: 14px;
    background: #fff;
    border-radius: 50%;
    border: 2px solid rgba(0,0,0,0.2);
    transform: translateX(-50%);
}

/* ── UV bar ────────────────────────────────────────────── */
.uv-bar {
    height: 5px;
    border-radius: 3px;
    background: linear-gradient(90deg, #4caf50, #8bc34a, #ffc107, #ff9800, #f44336, #9c27b0);
    position: relative;
    margin: 12px 0;
}
.uv-marker {
    position: absolute;
    top: -5px;
    width: 12px; height: 12px;
    background: #fff;
    border-radius: 50%;
    border: 2px solid rgba(0,0,0,0.15);
    transform: translateX(-50%);
}

/* ── Streamlit expander override ───────────────────────── */
[data-testid="stExpander"] {
    background: transparent !important;
    border: none !important;
}
[data-testid="stExpander"] details {
    background: transparent !important;
    border: none !important;
}
[data-testid="stExpander"] summary {
    color: rgba(255,255,255,0.8) !important;
}
[data-testid="stExpander"] summary:hover {
    color: #fff !important;
}

/* ── Column gap helper ─────────────────────────────────── */
[data-testid="stHorizontalBlock"] { gap: 14px !important; }

/* ── Misc Streamlit overrides ──────────────────────────── */
.stAlert, .stException { border-radius: 12px; }
hr { border-color: rgba(255,255,255,0.1) !important; }

/* ── Recent locations ──────────────────────────────────── */
.recent-btn {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 8px;
    padding: 6px 12px;
    color: #ccc;
    font-size: 13px;
    cursor: pointer;
    width: 100%;
    text-align: left;
    margin-bottom: 4px;
    transition: background 0.2s;
}
.recent-btn:hover { background: rgba(255,255,255,0.14); }

/* ── Wind card detail ──────────────────────────────────── */
.wind-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 5px 0;
    font-size: 14px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.wind-row:last-child { border-bottom: none; }
.wind-label { color: rgba(255,255,255,0.55); }
.wind-val { font-weight: 500; }

/* ── Map container ─────────────────────────────────────── */
.map-wrap {
    border-radius: 18px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.12);
}
.map-wrap iframe { border-radius: 18px; }

/* ── Pressure / Gauge ──────────────────────────────────── */
.gauge-wrap { text-align: center; margin: 10px 0; }

/* ── Moon emoji ────────────────────────────────────────── */
.moon-emoji { font-size: 48px; text-align: center; margin: 10px 0; }

</style>"""


# ── HTML helpers ─────────────────────────────────────────────────────────────

def card(icon: str, title: str, body: str, extra: str = "") -> str:
    """Wrap content in a glassmorphism card div."""
    cls = f"wcard {extra}".strip()
    raw = (
        f'<div class="{cls}">'
        f'<div class="wcard-hdr">{icon} {title}</div>'
        f'{body}'
        f'</div>'
    )
    return clean_html(raw)


def compass_svg(deg: float, speed: float, unit: str = "kph") -> str:
    """SVG compass dial pointing in wind direction."""
    import math
    rad = math.radians(deg)
    ax = 60 + 38 * math.sin(rad)
    ay = 60 - 38 * math.cos(rad)
    tx = 60 - 12 * math.sin(rad)
    ty = 60 + 12 * math.cos(rad)

    raw = f"""
    <svg viewBox="0 0 120 120" width="110" height="110" style="display:block;margin:8px auto">
      <circle cx="60" cy="60" r="50" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="1.5"/>
      <circle cx="60" cy="60" r="3" fill="rgba(255,255,255,0.3)"/>
      <text x="60" y="16" text-anchor="middle" fill="rgba(255,255,255,0.5)" font-size="11" font-weight="600">N</text>
      <text x="106" y="64" text-anchor="middle" fill="rgba(255,255,255,0.35)" font-size="10">E</text>
      <text x="60" y="112" text-anchor="middle" fill="rgba(255,255,255,0.35)" font-size="10">S</text>
      <text x="14" y="64" text-anchor="middle" fill="rgba(255,255,255,0.35)" font-size="10">W</text>
      <line x1="{tx:.1f}" y1="{ty:.1f}" x2="{ax:.1f}" y2="{ay:.1f}"
            stroke="white" stroke-width="2" stroke-linecap="round"/>
      <circle cx="{ax:.1f}" cy="{ay:.1f}" r="3.5" fill="white"/>
      <text x="60" y="56" text-anchor="middle" fill="white" font-size="18" font-weight="600">{round(speed)}</text>
      <text x="60" y="72" text-anchor="middle" fill="rgba(255,255,255,0.5)" font-size="10">{unit}</text>
    </svg>"""
    return clean_html(raw)


def sun_arc_svg(fraction: float, sunrise_str: str, sunset_str: str) -> str:
    """SVG sun position arc."""
    import math
    t = max(0.0, min(1.0, fraction))
    sx = 20 + 160 * t
    sy = 70 - 55 * math.sin(math.pi * t)
    is_up = 0 < t < 1

    sun_color = "#FFD700" if is_up else "rgba(255,215,0,0.3)"
    glow = f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="12" fill="rgba(255,215,0,0.15)"/>' if is_up else ""

    raw = f"""
    <svg viewBox="0 0 200 90" width="100%" height="70" style="margin:8px 0">
      <defs>
        <linearGradient id="arcg" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stop-color="rgba(255,255,255,0.1)"/>
          <stop offset="50%" stop-color="rgba(255,215,0,0.3)"/>
          <stop offset="100%" stop-color="rgba(255,255,255,0.1)"/>
        </linearGradient>
      </defs>
      <path d="M 20 70 Q 100 -15 180 70" fill="none" stroke="url(#arcg)" stroke-width="1.5" stroke-dasharray="4,3"/>
      <line x1="15" y1="70" x2="185" y2="70" stroke="rgba(255,255,255,0.12)" stroke-width="1"/>
      {glow}
      <circle cx="{sx:.1f}" cy="{sy:.1f}" r="5" fill="{sun_color}"/>
      <text x="20" y="85" text-anchor="middle" fill="rgba(255,255,255,0.45)" font-size="9">{sunrise_str}</text>
      <text x="180" y="85" text-anchor="middle" fill="rgba(255,255,255,0.45)" font-size="9">{sunset_str}</text>
    </svg>"""
    return clean_html(raw)


def pressure_gauge_svg(hpa: int) -> str:
    """Simple arc gauge for pressure."""
    import math
    norm = max(0, min(1, (hpa - 970) / 80))
    angle = -140 + norm * 280
    rad = math.radians(angle - 90)
    ix = 60 + 36 * math.cos(rad)
    iy = 55 + 36 * math.sin(rad)

    raw = f"""
    <svg viewBox="0 0 120 75" width="100" height="65" style="display:block;margin:6px auto">
      <path d="M 18 65 A 44 44 0 0 1 102 65" fill="none" stroke="rgba(255,255,255,0.12)" stroke-width="3" stroke-linecap="round"/>
      <circle cx="{ix:.1f}" cy="{iy:.1f}" r="4" fill="white"/>
      <text x="60" y="48" text-anchor="middle" fill="white" font-size="20" font-weight="500">{hpa}</text>
      <text x="60" y="62" text-anchor="middle" fill="rgba(255,255,255,0.5)" font-size="9">hPa</text>
    </svg>"""
    return clean_html(raw)


def moon_emoji(phase: float) -> str:
    """Return a moon-phase emoji."""
    if phase < 0.03 or phase > 0.97:
        return "🌑"
    if phase < 0.22:
        return "🌒"
    if phase < 0.28:
        return "🌓"
    if phase < 0.47:
        return "🌔"
    if phase < 0.53:
        return "🌕"
    if phase < 0.72:
        return "🌖"
    if phase < 0.78:
        return "🌗"
    return "🌘"