import streamlit as st
import urllib3
from bs4 import BeautifulSoup
import time
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Market War-Room", layout="wide")

# --- SIDEBAR ---
with st.sidebar:
    st.title("Settings")
    st.markdown("---")
    st.success("🚀 **Created by Hardik Jani**")
    if st.button('🔄 Refresh Real-Time Data'):
        st.rerun()
    st.caption(f"Last Sync: {time.strftime('%H:%M:%S')}")

# Custom CSS for Dark Theme
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 24px; color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏹 Market Watcher Pro: LIVE Analysis")
st.caption("Live Google Finance Scraper - No more N/A issues!")

# ==========================================
# PART 1: GOOGLE FINANCE SCRAPER FUNCTION
# ==========================================
def get_live_google(ticker, exchange="NSE"):
    try:
        url = f"https://www.google.com/finance/quote/{ticker}:{exchange}"
        http = urllib3.PoolManager()
        r = http.request('GET', url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(r.data, 'lxml')
        
        # Price fetching logic
        price = float(soup.find("div", {"class": "YMlS7e"}).text.replace(",", "").replace("₹", "").replace("$", ""))
        change_raw = soup.find("div", {"class": "Jw7Cdb"}).text
        # Change percentage nikalva mate
        change_pct = float(change_raw.replace("%", "").replace("+", "").replace("-", ""))
        if "-" in change_raw: change_pct = -change_pct
        
        return price, change_pct
    except:
        return 0.0, 0.0

# ==========================================
# PART 2: LIVE MARKET DASHBOARD
# ==========================================
st.header("🌍 Global & Domestic Live Cues")

# Tickers format for Google Finance
market_items = [
    {"name": "NIFTY 50", "sym": "NIFTY_50", "exch": "INDEXNSE"},
    {"name": "BANK NIFTY", "sym": "NIFTY_BANK", "exch": "INDEXNSE"},
    {"name": "GOLD (MCX)", "sym": "GOLD", "exch": "MCX"},
    {"name": "DOW JONES", "sym": ".DJI", "exch": "INDEXDJX"},
    {"name": "RELIANCE", "sym": "RELIANCE", "exch": "NSE"},
    {"name": "HDFC BANK", "sym": "HDFCBANK", "exch": "NSE"},
    {"name": "USD-INR", "sym": "USD-INR", "exch": "CURRENCY"},
    {"name": "INDIA VIX", "sym": "INDIAVIX", "exch": "INDEXNSE"}
]

cols = st.columns(4)
for i, item in enumerate(market_items):
    price, change = get_live_google(item["sym"], item["exch"])
    if price > 0:
        cols[i % 4].metric(item["name"], f"{price:,.2f}", f"{change:+.2f}%")
    else:
        cols[i % 4].error(f"{item['name']} Offline")

st.divider()

# ==========================================
# PART 3: STOCKS TO WATCH (Institutional)
# ==========================================
st.header("🎯 High Conviction Stocks to Watch")
st.caption("Common picks from HDFC & Parag Parikh (Watchlist only)")

s_col1, s_col2 = st.columns(2)
# Large Cap
with s_col1:
    st.subheader("🏙️ Large Cap")
    for s in ["ICICIBANK", "INFY"]:
        p, c = get_live_google(s, "NSE")
        st.write(f"**{s}**: ₹{p:,.2f} ({c:+.2f}%)")

# Small Cap
with s_col2:
    st.subheader("🏢 Small/Mid Cap")
    for s in ["MAHABANK", "PNBHOUSING", "KARURVYSYA"]:
        p, c = get_live_google(s, "NSE")
        st.write(f"**{s}**: ₹{p:,.2f} ({c:+.2f}%)")

# ==========================================
# PART 4: LEGAL & CONVICTION
# ==========================================
st.divider()
st.header(f"🎯 Market Conviction Score: 25/100")
st.error("### 📉 OUTLOOK: WEAKNESS / CONSOLIDATION")

st.info("⚠️ **Disclaimer:** Created by Hardik Jani. This is NOT investment advice. No charges are taken for this tool. Trading involves risk.")
