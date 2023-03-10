"""IN-BUILT MODULES"""
import logging as log
import json
import pandas as pd

from http import HTTPStatus
from datetime import datetime, timezone

import util.util_methods as U
import webrequests.webrequests as R


_HOST_URL_ = "https://query2.finance.yahoo.com"
_FUNDAMENTAL_DATA_URL_ = "v10/finance/quoteSummary"
_MODULES_ = ["assetProfile", "summaryDetail", "price", "incomeStatementHistory", "incomeStatementHistoryQuarterly", "balanceSheetHistory", "balanceSheetHistoryQuarterly", "cashflowStatementHistory", "cashflowStatementHistoryQuarterly", "defaultKeyStatistics", "financialData", "earnings", "earningsTrend", "industryTrend", "indexTrend", "sectorTrend"]



def get_fundamental_data(ticker: str, modules: list = []) -> dict:
    url = "{}/{}/{}".format(_HOST_URL_, _FUNDAMENTAL_DATA_URL_, ticker)
    
    valid_modules = []
    for m in modules:
        if m in _MODULES_:
            valid_modules.append(m)
        
    if valid_modules == []:
        log.warning("No modules found. Using all modules by default.")
        valid_modules = _MODULES_
    
    parameters_dict = {"modules": valid_modules}
    
    response = R.get_request(url, parameters_dict)
    if response.status_code != HTTPStatus.OK:
        log.error("GET request failed. url : {}, status_code : {}".format(response.url, response.status_code))
        return {}

    response_dict = json.loads(response.text)
    data = response_dict["quoteSummary"]["result"][0]
    return data


def get_raw_values(data: dict) -> dict:
    for key, value in data.items():
        if isinstance(value, dict) and "raw" in value:
            data[key] = value["raw"]

    return data


def convert_values_to_percent(data: dict, columns: list) -> dict:
    for column in columns:
        if column in data.keys():
            data[column] = data[column] * 100

    return data


def convert_values_to_date(data: dict, columns: list) -> dict:
    for column in columns:
        if column in data.keys():
            data[column] = datetime.fromtimestamp(data[column], timezone.utc).strftime('%Y-%m-%d')

    return data


def fix_asset_profile(data: dict) -> dict:
    asset_profile = data.get("assetProfile", {})
    if asset_profile == {}:
        return data
    
    company_officers = asset_profile.get("companyOfficers", [])
    for officer in company_officers:
        officer = get_raw_values(officer)
    
    data["assetProfile"] = asset_profile
    return data


def fix_summary_detail(data: dict) -> dict:
    summary_detail = data.get("summaryDetail", {})
    if summary_detail == {}:
        return data
    
    percent_columns = ["dividendYield", "payoutRatio", "trailingAnnualDividendYield"]
    date_columns = ["exDividendDate"]

    summary_detail = get_raw_values(summary_detail)
    summary_detail = convert_values_to_percent(summary_detail, percent_columns)
    summary_detail = convert_values_to_date(summary_detail, date_columns)
    
    data["summaryDetail"] = summary_detail
    return data


def fix_price(data: dict) -> dict:
    price = data.get("price", {})
    if price == {}:
        return data
    
    percent_columns = ["postMarketChangePercent", "regularMarketChangePercent"]

    price = get_raw_values(price)
    price = convert_values_to_percent(price, percent_columns)
    
    data["price"] = price
    return data


def fix_default_key_statistics(data: dict) -> dict:
    default_key_statistics = data.get("defaultKeyStatistics", {})
    if default_key_statistics == {}:
        return data
    
    percent_columns = ["profitMargins", "sharesPercentSharesOut", "heldPercentInsiders", "heldPercentInstitutions", "shortPercentOfFloat", "earningsQuarterlyGrowth", "52WeekChange", "SandP52WeekChange"]
    date_columns = ["dateShortInterest", "lastFiscalYearEnd", "nextFiscalYearEnd", "mostRecentQuarter", "lastSplitDate", "lastDividendDate"]

    default_key_statistics = get_raw_values(default_key_statistics)
    default_key_statistics = convert_values_to_percent(default_key_statistics, percent_columns)
    default_key_statistics = convert_values_to_date(default_key_statistics, date_columns)
    
    data["defaultKeyStatistics"] = default_key_statistics
    return data


def fix_financial_data(data: dict) -> dict:
    financial_data = data.get("financialData", {})
    if financial_data == {}:
        return data
    
    percent_columns = ["returnOnAssets", "returnOnEquity", "earningsGrowth", "revenueGrowth", "grossMargins", "ebitdaMargins", "operatingMargins", "profitMargins"]

    financial_data = get_raw_values(financial_data)
    financial_data = convert_values_to_percent(financial_data, percent_columns)
    
    data["financialData"] = financial_data
    return data


