import util_constants as UC
from datetime import datetime


def merge_dict(*args):
    output = {}
    for arg in args:
        output.update(arg)
    return output


def get_current_timestamp():
    current_time = datetime.now()
    timestamp = int(datetime.timestamp(current_time))
    return timestamp


def get_fields_from_stock_details_payload(response, fields):
    content = response.json()
    fields_data = {}
    result = content["quoteResponse"]["result"][0]
    for field in fields:
        for key in list(result.keys()):
            if field == key:
                fields_data[key] = result[key]
    
    return fields_data


def get_fields_from_fundamental_data_payload(response):
    content = response.json()
    fields_data = {}
    result = content["timeseries"]["result"]
    
    for i in range(len(result)):
        field = result[i]["meta"]["type"][0]
        content = None
        try:
            content = result[i][field]
        except:
            if field not in UC.ALTERNATE_FIELD_NAMES.keys():
                fields_data[field] = 0
                continue

            for alternate_field in UC.ALTERNATE_FIELD_NAMES[field]:
                try:
                    for j in range(len(result)):
                        if result[j]["meta"]["type"][0] == alternate_field:
                            content = result[j][alternate_field]
                    break
                except:
                    continue

        for j in range(len(content) - 1, -1, -1):
            if content[j] is not None:
                break
        
        field_data = content[j]["reportedValue"]["raw"]
        fields_data[field] = field_data
    
    return fields_data


def get_fields_from_key_statistics_payload(response, fields):
    content = response.json()
    fields_data = {}
    result = content["quoteSummary"]["result"][0]

    for key in list(result.keys()):
        if key == UC.DEFAULT_KEY_STATISTICS_MODULE_NAME:
            for field in fields:
                for f in result[key]:
                    if field == f:
                        fields_data[f] = result[key][f]["raw"]
    
    return fields_data


def get_fields_from_earnings_trend_payload(response, fields):
    content = response.json()
    fields_data = {}

    if content["quoteSummary"]["result"] is None:
        fields_data["growth"] = UC.GROWTH_RATE_11_TO_20_YR
        return fields_data

    result = content["quoteSummary"]["result"][0]
    flag = False

    for key in list(result.keys()):
        if key == UC.EARNINGS_TREND_MODULE_NAME:
            for field in fields:
                for i in range(len(result[key]["trend"])):
                    if result[key]["trend"][i]["period"] == field:
                        try:
                            fields_data["growth"] = result[key]["trend"][i]["growth"]["raw"]
                        except:
                            flag = True
                        
                if flag:
                    for i in range(len(result[key]["trend"])):
                        if result[key]["trend"][i]["period"] == "+1y":
                            fields_data["growth"] = result[key]["trend"][i]["growth"]["raw"]
                            flag = False
    
    return fields_data