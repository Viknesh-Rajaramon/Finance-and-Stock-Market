from string import Template
from datetime import datetime


def get_technical_chart_print_template() -> Template:
    template = Template(
        "###############################" + "\n" +
        "--------Interval : ${interval_alias}-------\n" + "\n" +
        ">>> Price : ${currency} ${last_close_price} <<<\n" + "\n" +
        "EMA 20  : ${currency} ${ema_20}" + "\n" +
        "EMA 40  : ${currency} ${ema_40}" + "\n" +
        "SMA 50  : ${currency} ${sma_50}" + "\n" +
        "SMA 100  : ${currency} ${sma_100}" + "\n" +
        "SMA 150  : ${currency} ${sma_150}" + "\n" +
        "SMA 200  : ${currency} ${sma_200}" + "\n"
    )

    return template


def get_fundamental_data_print_template() -> Template:
    template = Template(
        "###############################" + "\n" +
        "# Time : ${current_time}\n" +
        "#" + "\n" +
        "# ${longName} (${symbol})" + "\n" +
        "# [${sector}, ${industry}]" + "\n" + 
        "#\n###############################" + "\n"
        "# Operating Cash Flow (Current) : ${currency} ${totalCashFromOperatingActivitiesAnnual} millions" + "\n" +
        "# Total Debt (Short Term + LT Debt) : ${currency} ${totalDebtQuarterly} millions" + "\n" +
        "# Cash and Short Term Investments : ${currency} ${cashAndShortTermInvestmentsQuarterly} millions" + "\n" +
        "# Number of Shares Outstanding : ${sharesOutstanding} millions" + "\n" +
        "-------------------------------" + "\n"
    )

    """
        "Discount Rate : ${discount_rate} [Beta:${beta}]" + "\n"
        "\nEPS Growth (5 yr) : ${eps5Y}" + "\n"
        "EPS Growth (10 yr) : ${eps10Y}" + "\n"
        "EPS Growth (20 yr) : ${eps20Y}" + "\n
    """

    return template