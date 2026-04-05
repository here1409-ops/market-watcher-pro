import streamlit as st
import urllib3
from bs4 import BeautifulSoup

# 1. Page Configuration
st.set_page_config(page_title="Market War-Room", layout="wide")

# Corrected CSS for Dark Theme look
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 25px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏹 Market Watcher Pro: Pre-Market Analysis")
st.caption("Monday, April 6, 2026 | Geopolitical & Institutional Data")

# ==========================================
# PART 1: GLOBAL & DOMESTIC INDICES (Dow, Nikkei, GIFT Nifty)
# ==========================================
st.header("🌍 Global & Domestic Cues")
market_data = {
    "NIFTY 50":   {"today": 22713.10, "yesterday": 22679.40},
    "SENSEX":     {"today": 73319.55, "yesterday": 73134.32},
    "GIFT NIFTY": {"today": 22480.00, "yesterday": 22713.00},
    "DOW JONES":  {"today": 46504.67, "yesterday": 46565.74},
    "NIKKEI 225": {"today": 53123.49, "yesterday": 52463.27},
    "USD-INR":    {"today": 94.83,    "yesterday": 92.97},
    "BRENT_CRUDE":{"today": 102.40,   "yesterday": 89.20},
    "INDIA_VIX":  {"today": 25.52,    "yesterday": 21.40}
}

m_cols = st.columns(4)
idx = 0
for name, prices in market_data.items():
    cur, prev = prices["today"], prices["yesterday"]
    
    if name == "USD-INR":
        display_name = "INR-USD (Inv)"
        val, prev_val = 1/cur, 1/prev
        label = f"${val:.6f}"
    else:
        display_name = name
        val, prev_val = cur, prev
        label = f"{val:,.2f}"
    
    change = ((val - prev_val) / prev_val) * 100
    m_cols[idx % 4].metric(display_name, label, f"{change:.2f}%")
    idx += 1

st.divider()

# ==========================================
# PART 2: F&O, FII/DII & PCR (Weekly vs Monthly)
# ==========================================
col_fo, col_news = st.columns([1, 1.2])

with col_fo:
    st.header("📊 Institutional & F&O")
    
    pcr_w, pcr_m = 0.85, 0.72
    st.subheader("Nifty Put-Call Ratio")
    c1, c2 = st.columns(2)
    c1.metric("Weekly PCR", pcr_w)
    c2.metric("Monthly PCR", pcr_m, delta=f"{pcr_m - pcr_w:.2f}", delta_color="inverse")
    
    if pcr_m < pcr_w:
        st.error("⚠️ Monthly PCR < Weekly: Big players are heavily shorting!")
    
    st.divider()
    
    fii_net, dii_net = -9931.13, 7208.41
    st.write(f"**FII Net:** :red[₹{fii_net} Cr] (Selling)")
    st.write(f"**DII Net:** :green[+₹{dii_net} Cr] (Buying)")

# ==========================================
# PART 3: EMERGENCY NEWS FEED
# ==========================================
with col_news:
    st.header("🚨 Emergency News Feed")
    http = urllib3.PoolManager()
    news_urls = ['https://www.reuters.com/world/middle-east/', 'https://www.reuters.com/business/finance/']
    
    found_news = []
    keywords = ["RBI", "IRAN", "STRAIT", "HORMUZ", "TRUMP", "WAR", "OIL"]
    
    try:
        for url in news_urls:
            r = http.request('GET', url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(r.data, 'lxml')
            for tag in soup.find_all(['h3', 'a']):
                msg = tag.text.strip()
                if any(word in msg.upper() for word in keywords) and msg not in found_news:
                    found_news.append(msg)
        
        if found_news:
            for item in found_news[:8]:
                st.warning(f"• {item}")
        else:
            st.write("No major geopolitical alerts. RBI meeting in focus.")
    except:
        st.error("Could not fetch news headlines.")

# ==========================================
# PART 4: FINAL PREDICTION SCORE
# ==========================================
st.divider()

score = 100
gn_change = ((market_data["GIFT NIFTY"]["today"] - market_data["GIFT NIFTY"]["yesterday"]) / market_data["GIFT NIFTY"]["yesterday"]) * 100

if gn_change < -0.5: score -= 30
if fii_net < -2000: score -= 20
if market_data["BRENT_CRUDE"]["today"] > 95: score -= 20
if pcr_m < 0.8: score -= 20
if market_data["INDIA_VIX"]["today"] > 22: score -= 10

st.header(f"🎯 Final Conviction Score: {score}/100")

if score <= 30:
    st.error("### 📉 OUTLOOK: PANIC / BLOOD BATH OPENING")
    st.markdown("**Action:** High VIX + Oil Spike + War Tension. Wait for 9:45 AM stability.")
elif score <= 60:
    st.warning("### 📉 OUTLOOK: BEARISH / VOLATILE")
    st.markdown("**Action:** Global indices are under pressure. Sell on rise.")
else:
    st.success("### 📈 OUTLOOK: RESILIENT / STABLE")
