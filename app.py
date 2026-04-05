import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from data.fetcher import get_stock_data, get_company_financials, get_live_price
from data.preprocessor import add_technical_indicators, prepare_prophet_data
from models.prophet_model import run_prophet_forecast
from components.metrics import calculate_risk_metrics

# =========================
# ⚙️ PAGE CONFIG
# =========================
st.set_page_config(
    page_title="AI Financial Dashboard",
    layout="wide",
    page_icon="📊"
)

# =========================
# 🎨 STYLE (DARK MODE)
# =========================
st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 📊 HEADER
# =========================
st.markdown("""
# 📊 AI Financial Dashboard
### Real-time Analytics | Forecasting | Valuation
""")

# =========================
# 🎛️ TOP CONTROLS
# =========================
colA, colB, colC = st.columns([2,2,1])

with colA:
    ticker = st.text_input("Ticker", value="RELIANCE.NS")

with colB:
    forecast_days = st.slider("Forecast Days", 30, 365, 90)

with colC:
    st.write("")
    st.write("")
    refresh = st.button("🔄 Refresh")

# Auto-fix ticker (user friendly)
if "." not in ticker:
    ticker = ticker.upper() + ".NS"

# =========================
# 📥 LOAD DATA
# =========================
with st.spinner("🔄 Fetching market data..."):
    df = get_stock_data(ticker, period="3y")

# Fallback logic
if df.empty:
    st.warning("⚠️ Trying alternate exchange...")
    
    if ticker.endswith(".NS"):
        alt_ticker = ticker.replace(".NS", ".BO")
        df = get_stock_data(alt_ticker)

    if df.empty:
        st.error("❌ No data found. Try AAPL, TSLA, RELIANCE.NS")
        st.stop()

df = add_technical_indicators(df)

# =========================
# ⚡ LIVE PRICE + KPI
# =========================
live_price = get_live_price(ticker)
latest = live_price if live_price else df['Close'].iloc[-1]

prev = df['Close'].iloc[-2] if len(df) > 1 else latest
change_pct = ((latest - prev) / prev) * 100 if prev != 0 else 0

risk_metrics = calculate_risk_metrics(df['Daily_Return'].dropna())

st.markdown("## 📌 Key Metrics")

k1, k2, k3, k4 = st.columns(4)

k1.metric("💰 Price", f"₹{latest:.2f}", f"{change_pct:.2f}%")
k2.metric("📊 Volatility", f"{df['Volatility_30'].iloc[-1]*100:.1f}%")
k3.metric("⚖️ Sharpe", f"{risk_metrics['Sharpe_Ratio']:.2f}")
k4.metric("📉 Drawdown", f"{risk_metrics['Max_Drawdown']}%")

# Momentum indicator
if change_pct > 0:
    st.success("📈 Bullish Momentum")
else:
    st.error("📉 Bearish Momentum")

# =========================
# 📊 MAIN LAYOUT
# =========================
left, right = st.columns([2,1])

# LEFT: Chart
with left:
    st.subheader("📊 Price + Forecast")

    prophet_df = prepare_prophet_data(df)
    forecast = run_prophet_forecast(prophet_df, forecast_days)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['Close'],
        name='Actual Price',
        line=dict(color='#00d4ff')
    ))

    fig.add_trace(go.Scatter(
        x=forecast['ds'], y=forecast['yhat'],
        name='Forecast',
        line=dict(color='#ff6b35', dash='dash')
    ))

    fig.update_layout(template='plotly_dark', height=500)
    st.plotly_chart(fig, use_container_width=True)

# RIGHT: Summary
with right:
    st.subheader("📌 Summary")

    st.write(f"**Ticker:** {ticker}")
    st.write(f"**Price:** ₹{latest:.2f}")
    st.write(f"**Change:** {change_pct:.2f}%")

    trend = "📈 Bullish" if forecast['yhat'].iloc[-1] > latest else "📉 Bearish"
    st.write(f"**Forecast:** {trend}")

# =========================
# 📉 TABS SECTION
# =========================
tab1, tab2, tab3 = st.tabs(["📈 Technicals", "🏦 Fundamentals", "📊 Data"])

# Technicals
with tab1:
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df['Date'], y=df['Close'], name='Price'))
    fig2.add_trace(go.Scatter(x=df['Date'], y=df['MA_20'], name='MA 20'))
    fig2.add_trace(go.Scatter(x=df['Date'], y=df['MA_50'], name='MA 50'))
    fig2.update_layout(template='plotly_dark')
    st.plotly_chart(fig2, use_container_width=True)

# Fundamentals
with tab2:
    financials = get_company_financials(ticker)
    info = financials.get('info', {})

    f1, f2, f3, f4 = st.columns(4)

    f1.metric("Market Cap", f"₹{info.get('marketCap', 0)/1e9:.1f}B")
    f2.metric("P/E", info.get('trailingPE', 'N/A'))
    f3.metric("Revenue", f"₹{info.get('totalRevenue', 0)/1e9:.1f}B")
    f4.metric("Margin", f"{info.get('profitMargins', 0)*100:.1f}%")

# Raw data
with tab3:
    st.dataframe(df.tail())

# =========================
# 🕒 FOOTER
# =========================
st.caption(f"Last Updated: {pd.Timestamp.now().strftime('%H:%M:%S')}")