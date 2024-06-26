from requests import request, Response
from util_constants import HOST_URL, CRUMB_URL

def modify_query_params(params: dict) -> dict:
    for key, value in params.items():
        if isinstance(value, (str, int, float)):
            params[key] = str(value)
        elif isinstance(value, (list, tuple)):
            params[key] = ",".join(value)
    
    return params


def get_cookies():
    url = "https://fc.yahoo.com"
    response = request(method = "GET", url = url)

    cookies = response.headers.get("Set-Cookie", "").split(";")[0]
    return cookies


def get_yahoo_finance_crumb(headers):
    url = HOST_URL + "/" + CRUMB_URL
    response = request(method = "GET", url = url, headers = headers)

    crumb = response.content.decode()
    return crumb


def get_request(get_url: str, params: dict, include_crumb = False) -> Response:
    cookie = get_cookies()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Cookie": cookie,
    }

    if include_crumb:
        crumb = get_yahoo_finance_crumb(headers)
        params["crumb"] = crumb
    
    params = modify_query_params(params)

    response = request(method = "GET", url = get_url, params = params, headers = headers)
    return response
