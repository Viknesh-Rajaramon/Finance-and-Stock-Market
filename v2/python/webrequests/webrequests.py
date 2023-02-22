from requests import request, Response


def modify_query_params(params: dict) -> dict:
    for key, value in params.items():
        if isinstance(value, (str, int, float)):
            params[key] = str(value)
        elif isinstance(value, (list, tuple)):
            params[key] = ",".join(value)
    
    return params


def get_request(get_url: str, params: dict) -> Response:
    headers = {
        "Content-Type" : "application/x-www-form-urlencoded;charset=utf-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    }
    params = modify_query_params(params)
    response = request(method = "GET", url = get_url, params = params, headers = headers)
    return response
