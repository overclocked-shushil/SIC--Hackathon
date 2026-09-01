"""
app.py
The Streamlit UI styled after macOS / iOS Weather Dashboard.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from weather_api import fetch_weather_for_city, WeatherAPIError
from weather_processing import (
    parse_current_weather,
    parse_daily_forecast,
    calculate_average_temp,
    find_hottest_day,
)
from utils import format_date, format_datetime, validate_city_input
from config import DEFAULT_CITY

st.set_page_config(
    page_title="Weather Dashboard",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def apply_custom_styles():
    """Injects custom CSS to replicate the macOS translucency glassmorphic UI."""
    st.markdown(
        """
        <style>
        /* Main background - Sky Gradient */
        .stApp {
            background: linear-gradient(180deg, #1e3c72 0%, #2a5298 50%, #3b62a4 100%);
            color: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background: rgba(15, 25, 50, 0.45) !important;
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }

        /* Glass Cards Container */
        .glass-card {
            background: rgba(255, 255, 255, 0.12);
            backdrop-filter: blur(25px);
            -webkit-backdrop-filter: blur(25px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.18);
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        }

        /* Hero Temperature Readout */
        .hero-container {
            text-align: center;
            padding: 20px 0;
        }
        .hero-city {
            font-size: 2.2rem;
            font-weight: 600;
            letter-spacing: -0.5px;
            margin-bottom: 0px;
        }
        .hero-temp {
            font-size: 5.5rem;
            font-weight: 200;
            line-height: 1;
            margin: 5px 0;
        }
        .hero-condition {
            font-size: 1.2rem;
            font-weight: 400;
            opacity: 0.9;
        }
        .hero-highlow {
            font-size: 0.95rem;
            opacity: 0.75;
            margin-top: 4px;
        }

        /* Subheadings inside glass cards */
        .card-header {
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            opacity: 0.6;
            margin-bottom: 12px;
            font-weight: 600;
        }

        /* Weather Metric Grid */
        .metric-value {
            font-size: 1.8rem;
            font-weight: 600;
        }
        .metric-label {
            font-size: 0.85rem;
            opacity: 0.7;
        }

        /* Hide Streamlit default headers/footers */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(ttl=600)
def get_weather(city: str):
    return fetch_weather_for_city(city)


def create_forecast_chart(forecast):
    """Creates a transparent Plotly temperature range chart."""
    dates = [format_date(f.date) for f in forecast]
    highs = [f.temp_max for f in forecast]
    lows = [f.temp_min for f in forecast]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=dates,
            y=highs,
            name="High",
            mode="lines+markers",
            line=dict(color="#FFB347", width=3),
            marker=dict(size=6),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=lows,
            name="Low",
            mode="lines+markers",
            line=dict(color="#70A1FF", width=3),
            marker=dict(size=6),
        )
    )

    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        height=180,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=False,
            tickfont=dict(color="rgba(255,255,255,0.8)"),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.1)",
            zeroline=False,
            showline=False,
            tickfont=dict(color="rgba(255,255,255,0.6)"),
        ),
    )

    return fig


def main():
    apply_custom_styles()

    with st.sidebar:
        st.markdown("### 🔍 Search Location")
        city_input = st.text_input("City name", value=DEFAULT_CITY, label_visibility="collapsed")
        search = st.button("Get Weather", use_container_width=True)
        if search:
            st.session_state["last_city"] = city_input

    city_to_use = st.session_state.get("last_city", DEFAULT_CITY)

    try:
        city_to_use = validate_city_input(city_to_use)
        with st.spinner("Fetching weather..."):
            location, raw_weather = get_weather(city_to_use)
    except ValueError as e:
        st.error(str(e))
        return
    except WeatherAPIError as e:
        st.error(f"⚠️ {e}")
        return

    current = parse_current_weather(raw_weather)
    forecast = parse_daily_forecast(raw_weather)

    # Calculate High/Low bounds for today
    today_high = forecast[0].temp_max if forecast else current.temperature
    today_low = forecast[0].temp_min if forecast else current.temperature

    # --- HERO SECTION ---
    st.markdown(
        f"""
        <div class="hero-container">
            <div class="hero-city">📍 {location.get('name')}, {location.get('country', '')}</div>
            <div class="hero-temp">{current.temperature}°</div>
            <div class="hero-condition">{current.icon} {current.condition}</div>
            <div class="hero-highlow">H: {today_high}° &nbsp;|&nbsp; L: {today_low}°</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- MAIN GLASS PANEL DASHBOARD ---
    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        # 5-Day Forecast Card
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">📅 5-DAY FORECAST</div>', unsafe_allow_html=True)

        if forecast:
            for day in forecast:
                c1, c2, c3, c4 = st.columns([2, 1, 2, 2])
                with c1:
                    st.write(f"**{format_date(day.date)}**")
                with c2:
                    st.write(day.icon)
                with c3:
                    st.caption(day.condition)
                with c4:
                    st.write(f"**{day.temp_max}°** / {day.temp_min}°")
        st.markdown("</div>", unsafe_allow_html=True)

        # Temperature Trend Chart Card
        if forecast:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">📈 TEMPERATURE TREND</div>', unsafe_allow_html=True)
            st.plotly_chart(create_forecast_chart(forecast), use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        # Current Metrics Grid
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">💨 CURRENT CONDITIONS</div>', unsafe_allow_html=True)

        m1, m2 = st.columns(2)
        with m1:
            st.markdown(
                f"""
                <div class="metric-label">Wind Speed</div>
                <div class="metric-value">{current.windspeed} <span style="font-size: 1rem;">km/h</span></div>
                """,
                unsafe_allow_html=True,
            )
        with m2:
            st.markdown(
                f"""
                <div class="metric-label">Last Observed</div>
                <div class="metric-value" style="font-size: 1.1rem; padding-top: 8px;">{format_datetime(current.observed_at)}</div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

        # Insights Card
        if forecast:
            avg_temp = calculate_average_temp(forecast)
            hottest = find_hottest_day(forecast)

            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">📊 INSIGHTS</div>', unsafe_allow_html=True)
            st.write(f"• Average forecast high: **{avg_temp:.1f}°**")
            if hottest:
                st.write(f"• Hottest day: **{format_date(hottest.date)}** at **{hottest.temp_max}°**")
            st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()