import streamlit as st
import yfinance as yf
import pandas as pd
import feedparser
import time
import requests
import json
from nsepython import *

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(page_title="Market War-Room", layout="wide")

# ==========================================
# ADMIN PASSWORD & SIDEBAR
# ==========================================
ADMIN_PASSWORD = "123@123@123"  # ← change this to your own password

with st.sidebar:
    st.title("⚙️ Settings")
    st.markdown("---")
    st.success("🚀 **Created by Hardik Jani**")
    if st.button('🔄 Hard Reset App'):
        st.cache_data.clear()
        st.rerun()
    st.write("Market War-Room v8.0 (Ultimate)")
    st.caption(f"Last Sync: {time.strftime('%H:%M:%S')}")
    st.markdown("---")
    st.markdown("#### 🔐 Admin PCR Update")
    admin_pass = st.text_input("Password", type="password", key="admin_password")
    if admin_pass:
        if admin_pass == ADMIN_PASSWORD:
            st.success("✅ Admin access granted")
        else:
            st.error("❌ Wrong password")

# Define is_admin AFTER the sidebar block, outside it
is_admin = (admin_pass == ADMIN_PASSWORD) if admin_pass else False

AV_KEY = st.secrets.get("AV_KEY", "demo")

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
        r    = requests.get(url, timeout=10)
        data = r.json().get("Global Quote", {})
        price = float(data.get("05. price", 0))
        pct   = float(data.get("10. change percent", "0%").replace("%", ""))
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
            cur  = float(df['Close'].iloc[-1])
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
# PART 2: PCR HELPERS
# ==========================================

PCR_FILE = "pcr_values.json"

def load_pcr():
    try:
        with open(PCR_FILE, "r") as f:
            return json.load(f)
    except:
        return {
            "w_pcr": 0.0,
            "m_pcr": 0.0,
            "w_exp": "",
            "m_exp": "",
            "updated_at": "Not updated yet"
        }

def save_pcr(data):
    with open(PCR_FILE, "w") as f:
        json.dump(data, f)

def pcr_sentiment(pcr):
    """Returns (emoji_label, interpretation_text) for a PCR value."""
    if pcr is None or pcr == 0.0:
        return "⚫ N/A", "No value entered yet."
    if pcr >= 1.3:
        return "🟢 BULLISH", "Excessive Put buying → Contrarian BUY zone. Strong support."
    elif pcr >= 0.8:
        return "🟡 NEUTRAL", "Balanced OI. Wait for breakout. No strong directional bias."
    else:
        return "🔴 BEARISH", "Excessive Call writing → Bears in control. Selling pressure dominant."

# ==========================================
# PART 3: TOP PICKS
# Source: HDFC AMC publicly disclosed portfolio
# Update each quarter from: https://www.hdfcfund.com/
# ==========================================

