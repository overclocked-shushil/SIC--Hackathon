# ⛅ Weather Dashboard

A real-time weather dashboard built with **Streamlit** and the **Open-Meteo API**. Search any city in the world and get current conditions plus a 5-day forecast — no API key required.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![API](https://img.shields.io/badge/API-Open--Meteo-blue)

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture Overview](#-architecture-overview)
- [Project Structure](#-project-structure)
- [Data Flow](#-data-flow)
- [Module Deep Dive](#-module-deep-dive)
- [Getting Started](#-getting-started)
- [Running Tests](#-running-tests)
- [Configuration](#-configuration)
- [Tech Stack](#-tech-stack)
- [Contributing](#-contributing)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **City Search** | Search any city worldwide with live geocoding |
| 🌡️ **Current Weather** | Temperature, wind speed, and weather condition at a glance |
| 📅 **5-Day Forecast** | Daily high/low temperatures with weather icons |
| 📈 **Interactive Charts** | Line chart of forecast highs and lows |
| 📊 **Derived Stats** | Average forecast high + hottest upcoming day |
| ⚡ **Caching** | 10-minute TTL cache to avoid redundant API calls |
| 🌍 **No API Key** | Powered by Open-Meteo — completely free and open |

---

## 🏗️ Architecture Overview

The project follows a **layered architecture** with clear separation of concerns. Each module has a single responsibility and communicates through well-defined interfaces.

```
┌─────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER                │
│                      app.py                         │
│          (Streamlit UI, layout, user input)          │
└───────────┬──────────────────────┬──────────────────┘
            │                      │
            ▼                      ▼
┌───────────────────┐  ┌───────────────────────────────┐
│   API LAYER       │  │   PROCESSING LAYER            │
│  weather_api.py   │  │  weather_processing.py        │
│  (HTTP, geocoding │  │  (Parsing, data transformation │
│   raw JSON fetch) │  │   dataclasses, aggregations)   │
└───────────────────┘  └───────────────────────────────┘
            │                      │
            ▼                      ▼
┌───────────────────┐  ┌───────────────────────────────┐
│   CONFIG LAYER    │  │   UTILITY LAYER               │
│    config.py      │  │     utils.py                  │
│  (URLs, defaults, │  │  (date formatting, input       │
│   WMO codes)      │  │   validation, conversions)     │
└───────────────────┘  └───────────────────────────────┘
```

### Design Principles

- **No business logic in the UI** — `app.py` only handles layout and user interaction
- **No network calls in processing** — `weather_processing.py` is pure data transformation
- **No side effects in utilities** — `utils.py` contains only pure, stateless functions
- **Single responsibility** — each file has one job and one reason to change

---

## 📁 Project Structure

```
weather-dashboard/
│
├── app.py                     # Streamlit UI entry point
├── weather_api.py             # API communication layer (HTTP + geocoding)
├── weather_processing.py      # Data parsing & transformation (dataclasses)
├── config.py                  # Centralized configuration & WMO weather codes
├── utils.py                   # Pure helper functions (formatting, validation)
├── requirements.txt           # Python dependencies
│
├── tests/                     # Unit test suite
│   ├── __init__.py
│   ├── test_utils.py          # Tests for utils.py
│   └── test_weather_processing.py  # Tests for weather_processing.py
│
├── .gitignore                 # Git ignore rules (secrets, venv, caches)
└── README.md                  # This file
```

---

## 🔄 Data Flow

Here's the complete journey of a weather request — from user input to rendered dashboard:

```
 ┌──────────┐    1. Enter city     ┌──────────────┐
 │   User   │ ──────────────────►  │   app.py     │
 └──────────┘                      │  (Streamlit)  │
                                   └──────┬───────┘
                                          │
                          2. validate_city_input()
                                          │
                                          ▼
                                   ┌──────────────┐
                                   │   utils.py   │  ──► Sanitize & validate
                                   └──────┬───────┘
                                          │
                          3. fetch_weather_for_city()
                                          │
                                          ▼
                                   ┌──────────────┐
                                   │weather_api.py│
                                   └──────┬───────┘
                                          │
                     ┌────────────────────┤
                     │                    │
          4a. geocode_city()    4b. get_weather_data()
                     │                    │
                     ▼                    ▼
           ┌─────────────────┐  ┌─────────────────┐
           │ Geocoding API   │  │  Forecast API   │
           │(lat/lng lookup) │  │ (weather JSON)  │
           └─────────────────┘  └─────────────────┘
                     │                    │
                     └────────┬───────────┘
                              │
               5. Raw JSON returned to app.py
                              │
                              ▼
                    ┌──────────────────────┐
                    │weather_processing.py │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
    6a. parse_current    6b. parse_daily   6c. calculate_
        _weather()          _forecast()       average_temp()
              │                │            find_hottest_day()
              ▼                ▼                │
        CurrentWeather   [DailyForecast]        ▼
         dataclass        dataclass list    Derived stats
              │                │                │
              └────────────────┼────────────────┘
                               │
                7. Render to Streamlit UI
                               │
                               ▼
                    ┌──────────────────┐
                    │  Dashboard View  │
                    │  • Metrics row   │
                    │  • Line chart    │
                    │  • Forecast cards│
                    │  • Stats summary │
                    └──────────────────┘
```

### Step-by-Step Breakdown

| Step | Action | Module | Details |
|------|--------|--------|---------|
| 1 | User enters a city name in the sidebar | `app.py` | Streamlit text input with default city from config |
| 2 | Input is sanitized and validated | `utils.py` | Strips whitespace, rejects empty / too-long input |
| 3 | Orchestrates the full fetch pipeline | `weather_api.py` | `fetch_weather_for_city()` is the convenience entry point |
| 4a | City name → latitude/longitude | `weather_api.py` | Calls Open-Meteo Geocoding API |
| 4b | Coordinates → raw weather JSON | `weather_api.py` | Calls Open-Meteo Forecast API |
| 5 | Raw JSON returned to the UI layer | `app.py` | JSON includes current weather + daily forecasts |
| 6a | Parse current conditions | `weather_processing.py` | Returns a `CurrentWeather` dataclass |
| 6b | Parse daily forecast | `weather_processing.py` | Returns a list of `DailyForecast` dataclasses |
| 6c | Compute derived statistics | `weather_processing.py` | Average temp + hottest day from forecast list |
| 7 | Render everything on screen | `app.py` | Metrics, chart, cards, and stats via Streamlit widgets |

---

## 🔍 Module Deep Dive

### `app.py` — Presentation Layer

The Streamlit entry point. Handles only **UI layout and user interaction**.

| Responsibility | Implementation |
|---|---|
| Page config | Title, icon, wide layout |
| Sidebar search | Text input + button, session state management |
| Caching | `@st.cache_data(ttl=600)` — 10-minute TTL |
| Current weather display | 3-column metric row (temp, wind, condition) |
| Forecast chart | Pandas DataFrame → `st.line_chart()` |
| Forecast cards | Dynamic columns with icon, temps, condition |
| Error handling | Catches `ValueError` and `WeatherAPIError`, shows `st.error()` |

### `weather_api.py` — API Layer

Handles **all HTTP communication** with the Open-Meteo API. This module only fetches raw data — it does not interpret or transform it.

| Function | Purpose | Returns |
|---|---|---|
| `geocode_city(city_name)` | Convert city name → lat/lng | `dict` (location metadata) |
| `get_weather_data(lat, lng)` | Fetch current + forecast weather | `dict` (raw API JSON) |
| `fetch_weather_for_city(city)` | Convenience wrapper for both | `tuple[dict, dict]` |

**Custom Exception:** `WeatherAPIError` — raised on network failures or missing results.

### `weather_processing.py` — Processing Layer

**Pure data transformation** — no network calls, no side effects. Easy to unit test.

| Component | Type | Fields |
|---|---|---|
| `CurrentWeather` | dataclass | `temperature`, `windspeed`, `weathercode`, `condition`, `icon`, `observed_at` |
| `DailyForecast` | dataclass | `date`, `weathercode`, `condition`, `icon`, `temp_max`, `temp_min`, `precipitation`, `windspeed_max` |

| Function | Purpose |
|---|---|
| `describe_weather_code(code)` | WMO code → `(description, emoji)` with fallback |
| `parse_current_weather(raw)` | Raw JSON → `CurrentWeather` |
| `parse_daily_forecast(raw)` | Raw JSON → `list[DailyForecast]` |
| `calculate_average_temp(forecasts)` | Average of daily max temps |
| `find_hottest_day(forecasts)` | Day with highest max temperature |

### `config.py` — Configuration Layer

Centralized, single-source-of-truth for all settings.

| Setting | Default | Notes |
|---|---|---|
| `GEOCODING_URL` | `https://geocoding-api.open-meteo.com/v1/search` | Open-Meteo geocoding |
| `FORECAST_URL` | `https://api.open-meteo.com/v1/forecast` | Open-Meteo weather |
| `REQUEST_TIMEOUT` | `10` seconds | HTTP request timeout |
| `DEFAULT_CITY` | `Bengaluru` | Pre-filled city on launch |
| `DEFAULT_FORECAST_DAYS` | `5` | Number of forecast days |
| `TEMPERATURE_UNIT` | `celsius` | Options: `celsius`, `fahrenheit` |
| `WIND_SPEED_UNIT` | `kmh` | Options: `kmh`, `ms`, `mph`, `kn` |
| `WEATHER_CODES` | 20+ entries | WMO code → (description, emoji) mapping |

### `utils.py` — Utility Layer

Pure, stateless helper functions. No network calls, no Streamlit dependency.

| Function | Purpose | Example |
|---|---|---|
| `format_date(iso)` | `"2026-09-01"` → `"Tue, Sep 01"` | Display-friendly dates |
| `format_datetime(iso)` | `"2026-09-01T14:30"` → `"02:30 PM"` | Display-friendly times |
| `celsius_to_fahrenheit(c)` | Unit conversion | `0°C → 32°F` |
| `kmh_to_mph(kmh)` | Unit conversion | `100 km/h → 62.14 mph` |
| `validate_city_input(text)` | Strip, reject empty/long | Raises `ValueError` on bad input |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **pip** (Python package manager)
- Internet connection (to reach the Open-Meteo API)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/weather-dashboard.git
cd weather-dashboard

# 2. Create a virtual environment
python -m venv venv

# 3. Activate it
# macOS / Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt
```

### Run the App

```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`.

---

## 🧪 Running Tests

```bash
# Run the full test suite
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=. --cov-report=term-missing
```

### Test Coverage

| Test File | Module Under Test | What's Tested |
|---|---|---|
| `test_utils.py` | `utils.py` | Input validation (whitespace stripping, empty rejection), unit conversion |
| `test_weather_processing.py` | `weather_processing.py` | Current weather parsing, average temperature calculation |

---

## ⚙️ Configuration

All settings live in [`config.py`](config.py). No environment variables or API keys are needed.

To customize:

```python
# config.py

DEFAULT_CITY = "London"              # Change the default city
TEMPERATURE_UNIT = "fahrenheit"      # Switch to Fahrenheit
WIND_SPEED_UNIT = "mph"              # Switch to miles per hour
DEFAULT_FORECAST_DAYS = 7            # Extend forecast range
REQUEST_TIMEOUT = 15                 # Increase timeout for slow connections
```

---

## 🛠️ Tech Stack

| Technology | Role |
|---|---|
| [Streamlit](https://streamlit.io/) | Web framework for the interactive dashboard UI |
| [Open-Meteo API](https://open-meteo.com/) | Free, open-source weather + geocoding API |
| [Requests](https://docs.python-requests.org/) | HTTP client for API communication |
| [Pandas](https://pandas.pydata.org/) | DataFrame construction for chart data |
| [Pytest](https://docs.pytest.org/) | Unit testing framework |
| [Python Dataclasses](https://docs.python.org/3/library/dataclasses.html) | Structured data objects for weather models |

---

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/my-feature`
3. **Commit** your changes: `git commit -m "Add my feature"`
4. **Push** to the branch: `git push origin feature/my-feature`
5. **Open** a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">
  Built with ❤️ for the SIC Hackathon
</p>
