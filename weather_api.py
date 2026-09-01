"""
weather_api.py
Handles all HTTP communication with the Open-Meteo API.
This module ONLY fetches raw data — it does not interpret or transform it.
"""

from __future__ import annotations

import requests

from config import (
    GEOCODING_URL,
    FORECAST_URL,
    REQUEST_TIMEOUT,
    TEMPERATURE_UNIT,
    WIND_SPEED_UNIT,
)


class WeatherAPIError(Exception):
    """Raised when the weather API can't be reached or returns bad data."""
    pass


def geocode_city(city_name: str) -> dict:
    """
    Convert a city name into latitude/longitude + metadata.
    Returns the first matching location.
    Raises WeatherAPIError if the city can't be found or the request fails.
    """
    params = {"name": city_name, "count": 1, "language": "en", "format": "json"}

    try:
        response = requests.get(GEOCODING_URL, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise WeatherAPIError(f"Could not reach geocoding service: {e}")

    data = response.json()
    results = data.get("results")
    if not results:
        raise WeatherAPIError(f"No location found for '{city_name}'.")

    return results[0]


def get_weather_data(latitude: float, longitude: float) -> dict:
    """
    Fetch current weather + hourly + daily forecast for a coordinate pair.
    Returns raw JSON from Open-Meteo.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": True,
        "hourly": "temperature_2m,relative_humidity_2m,weathercode",
        "daily": "weathercode,temperature_2m_max,temperature_2m_min,"
                 "precipitation_sum,windspeed_10m_max",
        "temperature_unit": TEMPERATURE_UNIT,
        "windspeed_unit": WIND_SPEED_UNIT,
        "timezone": "auto",
    }

    try:
        response = requests.get(FORECAST_URL, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise WeatherAPIError(f"Could not reach weather service: {e}")

    return response.json()


def fetch_weather_for_city(city_name: str) -> tuple[dict, dict]:
    """
    Convenience function: geocode a city, then fetch its weather.
    Returns (location_info, raw_weather_json).
    """
    location = geocode_city(city_name)
    weather = get_weather_data(location["latitude"], location["longitude"])
    return location, weather
