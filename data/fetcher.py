import re
import time
import logging
import os
from typing import Optional, Tuple, Callable, Any, Dict

import pandas as pd
import yfinance as yf
import streamlit as st
import requests
from dotenv import load_dotenv
from fredapi import Fred

load_dotenv()

logger = logging.getLogger(__name__)

# -------------------------
# Helpers
# -------------------------
TICKER_RE = re.compile(r"^[A-Za-z0-9\.\-]{1,10}$")  # allow letters, numbers, dot, dash (simple validation)


def _is_valid_ticker(ticker: str) -> bool:
    if not ticker or not isinstance(ticker, str):
        return False
    return bool(TICKER_RE.fullmatch(ticker.strip()))


# Public alias (UI can import this)
def is_valid_ticker(ticker: str) -> bool:
    return _is_valid_ticker(ticker)


def _with_retries(
    fn: Callable[..., Any],
    *args,
    attempts: int = 3,
    backoff: float = 1.0,
    catch_exceptions: Tuple[type, ...] = (Exception,),
    **kwargs,
) -> Tuple[Optional[Any], Optional[str]]:
    """
    Run fn(*args, **kwargs) with retry/backoff. Returns (result, error_str).
    If rate limit or unrecoverable error is detected we return an error string.
    """
    last_err = None
    for attempt in range(1, attempts + 1):
        try:
            return fn(*args, **kwargs), None
        except catch_exceptions as e:
            last_err = e
            err_str = str(e) or e.__class__.__name__
            # simple 429 detection: if the exception contains '429' or an HTTPError with status_code
            status_code = None
            if isinstance(e, requests.HTTPError) and getattr(e, "response", None) is not None:
                status_code = getattr(e.response, "status_code", None)

            if "429" in err_str or status_code == 429:
                logger.warning("Rate limit detected while calling external API: %s", err_str)
                return None, "rate_limited"
            # don't retry for permanent client errors (400-499 except 429)
            if status_code and 400 <= status_code < 500 and status_code != 429:
                logger.warning("Client error detected (status %s): %s", status_code, err_str)
                return None, f"client_error:{status_code}"

            # transient - sleep and retry
            sleep_for = backoff * (2 ** (attempt - 1))
            logger.debug("Attempt %s failed: %s. Retrying in %.1f seconds...", attempt, err_str, sleep_for)
            time.sleep(sleep_for)

    logger.exception("Operation failed after %s attempts: %s", attempts, last_err)
    return None, str(last_err)


def _wrap_result(value: Any, error: Optional[str], return_error: bool):
    if return_error:
        return value, error
    return value


# =========================
# 📊 STOCK DATA (MAIN FUNCTION)
# =========================
@st.cache_data(ttl=300, show_spinner=False)
def fetch_data(ticker: str, period: str = "2y", return_error: bool = False) -> Any:
    """
    Returns a DataFrame (Date, Open, High, Low, Close, Volume) for the ticker.
    If return_error=True returns (df_or_none, error_string_or_None).
    Error strings: 'invalid_ticker', 'rate_limited', 'client_error:4xx', or raw exception text for unexpected failures.
    """
    if not _is_valid_ticker(ticker):
        logger.info("Invalid ticker provided to fetch_data: %s", ticker)
        return _wrap_result(pd.DataFrame(), "invalid_ticker", return_error)

    def _fetch_history(t: str, p: str):
        stock = yf.Ticker(t)
        # yfinance may raise or return empty DataFrame
        return stock.history(period=p)

    df, err = _with_retries(_fetch_history, ticker, period, attempts=3, backoff=1.0, catch_exceptions=(Exception,))
    if err:
        logger.warning("Failed to fetch data for %s: %s", ticker, err)
        return _wrap_result(pd.DataFrame(), err, return_error)

    if df is None or df.empty:
        logger.info("No data returned from Yahoo for %s", ticker)
        return _wrap_result(pd.DataFrame(), None, return_error)

    df = df.copy()
    df.reset_index(inplace=True)
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Ensure we only return the expected columns if present
    cols = [c for c in ["Date", "Open", "High", "Low", "Close", "Volume"] if c in df.columns]
    result_df = df[cols]
    return _wrap_result(result_df, None, return_error)


# =========================
# ⚡ LIVE PRICE
# =========================
@st.cache_data(ttl=60, show_spinner=False)
def get_live_price(ticker: str, return_error: bool = False) -> Any:
    """
    Returns a float price or None. If return_error=True returns (price_or_None, error_string).
    The function prefers fast_info, falls back to recent history close price.
    """
    if not _is_valid_ticker(ticker):
        logger.info("Invalid ticker provided to get_live_price: %s", ticker)
        return _wrap_result(None, "invalid_ticker", return_error)

    def _fetch_price(t: str):
        stock = yf.Ticker(t)

        # fast_info may be missing or incomplete
        fast_info = {}
        try:
            fast_info = getattr(stock, "fast_info", {}) or {}
        except Exception:
            logger.debug("fast_info access failed for %s", t)

        price = None
        if isinstance(fast_info, dict):
            price = fast_info.get("lastPrice") or fast_info.get("last_trade_price")
        # fallback to history (safer than calling stock.info which is sometimes slow)
        if price is None:
            hist = stock.history(period="1d", interval="1m")
            if hist is not None and not hist.empty and "Close" in hist.columns:
                price = float(hist["Close"].iloc[-1])
        # final fallback: try stock.info but do so carefully
        if price is None:
            try:
                info = getattr(stock, "info", {}) or {}
                price = info.get("currentPrice") or info.get("regularMarketPrice")
            except Exception:
                logger.debug("stock.info access failed for %s", t)
        return price

    price, err = _with_retries(_fetch_price, ticker, attempts=2, backoff=0.5, catch_exceptions=(Exception,))
    if err:
        logger.warning("Failed to get live price for %s: %s", ticker, err)
        return _wrap_result(None, err, return_error)

    return _wrap_result(price, None, return_error)


