"""
utils.py
Pure helper functions: formatting, conversions, weather interpretation.
No network calls, no Streamlit dependency — easy to test.
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
import math


# ── Temperature ──────────────────────────────────────────────────────────────

def fmt_temp(temp: float) -> str:
    """Round and format a temperature value with degree symbol."""
    return f"{round(temp)}°"


# ── Time / Date ──────────────────────────────────────────────────────────────

def time_from_unix(ts: int, tz_offset: int, fmt: str = "%H:%M") -> str:
    """Unix timestamp → formatted time string (e.g. '14:30')."""
    dt = datetime.fromtimestamp(ts, tz=timezone(timedelta(seconds=tz_offset)))
    return dt.strftime(fmt)


def hour_label(ts: int, tz_offset: int) -> str:
    """Unix timestamp → short hour label (e.g. '2pm', '14')."""
    dt = datetime.fromtimestamp(ts, tz=timezone(timedelta(seconds=tz_offset)))
    h = dt.hour
    if h == 0:
        return "12am"
    elif h < 12:
        return f"{h}am"
    elif h == 12:
        return "12pm"
    else:
        return f"{h - 12}pm"


def day_label(ts: int, tz_offset: int) -> str:
    """Unix timestamp → day name, or 'Today' if same calendar day."""
    dt = datetime.fromtimestamp(ts, tz=timezone(timedelta(seconds=tz_offset)))
    now = datetime.now(tz=timezone(timedelta(seconds=tz_offset)))
    if dt.date() == now.date():
        return "Today"
    return dt.strftime("%a")


# ── Wind ─────────────────────────────────────────────────────────────────────

_COMPASS = [
    "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
    "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
]


def wind_direction(deg: float) -> str:
    """Degrees (0-360) → compass label."""
    return _COMPASS[round(deg / 22.5) % 16]


# ── OWM Icon ─────────────────────────────────────────────────────────────────

def icon_url(code: str, size: int = 2) -> str:
    return f"https://openweathermap.org/img/wn/{code}@{size}x.png"


# ── AQI ──────────────────────────────────────────────────────────────────────

def aqi_from_pm25(pm25: float) -> int:
    """Compute US-style AQI from PM2.5 µg/m³."""
    bp = [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 500.4, 301, 500),
    ]
    for c_lo, c_hi, i_lo, i_hi in bp:
        if pm25 <= c_hi:
            return round(((i_hi - i_lo) / (c_hi - c_lo)) * (pm25 - c_lo) + i_lo)
    return 500


def aqi_label(aqi: int) -> str:
    if aqi <= 50:
        return "Good"
    if aqi <= 100:
        return "Satisfactory"
    if aqi <= 150:
        return "Moderate"
    if aqi <= 200:
        return "Poor"
    if aqi <= 300:
        return "Very Poor"
    return "Severe"


def aqi_color(aqi: int) -> str:
    if aqi <= 50:
        return "#4caf50"
    if aqi <= 100:
        return "#8bc34a"
    if aqi <= 150:
        return "#ffc107"
    if aqi <= 200:
        return "#ff9800"
    if aqi <= 300:
        return "#f44336"
    return "#7e0023"


# ── UV Index ─────────────────────────────────────────────────────────────────

def uv_category(uvi: float) -> tuple[str, str]:
    """(label, hex colour)."""
    if uvi <= 2:
        return "Low", "#4caf50"
    if uvi <= 5:
        return "Moderate", "#ffc107"
    if uvi <= 7:
        return "High", "#ff9800"
    if uvi <= 10:
        return "Very High", "#f44336"
    return "Extreme", "#9c27b0"


# ── Moon ─────────────────────────────────────────────────────────────────────

def moon_phase_name(phase: float) -> str:
    """OWM daily.moon_phase (0-1) → human-readable name."""
    if phase < 0.03 or phase > 0.97:
        return "New Moon"
    if phase < 0.22:
        return "Waxing Crescent"
    if phase < 0.28:
        return "First Quarter"
    if phase < 0.47:
        return "Waxing Gibbous"
    if phase < 0.53:
        return "Full Moon"
    if phase < 0.72:
        return "Waning Gibbous"
    if phase < 0.78:
        return "Last Quarter"
    return "Waning Crescent"


def moon_illumination(phase: float) -> int:
    """Approximate illumination %."""
    return round((1 - abs(2 * phase - 1)) * 100)


def days_to_full_moon(phase: float) -> int:
    """Approximate days until next full moon (phase = 0.5)."""
    if phase <= 0.5:
        return round((0.5 - phase) * 29.53)
    return round((1.5 - phase) * 29.53)


# ── Sun position ─────────────────────────────────────────────────────────────

def sun_fraction(sunrise: int, sunset: int, now: int) -> float:
    """0.0 = sunrise, 1.0 = sunset. Clamped to [0,1]."""
    if now <= sunrise:
        return 0.0
    if now >= sunset:
        return 1.0
    return (now - sunrise) / (sunset - sunrise)


# ── Visibility ───────────────────────────────────────────────────────────────

def visibility_note(vis_m: int) -> str:
    km = vis_m / 1000
    if km >= 20:
        return "Perfectly clear view."
    if km >= 10:
        return "Clear visibility."
    if km >= 5:
        return "Moderate visibility."
    if km >= 2:
        return "Low visibility."
    return "Very poor visibility."


# ── Feels-Like reasoning ────────────────────────────────────────────────────

def feels_like_reason(feels: float, actual: float, wind: float, hum: int) -> str:
    diff = feels - actual
    if abs(diff) < 1:
        return "Similar to the actual temperature."
    if diff < -2 and wind > 15:
        return "Wind is making it feel cooler."
    if diff < -1:
        return "Wind chill is lowering the perceived temperature."
    if diff > 2 and hum > 65:
        return "Humidity is making it feel warmer."
    if diff > 1:
        return "It feels warmer than the actual temperature."
    return "Close to the actual temperature."


# ── Dynamic condition summary ────────────────────────────────────────────────

def condition_summary(hourly: list, current: dict, tz_offset: int) -> str:
    """Scan the next 12 hours and generate a one-line forecast sentence."""
    cur_main = current["weather"][0]["main"]
    gust = current.get("wind_gust", current.get("wind_speed", 0))

    rain_keywords = {"Rain", "Drizzle", "Thunderstorm"}

    for h in hourly[:12]:
        h_main = h["weather"][0]["main"]
        h_time = time_from_unix(h["dt"], tz_offset)

        if h_main in rain_keywords and cur_main not in rain_keywords:
            s = f"Rainy conditions expected around {h_time}."
            if gust and gust > 20:
                s += f" Wind gusts up to {round(gust)} kph."
            return s
        if h_main == "Snow" and cur_main != "Snow":
            return f"Snow expected around {h_time}."
        if h_main == "Clear" and cur_main in rain_keywords:
            return f"Rain expected to clear around {h_time}."

    descs = {
        "Clear": "Clear skies expected throughout the day.",
        "Clouds": "Cloudy conditions expected to continue.",
        "Rain": "Rainy conditions throughout the day.",
        "Drizzle": "Light drizzle expected to continue.",
        "Thunderstorm": "Thunderstorm activity expected.",
        "Snow": "Snowy conditions expected to persist.",
        "Mist": "Misty conditions with reduced visibility.",
        "Fog": "Foggy conditions — drive carefully.",
        "Haze": "Hazy skies throughout the day.",
    }
    s = descs.get(cur_main, f"Current conditions: {cur_main}.")
    if gust and gust > 25:
        s += f" Wind gusts up to {round(gust)} kph."
    return s
