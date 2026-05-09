from math import isfinite
from pathlib import Path
import time

import streamlit as st
import yfinance as yf


st.set_page_config(
    page_title="NiveshX",
    page_icon="NX",
    layout="wide",
)


if "ticker" not in st.session_state:
    st.session_state.ticker = "RELIANCE.NS"

if "currency_rate" not in st.session_state:
    st.session_state.currency_rate = 83.0

if "feedback_open" not in st.session_state:
    st.session_state.feedback_open = False


LOGO_PATH = Path(__file__).parent / "assets" / "niveshx-logo-cropped.png"


def get_usd_inr_rate():
    try:
        rate = yf.Ticker("USDINR=X").history(period="1d")["Close"].iloc[-1]
        return rate
    except Exception:
        return 83.0


def format_inr(num, ticker_override=None):
    try:
        num = float(num)
    except (TypeError, ValueError):
        return "N/A"

    if not isfinite(num):
        return "N/A"

    # Indian-listed stocks (.NS / .BO) are already priced in INR by Yahoo Finance.
    # Only convert USD → INR for non-Indian tickers.
    ticker = ticker_override or st.session_state.get("ticker", "")
    is_indian = ticker.upper().endswith((".NS", ".BO"))
    if not is_indian:
        num *= st.session_state.currency_rate

    s = f"{num:.2f}"
    before, after = s.split(".")

    if len(before) > 3:
        last3 = before[-3:]
        rest = before[:-3]
        rest = ",".join([rest[max(i - 2, 0):i] for i in range(len(rest), 0, -2)][::-1])
        before = rest + "," + last3

    return f"₹{before}.{after}"


