from requests import request, Response


def get_request(get_url: str, params: dict) -> Response:
    headers = {
        "Content-Type" : "application/x-www-form-urlencoded;charset=utf-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    }
    response = request(method = "GET", url = get_url, params = params, headers = headers)
    return response
