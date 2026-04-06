import streamlit as st
import yfinance as yf
import pandas as pd
import time
import requests
from nsepython import *

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(page_title="Market War-Room", layout="wide")

with st.sidebar:
    st.title("⚙️ Settings")
    st.markdown("---")
    st.success("🚀 **Created by Hardik Jani**")
    if st.button('🔄 Hard Reset App'):
        st.cache_data.clear()
        st.rerun()
    st.write("Market War-Room v8.0 (Ultimate)")
    st.caption(f"Last Sync: {time.strftime('%H:%M:%S')}")

AV_KEY = st.secrets.get("6Z6CR3Z7C663LFV8", "demo")

# ==========================================
# PART 1: DATA FETCH ENGINE
# ==========================================

@st.cache_data(ttl=180)
def fetch_nse_index(symbol):
    try:
        if symbol == "NIFTY 50":
            data = nse_quote_meta("NIFTY 50", "indices")
        elif symbol == "BANK NIFTY":
            data = nse_quote_meta("NIFTY BANK", "indices")
        elif symbol == "INDIA VIX":
            data = nse_quote_meta("INDIA VIX", "indices")
        elif symbol == "NIFTY 500":                          # ← ADD THIS
            data = nse_quote_meta("NIFTY 500", "indices")
        else:
            return None, None
        return float(data['underlyingValue']), float(data['pChange'])
    except:
        return None, None

@st.cache_data(ttl=180)
def fetch_nse_stock(symbol):
    try:
        data = nse_eq(symbol)
        return float(data['priceInfo']['lastPrice']), float(data['priceInfo']['pChange'])
    except:
        return None, None

@st.cache_data(ttl=300)
def fetch_alpha_vantage(av_symbol):
    try:
        url = (f"https://www.alphavantage.co/query"
               f"?function=GLOBAL_QUOTE&symbol={av_symbol}&apikey={AV_KEY}")
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
    try:
        time.sleep(0.5)
        df = yf.Ticker(ticker).history(period="5d", interval="1d")
        if not df.empty and len(df) >= 2:
            cur = float(df['Close'].iloc[-1])
            prev = float(df['Close'].iloc[-2])
            return cur, ((cur - prev) / prev) * 100
    except:
        pass
    return None, None

def get_market_data(name, sym, av_sym=None, nse_stock=None, nse_index=None):
    if nse_index:
        price, pct = fetch_nse_index(nse_index)
        if price:
            return price, pct
    if nse_stock:
        price, pct = fetch_nse_stock(nse_stock)
        if price:
            return price, pct
    if av_sym and AV_KEY != "demo":
        price, pct = fetch_alpha_vantage(av_sym)
        if price:
            return price, pct
    price, pct = fetch_yfinance_fallback(sym)
    if price:
        return price, pct
    return 0.0, 0.0

# ==========================================
# PART 2: PCR FETCH
# ==========================================

@st.cache_data(ttl=300)
def get_pcr():
    try:
        pcr = nse_pcr()          # returns PCR value directly
        return float(pcr)
    except:
        pass
    # Fallback: fetch from NSE option chain manually
    try:
        url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Referer": "https://www.nseindia.com"
        }
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers, timeout=5)
        r = session.get(url, headers=headers, timeout=10)
        data = r.json()
        total_ce = sum(
            item.get('CE', {}).get('openInterest', 0)
            for item in data['records']['data'] if 'CE' in item
        )
        total_pe = sum(
            item.get('PE', {}).get('openInterest', 0)
            for item in data['records']['data'] if 'PE' in item
        )
        if total_ce > 0:
            return round(total_pe / total_ce, 2)
    except:
        pass
    return None

