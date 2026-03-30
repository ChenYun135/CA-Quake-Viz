import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime

# 1. 顶层配置：保持专业感
st.set_page_config(page_title="加州地震研究实验室", layout="wide", page_icon="🌋")

# 自定义 CSS 提升界面质感
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e9ecef; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

st.title("🛰️ 加州百年地震风险监测系统 (专业版)")
st.caption("研究员：Yun Chen | 数据源：USGS | 技术栈：Streamlit + Plotly")

# 2. 侧边栏：便捷筛选
with st.sidebar:
    st.header("⚙️ 筛选参数")
    year_range = st.slider("观测年份区间:", 1926, 2026, (1980, 2026))
    min_mag = st.number_input("最低震级筛选:", 4.0, 9.0, 4.5, step=0.1)
    st.divider()
    st.info("💡 地图支持滚轮缩放，点击右侧标签可隐藏特定震级数据。")

# 3. 数据加载逻辑 (增加错误处理)
@st.cache_data(show_spinner="正在同步科研数据库...")
def load_data(start_year):
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {
        "format": "geojson",
        "starttime": f"{start_year}-01-01",
        "minmagnitude": 4.0,
        "minlatitude": 32.5, "maxlatitude": 42.0,
        "minlongitude": -124.5, "maxlongitude": -114.1
    }
    try:
        resp = requests.get(url, params=params, timeout=10).json()
        features = []
        for f in resp['features']:
            p, g = f['properties'], f['geometry']
            features.append({
                'time': pd.to_datetime(p['time'], unit='ms', utc=True),
                'mag': p['mag'],
                'place': p.get('place', '未知区域'),
                'lat': g['coordinates'][1],
                'lon': g['coordinates'][0]
            })
        df = pd.DataFrame(features)
        df['year'] = df['time'].dt.year
        return df
    except:
        return pd.DataFrame()

df_raw = load_data(year_range[0])

if not df_raw.empty:
    # 动态筛选
    df = df_raw[(df_raw['year'] >= year_range[0]) & 
                (df_raw['year'] <= year_range[1]) & 
                (df_raw['mag'] >= min_mag)]

    # --- 核心指标看板 (功能性) ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("记录总数", f"{len(df)} 次")
    m2.metric("最大震级", f"M {df['mag'].max():.1f}")
    m3.metric("平均震级", f"M {df['mag'].mean():.1f}")
    m4.metric("最活跃年份", int(df['year'].mode()[0]) if not df.empty else "-")

    st.divider()

    # --- 多维展示标签页 (便捷性) ---
    tab1, tab2, tab3 = st.tabs(["🗺️ 空间分布地图", "📈 趋势与密度分析", "💾 结构化原始数据"])

    with tab1:
        # 使用 scatter_mapbox 代替 scatter_map 以获得更好的兼容性和交互感
        fig_map = px.scatter_mapbox(
            df, lat="lat", lon="lon", size="mag", color="mag",
            color_continuous_scale="Reds", hover_name="place",
            mapbox_style="carto-positron", zoom=5, height=700,
            title=f"加州地震空间分布图 ({year_range[0]}-{year_range[1]})"
        )
        fig_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("年度地震频次趋势")
            y_counts = df.groupby('year').size().reset_index(name='counts')
            fig_l = px.line(y_counts, x='year', y='counts', template="plotly_white")
            st.plotly_chart(fig_l, use_container_width=True)
        with c2:
            st.subheader("震级分布密度")
            fig_h = px.histogram(df, x="mag", nbins=20, template="plotly_white", color_discrete_sequence=['#d62728'])
            st.plotly_chart(fig_h, use_container_width=True)

    with tab3:
        st.subheader("筛选后的科研数据集")
        st.dataframe(df.sort_values('time', ascending=False), use_container_width=True)
        # 增加一键下载功能 (功能性)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 点击下载筛选后的数据集 (CSV)", data=csv, file_name="ca_quake_data.csv")

else:
    st.warning("正在连接 USGS 数据库，请稍候...")