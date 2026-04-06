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
    st.write("Market War-Room v5.0 (Stabilized)")
    st.caption(f"Last Sync: {time.strftime('%H:%M:%S')}")

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 24px; color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏹 Market Watcher Pro: LIVE Analysis")
st.caption("Stabilized Data Stream (Anti-Block Enabled)")

# ==========================================
# PART 1: ANTI-BLOCK DATA FETCH
# ==========================================
def get_reliable_data(ticker):
    @st.cache_data(ttl=30) # 30 સેકન્ડ કેશ રાખવી જરૂરી છે
    def fetch(t):
        try:
            # Yahoo Block થી બચવા માટે custom session
            session = requests.Session()
            session.headers.update({'User-Agent': 'Mozilla/5.0'})
            
            stock = yf.Ticker(t, session=session)
            # 1m ડેટા માં લોચો થાય છે એટલે 5m વાપરવો સેફ છે
            df = stock.history(period="2d", interval="5m") 
            
            if not df.empty:
                cur = df['Close'].iloc[-1]
                prev = df['Close'].iloc[-2]
                change = ((cur - prev) / prev) * 100
                return float(cur), float(change)
        except Exception as e:
            pass
        return 0.0, 0.0
    
    return fetch(ticker)

# ==========================================
# PART 2: DASHBOARD UI
# ==========================================
st.header("🌍 Global & Domestic Live Cues")

market_items = {
    "NIFTY 50": "^NSEI",
    "BANK NIFTY": "^NSEBANK",
    "GOLD (LIVE)": "GOLDM.NS",
    "DOW JONES": "^DJI",
    "NIKKEI 225": "^N225",
    "USD-INR": "INR=X",
    "BRENT_CRUDE": "BZ=F",
    "INDIA VIX": "^INDIAVIX"
}

m_cols = st.columns(4)
for i, (name, sym) in enumerate(market_items.items()):
    price, change = get_reliable_data(sym)
    if price > 0:
        m_cols[i % 4].metric(name, f"{price:,.2f}", f"{change:+.2f}%")
    else:
        # જો કનેક્શન જતું રહે તો જૂનો ડેટા બતાવવા પ્રયત્ન કરશે
        m_cols[i % 4].error(f"{name} ⚠️ Timeout")

st.divider()

# ==========================================
# PART 3: STOCKS & INSTITUTIONAL
# ==========================================
col_fo, col_news = st.columns([1, 1.2])

with col_fo:
    st.header("📊 Institutional Data")
    # આ ડેટા મેન્યુઅલી જ અપડેટ કરવો પડશે કારણ કે NSE ની સાઈટ ડાયરેક્ટ બ્લોક કરે છે
    st.write("**Weekly PCR:** 0.85 | **Monthly PCR:** 0.72")
    st.write("**FII Net:** :red[₹-9931.13 Cr] | **DII Net:** :green[+₹7208.41 Cr]")

with col_news:
    st.header("🎯 Stocks to Watch")
    watch_stocks = {"HDFC BANK": "HDFCBANK.NS", "ICICI BANK": "ICICIBANK.NS", "PNB HOUSING": "PNBHOUSING.NS"}
    for s_name, s_sym in watch_stocks.items():
        p, c = get_reliable_data(s_sym)
        if p > 0:
            st.write(f"**{s_name}**: ₹{p:,.2f} ({c:+.2f}%)")

# ==========================================
# PART 4: DISCLAIMER
# ==========================================
st.divider()
st.warning("⚠️ **Disclaimer:** Created by Hardik Jani. Personal reference only. No fees charged. Market data is delayed.")