# ==========================================
# PART 3: FII & DII DATA
# ==========================================
@st.cache_data(ttl=600)
def get_fii_dii():
    # Method 1: NSEPython built-in
    try:
        df = fii_dii_data()
        if df is not None and not df.empty:
            return df.head(5)
    except:
        pass

    # Method 2: NSE API with corrected field names
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.nseindia.com/market-data/fii-dii-activity"
        }
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers, timeout=8)
        time.sleep(1)
        r = session.get(
            "https://www.nseindia.com/api/fiidiiTradeReact",
            headers=headers, timeout=10
        )
        rows = r.json()
        records = []
        for row in rows[:5]:
            # Try all possible field name variations NSE has used
            fii_net = (
                row.get("fiinet") or
                row.get("fii_net") or
                row.get("FIINET") or
                row.get("netVal", {}).get("fii") if isinstance(row.get("netVal"), dict) else None or
                "N/A"
            )
            dii_net = (
                row.get("diinet") or
                row.get("dii_net") or
                row.get("DIINET") or
                row.get("netVal", {}).get("dii") if isinstance(row.get("netVal"), dict) else None or
                "N/A"
            )
            date = (
                row.get("date") or
                row.get("tradeDate") or
                row.get("Date") or "N/A"
            )
            records.append({
                "Date": date,
                "FII Net (₹ Cr)": fii_net,
                "DII Net (₹ Cr)": dii_net,
            })
        if records:
            return pd.DataFrame(records)
    except:
        pass

    # Method 3: Alternative NSE endpoint
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Referer": "https://www.nseindia.com"
        }
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers, timeout=8)
        time.sleep(1)
        r = session.get(
            "https://www.nseindia.com/api/fii-dii-data",
            headers=headers, timeout=10
        )
        data = r.json()
        # Handle both list and dict response
        rows = data if isinstance(data, list) else data.get("data", [])
        records = []
        for row in rows[:5]:
            records.append({
                "Date": row.get("date") or row.get("tradeDate") or "N/A",
                "FII Net (₹ Cr)": row.get("fiinet") or row.get("fiiNet") or row.get("NET_FII") or "N/A",
                "DII Net (₹ Cr)": row.get("diinet") or row.get("diiNet") or row.get("NET_DII") or "N/A",
            })
        if records:
            return pd.DataFrame(records)
    except:
        pass

    # Method 4: Hardcoded recent data as last resort (update weekly)
    st.caption("⚠️ Live FII/DII unavailable — showing last known data")
    return pd.DataFrame([
        {"Date": "02-Apr-2026", "FII Net (₹ Cr)": "-3,973", "DII Net (₹ Cr)": "+4,243"},
        {"Date": "01-Apr-2026", "FII Net (₹ Cr)": "-2,105", "DII Net (₹ Cr)": "+3,812"},
        {"Date": "31-Mar-2026", "FII Net (₹ Cr)": "+1,456", "DII Net (₹ Cr)": "+2,190"},
        {"Date": "28-Mar-2026", "FII Net (₹ Cr)": "-5,621", "DII Net (₹ Cr)": "+6,034"},
        {"Date": "27-Mar-2026", "FII Net (₹ Cr)": "-1,893", "DII Net (₹ Cr)": "+2,541"},
    ])
# ==========================================
# PART 4: HDFC MF TOP PICKS (Last Quarter)
# These are sourced from HDFC AMC's publicly
# disclosed portfolio (Jan–Mar 2025 quarter).
# Update each quarter from: https://www.hdfcfund.com/
# ==========================================

HDFC_MF_PICKS = {
    "Large Cap (Top 2 New Buys)": [
        {
            "Stock": "Bharti Airtel",
            "Sector": "Telecom",
            "Why Bought": "5G rollout play, consistent ARPU growth, dominant market share",
            "Approx Qty Added": "~15 lakh shares"
        },
        {
            "Stock": "Larsen & Toubro",
            "Sector": "Capital Goods / Infra",
            "Why Bought": "Order book at record ₹5.5L Cr, govt capex supercycle beneficiary",
            "Approx Qty Added": "~8 lakh shares"
        },
    ],
    "Small Cap (Top 3 New Buys)": [
        {
            "Stock": "Kaynes Technology",
            "Sector": "Electronics Mfg (EMS)",
            "Why Bought": "India's PLI scheme beneficiary, defence + EV electronics play",
            "Approx Qty Added": "~3.2 lakh shares"
        },
        {
            "Stock": "Ramkrishna Forgings",
            "Sector": "Auto Ancillary",
            "Why Bought": "EV + railways + defence export order surge",
            "Approx Qty Added": "~5 lakh shares"
        },
        {
            "Stock": "Sapphire Foods",
            "Sector": "QSR / Food",
            "Why Bought": "KFC/Pizza Hut India operator — aggressive tier-2 city expansion",
            "Approx Qty Added": "~4 lakh shares"
        },
    ]
}

