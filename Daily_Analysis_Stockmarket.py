import streamlit as st
import yfinance as yf
import urllib3
from bs4 import BeautifulSoup

# 1. Page Configuration
st.set_page_config(page_title="Market War-Room", layout="wide")

# --- SIDEBAR FOR CREDITS ---
with st.sidebar:
    st.title("Settings")
    st.markdown("---")
    st.markdown("### 🛠️ Developer Details")
    st.success("🚀 **Created by Hardik Jani**")
    st.markdown("---")
    if st.button('🔄 Refresh Live Data'):
        st.rerun()
    st.write("Market War-Room v2.0 (Live)")
    st.caption("Last Update: April 6, 2026")

# Custom CSS for Dark Theme look
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 25px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏹 Market Watcher Pro: LIVE Analysis")
st.caption("Live Global Cues & Institutional Data")

# ==========================================
# PART 1: LIVE GLOBAL & DOMESTIC DATA
# ==========================================
st.header("🌍 Global & Domestic Live Cues")

# Yahoo Finance Tickers
tickers = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "GIFT NIFTY": "NIFTY=F",
    "DOW JONES": "^DJI",
    "NIKKEI 225": "^N225",
    "USD-INR": "INR=X",
    "BRENT_CRUDE": "BZ=F",
    "INDIA_VIX": "^INDIAVIX"
}

def get_data(symbol):
    try:
        t = yf.Ticker(symbol)
        h = t.history(period="2d")
        if not h.empty and len(h) >= 2:
            cur = h['Close'].iloc[-1]
            prev = h['Close'].iloc[-2]
            return cur, prev
        elif not h.empty:
            cur = h['Close'].iloc[-1]
            return cur, cur
    except:
        return 0, 0
    return 0, 0

m_cols = st.columns(4)
for i, (name, sym) in enumerate(tickers.items()):
    cur, prev = get_data(sym)
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
    pcr_w, pcr_m = 0.85, 0.72 # These can be manual for now
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
        keywords = ["RBI", "IRAN", "WAR", "OIL", "MARKET"]
        found = False
        for tag in soup.find_all(['h3', 'a'])[:20]:
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
st.info("Strategy: Don't rush to buy the dip. Watch VIX and Oil prices.")
