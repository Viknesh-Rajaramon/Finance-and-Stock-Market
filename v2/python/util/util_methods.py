from .util_constants import _DAY_IN_SECONDS_, _WEEK_IN_SECONDS_, _MONTH_IN_SECONDS_, _CURRENCY_DICT_, _INTERVAL_DICT_, _ONE_MILLION_
from decimal import Decimal


def get_days_in_seconds(days: int) -> int:
    return days * _DAY_IN_SECONDS_


def get_weeks_in_seconds(weeks: int) -> int:
    return weeks * _WEEK_IN_SECONDS_


def get_months_in_seconds(months: int) -> int:
    return months * _MONTH_IN_SECONDS_


def get_currency_symbol(currency: str) -> str:
    return _CURRENCY_DICT_.get(currency, currency)


def get_upper_case_string(s: str) -> str:
    return s.upper()


def get_interval_alias(interval: str) -> str:
    return _INTERVAL_DICT_.get(interval, "")


def get_rounded_float_value(number: float, precision: int) -> Decimal:
    rounding_string = "0"
    if precision > 0:
        rounding_string = rounding_string + "." + "".join(["0" for i in range(0, precision)])
    
    decimalValue = Decimal(number)
    roundedNumber = decimalValue.quantize(Decimal(rounding_string))
    return roundedNumber


def convert_to_millions(num: int) -> Decimal:
    millions = num / _ONE_MILLION_
    return get_rounded_float_value(millions, 2)