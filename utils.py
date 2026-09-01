"""
utils.py
Small, stateless helper functions used across the app.
Nothing here touches the network or Streamlit — pure functions only.
"""

from datetime import datetime


def format_date(iso_date: str, fmt: str = "%a, %b %d") -> str:
    """Turn '2026-09-01' into 'Tue, Sep 01'."""
    try:
        return datetime.strptime(iso_date, "%Y-%m-%d").strftime(fmt)
    except ValueError:
        return iso_date


def format_datetime(iso_datetime: str, fmt: str = "%I:%M %p") -> str:
    """Turn '2026-09-01T14:30' into '02:30 PM'."""
    try:
        return datetime.strptime(iso_datetime, "%Y-%m-%dT%H:%M").strftime(fmt)
    except ValueError:
        return iso_datetime


def celsius_to_fahrenheit(celsius: float) -> float:
    return (celsius * 9 / 5) + 32


def kmh_to_mph(kmh: float) -> float:
    return kmh * 0.621371


def validate_city_input(text: str) -> str:
    """
    Basic sanitation for user-entered city names: strips whitespace,
    blocks empty or absurdly long input.
    Raises ValueError if the input is unusable.
    """
    cleaned = text.strip()
    if not cleaned:
        raise ValueError("Please enter a city name.")
    if len(cleaned) > 100:
        raise ValueError("City name is too long.")
    return cleaned