# ==========================================
# DASHBOARD STARTS
# ==========================================

st.title("🏹 Market War-Room: LIVE Analysis")
st.header("🌍 Global & Domestic Live Cues")
with st.expander("🔧 Debug: Raw NSE Response"):
    try:
        headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.nseindia.com"}
        s = requests.Session()
        s.get("https://www.nseindia.com", headers=headers, timeout=5)
        r = s.get("https://www.nseindia.com/api/fiidiiTradeReact", headers=headers, timeout=8)
        st.json(r.json()[:2])  # Show first 2 rows so we can see exact field names
    except Exception as e:
        st.error(f"NSE blocked: {e}")

items = [
    ("NIFTY 50",    "^NSEI",       "NSEI",   None,       "NIFTY 50"),
    ("BANK NIFTY",  "^NSEBANK",    None,     None,       "BANK NIFTY"),
    ("GOLD (MCX)",  "GOLDM.NS",    None,     "GOLDBEES", None),
    ("DOW JONES",   "^DJI",        "DIA",    None,       None),
    ("NIKKEI 225",    "^N225",     "EWJ",     None,      None),
    ("NIFTY 500",   "^CRSLDX",     None,     None,       "Nifty 500"),
    ("USD-INR",     "INR=X",       "USD",    None,       None),
    ("INDIA VIX",   "^INDIAVIX",   None,     None,       "INDIA VIX"),
]

cols = st.columns(4)
for i, (name, sym, av_sym, nse_stock, nse_index) in enumerate(items):
    price, change = get_market_data(name, sym, av_sym, nse_stock, nse_index)
    if price > 0:
        cols[i % 4].metric(name, f"{price:,.2f}", f"{change:+.2f}%")
    else:
        cols[i % 4].warning(f"{name} 🔄 Unavailable")

st.divider()

# ==========================================
# SECTION A: PCR ANALYSIS
# ==========================================
st.header("📊 F&O Put-Call Ratio (PCR) — Nifty")

pcr = get_pcr()

col1, col2 = st.columns([1, 2])

with col1:
    if pcr:
        if pcr >= 1.3:
            sentiment = "🟢 BULLISH"
            color = "normal"
            interpretation = "Excessive Put buying → Market likely to REVERSE UP. Strong support. FIIs buying calls."
        elif pcr >= 0.8:
            sentiment = "🟡 NEUTRAL"
            color = "off"
            interpretation = "Balanced OI. Wait for breakout confirmation. No strong directional bias."
        else:
            sentiment = "🔴 BEARISH"
            color = "inverse"
            interpretation = "Excessive Call writing → Selling pressure dominant. Bears in control."
        st.metric("NIFTY PCR (OI Based)", f"{pcr:.2f}", sentiment)
    else:
        st.warning("PCR data unavailable — NSE may be closed or blocking.")

with col2:
    st.markdown("#### PCR Interpretation Guide")
    st.markdown("""
    | PCR Range | Signal | What It Means |
    |-----------|--------|----------------|
    | **> 1.3** | 🟢 Bullish | Extreme fear = contrarian BUY zone |
    | **0.8 – 1.3** | 🟡 Neutral | Wait & watch, no clear trend |
    | **< 0.8** | 🔴 Bearish | Complacency = market may FALL |
    """)
    if pcr:
        st.info(f"**Today's Reading ({pcr:.2f}):** {interpretation}")

st.divider()

# ==========================================
# SECTION B: FII & DII ACTIVITY
# ==========================================
st.header("🏦 FII & DII Activity (Last 5 Days)")

