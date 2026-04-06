import streamlit as st
import yfinance as yf
import pandas as pd
import time
import requests
from nsepython import *

# ==========================================
# PAGE CONFIG & THEME
# ==========================================
st.set_page_config(page_title="Market War-Room Pro", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for Professional Look
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    [data-testid="stMetricValue"] { font-size: 28px !important; font-weight: 700; }
    .stDataFrame { border: 1px solid #30363d; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.title("⚙️ Terminal Settings")
    st.markdown("---")
    st.success("🚀 **Developer: Hardik Jani**")
    if st.button('🔄 Hard Reset Engine'):
        st.cache_data.clear()
        st.rerun()
    st.info("System: v9.0 (Live Alpha)")
    st.caption(f"Last Heartbeat: {time.strftime('%H:%M:%S')}")

AV_KEY = st.secrets.get("AV_KEY", "demo")

# ==========================================
# PART 1: HYBRID DATA ENGINE (NSE + YF)
# ==========================================

@st.cache_data(ttl=120)
def get_hybrid_data(name, yf_sym, nse_sym=None, is_index=False):
    # Step 1: Try NSE Python First (Real-time)
    try:
        if nse_sym:
            if is_index:
                data = nse_quote_meta(nse_sym, "indices")
                return float(data['underlyingValue']), float(data['pChange'])
            else:
                data = nse_eq(nse_sym)
                return float(data['priceInfo']['lastPrice']), float(data['priceInfo']['pChange'])
    except:
        pass

    # Step 2: Fallback to yfinance (Global/Backup)
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        ticker = yf.Ticker(yf_sym)
        df = ticker.history(period="2d", interval="1d")
        if not df.empty:
            cur = float(df['Close'].iloc[-1])
            prev = float(df['Close'].iloc[-2])
            return cur, ((cur - prev) / prev) * 100
    except:
        return 0.0, 0.0
    return 0.0, 0.0

# ==========================================
# PART 2: ADVANCED ANALYTICS (PCR & FII)
# ==========================================

@st.cache_data(ttl=300)
def get_live_pcr():
    try:
        return float(nse_pcr("NIFTY"))
    except:
        return None

@st.cache_data(ttl=600)
def get_fii_summary():
    try:
        df = fii_dii_data()
        return df.head(5) if df is not None else None
    except:
        return None

# ==========================================
# DASHBOARD MAIN UI
# ==========================================

st.title("🏹 Market War-Room: Pro Analysis")
st.caption("Multi-Source Data Feed (NSE + AlphaVantage + Yahoo Finance)")

# --- LIVE QUOTES GRID ---
st.subheader("🌍 Global & Domestic Watchlist")
items = [
    ("NIFTY 50", "^NSEI", "NIFTY 50", True),
    ("BANK NIFTY", "^NSEBANK", "NIFTY BANK", True),
    ("DOW JONES", "^DJI", None, False),
    ("GOLD (MCX)", "GOLDM.NS", None, False),
    ("RELIANCE", "RELIANCE.NS", "RELIANCE", False),
    ("HDFC BANK", "HDFCBANK.NS", "HDFCBANK", False),
    ("INDIA VIX", "^INDIAVIX", "INDIA VIX", True),
    ("USD-INR", "INR=X", None, False)
]

cols = st.columns(4)
for i, (name, yf_s, nse_s, is_idx) in enumerate(items):
    price, change = get_hybrid_data(name, yf_s, nse_s, is_idx)
    if price > 0:
        cols[i % 4].metric(name, f"{price:,.2f}", f"{change:+.2f}%")
    else:
        cols[i % 4].error(f"{name} 🔄 Offline")

st.divider()

# --- SENTIMENT ANALYSIS ---
col_pcr, col_fii = st.columns([1, 1.5])

with col_pcr:
    st.header("📊 Option Chain (PCR)")
    pcr = get_live_pcr()
    if pcr:
        if pcr >= 1.25:
            st.success(f"PCR: {pcr:.2f} (Bullish/Overbought)")
        elif pcr <= 0.75:
            st.error(f"PCR: {pcr:.2f} (Bearish/Oversold)")
        else:
            st.warning(f"PCR: {pcr:.2f} (Neutral)")
        
        st.progress(min(max(pcr/2, 0.0), 1.0))
        st.caption("Interpretation: >1.2 Bullish | <0.8 Bearish")
    else:
        st.warning("NSE Option Chain Unreachable")

with col_fii:
    st.header("🏦 Institutional Flow")
    fii_df = get_fii_summary()
    if fii_df is not None:
        st.dataframe(fii_df, use_container_width=True, hide_index=True)
    else:
        st.error("FII/DII Data Delayed from Source")

st.divider()

# --- HDFC MF STRATEGY ---
st.header("💼 HDFC MF: Whale Tracking")
st.info("Tracking New Positions for Jan-Mar 2025 Quarter")

tab1, tab2 = st.tabs(["🏙️ Large Cap Picks", "🏢 Small/Mid Cap Picks"])

HDFC_MF_PICKS = {
    "Large": [
        {"Stock": "Bharti Airtel", "Qty": "~15L", "Reason": "ARPU & 5G Growth"},
        {"Stock": "L&T", "Qty": "~8L", "Reason": "Order Book Record"}
    ],
    "Small": [
        {"Stock": "Kaynes Tech", "Qty": "~3.2L", "Reason": "EMS/PLI Leader"},
        {"Stock": "Sapphire Foods", "Qty": "~4L", "Reason": "QSR Expansion"}
    ]
}

with tab1:
    st.table(HDFC_MF_PICKS["Large"])
with tab2:
    st.table(HDFC_MF_PICKS["Small"])

# ==========================================
# FINAL LEGAL SHIELD
# ==========================================
st.divider()
st.error("### 📉 TRADING TERMINAL DISCLAIMER")
st.warning(f"""
**Developer:** Hardik Jani | **Source:** Public APIs | **Status:** Educational
1. **SEBI:** I am NOT a SEBI registered advisor.
2. **Advice:** This is NOT a buy/sell signal generator.
3. **Risk:** Trading involves 100% risk of capital.
4. **Fees:** This software is provided 100% Free of charge.
""")
