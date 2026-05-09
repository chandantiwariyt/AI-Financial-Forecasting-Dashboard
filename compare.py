import plotly.graph_objects as go
import streamlit as st

from data.fetcher import fetch_data


def show_compare(format_inr=None):
    st.markdown(
        """
        <div class="page-head">
          <p class="eyebrow">Side-by-side analysis</p>
          <h1 class="page-title">Compare Stocks</h1>
          <p class="page-copy">Review relative performance between two symbols with a simple Groww-style comparison view.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        col1, vs_col, col2 = st.columns([1, 0.18, 1], vertical_alignment="center")

        with col1:
            stock1 = st.text_input("Stock 1", "RELIANCE.NS")

        with vs_col:
            st.markdown("<div class='vs-pill'>VS</div>", unsafe_allow_html=True)

        with col2:
            stock2 = st.text_input("Stock 2", "TCS.NS")

        compare_clicked = st.button("Compare", use_container_width=True)

    if not compare_clicked:
        return

    try:
        with st.spinner("Fetching data..."):
            df1 = fetch_data(stock1)
            df2 = fetch_data(stock2)

            if df1.empty or df2.empty:
                st.error("Could not fetch data for one or both stocks.")
                return

            df1_close = df1["Close"].dropna()
            df2_close = df2["Close"].dropna()

            if df1_close.empty or df2_close.empty:
                st.error("Could not calculate performance for one or both stocks.")
                return

            df1_norm = df1_close / df1_close.iloc[0] * 100
            df2_norm = df2_close / df2_close.iloc[0] * 100
            perf1 = ((df1_close.iloc[-1] / df1_close.iloc[0]) - 1) * 100 if df1_close.iloc[0] else 0
            perf2 = ((df2_close.iloc[-1] / df2_close.iloc[0]) - 1) * 100 if df2_close.iloc[0] else 0

            with st.container(border=True):
                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(
                        x=df1.loc[df1_close.index, "Date"],
                        y=df1_norm,
                        name=stock1,
                        line=dict(width=2.8, color="#FF8A00"),
                    )
                )
                fig.add_trace(
                    go.Scatter(
                        x=df2.loc[df2_close.index, "Date"],
                        y=df2_norm,
                        name=stock2,
                        line=dict(width=2.8, color="#148A5B"),
                    )
                )
                fig.update_layout(
                    template="plotly_white",
                    paper_bgcolor="#FFFFFF",
                    plot_bgcolor="#FFFFFF",
                    font=dict(color="#182230", family="Inter"),
                    height=450,
                    margin=dict(l=10, r=10, t=30, b=10),
                    title="Relative Performance (Base = 100)",
                    xaxis=dict(showgrid=False, title=None),
                    yaxis=dict(gridcolor="#F0E5D8", title=None),
                    hovermode="x unified",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                )
                st.plotly_chart(fig, use_container_width=True)

            col_a, col_b = st.columns(2)
            col_a.markdown(f"<div class='metric-card'>{stock1}<b>{perf1:.2f}%</b></div>", unsafe_allow_html=True)
            col_b.markdown(f"<div class='metric-card'>{stock2}<b>{perf2:.2f}%</b></div>", unsafe_allow_html=True)

            st.markdown("### AI Comparison Insight")
            if perf1 > perf2:
                st.success(f"{stock1} is outperforming {stock2}.")
            elif perf2 > perf1:
                st.success(f"{stock2} is outperforming {stock1}.")
            else:
                st.info("Both stocks are performing similarly.")

    except Exception as e:
        st.error(f"Error comparing stocks: {e}")
