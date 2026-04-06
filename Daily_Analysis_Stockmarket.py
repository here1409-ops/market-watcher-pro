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
    if st.button('🔄 Force Refresh Now'):
        st.cache_data.clear()
        st.rerun()
    st.write("Market War-Room v4.6")
    st.caption(f"Last Sync: {time.strftime('%H:%M:%S')}")

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 24px; color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏹 Market Watcher Pro: LIVE Analysis")
st.caption("Live Global Cues & Institutional Tracking (Auto-refreshing...)")

# ==========================================
# PART 1: DATA FETCH FUNCTION
# ==========================================
def get_reliable_data(ticker):
    @st.cache_data(ttl=60)
    def fetch(t):
        try:
            data = yf.download(t, period="2d", interval="1h", progress=False)
            if not data.empty:
                cur = data['Close'].iloc[-1]
                prev = data['Close'].iloc[-2]
                return float(cur), float(((cur-prev)/prev)*100)
        except:
            pass
        return 0.0, 0.0
    return fetch(ticker)

# ==========================================
# PART 2: LIVE MARKET DATA
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
        m_cols[i % 4].warning(f"{name} ⏳ Syncing...")

st.divider()

# ==========================================
# PART 3: INSTITUTIONAL & NEWS
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
        for tag in soup.find_all(['h3', 'a'])[:20]:
            msg = tag.text.strip()
            if any(word in msg.upper() for word in keywords):
                st.warning(f"• {msg}")
                found = True
        if not found: st.write("No major alerts right now.")
    except:
        st.write("News currently unavailable.")

# ==========================================
# PART 4: STOCKS TO WATCH
# ==========================================
st.divider()
st.header("🎯 High Conviction Stocks to Watch")

c1, c2 = st.columns(2)
with c1:
    st.subheader("🏙️ Large Cap")
    l_stocks = {"HDFC BANK": "HDFCBANK.NS", "ICICI BANK": "ICICIBANK.NS"}
    for s_name, s_sym in l_stocks.items():
        val, chg = get_reliable_data(s_sym)
        st.write(f"**{s_name}**: ₹{val:,.2f} ({chg:+.2f}%)")

with c2:
    st.subheader("🏢 Small Cap")
    s_stocks = {"BANK OF MAHA": "MAHABANK.NS", "PNB HOUSING": "PNBHOUSING.NS", "KARUR VYSYA": "KARURVYSYA.NS"}
    for s_name, s_sym in s_stocks.items():
        val, chg = get_reliable_data(s_sym)
        st.write(f"**{s_name}**: ₹{val:,.2f} ({chg:+.2f}%)")

# ==========================================
# PART 5: CONVICTION & DISCLAIMER
# ==========================================
st.divider()
st.header(f"🎯 Conviction Score: 25/100")
st.error("### 📉 OUTLOOK: VOLATILE")

st.caption("⚠️ **IMPORTANT DISCLAIMER**")
st.warning("""
**Educational Purpose Only:** Created by **Hardik Jani**. 
1. **No Financial Advice:** This is NOT buy/sell advice. 
2. **Not Responsible for Losses:** I am NOT a SEBI registered advisor. 
3. **No Charges:** This tool is **100% FREE**.
""")
