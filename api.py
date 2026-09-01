"""
api.py
All HTTP communication with OpenWeatherMap + fallback services.

Strategy:  Try One Call 3.0 first (paid).  If it fails (401/402/timeout),
fall back to the FREE Weather 2.5 + 5-day Forecast APIs and transform
the response into the same structure app.py expects.
"""

from __future__ import annotations

import math
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from typing import Optional

import requests
import streamlit as st

# ── Endpoints ────────────────────────────────────────────────────────────────
_ONECALL  = "https://api.openweathermap.org/data/3.0/onecall"
_WEATHER  = "https://api.openweathermap.org/data/2.5/weather"
_FORECAST = "https://api.openweathermap.org/data/2.5/forecast"
_AIR      = "http://api.openweathermap.org/data/2.5/air_pollution"
_GEO      = "http://api.openweathermap.org/geo/1.0/direct"
_RGEO     = "http://api.openweathermap.org/geo/1.0/reverse"
_TIMEOUT  = 10


def _key() -> str:
    return "75d415ed1557fe2dabcb9b74c96a64c2"


# ══════════════════════════════════════════════════════════════════════════════
# PUBLIC — unified weather (what app.py calls)
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=600)
def get_onecall(lat: float, lon: float, units: str = "metric") -> Optional[dict]:
    """Return weather data in One-Call-compatible format.

    • Tries One Call 3.0 first (needs paid subscription).
    • Falls back to the free Weather 2.5 + 5-day-forecast APIs and
      transforms the data to match the same schema.
    """
    # ── Attempt One Call 3.0 ─────────────────────────────────────────────
    try:
        r = requests.get(_ONECALL, params={
            "lat": lat, "lon": lon,
            "appid": _key(), "units": units, "exclude": "minutely",
        }, timeout=_TIMEOUT)
        if r.status_code == 200:
            data = r.json()
            # Convert wind m/s → km/h for metric
            if units == "metric":
                _convert_wind(data)
            return data
    except requests.RequestException:
        pass

    # ── Fallback: free 2.5 APIs ──────────────────────────────────────────
    return _fetch_free(lat, lon, units)


# ══════════════════════════════════════════════════════════════════════════════
# FREE-API FETCHERS
# ══════════════════════════════════════════════════════════════════════════════

def _fetch_free(lat: float, lon: float, units: str) -> Optional[dict]:
    """Combine Weather 2.5 + 5-day forecast into One-Call shape."""
    cur_raw = _get_current(lat, lon, units)
    if not cur_raw:
        return None
    fc_raw = _get_forecast(lat, lon, units)
    return _transform(cur_raw, fc_raw, lat, units)


