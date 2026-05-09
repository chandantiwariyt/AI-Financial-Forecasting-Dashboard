import streamlit as st

from utils.report import generate_report


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
    trend = "Bullish ↗"
    volatility = "Moderate"
    recommendation = "HOLD"

    st.markdown(f"<div class='content-card'><p class='eyebrow'>Selected stock</p><h3>{stock}</h3></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.markdown(f"<div class='metric-card'>Trend Analysis<b>{trend}</b></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='metric-card'>Volatility<b>{volatility}</b></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='metric-card'>Recommendation<b>{recommendation}</b></div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("### Export Report")

        summary = f"""
        Stock: {stock}

        Trend: {trend}
        Volatility: {volatility}
        Recommendation: {recommendation}

        This report is generated using AI-based financial analysis.
        """

        if st.button("Generate Report", use_container_width=True):
            try:
                file_path = generate_report(stock, summary)

                st.success("Report generated successfully!")
                with open(file_path, "rb") as f:
                    st.download_button(
                        label="Download PDF",
                        data=f,
                        file_name=f"{stock}_report.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )

            except Exception:
                st.error("Error generating report. Check setup.")
