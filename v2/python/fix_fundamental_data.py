def replace_summaryProfile(data: dict) -> dict:
    data["sector"] = data["summaryProfile"]["sector"]
    data["industry"] = data["summaryProfile"]["industry"]

    del data["summaryProfile"]
    
    return data


def replace_defaultKeyStatistics(data: dict) -> dict:
    data["sharesOutstanding"] = data["defaultKeyStatistics"]["sharesOutstanding"]["raw"]
    data["beta"] = data["defaultKeyStatistics"]["beta"]["raw"]

    del data["defaultKeyStatistics"]

    return data


def replace_price(data: dict) -> dict:
    data["symbol"] = data["price"]["symbol"]
    data["longName"] = data["price"]["longName"]

    del data["price"]
    
    return data


def replace_cashflowStatementHistoryQuarterly(data: dict) -> dict:
    cash_flow_statement = data["cashflowStatementHistoryQuarterly"]["cashflowStatements"]

    keys = {"totalCashFromOperatingActivities" : "Annual", "capitalExpenditures" : "Annual"}
    for key, value in keys.items():
        data[key + value] = 0

    for key, value in keys.items():
        count = 0
        for quarter in cash_flow_statement:
            if value == "Quarterly" and count > 0:
                break
            data[key + value] += quarter.get(key, {}).get("raw", 0)
            count += 1

    if all([keys.get("totalCashFromOperatingActivities", ""), keys.get("capitalExpenditures", "")]):
        key = keys["totalCashFromOperatingActivities"]
        data["freeCashFlow" + key] = data["totalCashFromOperatingActivities" + key] + data["capitalExpenditures" + key]

    del data["cashflowStatementHistoryQuarterly"]
    
    return data


def replace_balanceSheetHistoryQuarterly(data: dict) -> dict:
    balance_sheet = data["balanceSheetHistoryQuarterly"]["balanceSheetStatements"]

    keys = {"cash" : "Quarterly", "shortTermInvestments" : "Quarterly", "totalCurrentLiabilities" : "Quarterly", "accountsPayable" : "Quarterly", "otherCurrentLiab" : "Quarterly", "longTermDebt" : "Quarterly"}
    for key, value in keys.items():
        data[key + value] = 0

    for key, value in keys.items():
        count = 0
        for quarter in balance_sheet:
            if value == "Quarterly" and count > 0:
                break
            data[key + value] += quarter.get(key, {}).get("raw", 0)
            count += 1

    if all([keys["cash"], keys["shortTermInvestments"]]):
        key = keys["cash"]
        data["cashAndShortTermInvestments" + key] = data["cash" + key] + data["shortTermInvestments" + key]


    if all([keys.get("totalCurrentLiabilities", ""), keys.get("accountsPayable", ""), keys.get("otherCurrentLiab", ""), keys.get("longTermDebt", "")]):
        key = keys.get("totalCurrentLiabilities", "")
        data["totalDebt" + key] = data["totalCurrentLiabilities" + key] - data["accountsPayable" + key] - data["otherCurrentLiab" + key] + data["longTermDebt" + key]

    del data["balanceSheetHistoryQuarterly"]
    
    return data


def fix_fundamental_data(data: dict) -> dict:
    new_data = replace_summaryProfile(data)
    new_data = replace_defaultKeyStatistics(data)
    new_data = replace_price(data)
    new_data = replace_cashflowStatementHistoryQuarterly(data)
    new_data = replace_balanceSheetHistoryQuarterly(data)
    return new_data