def fix_estimates(estimates: list) -> dict:
    for i in range(0, len(estimates)):
        estimates[i] = get_raw_values(estimates[i])
        
    estimates_dict = {}
    period = U.get_dict_keys(U._GROWTH_ESTIMATES_PERIOD_DICT_)
    for p in period:
        for i in range(0, len(estimates)):
            if estimates[i].get("period", "") == "":
                estimates_dict[p] = None
            elif estimates[i]["period"] == p:
                if estimates[i].get("growth", None) in [{}, None]:
                    estimates_dict[p] = None
                else:
                    estimates_dict[p] = estimates[i]["growth"]
    
    return estimates_dict


def fix_growth_estimates(data: dict, ticker: str) -> dict:
    index_trend = data.get("indexTrend", {})
    if index_trend != {}:
        index_trend = U.remove_keys_from_dict(index_trend, ["maxAge", "peRatio", "pegRatio"])
        index_trend = get_raw_values(index_trend)
        index_trend["symbol"] = ticker if index_trend.get("symbol", None) is None else index_trend["symbol"]
        estimates = index_trend.get("estimates", [])
        index_trend["estimates"] = fix_estimates(estimates)
        del data["indexTrend"]
    
    industry_trend = data.get("industryTrend", {})
    if industry_trend != {}:
        industry_trend = U.remove_keys_from_dict(industry_trend, ["maxAge", "peRatio", "pegRatio"])
        industry_trend = get_raw_values(industry_trend)
        industry_trend["symbol"] = "Industry" if industry_trend.get("symbol", None) is None else industry_trend["symbol"]
        estimates = industry_trend.get("estimates", [])
        industry_trend["estimates"] = fix_estimates(estimates)
        del data["industryTrend"]
    
    sector_trend = data.get("sectorTrend", {})
    if sector_trend != {}:
        sector_trend = U.remove_keys_from_dict(sector_trend, ["maxAge", "peRatio", "pegRatio"])
        sector_trend = get_raw_values(sector_trend)
        sector_trend["symbol"] = "Sector(s)" if sector_trend.get("symbol", None) is None else sector_trend["symbol"]
        estimates = sector_trend.get("estimates", [])
        sector_trend["estimates"] = fix_estimates(estimates)
        del data["sectorTrend"]

    earnings_trend = data.get("earningsTrend", {})
    if earnings_trend != {}:
        trend = earnings_trend.get("trend", [])
        
        if trend != []:
            stock_trend = {}
            stock_trend["symbol"] = ticker
            
            percent_columns = ["growth"]
            
            estimates = []
            for i in range(0, len(trend)):
                trend[i] = get_raw_values(trend[i])
                trend[i] = convert_values_to_percent(trend[i], percent_columns)
                
                earnings_estimates = trend[i].get("earningsEstimate", {})
                earnings_estimates = get_raw_values(earnings_estimates)

                growth = trend[i].get("growth", {})
                earnings_estimates_growth = earnings_estimates.get("growth", {})
                if "period" in trend[i].keys():
                    if growth != {}:
                        estimates.append({"period": trend[i]["period"], "growth": growth})
                    else:
                        estimates.append({"period": trend[i]["period"], "growth": earnings_estimates_growth})

            stock_trend["estimates"] = fix_estimates(estimates)
        
            df_dict = {
                stock_trend["symbol"]: stock_trend["estimates"],
                industry_trend["symbol"]: industry_trend["estimates"],
                sector_trend["symbol"]: sector_trend["estimates"],
                index_trend["symbol"]: index_trend["estimates"],
            }
            data["growthEstimates"] = pd.DataFrame(df_dict)
        
        del data["earningsTrend"]
    
    return data


def fix_fundamental_data(data: dict, ticker: str) -> dict:
    data = fix_asset_profile(data)
    data = fix_summary_detail(data)
    data = fix_price(data)
    data = fix_default_key_statistics(data)
    data = fix_financial_data(data)
    data = fix_growth_estimates(data, ticker)
    return data


def get_data(ticker: str) -> None:
    data = get_fundamental_data(ticker)
    if data == {}:
        log.error("Failed to get data.")
        return
    
    data = fix_fundamental_data(data, ticker)
    print(data)



if __name__ == "__main__":
    ticker = "aapl"
    ticker = U.get_upper_case_string(ticker)
    get_data(ticker) # Get fundamental data
