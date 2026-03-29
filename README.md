# 📈 AI Financial Forecasting Dashboard

An institutional-grade financial forecasting dashboard built with Python and Streamlit.

## 🔍 Features
- Live stock price data via yFinance (NSE, BSE, NYSE supported)
- 90-day AI forecast using Facebook Prophet ML model
- FRED macro indicators (GDP, Inflation, Fed Rate, VIX)
- Technical indicators — RSI, MACD, Bollinger Bands, Moving Averages
- Risk metrics — Sharpe Ratio, Sortino Ratio, Max Drawdown
- Company fundamentals — Market Cap, P/E Ratio, Revenue, Profit Margin
- Interactive Plotly charts with confidence intervals

## 🛠 Tech Stack
- Python, Streamlit, Prophet, TensorFlow
- yFinance, FRED API, Plotly, Pandas, Scikit-learn

## 🚀 How to Run
pip install -r requirements.txt
streamlit run app.py
Live App https://ai-financial-forecasting-dashboard.onrender.com/

## 📊 Sample Tickers
- Indian Stocks: RELIANCE.NS, TCS.NS, HDFCBANK.NS
- US Stocks: AAPL, MSFT, GOOGL
```

Then push to GitHub:
```
git add README.md
git commit -m "Added README"
git push
