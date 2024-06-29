DAY_IN_SECONDS = 60 * 60 * 24
WEEK_IN_SECONDS = DAY_IN_SECONDS * 7
MONTH_IN_SECONDS = DAY_IN_SECONDS * 31
ONE_MILLION = 1000000


CURRENCY_DICT = {
    "INR" : "₹",
}


INTERVAL_DICT = {
    "1d" : "1 Day",
    "1wk" : "1 Week",
    "1mo" : "1 Month",
}

HOST_URL = "https://query2.finance.yahoo.com"
CRUMB_URL = "v1/test/getcrumb"
FUNDAMENTAL_DATA_URL = "ws/fundamentals-timeseries/v1/finance/timeseries"
QUOTESUMMARY_URL = "v10/finance/quoteSummary"
STOCK_DETAILS_URL = "v7/finance/quote"

DEFAULT_KEY_STATISTICS_MODULE_NAME = "defaultKeyStatistics"
EARNINGS_TREND_MODULE_NAME = "earningsTrend"

GROWTH_RATE_11_TO_20_YR = 7.2 / 100

ONE_MILLION = 1000000

ALTERNATE_FIELD_NAMES = {
    "quarterlyCashCashEquivalentsAndShortTermInvestments": ["quarterlyCashCashEquivalentsAndFederalFundsSold"]
}

# As of 29th Jun 2024
RISK_FREE_RATE = 7.05 / 100
AVERAGE_MARKET_RISK_PREMIUM = 1.47 / 100