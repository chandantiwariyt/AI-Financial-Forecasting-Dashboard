import numpy as np
import streamlit as st

from data.fetcher import fetch_data
from utils.report import generate_report

# ---- Signal thresholds (documented so every card stays explainable) --------
# Momentum = % change in closing price over the trailing window below.
MOMENTUM_WINDOW = 20            # ~1 trading month
STRONG_MOVE_PCT = 3.0           # |momentum| >= this => a decisive up/down move
# Annualized volatility bands (daily-return std * sqrt(252)), expressed in %.
VOL_LOW_PCT = 20.0              # < 20%      => Low
VOL_HIGH_PCT = 40.0            # > 40%      => High   (20–40% => Moderate)


def _compute_signals(close):
    """Derive trend, volatility and a recommendation from real close prices.

    Returns a dict with the labels shown on the cards plus the underlying
    numbers, so nothing on the page is invented — every label is backed by a
    value the user can see. ``close`` is an array-like of closing prices.
    """
    close = np.asarray(close, dtype="float64")
    close = close[np.isfinite(close)]

    last = float(close[-1])

    # --- Momentum over the trailing window (shrinks to fit short history) ---
    window = min(MOMENTUM_WINDOW, len(close) - 1)
    past = float(close[-(window + 1)])
    momentum_pct = ((last / past) - 1.0) * 100.0 if past else 0.0

    # --- Trend vs the longer simple moving average ---
    sma_span = min(50, len(close))
    sma_long = float(np.mean(close[-sma_span:]))
    above_avg = last >= sma_long

    if momentum_pct >= STRONG_MOVE_PCT and above_avg:
        trend, trend_score = "Bullish Uptrend", 2
    elif momentum_pct <= -STRONG_MOVE_PCT and not above_avg:
        trend, trend_score = "Bearish Downtrend", -2
    elif abs(momentum_pct) < STRONG_MOVE_PCT:
        trend, trend_score = "Sideways / Range-bound", 0
    elif momentum_pct > 0:
        trend, trend_score = "Mildly Bullish", 1
    else:
        trend, trend_score = "Mildly Bearish", -1

    # --- Annualized volatility from daily returns ---
    returns = np.diff(close) / close[:-1]
    vol_window = returns[-30:] if len(returns) >= 30 else returns
    ann_vol_pct = float(np.std(vol_window) * np.sqrt(252) * 100.0) if len(vol_window) else 0.0

    if ann_vol_pct < VOL_LOW_PCT:
        volatility = "Low"
    elif ann_vol_pct <= VOL_HIGH_PCT:
        volatility = "Moderate"
    else:
        volatility = "High"

    # --- Recommendation: trend score, tempered by volatility (a heuristic) ---
    rec_map = {2: "BUY", 1: "ACCUMULATE", 0: "HOLD", -1: "REDUCE", -2: "SELL"}
    recommendation = rec_map[trend_score]
    # High volatility makes an outright BUY more cautious.
    if volatility == "High" and recommendation == "BUY":
        recommendation = "ACCUMULATE"

    return {
        "trend": trend,
        "volatility": volatility,
        "recommendation": recommendation,
        "last": last,
        "momentum_pct": momentum_pct,
        "ann_vol_pct": ann_vol_pct,
    }


def show_insights():
    st.markdown(
        """
        <div class="page-head">
          <p class="eyebrow">AI summary</p>
          <h1 class="page-title">Insights</h1>
          <p class="page-copy">Simple, consumer-friendly signals for the selected stock, with the same report export flow.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "ticker" not in st.session_state:
        st.session_state.ticker = "RELIANCE.NS"

    stock = st.session_state.ticker

    raw_df = fetch_data(stock)
    close = raw_df["Close"].dropna() if not raw_df.empty and "Close" in raw_df else None

    if close is None or len(close) < 2:
        st.markdown(
            f"<div class='content-card'><p class='eyebrow'>Selected stock</p><h3>{stock}</h3></div>",
            unsafe_allow_html=True,
        )
        st.warning("Not enough recent price data to compute insights. Try a symbol like RELIANCE.NS, TCS.NS, AAPL, or MSFT.")
        return

    resolved_stock = raw_df.attrs.get("resolved_ticker", stock)
    signals = _compute_signals(close.to_numpy())
    trend = signals["trend"]
    volatility = signals["volatility"]
    recommendation = signals["recommendation"]

    st.markdown(
        f"<div class='content-card'><p class='eyebrow'>Selected stock</p><h3>{resolved_stock}</h3></div>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    col1.markdown(f"<div class='metric-card'>Trend Analysis<b>{trend}</b></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='metric-card'>Volatility<b>{volatility}</b></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='metric-card'>Recommendation<b>{recommendation}</b></div>", unsafe_allow_html=True)

    # Transparency: show the actual numbers behind the labels above.
    st.caption(
        f"Based on {len(close)} sessions · "
        f"{MOMENTUM_WINDOW}-day momentum {signals['momentum_pct']:+.2f}% · "
        f"annualized volatility {signals['ann_vol_pct']:.1f}%. "
        "Educational heuristic, not financial advice."
    )

    with st.container(border=True):
        st.markdown("### Export Report")

        summary = f"""
        Stock: {resolved_stock}

        Trend: {trend}
        Volatility: {volatility} (annualized {signals['ann_vol_pct']:.1f}%)
        {MOMENTUM_WINDOW}-day momentum: {signals['momentum_pct']:+.2f}%
        Recommendation: {recommendation}

        Signals are computed from the last {len(close)} trading sessions of Yahoo Finance
        close prices. This is an educational heuristic, not financial advice.
        """

        if st.button("Generate Report", width="stretch"):
            try:
                file_path = generate_report(resolved_stock, summary)

                with open(file_path, "rb") as f:
                    st.session_state["report_pdf_bytes"] = f.read()
                st.session_state["report_pdf_name"] = f"{resolved_stock}_report.pdf"
                st.success("Report generated successfully!")

            except Exception as e:
                st.error(f"Error generating report: {e}")

        if "report_pdf_bytes" in st.session_state:
            st.download_button(
                label="Download PDF",
                data=st.session_state["report_pdf_bytes"],
                file_name=st.session_state.get("report_pdf_name", f"{resolved_stock}_report.pdf"),
                mime="application/pdf",
                width="stretch",
            )