def inject_theme():
    st.markdown(
        """
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

          :root {
            --saffron: #FF8A00;
            --saffron-dark: #D86F00;
            --saffron-soft: #FFF2E0;
            --green: #148A5B;
            --green-soft: #EAF8F1;
            --ink: #182230;
            --muted: #667085;
            --line: #E7E0D7;
            --soft: #FFF9F2;
            --card: #FFFFFF;
          }

          html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
          }

          .stApp {
            background:
              linear-gradient(180deg, #FFFFFF 0, var(--soft) 260px, #FFFFFF 100%);
            color: var(--ink);
          }

          header[data-testid="stHeader"] {
            display: none;
          }

          .main .block-container {
            max-width: 1280px;
            padding-top: 1rem;
            padding-bottom: 3rem;
          }

          section[data-testid="stSidebar"] {
            display: none;
          }

          .top-nav-shell {
            background: #FFFFFF;
            border: 1px solid #F0E5D8;
            border-radius: 18px;
            box-shadow: 0 12px 30px rgba(216, 111, 0, 0.08);
            padding: 0.65rem 0.85rem;
            margin-bottom: 1.35rem;
          }

          .nav-status {
            color: var(--green);
            font-size: 0.78rem;
            font-weight: 800;
            margin-top: 0.15rem;
          }

          div[data-testid="stImage"] img {
            max-height: 64px;
            width: auto;
            object-fit: contain;
          }

          .nav-market-status {
            color: var(--muted);
            font-size: 0.78rem;
            font-weight: 700;
            line-height: 1.25;
          }

          .nav-market-status strong {
            display: block;
            color: var(--ink);
            font-size: 1rem;
            margin: 0.15rem 0;
          }

          div[role="radiogroup"] {
            gap: 0.15rem;
          }

          div[role="radiogroup"] label {
            border-radius: 12px;
            padding: 0.45rem 0.75rem;
            border: 1px solid transparent;
            color: var(--ink) !important;
            font-weight: 700;
            opacity: 1 !important;
          }

          div[role="radiogroup"] label p,
          div[role="radiogroup"] label span {
            color: var(--ink) !important;
            opacity: 1 !important;
          }

          div[role="radiogroup"] label > div:first-child {
            display: none;
          }

          div[role="radiogroup"] label:has(input:checked) {
            background: var(--saffron-soft);
            border-color: #FFD3A1;
            color: var(--saffron-dark) !important;
            font-weight: 700;
          }

          div[role="radiogroup"] label:has(input:checked) p,
          div[role="radiogroup"] label:has(input:checked) span {
            color: var(--saffron-dark) !important;
          }

          div[role="radiogroup"] label:hover {
            background: #FFF7ED;
            border-color: #FFDDB8;
          }

          .login-feedback-note {
            color: var(--muted);
            font-size: 0.85rem;
            margin-bottom: 0.75rem;
          }

          .top-card,
          .metric-card,
          .content-card,
          .compare-card,
          .insight-card,
          div[data-testid="stVerticalBlockBorderWrapper"] {
            background: var(--card);
            border: 1px solid #F0E5D8;
            border-radius: 16px;
            box-shadow: 0 12px 30px rgba(216, 111, 0, 0.08);
          }

          div[data-testid="stVerticalBlockBorderWrapper"] {
            overflow: hidden;
          }

          .top-card {
            min-height: 78px;
            padding: 1rem 1.1rem;
            display: flex;
            flex-direction: column;
            justify-content: center;
          }

          .top-label,
          .eyebrow {
            color: #8A5A24;
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 0.01em;
            margin: 0;
          }

          .top-value {
            color: var(--ink);
            font-size: 1.22rem;
            font-weight: 800;
            margin: 0.2rem 0 0;
          }

          .live-row {
            display: flex;
            gap: 0.45rem;
            align-items: center;
            color: var(--green);
            font-weight: 700;
            margin-top: 0.35rem;
          }

          .live-dot {
            width: 9px;
            height: 9px;
            border-radius: 50%;
            background: var(--green);
            box-shadow: 0 0 0 6px rgba(20, 138, 91, 0.14);
          }

          .page-head {
            margin: 1.4rem 0 1.6rem;
          }

          .page-title {
            color: var(--ink);
            font-size: 2rem;
            font-weight: 800;
            line-height: 1.15;
            margin: 0.2rem 0 0.35rem;
            letter-spacing: 0;
          }

          .page-copy {
            color: var(--muted);
            font-size: 0.95rem;
            margin: 0;
          }

          .metric-card {
            padding: 1rem 1.05rem;
            min-height: 96px;
            color: var(--muted);
            font-size: 0.82rem;
            font-weight: 600;
          }

          .metric-card b {
            display: block;
            color: var(--ink);
            font-size: 1.35rem;
            line-height: 1.15;
            margin-top: 0.42rem;
          }

          .content-card,
          .compare-card,
          .insight-card {
            padding: 1.2rem;
            margin-bottom: 1.05rem;
          }

          .vs-pill {
            width: 46px;
            height: 46px;
            border-radius: 50%;
            background: var(--green-soft);
            color: var(--green);
            font-weight: 800;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 2.05rem auto 0;
            border: 1px solid #BCEAD5;
          }

          div[data-testid="stTextInput"] div[data-baseweb="input"],
          div[data-testid="stTextInput"] div[data-baseweb="base-input"],
          .stTextInput div[data-baseweb="input"],
          .stTextInput div[data-baseweb="base-input"],
          div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            border: 1px solid var(--line) !important;
            border-radius: 14px !important;
            background: #FFFFFF !important;
            background-color: #FFFFFF !important;
            box-shadow: none !important;
            outline: none !important;
          }

          div[data-testid="stTextInput"] div[data-baseweb="input"] *,
          div[data-testid="stTextInput"] div[data-baseweb="base-input"] *,
          .stTextInput div[data-baseweb="input"] *,
          .stTextInput div[data-baseweb="base-input"] *,
          div[data-testid="stTextInput"] input {
            border: 0 !important;
            box-shadow: none !important;
            outline: none !important;
            background: transparent !important;
            background-color: transparent !important;
          }

          div[data-testid="stTextInput"] input,
          .stTextInput input {
            min-height: 46px;
            color: var(--ink) !important;
            background: #FFFFFF !important;
            background-color: #FFFFFF !important;
            caret-color: var(--saffron);
            font-weight: 600;
            -webkit-text-fill-color: var(--ink) !important;
          }

          div[data-testid="stTextInput"] input:hover,
          div[data-testid="stTextInput"] input:focus,
          div[data-testid="stTextInput"] input:active,
          .stTextInput input:hover,
          .stTextInput input:focus,
          .stTextInput input:active {
            background: #FFFFFF !important;
            background-color: #FFFFFF !important;
            color: var(--ink) !important;
            -webkit-text-fill-color: var(--ink) !important;
          }

          div[data-testid="stTextInput"] input::placeholder {
            color: #8A94A6 !important;
            opacity: 1 !important;
            font-weight: 500;
          }

          div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within,
          div[data-testid="stTextInput"] div[data-baseweb="base-input"]:focus-within,
          .stTextInput div[data-baseweb="input"]:focus-within,
          .stTextInput div[data-baseweb="base-input"]:focus-within {
            border-color: var(--saffron) !important;
            box-shadow: 0 0 0 3px rgba(255, 138, 0, 0.14) !important;
          }

          div[data-testid="stTextInput"] [aria-invalid="true"] {
            border-color: var(--line) !important;
            box-shadow: none !important;
          }

          .stButton > button {
            border-radius: 12px;
            border: 1px solid var(--saffron);
            background: var(--saffron);
            color: #FFFFFF;
            font-weight: 750;
            min-height: 44px;
            box-shadow: 0 8px 18px rgba(255, 138, 0, 0.24);
          }

          .stButton > button:hover {
            border-color: var(--saffron-dark);
            background: var(--saffron-dark);
            color: #FFFFFF;
          }

          div[data-testid="stAlert"] {
            border-radius: 14px;
            border: 1px solid #F3D6AE;
          }

          div[data-testid="stAlert"] p {
            color: var(--ink);
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


st.session_state.currency_rate = get_usd_inr_rate()
inject_theme()


nav_items = {
    "Dashboard": "Dashboard",
    "Forecast": "Forecast",
    "Insights": "Insights",
    "Compare": "Compare",
}

with st.container(border=True):
    logo_col, nav_col, search_col, status_col, login_col = st.columns(
        [1.18, 2.2, 2.7, 1.0, 1.0],
        vertical_alignment="center",
    )

    with logo_col:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=150)
        else:
            st.markdown("### NiveshX")

    with nav_col:
        selected_nav = st.radio(
            "Navigation",
            list(nav_items.keys()),
            horizontal=True,
            label_visibility="collapsed",
        )
        page = nav_items[selected_nav]

    with search_col:
        ticker = st.text_input(
            "Search stocks",
            value=st.session_state.ticker,
            placeholder="Search stocks, ETFs, or symbols like RELIANCE.NS",
            label_visibility="collapsed",
        )
        st.session_state.ticker = ticker.strip().upper() or "RELIANCE.NS"

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

    with login_col:
        if st.button("Login", use_container_width=True):
            st.session_state.feedback_open = not st.session_state.feedback_open
        auto_refresh = st.toggle("Auto", value=False)

if auto_refresh:
    time.sleep(10)
    st.rerun()

if st.session_state.feedback_open:
    with st.container(border=True):
        st.markdown("### Login / Feedback")
        st.markdown(
            "<p class='login-feedback-note'>Share quick feedback for NiveshX. This prototype keeps the form local to the session.</p>",
            unsafe_allow_html=True,
        )
        name_col, email_col = st.columns(2)
        with name_col:
            st.text_input("Name", key="feedback_name")
        with email_col:
            st.text_input("Email or phone", key="feedback_contact")
        st.text_area("Feedback", key="feedback_message", placeholder="Tell us what should be improved next.")
        if st.button("Submit Feedback", use_container_width=True):
            st.success("Thanks. Your feedback has been captured for this session.")


if page == "Dashboard":
    from dashboard import show_dashboard

    show_dashboard(format_inr)
elif page == "Forecast":
    from forecast import show_forecast

    show_forecast(format_inr)
elif page == "Insights":
    from insights import show_insights

    show_insights()
elif page == "Compare":
    from compare import show_compare

    show_compare(format_inr)
