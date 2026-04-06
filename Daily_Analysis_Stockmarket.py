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
    st.caption(f"Last Sync: {time.strftime('%H:%M:%S')}")

# ==========================================
# PART 1: THE FIX - STABLE DATA FETCH
# ==========================================
def get_market_data(ticker):
    @st.cache_data(ttl=60) # 60 સેકન્ડ સુધી ડેટા પકડી રાખશે
    def fetch(t):
        try:
            # બ્રાઉઝર જેવી ઓળખ આપવા માટે Headers
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            session = requests.Session()
            session.headers.update(headers)
            
            # yfinance ને આ સેશન આપવું જરૂરી છે
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
# PART 2: UI DASHBOARD
# ==========================================
st.title("🏹 Market Watcher Pro: LIVE Analysis")
st.header("🌍 Global & Domestic Live Cues")

# Tickers જે Yahoo પર 100% લાઈવ હોય છે
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
        # જો હજુ પણ બ્લોક હોય તો આ દેખાશે
        cols[i % 4].warning(f"{name} 🔄 Reconnecting...")

# ==========================================
# PART 3: LEGAL DISCLAIMER (Required)
# ==========================================
st.divider()
st.caption("⚠️ **IMPORTANT DISCLAIMER**")
st.warning("""
**Educational Purpose Only:** This dashboard is created by **Hardik Jani** for reference only.
1. **No Financial Advice:** This is NOT buy/sell advice.
2. **Not Responsible:** I am NOT a SEBI registered advisor. I am not responsible for any losses.
3. **No Charges:** We **DO NOT charge any fees** for this page.
""")
