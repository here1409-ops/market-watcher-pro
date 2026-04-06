import streamlit as st
import yfinance as yf
import urllib3
from bs4 import BeautifulSoup
import time

# 1. Page Configuration
st.set_page_config(page_title="Market War-Room", layout="wide")

# --- SIDEBAR FOR CREDITS ---
with st.sidebar:
    st.title("Settings")
    st.markdown("---")
    st.markdown("### 🛠️ Developer Details")
    st.success("🚀 **Created by Hardik Jani**")
    st.markdown("---")
    if st.button('🔄 Force Refresh Now'):
        st.cache_data.clear()
        st.rerun()
    st.write("Market War-Room v4.0 (Live)")
    st.caption(f"Last Sync: {time.strftime('%H:%M:%S')}")

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 25px; }
    .stock-card { background-color: #1e2130; padding: 15px; border-radius: 10px; border-left: 5px solid #4CAF50; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏹 Market Watcher Pro: LIVE Analysis")
st.caption("Live Global Cues & Institutional Tracking (Auto-refreshing...)")

# ==========================================
# PART 1: LIVE GLOBAL & DOMESTIC DATA
# ==========================================
st.header("🌍 Global & Domestic Live Cues")

tickers = {
    "NIFTY 50": "^NSEI",
    "BANK NIFTY": "^NSEBANK",
    "GOLD (LIVE)": "GC=F", 
    "DOW JONES": "^DJI",
    "NIKKEI 225": "^N225",
    "USD-INR": "INR=X",
    "BRENT_CRUDE": "BZ=F",
    "INDIA_VIX": "^INDIAVIX"
}

def get_data_live(symbol):
    try:
        t = yf.Ticker(symbol)
        h = t.history(period="1d", interval="1m")
        if not h.empty:
            cur = h['Close'].iloc[-1]
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
# PART 3: STOCKS TO WATCH (Institutional Picks)
# ==========================================
st.divider()
st.header("🎯 High Conviction Stocks to Watch")
st.caption("Based on heavy institutional buying in the last quarter")

# Logic: Priority to Common, then HDFC MF Picks
# Large Cap: HDFC Bank, ICICI Bank (Commonly held/added)
# Small Cap: Bank of Maharashtra, PNB Housing, Karur Vysya (HDFC Small Cap active picks)

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏙️ Large Cap Segment")
    large_caps = {"HDFC BANK": "HDFCBANK.NS", "ICICI BANK": "ICICIBANK.NS"}
    for name, sym in large_caps.items():
        cur, prev = get_data_live(sym)
        chg = ((cur-prev)/prev)*100 if prev!=0 else 0
        st.markdown(f"**{name}**: ₹{cur:,.2f} ({chg:+.2f}%)")

with col2:
    st.subheader("🏢 Small Cap Segment")
    small_caps = {"BANK OF MAHA": "MAHABANK.NS", "PNB HOUSING": "PNBHOUSING.NS", "KARUR VYSYA": "KARURVYSYA.NS"}
    for name, sym in small_caps.items():
        cur, prev = get_data_live(sym)
        chg = ((cur-prev)/prev)*100 if prev!=0 else 0
        st.markdown(f"**{name}**: ₹{cur:,.2f} ({chg:+.2f}%)")
print("these stocks are not recommendation, given only on the basis of volume and turnover")

# ==========================================
# PART 4: CONVICTION SCORE
# ==========================================
st.divider()
st.header(f"🎯 Market Conviction Score: 25/100")
st.error("### 📉 OUTLOOK: PANIC / GAP DOWN OPENING")
st.info("Strategy: HDFC Bank and ICICI Bank are at crucial supports. Watch for recovery near 10:30 AM.")