HDFC_MF_PICKS = {
    "Large Cap (Top 2 New Buys)": [
        {
            "Stock": "Bharti Airtel",
            "Sector": "Telecom",
            "Reason to buy": "5G rollout play, consistent ARPU growth, dominant market share",
            "Approx Qty Added": "~15 lakh shares"
        },
        {
            "Stock": "Larsen & Toubro",
            "Sector": "Capital Goods / Infra",
            "Reason to buy": "Order book at record ₹5.5L Cr, govt capex supercycle beneficiary",
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
    ("GOLD (Bees)", "GOLDM.NS",  None,   "GOLDBEES", None),
    ("DOW JONES",  "^DJI",      "DIA",  None,       None),
    ("NIKKEI 225", "NKY=F", "EWJ", None, None),  # Nikkei futures, more reliable
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
# SECTION A: PCR ANALYSIS
# ==========================================

st.header("📊 F&O Put-Call Ratio (PCR) — Nifty")

pcr_store = load_pcr()

# ── Admin sees input fields ───────────────────────────────────
if is_admin:
    st.info("✅ Admin mode — your entries will be visible to all users once saved.")
    inp_col1, inp_col2 = st.columns(2)

    with inp_col1:
        weekly_expiry_label = st.text_input(
            "📅 Weekly Expiry Date (e.g. 10-Apr-2025)",
            value=pcr_store["w_exp"],
            placeholder="10-Apr-2025"
        )
        w_pcr = st.number_input(
            "Weekly PCR Value",
            min_value=0.0,
            max_value=5.0,
            value=float(pcr_store["w_pcr"]),
            step=0.01,
            format="%.2f",
            help="Enter Weekly PCR from NSE option chain (Put OI / Call OI)"
        )

    with inp_col2:
        monthly_expiry_label = st.text_input(
            "🗓️ Monthly Expiry Date (e.g. 24-Apr-2025)",
            value=pcr_store["m_exp"],
            placeholder="24-Apr-2025"
        )
        m_pcr = st.number_input(
            "Monthly PCR Value",
            min_value=0.0,
            max_value=5.0,
            value=float(pcr_store["m_pcr"]),
            step=0.01,
            format="%.2f",
            help="Enter Monthly PCR from NSE option chain (Put OI / Call OI)"
        )

    if st.button("💾 Save & Publish PCR to all users"):
        save_pcr({
            "w_pcr": w_pcr,
            "m_pcr": m_pcr,
            "w_exp": weekly_expiry_label,
            "m_exp": monthly_expiry_label,
            "updated_at": time.strftime("%d-%b-%Y %H:%M:%S")
        })
        st.success("✅ PCR values saved! All users will now see the updated values.")
        st.rerun()

# ── Everyone else sees saved values only ─────────────────────
else:
    w_pcr                = float(pcr_store["w_pcr"])
    m_pcr                = float(pcr_store["m_pcr"])
    weekly_expiry_label  = pcr_store["w_exp"]
    monthly_expiry_label = pcr_store["m_exp"]
    st.caption(f"🕐 PCR last updated by admin: **{pcr_store['updated_at']}**")

st.markdown("---")

# ── Sentiment calculation ─────────────────────────────────────
w_label, w_interp = pcr_sentiment(w_pcr)
m_label, m_interp = pcr_sentiment(m_pcr)

if w_pcr > 0 and m_pcr > 0:
    c_pcr = round((w_pcr + m_pcr) / 2, 2)
elif w_pcr > 0:
    c_pcr = w_pcr
elif m_pcr > 0:
    c_pcr = m_pcr
else:
    c_pcr = None

c_label, c_interp = pcr_sentiment(c_pcr)

# ── Metric cards ──────────────────────────────────────────────
col_w, col_m, col_c = st.columns(3)

with col_w:
    expiry_str = f" — `{weekly_expiry_label}`" if weekly_expiry_label else ""
    st.markdown(f"##### 📅 Weekly PCR{expiry_str}")
    if w_pcr > 0:
        st.metric("Weekly PCR (OI)", f"{w_pcr:.2f}", w_label)
    else:
        st.info("PCR not updated yet")

with col_m:
    expiry_str = f" — `{monthly_expiry_label}`" if monthly_expiry_label else ""
    st.markdown(f"##### 🗓️ Monthly PCR{expiry_str}")
    if m_pcr > 0:
        st.metric("Monthly PCR (OI)", f"{m_pcr:.2f}", m_label)
    else:
        st.info("PCR not updated yet")

with col_c:
    st.markdown("##### 🔢 Combined PCR (Avg)")
    if c_pcr:
        st.metric("Combined PCR", f"{c_pcr:.2f}", c_label)
    else:
        st.info("PCR not updated yet")

# ── Signal interpretation row ─────────────────────────────────
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
    elif "NEUTRAL" in label:
        col.warning(f"**{title}:** {interp}")
    else:
        col.info(f"**{title}:** {interp}")

# ── Reference table ───────────────────────────────────────────
with st.expander("📖 PCR Interpretation Guide"):
    st.markdown("""
    | PCR Range | Signal | What It Means |
    |-----------|--------|----------------|
    | **> 1.3** | 🟢 Bullish | Extreme Put OI = contrarian BUY zone |
    | **0.8 – 1.3** | 🟡 Neutral | Wait & watch, no clear trend |
    | **< 0.8** | 🔴 Bearish | Excess Call OI = market may FALL |

    > **Weekly PCR** reacts faster to short-term sentiment shifts.  
    > **Monthly PCR** reflects bigger-picture institutional positioning.  
    > **Combined** is a simple average of both — broadest reading.

    💡 **Where to get PCR?** NSE website → F&O → Option Chain → NIFTY  
    Or use [Sensibull](https://sensibull.com) / [Opstra](https://opstra.definedge.com)
    """)

st.divider()

# ==========================================
# SECTION B: HDFC MF TOP PICKS
# ==========================================

st.header("💼 Top Picks")
st.caption("📅 Source: Updated each quarter")

for category, stocks in HDFC_MF_PICKS.items():
    st.subheader(f"📌 {category}")
    df = pd.DataFrame(stocks)
    st.dataframe(df, use_container_width=True, hide_index=True)


# ==========================================
# SECTION C: INDIAN MARKET NEWS & DATA
# ==========================================

st.header("📰 Indian Market — Latest News & Key Data")
st.caption("🔄 Auto-fetched from Economic Times, Moneycontrol & NSE announcements")

# ── News Feed Sources ─────────────────────────────────────────
NEWS_FEEDS = {
    "📊 Economic Times Markets": "https://economictimes.indiatimes.com/markets/rss.cms",
    "💹 Moneycontrol Top News":  "https://www.moneycontrol.com/rss/latestnews.xml",
    "🏦 NSE / BSE Updates":      "https://news.google.com/rss/search?q=NSE+BSE+India+stock+market&hl=en-IN&gl=IN&ceid=IN:en",
}

@st.cache_data(ttl=600)  # refresh every 10 minutes
def fetch_news(url):
    try:
        feed    = feedparser.parse(url)
        entries = []
        for entry in feed.entries[:6]:  # top 6 from each source
            entries.append({
                "title":     entry.get("title", "No Title"),
                "link":      entry.get("link",  "#"),
                "published": entry.get("published", ""),
                "summary":   entry.get("summary", "")[:180] + "..."
                             if len(entry.get("summary", "")) > 180
                             else entry.get("summary", "")
            })
        return entries
    except:
        return []

# ── Display news in tabs ──────────────────────────────────────
tab1, tab2, tab3 = st.tabs(list(NEWS_FEEDS.keys()))

for tab, (source_name, feed_url) in zip([tab1, tab2, tab3], NEWS_FEEDS.items()):
    with tab:
        articles = fetch_news(feed_url)
        if articles:
            for article in articles:
                with st.container():
                    col_text, col_link = st.columns([5, 1])
                    with col_text:
                        st.markdown(f"**{article['title']}**")
                        if article['summary']:
                            st.caption(article['summary'])
                        if article['published']:
                            st.caption(f"🕐 {article['published']}")
                    with col_link:
                        st.markdown(
                            f"<a href='{article['link']}' target='_blank'>"
                            f"<button style='background:#ff4b4b;color:white;"
                            f"border:none;padding:6px 12px;border-radius:6px;"
                            f"cursor:pointer;font-size:13px;'>Read →</button></a>",
                            unsafe_allow_html=True
                        )
                    st.markdown("---")
        else:
            st.warning(f"Could not fetch news from {source_name}. Check internet connection.")

# ── Key Market Data Points ────────────────────────────────────
st.markdown("### 📌 Key Data to Watch Today")

data_col1, data_col2, data_col3 = st.columns(3)

with data_col1:
    st.markdown("""
    **🗓️ Important Dates**
    - F&O Expiry: Every Thursday
    - Monthly Expiry: Last Thursday
    - Results Season: Apr–May / Oct–Nov
    - RBI Policy: Every 2 months
    """)

with data_col2:
    st.markdown("""
    **📉 Key Levels to Watch**
    - Nifty Support: Check Prev. Day Low
    - Nifty Resistance: Check Prev. Day High
    - Bank Nifty follows Nifty trend
    - VIX > 20 = High fear zone
    - VIX < 13 = Complacency zone
    """)

with data_col3:
    st.markdown("""
    **🔗 Useful Links**
    - [NSE Option Chain](https://www.nseindia.com/option-chain)
    - [NSE Announcements](https://www.nseindia.com/companies-listing/corporate-filings-announcements)
    - [RBI Website](https://www.rbi.org.in)
    - [SEBI Website](https://www.sebi.gov.in)
    - [Sensibull PCR](https://sensibull.com)
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
- 🔁 **Data Accuracy:** Live data depends on third-party APIs (NSE, Alpha Vantage). Occasional delays or unavailability may occur.
- 👤 **Your Responsibility:** All trading/investment decisions are solely your own. The creator is NOT responsible for any financial losses.

*Always consult a SEBI-registered financial advisor before making investment decisions.*
""")
