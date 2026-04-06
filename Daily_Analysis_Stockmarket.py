import streamlit as st
import yfinance as yf
import pandas as pd
import time
import requests

# 1. Page Configuration
st.set_page_config(page_title="Market War-Room", layout="wide")

# --- SIDEBAR ---
with st.sidebar:
    st.title("Settings")
    st.markdown("---")
    st.success("🚀 **Created by Hardik Jani**")
    if st.button('🔄 Force Refresh Now'):
        st.cache_data.clear()
        st.rerun()
    st.write("Market War-Room v6.0 (Stable)")
    st.caption(f"Last Sync: {time.strftime('%H:%M:%S')}")

# Custom CSS for UI
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 24px; color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏹 Market Watcher Pro: LIVE Analysis")
st.caption("Stabilized Data Feed with Anti-Block Technology")

# ==========================================
# PART 1: ANTI-BLOCK DATA FETCH FUNCTION
# ==========================================
def get_market_data(ticker):
    @st.cache_data(ttl=60) # 60 સેકન્ડ સુધી ડેટા કેશ કરશે જેથી બ્લોક ના થાય
    def fetch(t):
        try:
            # બ્રાઉઝર જેવી ઓળખ આપવા માટે Headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            session = requests.Session()
            session.headers.update(headers)
            
            # yfinance ને સેસન સાથે ડાઉનલોડ કરવું
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
# PART 2: GLOBAL & DOMESTIC DASHBOARD
# ==========================================
st.header("🌍 Global & Domestic Live Cues")

# Tickers list
items = {
    "NIFTY 50": "^NSEI",
    "BANK NIFTY": "^NSEBANK",
    "GOLD (MCX)": "GOLDM.NS",
    "DOW JONES": "^DJI",
    "RELIANCE": "RELIANCE.NS",
    "HDFC BANK": "HDFCBANK.NS",
    "USD-INR": "INR=X",
    "INDIA VIX": "^INDIAVIX"
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
# PART 3: INSTITUTIONAL DATA & WATCHLIST
# ==========================================
c_info, c_stocks = st.columns([1, 1.2])

with c_info:
    st.header("📊 Institutional Data")
    st.write("**Weekly PCR:** 0.85 | **Monthly PCR:** 0.72")
    st.write("**FII Net:** :red[₹-9931.13 Cr] | **DII Net:** :green[+₹7208.41 Cr]")

with c_stocks:
    st.header("🎯 Watchlist (Not Advice)")
    watchlist = {"ICICI BANK": "ICICIBANK.NS", "PNB HOUSING": "PNBHOUSING.NS", "MAHABANK": "MAHABANK.NS"}
    for s_name, s_sym in watchlist.items():
        p, c = get_market_data(s_sym)
        if p > 0:
            st.write(f"**{s_name}**: ₹{p:,.2f} ({c:+.2f}%)")

# ==========================================
# PART 4: LEGAL DISCLAIMER (Strict Compliance)
# ==========================================
st.divider()
st.header("🎯 Market Conviction Score: 25/100")
st.error("### 📉 OUTLOOK: VOLATILE")

st.caption("⚠️ **IMPORTANT DISCLAIMER**")
st.warning("""
**Educational Purpose Only:** This dashboard is created by **Hardik Jani** for personal reference only.
1. **No Financial Advice:** Any data shown here should NOT be considered as buy/sell advice.
2. **Not Responsible for Losses:** I am NOT a SEBI registered advisor. I am not responsible for any financial losses.
3. **No Charges:** We **DO NOT charge any fees** for accessing or using this page. It is 100% free.
4. **Reference Only:** Everything bought or sold on the basis of this page is at the user's own risk.
""")
