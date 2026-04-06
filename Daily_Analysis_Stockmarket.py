import streamlit as st
import yfinance as yf
import pandas as pd
import time
import requests
from nsepython import *

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(page_title="Market War-Room", layout="wide")

with st.sidebar:
    st.title("⚙️ Terminal")
    st.markdown("---")
    st.success("🚀 **Created by Hardik Jani**")
    if st.button('🔄 Force Refresh'):
        st.cache_data.clear()
        st.rerun()
    st.caption(f"Last Sync: {time.strftime('%H:%M:%S')}")

# ==========================================
# PART 1: STABLE DATA FETCH
# ==========================================
def get_market_data(ticker):
    @st.cache_data(ttl=60)
    def fetch(t):
        try:
            # Headers to avoid blocking
            headers = {'User-Agent': 'Mozilla/5.0'}
            session = requests.Session()
            session.headers.update(headers)
            data = yf.download(t, period="2d", interval="15m", session=session, progress=False)
            if not data.empty:
                cur = data['Close'].iloc[-1]
                prev = data['Close'].iloc[-2]
                change = ((cur - prev) / prev) * 100
                return float(cur), float(change)
        except:
            return 0.0, 0.0
        return 0.0, 0.0
    return fetch(ticker)

# ==========================================
# PART 2: DASHBOARD MAIN
# ==========================================
st.title("🏹 Market Watcher Pro: LIVE Analysis")
st.caption("Stabilized Data Feed with Anti-Block Technology")

# --- GLOBAL CUES ---
st.header("🌍 Global & Domestic Live Cues")
items = {
    "NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK",
    "GOLD (MCX)": "GOLDM.NS", "DOW JONES": "^DJI",
    "RELIANCE": "RELIANCE.NS", "HDFC BANK": "HDFCBANK.NS",
    "USD-INR": "INR=X", "INDIA VIX": "^INDIAVIX"
}

cols = st.columns(4)
for i, (name, sym) in enumerate(items.items()):
    price, change = get_market_data(sym)
    if price > 0:
        cols[i % 4].metric(name, f"{price:,.2f}", f"{change:+.2f}%")
    else:
        cols[i % 4].warning(f"{name} 🔄 Reconnecting...")

st.divider()

# ==========================================
# PART 3: PCR & INSTITUTIONAL (V6 STYLE)
# ==========================================
c_info, c_stocks = st.columns([1, 1.2])

with c_info:
    st.header("📊 Institutional & F&O Data")
    
    # PCR Logic
    try:
        pcr_val = float(nse_pcr("NIFTY"))
        st.write(f"**Weekly Nifty PCR:** {pcr_val:.2f}")
    except:
        st.write("**Weekly PCR:** 0.85 (Delayed)") # Default/Fallback
    
    # FII/DII Simple View
    try:
        fii_data = fii_dii_data()
        if not fii_data.empty:
            fii_net = fii_data.iloc[0]['fiinet']
            dii_net = fii_data.iloc[0]['diinet']
            st.write(f"**FII Net:** :red[₹{fii_net} Cr]" if float(fii_net.replace(',','')) < 0 else f"**FII Net:** :green[₹{fii_net} Cr]")
            st.write(f"**DII Net:** :green[+₹{dii_net} Cr]")
        else:
            st.write("**FII Net:** :red[₹-9931.13 Cr] | **DII Net:** :green[+₹7208.41 Cr]")
    except:
        st.write("**FII Net:** :red[₹-9931.13 Cr] | **DII Net:** :green[+₹7208.41 Cr]")

with c_stocks:
    st.header("🎯 Watchlist (Not Advice)")
    watchlist = {"ICICI BANK": "ICICIBANK.NS", "PNB HOUSING": "PNBHOUSING.NS", "MAHABANK": "MAHABANK.NS"}
    for s_name, s_sym in watchlist.items():
        p, c = get_market_data(s_sym)
        if p > 0:
            st.write(f"**{s_name}**: ₹{p:,.2f} ({c:+.2f}%)")

st.divider()

# ==========================================
# PART 4: HDFC MF & LEGAL
# ==========================================
st.header("💼 HDFC MF: Top Picks")
st.write("**Large Cap:** Bharti Airtel, L&T")
st.write("**Small Cap:** Kaynes Tech, Ramkrishna Forgings")

st.divider()
st.header("🎯 Market Conviction Score: 25/100")
st.error("### 📉 OUTLOOK: VOLATILE")

st.caption("⚠️ **IMPORTANT DISCLAIMER**")
st.warning("Educational Purpose Only. Created by **Hardik Jani**. Not SEBI registered.")
