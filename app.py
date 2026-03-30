import streamlit as st
import pandas as pd
import numpy as np
import requests
import datetime
import pydeck as pdk
import os

st.set_page_config(page_title="加州百年地震分析", layout="wide")

@st.cache_data(show_spinner=True, ttl=60*60*24)
def fetch_quake_data():
    url = (
        "https://earthquake.usgs.gov/fdsnws/event/1/query"
        "?format=geojson"
        "&starttime=1926-01-01"
        f"&endtime={datetime.datetime.now().strftime('%Y-%m-%d')}"
        "&minmagnitude=4.0"
        "&minlatitude=32.5"
        "&maxlatitude=42"
        "&minlongitude=-124.5"
        "&maxlongitude=-114.1"
        "&orderby=time-asc"
    )
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    features = data.get('features', [])
    records = []
    for feat in features:
        prop = feat['properties']
        geom = feat['geometry']['coordinates']
        time_epoch = int(prop['time']) / 1000  # ms to s
        # To support pre-1970 times, use pandas.to_datetime(int, unit='s', origin='unix')
        dt = pd.to_datetime(time_epoch, unit='s', origin='unix', utc=True)
        records.append({
            "time": dt.tz_convert('US/Pacific'),
            "latitude": geom[1],
            "longitude": geom[0],
            "depth": geom[2],
            "mag": prop['mag'],
            "place": prop['place'],
            "year": dt.year
        })
    df = pd.DataFrame(records)
    # Save to CSV with utf-8-sig encoding
    df.to_csv("CA_100Year_Quakes.csv", index=False, encoding="utf-8-sig")
    return df

@st.cache_data(show_spinner=True)
def load_data():
    if os.path.exists("CA_100Year_Quakes.csv"):
        df = pd.read_csv("CA_100Year_Quakes.csv", encoding="utf-8-sig")
        df['time'] = pd.to_datetime(df['time'])
        df['year'] = df['time'].dt.year
        return df
    else:
        return fetch_quake_data()

st.title("🔬 加州百年地震分析（M4.0+）")
st.markdown(
    "> 基于 USGS API · 地域范围：加州 · 时间范围：1926年至今 · 仅包含M4.0级以上地震"
)

df = load_data()

if df.empty:
    st.error("未能获取地震数据。")
    st.stop()

# Year selection in sidebar
min_year = int(df['year'].min())
max_year = int(df['year'].max())
years = st.sidebar.slider(
    '选择年份区间：',
    min_year, max_year, (min_year, max_year),
    step=1
)
mask = (df['year'] >= years[0]) & (df['year'] <= years[1])
filtered = df.loc[mask].copy()

# Color mapping by year (earlier=浅, 最近=深)
def year_to_color(y):
    # Map to blue: older - light, recent - dark
    norm = (y - min_year) / (max_year - min_year + 1e-8)
    # Light blue (0,136,255) to dark blue (0,30,110)
    r, g, b = np.array([0, 136, 255]) * (1 - norm) + np.array([0, 30, 110]) * norm
    return [int(r), int(g), int(b), 120]

filtered["color"] = filtered['year'].apply(year_to_color)
# Dot size by magnitude（4级=40, 5级=60, ... 上限=120）
filtered["size"] = filtered['mag'].clip(lower=4, upper=8).apply(lambda m: 20 + (m-4)*20)

# Pydeck Map
mid_lat = filtered['latitude'].mean() if not filtered.empty else 37
mid_lng = filtered['longitude'].mean() if not filtered.empty else -120
st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=pdk.ViewState(
        latitude=mid_lat,
        longitude=mid_lng,
        zoom=5.7,
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            "ScatterplotLayer",
            data=filtered,
            get_position='[longitude, latitude]',
            get_radius="size",
            radius_min_pixels=3,
            radius_max_pixels=40,
            get_fill_color="color",
            pickable=True,
            auto_highlight=True,
        )
    ],
    tooltip={"html": "<b>时间：</b> {time} <br><b>震级：</b> {mag} <br><b>位置：</b> {place}", "style": {"color": "white"}}
))

# Stat cards at bottom
c1, c2 = st.columns(2)
with c1:
    st.metric("该时段地震总数", f"{len(filtered):,}")
with c2:
    if not filtered.empty:
        st.metric("最大震级", f"{filtered['mag'].max():.1f}")
    else:
        st.metric("最大震级", "--")