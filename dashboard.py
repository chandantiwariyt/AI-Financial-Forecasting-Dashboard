import plotly.express as px
import streamlit as st

from data.fetcher import fetch_data


def show_dashboard(format_inr):
    stock = st.session_state.ticker

    st.markdown(
        f"""
        <div class="page-head">
          <p class="eyebrow">Live market snapshot</p>
          <h1 class="page-title">{stock} overview</h1>
          <p class="page-copy">Track live price action, volume, trend, and a quick market read in one clean workspace.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df = fetch_data(stock).dropna(subset=["Close"])

    if len(df) < 2:
        st.error("Not enough recent price data found for this ticker.")
        return

    latest = df["Close"].iloc[-1]
    prev = df["Close"].iloc[-2]
    volume = df["Volume"].dropna().iloc[-1] if "Volume" in df and not df["Volume"].dropna().empty else 0

    change = latest - prev
    pct = (change / prev) * 100 if prev else 0
    trend_label = "Uptrend" if pct > 0 else "Downtrend"
    trend_icon = "↗" if pct > 0 else "↘"

    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(f"<div class='metric-card'>Price<b>{format_inr(latest)}</b></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='metric-card'>Change<b>{pct:.2f}%</b></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='metric-card'>Volume<b>{volume:,.0f}</b></div>", unsafe_allow_html=True)
    col4.markdown(f"<div class='metric-card'>Trend<b>{trend_icon} {trend_label}</b></div>", unsafe_allow_html=True)

    with st.container(border=True):
        fig = px.line(df, x="Date", y="Close")
        fig.update_traces(line_color="#FF8A00", line_width=2.8)
        fig.update_layout(
            template="plotly_white",
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font=dict(color="#182230", family="Inter"),
            margin=dict(l=10, r=10, t=20, b=10),
            xaxis=dict(showgrid=False, title=None),
            yaxis=dict(gridcolor="#F0E5D8", title="Close"),
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Market Insight")
    if pct > 1:
        st.success("Strong upward momentum detected.")
    elif pct > 0:
        st.info("Moderate growth observed.")
    else:
        st.warning("Downward pressure on stock.")
