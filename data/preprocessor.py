import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df['MA_20']  = df['Close'].rolling(window=20).mean()
    df['MA_50']  = df['Close'].rolling(window=50).mean()
    df['MA_200'] = df['Close'].rolling(window=200).mean()

    delta = df['Close'].diff()
    gain  = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss  = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs    = gain / loss
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
    prophet_df = df[['Date', 'Close']].copy()
    prophet_df.columns = ['ds', 'y']
    prophet_df['ds'] = prophet_df['ds'].dt.tz_localize(None)
    return prophet_df

def prepare_lstm_data(df: pd.DataFrame, lookback: int = 60):
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df[['Close']].values)

    X, y = [], []
    for i in range(lookback, len(scaled)):
        X.append(scaled[i-lookback:i, 0])
        y.append(scaled[i, 0])

    return np.array(X), np.array(y), scaler