"""Offline smoke tests for NiveshX finance logic (no network calls).

These cover the two pieces of domain logic added in this change set:
  * Prophet holiday-calendar selection by ticker suffix.
  * The data-driven Insights signals (trend / volatility / recommendation).
Plus PDF report generation. Prophet model fitting is intentionally not
exercised here to keep the suite fast and network-free.
"""
import os

import numpy as np

from insights import _compute_signals
from models.prophet_model import _holiday_country_for_ticker
from utils.report import generate_report


def test_holiday_country_mapping():
    assert _holiday_country_for_ticker("RELIANCE.NS") == "IN"
    assert _holiday_country_for_ticker("tata.bo") == "IN"
    assert _holiday_country_for_ticker("AAPL") == "US"
    assert _holiday_country_for_ticker(None) == "US"
    # Indices, FX pairs and other exchanges get no country calendar.
    assert _holiday_country_for_ticker("^NSEI") is None
    assert _holiday_country_for_ticker("USDINR=X") is None
    assert _holiday_country_for_ticker("VOD.L") is None


def test_signals_uptrend_is_bullish():
    s = _compute_signals(100 + np.linspace(0, 20, 60))
    assert s["trend"] == "Bullish Uptrend"
    assert s["recommendation"] in {"BUY", "ACCUMULATE"}
    assert s["momentum_pct"] > 0


def test_signals_downtrend_is_bearish():
    s = _compute_signals(120 - np.linspace(0, 20, 60))
    assert s["trend"] == "Bearish Downtrend"
    assert s["recommendation"] == "SELL"
    assert s["momentum_pct"] < 0


def test_signals_flat_is_sideways():
    s = _compute_signals(np.full(60, 100.0))
    assert s["trend"] == "Sideways / Range-bound"
    assert s["recommendation"] == "HOLD"
    assert s["volatility"] == "Low"


def test_high_volatility_tempers_buy():
    # A strong but very noisy up-move reads as High volatility, which softens
    # an outright BUY down to ACCUMULATE.
    rng = np.random.default_rng(0)
    arr = 100 + np.linspace(0, 30, 80) + rng.normal(0, 8, 80)
    s = _compute_signals(arr)
    assert s["ann_vol_pct"] > 40.0
    assert s["volatility"] == "High"
    assert s["recommendation"] != "BUY"


def test_generate_report_creates_pdf():
    path = generate_report(
        "RELIANCE.NS",
        "Stock: RELIANCE.NS\nTrend: Bullish Uptrend\nRecommendation: BUY",
    )
    assert os.path.exists(path)
    assert os.path.getsize(path) > 0
    with open(path, "rb") as fh:
        assert fh.read(4) == b"%PDF"
