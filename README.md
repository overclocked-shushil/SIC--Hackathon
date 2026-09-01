# ⛅ Weather Dashboard — Apple-Style

A real-time weather dashboard built with **Streamlit** that visually replicates the **macOS Weather app**. Powered by the **OpenWeatherMap One Call API 3.0** — featuring glassmorphism UI, dynamic backgrounds, geolocation, AQI, wind compass, moon phase, and 13 live weather cards.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![API](https://img.shields.io/badge/API-OpenWeatherMap-orange)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **City Search** | Search any city worldwide with live forward geocoding |
| 📍 **Auto Location** | Detects location via IP on first load, with manual GPS override |
| 🌡️ **Current Weather** | Temperature, wind speed, condition — all real-time |
| 📅 **10-Day Forecast** | Daily high/low with gradient temperature bars, expandable details |
| ⏱ **Hourly Strip** | Scrollable 16-hour forecast with icons & precipitation % |
| 🌫 **Air Quality** | PM2.5-based AQI with gradient bar and category label |
| 💨 **Wind Compass** | SVG compass dial showing speed, gusts & direction |
| 🗺 **Live Map** | Dark-themed Folium map centered on current location |
| ☀️ **UV Index** | Value, category, gradient bar, "safe until" sunset time |
| 🌅 **Sunset/Sunrise** | Actual times with animated sun-arc position diagram |
| 🌡 **Feels Like** | With dynamic reasoning (wind chill, humidity, etc.) |
| 🌧 **Precipitation** | Today's mm + tomorrow's forecast |
| 🌙 **Moon Phase** | Name, illumination %, moonrise, days to full moon |
| 💧 **Humidity** | Current % with dew point |
| 👁 **Visibility** | Distance in km with quality description |
| ⏱ **Pressure** | hPa on an SVG gauge dial |
| 📊 **Averages** | Today vs weekly average high comparison |
| 🎨 **Dynamic Background** | Gradient changes based on weather condition + day/night |
| 🌡↔️ **°C / °F Toggle** | Reformats every temperature on the page instantly |
| ⚡ **Caching** | 10-minute TTL on weather, 1-hour TTL on geocoding |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                       │
│                         app.py                               │
│    Streamlit UI, layout, 13 weather cards, sidebar,          │
│    session state management, geolocation flow                │
└────────────┬─────────────────┬────────────────┬──────────────┘
             │                 │                │
             ▼                 ▼                ▼
  ┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
  │    API LAYER     │ │ STYLES LAYER │ │  UTILITY LAYER   │
  │     api.py       │ │  styles.py   │ │    utils.py      │
  │                  │ │              │ │                  │
  │ • One Call 3.0   │ │ • Base CSS   │ │ • Temp format    │
  │ • Air Pollution  │ │ • Dynamic BG │ │ • Time format    │
  │ • Geocoding      │ │ • Card HTML  │ │ • AQI compute    │
  │ • IP fallback    │ │ • SVG gens   │ │ • Moon phase     │
  └──────────────────┘ └──────────────┘ │ • Wind direction │
                                        │ • Condition text │
                                        └──────────────────┘
```

### Design Principles

- **No business logic in the UI** — `app.py` only handles layout and rendering
- **No network calls in processing** — `utils.py` is pure data transformation
- **No side effects in utilities** — all functions are stateless and testable
- **Single source of truth** — `st.session_state["location"]` drives the entire dashboard

---

## 📁 Project Structure

```
weather-dashboard/
├── app.py                  # Streamlit entry point — layout & 13 cards
├── api.py                  # All OpenWeatherMap API calls (cached)
├── styles.py               # Glassmorphism CSS, dynamic backgrounds, SVG helpers
├── utils.py                # Pure helpers: formatting, AQI, moon phase, etc.
├── requirements.txt        # Python dependencies
├── .streamlit/
│   └── secrets.toml        # API key (gitignored — never committed)
├── .gitignore              # Secrets, venv, caches excluded
└── README.md               # This file
```

---

## 🚀 Getting Started

### 1. Get an API Key

1. Sign up at [openweathermap.org](https://openweathermap.org/api)
2. Subscribe to **"One Call API 3.0"** (free tier: 1,000 calls/day)
3. Copy your API key

### 2. Install & Configure

```bash
# Clone the repo
git clone https://github.com/<your-username>/weather-dashboard.git
cd weather-dashboard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Add your API key
echo 'OPENWEATHER_API_KEY = "your_actual_key_here"' > .streamlit/secrets.toml
```

### 3. Run

```bash
streamlit run app.py
```

Opens at `http://localhost:8501` 🚀

---

## 🔄 Data Flow

```
User searches "Tokyo"
        │
        ▼
  forward_geocode("Tokyo")  →  lat: 35.68, lon: 139.69
        │
        ├── get_onecall(35.68, 139.69, "metric")
        │       → current + hourly (48h) + daily (8d) + alerts
        │
        └── get_air_quality(35.68, 139.69)
                → AQI, PM2.5, pollutant components
        │
        ▼
  utils.py parses → condition_summary, moon_phase, AQI score, etc.
  styles.py selects → dynamic background CSS, card HTML, SVGs
        │
        ▼
  app.py renders 13 cards + header + hourly strip + map
```

---

## ⚙️ Configuration

| Setting | Location | Default |
|---|---|---|
| API Key | `.streamlit/secrets.toml` | *(required)* |
| Default City | `app.py` → `_DEFAULT` | Bengaluru |
| Temperature Unit | Sidebar toggle | °C (metric) |
| Cache TTL | `api.py` → `@st.cache_data` | 600s weather, 3600s geocoding |

---

## 🛠️ Tech Stack

| Technology | Role |
|---|---|
| [Streamlit](https://streamlit.io/) | Web framework |
| [OpenWeatherMap](https://openweathermap.org/) | Weather, AQI & geocoding APIs |
| [Folium](https://python-visualization.github.io/folium/) | Interactive map |
| [streamlit-folium](https://github.com/randyzwitch/streamlit-folium) | Folium integration |
| [Requests](https://docs.python-requests.org/) | HTTP client |
| Custom CSS | Glassmorphism + dynamic backgrounds |
| Custom SVG | Wind compass, sun arc, pressure gauge |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m "Add my feature"`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

Open source under the [MIT License](LICENSE).

---

<p align="center">
  Built with ❤️ for the SIC Hackathon Team — Dew Point
</p>
