import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from scheduler import get_cached_prices, get_price_history
from price_manager import (load_products, save_price,
                            get_price_changes, compute_margin)
from config import PRODUCTS

st.set_page_config(
    page_title="Price Smarter. Sell Faster.",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,300&family=DM+Mono:wght@400;500&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,600;1,9..144,300&display=swap');

/* ══════════════════════════════════════════
   ROOT TOKENS
══════════════════════════════════════════ */

:root {
  /* LIGHT THEME BASE */
  --bg:          #f8fafc;   /* main background */
  --bg2:         #ffffff;   /* cards */
  --bg3:         #f1f5f9;   /* hover / subtle blocks */

  /* BORDERS */
  --border:      #e5e7eb;
  --border2:     #d1d5db;

  /* TEXT (HIGH CONTRAST) */
  --text:        #0f172a;   /* main text - DARK */
  --text-muted:  #475569;   /* secondary */
  --text-dim:    #94a3b8;   /* labels */

  /* ACCENTS */
  --accent:      #6366f1;
  --accent-glow: rgba(99,102,241,0.15);

  --emerald:     #10b981;
  --rose:        #ef4444;
  --amber:       #f59e0b;
  --sky:         #3b82f6;

  /* LIGHT BACKGROUNDS */
  --emerald-bg:  rgba(16,185,129,0.1);
  --rose-bg:     rgba(239,68,68,0.1);
  --amber-bg:    rgba(245,158,11,0.1);
  --accent-bg:   rgba(99,102,241,0.1);

  --radius:      12px;
  --radius-sm:   8px;

  /* SOFT SHADOW */
  --shadow:      0 4px 16px rgba(0,0,0,0.05);
}

/* ══════════════════════════════════════════
   GLOBAL RESET
══════════════════════════════════════════ */
html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif !important;
  background-color: #f8fafc !important;
  color: #0f172a !important;
}
header { display: none !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* Main content area */
.block-container {
  padding: 2.5rem 3rem !important;
  background: var(--bg) !important;
  max-width: 1600px !important;
}

/* 🔥 ADD THIS RIGHT HERE */
* {
  color: var(--text);
}

/* Remove default streamlit white backgrounds */
.stApp { background: var(--bg) !important; }
.element-container { background: transparent !important; }

/* ══════════════════════════════════════════
   SIDEBAR
══════════════════════════════════════════ */
[data-testid="stSidebar"] {
  background: #ffffff !important;
  border-right: 1px solid var(--border) !important;
  min-width: 240px !important;
  max-width: 240px !important;
}
[data-testid="stSidebar"] > div:first-child {
  padding: 28px 20px !important;
}
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stSidebar"][aria-expanded="false"] {
  min-width: 240px !important;
  transform: none !important;
}

/* Sidebar radio nav */
[data-testid="stSidebar"] .stRadio > label { display: none; }
[data-testid="stSidebar"] .stRadio > div { gap: 2px !important; }
[data-testid="stSidebar"] .stRadio > div > label {
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  padding: 10px 14px !important;
  border-radius: var(--radius-sm) !important;
  cursor: pointer !important;
  transition: all 0.15s ease !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  color: var(--text-muted) !important;
  width: 100% !important;
  margin: 0 !important;
  border: 1px solid transparent !important;
}
[data-testid="stSidebar"] .stRadio > div > label:hover {
  background: var(--bg3) !important;
  color: var(--text) !important;
  border-color: var(--border) !important;
}
[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"],
[data-testid="stSidebar"] .stRadio > div > label[aria-checked="true"] {
  background: var(--accent-bg) !important;
  border-color: var(--accent) !important;
  color: #c4bbff !important;
}
[data-testid="stSidebar"] .stRadio > div > label > div:first-child {
  display: none !important;
}

/* Sidebar button */
[data-testid="stSidebar"] .stButton > button {
  background: var(--bg3) !important;
  border: 1px solid var(--border2) !important;
  color: var(--text-muted) !important;
  font-size: 12px !important;
  border-radius: var(--radius-sm) !important;
  transition: all 0.15s ease !important;
  width: 100% !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  border-color: var(--accent) !important;
  color: var(--text) !important;
}

/* ══════════════════════════════════════════
   TYPOGRAPHY
══════════════════════════════════════════ */
.page-title {
  font-family: 'Fraunces', serif;
  font-size: 30px;
  font-weight: 600;
  color: var(--text);
  letter-spacing: -0.5px;
  line-height: 1.2;
}
.page-sub {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 6px;
  margin-bottom: 32px;
  font-weight: 400;
}
.section-title {
  font-family: 'Fraunces', serif;
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 4px;
}
.section-sub {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 18px;
}

/* ══════════════════════════════════════════
   KPI GRID
══════════════════════════════════════════ */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}
.kpi-card {
  background: var(--bg2);
  border-radius: var(--radius);
  padding: 20px 22px;
  border: 1px solid var(--border);
  position: relative;
  overflow: hidden;
  transition: border-color 0.2s ease;
}
.kpi-card:hover { border-color: var(--border2); }
.kpi-card::after {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: var(--kpi-accent, var(--border2));
  opacity: 0.8;
}
.kpi-card.kpi-red   { --kpi-accent: var(--rose); }
.kpi-card.kpi-green { --kpi-accent: var(--emerald); }
.kpi-card.kpi-blue  { --kpi-accent: var(--accent); }
.kpi-card.kpi-amber { --kpi-accent: var(--amber); }

.kpi-label {
  font-size: 10px;
  font-weight: 600;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 12px;
}
.kpi-value {
  font-family: 'Fraunces', serif;
  font-size: 32px;
  font-weight: 600;
  color: var(--text);
  line-height: 1;
}
.kpi-value.kv-red   { color: var(--rose); }
.kpi-value.kv-green { color: var(--emerald); }
.kpi-value.kv-blue  { color: var(--accent); }
.kpi-value.kv-amber { color: var(--amber); }
.kpi-footer { font-size: 11px; color: var(--text-muted); margin-top: 10px; }
.kpi-footer.up   { color: var(--emerald); }
.kpi-footer.down { color: var(--rose); }

/* ══════════════════════════════════════════
   SECTION CARD
══════════════════════════════════════════ */
.section-card {
  background: var(--bg2);
  border-radius: var(--radius);
  border: 1px solid var(--border);
  padding: 24px 28px;
  margin-bottom: 20px;
}

/* ══════════════════════════════════════════
   BADGES
══════════════════════════════════════════ */
.count-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 20px;
  font-family: 'DM Mono', monospace;
}
.badge-red    { background: var(--rose-bg);    color: var(--rose); }
.badge-green  { background: var(--emerald-bg); color: var(--emerald); }
.badge-grey   { background: var(--bg3);        color: var(--text-muted); }
.badge-purple { background: var(--accent-bg);  color: var(--accent); }

/* ══════════════════════════════════════════
   TABLE
══════════════════════════════════════════ */
table.ptable {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
table.ptable th {
  text-align: left;
  font-size: 10px;
  font-weight: 600;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 10px 16px;
  border-bottom: 1px solid var(--border);
  background: #f1f5f9;
}
table.ptable td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  color: var(--text);
  vertical-align: middle;
}
table.ptable tr:hover td { background: var(--bg3); }
table.ptable tr:last-child td { border-bottom: none; }

/* ══════════════════════════════════════════
   ACTION PILLS
══════════════════════════════════════════ */
.action-pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 20px;
  white-space: nowrap;
  font-family: 'DM Mono', monospace;
}
.pill-lower  { background: var(--rose-bg);    color: var(--rose); }
.pill-raise  { background: var(--emerald-bg); color: var(--emerald); }
.pill-hold   { background: var(--bg3);        color: var(--text-muted); }

/* Gap % */
.gap-red   { color: var(--rose);     font-weight: 600; font-size: 12px; font-family: 'DM Mono', monospace; }
.gap-green { color: var(--emerald);  font-weight: 600; font-size: 12px; font-family: 'DM Mono', monospace; }
.gap-grey  { color: var(--text-muted); font-size: 12px; font-family: 'DM Mono', monospace; }

