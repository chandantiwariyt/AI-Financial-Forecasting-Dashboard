from prophet import Prophet
import pandas as pd

def prophet_forecast(df, forecast_days=90):
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
    future = model.make_future_dataframe(periods=forecast_days, freq='B')
    forecast = model.predict(future)
    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper', 'trend', 'weekly', 'yearly']]