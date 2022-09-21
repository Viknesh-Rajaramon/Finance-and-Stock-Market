import pandas as pd
import numpy as np
import math
import yfinance as yf
import json
import requests
import re
import matplotlib.pyplot as plt

from datetime import datetime, date
from os import system
from sklearn.impute import SimpleImputer

class IV_CALCULATION:
    operating_cash_flow = 0
    net_income = 0
    total_debt = 0
    cash_and_short_term_investments = 0
    number_of_shares = 0
    discount_rate = 0.0
    ticker = ""
    info = ""
    million = 1000000
    cash_flow = 0
    income_statement = 0
    balance_sheet = 0
    stats = 0
    beta = 0
    risk_free_rate = float(0.64/100)
    market_risk_premium = float(5.00/100)
    eps_5y = 0.0
    eps_10y = 0.0
    eps_20y = float(4.18/100)
    year = [date.today().year]
    operating_cash_flow_projected = []
    discount_factor = [1]
    discounted_value = []
    last_close_price = 0.0
    final_intrinsic_value_10_yr = 0.0
    discount_premium_10_yr = 0.0
    final_intrinsic_value_20_yr = 0.0
    discount_premium_20_yr = 0.0
    currency = {'USD' : '$', 'INR' : ''}
    
    def __init__(self, ticker):
        self.ticker = ticker.upper()
        self.company = yf.Ticker(self.ticker)
        self.info = self.company.info
        self.cash_flow = self.company.quarterly_cashflow
        self.income_statement = self.company.quarterly_financials
        self.balance_sheet = self.company.quarterly_balance_sheet
        self.last_close_price = self.info['previousClose']
    
    def get_operating_cash_flow(self):
        self.operating_cash_flow = round(float(np.nansum(self.cash_flow.loc['Total Cash From Operating Activities', :][0:4])), 2)
    
    def get_net_income(self):
        self.net_income = round(float(np.nansum(self.income_statement.loc['Net Income', :][0:4])), 2)
    
    def get_total_debt(self):
        self.total_debt = round(float(np.nansum([self.balance_sheet.loc['Long Term Debt', :][0], self.balance_sheet.loc['Short Long Term Debt', :][0]])), 2)
    
    def get_cash_and_short_term_investments(self):
        self.cash_and_short_term_investments = round(float(np.nansum([self.balance_sheet.loc['Cash', :][0], self.balance_sheet.loc['Short Term Investments', :][0]])), 2)
    
    def get_number_of_shares(self):
        self.number_of_shares = round(self.info['sharesOutstanding'], 2)
    
    def get_discount_rate(self):
        self.beta = self.info['beta']
        
        if(self.beta < 0.8):
            self.discount_rate = self.risk_free_rate + 0.8 * self.market_risk_premium
        elif((self.beta <= 0.8) and (self.beta < 1.0)):
            self.discount_rate = self.risk_free_rate + 1.0 * self.market_risk_premium
        elif((self.beta <= 1.0) and (self.beta < 1.1)):
            self.discount_rate = self.risk_free_rate + 1.1 * self.market_risk_premium
        elif(self.beta <= 1.1 and self.beta < 1.2):
            self.discount_rate = self.risk_free_rate + 1.2 * self.market_risk_premium
        elif(self.beta <= 1.2 and self.beta < 1.3):
            self.discount_rate = self.risk_free_rate + 1.3 * self.market_risk_premium
        elif(self.beta <= 1.3 and self.beta < 1.4):
            self.discount_rate = self.risk_free_rate + 1.4 * self.market_risk_premium
        elif(self.beta <= 1.4 and self.beta < 1.5):
            self.discount_rate = self.risk_free_rate + 1.5 * self.market_risk_premium
        else:
            self.discount_rate = self.risk_free_rate + 1.6 * self.market_risk_premium
    
    def get_eps_growth_rate(self):
        r = requests.get("https://finance.yahoo.com/quote/{}/analysis?p={}".format(self.ticker, self.ticker))
        data = json.loads(re.search('root\.App\.main\s*=s*(.*);', r.text).group(1))
        field = [t for t in data["context"]["dispatcher"]["stores"]["QuoteSummaryStore"]["earningsTrend"]["trend"] if t["period"] == "+5y"]
        
        self.eps_5y = float(field[0]['growth']['raw'])
        self.eps_10y = min(float(self.eps_5y/2), float(15/100))
    
    def compute_discounted_cash_flow(self):
        self.operating_cash_flow_projected.append(self.operating_cash_flow)
        self.discounted_value.append(self.operating_cash_flow)

        for i in range(1, 21, 1):
            self.year.append(date.today().year + i)
            growth_rate = 0
            if(i <= 5):
                growth_rate = self.eps_5y
            elif(i <= 10):
                growth_rate = self.eps_10y
            else:
                growth_rate = self.eps_20y
            self.operating_cash_flow_projected.append(round(self.operating_cash_flow_projected[i-1] * (1 + growth_rate), 2))
            self.discount_factor.append((self.discount_factor[i-1] / (1 + self.discount_rate)))
            self.discounted_value.append(round(self.operating_cash_flow_projected[i] * self.discount_factor[i], 2))
        
        self.operating_cash_flow_projected.pop(0)
        self.discount_factor.pop(0)
        self.discounted_value.pop(0)
    
    def pv_cash_flow_10_yr(self):
        pv_cash_flow = 0
        
        for i in range(0, 10, 1):
            pv_cash_flow += self.discounted_value[i]
        
        intrinsic_value_before_debt = float(pv_cash_flow / self.number_of_shares)
        less_debt_per_share = float(self.total_debt / self.number_of_shares)
        plus_cash_per_share = float(self.cash_and_short_term_investments / self.number_of_shares)

        self.final_intrinsic_value_10_yr = intrinsic_value_before_debt - less_debt_per_share + plus_cash_per_share
        self.discount_premium_10_yr = (self.last_close_price - self.final_intrinsic_value_10_yr) / self.final_intrinsic_value_10_yr
    
    def pv_cash_flow_20_yr(self):
        pv_cash_flow = 0
        
        for i in range(0, 20, 1):
            pv_cash_flow += self.discounted_value[i]
        
        intrinsic_value_before_debt = round(float(pv_cash_flow / self.number_of_shares), 2)
        less_debt_per_share = round(float(self.total_debt / self.number_of_shares), 2)
        plus_cash_per_share = round(float(self.cash_and_short_term_investments / self.number_of_shares), 2)

        self.final_intrinsic_value_20_yr = intrinsic_value_before_debt - less_debt_per_share + plus_cash_per_share
        self.discount_premium_20_yr = (self.last_close_price - self.final_intrinsic_value_20_yr) / self.final_intrinsic_value_20_yr
    
    def moving_averages_price_1_day_interval(self):
        history = self.company.history(period = "max", interval = "1d")
        closing_prices = history.iloc[:, 3]

        imputer = SimpleImputer(missing_values = np.nan, strategy = 'mean')
        imputer = imputer.fit(closing_prices.values.reshape(-1, 1))

        closing_prices = imputer.transform(closing_prices.values.reshape(-1, 1))

        closing_prices = pd.DataFrame(closing_prices, columns = ['Close'])

        self.daily_ema_20 = np.array(round(closing_prices.ewm(span = 20, adjust = False).mean().iloc[-1], 2))[0]
        self.daily_ema_40 = np.array(round(closing_prices.ewm(span = 24, adjust = False).mean().iloc[-1], 2))[0]

        self.daily_sma_50 = np.array(round(closing_prices.rolling(window = 50).mean().iloc[-1], 2))[0]
        self.daily_sma_100 = np.array(round(closing_prices.rolling(window = 100).mean().iloc[-1], 2))[0]
        self.daily_sma_150 = np.array(round(closing_prices.rolling(window = 150).mean().iloc[-1], 2))[0]
        self.daily_sma_200 = np.array(round(closing_prices.rolling(window = 200).mean().iloc[-1], 2))[0]
    
    def moving_averages_price_1_week_interval(self):
        history = self.company.history(period = "max", interval = "1wk")
        closing_prices = history.iloc[:, 3]

        imputer = SimpleImputer(missing_values = np.nan, strategy = 'mean')
        imputer = imputer.fit(closing_prices.values.reshape(-1, 1))

        closing_prices = imputer.transform(closing_prices.values.reshape(-1, 1))

        closing_prices = pd.DataFrame(closing_prices, columns = ['Close'])

        self.weekly_ema_20 = np.array(round(closing_prices.ewm(span = 20, adjust = False).mean().iloc[-1], 2))[0]
        self.weekly_ema_40 = np.array(round(closing_prices.ewm(span = 24, adjust = False).mean().iloc[-1], 2))[0]

        self.weekly_sma_50 = np.array(round(closing_prices.rolling(window = 50).mean().iloc[-1], 2))[0]
        self.weekly_sma_100 = np.array(round(closing_prices.rolling(window = 100).mean().iloc[-1], 2))[0]
        self.weekly_sma_150 = np.array(round(closing_prices.rolling(window = 150).mean().iloc[-1], 2))[0]
        self.weekly_sma_200 = np.array(round(closing_prices.rolling(window = 200).mean().iloc[-1], 2))[0]
    
    def plot_discounted_cash_flow_projection(self, years):
        cash_flow_projected = np.divide(self.operating_cash_flow_projected, 1000000)
        discount_value = np.divide(self.discounted_value, 1000000)

        year = [(i + 1) for i in range(0, years, 1)]

        plt.suptitle("Intrinsic Value", fontweight = 'bold')
        plt.title("(Discounted Cash Flow Method {} years)".format(str(years)), fontweight = 'bold')
        plt.xlabel("Year", fontweight = 'bold')
        plt.ylabel("Value (in millions - {})".format(self.currency[self.info['currency']]), fontweight = 'bold')
        plt.ylim(bottom = 0, top = cash_flow_projected[-1] + (pow(10, math.floor(math.log10(cash_flow_projected[-1]))) * 5))

        plt.plot(year, cash_flow_projected[0 : years], color = 'blue', label = 'Cash Flow (Projected)', marker = "D")
        plt.plot(year, discount_value[0 : years], color = 'red', label = 'Cash Flow (Discounted)', marker = "s")

        plt.legend(loc = 'upper left')
        plt.show()

    def compute_IV(self):
        self.get_operating_cash_flow()
        self.get_net_income()
        self.get_total_debt()
        self.get_cash_and_short_term_investments()
        self.get_number_of_shares()
        self.get_discount_rate()
        self.get_eps_growth_rate()
        self.compute_discounted_cash_flow()
        self.pv_cash_flow_10_yr()
        self.pv_cash_flow_20_yr()
        self.moving_averages_price_1_day_interval()
        self.moving_averages_price_1_week_interval()

    def print_info(self):
        print("\033c###############################")
        
        print("# " + str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
        print("# ")
        print("# {} ({})".format(self.info['longName'], self.info['symbol']))
        print("# [{}, {}]".format(self.info['sector'], self.info['industry']))
        
        print("#\n###############################")
        
        print("# Operating Cash Flow (Current) : {} {} millions".format(self.currency[self.info['currency']], str(round(self.operating_cash_flow / self.million, 2))))
        print("# Net Income (ttm) : {} {} millions".format(self.currency[self.info['currency']], str(round(self.net_income / self.million, 2))))
        print("# Total Debt (Short Term + LT Debt) : {} {} millions".format(self.currency[self.info['currency']], str(round(self.total_debt / self.million, 2))))
        print("# Cash and Short Term Investments : {} {} millions".format(self.currency[self.info['currency']], str(round(self.cash_and_short_term_investments / self.million, 2))))
        print("# Number of Shares Outstanding : {} millions".format(str(round(self.number_of_shares / self.million, 2))))
        
        print("-------------------------------")
        
        print("Discount Rate : {:.1%} [Beta:{}]".format(self.discount_rate, round(self.beta, 1)))
        print("\nEPS Growth (5 yr) : {:.2%}".format(self.eps_5y))
        print("EPS Growth (10 yr) : {:.2%}".format(self.eps_10y))
        print("EPS Growth (20 yr) : {:.2%}".format(self.eps_20y))
        
        print("===============================")
        
        print("Final Intrinsic Value (10 yr) : {} {}".format(self.currency[self.info['currency']], str(round(self.final_intrinsic_value_10_yr, 2))))
        print("(Discount)/Premium (10 yr) : {:.2%}".format(self.discount_premium_10_yr))
        print("\nFinal Intrinsic Value (20 yr) : {} {}".format(self.currency[self.info['currency']], str(round(self.final_intrinsic_value_20_yr, 2))))
        print("(Discount)/Premium (20 yr) : {:.2%}".format(self.discount_premium_20_yr))
        
        print("###############################")
        
        print("--------Interval : 1 Day-------\n")
        print(">>> Price : {} {} <<<\n".format(self.currency[self.info['currency']], self.last_close_price))
        print("EMA 20  : {} {}".format(self.currency[self.info['currency']], self.daily_ema_20))
        print("EMA 40  : {} {}".format(self.currency[self.info['currency']], self.daily_ema_40))
        print("SMA 50  : {} {}".format(self.currency[self.info['currency']], self.daily_sma_50))
        print("SMA 100 : {} {}".format(self.currency[self.info['currency']], self.daily_sma_100))
        print("SMA 150 : {} {}".format(self.currency[self.info['currency']], self.daily_sma_150))
        print("SMA 200 : {} {}".format(self.currency[self.info['currency']], self.daily_sma_200))
        
        print("###############################")
        
        print("--------Interval : 1 Week-------\n")
        print(">>> Price : {} {} <<<\n".format(self.currency[self.info['currency']], self.last_close_price))
        print("EMA 20  : {} {}".format(self.currency[self.info['currency']], self.weekly_ema_20))
        print("EMA 40  : {} {}".format(self.currency[self.info['currency']], self.weekly_ema_40))
        print("SMA 50  : {} {}".format(self.currency[self.info['currency']], self.weekly_sma_50))
        print("SMA 100 : {} {}".format(self.currency[self.info['currency']], self.weekly_sma_100))
        print("SMA 150 : {} {}".format(self.currency[self.info['currency']], self.weekly_sma_150))
        print("SMA 200 : {} {}".format(self.currency[self.info['currency']], self.weekly_sma_200))

        self.plot_discounted_cash_flow_projection(10)
        self.plot_discounted_cash_flow_projection(20)


if __name__ == "__main__":
    stock = IV_CALCULATION(input("Enter the Stock Symbol/Ticker : "))
    stock.compute_IV()
    stock.print_info()
