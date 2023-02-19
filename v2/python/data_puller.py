"""IN-BUILT MODULES"""
import time
import logging as log
import json
import pandas as pd

from http import HTTPStatus
from typing import Tuple

import util.util_methods as U
import webrequests.webrequests as R


_BASE_URL_ = "https://query2.finance.yahoo.com"
_UNIX_TIMESTAMP_1900_ = -2208994789 


def convert_data_to_dataframe(data, timestamp: list) -> pd.DataFrame:
    df = pd.DataFrame({
        "timestamp" : timestamp,
        "low": list(data["low"]),
        "close": list(data["close"]),
        "high": list(data["high"]),
        "open": list(data["open"]),
    })
    
    return df


def get_historical_data(ticker: str, interval: str) -> Tuple[pd.DataFrame, dict]:
    url = "{}/v8/finance/chart/{}".format(_BASE_URL_, ticker)
    
    start_timestamp = _UNIX_TIMESTAMP_1900_
    end_timestamp = int(time.time())
    parameters_dict = {"period1": start_timestamp,
        "period2": end_timestamp, "interval": interval}
    
    response = R.get_request(url, parameters_dict)
    if response.status_code != HTTPStatus.OK:
        log.error("GET request failed.", extra = {"url": response.url, "status_code" : response.status_code})
        return pd.DataFrame(), {}

    response_dict = json.loads(response.text)
    chart = response_dict["chart"]
    results = chart["result"]
    data = results[0]
    metadata = data["meta"]
    timestamp = data["timestamp"]
    data = data["indicators"]
    data = data["quote"]
    data = data[0]
    return convert_data_to_dataframe(data, timestamp), metadata


def get_simple_moving_averages(prices: pd.DataFrame, column: str, window_size: int) -> list:
    simple_moving_average = prices.loc[:, column].rolling(window = window_size).mean().tolist()
    return simple_moving_average


def get_current_simple_moving_average(prices: pd.DataFrame, column: str, window_size: int) -> float:
    simple_moving_averages = get_simple_moving_averages(prices, column, window_size)
    return simple_moving_averages[-1]


def get_exponential_moving_averages(prices: pd.DataFrame, column: str, window_size: int) -> list:
    exponential_moving_average = prices.loc[:, column].ewm(span = window_size).mean().tolist()
    return exponential_moving_average


def get_current_exponential_moving_average(prices: pd.DataFrame, column: str, window_size: int) -> float:
    exponential_moving_averages = get_exponential_moving_averages(prices, column, window_size)
    return exponential_moving_averages[-1]


def get_moving_average(type: str):
    if type == "SMA":
        return get_current_simple_moving_average
    elif type == "EMA":
        return get_current_exponential_moving_average
    else:
        log.warning("Only SMA and EMA is supported. Using SMA as default")
        return get_current_simple_moving_average


def print_technical_chart_info(df: pd.DataFrame, column: str, currency: str, last_close_price: float, interval: str) -> None:
    ema = get_moving_average("EMA")
    sma = get_moving_average("SMA")
    
    ema_20 = U.get_rounded_float_value(ema(df, column, 20), 2)
    ema_40 = U.get_rounded_float_value(ema(df, column, 40), 2)
    
    sma_50 = U.get_rounded_float_value(sma(df, column, 50), 2)
    sma_100 = U.get_rounded_float_value(sma(df, column, 100), 2)
    sma_150 = U.get_rounded_float_value(sma(df, column, 150), 2)
    sma_200 = U.get_rounded_float_value(sma(df, column, 200), 2)

    interval_alias = U.get_interval_alias(interval)

    print("###############################")
    print("--------Interval : {}-------\n".format(interval_alias))
    print(">>> Price : {} {} <<<\n".format(currency, last_close_price))
    print("EMA 20  : {} {}".format(currency, ema_20))
    print("EMA 40  : {} {}".format(currency, ema_40))
    print("SMA 50  : {} {}".format(currency, sma_50))
    print("SMA 100 : {} {}".format(currency, sma_100))
    print("SMA 150 : {} {}".format(currency, sma_150))
    print("SMA 200 : {} {}".format(currency, sma_200))
    return


def get_data(ticker: str, interval: str) -> None:
    if interval not in ["1d", "1wk", "1mo"]:
        log.warning("Only 1d, 1wk, 1mo interval is supported. Using \"1d\" as default")
        interval = "1d"
    
    data, metadata = get_historical_data(ticker, interval)
    if metadata == {} or data.empty:
        log.error("Failed to get data.")
        return

    currency = U.get_currency_symbol(metadata["currency"])
    last_close_price = float(metadata["regularMarketPrice"])

    print_technical_chart_info(data, "close", currency, last_close_price, interval)



if __name__ == "__main__":
    ticker = "aapl" # 
    ticker = U.get_upper_case_string(ticker)
    get_data(ticker, "1d") # Get daily data
    get_data(ticker, "1wk") # Get weekly data
    get_data(ticker, "1mo") # Get monthly data