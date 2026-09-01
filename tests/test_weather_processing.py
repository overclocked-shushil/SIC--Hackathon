# tests/test_weather_processing.py

from weather_processing import parse_current_weather, calculate_average_temp, DailyForecast


def test_parse_current_weather():
    raw = {
        "current_weather": {
            "temperature": 28.5,
            "windspeed": 12.0,
            "weathercode": 1,
            "time": "2026-09-01T14:00",
        }
    }
    result = parse_current_weather(raw)
    assert result.temperature == 28.5
    assert result.condition == "Mainly clear"


def test_calculate_average_temp():
    forecasts = [
        DailyForecast("2026-09-01", 1, "Mainly clear", "🌤️", 30, 20, 0, 10),
        DailyForecast("2026-09-02", 1, "Mainly clear", "🌤️", 32, 22, 0, 10),
    ]
    assert calculate_average_temp(forecasts) == 31.0
