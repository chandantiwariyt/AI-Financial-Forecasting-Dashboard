from neuralprophet import NeuralProphet
import pandas as pd

def run_prophet_forecast(df: pd.DataFrame, forecast_days: int = 90) -> pd.DataFrame:
    model = NeuralProphet(
        weekly_seasonality=True,
        yearly_seasonality=True,
    )
    model.fit(df, freq='B')
    future = model.make_future_dataframe(df, periods=forecast_days)
    forecast = model.predict(future)
    forecast = forecast.rename(columns={'yhat1': 'yhat'})
    forecast['yhat_lower'] = forecast['yhat'] * 0.95
    forecast['yhat_upper'] = forecast['yhat'] * 1.05
    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
```

Push again:
```
git add .
git commit -m "Updated prophet model"
git push