def _get_current(lat: float, lon: float, units: str) -> Optional[dict]:
    try:
        r = requests.get(_WEATHER, params={
            "lat": lat, "lon": lon, "appid": _key(), "units": units,
        }, timeout=_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.RequestException:
        return None


def _get_forecast(lat: float, lon: float, units: str) -> Optional[dict]:
    try:
        r = requests.get(_FORECAST, params={
            "lat": lat, "lon": lon, "appid": _key(), "units": units,
        }, timeout=_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.RequestException:
        return None


# ══════════════════════════════════════════════════════════════════════════════
# TRANSFORM free-API responses → One Call shape
# ══════════════════════════════════════════════════════════════════════════════

def _ms_to_display(speed: float, units: str) -> float:
    """Convert API wind speed to display units (km/h or mph)."""
    if units == "metric":
        return round(speed * 3.6, 1)      # m/s → km/h
    return round(speed, 1)                 # imperial already mph


def _transform(cur: dict, fc: Optional[dict], lat: float, units: str) -> dict:
    main  = cur.get("main", {})
    wind  = cur.get("wind", {})
    sys   = cur.get("sys", {})
    tz    = cur.get("timezone", 0)
    clouds = cur.get("clouds", {}).get("all", 0)
    temp  = main.get("temp", 20)
    hum   = main.get("humidity", 50)
    now_dt = datetime.fromtimestamp(cur.get("dt", 0),
                                    tz=timezone(timedelta(seconds=tz)))

    cur_block = {
        "dt":         cur.get("dt", 0),
        "temp":       temp,
        "feels_like": main.get("feels_like", temp),
        "pressure":   main.get("pressure", 1013),
        "humidity":   hum,
        "dew_point":  _dew_point(temp, hum),
        "uvi":        _est_uvi(lat, clouds, now_dt.hour),
        "clouds":     clouds,
        "visibility": cur.get("visibility", 10000),
        "wind_speed": _ms_to_display(wind.get("speed", 0), units),
        "wind_deg":   wind.get("deg", 0),
        "wind_gust":  _ms_to_display(wind.get("gust", wind.get("speed", 0)), units),
        "weather":    cur.get("weather",
                              [{"id": 800, "main": "Clear",
                                "description": "clear sky", "icon": "01d"}]),
    }

    # ── Hourly (from 3-hour buckets) ─────────────────────────────────────
    hourly = []
    for e in (fc or {}).get("list", []):
        em = e.get("main", {})
        hourly.append({
            "dt":         e.get("dt", 0),
            "temp":       em.get("temp", 0),
            "feels_like": em.get("feels_like", 0),
            "pressure":   em.get("pressure", 1013),
            "humidity":   em.get("humidity", 0),
            "wind_speed": _ms_to_display(e.get("wind", {}).get("speed", 0), units),
            "wind_deg":   e.get("wind", {}).get("deg", 0),
            "weather":    e.get("weather", []),
            "pop":        e.get("pop", 0),
        })

    # ── Daily (aggregate 3-h buckets by calendar day) ────────────────────
    daily = _agg_daily(fc, tz, sys, units)

    return {
        "current":         cur_block,
        "hourly":          hourly,
        "daily":           daily,
        "timezone_offset": tz,
    }


def _agg_daily(fc: Optional[dict], tz: int, sys: dict, units: str) -> list:
    if not fc:
        return []

    city    = fc.get("city", {})
    sunrise = city.get("sunrise", sys.get("sunrise", 0))
    sunset  = city.get("sunset",  sys.get("sunset",  0))

    by_date: dict[str, list] = defaultdict(list)
    for e in fc.get("list", []):
        dt = datetime.fromtimestamp(e["dt"],
                                    tz=timezone(timedelta(seconds=tz)))
        by_date[dt.strftime("%Y-%m-%d")].append(e)

    daily = []
    for ds in sorted(by_date):
        grp   = by_date[ds]
        temps = [e["main"]["temp"] for e in grp]
        hums  = [e["main"]["humidity"] for e in grp]
        winds = [e["wind"]["speed"] for e in grp]
        pops  = [e.get("pop", 0) for e in grp]
        rain  = sum(
            (e.get("rain", {}).get("3h", 0)
             if isinstance(e.get("rain"), dict) else 0)
            for e in grp
        )
        mid = grp[len(grp) // 2]
        dt_obj = datetime.strptime(ds, "%Y-%m-%d").replace(
            tzinfo=timezone.utc)

        daily.append({
            "dt":         grp[0]["dt"],
            "sunrise":    sunrise,
            "sunset":     sunset,
            "moonrise":   0,
            "moon_phase": _moon_phase(int(dt_obj.timestamp())),
            "temp":       {"min": min(temps), "max": max(temps)},
            "humidity":   round(sum(hums) / len(hums)),
            "wind_speed": _ms_to_display(max(winds), units),
            "pop":        max(pops),
            "rain":       round(rain, 1),
            "weather":    mid.get("weather", []),
        })
    return daily


# ══════════════════════════════════════════════════════════════════════════════
# ONE CALL 3.0 — post-processing helpers
# ══════════════════════════════════════════════════════════════════════════════

def _convert_wind(data: dict):
    """In-place: m/s → km/h for metric One Call 3.0 responses."""
    def _w(d: dict):
        for k in ("wind_speed", "wind_gust"):
            if k in d:
                d[k] = round(d[k] * 3.6, 1)
    _w(data.get("current", {}))
    for h in data.get("hourly", []):
        _w(h)
    for d in data.get("daily", []):
        _w(d)


# ══════════════════════════════════════════════════════════════════════════════
# COMPUTATION HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _dew_point(t: float, rh: int) -> float:
    a, b = 17.27, 237.7
    alpha = (a * t / (b + t)) + math.log(max(rh, 1) / 100.0)
    return round((b * alpha) / (a - alpha), 1)


def _est_uvi(lat: float, cloud_pct: int, hour: int) -> float:
    """Rough UV estimate from latitude, clouds, time-of-day."""
    base  = max(0.0, 12 - abs(lat) / 7)
    solar = max(0.0, math.cos(math.radians((hour - 12) * 15)))
    cloud = 1 - (cloud_pct / 100) * 0.75
    return round(max(0, base * solar * cloud), 1)


def _moon_phase(ts: int) -> float:
    """Approximate lunar phase (0-1) from unix timestamp."""
    ref   = 947182440          # 2000-01-06 18:14 UTC (new moon)
    cycle = 29.53058867 * 86400
    p = ((ts - ref) / cycle) % 1.0
    return round(p if p >= 0 else p + 1.0, 2)


# ══════════════════════════════════════════════════════════════════════════════
# AIR QUALITY  (free endpoint — works with any key)
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=600)
def get_air_quality(lat: float, lon: float) -> Optional[dict]:
    try:
        r = requests.get(_AIR, params={
            "lat": lat, "lon": lon, "appid": _key(),
        }, timeout=_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        return data["list"][0] if data.get("list") else None
    except (requests.RequestException, KeyError, IndexError):
        return None


# ══════════════════════════════════════════════════════════════════════════════
# GEOCODING  (free endpoint)
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600)
def forward_geocode(city: str) -> Optional[dict]:
    try:
        r = requests.get(_GEO, params={
            "q": city, "limit": 1, "appid": _key(),
        }, timeout=_TIMEOUT)
        r.raise_for_status()
        hits = r.json()
        if not hits:
            return None
        h = hits[0]
        return dict(name=h.get("name", city), lat=h["lat"], lon=h["lon"],
                    country=h.get("country", ""), state=h.get("state", ""))
    except (requests.RequestException, KeyError):
        return None


@st.cache_data(ttl=3600)
def reverse_geocode(lat: float, lon: float) -> Optional[dict]:
    try:
        r = requests.get(_RGEO, params={
            "lat": lat, "lon": lon, "limit": 1, "appid": _key(),
        }, timeout=_TIMEOUT)
        r.raise_for_status()
        hits = r.json()
        if not hits:
            return None
        h = hits[0]
        return dict(name=h.get("name", "Unknown"), lat=h["lat"], lon=h["lon"],
                    country=h.get("country", ""), state=h.get("state", ""))
    except (requests.RequestException, KeyError):
        return None


# ══════════════════════════════════════════════════════════════════════════════
# IP-BASED FALLBACK  (no key needed)
# ══════════════════════════════════════════════════════════════════════════════

def get_ip_location() -> Optional[dict]:
    try:
        r = requests.get("https://ipapi.co/json/", timeout=_TIMEOUT)
        r.raise_for_status()
        d = r.json()
        if d.get("latitude") and d.get("longitude"):
            return dict(name=d.get("city", "Unknown"), lat=d["latitude"],
                        lon=d["longitude"], country=d.get("country_name", ""))
        return None
    except (requests.RequestException, KeyError):
        return None