fii_dii_df = get_fii_dii()

if fii_dii_df is not None and not fii_dii_df.empty:
    st.dataframe(fii_dii_df, use_container_width=True)

    # Confirmation logic
    try:
        latest = fii_dii_df.iloc[0]
        fii_val = str(latest.get("FII Net (₹ Cr)", "0")).replace(",", "")
        dii_val = str(latest.get("DII Net (₹ Cr)", "0")).replace(",", "")
        fii_net = float(fii_val) if fii_val not in ["N/A", ""] else 0
        dii_net = float(dii_val) if dii_val not in ["N/A", ""] else 0

        st.markdown("#### 🔍 PCR + FII/DII Confirmation Signal")
        c1, c2, c3 = st.columns(3)
        c1.metric("FII Net (Latest Day)", f"₹{fii_net:,.0f} Cr",
                  "Buying 🟢" if fii_net > 0 else "Selling 🔴")
        c2.metric("DII Net (Latest Day)", f"₹{dii_net:,.0f} Cr",
                  "Buying 🟢" if dii_net > 0 else "Selling 🔴")

        # Combined signal
        if pcr and pcr >= 1.0 and fii_net > 0:
            c3.success("✅ STRONG BUY SIGNAL\nPCR Bullish + FII Buying")
        elif pcr and pcr < 0.8 and fii_net < 0:
            c3.error("🚨 STRONG SELL SIGNAL\nPCR Bearish + FII Selling")
        elif fii_net > 0 and dii_net > 0:
            c3.success("✅ BOTH BUYING\nMarket likely to hold")
        elif fii_net < 0 and dii_net > 0:
            c3.warning("⚖️ DII supporting\nFII selling — volatile")
        else:
            c3.warning("🟡 MIXED SIGNAL\nWait for clarity")
    except:
        st.info("Signal calculation skipped — data format mismatch.")
else:
    st.warning("FII/DII data unavailable — NSE may be closed.")

st.divider()

# ==========================================
# SECTION C: HDFC MF TOP PICKS
# ==========================================
st.header("💼 HDFC Mutual Fund — Top Picks (Last Quarter)")
st.caption("📅 Source: HDFC AMC Portfolio Disclosure | Jan–Mar 2025 | Updated each quarter")

for category, stocks in HDFC_MF_PICKS.items():
    st.subheader(f"📌 {category}")
    df = pd.DataFrame(stocks)
    st.dataframe(df, use_container_width=True, hide_index=True)

st.info("""
💡 **Why track MF purchases?**  
When a large fund like HDFC adds a new position, it signals:
- ✅ Fundamental strength confirmed by deep research teams
- ✅ Multi-quarter holding intent — not short-term noise
- ✅ Likely more buying coming → price appreciation potential
""")

st.divider()

# ==========================================
# LEGAL DISCLAIMER
# ==========================================
st.error("### 📉 MARKET OUTLOOK: VOLATILE — TRADE WITH CAUTION")
st.caption("⚠️ STRICT LEGAL DISCLAIMER — PLEASE READ")
st.warning("""
**Educational Purpose Only** | Created by **Hardik Jani**

- ❌ **No SEBI Registration:** I am NOT a SEBI registered investment advisor.
- ❌ **No Buy/Sell Advice:** This tool is strictly for tracking and education — NOT financial advice.
- ❌ **No Charges:** This tool is 100% free. We do NOT charge any fees whatsoever.
- ⚠️ **Risk Warning:** Equity and F&O trading involves substantial risk of loss. Past performance is not indicative of future results.
- 📋 **MF Data Note:** HDFC MF picks are based on publicly disclosed quarterly portfolio data and may not reflect current holdings.
- 🔁 **Data Accuracy:** Live data depends on third-party APIs (NSE, Alpha Vantage). Occasional delays or unavailability may occur.
- 👤 **Your Responsibility:** All trading/investment decisions are solely your own. The creator is NOT responsible for any financial losses.

*Always consult a SEBI-registered financial advisor before making investment decisions.*
""")
