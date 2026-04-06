import streamlit as st
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
    if st.button('🔄 Refresh Real-Time'):
        st.rerun()
    st.caption(f"Last Sync: {time.strftime('%H:%M:%S')}")

# Custom CSS
st.markdown("<style>.main { background-color: #0e1117; } div[data-testid='stMetricValue'] { font-size: 24px; color: #ffffff; }</style>", unsafe_allow_html=True)

st.title("🏹 Market Watcher Pro: LIVE Analysis")
st.caption("Google Finance Scraper - Fixed Timeout Issues!")

# ==========================================
# PART 1: GOOGLE FINANCE SCRAPER
# ==========================================
def get_google_price(ticker, exchange):
    try:
        url = f"https://www.google.com/finance/quote/{ticker}:{exchange}"
        http = urllib3.PoolManager()
        r = http.request('GET', url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(r.data, 'html.parser')
        
        # Price Fetching
        price_div = soup.find("div", {"class": "YMlS7e"})
        change_div = soup.find("div", {"class": "Jw7Cdb"})
        
        if price_div:
            price = price_div.text.replace("₹", "").replace("$", "").replace(",", "")
            change = change_div.text if change_div else "0%"
            return price, change
    except:
        return None, None
    return None, None

# ==========================================
# PART 2: DASHBOARD
# ==========================================
st.header("🌍 Global & Domestic Live Cues")

# Tickers format for Google Finance
items = [
    {"label": "NIFTY 50", "ticker": "NIFTY_50", "exch": "INDEXNSE"},
    {"label": "BANK NIFTY", "ticker": "NIFTY_BANK", "exch": "INDEXNSE"},
    {"label": "GOLD (MCX)", "ticker": "GOLD", "exch": "MCX"},
    {"label": "DOW JONES", "ticker": ".DJI", "exch": "INDEXDJX"},
    {"label": "SENSEX", "ticker": "SENSEX", "exch": "INDEXBOM"},
    {"label": "HDFC BANK", "ticker": "HDFCBANK", "exch": "NSE"},
    {"label": "USD-INR", "ticker": "USD-INR", "exch": "CURRENCY"},
    {"label": "INDIA VIX", "ticker": "INDIAVIX", "exch": "INDEXNSE"}
]

cols = st.columns(4)
for i, item in enumerate(items):
    price, change = get_google_price(item["ticker"], item["exch"])
    if price:
        cols[i % 4].metric(item["label"], price, change)
    else:
        cols[i % 4].error(f"{item['label']} Offline")

# ==========================================
# PART 3: STOCKS & LEGAL
# ==========================================
st.divider()
st.header("🎯 Stocks to Watch")
st.write("**HDFC BANK | ICICI BANK | PNB HOUSING**")

st.divider()
st.header("🎯 Market Conviction Score: 25/100")
st.error("### 📉 OUTLOOK: VOLATILE")

st.info("⚠️ **Disclaimer:** Created by Hardik Jani. Educational purpose only. Not SEBI registered. No fees charged.")
