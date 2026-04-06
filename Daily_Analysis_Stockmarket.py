import streamlit as st
import yfinance as yf
import pandas as pd
import time
import requests
from random import randint

# 1. Page Configuration
st.set_page_config(page_title="Market War-Room", layout="wide")

# --- SIDEBAR ---
with st.sidebar:
    st.title("Settings")
    st.markdown("---")
    st.success("🚀 **Created by Hardik Jani**")
    if st.button('🔄 Hard Reset App'):
        st.cache_data.clear()
        st.rerun()
    st.write("Market War-Room v7.0 (Ultimate)")
    st.caption(f"Last Sync: {time.strftime('%H:%M:%S')}")

# ==========================================
# PART 1: ULTRA-STABLE DATA FETCH (THE FIX)
# ==========================================
def get_immortal_data(ticker):
    @st.cache_data(ttl=120) # Cache વધાર્યું છે જેથી બ્લોકિંગ ના થાય
    def fetch(t):
        # Rotating User-Agents
        agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        
        try:
            session = requests.Session()
            session.headers.update({'User-Agent': agents[randint(0, 2)]})
            
            # Fast fetch logic
            stock = yf.Ticker(t, session=session)
            df = stock.history(period="5d", interval="1d") # '1m' બ્લોક થાય છે એટલે '1d' વાપરવો સેફ છે
            
            if not df.empty and len(df) >= 2:
                cur = df['Close'].iloc[-1]
                prev = df['Close'].iloc[-2]
                change = ((cur - prev) / prev) * 100
                return float(cur), float(change)
        except:
            pass
        return 0.0, 0.0
    
    return fetch(ticker)

# ==========================================
# PART 2: THE DASHBOARD
# ==========================================
st.title("🏹 Market Watcher Pro: LIVE Analysis")
st.header("🌍 Global & Domestic Live Cues")

# Essential Tickers only
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
    price, change = get_immortal_data(sym)
    if price > 0:
        cols[i % 4].metric(name, f"{price:,.2f}", f"{change:+.2f}%")
    else:
        cols[i % 4].warning(f"{name} 🔄 Retrying...")

# ==========================================
# PART 3: THE LEGAL SHIELD (Mandatory)
# ==========================================
st.divider()
st.error("### 📉 OUTLOOK: VOLATILE / BEARISH")

st.caption("⚠️ **STRICT LEGAL DISCLAIMER**")
st.warning("""
**Educational Purpose Only:** Created by **Hardik Jani**.
* **No SEBI Registration:** I am NOT a SEBI registered advisor.
* **No Advice:** This tool is for tracking, NOT for buy/sell calls.
* **No Charges:** We **DO NOT charge any fees**. Access is 100% free.
* **Risk Warning:** Trading is risky; I am NOT responsible for your losses.
""")
