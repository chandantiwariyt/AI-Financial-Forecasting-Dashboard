import yfinance as yf
import pandas as pd
from fredapi import Fred
import os
from dotenv import load_dotenv

load_dotenv()

# =========================
# 📊 STOCK DATA (HISTORICAL)
# =========================
def get_stock_data(ticker: str, period: str = "2y") -> pd.DataFrame:
    stock = yf.Ticker(ticker)
    
    df = stock.history(period=period)

    # 🔥 DEBUG PRINT
    print(f"Ticker: {ticker}")
    print(df.tail())

    if df.empty:
        print("⚠️ No data returned from Yahoo")

    df.reset_index(inplace=True)

    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])

    return df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']] if not df.empty else df


# =========================
# ⚡ LIVE PRICE (FAST)
# =========================
def get_live_price(ticker: str) -> float:
    stock = yf.Ticker(ticker)

    try:
        live_price = stock.fast_info.get('lastPrice', None)

        if live_price is None:
            live_price = stock.info.get('currentPrice', None)

        return live_price

    except Exception:
        return None


# =========================
# 🧾 COMPANY FINANCIALS
# =========================
def get_company_financials(ticker: str) -> dict:
    stock = yf.Ticker(ticker)

    return {
        'income_statement': stock.financials,
        'balance_sheet': stock.balance_sheet,
        'cash_flow': stock.cashflow,
        'info': stock.info
    }


# =========================
# 🌍 MACRO DATA (FRED)
# =========================
def get_macro_indicators() -> pd.DataFrame:
    fred = Fred(api_key=os.getenv("FRED_API_KEY"))

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
        except Exception:
            macro_df[name] = None

    macro_df.reset_index(inplace=True)
    macro_df.rename(columns={'index': 'Date'}, inplace=True)

    return macro_df


# =========================
# 🚀 SNAPSHOT (OPTIONAL PRO FEATURE)
# =========================
def get_company_snapshot(ticker: str) -> dict:
    stock = yf.Ticker(ticker)

    try:
        fast = stock.fast_info

        return {
            "price": fast.get("lastPrice"),
            "market_cap": fast.get("marketCap"),
            "volume": fast.get("lastVolume")
        }

    except Exception:
        return {}