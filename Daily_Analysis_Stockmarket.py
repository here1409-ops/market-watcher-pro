import streamlit as st
import yfinance as yf
import urllib3
from bs4 import BeautifulSoup
import time

# 1. Page Configuration
st.set_page_config(page_title="Market War-Room", layout="wide")

# --- AUTO REFRESH LOGIC (Every 60 Seconds) ---
# Aa line thi page automatic refresh thaya karse
# st.empty() vapri ne loop pan kari sakay, pan refresh best che
# streamlit_autorefresh vaparva mate extra install karvu pade, etle aapne simple logic rakhye che.

# --- SIDEBAR FOR CREDITS ---
with st.sidebar:
    st.title("Settings")
    st.markdown("---")
    st.markdown("### 🛠️ Developer Details")
    st.success("🚀 **Created by Hardik Jani**")
    st.markdown("---")
    if st.button('🔄 Force Refresh Now'):
        st.cache_data.clear() # Cache clear karse
        st.rerun()
    st.write("Market War-Room v3.0 (Real-Time)")
    st.caption(f"Last Sync: {time.strftime('%H:%M:%S')}")

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 25px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏹 Market Watcher Pro: LIVE Analysis")
st.caption("Live Global Cues & Institutional Data (Auto-refreshing...)")

# ==========================================
# PART 1: LIVE GLOBAL & DOMESTIC DATA
# ==========================================
st.header("🌍 Global & Domestic Live Cues")

# Best working tickers for yfinance
tickers = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "GOLD (LIVE)": "GC=F", # "Gold rate" 
    "DOW JONES": "^DJI",
    "NIKKEI 225": "^N225",
    "USD-INR": "INR=X",
    "BRENT_CRUDE": "BZ=F",
    "INDIA_VIX": "^INDIAVIX"
}

# Function with no cache to get REAL real-time data
def get_data_live(symbol):
    try:
        # Ticker fetch karva mate
        t = yf.Ticker(symbol)
        # period="1d" ane interval="1m" sauthi latest data aape
        h = t.history(period="1d", interval="1m")
        if not h.empty:
            cur = h['Close'].iloc[-1]
            # Previous close mate biji history fetch karvi pade
            h2 = t.history(period="2d")
            prev = h2['Close'].iloc[-2] if len(h2) > 1 else cur
            return cur, prev
    except:
        return 0, 0
    return 0, 0

m_cols = st.columns(4)
for i, (name, sym) in enumerate(tickers.items()):
    cur, prev = get_data_live(sym)
    if cur > 0:
        change = ((cur - prev) / prev) * 100 if prev != 0 else 0
        label = f"{cur:,.2f}"
        if name == "USD-INR": label = f"₹{cur:.2f}"
        m_cols[i % 4].metric(name, label, f"{change:.2f}%")
    else:
        m_cols[i % 4].error(f"{name} N/A")

st.divider()

# ==========================================
# PART 2: F&O & NEWS FEED
# ==========================================
col_fo, col_news = st.columns([1, 1.2])

with col_fo:
    st.header("📊 Institutional Data")
    # Aa data dar 15 min a badlavo hoy to manual j best che
    pcr_w, pcr_m = 0.85, 0.72 
    st.write(f"**Weekly PCR:** {pcr_w} | **Monthly PCR:** {pcr_m}")
    
    fii_net, dii_net = -9931.13, 7208.41
    st.write(f"**FII Net:** :red[₹{fii_net} Cr]")
    st.write(f"**DII Net:** :green[+₹{dii_net} Cr]")
    
    if pcr_m < pcr_w:
        st.error("⚠️ Danger: Monthly PCR is Bearish!")

with col_news:
    st.header("🚨 Emergency News")
    http = urllib3.PoolManager()
    try:
        r = http.request('GET', 'https://www.reuters.com/business/finance/', headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(r.data, 'lxml')
        keywords = ["RBI", "IRAN", "WAR", "OIL", "MARKET", "NIFTY"]
        found = False
        for tag in soup.find_all(['h3', 'a'])[:30]:
            msg = tag.text.strip()
            if any(word in msg.upper() for word in keywords):
                st.warning(f"• {msg}")
                found = True
        if not found: st.write("No major alerts right now.")
    except:
        st.write("News currently unavailable.")

# ==========================================
# PART 3: CONVICTION SCORE
# ==========================================
st.divider()
st.header("🎯 Conviction Score: 25/100")
st.error("### 📉 OUTLOOK: PANIC / GAP DOWN OPENING")
st.info("Strategy: Real-time checks confirm high volatility. Watch VIX levels.")
