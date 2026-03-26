import streamlit as st
import plotly.graph_objects as go
from data.fetcher import get_stock_data, get_company_financials
from data.preprocessor import add_technical_indicators, prepare_prophet_data
from models.prophet_model import run_prophet_forecast
from components.metrics import calculate_forecast_accuracy, calculate_risk_metrics
import pandas as pd

st.set_page_config(page_title="AI Financial Forecasting Dashboard", layout="wide", page_icon="📈")

# --- Sidebar ---
st.sidebar.title("⚙️ Dashboard Controls")
ticker        = st.sidebar.text_input("Stock Ticker", value="RELIANCE.NS")
forecast_days = st.sidebar.slider("Forecast Horizon (Days)", 30, 365, 90)

# --- Header ---
st.title("📈 AI Financial Forecasting Dashboard")
st.caption("Institutional-grade forecasting powered by ML")

# --- Load Data ---
with st.spinner("Fetching market data..."):
    df = get_stock_data(ticker, period="3y")
    df = add_technical_indicators(df)

# --- KPI Row ---
col1, col2, col3, col4 = st.columns(4)
latest       = df['Close'].iloc[-1]
prev         = df['Close'].iloc[-2]
change_pct   = ((latest - prev) / prev) * 100
risk_metrics = calculate_risk_metrics(df['Daily_Return'].dropna())

col1.metric("Current Price",     f"₹{latest:.2f}",                f"{change_pct:.2f}%")
col2.metric("Volatility (Ann.)", f"{df['Volatility_30'].iloc[-1]*100:.1f}%")
col3.metric("Sharpe Ratio",      risk_metrics['Sharpe_Ratio'])
col4.metric("Max Drawdown",      f"{risk_metrics['Max_Drawdown']}%")

# --- Forecast Chart ---
st.subheader("📊 Price History + AI Forecast")
prophet_df = prepare_prophet_data(df)
forecast   = run_prophet_forecast(prophet_df, forecast_days)

fig = go.Figure()
fig.add_trace(go.Scatter(x=df['Date'],       y=df['Close'],            name='Actual Price', line=dict(color='#00d4ff')))
fig.add_trace(go.Scatter(x=forecast['ds'],   y=forecast['yhat'],       name='Forecast',     line=dict(color='#ff6b35', dash='dash')))
fig.add_trace(go.Scatter(x=forecast['ds'],   y=forecast['yhat_upper'], name='Upper CI',     line=dict(color='rgba(255,107,53,0.2)')))
fig.add_trace(go.Scatter(x=forecast['ds'],   y=forecast['yhat_lower'], name='Lower CI',     fill='tonexty', line=dict(color='rgba(255,107,53,0.2)')))
fig.update_layout(template='plotly_dark', height=500, hovermode='x unified')
st.plotly_chart(fig, use_container_width=True)

# --- Technical Indicators ---
st.subheader("📉 Technical Indicators")
tab1, tab2, tab3 = st.tabs(["Moving Averages", "RSI", "MACD"])

with tab1:
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df['Date'], y=df['Close'],  name='Price'))
    fig2.add_trace(go.Scatter(x=df['Date'], y=df['MA_20'],  name='20-Day MA'))
    fig2.add_trace(go.Scatter(x=df['Date'], y=df['MA_50'],  name='50-Day MA'))
    fig2.add_trace(go.Scatter(x=df['Date'], y=df['MA_200'], name='200-Day MA'))
    fig2.update_layout(template='plotly_dark', height=400)
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=df['Date'], y=df['RSI'], name='RSI', line=dict(color='orange')))
    fig3.add_hline(y=70, line_dash="dash", line_color="red",   annotation_text="Overbought")
    fig3.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")
    fig3.update_layout(template='plotly_dark', height=300)
    st.plotly_chart(fig3, use_container_width=True)

with tab3:
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=df['Date'], y=df['MACD'],        name='MACD',   line=dict(color='blue')))
    fig4.add_trace(go.Scatter(x=df['Date'], y=df['MACD_Signal'], name='Signal', line=dict(color='red')))
    fig4.update_layout(template='plotly_dark', height=300)
    st.plotly_chart(fig4, use_container_width=True)

# --- Company Fundamentals ---
st.subheader("🏦 Company Fundamentals")
financials = get_company_financials(ticker)
info       = financials['info']

fcol1, fcol2, fcol3, fcol4 = st.columns(4)
fcol1.metric("Market Cap",     f"₹{info.get('marketCap', 0)/1e9:.1f}B")
fcol2.metric("P/E Ratio",      info.get('trailingPE', 'N/A'))
fcol3.metric("Revenue",        f"₹{info.get('totalRevenue', 0)/1e9:.1f}B")
fcol4.metric("Profit Margin",  f"{info.get('profitMargins', 0)*100:.1f}%")