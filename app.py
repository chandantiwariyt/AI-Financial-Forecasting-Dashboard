from math import isfinite
import os
from pathlib import Path
import tempfile
import time
from typing import Optional

import streamlit as st
import yfinance as yf

# ---- Page config -----------------------------------------------------------
st.set_page_config(page_title="NiveshX", page_icon="NX", layout="wide")

# ---- Constants -------------------------------------------------------------
LOGO_PATH = Path(__file__).parent / "assets" / "niveshx-logo-cropped.png"
THEME_CSS_PATH = Path(__file__).parent / "assets" / "theme.css"

# Refresh interval (seconds) for auto refresh behavior
REFRESH_INTERVAL = 10
# Default fallback USD→INR
USDINR_FALLBACK = 83.0

# ---- Session defaults ------------------------------------------------------
if "ticker" not in st.session_state:
    st.session_state.ticker = "RELIANCE.NS"

if "currency_rate" not in st.session_state:
    st.session_state.currency_rate = USDINR_FALLBACK

if "currency_rate_fetched_at" not in st.session_state:
    st.session_state.currency_rate_fetched_at = 0.0

if "feedback_open" not in st.session_state:
    st.session_state.feedback_open = False

if "auto_refresh_last" not in st.session_state:
    st.session_state.auto_refresh_last = 0.0

# yfinance keeps a small timezone cache; point it at a writable temp dir so a
# read-only/locked default location can't crash data fetches on some hosts.
try:
    yf_cache_dir = Path(os.getenv("YFINANCE_CACHE_DIR", Path(tempfile.gettempdir()) / "niveshx_yfinance"))
    yf_cache_dir.mkdir(parents=True, exist_ok=True)
    yf.set_tz_cache_location(str(yf_cache_dir))
except Exception:
    pass


# ---- Cached external fetches -----------------------------------------------
# @st.cache_data avoids re-hitting the network on every Streamlit rerun.
@st.cache_data(ttl=300)
def fetch_usd_inr_rate() -> Optional[float]:
    """Return the latest USD->INR rate via yfinance, or None on failure.

    Tries the cheap fast_info quote first, then a short daily-history
    fallback. Returning None lets the caller keep the last known rate.
    """
    try:
        ticker = yf.Ticker("USDINR=X")
        fast_rate = ticker.fast_info.get("lastPrice")
        if fast_rate is not None:
            fast_rate = float(fast_rate)
            if isfinite(fast_rate) and fast_rate > 0:
                return fast_rate

        close = ticker.history(period="5d")["Close"].dropna()
        if not close.empty:
            rate = float(close.iloc[-1])
            if isfinite(rate) and rate > 0:
                return rate
    except Exception:
        return None

    return None


def validate_ticker(candidate: str) -> bool:
    """Lightweight validation: attempt a minimal history fetch to see if ticker exists."""
    candidate = (candidate or "").strip().upper()
    if not candidate:
        return False
    try:
        # Small history window to keep the request light; if it returns rows we accept it.
        hist = yf.Ticker(candidate).history(period="1d")
        return not hist.empty
    except Exception:
        return False


# ---- Formatting helper ----------------------------------------------------
def format_inr(num, ticker_override=None):
    try:
        num = float(num)
    except (TypeError, ValueError):
        return "N/A"

    if not isfinite(num):
        return "N/A"

    # Indian-listed stocks (.NS / .BO) are already priced in INR by Yahoo Finance.
    ticker = ticker_override or st.session_state.get("ticker", "")
    is_indian = ticker.upper().endswith((".NS", ".BO"))

    if not is_indian:
        return f"${num:,.2f}"

    s = f"{num:.2f}"
    before, after = s.split(".")
    if len(before) > 3:
        last3 = before[-3:]
        rest = before[:-3]
        rest = ",".join([rest[max(i - 2, 0):i] for i in range(len(rest), 0, -2)][::-1])
        before = rest + "," + last3

    return f"₹{before}.{after}"


