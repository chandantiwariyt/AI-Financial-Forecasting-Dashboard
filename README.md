# >![alt text](niveshx-logo-cropped) NiveshX

NiveshX is an AI-powered financial forecasting dashboard for Indian and global market symbols. It combines live market data, Prophet forecasting, stock comparison, simple AI-style insights, and PDF report export in a cleaner investor-facing Streamlit interface.


## 🚀 How to Run
Live App [Click here](https://ai-financial-forecasting-dashboard.onrender.com/)

## 📊 Sample Tickers
- Indian Stocks: RELIANCE.NS, TCS.NS, HDFCBANK.NS
- US Stocks: AAPL, MSFT, GOOGL

## Current Version

Suggested release version: `v1.1.0`

This version fixes stock pricing for Indian-listed tickers (.NS/.BO) which were incorrectly inflated by USD-INR conversion. Also introduces multi-page architecture, NiveshX branding, and a polished top-bar navigation.

## What's New In This Update

- Rebranded the product from FinAI Dashboard / FinAI Pro to NiveshX.
- Added the NiveshX logo as a local app asset.
- Added a saffron, white, and green visual system.
- Moved navigation from the sidebar to a Groww-style top tab bar.
- Added a top stock search box for the global ticker.
- Added a compact live data and USD-INR status in the top bar.
- Added a Login / Feedback button with a local feedback form.
- Improved top navigation text contrast so inactive tabs stay readable on the white header.
- Cleaned the stock search input focus style to remove default red/black border artifacts.
- Redesigned Dashboard metric cards and charts.
- Redesigned Compare as a single card with a central VS marker.
- Added full-width saffron CTA buttons.
- Updated Forecast and Compare pages to keep the same function flow with cleaner cards.
- Improved forecast input cleanup so invalid close prices do not produce `nan%`.
- Added safer dashboard handling for missing recent close prices.

## Features

### Dashboard

- Live stock price data from Yahoo Finance via `yfinance`.
- Global ticker search shared across the app.
- Top navigation for Dashboard, Forecast, Insights, and Compare.
- Login / Feedback form for quick product feedback.
- Price, change, volume, and trend cards.
- Interactive historical close-price chart.
- Simple market insight message.

### Forecast

- Prophet-based time-series forecasting.
- Forecast windows: 30 days, 90 days, and 1 year.
- Forecast chart with historical price, prediction line, and confidence band.
- Predicted price, trend, confidence, and AI-style summary.

### Compare

- Compare two symbols side by side.
- Relative performance chart with base value set to 100.
- Performance cards for both stocks.
- AI-style outperforming/underperforming insight.

### Insights

- Selected stock summary.
- Trend, volatility, and recommendation cards.
- PDF report generation and download.

## Tech Stack

| Area | Tools |
| --- | --- |
| App framework | Streamlit |
| Market data | yfinance |
| Forecasting | Prophet |
| Charts | Plotly |
| Data handling | Pandas, NumPy |
| Reports | Local PDF utility |

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip or virtual environment

### Installation

```bash
# Clone the repository
git clone https://github.com/chandantiwariyt/AI-Financial-Forecasting-Dashboard.git
cd personal-finance-tracker

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## 🔮 Future Improvements
- [ ] Adding Mutual Funds
- [ ] Nifty 50

---

## 👤 Author
Built by **Chandan Tiwari** — [LinkedIn](https://www.linkedin.com/in/chandantiwari4/) · [GitHub](https://github.com/chandantiwariyt)
---

## 📄 License
This project is open source and available under the [MIT License](LICENSE).
