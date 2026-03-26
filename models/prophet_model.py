from prophet import Prophet
import pandas as pd

def run_prophet_forecast(df: pd.DataFrame, forecast_days: int = 90) -> pd.DataFrame:
    model = Prophet(
        changepoint_prior_scale=0.05,
        seasonality_prior_scale=10,
        daily_seasonality=False,
        weekly_seasonality=True,
        yearly_seasonality=True,
        interval_width=0.95
    )

    model.add_country_holidays(country_name='US')
    model.fit(df)

    future   = model.make_future_dataframe(periods=forecast_days, freq='B')
    forecast = model.predict(future)

    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper', 'trend', 'weekly', 'yearly']]

def get_prophet_components(model, forecast) -> dict:
    return {
        'trend':  forecast[['ds', 'trend']],
        'weekly': forecast[['ds', 'weekly']],
        'yearly': forecast[['ds', 'yearly']]
    }