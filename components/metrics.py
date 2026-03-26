import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error

def calculate_forecast_accuracy(actual, predicted) -> dict:
    mape = np.mean(np.abs((actual - predicted) / actual)) * 100
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    mae  = mean_absolute_error(actual, predicted)

    actual_dir    = np.sign(np.diff(actual))
    predicted_dir = np.sign(np.diff(predicted))
    dir_accuracy  = np.mean(actual_dir == predicted_dir) * 100

    return {
        'MAPE':                 round(mape, 2),
        'RMSE':                 round(rmse, 2),
        'MAE':                  round(mae, 2),
        'Directional_Accuracy': round(dir_accuracy, 2)
    }

def calculate_risk_metrics(returns) -> dict:
    sharpe  = (returns.mean() / returns.std()) * np.sqrt(252)
    neg     = returns[returns < 0]
    sortino = (returns.mean() / neg.std()) * np.sqrt(252)

    cumulative  = (1 + returns).cumprod()
    rolling_max = cumulative.cummax()
    drawdown    = (cumulative - rolling_max) / rolling_max
    max_dd      = drawdown.min()

    return {
        'Sharpe_Ratio':  round(sharpe, 2),
        'Sortino_Ratio': round(sortino, 2),
        'Max_Drawdown':  round(max_dd * 100, 2)
    }