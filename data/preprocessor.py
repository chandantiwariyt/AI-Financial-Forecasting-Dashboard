import pandas as pd
import numpy as np


def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add technical indicators to stock DataFrame (expects 'Close' column)."""
    df['MA_20']  = df['Close'].rolling(window=20).mean()
    df['MA_50']  = df['Close'].rolling(window=50).mean()
    df['MA_200'] = df['Close'].rolling(window=200).mean()

    delta = df['Close'].diff()
    gain  = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss  = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    # Guard against division by zero when loss is 0 (stock only goes up)
    rs    = gain / loss.replace(0, np.nan)
    df['RSI'] = 100 - (100 / (1 + rs))

    df['BB_Upper'] = df['MA_20'] + (df['Close'].rolling(20).std() * 2)
    df['BB_Lower'] = df['MA_20'] - (df['Close'].rolling(20).std() * 2)

    exp1 = df['Close'].ewm(span=12).mean()
    exp2 = df['Close'].ewm(span=26).mean()
    df['MACD']        = exp1 - exp2
    df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()

    df['Daily_Return']  = df['Close'].pct_change()
    df['Volatility_30'] = df['Daily_Return'].rolling(30).std() * np.sqrt(252)

    return df.dropna()


def prepare_prophet_data(df: pd.DataFrame) -> pd.DataFrame:
    """Convert stock DataFrame to Prophet format (ds, y columns)."""
    prophet_df = df[['Date', 'Close']].copy()
    prophet_df.columns = ['ds', 'y']
    prophet_df['ds'] = prophet_df['ds'].dt.tz_localize(None)
    return prophet_df


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess raw stock data for Prophet model.
    Converts fetch_data() output to Prophet-compatible format with ds/y columns.
    """
    if df.empty:
        return df

    result = df[['Date', 'Close']].copy()
    result.columns = ['ds', 'y']
    result = result.dropna(subset=['ds', 'y'])

    # Remove timezone if present
    if result['ds'].dt.tz is not None:
        result['ds'] = result['ds'].dt.tz_localize(None)

    return result