# ---- Theme injection (external file preferred) -----------------------------
def inject_theme():
    """Load the theme from assets/theme.css if present, else use an inline fallback.

    SECURITY: only static, hardcoded CSS is injected here — never user input.
    """
    if THEME_CSS_PATH.exists():
        css = THEME_CSS_PATH.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
        return

    # Minimal fallback so the layout stays usable if theme.css is missing.
    st.markdown(
        """
        <style>
        :root { --saffron: #FF8A00; --saffron-dark: #D86F00; --soft: #FFF9F2; --ink: #182230; }
        html, body, [class*="css"] { font-family: Inter, sans-serif; }
        .stApp { background: linear-gradient(180deg, #FFFFFF 0, var(--soft) 260px, #FFFFFF 100%); color: var(--ink); }
        header[data-testid="stHeader"] { display: none; }
        section[data-testid="stSidebar"] { display: none; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---- Fetch currency rate (cached) -----------------------------------------
rate = fetch_usd_inr_rate()
if rate is None:
    # Keep previous session value or fallback; don't spam user, give a single warning.
    if time.time() - st.session_state.currency_rate_fetched_at > 300:
        st.warning("Couldn't refresh USD→INR rate right now — using cached/default value.")
    rate = st.session_state.currency_rate or USDINR_FALLBACK
else:
    st.session_state.currency_rate = rate
    st.session_state.currency_rate_fetched_at = time.time()

# Apply theme
inject_theme()

# ---- Navigation items -----------------------------------------------------
nav_items = {"Dashboard": "Dashboard", "Forecast": "Forecast", "Insights": "Insights", "Compare": "Compare"}

# ---- Top bar: logo / nav / search / status / feedback ----------------------
with st.container(border=True):
    logo_col, nav_col, search_col, status_col, feedback_col = st.columns(
        [1.18, 2.2, 2.7, 1.0, 1.0], vertical_alignment="center"
    )

    with logo_col:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=150)
        else:
            st.markdown("### NiveshX")

    with nav_col:
        selected_nav = st.radio(
            "Navigation", list(nav_items.keys()), horizontal=True, label_visibility="collapsed"
        )
        page = nav_items[selected_nav]

    # Search: popular quick-select + custom text input with validation
    with search_col:
        st.markdown("Search stocks")
        popular = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "NIFTYBEES.NS"]
        quick = st.selectbox("Popular", options=["(choose)"] + popular, index=0, label_visibility="collapsed")
        custom_ticker = st.text_input(
            "Custom ticker",
            value="",
            placeholder="Type a symbol like RELIANCE.NS and press Enter",
            label_visibility="collapsed",
        ).strip()

        # Determine candidate ticker (prefer quick selection if chosen)
        candidate_ticker = quick if quick != "(choose)" else custom_ticker
        if candidate_ticker:
            candidate_ticker = candidate_ticker.upper()

            # Only validate when the user has provided input
            if validate_ticker(candidate_ticker):
                # Update global ticker only when it's actually changed and valid
                if st.session_state.ticker != candidate_ticker:
                    st.session_state.ticker = candidate_ticker
                    # NOTE: If other modules (forecast) read ticker from session_state directly,
                    # they will be in sync. Prefer passing ticker explicitly to modules where possible.
            else:
                st.error(f"Couldn't find data for '{candidate_ticker}'. Please check the symbol and try again.")

    with status_col:
        st.markdown(
            f"""
            <div class="nav-market-status">
              <span>USD-INR</span>
              <strong>{st.session_state.currency_rate:.2f}</strong>
              <div class="live-row"><span class="live-dot"></span><span>Live</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Feedback button (renamed from Login to match actual behavior)
    with feedback_col:
        if st.button("Feedback", width="stretch"):
            st.session_state.feedback_open = not st.session_state.feedback_open

        auto_refresh = st.checkbox("Auto refresh", value=False)

# ---- Auto refresh handling (guarded to avoid tight rerun loop) -------------
if auto_refresh:
    now = time.time()
    last = st.session_state.get("auto_refresh_last", 0.0)
    if now - last >= REFRESH_INTERVAL:
        st.session_state.auto_refresh_last = now
        # Trigger a controlled rerun only at the refresh interval boundary.
        st.rerun()

# ---- Feedback panel -------------------------------------------------------
if st.session_state.feedback_open:
    with st.container(border=True):
        st.markdown("### Feedback")
        st.markdown(
            "<p class='login-feedback-note'>Share quick feedback for NiveshX. This prototype keeps the form local to the session.</p>",
            unsafe_allow_html=True,
        )
        name_col, contact_col = st.columns(2)
        with name_col:
            st.text_input("Name", key="feedback_name")
        with contact_col:
            st.text_input("Email or phone", key="feedback_contact")
        st.text_area("Feedback", key="feedback_message", placeholder="Tell us what should be improved next.")
        if st.button("Submit Feedback", width="stretch"):
            st.success("Thanks. Your feedback has been captured for this session.")
            # Keep the feedback purely session-scoped for now (no external storage).


# ---- Page routing ----------------------------------------------------------
# Page modules live in the project root (single source of truth). Streamlit only
# auto-detects a multi-page app from a `pages/` directory, so these root-level
# modules are never treated as standalone pages.
if page == "Dashboard":
    from dashboard import show_dashboard
    show_dashboard(format_inr)

elif page == "Forecast":
    # Pass the ticker explicitly so Forecast always gets the intended symbol.
    from forecast import show_forecast
    show_forecast(format_inr, ticker=st.session_state.ticker)

elif page == "Insights":
    from insights import show_insights
    show_insights()

elif page == "Compare":
    from compare import show_compare
    show_compare(format_inr)