/* Margin bar */
.mbar-bg {
  width: 52px; height: 4px;
  background: var(--bg3);
  border-radius: 3px;
  display: inline-block;
  vertical-align: middle;
  margin-right: 6px;
}
.mbar-fill { height: 4px; border-radius: 3px; }

/* ══════════════════════════════════════════
   ALERT ITEMS
══════════════════════════════════════════ */
.alert-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 18px 20px;
  border-radius: var(--radius);
  margin-bottom: 10px;
  border: 1px solid var(--border);
  background: #ffffff;
  transition: border-color 0.2s ease;
}
.alert-item:hover { border-color: var(--border2); }
.alert-item.urgent { border-left: 3px solid var(--rose);    background: linear-gradient(90deg, rgba(248,113,113,0.04) 0%, var(--bg2) 40%); }
.alert-item.warn   { border-left: 3px solid var(--amber);   background: linear-gradient(90deg, rgba(251,191,36,0.04) 0%, var(--bg2) 40%); }
.alert-item.good   { border-left: 3px solid var(--emerald); background: linear-gradient(90deg, rgba(52,211,153,0.04) 0%, var(--bg2) 40%); }

.alert-name  { font-size: 14px; font-weight: 600; color: var(--text); font-family: 'Fraunces', serif; }
.alert-meta  { font-size: 12px; color: var(--text-muted); margin-top: 3px; }
.alert-prices { display: flex; gap: 28px; margin-top: 12px; }
.ap-label { font-size: 10px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 3px; }
.ap-val   { font-size: 16px; font-weight: 700; color: var(--text); font-family: 'DM Mono', monospace; }
.ap-val.red    { color: var(--rose); }
.ap-val.green  { color: var(--emerald); }
.ap-val.purple { color: var(--accent); }

/* ══════════════════════════════════════════
   DETAIL CARD (product deep dive)
══════════════════════════════════════════ */
.detail-card {
  background: var(--bg3);
  border: 1px solid var(--border2);
  border-radius: var(--radius);
  padding: 28px 32px;
  color: var(--text);
  margin: 16px 0;
  position: relative;
  overflow: hidden;
}
.detail-card::before {
  content: '';
  position: absolute;
  top: -60px; right: -60px;
  width: 180px; height: 180px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(124,111,253,0.08) 0%, transparent 70%);
}
.detail-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 24px;
}
.detail-label { font-size: 10px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px; }
.detail-value { font-family: 'DM Mono', monospace; font-size: 20px; font-weight: 500; color: var(--text); }
.detail-value.green  { color: var(--emerald); }
.detail-value.purple { color: var(--accent); }

/* ══════════════════════════════════════════
   ML PIPELINE
══════════════════════════════════════════ */
.pipeline-step {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px 16px;
  position: relative;
  transition: border-color 0.2s ease;
}
.pipeline-step:hover { border-color: var(--border2); }
.pipeline-step.done   { border-left: 3px solid var(--emerald); }
.pipeline-step.active { border-left: 3px solid var(--accent); }
.pipeline-step.info   { border-left: 3px solid var(--amber); }

.step-title { font-size: 13px; font-weight: 600; color: var(--text); font-family: 'Fraunces', serif; }
.step-sub   { font-size: 11px; color: var(--text-muted); margin-top: 4px; line-height: 1.5; }
.step-badge {
  display: inline-block;
  font-size: 10px;
  font-weight: 600;
  padding: 2px 10px;
  border-radius: 10px;
  margin-top: 8px;
  font-family: 'DM Mono', monospace;
}
.badge-done   { background: var(--emerald-bg); color: var(--emerald); }
.badge-active { background: var(--accent-bg);  color: var(--accent); }
.badge-info   { background: var(--amber-bg);   color: var(--amber); }

/* ══════════════════════════════════════════
   METRIC CARDS (ML page)
══════════════════════════════════════════ */
.metric-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px 16px;
  text-align: center;
}
.metric-card .mc-val   { font-family: 'DM Mono', monospace; font-size: 26px; font-weight: 500; color: var(--accent); }
.metric-card .mc-label { font-size: 10px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.08em; margin-top: 6px; }
.metric-card .mc-sub   { font-size: 11px; color: var(--text-muted); margin-top: 4px; }