# =========================
# 🧾 COMPANY FINANCIALS
# =========================
@st.cache_data(ttl=600, show_spinner=False)
def get_company_financials(ticker: str, return_error: bool = False) -> Any:
    """
    Returns a dict with keys income_statement, balance_sheet, cash_flow, info.
    If return_error=True returns (dict_or_empty, error_string_or_None).
    Each field is fetched independently to avoid a single failing attribute from breaking the whole call.
    """
    if not _is_valid_ticker(ticker):
        logger.info("Invalid ticker for get_company_financials: %s", ticker)
        return _wrap_result({"income_statement": None, "balance_sheet": None, "cash_flow": None, "info": {}}, "invalid_ticker", return_error)

    stock = yf.Ticker(ticker)
    results: Dict[str, Optional[Any]] = {"income_statement": None, "balance_sheet": None, "cash_flow": None, "info": {}}

    # Wrap each attribute to avoid one failing call breaking the rest
    def _safe_attr(getter: Callable[[], Any], name: str):
        try:
            return getter()
        except Exception as e:
            logger.warning("Failed to fetch %s for %s: %s", name, ticker, e)
            return None

    results["income_statement"] = _safe_attr(lambda: stock.financials, "income_statement")
    results["balance_sheet"] = _safe_attr(lambda: stock.balance_sheet, "balance_sheet")
    results["cash_flow"] = _safe_attr(lambda: stock.cashflow, "cash_flow")

    # info is potentially slow/unreliable; fetch as a last resort and protect by retries
    def _fetch_info():
        try:
            return getattr(stock, "info", {}) or {}
        except Exception as e:
            raise

    info, err = _with_retries(_fetch_info, attempts=2, backoff=0.5, catch_exceptions=(Exception,))
    if err:
        logger.warning("Failed to fetch 'info' for %s: %s", ticker, err)
        results["info"] = {}
        # don't treat info failure as fatal; return the other data with an error tag if requested
        final_err = err
    else:
        results["info"] = info
        final_err = None

    return _wrap_result(results, final_err, return_error)


# =========================
# 🌍 MACRO DATA
# =========================
@st.cache_data(ttl=3600, show_spinner=False)
def get_macro_indicators(return_error: bool = False) -> Any:
    fred_key = os.getenv("FRED_API_KEY")

    if not fred_key:
        logger.error("FRED_API_KEY not set")
        return _wrap_result(pd.DataFrame(), "fred_key_missing", return_error)

    fred = Fred(api_key=fred_key)

    indicators = {
        "GDP": "GDP",
        "Inflation": "CPIAUCSL",
        "Fed_Rate": "FEDFUNDS",
        "Unemployment": "UNRATE",
        "VIX": "VIXCLS",
    }

    macro_df = pd.DataFrame()
    for name, series_id in indicators.items():
        try:
            series = fred.get_series(series_id, observation_start="2020-01-01")
            macro_df[name] = series
        except Exception as e:
            logger.warning("Failed to fetch %s from FRED: %s", name, e)
            macro_df[name] = None

    macro_df.reset_index(inplace=True)
    macro_df.rename(columns={"index": "Date"}, inplace=True)
    return _wrap_result(macro_df, None, return_error)


# =========================
# 🚀 SNAPSHOT
# =========================
@st.cache_data(ttl=60, show_spinner=False)
def get_company_snapshot(ticker: str, return_error: bool = False) -> Any:
    """
    Returns a small dict: {price, market_cap, volume}. Safe access to fast_info with fallbacks.
    If return_error=True returns (snapshot_dict, error_string)
    """
    if not _is_valid_ticker(ticker):
        logger.info("Invalid ticker for get_company_snapshot: %s", ticker)
        return _wrap_result({}, "invalid_ticker", return_error)

    def _fetch_snapshot(t: str):
        stock = yf.Ticker(t)
        snapshot = {"price": None, "market_cap": None, "volume": None}
        try:
            fast = getattr(stock, "fast_info", {}) or {}
            if isinstance(fast, dict):
                snapshot["price"] = fast.get("lastPrice")
                snapshot["market_cap"] = fast.get("marketCap")
                snapshot["volume"] = fast.get("lastVolume")
        except Exception:
            logger.debug("fast_info access failed for snapshot on %s", t)

        # fallback to history price if needed
        if snapshot["price"] is None:
            hist = stock.history(period="1d", interval="1m")
            if hist is not None and not hist.empty and "Close" in hist.columns:
                snapshot["price"] = float(hist["Close"].iloc[-1])

        # market cap fallback: try info but protected
        if snapshot["market_cap"] is None:
            try:
                info = getattr(stock, "info", {}) or {}
                snapshot["market_cap"] = info.get("marketCap")
            except Exception:
                logger.debug("stock.info access failed for marketCap on %s", t)

        return snapshot

    snapshot, err = _with_retries(_fetch_snapshot, ticker, attempts=2, backoff=0.5, catch_exceptions=(Exception,))
    if err:
        logger.warning("Failed to get snapshot for %s: %s", ticker, err)
        return _wrap_result({}, err, return_error)

    return _wrap_result(snapshot or {}, None, return_error)
