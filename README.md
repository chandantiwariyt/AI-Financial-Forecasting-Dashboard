# NiveshX

<p align="center">
  <img src="assets/niveshx-logo-cropped.png" alt="NiveshX Logo" width="280">
</p>

NiveshX is an AI-powered financial forecasting dashboard for Indian and global market symbols. It combines live market data, Prophet forecasting, stock comparison, simple AI-style insights, and PDF report export in a cleaner investor-facing Streamlit interface.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red)
![Plotly](https://img.shields.io/badge/Plotly-6.x-purple)
![Prophet](https://img.shields.io/badge/Prophet-Forecasting-green)
![yfinance](https://img.shields.io/badge/yfinance-Market%20Data-blue)

## 🔴 Live Demo

Run locally using the steps below, or open the deployed dashboard: [Live🔴](https://ai-financial-forecasting-dashboard.onrender.com/)

## Sample Tickers

- Indian stocks: `RELIANCE.NS`, `TCS.NS`, `HDFCBANK.NS`
- Plain Indian search fallback: `RELIANCE` resolves to `RELIANCE.NS` if the exact symbol has no Yahoo Finance data.
- US stocks: `AAPL`, `MSFT`, `GOOGL`

## Current Version

Suggested release version: `v1.2.2`

This version fixes share-price accuracy, uses live dashboard quotes when available, keeps Indian-listed prices in INR without double conversion, and documents the NiveshX UI refresh.

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
- Fixed Indian stock prices so `.NS` and `.BO` tickers are not multiplied by USD-INR.
- Switched Yahoo Finance history calls to unadjusted `Close` prices for clearer share-price display.
- Added live quote usage on the Dashboard, with last close as the fallback.
- Added ticker fallback so plain Indian symbols such as `RELIANCE` can resolve to `.NS`.
- Added a safe yfinance cache location to avoid local cache database crashes.
- Redesigned Dashboard metric cards and charts.
- Redesigned Compare as a single card with a central VS marker.
- Updated Forecast and Compare pages to keep the same function flow with cleaner cards.
- Improved forecast input cleanup so invalid close prices do not produce `nan%`.

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
| Reports | ReportLab |

## Run Locally

From VS Code or PowerShell:

```powershell
cd "C:\Users\kunal\OneDrive\Financial ProJects\AI financial Forcasting Dashboards"
.\venv\Scripts\activate
streamlit run app.py
```

If `streamlit` is not recognized:

```powershell
.\venv\Scripts\python.exe -m streamlit run app.py
```

Then open the local URL printed by Streamlit, usually:

```text
http://localhost:8501
```

## Release This As A New Version

Use this checklist after testing locally:

1. Review changed files:

```powershell
git status
git diff
```

2. Stage only the files for this release:

```powershell
git add app.py dashboard.py forecast.py data/fetcher.py README.md assets/niveshx-logo.png assets/niveshx-logo-cropped.png
```

3. Commit the update:

```powershell
git commit -m "Release NiveshX price accuracy update"
```

4. Create a version tag:

```powershell
git tag v1.2.2
```

5. Push the code and tag:

```powershell
git push origin main
git push origin v1.2.2
```

6. Redeploy:

- If Render is connected to GitHub, pushing to `main` should trigger a deploy automatically.
- If auto-deploy is disabled, open the Render dashboard and click `Manual Deploy`.
- After deployment, verify Dashboard, Forecast, Compare, and Insights in the live app.

## Future Improvements

- Add mutual fund views.
- Add Nifty 50 watchlist support.
- Add persisted user feedback storage.

## Author

Built by Chandan Tiwari: [LinkedIn](https://www.linkedin.com/in/chandantiwari4/) | [GitHub](https://github.com/chandantiwariyt)

## License

This project is open source and available under the MIT License.
