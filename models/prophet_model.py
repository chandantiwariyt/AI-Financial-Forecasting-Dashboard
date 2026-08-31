from prophet import Prophet
import logging

logger = logging.getLogger(__name__)


def _holiday_country_for_ticker(ticker):
    """Map a Yahoo Finance ticker to a `holidays`-package country code.

    Yahoo appends an exchange suffix to non-US symbols (e.g. ``RELIANCE.NS`` on
    the NSE). We only attach a holiday calendar we're confident about:

        * ``.NS`` / ``.BO``  -> ``IN`` (India: NSE / BSE)
        * no exchange suffix -> ``US`` (e.g. AAPL, MSFT, GOOGL)

    Indices (``^NSEI``), FX pairs (``USDINR=X``) and any other exchange suffix
    return ``None`` so we skip country holidays rather than apply the wrong
    market calendar to the model.
    """
    if not ticker:
        return "US"
    symbol = str(ticker).strip().upper()
    if symbol.startswith("^") or "=" in symbol:
        return None
    if symbol.endswith((".NS", ".BO")):
        return "IN"
    if "." not in symbol:
        return "US"
    return None


def run_prophet_model(df, forecast_days=90, ticker=None):
    """
    Run Facebook Prophet forecast.

    Args:
        df: DataFrame with 'ds' (datetime) and 'y' (price) columns
        forecast_days: Number of business days to forecast
        ticker: Symbol being forecast. Selects the national holiday calendar
            (Indian holidays for .NS/.BO, US holidays for plain US symbols);
            holidays are skipped for indices/FX/other exchanges.

    Returns:
        DataFrame with forecast columns: ds, yhat, yhat_lower, yhat_upper, trend, weekly, yearly
    """
    model = Prophet(
        changepoint_prior_scale=0.05,
        seasonality_prior_scale=10,
        daily_seasonality=False,
        weekly_seasonality=True,
        yearly_seasonality=True,
        interval_width=0.95
    )

    country = _holiday_country_for_ticker(ticker)
    if country:
        try:
            model.add_country_holidays(country_name=country)
        except Exception as exc:
            # An unsupported country code in the installed holidays package
            # must not break forecasting — proceed without holiday regressors.
            logger.warning("Skipping holiday calendar %r for ticker %r: %s", country, ticker, exc)

    model.fit(df)
    future = model.make_future_dataframe(periods=forecast_days, freq='B')
    forecast = model.predict(future)
    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper', 'trend', 'weekly', 'yearly']]
