"""IN-BUILT MODULES"""
import logging as log
import json

from http import HTTPStatus
from datetime import datetime

import util.util_methods as U
import webrequests.webrequests as R
import print_template as T
from fix_fundamental_data import fix_fundamental_data


_HOST_URL_ = "https://query2.finance.yahoo.com"
_FUNDAMENTAL_DATA_URL_ = "v10/finance/quoteSummary"
_MODULES_ =["summaryProfile", "defaultKeyStatistics", "price", "balanceSheetHistoryQuarterly", "cashflowStatementHistoryQuarterly"]


def get_fundamental_data(ticker: str) -> dict:
    url = "{}/{}/{}".format(_HOST_URL_, _FUNDAMENTAL_DATA_URL_, ticker)
    
    parameters_dict = {"modules": _MODULES_}
    
    response = R.get_request(url, parameters_dict)
    if response.status_code != HTTPStatus.OK:
        log.error("GET request failed.", extra = {"url": response.url, "status_code" : response.status_code})
        return {}

    response_dict = json.loads(response.text)
    data = response_dict["quoteSummary"]["result"][0]
    return data


def print_fundamental_data_info(data: dict, currency: str) -> None:
    template_params = {
        "sector": data["sector"],
        "industry": data["industry"],
        "symbol": data["symbol"],
        "longName": data["longName"],
        "currency": currency,
        "current_time": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "beta": U.get_rounded_float_value(data["beta"], 2),
        "sharesOutstanding": U.convert_to_millions(data["sharesOutstanding"]),
        "totalCashFromOperatingActivitiesAnnual": U.convert_to_millions(data["totalCashFromOperatingActivitiesAnnual"]),
        "cashAndShortTermInvestmentsQuarterly": U.convert_to_millions(data["cashAndShortTermInvestmentsQuarterly"]),
        "totalDebtQuarterly": U.convert_to_millions(data["totalDebtQuarterly"])
    }

    template = T.get_fundamental_data_print_template()
    info = template.substitute(template_params)
    print(info)
    return


def get_data(ticker: str) -> None:    
    data = get_fundamental_data(ticker)
    if data == {}:
        log.error("Failed to get data.")
        return
    
    data = fix_fundamental_data(data)
    print_fundamental_data_info(data, "$")



if __name__ == "__main__":
    ticker = "bdx"
    ticker = U.get_upper_case_string(ticker)
    get_data(ticker) # Get fundamental data