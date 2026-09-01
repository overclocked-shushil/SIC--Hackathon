"""
app.py
Apple-style Weather Dashboard — Streamlit entry point.
All layout & orchestration lives here; business logic is in api/utils/styles.
"""

from __future__ import annotations

import time

import streamlit as st

from api import (
    forward_geocode,
    get_air_quality,
    get_ip_location,
    get_onecall,
    reverse_geocode,
)
from styles import (
    card,
    compass_svg,
    get_activity_recommendations,
    get_background_css,
    get_base_css,
    get_clothing_recommendation,
    moon_emoji,
    pressure_gauge_svg,
    sun_arc_svg,
)
from utils import (
    aqi_color,
    aqi_from_pm25,
    aqi_label,
    condition_summary,
    day_label,
    days_to_full_moon,
    feels_like_reason,
    fmt_temp,
    hour_label,
    icon_url,
    moon_illumination,
    moon_phase_name,
    sun_fraction,
    time_from_unix,
    uv_category,
    visibility_note,
    wind_direction,
)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Weather Dashboard", page_icon="⛅", layout="wide")

# ── Defaults ─────────────────────────────────────────────────────────────────
_DEFAULT = dict(name="Bengaluru", lat=12.9716, lon=77.5946, country="IN")


# ══════════════════════════════════════════════════════════════════════════════
# Session state helpers
# ══════════════════════════════════════════════════════════════════════════════

def _init_state():
    if "location" not in st.session_state:
        st.session_state["location"] = None  # resolved later
    if "recent" not in st.session_state:
        st.session_state["recent"] = []
    if "units" not in st.session_state:
        st.session_state["units"] = "metric"
    if "active_view" not in st.session_state:
        st.session_state["active_view"] = "dashboard"


def _set_location(loc: dict):
    st.session_state["location"] = loc
    _add_recent(loc["name"])


def _add_recent(name: str):
    r = st.session_state["recent"]
    if name in r:
        r.remove(name)
    r.insert(0, name)
    st.session_state["recent"] = r[:5]


def _resolve_initial_location():
    """On very first load, resolve location via IP → default fallback."""
    if st.session_state["location"] is not None:
        return
    with st.spinner("Detecting your location…"):
        loc = get_ip_location()
        if loc:
            geo = reverse_geocode(loc["lat"], loc["lon"])
            if geo:
                _set_location(geo)
                return
            _set_location(loc)
            return
        _set_location(_DEFAULT)


# ══════════════════════════════════════════════════════════════════════════════
# Sidebar
# ══════════════════════════════════════════════════════════════════════════════

def _sidebar():
    with st.sidebar:
        st.markdown("### ⛅ Weather")
        city = st.text_input("Search city", placeholder="Enter city name…",
                            label_visibility="collapsed")

        c1, c2 = st.columns(2)
        with c1:
            search = st.button("🔍 Search", use_container_width=True)
        with c2:
            locate = st.button("📍 My Location", use_container_width=True)

        if search and city.strip():
            geo = forward_geocode(city.strip())
            if geo:
                _set_location(geo)
                st.rerun()
            else:
                st.error(f"City '{city}' not found.")

        if locate:
            loc = get_ip_location()
            if loc:
                geo = reverse_geocode(loc["lat"], loc["lon"])
                _set_location(geo or loc)
                st.rerun()
            else:
                st.warning("Could not detect location.")

        # Navigation
        st.divider()
        st.markdown("### 📍 Navigation")
        if st.button("📊 Weather Dashboard", use_container_width=True):
            st.session_state["active_view"] = "dashboard"
            st.rerun()

        if st.button("💡 Insights & Activities", use_container_width=True):
            st.session_state["active_view"] = "insights"
            st.rerun()

        # Unit toggle
        st.divider()
        is_f = st.toggle("Show in °F", value=(st.session_state["units"] == "imperial"))
        new_unit = "imperial" if is_f else "metric"
        if new_unit != st.session_state["units"]:
            st.session_state["units"] = new_unit
            st.rerun()

        # Recent locations
        recents = st.session_state.get("recent", [])
        if recents:
            st.divider()
            st.caption("RECENT LOCATIONS")
            for rname in recents:
                if st.button(f"📌 {rname}", key=f"rec_{rname}", use_container_width=True):
                    geo = forward_geocode(rname)
                    if geo:
                        _set_location(geo)
                        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# Header
# ══════════════════════════════════════════════════════════════════════════════

