
import math
import time
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh


st.set_page_config(
    page_title="BANKGUARD BD",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- STYLE --------------------
st.markdown(
    """
    <style>
    :root {
        --bg: #011a2d;
        --sidebar: #242632;
        --panel: #082645;
        --panel2: #0b2a49;
        --border: #194d73;
        --text: #f8fbff;
        --muted: #8fa6bf;
        --green: #32d57d;
        --red: #f14d55;
        --teal1: #0a3c72;
        --teal2: #0d8478;
    }
    html, body, [class*="css"] {
        font-family: "Inter", "Segoe UI", Arial, sans-serif;
    }
    [data-testid="stAppViewContainer"] {
        background: #001629;
        color: var(--text);
    }
    [data-testid="stHeader"] {
        background: rgba(0, 22, 41, 0.95);
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #282936 0%, #232431 100%);
        border-right: 1px solid rgba(255,255,255,0.04);
    }
    .block-container {
        padding-top: 1.25rem;
        max-width: 1400px;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 2.6rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .sb-title {
        display:flex;
        align-items:center;
        gap:10px;
        font-weight:800;
        font-size:20px;
        color:#ffffff;
        margin-bottom:18px;
    }
    .live-mode {
        display:inline-block;
        background:#c8333c;
        color:#fff;
        padding:8px 14px;
        border-radius:999px;
        font-size:12px;
        font-weight:800;
        margin-bottom:26px;
    }
    .sb-section-title {
        color:#ffffff;
        font-size:13px;
        font-weight:700;
        margin:14px 0 8px 0;
    }
    .net-item {
        background: rgba(52, 145, 94, 0.45);
        border:1px solid rgba(107, 233, 154, 0.06);
        color:#5ff297;
        border-radius:12px;
        padding:16px 14px;
        margin-bottom:12px;
        font-weight:700;
        font-size:13px;
    }
    .hero {
        background: linear-gradient(90deg, #0a3d73 0%, #0f7a78 100%);
        border: 1px solid rgba(104, 228, 217, 0.14);
        border-radius: 18px;
        padding: 28px 24px 22px 24px;
        margin-bottom: 6px;
    }
    .hero-row {
        display:flex;
        align-items:flex-start;
        justify-content:space-between;
        gap:16px;
    }
    .hero-title {
        font-size: 36px;
        font-weight: 900;
        color: #ffffff;
        letter-spacing:0.3px;
        margin-bottom:10px;
    }
    .hero-sub {
        color: #e9f8ff;
        font-size: 15px;
        line-height:1.45;
    }
    .mini-muted {
        color:#b8dded;
        font-size:13px;
        margin-top:8px;
    }
    .live-pill {
        display:inline-block;
        background:#d33a40;
        color:#fff;
        border-radius:999px;
        padding:8px 15px;
        font-size:12px;
        font-weight:900;
        white-space:nowrap;
    }
    .metric-card {
        background:#09213e;
        border:1px solid #194d73;
        border-radius:18px;
        padding:16px 18px;
        min-height:118px;
    }
    .metric-label {
        color:#9ec3dc;
        font-size:12px;
        font-weight:800;
        letter-spacing:.4px;
        text-transform:uppercase;
    }
    .metric-value {
        color:#ffffff;
        font-size:25px;
        font-weight:900;
        margin-top:12px;
    }
    .metric-sub {
        color:#63cbff;
        font-size:12px;
        margin-top:10px;
    }
    .status-strip {
        border-radius:12px;
        padding:14px 16px;
        font-size:14px;
        font-weight:700;
        margin:4px 0 16px 0;
        border:1px solid rgba(255,255,255,0.05);
        color:#ffefaa;
        background: linear-gradient(90deg, rgba(78,86,32,.90) 0%, rgba(76,98,44,.92) 100%);
    }
    .section-head {
        color:#ffffff;
        font-size:17px;
        font-weight:900;
        margin: 8px 0 10px 0;
    }
    .panel {
        background:#08213d;
        border-radius:16px;
        border:1px solid rgba(50, 120, 170, 0.15);
        padding:12px;
    }
    .stack-card {
        background:#08213d;
        border:1px solid #194d73;
        border-radius:16px;
        padding:14px 16px;
        min-height:112px;
        margin-bottom:16px;
    }
    .stack-title {
        color:#ffffff;
        font-size:13px;
        margin-bottom:10px;
    }
    .stack-main {
        color:#ffffff;
        font-size:26px;
        font-weight:900;
        line-height:1.1;
    }
    .badge-green {
        display:inline-block;
        margin-top:10px;
        background:rgba(32, 140, 88, 0.55);
        color:#67f1a0;
        padding:6px 10px;
        border-radius:999px;
        font-size:12px;
        font-weight:700;
    }
    .pilot-card {
        background:#08213d;
        border:1px solid #194d73;
        border-radius:16px;
        padding:16px 16px 14px 16px;
        min-height:110px;
    }
    .pilot-label {
        color:#8fb2cf;
        font-size:12px;
        font-weight:700;
        margin-bottom:12px;
    }
    .pilot-value {
        color:#ffffff;
        font-size:22px;
        font-weight:900;
        margin-bottom:8px;
    }
    .pilot-sub {
        color:#56c2ff;
        font-size:12px;
    }
    .footer-note {
        text-align:center;
        color:#88a2b8;
        font-size:12px;
        margin-top:16px;
    }
    div.stButton > button {
        width: 100%;
        border: 1px solid rgba(255,255,255,0.18);
        border-radius: 10px;
        background: transparent;
        color: #ffffff;
        font-weight: 800;
        padding: 10px 8px;
    }
    div.stButton > button:hover {
        border: 1px solid rgba(255,255,255,0.32);
        color: #ffffff;
    }
    div[data-baseweb="select"] > div {
        background:#06101d !important;
        border:1px solid rgba(255,255,255,0.08) !important;
        color:#fff !important;
        border-radius:10px !important;
    }
    .small-note { color:#8fa6bf; font-size:12px; line-height:1.45; }
    hr {
        border: none;
        border-top: 1px solid rgba(255,255,255,0.10);
        margin: 18px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------- HELPERS --------------------
def get_secret(name: str, default: str = "") -> str:
    try:
        return str(st.secrets.get(name, default))
    except Exception:
        return default

def fetch_thingspeak(channel_id: str, read_key: str, results: int = 45) -> pd.DataFrame:
    url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.json"
    params = {"results": results}
    if read_key.strip():
        params["api_key"] = read_key.strip()
    r = requests.get(url, params=params, timeout=12)
    r.raise_for_status()
    payload = r.json()
    rows = []
    for item in payload.get("feeds", []):
        rows.append({
            "timestamp": pd.to_datetime(item.get("created_at"), utc=True, errors="coerce"),
            "bank_distance_cm": pd.to_numeric(item.get("field1"), errors="coerce"),
            "tilt_deg": pd.to_numeric(item.get("field2"), errors="coerce"),
            "soil_moisture_pct": pd.to_numeric(item.get("field3"), errors="coerce"),
            "river_distance_cm": pd.to_numeric(item.get("field4"), errors="coerce"),
            "flow_lpm": pd.to_numeric(item.get("field5"), errors="coerce"),
        })
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df = df.dropna(subset=["timestamp", "bank_distance_cm", "tilt_deg", "soil_moisture_pct", "river_distance_cm"])
    return df.sort_values("timestamp").reset_index(drop=True)

def make_demo_data(zone: str, points: int = 32) -> pd.DataFrame:
    cfg = {
        "Padma Zone": {"retreat": 1.8, "tilt": 6.2, "moist": 68, "river": 76, "flow": 1.2},
        "Jamuna Zone": {"retreat": 2.6, "tilt": 8.5, "moist": 72, "river": 81, "flow": 1.0},
        "Meghna Zone": {"retreat": 1.2, "tilt": 4.0, "moist": 60, "river": 70, "flow": 1.4},
        "BAUET Demo Zone": {"retreat": 2.1, "tilt": 7.0, "moist": 66, "river": 78, "flow": 1.1},
    }[zone]
    now = datetime.now(timezone.utc)
    t = np.linspace(0, 1, points)
    wobble = np.sin(np.linspace(0, 5*np.pi, points))
    bank_baseline = 10.0
    river_sensor_height = 15.0

    retreat = 0.3 + cfg["retreat"] * (0.45 + 0.55*t) + 0.22 * wobble
    tilt_change = 1.2 + cfg["tilt"] * (0.35 + 0.65*t) + 0.7 * np.sin(np.linspace(0, 2.6*np.pi, points))
    soil = 38 + (cfg["moist"] - 38) * (0.35 + 0.65*t) + 1.0 * wobble
    river_pct = 48 + (cfg["river"] - 48) * (0.35 + 0.65*t) + 2.5 * wobble
    flow = 1.9 + (cfg["flow"] - 1.9) * (0.2 + 0.8*t) + 0.05*wobble

    timestamps = [now - timedelta(seconds=(points - 1 - i) * 10) for i in range(points)]
    return pd.DataFrame({
        "timestamp": timestamps,
        "bank_distance_cm": bank_baseline + np.maximum(retreat, 0),
        "tilt_deg": np.maximum(tilt_change, 0),
        "soil_moisture_pct": np.clip(soil, 0, 100),
        "river_distance_cm": river_sensor_height * (1 - np.clip(river_pct, 0, 100)/100),
        "flow_lpm": np.maximum(flow, 0),
    })

def add_metrics(df: pd.DataFrame, bank_baseline=10.0, river_sensor_height=15.0) -> pd.DataFrame:
    d = df.copy()
    d["bank_retreat_cm"] = (d["bank_distance_cm"] - bank_baseline).clip(lower=0)
    d["tilt_change_deg"] = d["tilt_deg"].abs()
    d["river_level_pct"] = ((river_sensor_height - d["river_distance_cm"]) / river_sensor_height * 100).clip(0, 100)
    d["stability_score"] = (100 - (d["tilt_change_deg"] * 4 + d["bank_retreat_cm"] * 10)).clip(0, 100)
    risk_raw = (
        0.40 * (d["bank_retreat_cm"] / 4.0 * 100).clip(0,100)
        + 0.25 * (d["tilt_change_deg"] / 12.0 * 100).clip(0,100)
        + 0.20 * (d["soil_moisture_pct"] / 100 * 100).clip(0,100)
        + 0.15 * (d["river_level_pct"] / 100 * 100).clip(0,100)
    )
    d["risk_score"] = risk_raw.clip(0, 98.5)
    return d

def status_message(score: float, zone: str):
    if score < 25:
        return "LOW EROSION RISK — bank condition currently operating within normal range.", "green"
    elif score < 50:
        return f"MEDIUM EROSION RISK — increased monitoring recommended for {zone}.", "amber"
    elif score < 75:
        return f"HIGH EROSION RISK — erosion activity rising in {zone}.", "orange"
    else:
        return f"CRITICAL EROSION RISK — immediate response recommended for {zone}.", "red"

def metric_card(label: str, value: str, sub: str):
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-label">{label}</div>
          <div class="metric-value">{value}</div>
          <div class="metric-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def make_line_chart(df: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=(df["river_level_pct"]/100),
        mode="lines+markers",
        name="River Level (m)",
        line=dict(color="#6c74ff", width=2.5),
        marker=dict(size=6, color="#6c74ff")
    ))
    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=df["risk_score"],
        mode="lines",
        name="AI Risk Score",
        yaxis="y2",
        line=dict(color="#ff5a4a", width=2.2)
    ))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#08213d",
        plot_bgcolor="#08213d",
        margin=dict(l=55, r=55, t=16, b=38),
        height=338,
        font=dict(color="#dfefff"),
        legend=dict(orientation="h", x=0.02, y=1.10, bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(showgrid=False, tickfont=dict(size=11)),
        yaxis=dict(
            title="River Level (m)",
            gridcolor="rgba(255,255,255,0.10)",
            zeroline=False,
            range=[0.45, 0.95]
        ),
        yaxis2=dict(
            title="Risk Score",
            overlaying="y",
            side="right",
            range=[0, 100],
            showgrid=False
        ),
    )
    return fig

def make_gauge(score: float):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix":"%", "font":{"size":28, "color":"#f7fbff"}},
        title={"text":"Real-time Risk Score", "font":{"size":12, "color":"#cfe7f4"}},
        gauge={
            "axis":{"range":[0,100], "tickmode":"array", "tickvals":[0,20,40,60,80,100], "tickcolor":"#dfefff"},
            "bar":{"color":"rgba(0,0,0,0)"},
            "bgcolor":"#08213d",
            "borderwidth":0,
            "steps":[
                {"range":[0,30], "color":"#009b24"},
                {"range":[30,60], "color":"#f0bb36"},
                {"range":[60,80], "color":"#f87b28"},
                {"range":[80,100], "color":"#ea2428"},
            ],
            "threshold":{
                "line":{"color":"#ffffff","width":4},
                "thickness":0.82,
                "value":score
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor="#08213d",
        height=338,
        margin=dict(l=10,r=10,t=28,b=6),
        font=dict(color="#eef8ff")
    )
    return fig

def bar_chart_ai():
    labels = ["Random Forest", "XGBoost", "ANN", "LSTM"]
    values = [90, 93, 91, 92]
    fig = go.Figure(go.Bar(x=labels, y=values, marker_color="#6970eb"))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#08213d",
        plot_bgcolor="#08213d",
        height=250,
        margin=dict(l=50, r=15, t=10, b=30),
        yaxis=dict(title="Accuracy (%)", range=[80,100], gridcolor="rgba(255,255,255,0.10)"),
        xaxis=dict(showgrid=False),
        font=dict(color="#eef8ff"),
    )
    fig.update_traces(text=values, textposition="inside", insidetextfont=dict(color="white", size=12))
    return fig

def bar_chart_hotspot():
    labels = ["Z1", "Z2", "Z3", "Z4", "Z5"]
    values = [18, 32, 78, 64, 24]
    fig = go.Figure(go.Bar(x=labels, y=values, marker_color="#6970eb"))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#08213d",
        plot_bgcolor="#08213d",
        height=250,
        margin=dict(l=50, r=15, t=10, b=30),
        yaxis=dict(title="Anomaly Score", range=[0,100], gridcolor="rgba(255,255,255,0.10)"),
        xaxis=dict(showgrid=False),
        font=dict(color="#eef8ff"),
    )
    fig.update_traces(text=values, textposition="inside", insidetextfont=dict(color="white", size=12))
    return fig

# -------------------- SIDEBAR --------------------
if "running" not in st.session_state:
    st.session_state.running = True

st.sidebar.markdown('<div class="sb-title">💧 <span>BANKGUARD BD</span></div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="live-mode">● LIVE PRESENTATION MODE</div>', unsafe_allow_html=True)

zone = st.sidebar.selectbox("Monitoring Zone", ["Padma Zone", "Jamuna Zone", "Meghna Zone", "BAUET Demo Zone"])
refresh_seconds = st.sidebar.slider("Refresh interval (seconds)", min_value=2, max_value=10, value=5, step=1)

btn1, btn2 = st.sidebar.columns(2)
with btn1:
    if st.button("▶ START"):
        st.session_state.running = True
with btn2:
    if st.button("⏸ STOP"):
        st.session_state.running = False

if st.session_state.running:
    st_autorefresh(interval=refresh_seconds * 1000, key="bankguard_autorefresh")

st.sidebar.markdown("<hr>", unsafe_allow_html=True)
st.sidebar.markdown('<div class="sb-title" style="font-size:16px;margin-bottom:14px;">IoT Sensor Network</div>', unsafe_allow_html=True)
for name in [
    "River Level ONLINE",
    "Bank Distance ONLINE",
    "Soil Moisture ONLINE",
    "Slope Tilt ONLINE",
    "Water Flow ONLINE"
]:
    st.sidebar.markdown(f'<div class="net-item">● {name}</div>', unsafe_allow_html=True)

st.sidebar.markdown("<hr>", unsafe_allow_html=True)
mode = st.sidebar.radio("Data Source", ["Demo Mode", "ThingSpeak Live"], index=0)
st.sidebar.markdown('<div class="small-note">Demo Mode দেখানোর জন্য। Actual ESP32 reading ব্যবহার করতে চাইলে ThingSpeak Live বেছে নাও।</div>', unsafe_allow_html=True)
channel_id = ""
read_key = ""
if mode == "ThingSpeak Live":
    channel_id = st.sidebar.text_input("ThingSpeak Channel ID", value=get_secret("THINGSPEAK_CHANNEL_ID", ""))
    read_key = st.sidebar.text_input("Read API Key", value=get_secret("THINGSPEAK_READ_API_KEY", ""), type="password")
else:
    st.sidebar.markdown('<div class="small-note">Demo data simulation only — real measurement নয়।</div>', unsafe_allow_html=True)

# -------------------- DATA --------------------
bank_baseline_cm = 10.0
river_sensor_height_cm = 15.0

if mode == "ThingSpeak Live" and channel_id.strip():
    try:
        raw = fetch_thingspeak(channel_id.strip(), read_key.strip(), results=34)
        if raw.empty:
            raw = make_demo_data(zone)
            st.warning("ThingSpeak channel থেকে data পাওয়া যায়নি। আপাতত Demo data দেখানো হচ্ছে।")
    except Exception as e:
        raw = make_demo_data(zone)
        st.warning(f"ThingSpeak connection error. আপাতত Demo data দেখানো হচ্ছে। Error: {e}")
else:
    raw = make_demo_data(zone)

df = add_metrics(raw, bank_baseline=bank_baseline_cm, river_sensor_height=river_sensor_height_cm)
latest = df.iloc[-1]
status_text, status_level = status_message(float(latest["risk_score"]), zone)

# -------------------- HEADER --------------------
st.markdown(
    f"""
    <div class="hero">
      <div class="hero-row">
        <div>
          <div class="hero-title">💧 &nbsp;BANKGUARD BD</div>
          <div class="hero-sub">AI-Assisted Smart Riverbank Erosion Monitoring, Slope Instability Detection &amp; Early Warning System</div>
        </div>
        <div style="text-align:right;">
          <div class="live-pill">● LIVE</div>
          <div class="mini-muted" style="margin-top:28px;">IoT Command Center</div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------- TOP METRIC CARDS --------------------
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    metric_card("🌊 RIVER LEVEL", f'{latest["river_level_pct"]/100:.2f} m', "River sensor • LIVE")
with c2:
    metric_card("📏 BANK RETREAT", f'{latest["bank_retreat_cm"]:.1f} cm', "Bank sensor • LIVE")
with c3:
    metric_card("🌱 SOIL MOISTURE", f'{latest["soil_moisture_pct"]:.0f} %', "Soil sensor • LIVE")
with c4:
    stability_label = "GOOD" if latest["stability_score"] >= 70 else "WATCH" if latest["stability_score"] >= 45 else "RISK"
    metric_card("🧭 BANK STABILITY", stability_label, f'Tilt {latest["tilt_change_deg"]:.1f}° • Stability index')
with c5:
    metric_card("💧 WATER FLOW", f'{latest["flow_lpm"]:.1f} L/min', "Pump line sensor")

icon = "⚠" if latest["risk_score"] >= 25 else "✓"
st.markdown(f'<div class="status-strip">{icon} &nbsp;{status_text}</div>', unsafe_allow_html=True)

# -------------------- MAIN ROW: TREND + GAUGE --------------------
left, right = st.columns([2.2, 1.05])
with left:
    st.markdown('<div class="section-head">📈 LIVE SENSOR & RISK TREND</div>', unsafe_allow_html=True)
    st.plotly_chart(make_line_chart(df), use_container_width=True, config={"displayModeBar": False})
with right:
    st.markdown('<div class="section-head">◉ AI EROSION RISK</div>', unsafe_allow_html=True)
    st.plotly_chart(make_gauge(float(latest["risk_score"])), use_container_width=True, config={"displayModeBar": False})

# -------------------- SECOND ROW --------------------
col_a, col_b, col_c = st.columns([1.1, 1.1, 0.95])
with col_a:
    st.markdown('<div class="section-head">🧠 AI MODEL PERFORMANCE</div>', unsafe_allow_html=True)
    st.plotly_chart(bar_chart_ai(), use_container_width=True, config={"displayModeBar": False})
with col_b:
    st.markdown('<div class="section-head">🚧 EROSION HOTSPOT DETECTION</div>', unsafe_allow_html=True)
    st.plotly_chart(bar_chart_hotspot(), use_container_width=True, config={"displayModeBar": False})
    st.markdown(
        '<div class="footer-note" style="text-align:left;margin-top:-4px;">Pilot erosion detection accuracy: 91%</div>',
        unsafe_allow_html=True,
    )
with col_c:
    st.markdown('<div class="section-head">♻ RIVERBANK RESPONSE & SAFETY</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="stack-card">
          <div class="stack-title">Monitoring</div>
          <div class="stack-main">ACTIVE</div>
          <div class="badge-green">↑ Process running</div>
        </div>
        <div class="stack-card">
          <div class="stack-title">Safety Check</div>
          <div class="stack-main">PASS</div>
          <div class="badge-green">↑ Safe range</div>
        </div>
        <div class="stack-card">
          <div class="stack-title">Field Response</div>
          <div class="stack-main">READY</div>
          <div class="badge-green">↑ Monitoring team standby</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -------------------- THIRD ROW --------------------
st.markdown('<div class="section-head">📊 PILOT USE CASE — LIVE SYSTEM STATUS</div>', unsafe_allow_html=True)
p1, p2, p3, p4 = st.columns(4)
with p1:
    st.markdown(
        '<div class="pilot-card"><div class="pilot-label">Coverage Area</div><div class="pilot-value">15 km²</div><div class="pilot-sub">BANKGUARD BD pilot target</div></div>',
        unsafe_allow_html=True,
    )
with p2:
    st.markdown(
        '<div class="pilot-card"><div class="pilot-label">Sensors Deployed</div><div class="pilot-value">60+</div><div class="pilot-sub">BANKGUARD BD pilot target</div></div>',
        unsafe_allow_html=True,
    )
with p3:
    st.markdown(
        '<div class="pilot-card"><div class="pilot-label">Flood Warning Accuracy</div><div class="pilot-value">92%</div><div class="pilot-sub">BANKGUARD BD pilot target</div></div>',
        unsafe_allow_html=True,
    )
with p4:
    st.markdown(
        '<div class="pilot-card"><div class="pilot-label">Erosion Detection Accuracy</div><div class="pilot-value">91%</div><div class="pilot-sub">BANKGUARD BD pilot target</div></div>',
        unsafe_allow_html=True,
    )

last_update = pd.to_datetime(latest["timestamp"], utc=True).strftime("%d %b %Y, %I:%M:%S %p")
st.markdown(
    f'<div class="footer-note">Last sensor update: {last_update} • Zone: {zone} • BANKGUARD BD Smart River Command Center</div>',
    unsafe_allow_html=True,
)
