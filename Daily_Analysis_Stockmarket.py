import streamlit as st
import yfinance as yf
import pandas as pd
import time
import requests
from nsepython import *

# ==========================================
# MULTI-SOURCE DATA ENGINE (Anti-Block)
# ==========================================

AV_KEY = st.secrets.get("7VS2EN1LYXT19R24", "demo")  # Add your key in Streamlit secrets

@st.cache_data(ttl=180)
def fetch_nse_index(symbol):
    """Fetch NSE indices directly from NSE — no Yahoo needed."""
    try:
        if symbol == "NIFTY 50":
            data = nse_quote_meta("NIFTY 50", "indices")
            price = float(data['underlyingValue'])
            change = float(data['change'])
            pct = float(data['pChange'])
            return price, pct
        elif symbol == "BANK NIFTY":
            data = nse_quote_meta("NIFTY BANK", "indices")
            price = float(data['underlyingValue'])
            pct = float(data['pChange'])
            return price, pct
        elif symbol == "INDIA VIX":
            data = nse_quote_meta("INDIA VIX", "indices")
            price = float(data['underlyingValue'])
            pct = float(data['pChange'])
            return price, pct
    except Exception as e:
        return None, None
    return None, None

@st.cache_data(ttl=180)
def fetch_nse_stock(symbol):
    """Fetch NSE stock quote directly."""
    try:
        data = nse_eq(symbol)
        price = float(data['priceInfo']['lastPrice'])
        pct = float(data['priceInfo']['pChange'])
        return price, pct
    except:
        return None, None

@st.cache_data(ttl=300)
def fetch_alpha_vantage(av_symbol):
    """Fetch global indices via Alpha Vantage."""
    try:
        url = (
            f"https://www.alphavantage.co/query"
            f"?function=GLOBAL_QUOTE&symbol={av_symbol}&apikey={AV_KEY}"
        )
        r = requests.get(url, timeout=10)
        data = r.json().get("Global Quote", {})
        price = float(data.get("05. price", 0))
        pct = float(data.get("10. change percent", "0%").replace("%", ""))
        if price > 0:
            return price, pct
    except:
        pass
    return None, None

@st.cache_data(ttl=180)
def fetch_yfinance_fallback(ticker):
    """Last resort — yfinance with delay to reduce blocking."""
    try:
        time.sleep(0.5)
        df = yf.Ticker(ticker).history(period="5d", interval="1d")
        if not df.empty and len(df) >= 2:
            cur = float(df['Close'].iloc[-1])
            prev = float(df['Close'].iloc[-2])
            pct = ((cur - prev) / prev) * 100
            return cur, pct
    except:
        pass
    return None, None

def get_market_data(name, sym, av_sym=None, nse_stock=None, nse_index=None):
    """
    Smart router — tries sources in order:
    1. NSE direct (for Indian data)
    2. Alpha Vantage (for global)
    3. yfinance (fallback)
    """
    # Try NSE index (Nifty, BankNifty, VIX)
    if nse_index:
        price, pct = fetch_nse_index(nse_index)
        if price:
            return price, pct

    # Try NSE stock quote
    if nse_stock:
        price, pct = fetch_nse_stock(nse_stock)
        if price:
            return price, pct

    # Try Alpha Vantage for global
    if av_sym and AV_KEY != "demo":
        price, pct = fetch_alpha_vantage(av_sym)
        if price:
            return price, pct

    # Last resort: yfinance
    price, pct = fetch_yfinance_fallback(sym)
    if price:
        return price, pct

    return 0.0, 0.0

# ==========================================
# DASHBOARD
# ==========================================
st.title("🏹 Market Watcher Pro: LIVE Analysis")
st.header("🌍 Global & Domestic Live Cues")

# Each entry: (display_name, yf_ticker, av_symbol, nse_stock_symbol, nse_index_name)
items = [
    ("NIFTY 50",    "^NSEI",       "NSEI",   None,          "NIFTY 50"),
    ("BANK NIFTY",  "^NSEBANK",    None,     None,          "BANK NIFTY"),
    ("GOLD (MCX)",  "GOLDM.NS",    None,     "GOLDBEES",    None),
    ("DOW JONES",   "^DJI",        "DIA",    None,          None),
    ("RELIANCE",    "RELIANCE.NS", None,     "RELIANCE",    None),
    ("HDFC BANK",   "HDFCBANK.NS", None,     "HDFCBANK",    None),
    ("USD-INR",     "INR=X",       "USD",    None,          None),
    ("INDIA VIX",   "^INDIAVIX",   None,     None,          "INDIA VIX"),
]

cols = st.columns(4)
for i, (name, sym, av_sym, nse_stock, nse_index) in enumerate(items):
    price, change = get_market_data(name, sym, av_sym, nse_stock, nse_index)
    if price > 0:
        cols[i % 4].metric(name, f"{price:,.2f}", f"{change:+.2f}%")
    else:
        cols[i % 4].warning(f"{name} 🔄 Unavailable")
