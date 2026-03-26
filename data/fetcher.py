import yfinance as yf
import pandas as pd
from fredapi import Fred
import os
from dotenv import load_dotenv

load_dotenv()

def get_stock_data(ticker: str, period: str = "2y") -> pd.DataFrame:
    stock = yf.Ticker(ticker)
    df = stock.history(period=period)
    df.reset_index(inplace=True)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    return df

def get_macro_indicators() -> pd.DataFrame:
    fred = Fred(api_key=os.getenv("FRED_API_KEY"))
    indicators = {
        'GDP':          'GDP',
        'Inflation':    'CPIAUCSL',
        'Fed_Rate':     'FEDFUNDS',
        'Unemployment': 'UNRATE',
        'VIX':          'VIXCLS'
    }
    macro_df = pd.DataFrame()
    for name, series_id in indicators.items():
        series = fred.get_series(series_id, observation_start='2020-01-01')
        macro_df[name] = series
    macro_df.reset_index(inplace=True)
    macro_df.rename(columns={'index': 'Date'}, inplace=True)
    return macro_df

def get_company_financials(ticker: str) -> dict:
    stock = yf.Ticker(ticker)
    return {
        'income_statement': stock.financials,
        'balance_sheet':    stock.balance_sheet,
        'cash_flow':        stock.cashflow,
        'info':             stock.info
    }