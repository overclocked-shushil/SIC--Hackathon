import os
import sys
import json
import webbrowser
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import folium
from datetime import date, datetime, time, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE_DIR, "output_maps")
os.makedirs(OUT_DIR, exist_ok=True)

CSV_PATH = "/Users/shushil/Downloads/vaccinations.csv"
GEOJSON_PATH = "/Users/shushil/Downloads/World_Countries_(Generalized)_2173680399808997149.geojson"


def require_file(path):
    if not os.path.exists(path):
        sys.exit(f"Required data file not found: {path}")


def save_and_open(fmap, filename):
    path = os.path.join(OUT_DIR, filename)
    fmap.save(path)
    webbrowser.open(f"file://{path}")
    print(f"Saved map: {path}")


def main():
    require_file(CSV_PATH)
    df = pd.read_csv(CSV_PATH)

    rename_map = {}
    if 'location' in df.columns and 'Entity' not in df.columns:
        rename_map['location'] = 'Entity'
    if 'iso_code' in df.columns and 'Code' not in df.columns:
        rename_map['iso_code'] = 'Code'
    if 'date' in df.columns and 'Day' not in df.columns:
        rename_map['date'] = 'Day'
    if rename_map:
        df = df.rename(columns=rename_map)

    df.info()

    df['Date'] = pd.to_datetime(df['Day'])
    df.set_index('Date', inplace=True)
    df.drop(['Day'], axis=1, inplace=True)
    print(df.head())

    print(len(df['Entity'].unique()))

    covid_c = df.groupby(['Entity'])

    for key, group in covid_c:
        print('+key:', key)
        print('+number:', len(group))
        print(group.head())
        print('\n')

    total_df = covid_c[['total_vaccinations_per_hundred']].sum()
    print(total_df.head())

    map1 = folium.Map(location=[37.2594750011864, 127.05145091394964],
                       zoom_start=13,
                       tiles="Esri.WorldStreetMap")
    save_and_open(map1, "map_street.html")

    map2 = folium.Map(location=[37.2594750011864, 127.05145091394964],
                       zoom_start=13,
                       tiles="Esri.WorldImagery")
    save_and_open(map2, "map_imagery.html")

    marker_map = folium.Map(location=[45.372, -121.6972], zoom_start=12, tiles="Esri.WorldStreetMap")

    folium.Marker(
        location=[45.3288, -121.6625],
        popup="Mt. Hood Meadows",
        icon=folium.Icon(icon="cloud"),
    ).add_to(marker_map)

    folium.Marker(
        location=[45.3311, -121.7113],
        popup="Timberline Lodge",
        icon=folium.Icon(color="green"),
    ).add_to(marker_map)

    folium.CircleMarker(
        location=[45.3800, -121.6000],
        radius=100,
        popup="circle",
        color="#3186cc",
        fill=True,
        fill_color="#3186cc",
    ).add_to(marker_map)

    save_and_open(marker_map, "map_markers.html")

    url = (
        "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data"
    )
    state_geo = f"{url}/us-states.json"
    state_unemployment = f"{url}/US_Unemployment_Oct2012.csv"
    state_data = pd.read_csv(state_unemployment)

    m_us = folium.Map(location=[48, -102], zoom_start=3)

    folium.Choropleth(
        geo_data=state_geo,
        name="choropleth",
        data=state_data,
        columns=["State", "Unemployment"],
        key_on="feature.id",
        fill_color="YlGn",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Unemployment Rate (%)",
    ).add_to(m_us)

    folium.LayerControl().add_to(m_us)
    save_and_open(m_us, "map_us_unemployment.html")

    require_file(GEOJSON_PATH)

    center = [35.762887375145795, 84.08313219586536]

    m_world = folium.Map(location=center, zoom_start=2,
                          max_bounds=True,
                          min_zoom=1, min_lat=-84,
                          max_lat=84, min_lon=-175, max_lon=187)

    with open(GEOJSON_PATH, encoding='utf-8') as f:
        json_data = json.load(f)

    folium.Choropleth(geo_data=json_data,
                       data=total_df,
                       columns=(total_df.index, 'total_vaccinations_per_hundred'),
                       key_on='properties.COUNTRY',
                       fill_color='RdYlGn',
                       fill_opacity=0.7,
                       line_opacity=0.5,
                       ).add_to(m_world)

    folium.LayerControl().add_to(m_world)
    save_and_open(m_world, "map_world_covid.html")


if __name__ == "__main__":
    main()
