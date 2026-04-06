import streamlit as st
import yfinance as yf
import urllib3
from bs4 import BeautifulSoup
import time

# 1. Page Configuration
st.set_page_config(page_title="Market War-Room", layout="wide")

# --- SIDEBAR ---
with st.sidebar:
    st.title("Settings")
    st.markdown("---")
    st.success("🚀 **Created by Hardik Jani**")
    if st.button('🔄 Force Refresh Data'):
        st.cache_data.clear()
        st.rerun()
    st.caption(f"Last Sync: {time.strftime('%H:%M:%S')}")

# Custom CSS for Dark UI
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 25px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏹 Market Watcher Pro: LIVE Analysis")
st.caption("Live Global Cues & Institutional Tracking (Auto-refreshing...)")

# ==========================================
# PART 1: LIVE GLOBAL & DOMESTIC DATA
# ==========================================
st.header("🌍 Global & Domestic Live Cues")

# UPDATED TICKERS: Gold rate mate GOLDM.NS (NSE) vadhare accurate che India mate
tickers = {
    "NIFTY 50": "^NSEI",
    "BANK NIFTY": "^NSEBANK",
    "GOLD (LIVE)": "GOLDM.NS",  # Fixed for Indian Market
    "DOW JONES": "^DJI",
    "NIKKEI 225": "^N225",
    "USD-INR": "INR=X",
    "BRENT_CRUDE": "BZ=F",
    "INDIA_VIX": "^INDIAVIX"
}

def get_data_live(symbol):
    try:
        # 1m interval latest point fetch karva mate best che
        data = yf.download(symbol, period="1d", interval="1m", progress=False)
        if not data.empty:
            cur = data['Close'].iloc[-1]
            prev = data['Open'].iloc[0] # Day open sathe compare karvu vadhare precise che
            return float(cur), float(prev)
    except:
        return 0, 0
    return 0, 0

m_cols = st.columns(4)
for i, (name, sym) in enumerate(tickers.items()):
    cur, prev = get_data_live(sym)
    if cur > 0:
        change = ((cur - prev) / prev) * 100
        label = f"{cur:,.2f}"
        if name == "USD-INR": label = f"₹{cur:.2f}"
        m_cols[i % 4].metric(name, label, f"{change:.2f}%")
    else:
        m_cols[i % 4].error(f"{name} N/A")

st.divider()

# ==========================================
# PART 2: INSTITUTIONAL & NEWS
# ==========================================
col_fo, col_news = st.columns([1, 1.2])

with col_fo:
    st.header("📊 Institutional Data")
    pcr_w, pcr_m = 0.85, 0.72 
    st.write(f"**Weekly PCR:** {pcr_w} | **Monthly PCR:** {pcr_m}")
    fii_net, dii_net = -9931.13, 7208.41
    st.write(f"**FII Net:** :red[₹{fii_net} Cr] | **DII Net:** :green[+₹{dii_net} Cr]")
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
        for tag in soup.find_all(['h3', 'a'])[:25]:
            msg = tag.text.strip()
            if any(word in msg.upper() for word in keywords):
                st.warning(f"• {msg}")
                found = True
        if not found: st.write("No major alerts right now.")
    except:
        st.write("News feed down.")

# ==========================================
# PART 3: STOCKS TO WATCH
# ==========================================
st.divider()
st.header("🎯 Stocks to Watch")
st.caption("Based on volume and turnover. This is NOT a recommendation, only for your watchlist.")

c1, c2 = st.columns(2)
# Picks based on HDFC & Parag Parikh priority
with c1:
    st.subheader("🏙️ Large Cap Segment")
    for s_name, s_sym in {"HDFC BANK": "HDFCBANK.NS", "ICICI BANK": "ICICIBANK.NS"}.items():
        val, _ = get_data_live(s_sym)
        st.write(f"**{s_name}**: ₹{val:,.2f}")

with c2:
    st.subheader("🏢 Small Cap Segment")
    for s_name, s_sym in {"BANK OF MAHA": "MAHABANK.NS", "PNB HOUSING": "PNBHOUSING.NS", "KARUR VYSYA": "KARURVYSYA.NS"}.items():
        val, _ = get_data_live(s_sym)
        st.write(f"**{s_name}**: ₹{val:,.2f}")

# ==========================================
# PART 4: CONVICTION SCORE
# ==========================================
st.divider()
st.header(f"🎯 Market Conviction Score: 25/100")
st.error("### 📉 OUTLOOK: PANIC / GAP DOWN OPENING")
st.info("Strategy: HDFC Bank and ICICI Bank are at crucial supports. Watch for recovery near 10:30 AM.")

# ==========================================
# PART 5: LEGAL DISCLAIMER & DECLARATION
# ==========================================
st.divider()
st.caption("⚠️ **IMPORTANT DISCLAIMER**")
st.warning("""
**Educational Purpose Only:** Created by **Hardik Jani** for personal reference. 
1. **No Financial Advice:** This is NOT buy/sell advice. 
2. **Not Responsible for Losses:** I am NOT a SEBI registered advisor. Trading is at your own risk. 
3. **No Charges:** This page is **100% FREE**. We do not charge any fees.
""")
