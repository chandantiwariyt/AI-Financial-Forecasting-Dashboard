import yfinance as yf
import pandas as pd
import streamlit as st
from fredapi import Fred
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# =========================
# 📊 STOCK DATA (MAIN FUNCTION)
# =========================
@st.cache_data(ttl=300, show_spinner=False)
def fetch_data(ticker: str, period: str = "2y") -> pd.DataFrame:
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
    except (ConnectionError, TimeoutError, ValueError) as e:
        logger.warning(f"Failed to fetch stock data for {ticker}: {e}")
        return pd.DataFrame()

    if df.empty:
        logger.info(f"No data returned from Yahoo for {ticker}")
        return df

    df.reset_index(inplace=True)

    # Ensure proper datetime
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])

    return df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]


# =========================
# ⚡ LIVE PRICE
# =========================
@st.cache_data(ttl=60, show_spinner=False)
def get_live_price(ticker: str) -> float:
    try:
        stock = yf.Ticker(ticker)
        live_price = stock.fast_info.get('lastPrice', None)

        if live_price is None:
            live_price = stock.info.get('currentPrice', None)

        return live_price

    except (ConnectionError, TimeoutError, KeyError, ValueError) as e:
        logger.warning(f"Failed to get live price for {ticker}: {e}")
        return None


# =========================
# 🧾 COMPANY FINANCIALS
# =========================
@st.cache_data(ttl=600, show_spinner=False)
def get_company_financials(ticker: str) -> dict:
    try:
        stock = yf.Ticker(ticker)

        return {
            'income_statement': stock.financials,
            'balance_sheet': stock.balance_sheet,
            'cash_flow': stock.cashflow,
            'info': stock.info
        }

    except (ConnectionError, TimeoutError, KeyError, ValueError) as e:
        logger.warning(f"Failed to get financials for {ticker}: {e}")
        return {
            'income_statement': None,
            'balance_sheet': None,
            'cash_flow': None,
            'info': {}
        }


# =========================
# 🌍 MACRO DATA
# =========================
@st.cache_data(ttl=3600, show_spinner=False)
def get_macro_indicators() -> pd.DataFrame:
    fred_key = os.getenv("FRED_API_KEY")

    if not fred_key:
        logger.error("FRED_API_KEY not set")
        return pd.DataFrame()

    fred = Fred(api_key=fred_key)

    indicators = {
        'GDP': 'GDP',
        'Inflation': 'CPIAUCSL',
        'Fed_Rate': 'FEDFUNDS',
        'Unemployment': 'UNRATE',
        'VIX': 'VIXCLS'
    }

    macro_df = pd.DataFrame()

    for name, series_id in indicators.items():
        try:
            series = fred.get_series(series_id, observation_start='2020-01-01')
            macro_df[name] = series
        except Exception as e:
            logger.warning(f"Failed to fetch {name}: {e}")
            macro_df[name] = None

    macro_df.reset_index(inplace=True)
    macro_df.rename(columns={'index': 'Date'}, inplace=True)

    return macro_df


# =========================
# 🚀 SNAPSHOT
# =========================
@st.cache_data(ttl=60, show_spinner=False)
def get_company_snapshot(ticker: str) -> dict:
    try:
        stock = yf.Ticker(ticker)
        fast = stock.fast_info

        return {
            "price": fast.get("lastPrice"),
            "market_cap": fast.get("marketCap"),
            "volume": fast.get("lastVolume")
        }

    except Exception as e:
        logger.warning(f"Failed to get snapshot for {ticker}: {e}")
        return {}