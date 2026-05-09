import plotly.graph_objects as go
import streamlit as st

from data.fetcher import fetch_data
from data.preprocessor import preprocess_data
from models.prophet_model import run_prophet_model


def show_forecast(format_inr=None):
    st.markdown(
        """
        <div class="page-head">
          <p class="eyebrow">AI forecast engine</p>
          <h1 class="page-title">Forecast future price movement</h1>
          <p class="page-copy">Run Prophet forecasts with confidence bands while keeping the experience clean and investor-friendly.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([0.9, 2.1])

    with col1:
        with st.container(border=True):
            st.markdown("### Configuration")
            stock = st.text_input("Stock Symbol", st.session_state.get("ticker", "RELIANCE.NS"))
            st.caption("Use .NS for Indian stocks")

            period_map = {"30 Days": 30, "90 Days": 90, "1 Year": 365}
            period = st.selectbox("Forecast Period", list(period_map.keys()))
            forecast_days = period_map[period]

            run = st.button("Run Prediction", use_container_width=True)

    with col2:
        with st.container(border=True):
            st.markdown("### Forecast Output")

            if run:
                try:
                    with st.spinner("Running AI model..."):
                        raw_df = fetch_data(stock)

                        if raw_df.empty:
                            st.error("No data found. Check stock symbol.")
                            return

                        df = preprocess_data(raw_df)

                        if len(df) < 2:
                            st.error("Not enough valid price data found for forecasting.")
                            return

                        forecast_df = run_prophet_model(df, forecast_days=forecast_days)

                        fig = go.Figure()
                        fig.add_trace(
                            go.Scatter(
                                x=df["ds"],
                                y=df["y"],
                                name="Historical",
                                line=dict(color="#FF8A00", width=2.6),
                            )
                        )
                        fig.add_trace(
                            go.Scatter(
                                x=forecast_df["ds"],
                                y=forecast_df["yhat"],
                                name="Forecast",
                                line=dict(color="#148A5B", width=2.8, dash="dash"),
                            )
                        )
                        fig.add_trace(
                            go.Scatter(
                                x=forecast_df["ds"],
                                y=forecast_df["yhat_upper"],
                                line=dict(width=0),
                                showlegend=False,
                            )
                        )
                        fig.add_trace(
                            go.Scatter(
                                x=forecast_df["ds"],
                                y=forecast_df["yhat_lower"],
                                fill="tonexty",
                                fillcolor="rgba(20,138,91,0.14)",
                                line=dict(width=0),
                                name="Confidence",
                            )
                        )
                        fig.update_layout(
                            template="plotly_white",
                            paper_bgcolor="#FFFFFF",
                            plot_bgcolor="#FFFFFF",
                            font=dict(color="#182230", family="Inter"),
                            height=450,
                            margin=dict(l=10, r=10, t=30, b=10),
                            xaxis=dict(showgrid=False, title=None),
                            yaxis=dict(gridcolor="#F0E5D8", title=None),
                            hovermode="x unified",
                        )

                        st.plotly_chart(fig, use_container_width=True)

                        latest = forecast_df["yhat"].iloc[-1]
                        prev = df["y"].iloc[-1]
                        change = latest - prev
                        pct = (change / prev) * 100 if prev else 0
                        predicted_price = format_inr(latest, ticker_override=stock) if format_inr else f"₹{latest:,.2f}"
                        trend_label = "Up" if pct > 0 else "Down"
                        trend_icon = "↗" if pct > 0 else "↘"
                        confidence_width = forecast_df["yhat_upper"].iloc[-1] - forecast_df["yhat_lower"].iloc[-1]

                        col_a, col_b, col_c = st.columns(3)
                        col_a.markdown(
                            f"<div class='metric-card'>Predicted Price<b>{predicted_price}</b><span>{pct:.2f}%</span></div>",
                            unsafe_allow_html=True,
                        )
                        col_b.markdown(
                            f"<div class='metric-card'>Trend<b>{trend_icon} {trend_label}</b></div>",
                            unsafe_allow_html=True,
                        )
                        col_c.markdown(
                            f"<div class='metric-card'>Confidence<b>{'High' if confidence_width < 15 else 'Moderate'}</b></div>",
                            unsafe_allow_html=True,
                        )

                        st.markdown("### AI Insight")
                        if pct > 2:
                            st.success("Strong upward trend predicted based on momentum.")
                        elif pct > 0:
                            st.info("Moderate growth expected.")
                        else:
                            st.warning("Possible downward trend. Exercise caution.")

                except Exception as e:
                    st.error(f"Something went wrong: {e}")
            else:
                st.info("Choose a forecast period and run a prediction to view the AI output.")