def _header(weather: dict, loc: dict, tz: int):
    cur = weather["current"]
    summary = condition_summary(weather.get("hourly", []), cur, tz)
    cond = cur["weather"][0]["description"].title()

    st.markdown(f"""
    <div class="dash-header">
        <div class="city">📍 {loc.get('country', '')}</div>
        <div class="city-name">{loc['name']}</div>
        <div class="big-temp">{fmt_temp(cur['temp'])}</div>
        <div class="summary">{cond}  ·  {summary}</div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Hourly strip
# ══════════════════════════════════════════════════════════════════════════════

def _hourly(weather: dict, tz: int):
    hours = weather.get("hourly", [])[:16]
    if not hours:
        return

    items_html = ""
    for i, h in enumerate(hours):
        t = "Now" if i == 0 else hour_label(h["dt"], tz)
        ic = icon_url(h["weather"][0]["icon"])
        pop = h.get("pop", 0)
        pop_str = f"{round(pop * 100)}%" if pop > 0.05 else ""
        temp = fmt_temp(h["temp"])

        items_html += f"""
        <div class="hourly-item">
            <div class="h-time">{t}</div>
            <div class="h-icon"><img src="{ic}" alt=""></div>
            <div class="h-pop">{pop_str}</div>
            <div class="h-temp">{temp}</div>
        </div>"""

    st.markdown(f"""
    <div class="hourly-wrap">
        <div class="hourly-strip">{items_html}</div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# 10-Day Forecast
# ══════════════════════════════════════════════════════════════════════════════

def _forecast_card(weather: dict, tz: int):
    daily = weather.get("daily", [])
    if not daily:
        return

    all_lo = min(d["temp"]["min"] for d in daily)
    all_hi = max(d["temp"]["max"] for d in daily)
    span = all_hi - all_lo or 1

    rows = ""
    for d in daily:
        day = day_label(d["dt"], tz)
        ic = icon_url(d["weather"][0]["icon"], 2)
        pop = d.get("pop", 0)
        pop_str = f"{round(pop * 100)}%" if pop > 0.05 else ""
        lo = round(d["temp"]["min"])
        hi = round(d["temp"]["max"])

        left_pct = ((d["temp"]["min"] - all_lo) / span) * 100
        width_pct = ((d["temp"]["max"] - d["temp"]["min"]) / span) * 100

        rows += f"""
        <div class="fc-row">
            <div class="fc-day">{day}</div>
            <div class="fc-icon"><img src="{ic}" alt=""></div>
            <div class="fc-pop">{pop_str}</div>
            <div class="fc-lo">{lo}°</div>
            <div class="fc-bar-wrap">
                <div class="fc-bar" style="left:{left_pct:.1f}%;width:{width_pct:.1f}%"></div>
            </div>
            <div class="fc-hi">{hi}°</div>
        </div>"""

    body = f'<div>{rows}</div>'
    st.markdown(card("📅", "10-DAY FORECAST", body, "wcard-lg"), unsafe_allow_html=True)

    for d in daily:
        day = day_label(d["dt"], tz)
        desc = d["weather"][0]["description"].title()
        with st.expander(f"{day} — {desc}"):
            ec1, ec2, ec3, ec4 = st.columns(4)
            ec1.metric("🌡 High", fmt_temp(d["temp"]["max"]))
            ec2.metric("🌡 Low", fmt_temp(d["temp"]["min"]))
            ec3.metric("💨 Wind", f"{round(d.get('wind_speed', 0))} kph")
            ec4.metric("💧 Humidity", f"{d.get('humidity', 0)}%")


# ══════════════════════════════════════════════════════════════════════════════
# Air Quality card
# ══════════════════════════════════════════════════════════════════════════════

def _aqi_card(aqi_data: dict | None):
    if not aqi_data:
        st.markdown(card("🌫", "AIR QUALITY", '<div class="wcard-sub">Data unavailable</div>'),
                    unsafe_allow_html=True)
        return

    pm25 = aqi_data.get("components", {}).get("pm2_5", 0)
    aqi_val = aqi_from_pm25(pm25)
    label = aqi_label(aqi_val)
    marker_pct = min(aqi_val / 500 * 100, 100)

    body = f"""
    <div class="wcard-val">{aqi_val}</div>
    <div class="wcard-lbl">{label}</div>
    <div class="aqi-bar"><div class="aqi-marker" style="left:{marker_pct:.1f}%"></div></div>
    <div class="wcard-sub">Air quality index is {aqi_val}, based on PM2.5 levels.</div>
    """
    st.markdown(card("🌫", "AIR QUALITY", body), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Wind card
# ══════════════════════════════════════════════════════════════════════════════

def _wind_card(cur: dict):
    speed = cur.get("wind_speed", 0)
    gust = cur.get("wind_gust", speed)
    deg = cur.get("wind_deg", 0)
    direction = wind_direction(deg)
    unit = "kph" if st.session_state["units"] == "metric" else "mph"

    svg = compass_svg(deg, speed, unit)
    details = f"""
    <div class="wind-row"><span class="wind-label">Wind</span><span class="wind-val">{round(speed)} {unit}</span></div>
    <div class="wind-row"><span class="wind-label">Gusts</span><span class="wind-val">{round(gust)} {unit}</span></div>
    <div class="wind-row"><span class="wind-label">Direction</span><span class="wind-val">{deg}° {direction}</span></div>
    """
    body = svg + details
    st.markdown(card("💨", "WIND", body), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Map card
# ══════════════════════════════════════════════════════════════════════════════

def _map_card(loc: dict):
    try:
        import folium
        from streamlit_folium import st_folium

        m = folium.Map(
            location=[loc["lat"], loc["lon"]],
            zoom_start=9,
            tiles="CartoDB dark_matter",
            control_scale=False,
            zoom_control=False,
        )
        folium.Marker(
            [loc["lat"], loc["lon"]],
            popup=loc["name"],
            tooltip="My Location",
            icon=folium.Icon(color="blue", icon="cloud"),
        ).add_to(m)

        st.markdown('<div class="wcard-hdr">🗺 WIND MAP</div>', unsafe_allow_html=True)
        st_folium(m, height=320, use_container_width=True,
                  returned_objects=[])
    except ImportError:
        st.markdown(card("🗺", "MAP",
                         f'<div class="wcard-sub">Install streamlit-folium for map view.<br>'
                         f'Lat: {loc["lat"]:.2f}, Lon: {loc["lon"]:.2f}</div>'),
                    unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# UV Index card
# ══════════════════════════════════════════════════════════════════════════════

def _uv_card(cur: dict, daily_today: dict, tz: int):
    uvi = cur.get("uvi", 0)
    label, color = uv_category(uvi)
    marker_pct = min(uvi / 12 * 100, 100)

    sunset = daily_today.get("sunset", 0)
    safe_until = time_from_unix(sunset, tz) if sunset else "—"
    note = f"Use sun protection until {safe_until}." if uvi > 3 else "No protection needed."

    body = f"""
    <div class="wcard-val" style="color:{color}">{round(uvi)}</div>
    <div class="wcard-lbl">{label}</div>
    <div class="uv-bar"><div class="uv-marker" style="left:{marker_pct:.1f}%"></div></div>
    <div class="wcard-sub">{note}</div>
    """
    st.markdown(card("☀️", "UV INDEX", body, "wcard-sm"), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Sunset / Sunrise card
# ══════════════════════════════════════════════════════════════════════════════

def _sunset_card(cur: dict, daily_today: dict, tz: int):
    sunrise = daily_today.get("sunrise", 0)
    sunset = daily_today.get("sunset", 0)
    now_ts = cur.get("dt", 0)

    sr_str = time_from_unix(sunrise, tz) if sunrise else "—"
    ss_str = time_from_unix(sunset, tz) if sunset else "—"
    frac = sun_fraction(sunrise, sunset, now_ts)

    svg = sun_arc_svg(frac, sr_str, ss_str)
    body = f"""
    <div class="wcard-val">{ss_str}</div>
    {svg}
    <div class="wcard-sub">Sunrise: {sr_str}</div>
    """
    st.markdown(card("🌅", "SUNSET", body, "wcard-sm"), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Feels Like card
# ══════════════════════════════════════════════════════════════════════════════

def _feelslike_card(cur: dict):
    feels = cur.get("feels_like", cur.get("temp", 0))
    actual = cur.get("temp", 0)
    wind = cur.get("wind_speed", 0)
    hum = cur.get("humidity", 0)
    reason = feels_like_reason(feels, actual, wind, hum)

    body = f"""
    <div class="wcard-val">{fmt_temp(feels)}</div>
    <div class="wcard-sub">{reason}</div>
    """
    st.markdown(card("🌡", "FEELS LIKE", body, "wcard-sm"), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Precipitation card
# ══════════════════════════════════════════════════════════════════════════════

def _precip_card(daily: list):
    today_rain = daily[0].get("rain", 0) if daily else 0
    tomorrow_rain = daily[1].get("rain", 0) if len(daily) > 1 else 0
    today_pop = daily[0].get("pop", 0) if daily else 0

    body = f"""
    <div class="wcard-val">{today_rain:.1f} mm</div>
    <div class="wcard-lbl">Today</div>
    <div class="wcard-sub">{tomorrow_rain:.1f} mm expected tomorrow.<br>
    {round(today_pop * 100)}% chance of rain today.</div>
    """
    st.markdown(card("🌧", "PRECIPITATION", body, "wcard-sm"), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Moon Phase card
# ══════════════════════════════════════════════════════════════════════════════

def _moon_card(daily_today: dict, tz: int):
    phase = daily_today.get("moon_phase", 0)
    name = moon_phase_name(phase)
    illum = moon_illumination(phase)
    dtf = days_to_full_moon(phase)
    moonrise = daily_today.get("moonrise", 0)
    mr_str = time_from_unix(moonrise, tz) if moonrise else "—"
    emoji = moon_emoji(phase)

    body = f"""
    <div class="wcard-lbl" style="text-transform:uppercase">{name}</div>
    <div class="moon-emoji">{emoji}</div>
    <div class="wcard-sub">
        Illumination &nbsp;&nbsp; <strong>{illum}%</strong><br>
        Moonrise &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <strong>{mr_str}</strong><br>
        Next Full Moon &nbsp; <strong>{dtf} days</strong>
    </div>
    """
    st.markdown(card("🌙", f"MOON — {name.upper()}", body, "wcard-sm"), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Humidity card
# ══════════════════════════════════════════════════════════════════════════════

def _humidity_card(cur: dict):
    hum = cur.get("humidity", 0)
    dew = cur.get("dew_point", 0)

    body = f"""
    <div class="wcard-val">{hum}%</div>
    <div class="wcard-sub">The dew point is {fmt_temp(dew)} right now.</div>
    """
    st.markdown(card("💧", "HUMIDITY", body, "wcard-sm"), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Visibility card
# ══════════════════════════════════════════════════════════════════════════════

def _visibility_card(cur: dict):
    vis_m = cur.get("visibility", 10000)
    km = vis_m / 1000
    note = visibility_note(vis_m)

    body = f"""
    <div class="wcard-val">{km:.0f} km</div>
    <div class="wcard-sub">{note}</div>
    """
    st.markdown(card("👁", "VISIBILITY", body, "wcard-sm"), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Pressure card
# ══════════════════════════════════════════════════════════════════════════════

def _pressure_card(cur: dict):
    hpa = cur.get("pressure", 1013)
    svg = pressure_gauge_svg(hpa)

    body = f"""
    {svg}
    """
    st.markdown(card("⏱", "PRESSURE", body, "wcard-sm"), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Averages card
# ══════════════════════════════════════════════════════════════════════════════

def _averages_card(daily: list):
    if not daily:
        st.markdown(card("📊", "AVERAGES", '<div class="wcard-sub">No data</div>', "wcard-sm"),
                    unsafe_allow_html=True)
        return

    today_hi = daily[0]["temp"]["max"]
    week_avg = sum(d["temp"]["max"] for d in daily) / len(daily)
    diff = today_hi - week_avg
    sign = "+" if diff >= 0 else ""

    body = f"""
    <div class="wcard-val">{sign}{diff:.0f}°</div>
    <div class="wcard-lbl">{"above" if diff >= 0 else "below"} average daily high</div>
    <div class="wcard-sub">
        Today &nbsp;&nbsp;&nbsp;&nbsp; H:{round(today_hi)}°<br>
        Average &nbsp; H:{round(week_avg)}°
    </div>
    """
    st.markdown(card("📊", "AVERAGES", body, "wcard-sm"), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    _init_state()

    # Inject base CSS immediately
    st.markdown(get_base_css(), unsafe_allow_html=True)

    # Sidebar (may trigger rerun)
    _sidebar()

    # Resolve location on first visit
    _resolve_initial_location()
    loc = st.session_state["location"]
    if not loc:
        st.error("Unable to determine location. Please search for a city.")
        return

    # ── Fetch data ───────────────────────────────────────────────────────────
    units = st.session_state["units"]
    weather = get_onecall(loc["lat"], loc["lon"], units)
    aqi_data = get_air_quality(loc["lat"], loc["lon"])

    if not weather:
        st.error("⚠️ Failed to fetch weather data. Check your API key in `.streamlit/secrets.toml`.")
        return

    cur = weather["current"]
    daily = weather.get("daily", [])
    tz = weather.get("timezone_offset", 0)
    daily_today = daily[0] if daily else {}

    # ── Dynamic background ───────────────────────────────────────────────────
    cond_id = cur["weather"][0]["id"]
    icon_code = cur["weather"][0]["icon"]
    st.markdown(get_background_css(cond_id, icon_code), unsafe_allow_html=True)

    # ── Render View based on active_view ─────────────────────────────────────
    if st.session_state.get("active_view") == "insights":
        # INSIGHTS & ACTIVITIES VIEW
        st.markdown(f"<h2 style='text-align: center;'>Weather Insights for {loc['name']}</h2>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        current_temp = cur["temp"]
        condition_code = cond_id
        wind_speed = cur.get("wind_speed", 0)
        is_day = not icon_code.endswith("n")

        # Convert imperial to metric if needed for the logic function limits
        temp_c = (current_temp - 32) * 5 / 9 if units == "imperial" else current_temp
        wind_kph = wind_speed * 1.60934 if units == "imperial" else wind_speed

        clothing = get_clothing_recommendation(temp_c, condition_code, is_day)
        activities = get_activity_recommendations(temp_c, condition_code, wind_kph)

        col1, col2 = st.columns(2)

        with col1:
            items_html = "".join([f"<li style='margin-bottom: 6px;'>{item}</li>" for item in clothing["items"]])
            clothing_body = f"""
            <div class="wcard-lbl">{clothing['summary']}</div>
            <ul style="padding-left: 18px; color: rgba(255,255,255,0.85); font-size: 14px;">
                {items_html}
            </ul>
            """
            st.markdown(card("👕", "Clothing Recommendation", clothing_body, extra="wcard-lg"), unsafe_allow_html=True)

        with col2:
            outdoor_html = "".join([f"<li style='margin-bottom: 6px;'>{act}</li>" for act in activities["outdoor"]])
            indoor_html = "".join([f"<li style='margin-bottom: 6px;'>{act}</li>" for act in activities["indoor"]])

            activities_body = f"""
            <div style="font-weight: 600; font-size: 14px; margin-bottom: 4px; color: #5ac8fa;">🌲 Outdoor</div>
            <ul style="padding-left: 18px; color: rgba(255,255,255,0.85); font-size: 13px; margin-bottom: 12px;">
                {outdoor_html}
            </ul>
            <div style="font-weight: 600; font-size: 14px; margin-bottom: 4px; color: #ffd60a;">🏠 Indoor</div>
            <ul style="padding-left: 18px; color: rgba(255,255,255,0.85); font-size: 13px;">
                {indoor_html}
            </ul>
            """
            st.markdown(card("🚴", "Suggested Activities", activities_body, extra="wcard-lg"), unsafe_allow_html=True)

    else:
        # MAIN WEATHER DASHBOARD VIEW
        _header(weather, loc, tz)
        _hourly(weather, tz)

        col_left, col_mid, col_right = st.columns([3, 3, 3])
        with col_left:
            _forecast_card(weather, tz)
        with col_mid:
            _aqi_card(aqi_data)
            _wind_card(cur)
        with col_right:
            _map_card(loc)

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        r1c1, r1c2, r1c3, r1c4 = st.columns(4)
        with r1c1:
            _uv_card(cur, daily_today, tz)
        with r1c2:
            _sunset_card(cur, daily_today, tz)
        with r1c3:
            _feelslike_card(cur)
        with r1c4:
            _precip_card(daily)

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        r2c1, r2c2, r2c3, r2c4, r2c5 = st.columns(5)
        with r2c1:
            _moon_card(daily_today, tz)
        with r2c2:
            _humidity_card(cur)
        with r2c3:
            _visibility_card(cur)
        with r2c4:
            _pressure_card(cur)
        with r2c5:
            _averages_card(daily)

    # ── Footer ───────────────────────────────────────────────────────────────
    st.markdown(
        '<div style="text-align:center;padding:30px 0 10px;font-size:11px;'
        'color:rgba(255,255,255,0.3)">Powered by OpenWeatherMap  ·  '
        'Built with ❤️ for the SIC Hackathon Team — Dew Point</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()