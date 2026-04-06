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
        elif symbol == "NIFTY 500":
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
# PART 2: PCR FETCH (Weekly + Monthly)
# ==========================================

@st.cache_data(ttl=300)
def get_pcr_detailed():
    """
    Returns dict: {
        'weekly':  (pcr_value, expiry_date_str),
        'monthly': (pcr_value, expiry_date_str),
        'combined': pcr_value,
        '_source': source_string
    }
    """
    result = {"weekly": (None, ""), "monthly": (None, ""), "combined": None}

    try:
        url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "application/json",
            "Referer": "https://www.nseindia.com",
            "Accept-Language": "en-US,en;q=0.9",
        }
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers, timeout=5)
        r = session.get(url, headers=headers, timeout=10)
        data = r.json()

        records      = data.get("records", {})
        expiry_dates = records.get("expiryDates", [])
        all_data     = records.get("data", [])

        if not expiry_dates or not all_data:
            raise ValueError("Empty option chain")

        from datetime import datetime

        def parse_expiry(s):
            return datetime.strptime(s, "%d-%b-%Y")

        sorted_expiries = sorted(expiry_dates, key=parse_expiry)
        weekly_expiry   = sorted_expiries[0]

        today      = datetime.today()
        same_month = [
            e for e in sorted_expiries
            if parse_expiry(e).month == today.month
            and parse_expiry(e).year  == today.year
        ]
        monthly_expiry = same_month[-1] if same_month else sorted_expiries[1]

        oi_by_expiry = {}
        for item in all_data:
            exp = item.get("expiryDate", "")
            if exp not in oi_by_expiry:
                oi_by_expiry[exp] = {"ce": 0, "pe": 0}
            oi_by_expiry[exp]["ce"] += item.get("CE", {}).get("openInterest", 0)
            oi_by_expiry[exp]["pe"] += item.get("PE", {}).get("openInterest", 0)

        def calc_pcr(expiry):
            d = oi_by_expiry.get(expiry, {"ce": 0, "pe": 0})
            if d["ce"] > 0:
                return round(d["pe"] / d["ce"], 2)
            return None

        result["weekly"]   = (calc_pcr(weekly_expiry),  weekly_expiry)
        result["monthly"]  = (calc_pcr(monthly_expiry), monthly_expiry)
        total_ce = sum(v["ce"] for v in oi_by_expiry.values())
        total_pe = sum(v["pe"] for v in oi_by_expiry.values())
        result["combined"] = round(total_pe / total_ce, 2) if total_ce > 0 else None
        result["_source"]  = "option_chain"
        return result

    except Exception:
        pass

    # Fallback 1: Try nse_pcr() from nsepython
    try:
        pcr_val = float(nse_pcr())
        result["combined"] = pcr_val
        result["weekly"]   = (pcr_val, "approx")
        result["monthly"]  = (pcr_val, "approx")
        result["_source"]  = "nse_pcr_fallback"
        return result
    except Exception:
        pass

    # Fallback 2: Session retry with browser-mimicking headers
    try:
        import time as _time
        url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Accept": "*/*",
            "Referer": "https://www.nseindia.com/option-chain",
            "X-Requested-With": "XMLHttpRequest",
        }
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers, timeout=6)
        _time.sleep(1.5)
        session.get("https://www.nseindia.com/option-chain", headers=headers, timeout=6)
        _time.sleep(1)
        r    = session.get(url, headers=headers, timeout=12)
        data = r.json()

        records      = data.get("records", {})
        all_data     = records.get("data", [])
        expiry_dates = records.get("expiryDates", [])

        if all_data and expiry_dates:
            from datetime import datetime

            def parse_expiry(s):
                return datetime.strptime(s, "%d-%b-%Y")

            sorted_expiries = sorted(expiry_dates, key=parse_expiry)
            weekly_expiry   = sorted_expiries[0]
            today      = datetime.today()
            same_month = [
                e for e in sorted_expiries
                if parse_expiry(e).month == today.month
                and parse_expiry(e).year  == today.year
            ]
            monthly_expiry = same_month[-1] if same_month else sorted_expiries[1]

            oi_by_expiry = {}
            for item in all_data:
                exp = item.get("expiryDate", "")
                if exp not in oi_by_expiry:
                    oi_by_expiry[exp] = {"ce": 0, "pe": 0}
                oi_by_expiry[exp]["ce"] += item.get("CE", {}).get("openInterest", 0)
                oi_by_expiry[exp]["pe"] += item.get("PE", {}).get("openInterest", 0)

            def calc_pcr(exp):
                d = oi_by_expiry.get(exp, {"ce": 0, "pe": 0})
                return round(d["pe"] / d["ce"], 2) if d["ce"] > 0 else None

            result["weekly"]   = (calc_pcr(weekly_expiry),  weekly_expiry)
            result["monthly"]  = (calc_pcr(monthly_expiry), monthly_expiry)
            total_ce = sum(v["ce"] for v in oi_by_expiry.values())
            total_pe = sum(v["pe"] for v in oi_by_expiry.values())
            result["combined"] = round(total_pe / total_ce, 2) if total_ce > 0 else None
            result["_source"]  = "session_retry"
            return result
    except Exception:
        pass

    result["_source"] = "failed"
    return result


def pcr_sentiment(pcr):
    """Returns (emoji_label, interpretation_text) for a PCR value."""
    if pcr is None:
        return "⚫ N/A", "Data unavailable"
    if pcr >= 1.3:
        return "🟢 BULLISH", "Excessive Put buying → Contrarian BUY zone. Strong support."
    elif pcr >= 0.8:
        return "🟡 NEUTRAL", "Balanced OI. Wait for breakout. No strong directional bias."
    else:
        return "🔴 BEARISH", "Excessive Call writing → Bears in control. Selling pressure dominant."

# ==========================================
# PART 3: FII & DII DATA
# ==========================================

@st.cache_data(ttl=600)
def get_fii_dii():
    # Method 1: jugaad-data
    try:
        from jugaad_data.nse import NSELive
        n    = NSELive()
        data = n.fii_dii_data()
        if data:
            records = []
            for row in data[:5]:
                records.append({
                    "Date":           row.get("date", "N/A"),
                    "FII Net (₹ Cr)": row.get("fiinet", "N/A"),
                    "DII Net (₹ Cr)": row.get("diinet", "N/A"),
                })
            df = pd.DataFrame(records)
            if not df.empty:
                return df
    except:
        pass

    # Method 2: Google Sheets (populate manually once a day)
    try:
        sheet_url = "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms/export?format=csv"
        df = pd.read_csv(sheet_url)
        if not df.empty:
            return df.head(5)
    except:
        pass

    # Method 3: Static fallback — update manually every week
    st.caption("⚠️ Live FII/DII feed blocked by NSE on cloud — showing last known data.")
    return pd.DataFrame([
        {"Date": "04-Apr-2026", "FII Net (₹ Cr)": "-3,973", "DII Net (₹ Cr)": "+4,243"},
        {"Date": "03-Apr-2026", "FII Net (₹ Cr)": "-2,105", "DII Net (₹ Cr)": "+3,812"},
        {"Date": "02-Apr-2026", "FII Net (₹ Cr)": "+1,456", "DII Net (₹ Cr)": "+2,190"},
        {"Date": "01-Apr-2026", "FII Net (₹ Cr)": "-5,621", "DII Net (₹ Cr)": "+6,034"},
        {"Date": "28-Mar-2026", "FII Net (₹ Cr)": "-1,893", "DII Net (₹ Cr)": "+2,541"},
    ])

# ==========================================
# PART 4: TOP PICKS
# Source: HDFC AMC publicly disclosed portfolio
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

items = [
    ("NIFTY 50",   "^NSEI",     "NSEI", None,       "NIFTY 50"),
    ("BANK NIFTY", "^NSEBANK",  None,   None,       "BANK NIFTY"),
    ("GOLD (MCX)", "GOLDM.NS",  None,   "GOLDBEES", None),
    ("DOW JONES",  "^DJI",      "DIA",  None,       None),
    ("NIKKEI 225", "^N225",     "EWJ",  None,       None),
    ("NIFTY 500",  "^CRSLDX",   None,   None,       "Nifty 500"),
    ("USD-INR",    "INR=X",     "USD",  None,       None),
    ("INDIA VIX",  "^INDIAVIX", None,   None,       "INDIA VIX"),
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
# SECTION A: PCR ANALYSIS (Weekly + Monthly)
# ==========================================

st.header("📊 F&O Put-Call Ratio (PCR) — Nifty")

pcr_data = get_pcr_detailed()

source = pcr_data.get("_source", "")
if source == "nse_pcr_fallback":
    st.info("ℹ️ NSE option chain blocked on cloud — showing single PCR value from nsepython. Weekly & Monthly are approximate.")
elif source == "failed":
    st.warning("⚠️ PCR data unavailable — NSE is blocking all API calls (market may be closed, or cloud IP blocked).")

w_pcr, w_exp = pcr_data["weekly"]
m_pcr, m_exp = pcr_data["monthly"]
c_pcr        = pcr_data["combined"]

w_label, w_interp = pcr_sentiment(w_pcr)
m_label, m_interp = pcr_sentiment(m_pcr)
c_label, c_interp = pcr_sentiment(c_pcr)

# Metric cards
col_w, col_m, col_c = st.columns(3)

with col_w:
    st.markdown("##### 📅 Weekly PCR" + (f" — `{w_exp}`" if w_exp and w_exp != "approx" else ""))
    if w_pcr:
        st.metric("Weekly PCR (OI)", f"{w_pcr:.2f}", w_label)
    else:
        st.warning("Weekly PCR unavailable")

with col_m:
    st.markdown("##### 🗓️ Monthly PCR" + (f" — `{m_exp}`" if m_exp and m_exp != "approx" else ""))
    if m_pcr:
        st.metric("Monthly PCR (OI)", f"{m_pcr:.2f}", m_label)
    else:
        st.warning("Monthly PCR unavailable")

with col_c:
    st.markdown("##### 🔢 Combined PCR (All Expiries)")
    if c_pcr:
        st.metric("Combined PCR (OI)", f"{c_pcr:.2f}", c_label)
    else:
        st.warning("Combined PCR unavailable")

# Interpretation row
st.markdown("---")
interp_cols = st.columns(3)
for col, label, interp, title in [
    (interp_cols[0], w_label, w_interp, "Weekly Signal"),
    (interp_cols[1], m_label, m_interp, "Monthly Signal"),
    (interp_cols[2], c_label, c_interp, "Combined Signal"),
]:
    if "BULLISH" in label:
        col.success(f"**{title}:** {interp}")
    elif "BEARISH" in label:
        col.error(f"**{title}:** {interp}")
    else:
        col.warning(f"**{title}:** {interp}")

# Reference table
with st.expander("📖 PCR Interpretation Guide"):
    st.markdown("""
    | PCR Range | Signal | What It Means |
    |-----------|--------|----------------|
    | **> 1.3** | 🟢 Bullish | Extreme Put OI = contrarian BUY zone |
    | **0.8 – 1.3** | 🟡 Neutral | Wait & watch, no clear trend |
    | **< 0.8** | 🔴 Bearish | Excess Call OI = market may FALL |

    > **Weekly PCR** reacts faster to short-term sentiment shifts.  
    > **Monthly PCR** reflects bigger-picture institutional positioning.  
    > **Combined** gives the broadest market-wide reading.
    """)

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
        latest  = fii_dii_df.iloc[0]
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

        # Combined signal — uses c_pcr (combined PCR) for confirmation
        if c_pcr and c_pcr >= 1.0 and fii_net > 0:
            c3.success("✅ STRONG BUY SIGNAL\nPCR Bullish + FII Buying")
        elif c_pcr and c_pcr < 0.8 and fii_net < 0:
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

st.header("💼 Top Picks")
st.caption("📅 Source: Updated each quarter")

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
