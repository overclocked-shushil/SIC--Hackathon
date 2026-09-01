"""
weather_processing.py
Turns raw Open-Meteo JSON into clean, ready-to-display Python objects.
No network calls happen here — this module is pure data transformation,
which makes it easy to unit test.
"""

from __future__ import annotations

from dataclasses import dataclass
from config import WEATHER_CODES


@dataclass
class CurrentWeather:
    temperature: float
    windspeed: float
    weathercode: int
    condition: str
    icon: str
    observed_at: str


@dataclass
class DailyForecast:
    date: str
    weathercode: int
    condition: str
    icon: str
    temp_max: float
    temp_min: float
    precipitation: float
    windspeed_max: float


def describe_weather_code(code: int) -> tuple[str, str]:
    """Map a WMO weather code to (description, emoji). Falls back gracefully."""
    return WEATHER_CODES.get(code, ("Unknown", "❓"))


def parse_current_weather(raw: dict) -> CurrentWeather:
    """Extract and clean the 'current_weather' block."""
    current = raw.get("current_weather", {})
    condition, icon = describe_weather_code(current.get("weathercode", -1))

    return CurrentWeather(
        temperature=current.get("temperature", 0.0),
        windspeed=current.get("windspeed", 0.0),
        weathercode=current.get("weathercode", -1),
        condition=condition,
        icon=icon,
        observed_at=current.get("time", ""),
    )


def parse_daily_forecast(raw: dict) -> list[DailyForecast]:
    """Extract the 'daily' block into a list of per-day forecast objects."""
    daily = raw.get("daily", {})
    dates = daily.get("time", [])

    forecasts = []
    for i, date in enumerate(dates):
        code = daily.get("weathercode", [])[i]
        condition, icon = describe_weather_code(code)

        forecasts.append(
            DailyForecast(
                date=date,
                weathercode=code,
                condition=condition,
                icon=icon,
                temp_max=daily.get("temperature_2m_max", [])[i],
                temp_min=daily.get("temperature_2m_min", [])[i],
                precipitation=daily.get("precipitation_sum", [])[i],
                windspeed_max=daily.get("windspeed_10m_max", [])[i],
            )
        )

    return forecasts


def calculate_average_temp(forecasts: list[DailyForecast]) -> float:
    """Example aggregate: average of daily max temps across the forecast window."""
    if not forecasts:
        return 0.0
    return sum(f.temp_max for f in forecasts) / len(forecasts)


def find_hottest_day(forecasts: list[DailyForecast]) -> DailyForecast | None:
    """Return the forecast day with the highest max temperature."""
    if not forecasts:
        return None
    return max(forecasts, key=lambda f: f.temp_max)
