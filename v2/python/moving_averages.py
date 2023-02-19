import pandas as pd
import logging as log


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