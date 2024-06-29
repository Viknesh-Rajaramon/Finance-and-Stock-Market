import util_methods as UM
import util_constants as UC
from webrequests import get_request


class Intrinsic_Value_Calculator():
    def __init__(self, ticker):
        self.ticker = ticker
        self.stock_details = None
        self.fundamental_data = None
        self.key_statistics = None
        self.earnings_trend = None
        self.data = None

    def get_stock_details(self):
        fields = ["symbol", "longName", "regularMarketPrice"]

        params = {
            "symbols": self.ticker,
        }

        url = "{}/{}".format(UC.HOST_URL, UC.STOCK_DETAILS_URL)
        response = get_request(url, params, True)
        self.stock_details = UM.get_fields_from_stock_details_payload(response, fields)
    

    def get_additional_fundamental_data_fields(self):
        additional_fields = []

        for _, values in UC.ALTERNATE_FIELD_NAMES.items():
            additional_fields = additional_fields + values

        return additional_fields


    def get_fundamental_data(self):
        fields = ["annualOperatingCashFlow", "annualNetIncome", "annualFreeCashFlow", "quarterlyTotalDebt", "quarterlyCashCashEquivalentsAndShortTermInvestments"]

        current_timestamp = UM.get_current_timestamp()
        params = {
            "merge": False,
            "padTimeSeries": True,
            "period2": current_timestamp,
            "type": fields + self.get_additional_fundamental_data_fields(),
        }

        url = "{}/{}/{}".format(UC.HOST_URL, UC.FUNDAMENTAL_DATA_URL, self.ticker)
        response = get_request(url, params)

        if response.status_code == 404:
            ticker = self.ticker.split(".")[0] + ".BO"
            url = "{}/{}/{}".format(UC.HOST_URL, UC.FUNDAMENTAL_DATA_URL, ticker)
            response = get_request(url, params)

        self.fundamental_data = UM.get_fields_from_fundamental_data_payload(response)


    def get_key_statistics(self):
        fields = ["sharesOutstanding", "beta"]

        params = {
            "modules": UC.DEFAULT_KEY_STATISTICS_MODULE_NAME,
        }

        url = "{}/{}/{}".format(UC.HOST_URL, UC.QUOTESUMMARY_URL, ticker)
        response = get_request(url, params, True)
        self.key_statistics = UM.get_fields_from_key_statistics_payload(response, fields)


    def get_earnings_trend(self):
        fields = ["+5y"]

        params = {
            "modules": UC.EARNINGS_TREND_MODULE_NAME,
        }

        url = "{}/{}/{}".format(UC.HOST_URL, UC.QUOTESUMMARY_URL, self.ticker)
        response = get_request(url, params, True)

        if response.status_code == 404:
            ticker = self.ticker.split(".")[0] + ".BO"
            url = "{}/{}/{}".format(UC.HOST_URL, UC.QUOTESUMMARY_URL, ticker)
            response = get_request(url, params, True)

        self.earnings_trend = UM.get_fields_from_earnings_trend_payload(response, fields)


    def get_discount_rate(self):
        self.data["discount_rate"] = UC.RISK_FREE_RATE + self.data["beta"] * UC.AVERAGE_MARKET_RISK_PREMIUM
    

    def get_growth_rates(self):
        self.data["growth_1_to_5"] = max(UC.GROWTH_RATE_11_TO_20_YR, self.data["growth"])
        self.data["growth_6_to_10"] = min(15 / 100, self.data["growth_1_to_5"])
        self.data["growth_11_to_20"] = UC.GROWTH_RATE_11_TO_20_YR

        del self.data["growth"]


    def projected_values(self, keys):
        for key in keys:
            projected_value = self.data[key]
            discount_factor = 1
            
            discounted_value = []
            for i in range(1, 21):
                growth_rate = 0
                if i >= 1 and i <= 5:
                    growth_rate = self.data["growth_1_to_5"]
                elif i >= 6 and i <= 10:
                    growth_rate = self.data["growth_6_to_10"]
                else:
                    growth_rate = self.data["growth_11_to_20"]

                projected_value = projected_value * (1 + growth_rate)
                discount_factor = discount_factor / (1 + self.data["discount_rate"])

                discounted_value.append(projected_value * discount_factor)

            self.data["pv_of_20_yr_" + key] = sum(discounted_value)


    def calculate_intrinsic_value(self):
        self.get_stock_details()
        self.get_fundamental_data()
        self.get_key_statistics()
        self.get_earnings_trend()
        
        self.data = UM.merge_dict(self.stock_details, self.fundamental_data, self.key_statistics, self.earnings_trend)
        
        self.get_discount_rate()
        self.get_growth_rates()

        keys = ["annualOperatingCashFlow", "annualNetIncome", "annualFreeCashFlow"]
        self.projected_values(keys)


    def print_template(self):
        print("")

        print("Name of Stock    :", self.data["longName"])
        print("Stock Symbol     :", self.data["symbol"])

        print("")
        
        print("Operating Cash Flow (Current)     : {:.2f} millions".format(self.data["annualOperatingCashFlow"] / UC.ONE_MILLION))
        print("Net Income (Current)              : {:.2f} millions".format(self.data["annualNetIncome"] / UC.ONE_MILLION))
        print("Free Cash Flow (Current)          : {:.2f} millions".format(self.data["annualFreeCashFlow"] / UC.ONE_MILLION))
        print("Total Debt (Short Term + LT Debt) : {:.2f} millions".format(self.data["quarterlyTotalDebt"] / UC.ONE_MILLION))
        print("Cash and Short Term Investments   : {:.2f} millions".format(self.data["quarterlyCashCashEquivalentsAndShortTermInvestments"] / UC.ONE_MILLION))
        print("Growth Rate (Yr 1 - 5)            : {:.2f} %".format(self.data["growth_1_to_5"] * 100))
        print("Growth Rate (Yr 6 - 10)           : {:.2f} %".format(self.data["growth_6_to_10"] * 100))
        print("Growth Rate (Yr 11 - 20)          : {:.2f} %".format(self.data["growth_11_to_20"] * 100))

        print("")
        
        print("No. of Shares Outstanding : {:.1f} millions".format(self.data["sharesOutstanding"] / UC.ONE_MILLION))

        print("")

        print("Discount Rate : {:.1f} %".format(self.data["discount_rate"] * 100))

        print("")

        print("Last Closing Price :", self.data["regularMarketPrice"])

        print("")

        print("***************** DISCOUNTED CASH FLOW METHOD **************************")
        print("PV of 20 yr Operating Cash Flow  : {:.2f} millions".format(self.data["pv_of_20_yr_annualOperatingCashFlow"] / UC.ONE_MILLION))
        print("Intrinsic Value before cash/debt : {:.2f}".format(self.data["pv_of_20_yr_annualOperatingCashFlow"] / self.data["sharesOutstanding"]))
        print("less Debt per Share              : {:.2f}".format(self.data["quarterlyTotalDebt"] / self.data["sharesOutstanding"]))
        print("Plus (+) Cash Per Share          : {:.2f}".format(self.data["quarterlyCashCashEquivalentsAndShortTermInvestments"] / self.data["sharesOutstanding"]))

        print("")

        final_intrinsic_value = (self.data["pv_of_20_yr_annualOperatingCashFlow"] - self.data["quarterlyTotalDebt"] + self.data["quarterlyCashCashEquivalentsAndShortTermInvestments"]) / self.data["sharesOutstanding"]
        print("Final Intrinsic Value Per Share : {:.2f}".format(final_intrinsic_value))
        print("(Discount)/Premium : {:.2f} %".format((self.data["regularMarketPrice"] / final_intrinsic_value - 1) * 100))
        
        print("\n***************** DISCOUNTED NET INCOME METHOD **************************")
        print("PV of 20 yr Net Income           : {:.2f} millions".format(self.data["pv_of_20_yr_annualNetIncome"] / UC.ONE_MILLION))
        print("Intrinsic Value before cash/debt : {:.2f}".format(self.data["pv_of_20_yr_annualNetIncome"] / self.data["sharesOutstanding"]))
        print("less Debt per Share              : {:.2f}".format(self.data["quarterlyTotalDebt"] / self.data["sharesOutstanding"]))
        print("Plus (+) Cash Per Share          : {:.2f}".format(self.data["quarterlyCashCashEquivalentsAndShortTermInvestments"] / self.data["sharesOutstanding"]))

        print("")

        final_intrinsic_value = (self.data["pv_of_20_yr_annualNetIncome"] - self.data["quarterlyTotalDebt"] + self.data["quarterlyCashCashEquivalentsAndShortTermInvestments"]) / self.data["sharesOutstanding"]
        print("Final Intrinsic Value Per Share : {:.2f}".format(final_intrinsic_value))
        print("(Discount)/Premium : {:.2f} %".format((self.data["regularMarketPrice"] / final_intrinsic_value - 1) * 100))
        
        print("\n***************** DISCOUNTED FREE CASH FLOW METHOD **************************")
        print("PV of 20 yr Free Cash Flow       : {:.2f} millions".format(self.data["pv_of_20_yr_annualFreeCashFlow"] / UC.ONE_MILLION))
        print("Intrinsic Value before cash/debt : {:.2f}".format(self.data["pv_of_20_yr_annualFreeCashFlow"] / self.data["sharesOutstanding"]))
        print("less Debt per Share              : {:.2f}".format(self.data["quarterlyTotalDebt"] / self.data["sharesOutstanding"]))
        print("Plus (+) Cash Per Share          : {:.2f}".format(self.data["quarterlyCashCashEquivalentsAndShortTermInvestments"] / self.data["sharesOutstanding"]))

        print("")

        final_intrinsic_value = (self.data["pv_of_20_yr_annualFreeCashFlow"] - self.data["quarterlyTotalDebt"] + self.data["quarterlyCashCashEquivalentsAndShortTermInvestments"]) / self.data["sharesOutstanding"]
        print("Final Intrinsic Value Per Share : {:.2f}".format(final_intrinsic_value))
        print("(Discount)/Premium : {:.2f} %".format((self.data["regularMarketPrice"] / final_intrinsic_value - 1) * 100))
        
        print("")



if __name__ == "__main__":
    tickers = ["AMBUJACEM", "ASIANPAINT", "BRITANNIA", "BSE", "CDSL", "COLPAL", "CROMPTON", "DABUR", "DMART", "EICHERMOT", "HAVELLS", "HCLTECH", "HDFCBANK", "HEROMOTOCO", "HINDUNILVR", "INFY", "IRCTC", "KOTAKBANK", "PIDILITIND", "RAMCOCEM", "RELIANCE", "SBICARD", "STARHEALTH", "SUNTV", "TCS", "TVSMOTOR"]
    for t in tickers:
        ticker = t + ".NS"
        iv = Intrinsic_Value_Calculator(ticker)
        iv.calculate_intrinsic_value()
        iv.print_template()
        print("####################################################################################################################################")