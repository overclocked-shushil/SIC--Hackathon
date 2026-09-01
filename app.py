"""
app.py
The Streamlit UI. This file calls into weather_api.py and
weather_processing.py and handles layout and user interaction.
Business logic does not live here.
"""

import streamlit as st
import pandas as pd

from weather_api import fetch_weather_for_city, WeatherAPIError
from weather_processing import (
    parse_current_weather,
    parse_daily_forecast,
    calculate_average_temp,
    find_hottest_day,
)
from utils import format_date, format_datetime, validate_city_input
from config import DEFAULT_CITY

st.set_page_config(page_title="Weather Dashboard", page_icon="⛅", layout="wide")


@st.cache_data(ttl=600)  # cache for 10 minutes so reruns don't refetch needlessly
def get_weather(city: str):
    return fetch_weather_for_city(city)


def main():
    st.title("⛅ Weather Dashboard")
    st.caption("Powered by Open-Meteo — no API key required.")

    with st.sidebar:
        st.header("Search")
        city_input = st.text_input("City name", value=DEFAULT_CITY)
        search = st.button("Get Weather", use_container_width=True)
        if search:
            st.session_state["last_city"] = city_input

    city_to_use = st.session_state.get("last_city", DEFAULT_CITY)

    try:
        city_to_use = validate_city_input(city_to_use)
        with st.spinner(f"Fetching weather for {city_to_use}..."):
            location, raw_weather = get_weather(city_to_use)
    except ValueError as e:
        st.error(str(e))
        return
    except WeatherAPIError as e:
        st.error(f"⚠️ {e}")
        return

    current = parse_current_weather(raw_weather)
    forecast = parse_daily_forecast(raw_weather)

    # --- Location header ---
    st.subheader(f"{location.get('name')}, {location.get('country', '')}")

    # --- Current conditions ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Temperature", f"{current.temperature}°")
    col2.metric("Wind Speed", f"{current.windspeed} km/h")
    col3.metric("Condition", f"{current.icon} {current.condition}")

    st.caption(f"Last observed: {format_datetime(current.observed_at)}")
    st.divider()

    # --- Forecast chart ---
    st.subheader("5-Day Forecast")

    if forecast:
        chart_df = pd.DataFrame(
            {
                "Date": [format_date(f.date) for f in forecast],
                "High": [f.temp_max for f in forecast],
                "Low": [f.temp_min for f in forecast],
            }
        ).set_index("Date")

        st.line_chart(chart_df)

        # --- Forecast cards ---
        cols = st.columns(len(forecast))
        for col, day in zip(cols, forecast):
            with col:
                st.markdown(f"**{format_date(day.date)}**")
                st.markdown(f"{day.icon}")
                st.markdown(f"{day.temp_max}° / {day.temp_min}°")
                st.caption(day.condition)

        st.divider()

        # --- Simple derived stats ---
        avg_temp = calculate_average_temp(forecast)
        hottest = find_hottest_day(forecast)

        st.write(f"📊 Average forecast high: **{avg_temp:.1f}°**")
        if hottest:
            st.write(
                f"🔥 Hottest day: **{format_date(hottest.date)}** "
                f"at **{hottest.temp_max}°**"
            )
    else:
        st.warning("No forecast data available.")


if __name__ == "__main__":
    main()