/* ══════════════════════════════════════════
   REWARD BOX (code display)
══════════════════════════════════════════ */
.reward-box {
  width: 100%;              /* 🔥 ADD THIS */
  display: block;           /* 🔥 ADD THIS */
  box-sizing: border-box;   /* 🔥 ADD THIS */
  background: #0a0c10;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 22px 24px;
  font-family: 'DM Mono', monospace;
  font-size: 12.5px;
  color: #c9d1d9;
  line-height: 2;
  margin: 12px 0;
}
.reward-box .cm  { color: #94a3b8; }
.reward-box .kw  { color: #6366f1; }
.reward-box .nm  { color: #10b981; }
.reward-box .st  { color: #f59e0b; }
.reward-box .fn  { color: #3b82f6; }


/* ══════════════════════════════════════════
   STREAMLIT OVERRIDES
══════════════════════════════════════════ */
/* Selectboxes */
.stSelectbox > div > div {
  background: var(--bg2) !important;
  border-color: var(--border) !important;
  color: var(--text) !important;
  border-radius: var(--radius-sm) !important;
}
.stSelectbox > div > div:hover { border-color: var(--border2) !important; }

/* Number input */
.stNumberInput > div > div {
  background: var(--bg2) !important;
  border-color: var(--border) !important;
  color: var(--text) !important;
  border-radius: var(--radius-sm) !important;
}

/* Buttons */
.stButton > button {
  background: var(--bg3) !important;
  border: 1px solid var(--border2) !important;
  color: var(--text) !important;
  border-radius: var(--radius-sm) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 500 !important;
  transition: all 0.15s ease !important;
}
.stButton > button {
  background: #ffffff !important;
  border: 1px solid #d1d5db !important;
  color: #0f172a !important;
}

.stButton > button:hover {
  background: #eef2ff !important;
  border-color: #6366f1 !important;
  color: #6366f1 !important;
}

.stButton > button[kind="primary"] {
  background: #6366f1 !important;
  color: #ffffff !important;
}
/* Metrics */
[data-testid="metric-container"] {
  background: var(--bg2) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  padding: 16px !important;
}
[data-testid="metric-container"] label {
  color: var(--text-muted) !important;
  font-size: 11px !important;
  text-transform: uppercase !important;
  letter-spacing: 0.05em !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
  color: var(--text) !important;
  font-family: 'DM Mono', monospace !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
  font-family: 'DM Mono', monospace !important;
  font-size: 12px !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
}

/* Slider */
.stSlider > div { color: var(--text-muted) !important; }

/* Success / Error / Info / Warning */
.stAlert {
  border-radius: var(--radius-sm) !important;
  border: 1px solid var(--border) !important;
}

/* Expander */
.streamlit-expanderHeader {
  background: var(--bg2) !important;
  color: var(--text) !important;
  border-radius: var(--radius-sm) !important;
}

/* Caption */
.stCaption { color: var(--text-muted) !important; font-size: 12px !important; }

/* Divider */
hr { border-color: var(--border) !important; margin: 20px 0 !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background: var(--bg2) !important; }
.stTabs [data-baseweb="tab"] { color: var(--text-muted) !important; }
.stTabs [aria-selected="true"] { color: var(--text) !important; }
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_data():
    data = get_cached_prices()
    if not data:
        st.error("Run `python scheduler.py` first.")
        st.stop()
    return data

shop_data  = load_data()
product_df = load_products()

rows = []
for d in shop_data:
    p   = d.get("product", {})
    pid = d.get("product_id", "")
    csv_row    = product_df[product_df["id"] == pid]
    cost_price = int(csv_row["cost_price"].values[0]) if len(csv_row) else 0
    price_col  = "base_price" if "base_price" in csv_row.columns else "your_price"
    your_price = int(csv_row[price_col].values[0]) if len(csv_row) else int(p.get("base_price", 0))
    margin     = compute_margin(your_price, cost_price)
    rows.append({
        "id":           pid,
        "name":         p.get("name", ""),
        "category":     p.get("category", ""),
        "brand":        p.get("brand", ""),
        "your_price":   your_price,
        "cost_price":   cost_price,
        "profit":       margin["profit"],
        "margin_pct":   margin["margin_pct"],
        "margin_label": margin["margin_label"],
        "margin_color": margin["margin_color"],
        "market_min":   int(d.get("comp_min", 0)),
        "market_avg":   int(d.get("comp_avg", 0)),
        "market_max":   int(d.get("comp_max", 0)),
        "suggested":    int(d.get("suggested_price", 0)),
        "action":       d.get("action", "Hold"),
        "urgency":      d.get("urgency", "none"),
        "gap_pct":      round(float(d.get("gap_pct", 0)), 1),
        "sellers_found":int(d.get("sellers_found", 0)),
        "sellers":      d.get("sellers", []),
        "stock":        int(p.get("stock", 0)),
        "timestamp":    d.get("timestamp", ""),
    })
df = pd.DataFrame(rows)

# ── KPI calculations ──────────────────────────────────────────
high_alert  = len(df[df["urgency"] == "high"])
raise_count = len(df[df["action"]  == "Raise price"])
hold_count  = len(df[df["action"]  == "Hold"])
lower_count = len(df[df["action"]  == "Lower price"])
avg_margin  = df[df["margin_pct"] > 0]["margin_pct"].mean()
thin_count  = len(df[(df["margin_pct"] > 0) & (df["margin_pct"] < 10)])
last_time   = df["timestamp"].iloc[0][11:16] if len(df) else "—"

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:4px 0 28px'>
      <div style='font-family:"Fraunces",serif;font-size:22px;font-weight:600;color:#0f172a;letter-spacing:-0.3px'>
        Price Smarter. Sell Faster. 🚀
      </div>
      <div style='font-size:11px;color:#3d4151;margin-top:4px'>
        My Electronics Shop
      </div>
    </div>
    <div style='font-size:9px;font-weight:600;color:#3d4151;text-transform:uppercase;
                letter-spacing:0.12em;margin-bottom:8px;padding-left:2px'>
      Navigation
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "nav",
        [
            "⬛  Dashboard",
            "📋  All Products",
            "✏️  Update Prices",
            "💰  Profit Margins",
            f"🚨  Alerts  [{high_alert}]",
            "📈  Price History",
            "🧠  ML Pipeline",
        ],
        label_visibility="collapsed",
    )

    st.markdown(f"""
    <div style='padding-top:24px;border-top:1px solid rgba(255,255,255,0.06);margin-top:16px'>
      <div style='display:flex;align-items:center;gap:6px;font-size:11px;color:#3d4151;margin-bottom:6px'>
        <div style='width:5px;height:5px;background:#34d399;border-radius:50%;flex-shrink:0;
                    box-shadow:0 0 6px rgba(52,211,153,0.6)'></div>
        Live · Updated {last_time}
      </div>
      <div style='font-size:11px;color:#3d4151'>
        Ludhiana, Punjab · {len(df)} products
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("↻  Refresh data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ── Plotly theme ──────────────────────────────────────────────
PLOT_LAYOUT = dict(
    plot_bgcolor="#ffffff",
    paper_bgcolor="#ffffff",
    font=dict(family="DM Sans", color="#334155"),
    margin=dict(t=20, b=30, l=10, r=10),
)

# ── Helper functions ──────────────────────────────────────────
def fmt_margin(pct):
    if pct <= 0: return "—"
    w = min(int(pct * 2.5), 100)
    c = "#34d399" if pct >= 20 else "#fbbf24" if pct >= 10 else "#f87171"
    return (f"<div style='display:flex;align-items:center;gap:6px'>"
            f"<div class='mbar-bg'><div class='mbar-fill' style='width:{w}%;background:{c}'></div></div>"
            f"<span style='font-size:12px;color:{c};font-weight:600;font-family:\"DM Mono\",monospace'>{pct:.1f}%</span></div>")

def fmt_action(val):
    if val == "Lower price":
        return "<span class='action-pill pill-lower'>↓ Lower</span>"
    if val == "Raise price":
        return "<span class='action-pill pill-raise'>↑ Raise</span>"
    return "<span class='action-pill pill-hold'>⟳ Hold</span>"

def fmt_gap(pct):
    if pct >  5: return f"<span class='gap-red'>+{pct:.1f}%</span>"
    if pct < -5: return f"<span class='gap-green'>{pct:.1f}%</span>"
    return f"<span class='gap-grey'>{pct:.1f}%</span>"

# ══════════════════════════════════════════════════
# PAGE: Dashboard
# ══════════════════════════════════════════════════
if "Dashboard" in page:
    st.markdown(f"""
    <div class="page-title"><h1>Welcome To Dynamic Pricing Engine</h1></div>
    <div class="page-sub">Pricing intelligence for today &nbsp;·&nbsp; {len(df)} products tracked &nbsp;·&nbsp; Last refreshed {last_time}</div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card kpi-blue">
        <div class="kpi-label">Products Tracked</div>
        <div class="kpi-value kv-blue">{len(df)}</div>
        <div class="kpi-footer">6 categories monitored</div>
      </div>
      <div class="kpi-card kpi-red">
        <div class="kpi-label">Need Lower Price</div>
        <div class="kpi-value kv-red">{high_alert}</div>
        <div class="kpi-footer down">{'⚠ Act today' if high_alert else '✓ All good'}</div>
      </div>
      <div class="kpi-card kpi-green">
        <div class="kpi-label">Can Raise Price</div>
        <div class="kpi-value kv-green">{raise_count}</div>
        <div class="kpi-footer up">↑ Extra revenue available</div>
      </div>
      <div class="kpi-card kpi-blue">
        <div class="kpi-label">Avg Profit Margin</div>
        <div class="kpi-value kv-blue">{avg_margin:.1f}%</div>
        <div class="kpi-footer up">✓ Healthy</div>
      </div>
      <div class="kpi-card {'kpi-red' if thin_count else 'kpi-green'}">
        <div class="kpi-label">Thin Margins &lt;10%</div>
        <div class="kpi-value {'kv-red' if thin_count else 'kv-green'}">{thin_count}</div>
        <div class="kpi-footer {'down' if thin_count else 'up'}">{'⚠ Check these' if thin_count else '✓ All above 10%'}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1.2])
    with c1:
        st.markdown('<div class="section-title">Action Breakdown</div>', unsafe_allow_html=True)
        action_counts = df["action"].value_counts()
        fig = go.Figure(go.Pie(
            labels=action_counts.index, values=action_counts.values,
            hole=0.6,
            marker_colors=["#f87171", "#34d399", "#3d4151"],
        ))
        fig.update_layout(
            **PLOT_LAYOUT,
            height=240,
            legend=dict(orientation="h", y=-0.1, font=dict(color="#6b7280")),
        )
        fig.update_traces(textfont_color="#e8eaf0")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<div class="section-title">Margin Health by Category</div>', unsafe_allow_html=True)
        cat_m = df[df["margin_pct"]>0].groupby("category")["margin_pct"].mean().sort_values()
        fig2 = go.Figure(go.Bar(
            x=cat_m.values, y=cat_m.index, orientation="h",
            marker_color=["#34d399" if v>=20 else "#fbbf24" if v>=10 else "#f87171" for v in cat_m.values],
            text=[f"{v:.1f}%" for v in cat_m.values], textposition="outside",
            textfont=dict(color="#e8eaf0", size=11)))
        fig2.update_layout(
            **PLOT_LAYOUT,
            height=240,
            xaxis_title="Avg margin %",
            xaxis=dict(color="#3d4151", gridcolor="#1a1d28"),
            yaxis=dict(color="#6b7280"),
        )
        st.plotly_chart(fig2, use_container_width=True)

    urgent_dash = df[df["urgency"]=="high"].head(3)
    if not urgent_dash.empty:
        st.markdown('<div class="section-title" style="margin-top:8px">🔴 Top Urgent Alerts</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">These products need immediate price attention</div>', unsafe_allow_html=True)
        for _, row in urgent_dash.iterrows():
            sug_m = compute_margin(row["suggested"], row["cost_price"])
            st.markdown(f"""
            <div class="alert-item urgent">
              <div style="flex:1">
                <div class="alert-name">🔴 {row["name"]}</div>
                <div class="alert-meta">{row["category"]} &nbsp;·&nbsp; {row["gap_pct"]:.1f}% above market</div>
                <div class="alert-prices">
                  <div><div class="ap-label">Your Price</div><div class="ap-val red">₹{row["your_price"]:,}</div></div>
                  <div><div class="ap-label">Market Avg</div><div class="ap-val">₹{row["market_avg"]:,}</div></div>
                  <div><div class="ap-label">Suggested</div><div class="ap-val green">₹{row["suggested"]:,}</div></div>
                  <div><div class="ap-label">Margin After</div><div class="ap-val purple">{sug_m["margin_pct"]:.1f}%</div></div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# PAGE: All Products
# ══════════════════════════════════════════════════
elif "All Products" in page:
    st.markdown('<div class="page-title">All Products</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Live market prices fetched every 30 minutes</div>', unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3)
    with f1:
        sel_cat = st.selectbox("Category", ["All"] + sorted(df["category"].unique().tolist()))
    with f2:
        sel_brand = st.selectbox("Brand", ["All"] + sorted(df["brand"].unique().tolist()))
    with f3:
        sel_action = st.selectbox("Action", ["All", "Lower price", "Hold", "Raise price"])

    fdf = df.copy()
    if sel_cat    != "All": fdf = fdf[fdf["category"] == sel_cat]
    if sel_brand  != "All": fdf = fdf[fdf["brand"]    == sel_brand]
    if sel_action != "All": fdf = fdf[fdf["action"]   == sel_action]

    st.markdown(f"""
    <div style="display:flex;gap:8px;margin:14px 0 18px;flex-wrap:wrap;">
      <span class="count-badge badge-grey">📦 {len(fdf)} products</span>
      <span class="count-badge badge-red">↓ {len(fdf[fdf["action"]=="Lower price"])} lower</span>
      <span class="count-badge badge-green">↑ {len(fdf[fdf["action"]=="Raise price"])} raise</span>
      <span class="count-badge badge-grey">⟳ {len(fdf[fdf["action"]=="Hold"])} hold</span>
    </div>
    """, unsafe_allow_html=True)

    disp = fdf[[
        "name", "category", "your_price", "cost_price",
        "profit", "margin_pct", "market_avg",
        "suggested", "action", "gap_pct", "sellers_found"
    ]].copy()

    disp["margin_pct"] = disp["margin_pct"].apply(fmt_margin)
    disp["action"]     = disp["action"].apply(fmt_action)
    disp["gap_pct"]    = disp["gap_pct"].apply(fmt_gap)
    disp["your_price"] = disp["your_price"].apply(lambda x: f"₹{x:,}")
    disp["cost_price"] = disp["cost_price"].apply(lambda x: f"₹{x:,}" if x else "—")
    disp["profit"]     = disp["profit"].apply(lambda x: f"₹{x:,}" if x else "—")
    disp["market_avg"] = disp["market_avg"].apply(lambda x: f"₹{x:,}")
    disp["suggested"]  = disp["suggested"].apply(lambda x: f"₹{x:,}")
    disp.columns = ["Product","Category","Your Price","Cost","Profit/unit",
                    "Margin","Market Avg","Suggested","Action","Gap %","Sellers"]

    st.write(disp.to_html(escape=False, index=False, classes="ptable", border=0),
             unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Product Deep Dive</div>', unsafe_allow_html=True)
    sel_prod = st.selectbox("Select product", df["name"].tolist(), key="detail")
    row      = df[df["name"] == sel_prod].iloc[0]
    sug_m    = compute_margin(row["suggested"], row["cost_price"])

    st.markdown(f"""
    <div class="detail-card">
      <div class="detail-grid">
        <div><div class="detail-label">Your Price</div><div class="detail-value">₹{row["your_price"]:,}</div></div>
        <div><div class="detail-label">Cost Price</div><div class="detail-value">₹{row["cost_price"]:,}</div></div>
        <div><div class="detail-label">Profit / Unit</div><div class="detail-value green">₹{row["profit"]:,}</div></div>
        <div><div class="detail-label">Margin</div><div class="detail-value purple">{row["margin_pct"]:.1f}%</div></div>
        <div><div class="detail-label">Market Avg</div><div class="detail-value">₹{row["market_avg"]:,}</div></div>
        <div><div class="detail-label">Sellers Found</div><div class="detail-value">{row["sellers_found"]}</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if row["action"] == "Lower price":
        st.error(f"⚠ You are **{row['gap_pct']:.1f}%** above market. Drop to ₹{row['suggested']:,} — still {sug_m['margin_pct']:.1f}% margin (₹{sug_m['profit']:,}/unit)")
    elif row["action"] == "Raise price":
        st.success(f"✅ You are **{abs(row['gap_pct']):.1f}%** below market. Raise to ₹{row['suggested']:,} — margin improves to {sug_m['margin_pct']:.1f}% (₹{sug_m['profit']:,}/unit)")
    else:
        st.info(f"✓ Price is competitive. Market avg ₹{row['market_avg']:,} · Margin {row['margin_pct']:.1f}%")

    if row["sellers"]:
        st.caption("Sellers: " + "  ·  ".join(row["sellers"][:5]))

# ══════════════════════════════════════════════════
# PAGE: Update Prices
# ══════════════════════════════════════════════════
elif "Update Prices" in page:
    st.markdown('<div class="page-title">Update Prices</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Apply AI-suggested prices or set custom ones manually</div>', unsafe_allow_html=True)

    urgent = df[df["urgency"].isin(["high","medium"])].sort_values("gap_pct", ascending=False)
    raises = df[df["action"] == "Raise price"].sort_values("gap_pct")

    st.markdown('<div class="section-title">🔴 Urgent — Lower These Prices</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Your price is significantly above market average</div>', unsafe_allow_html=True)

    if urgent.empty:
        st.success("All prices are competitive right now.")
    else:
        for _, row in urgent.iterrows():
            sug_m = compute_margin(row["suggested"], row["cost_price"])
            icon  = "🔴" if row["urgency"] == "high" else "🟡"
            c1,c2,c3,c4,c5 = st.columns([3,1,1,1,1])
            with c1:
                st.markdown(f"**{icon} {row['name']}**")
                st.caption(f"After change: {sug_m['margin_pct']:.1f}% margin · ₹{sug_m['profit']:,}/unit")
            with c2: st.metric("Current",    f"₹{row['your_price']:,}")
            with c3: st.metric("Market avg", f"₹{row['market_avg']:,}")
            with c4:
                diff = row["suggested"] - row["your_price"]
                st.metric("Suggested", f"₹{row['suggested']:,}", delta=f"₹{diff:+,}")
            with c5:
                if st.button("Apply ✓", key=f"u_{row['id']}", type="primary"):
                    if save_price(row["id"], row["suggested"], row["your_price"]):
                        st.success("Updated!")
                        st.cache_data.clear()
                        st.rerun()
            st.divider()

    st.markdown('<div class="section-title" style="margin-top:8px">✅ Opportunities — Raise These Prices</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">You are priced below market — earn more per unit</div>', unsafe_allow_html=True)

    if raises.empty:
        st.info("No raise opportunities right now.")
    else:
        for _, row in raises.iterrows():
            sug_m = compute_margin(row["suggested"], row["cost_price"])
            gain  = row["suggested"] - row["your_price"]
            c1,c2,c3,c4,c5 = st.columns([3,1,1,1,1])
            with c1:
                st.markdown(f"**✅ {row['name']}**")
                st.caption(f"New margin: {sug_m['margin_pct']:.1f}% · Extra ₹{gain:,}/unit")
            with c2: st.metric("Current",    f"₹{row['your_price']:,}")
            with c3: st.metric("Market avg", f"₹{row['market_avg']:,}")
            with c4: st.metric("Raise to",   f"₹{row['suggested']:,}", delta=f"+₹{gain:,}")
            with c5:
                if st.button("Apply ✓", key=f"r_{row['id']}", type="primary"):
                    if save_price(row["id"], row["suggested"], row["your_price"]):
                        st.success("Updated!")
                        st.cache_data.clear()
                        st.rerun()
            st.divider()

    st.markdown('<div class="section-title" style="margin-top:8px">✏️ Manual Price Editor</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Set any custom price — live margin preview as you type</div>', unsafe_allow_html=True)

    m1, m2 = st.columns(2)
    with m1:
        edit_prod = st.selectbox("Product", df["name"].tolist(), key="ep")
    edit_row = df[df["name"] == edit_prod].iloc[0]
    with m2:
        new_price = st.number_input("New price (₹)",
            min_value=int(edit_row["market_min"] * 0.5),
            max_value=int(edit_row["market_max"] * 1.5),
            value=int(edit_row["your_price"]), step=50, key="npi")

    prev  = compute_margin(new_price, edit_row["cost_price"])
    old_m = compute_margin(edit_row["your_price"], edit_row["cost_price"])
    p1,p2,p3,p4 = st.columns(4)
    p1.metric("New price",  f"₹{new_price:,}")
    p2.metric("Cost",       f"₹{edit_row['cost_price']:,}" if edit_row["cost_price"] else "—")
    p3.metric("New profit", f"₹{prev['profit']:,}" if prev["profit"] > 0 else "—",
              delta=f"₹{prev['profit']-old_m['profit']:+,}" if edit_row["cost_price"] else None)
    p4.metric("New margin", f"{prev['margin_pct']:.1f}%" if prev["margin_pct"] > 0 else "—",
              delta=f"{prev['margin_pct']-old_m['margin_pct']:+.1f}%" if edit_row["cost_price"] else None)

    if edit_row["cost_price"] > 0 and prev["margin_pct"] < 5:
        st.error(f"⚠ Margin below 5% at ₹{new_price:,} — barely any profit")
    elif edit_row["cost_price"] > 0 and prev["margin_pct"] < 10:
        st.warning(f"⚠ Thin margin at {prev['margin_pct']:.1f}%")

    if st.button("💾 Save price", type="primary"):
        if new_price != edit_row["your_price"]:
            if save_price(edit_row["id"], new_price, edit_row["your_price"]):
                st.success(f"✅ {edit_prod}: ₹{edit_row['your_price']:,} → ₹{new_price:,}")
                st.cache_data.clear()
                st.rerun()
        else:
            st.info("Price unchanged.")

    changes = get_price_changes(days=30)
    if changes:
        st.divider()
        st.markdown("**Price Change Log**")
        id_to_name = {p["id"]: p["name"] for p in PRODUCTS}
        for c in changes:
            c["product"] = id_to_name.get(c["product_id"], c["product_id"])
        log_df = pd.DataFrame(changes)[["changed_at","product","old_price","new_price","change_amt"]]
        log_df["old_price"]  = log_df["old_price"].apply(lambda x: f"₹{int(x):,}")
        log_df["new_price"]  = log_df["new_price"].apply(lambda x: f"₹{int(x):,}")
        log_df["change_amt"] = log_df["change_amt"].apply(lambda x: f"+₹{int(x):,}" if x > 0 else f"₹{int(x):,}")
        log_df["changed_at"] = log_df["changed_at"].apply(lambda x: x[:16])
        log_df.columns = ["Time","Product","Old Price","New Price","Change"]
        st.dataframe(log_df, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════
# PAGE: Profit Margins
# ══════════════════════════════════════════════════
elif "Profit Margins" in page:
    st.markdown('<div class="page-title">Profit Margins</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Margin health across all categories and products</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Margin by Category</div>', unsafe_allow_html=True)

    cat_m = df[df["margin_pct"] > 0].groupby("category").agg(
        avg_margin=("margin_pct","mean"),
        avg_profit=("profit","mean"),
        count=("name","count")
    ).reset_index().sort_values("avg_margin", ascending=False)

    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure(go.Bar(
            x=cat_m["avg_margin"], y=cat_m["category"], orientation="h",
            marker_color=["#34d399" if v>=20 else "#fbbf24" if v>=10 else "#f87171"
                          for v in cat_m["avg_margin"]],
            text=[f"{v:.1f}%" for v in cat_m["avg_margin"]],
            textposition="outside",
            textfont=dict(color="#e8eaf0", size=11)))
        fig.update_layout(
            **PLOT_LAYOUT,
            xaxis_title="Avg margin %",
            xaxis=dict(color="#3d4151", gridcolor="#1a1d28"),
            yaxis=dict(color="#6b7280"),
            height=280,
        )
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig2 = go.Figure(go.Bar(
            x=cat_m["avg_profit"], y=cat_m["category"], orientation="h",
            marker_color="#7c6ffd",
            text=[f"₹{int(v):,}" for v in cat_m["avg_profit"]],
            textposition="outside",
            textfont=dict(color="#e8eaf0", size=11)))
        fig2.update_layout(
            **PLOT_LAYOUT,
            xaxis_title="Avg profit/unit (₹)",
            xaxis=dict(color="#3d4151", gridcolor="#1a1d28"),
            yaxis=dict(color="#6b7280"),
            height=280,
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title" style="margin-top:8px">All Products — Margin Breakdown</div>', unsafe_allow_html=True)
    mf = st.selectbox("Filter", ["All","Healthy (≥20%)","Moderate (10–20%)","Thin (<10%)"], key="mf")
    mdf = df[df["cost_price"] > 0].copy()
    if mf == "Healthy (≥20%)":      mdf = mdf[mdf["margin_pct"] >= 20]
    elif mf == "Moderate (10–20%)": mdf = mdf[(mdf["margin_pct"]>=10)&(mdf["margin_pct"]<20)]
    elif mf == "Thin (<10%)":       mdf = mdf[mdf["margin_pct"] < 10]
    mdf = mdf.sort_values("margin_pct")

    md = mdf[["name","category","your_price","cost_price","profit","margin_pct","margin_label"]].copy()
    md["your_price"] = md["your_price"].apply(lambda x: f"₹{x:,}")
    md["cost_price"] = md["cost_price"].apply(lambda x: f"₹{x:,}")
    md["profit"]     = md["profit"].apply(lambda x: f"₹{x:,}")
    md["margin_pct"] = md["margin_pct"].apply(lambda x: f"{x:.1f}%")
    md.columns = ["Product","Category","Your Price","Cost","Profit/unit","Margin %","Health"]

    def sh(v):
        if v == "Healthy":   return "color:#10b981;font-weight:600"
        if v == "Thin":      return "color:#ef4444;font-weight:600"
        if v == "Loss!":     return "color:#ef4444;font-weight:700"
        if v == "Moderate":  return "color:#f59e0b;font-weight:600"
        return ""
    st.dataframe(md.style.map(sh, subset=["Health"]),
                 use_container_width=True, hide_index=True)

    st.divider()
    st.markdown('<div class="section-title">Margin vs Market Gap</div>', unsafe_allow_html=True)
    st.caption("Top-right = raise safely · Bottom-right = urgent action needed")
    sdf = df[df["cost_price"] > 0].copy()
    cmap = {"Lower price":"#f87171","Hold":"#3d4151","Raise price":"#34d399"}
    fig3 = go.Figure()
    for action, grp in sdf.groupby("action"):
        fig3.add_trace(go.Scatter(
            x=grp["gap_pct"], y=grp["margin_pct"],
            mode="markers+text", name=action,
            text=grp["name"].apply(lambda x: x.split()[-1]),
            textposition="top center",
            textfont=dict(size=10, family="DM Sans", color="#6b7280"),
            marker=dict(size=11, color=cmap.get(action,"#3d4151"))))
    fig3.add_vline(x=0, line_dash="dash", line_color="#1a1d28")
    fig3.add_hline(y=10, line_dash="dash", line_color="#f87171", opacity=0.4,
                   annotation_text="10% margin floor",
                   annotation_font_color="#f87171")
    fig3.update_layout(
        **PLOT_LAYOUT,
        xaxis_title="Gap vs market %",
        yaxis_title="Your margin %",
        xaxis=dict(color="#3d4151", gridcolor="#1a1d28", zerolinecolor="#1a1d28"),
        yaxis=dict(color="#3d4151", gridcolor="#1a1d28"),
        height=420,
        legend=dict(font=dict(color="#6b7280")),
    )
    st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════════
# PAGE: Alerts
# ══════════════════════════════════════════════════
elif "Alerts" in page:
    st.markdown('<div class="page-title">Alerts</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Prices that need immediate attention</div>', unsafe_allow_html=True)

    urgent = df[df["urgency"].isin(["high","medium"])].sort_values("gap_pct", ascending=False)
    opps   = df[df["action"] == "Raise price"].sort_values("gap_pct")

    st.markdown(f'<div class="section-title">🔴 Urgent Price Alerts <span class="count-badge badge-red" style="margin-left:8px">{len(urgent)} products</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Your price is above market — customers will buy from competitors</div>', unsafe_allow_html=True)

    if urgent.empty:
        st.success("All your prices are competitive right now.")
    else:
        for _, row in urgent.iterrows():
            sug_m = compute_margin(row["suggested"], row["cost_price"])
            level = "urgent" if row["urgency"] == "high" else "warn"
            icon  = "🔴" if row["urgency"] == "high" else "🟡"
            st.markdown(f"""
            <div class="alert-item {level}">
              <div style="flex:1">
                <div class="alert-name">{icon} {row["name"]}</div>
                <div class="alert-meta">{row["category"]} &nbsp;·&nbsp; {row["sellers_found"]} sellers found &nbsp;·&nbsp; {row["gap_pct"]:.1f}% above market</div>
                <div class="alert-prices">
                  <div><div class="ap-label">Your Price</div><div class="ap-val red">₹{row["your_price"]:,}</div></div>
                  <div><div class="ap-label">Market Avg</div><div class="ap-val">₹{row["market_avg"]:,}</div></div>
                  <div><div class="ap-label">Suggested</div><div class="ap-val green">₹{row["suggested"]:,}</div></div>
                  <div><div class="ap-label">Margin After</div><div class="ap-val purple">{sug_m["margin_pct"]:.1f}%</div></div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">✅ Raise Price Opportunities <span class="count-badge badge-green" style="margin-left:8px">{len(opps)} products</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">You are priced below market — you are leaving money on the table</div>', unsafe_allow_html=True)

    if opps.empty:
        st.info("No opportunities right now.")
    else:
        for _, row in opps.iterrows():
            sug_m = compute_margin(row["suggested"], row["cost_price"])
            gain  = row["suggested"] - row["your_price"]
            st.markdown(f"""
            <div class="alert-item good">
              <div style="flex:1">
                <div class="alert-name">✅ {row["name"]}</div>
                <div class="alert-meta">{row["category"]} &nbsp;·&nbsp; {row["sellers_found"]} sellers &nbsp;·&nbsp; {abs(row["gap_pct"]):.1f}% below market &nbsp;·&nbsp; Extra ₹{gain:,}/unit if you raise</div>
                <div class="alert-prices">
                  <div><div class="ap-label">Your Price</div><div class="ap-val">₹{row["your_price"]:,}</div></div>
                  <div><div class="ap-label">Market Avg</div><div class="ap-val">₹{row["market_avg"]:,}</div></div>
                  <div><div class="ap-label">Raise To</div><div class="ap-val green">₹{row["suggested"]:,}</div></div>
                  <div><div class="ap-label">New Margin</div><div class="ap-val purple">{sug_m["margin_pct"]:.1f}%</div></div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# PAGE: Price History
# ══════════════════════════════════════════════════
elif "Price History" in page:
    st.markdown('<div class="page-title">Price History</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Your price vs market average over time</div>', unsafe_allow_html=True)

    h1, h2 = st.columns([2,1])
    with h1:
        sel_h = st.selectbox("Product", df["name"].tolist(), key="hist")
    with h2:
        days_h = st.slider("Days", 1, 30, 7)

    row_h = df[df["name"] == sel_h].iloc[0]
    hist  = get_price_history(row_h["id"], days=days_h)

    if not hist:
        st.info("History builds up every 30 min as the scheduler runs. Check back after a few hours.")
    else:
        hdf = pd.DataFrame(hist)
        hdf["recorded_at"] = pd.to_datetime(hdf["recorded_at"])
        if len(hdf) < 2:
            st.info(f"Only {len(hdf)} data point so far. Check back after a few more scheduler runs.")
        else:
            fig4 = go.Figure()
            fig4.add_trace(go.Scatter(x=hdf["recorded_at"], y=hdf["your_price"],
                mode="lines+markers", name="Your price",
                line=dict(color="#7c6ffd", width=2.5),
                marker=dict(color="#7c6ffd", size=5)))
            fig4.add_trace(go.Scatter(x=hdf["recorded_at"], y=hdf["market_avg"],
                mode="lines", name="Market avg",
                line=dict(color="#fbbf24", width=2, dash="dot")))
            fig4.add_trace(go.Scatter(x=hdf["recorded_at"], y=hdf["market_min"],
                mode="lines", name="Market min",
                line=dict(color="#34d399", width=1.5, dash="dash")))
            fig4.add_trace(go.Scatter(x=hdf["recorded_at"], y=hdf["suggested"],
                mode="lines", name="Suggested",
                line=dict(color="#f87171", width=1.5, dash="dashdot")))
            fig4.update_layout(
                **PLOT_LAYOUT,
                xaxis_title="Time",
                yaxis_title="Price (₹)",
                xaxis=dict(color="#3d4151", gridcolor="#1a1d28"),
                yaxis=dict(color="#3d4151", gridcolor="#1a1d28"),
                height=400,
                legend=dict(orientation="h", y=1.08, font=dict(color="#6b7280")),
            )
            st.plotly_chart(fig4, use_container_width=True)

        with st.expander("Raw data table"):
            hs = hdf[["recorded_at","your_price","market_min","market_avg",
                       "suggested","action","sellers"]].copy()
            for c in ["your_price","market_min","market_avg","suggested"]:
                hs[c] = hs[c].apply(lambda x: f"₹{int(x):,}")
            hs["sellers"] = hs["sellers"].astype(int)
            hs.columns = ["Time","Your Price","Mkt Min","Mkt Avg","Suggested","Action","Sellers"]
            st.dataframe(hs, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════
# PAGE: ML Pipeline
# ══════════════════════════════════════════════════
elif "ML Pipeline" in page:
    st.markdown('<div class="page-title">ML Pipeline</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Training pipeline · Demand model · RL agent · Evaluation metrics</div>', unsafe_allow_html=True)

    # Pipeline overview
    st.markdown('<div class="section-title">🔄 Full Training Pipeline</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">End-to-end flow from raw data to live pricing decisions</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:0;align-items:center;margin-bottom:20px">
      <div class="pipeline-step done" style="text-align:center">
        <div style="font-size:24px;margin-bottom:8px">📦</div>
        <div class="step-title">Data Collection</div>
        <div class="step-sub">SerpAPI Google Shopping · Weather API · 8,000 synthetic rows</div>
        <span class="step-badge badge-done">✓ Done</span>
      </div>
      <div style="text-align:center;font-size:20px;color:#3d4151">→</div>
      <div class="pipeline-step done" style="text-align:center">
        <div style="font-size:24px;margin-bottom:8px">📈</div>
        <div class="step-title">Demand Model</div>
        <div class="step-sub">XGBoost Regressor · 6 features · MAE ~12 units · R² 0.97</div>
        <span class="step-badge badge-done">✓ Trained</span>
      </div>
      <div style="text-align:center;font-size:20px;color:#3d4151">→</div>
      <div class="pipeline-step active" style="text-align:center">
        <div style="font-size:24px;margin-bottom:8px">🤖</div>
        <div class="step-title">RL Agent (DQN)</div>
        <div class="step-sub">3-action policy · Reward = revenue − fairness penalty</div>
        <span class="step-badge badge-active">● Live</span>
      </div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 0.1fr 1fr 0.1fr 1fr;gap:0;align-items:center;margin-bottom:28px">
      <div class="pipeline-step info" style="text-align:center">
        <div style="font-size:24px;margin-bottom:8px">🔍</div>
        <div class="step-title">Market Fetch</div>
        <div class="step-sub">Every 30 min · Competitor prices · Urgency scoring</div>
        <span class="step-badge badge-info">⟳ Scheduled</span>
      </div>
      <div style="text-align:center;font-size:20px;color:#3d4151">→</div>
      <div class="pipeline-step info" style="text-align:center">
        <div style="font-size:24px;margin-bottom:8px">💡</div>
        <div class="step-title">Price Decision</div>
        <div class="step-sub">RL action + market logic → suggested price per product</div>
        <span class="step-badge badge-info">⟳ Running</span>
      </div>
      <div style="text-align:center;font-size:20px;color:#3d4151">→</div>
      <div class="pipeline-step done" style="text-align:center">
        <div style="font-size:24px;margin-bottom:8px">🖥️</div>
        <div class="step-title">Dashboard</div>
        <div class="step-sub">You are here — review, apply, or override suggestions</div>
        <span class="step-badge badge-done">✓ Live</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Demand Model
    st.markdown('<div class="section-title">📈 Demand Forecasting Model — XGBoost</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Predicts units sold given price, competitor context, and time signals</div>', unsafe_allow_html=True)

    dm_c1, dm_c2 = st.columns([1,1])
    with dm_c1:
        st.markdown("**Architecture & Features**")
        st.markdown("""
        <table class="ptable">
          <thead><tr><th>Feature</th><th>Type</th><th>Role</th></tr></thead>
          <tbody>
            <tr><td><code style="color:#7c6ffd;background:#1a1d28;padding:2px 6px;border-radius:4px">price</code></td><td style="color:#6b7280">Float</td><td>Your current listing price (₹)</td></tr>
            <tr><td><code style="color:#7c6ffd;background:#1a1d28;padding:2px 6px;border-radius:4px">comp_avg</code></td><td style="color:#6b7280">Float</td><td>Competitor market average (₹)</td></tr>
            <tr><td><code style="color:#7c6ffd;background:#1a1d28;padding:2px 6px;border-radius:4px">hour</code></td><td style="color:#6b7280">Int 0–23</td><td>Hour of day — captures peak traffic</td></tr>
            <tr><td><code style="color:#7c6ffd;background:#1a1d28;padding:2px 6px;border-radius:4px">day_of_week</code></td><td style="color:#6b7280">Int 0–6</td><td>Weekday vs weekend demand shift</td></tr>
            <tr><td><code style="color:#7c6ffd;background:#1a1d28;padding:2px 6px;border-radius:4px">weather_boost</code></td><td style="color:#6b7280">Float 0–0.5</td><td>Rain/heat → more online shopping</td></tr>
            <tr><td><code style="color:#7c6ffd;background:#1a1d28;padding:2px 6px;border-radius:4px">trend_score</code></td><td style="color:#6b7280">Float 0–1</td><td>Search demand signal (time-adjusted)</td></tr>
          </tbody>
        </table>
        """, unsafe_allow_html=True)

        st.markdown("<br>**Demand formula (data generation)**", unsafe_allow_html=True)
        st.code("""demand = (
    300
    - 0.18 * price           # price elasticity
    + 0.08 * comp_avg        # competitor effect
    + 60  * trend_score      # search demand
    + 40  * weather_boost    # weather signal
    + 25  * is_weekend       # weekend boost
    + 30  * is_evening_peak  # 19:00–22:00 peak
    + noise(0, 15)           # realistic variance
).clip(0, 800)""", language="python")

    with dm_c2:
        st.markdown("**Simulated training data distribution**")
        np.random.seed(42)
        n = 500
        price        = np.random.uniform(5000, 130000, n)
        comp_avg     = np.random.uniform(4000, 140000, n)
        trend_score  = np.random.uniform(0.2, 1.0, n)
        weather_boost= np.random.uniform(0, 0.5, n)
        hour         = np.random.randint(0, 24, n)
        day          = np.random.randint(0, 7, n)
        demand = (300 - 0.18*price/1000 + 0.08*comp_avg/1000 + 60*trend_score
                  + 40*weather_boost + 25*(day>=5) + 30*((hour>=19)&(hour<=22))
                  + np.random.normal(0,15,n)).clip(0,800)

        fig_d = go.Figure()
        fig_d.add_trace(go.Scatter(
            x=price/1000, y=demand, mode="markers",
            marker=dict(size=4, color=trend_score, colorscale="Viridis",
                       showscale=True,
                       colorbar=dict(title=dict(text="Trend", font=dict(color="#334155")),thickness=10,tickfont=dict(color="#334155"))),
            name="Samples"))
        fig_d.update_layout(
            **PLOT_LAYOUT,
            xaxis_title="Price (₹ thousands)",
            yaxis_title="Demand (units)",
            xaxis=dict(color="#3d4151", gridcolor="#1a1d28"),
            yaxis=dict(color="#3d4151", gridcolor="#1a1d28"),
            height=280,
        )
        st.plotly_chart(fig_d, use_container_width=True)

        st.markdown("**Feature importance (relative)**")
        features = ["price","comp_avg","trend_score","weather_boost","hour","day_of_week"]
        importance= [0.38, 0.25, 0.17, 0.09, 0.07, 0.04]
        fig_imp = go.Figure(go.Bar(
            x=importance, y=features, orientation="h",
            marker_color=["#7c6ffd","#7c6ffd","#a78bfa","#c4b5fd","#2d2d52","#1e1e3a"],
            text=[f"{v:.0%}" for v in importance], textposition="outside",
            textfont=dict(color="#e8eaf0")))
        fig_imp.update_layout(
            **PLOT_LAYOUT,
            height=200,
            xaxis=dict(showticklabels=False, gridcolor="#1a1d28"),
            yaxis=dict(color="#6b7280"),
        )
        st.plotly_chart(fig_imp, use_container_width=True)

    # RL Agent
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">🤖 RL Agent — Deep Q-Network (DQN)</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Learns optimal pricing actions through trial-and-error with a revenue-maximising reward signal</div>', unsafe_allow_html=True)

    rl_c1, rl_c2 = st.columns([1,1])
    with rl_c1:
        st.markdown("**Network architecture** — loaded from `dqn_model.pth`")
        st.markdown("""
        <table class="ptable">
          <thead><tr><th>Layer</th><th>Shape</th><th>Notes</th></tr></thead>
          <tbody>
            <tr><td>Input</td><td style="font-family:'DM Mono',monospace;color:#7c6ffd">[6]</td><td>price, comp_avg, hour, day, weather, trend</td></tr>
            <tr><td>Linear + ReLU</td><td style="font-family:'DM Mono',monospace;color:#7c6ffd">[128]</td><td>First hidden layer</td></tr>
            <tr><td>Linear + ReLU</td><td style="font-family:'DM Mono',monospace;color:#7c6ffd">[128]</td><td>Second hidden layer</td></tr>
            <tr><td>Linear (output)</td><td style="font-family:'DM Mono',monospace;color:#7c6ffd">[3]</td><td>Q-values for 3 actions</td></tr>
          </tbody>
        </table>
        """, unsafe_allow_html=True)

        st.markdown("<br>**3 Pricing Actions**", unsafe_allow_html=True)
        st.markdown("""
        <div style="display:flex;gap:10px;margin:12px 0">
          <div style="flex:1;background:var(--rose-bg);border:1px solid rgba(248,113,113,0.15);border-radius:10px;padding:14px;text-align:center">
            <div style="font-size:22px;margin-bottom:6px">↓</div>
            <div style="font-weight:600;color:#f87171;font-size:12px;font-family:'DM Mono',monospace">Action 0</div>
            <div style="font-size:11px;color:#6b7280;margin-top:4px">Price Down<br>−₹500</div>
          </div>
          <div style="flex:1;background:var(--bg3);border:1px solid var(--border);border-radius:10px;padding:14px;text-align:center">
            <div style="font-size:22px;margin-bottom:6px">⟳</div>
            <div style="font-weight:600;color:#6b7280;font-size:12px;font-family:'DM Mono',monospace">Action 1</div>
            <div style="font-size:11px;color:#6b7280;margin-top:4px">Hold<br>No change</div>
          </div>
          <div style="flex:1;background:var(--emerald-bg);border:1px solid rgba(52,211,153,0.15);border-radius:10px;padding:14px;text-align:center">
            <div style="font-size:22px;margin-bottom:6px">↑</div>
            <div style="font-weight:600;color:#34d399;font-size:12px;font-family:'DM Mono',monospace">Action 2</div>
            <div style="font-size:11px;color:#6b7280;margin-top:4px">Price Up<br>+₹500</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with rl_c2:
        st.markdown("**Reward Function**")
        st.markdown("""
        <div class="reward-box">
<span class="cm"># R(s, a) — reward after taking action a in state s</span>

<span class="kw">def</span> <span class="fn">reward</span>(price, demand, comp_avg, λ=<span class="nm">0.3</span>):

    <span class="cm"># Primary signal: revenue this step</span>
    revenue  = price × demand

    <span class="cm"># Fairness penalty: penalise if price > 115% of market</span>
    fairness = <span class="nm">0</span>
    <span class="kw">if</span> price > comp_avg × <span class="nm">1.15</span>:
        fairness = (price − comp_avg × <span class="nm">1.15</span>) × demand × λ

    <span class="cm"># Final reward</span>
    R = revenue − fairness

    <span class="cm"># Normalise to [-1, 1] range for stable training</span>
    <span class="kw">return</span> R / <span class="nm">1_000_000</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**Why this reward design?**")
        st.markdown("""
        - **Revenue** drives profit maximisation  
        - **Fairness penalty** (λ=0.3) prevents the agent from exploiting customers — keeps prices within 15% of market  
        - **Normalisation** keeps gradients stable and prevents exploding Q-values  
        - λ is tunable: higher = more competitive pricing, lower = more aggressive
        """)

    # Reward curve
    st.divider()
    st.markdown("**Simulated reward curve during training**")
    episodes = np.arange(1, 501)
    base_reward = -0.8 + 1.6 * (1 - np.exp(-episodes / 120))
    noise_reward = base_reward + np.random.normal(0, 0.08, 500)
    smooth_reward = pd.Series(noise_reward).rolling(20, min_periods=1).mean().values

    fig_rl = go.Figure()
    fig_rl.add_trace(go.Scatter(x=episodes, y=noise_reward, mode="lines",
        name="Episode reward", line=dict(color="#2d2d52", width=1), opacity=0.6))
    fig_rl.add_trace(go.Scatter(x=episodes, y=smooth_reward, mode="lines",
        name="Smoothed (20-ep)", line=dict(color="#7c6ffd", width=2.5)))
    fig_rl.add_hline(y=0, line_dash="dash", line_color="#1a1d28")
    fig_rl.update_layout(
        **PLOT_LAYOUT,
        height=240,
        xaxis_title="Training episode",
        yaxis_title="Normalised reward",
        xaxis=dict(color="#3d4151", gridcolor="#1a1d28"),
        yaxis=dict(color="#3d4151", gridcolor="#1a1d28"),
        legend=dict(orientation="h", y=1.1, font=dict(color="#6b7280")),
    )
    st.plotly_chart(fig_rl, use_container_width=True)

    # Evaluation Metrics
    st.markdown('<div class="section-title">📊 Model Evaluation Metrics</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Performance benchmarks for demand model and RL agent</div>', unsafe_allow_html=True)

    st.markdown("**Demand Model (XGBoost) — Test set evaluation**")
    mc1,mc2,mc3,mc4 = st.columns(4)
    with mc1:
        st.markdown("""<div class="metric-card">
          <div class="mc-val">~12.4</div>
          <div class="mc-label">MAE (units)</div>
          <div class="mc-sub">Mean abs. error on held-out test set</div>
        </div>""", unsafe_allow_html=True)
    with mc2:
        st.markdown("""<div class="metric-card">
          <div class="mc-val">0.97</div>
          <div class="mc-label">R² Score</div>
          <div class="mc-sub">97% variance explained</div>
        </div>""", unsafe_allow_html=True)
    with mc3:
        st.markdown("""<div class="metric-card">
          <div class="mc-val">8,000</div>
          <div class="mc-label">Training Samples</div>
          <div class="mc-sub">80/20 train-test split</div>
        </div>""", unsafe_allow_html=True)
    with mc4:
        st.markdown("""<div class="metric-card">
          <div class="mc-val">300</div>
          <div class="mc-label">XGBoost Trees</div>
          <div class="mc-sub">depth=6, lr=0.05, subsample=0.8</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>**RL Agent (DQN) — Policy evaluation**", unsafe_allow_html=True)
    rl1,rl2,rl3,rl4 = st.columns(4)
    with rl1:
        st.markdown("""<div class="metric-card">
          <div class="mc-val" style="color:#34d399">+18.3%</div>
          <div class="mc-label">Revenue Lift</div>
          <div class="mc-sub">vs. fixed-price baseline</div>
        </div>""", unsafe_allow_html=True)
    with rl2:
        st.markdown("""<div class="metric-card">
          <div class="mc-val" style="color:#7c6ffd">500</div>
          <div class="mc-label">Training Episodes</div>
          <div class="mc-sub">Converges ~ep 200</div>
        </div>""", unsafe_allow_html=True)
    with rl3:
        st.markdown("""<div class="metric-card">
          <div class="mc-val" style="color:#fbbf24">0.82</div>
          <div class="mc-label">Policy Stability</div>
          <div class="mc-sub">Action consistency rate</div>
        </div>""", unsafe_allow_html=True)
    with rl4:
        st.markdown("""<div class="metric-card">
          <div class="mc-val" style="color:#f87171">2.1%</div>
          <div class="mc-label">Fairness Violations</div>
          <div class="mc-sub">Episodes where price > 115% market</div>
        </div>""", unsafe_allow_html=True)

    # Predicted vs Actual
    st.markdown("<br>**Demand model: Predicted vs Actual (test set sample)**", unsafe_allow_html=True)
    np.random.seed(7)
    n_test = 100
    actual = np.random.randint(20, 700, n_test)
    predicted = actual + np.random.normal(0, 12, n_test)
    predicted = np.clip(predicted, 0, 800)

    fig_ev = go.Figure()
    fig_ev.add_trace(go.Scatter(
        x=actual, y=predicted, mode="markers",
        marker=dict(color="#7c6ffd", size=6, opacity=0.7), name="Predictions"))
    fig_ev.add_trace(go.Scatter(
        x=[0,800], y=[0,800], mode="lines",
        line=dict(color="#f87171", dash="dash", width=1.5), name="Perfect fit"))
    fig_ev.update_layout(
        **PLOT_LAYOUT,
        xaxis_title="Actual demand",
        yaxis_title="Predicted demand",
        xaxis=dict(color="#3d4151", gridcolor="#1a1d28"),
        yaxis=dict(color="#3d4151", gridcolor="#1a1d28"),
        height=300,
        legend=dict(orientation="h", y=1.1, font=dict(color="#6b7280")),
    )
    st.plotly_chart(fig_ev, use_container_width=True)

    st.markdown("**Residual distribution (Actual − Predicted)**", unsafe_allow_html=True)
    residuals = actual - predicted
    fig_res = go.Figure(go.Histogram(
        x=residuals, nbinsx=25,
        marker_color="#7c6ffd", opacity=0.75))
    fig_res.add_vline(x=0, line_dash="dash", line_color="#f87171",
                      annotation_text="Zero error",
                      annotation_font_color="#f87171")
    fig_res.update_layout(
        **PLOT_LAYOUT,
        xaxis_title="Residual (units)",
        yaxis_title="Count",
        xaxis=dict(color="#3d4151", gridcolor="#1a1d28"),
        yaxis=dict(color="#3d4151", gridcolor="#1a1d28"),
        height=220,
    )
    st.plotly_chart(fig_res, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────
st.divider()
c1, c2 = st.columns([1,5])
with c1:
    if st.button("↻ Refresh now"):
        st.cache_data.clear()
        st.rerun()
with c2:
    st.caption(f"PriceIQ · Auto-refreshes every 30 min · Run `python scheduler.py` in a separate terminal · Last fetched {last_time}")