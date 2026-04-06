import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. Page Configuration
st.set_page_config(page_title="Market War-Room", layout="wide")

# --- SIDEBAR ---
with st.sidebar:
    st.title("Settings")
    st.markdown("---")
    st.success("🚀 **Created by Hardik Jani**")
    if st.button('🔄 Force Refresh'):
        st.cache_data.clear()
        st.rerun()
    st.caption(f"Last Sync: {time.strftime('%H:%M:%S')}")

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 24px; color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏹 Market Watcher Pro: LIVE Analysis")
st.caption("Reliable Multi-Source Data Feed (Real-Time)")

# ==========================================
# PART 1: RELIABLE DATA FETCH FUNCTION
# ==========================================
def get_reliable_data(ticker):
    try:
        # Method 1: Fast Download
        data = yf.download(ticker, period="2d", interval="1m", progress=False)
        if not data.empty:
            cur = data['Close'].iloc[-1]
            prev = data['Close'].iloc[0]
            return float(cur), float(((cur-prev)/prev)*100)
        
        # Method 2: Ticker Info (Back-up)
        t = yf.Ticker(ticker)
        h = t.history(period="2d")
        if not h.empty:
            cur = h['Close'].iloc[-1]
            prev = h['Close'].iloc[-2]
            return float(cur), float(((cur-prev)/prev)*100)
    except:
        return 0.0, 0.0
    return 0.0, 0.0

# ==========================================
# PART 2: DASHBOARD
# ==========================================
st.header("🌍 Global & Domestic Live Cues")

# Tickers je 100% chale che Yahoo par
market_items = {
    "NIFTY 50": "^NSEI",
    "BANK NIFTY": "^NSEBANK",
    "GOLD (LIVE)": "GOLDM.NS",
    "DOW JONES": "^DJI",
    "RELIANCE": "RELIANCE.NS",
    "HDFC BANK": "HDFCBANK.NS",
    "USD-INR": "INR=X",
    "INDIA VIX": "^INDIAVIX"
}

cols = st.columns(4)
for i, (name, sym) in enumerate(market_items.items()):
    price, change = get_reliable_data(sym)
    if price > 0:
        cols[i % 4].metric(name, f"{price:,.2f}", f"{change:+.2f}%")
    else:
        cols[i % 4].error(f"{name} Connection Lost")

st.divider()

# ==========================================
# PART 3: STOCKS TO WATCH
# ==========================================
st.header("🎯 High Conviction Stocks to Watch")
c1, c2 = st.columns(2)

with c1:
    st.subheader("🏙️ Large Cap")
    for s_name, s_sym in {"ICICI BANK": "ICICIBANK.NS", "INFOSYS": "INFY.NS"}.items():
        p, c = get_reliable_data(s_sym)
        st.write(f"**{s_name}**: ₹{p:,.2f} ({c:+.2f}%)")

with c2:
    st.subheader("🏢 Small/Mid Cap")
    for s_name, s_sym in {"MAHA BANK": "MAHABANK.NS", "PNB HOUSING": "PNBHOUSING.NS"}.items():
        p, c = get_reliable_data(s_sym)
        st.write(f"**{s_name}**: ₹{p:,.2f} ({c:+.2f}%)")

# ==========================================
# PART 4: LEGAL & CONVICTION
# ==========================================
st.divider()
st.header(f"🎯 Market Conviction Score: 25/100")
st.error("### 📉 OUTLOOK: WEAKNESS / VOLATILITY")

st.info("⚠️ **Disclaimer:** Created by Hardik Jani. Personal reference only. No financial advice. 100% Free Tool.")
