# API.py
# Hold lists of api classes to use with application

import config as conf
import requests
import json

class BaseAPI:
    """Base API Class"""

    def __init__(self, base_url, endpoint):
        self._API_BASE_URL  = base_url
        self._ENDPOINT      = endpoint

    def request(self, method, headers, params):
        url = self._API_BASE_URL + self._ENDPOINT

        response = None
        if headers == None and params == None:
            response = requests.request(method, url)
        elif headers == None and params != None:
            response = requests.request(method, url, params=params)
        elif headers != None and params == None:
            response = requests.request(method, url, headers=headers)
        else:
            response = requests.request(method, url, headers=headers, params=params)

        return response

    def get(self, headers=None, params=None):
        return self.request("GET", headers, params)

    def request_json(self, method="GET", headers=None, params=None):
        print(self, method, headers, params)

        response = self.request(method, headers, params)
        return json.loads(response.text)

    def get_json(self, headers=None, params=None):
        return self.request_json("GET", headers, params)

class AlpacaAPI(BaseAPI):
    """Base Alpaca API Class"""

    def __init__(self, api_key_id, api_key, base_url, endpoint):
        self._API_KEY_ID    = api_key_id
        self._API_KEY       = api_key
        super().__init__(base_url, endpoint)

    def request(self, method, params):
        headers = {"APCA-API-KEY-ID": self._API_KEY_ID, "APCA-API-SECRET-KEY": self._API_KEY}
        url = self._API_BASE_URL + self._ENDPOINT

        response = requests.request(method, url, headers=headers, params=params)

        return response

    def get(self, params=None):
        return self.request("GET", params)

    def request_json(self, method="GET", params=None):
        response = self.request(method, params)
        return json.loads(response.text)

    def get_json(self, params=None):
        return self.request_json("GET", params)


class AlpacaPaperDataAPI(AlpacaAPI):
    """Base Alpaca Paper API Class"""

    def __init__(self, endpoint):
        super().__init__(conf.ALPACA_PAPER_API_KEY_ID, conf.ALPACA_PAPER_API_SECRET_KEY, conf.ALPACA_BASE_DATA_URL, endpoint)

class AlpacaPaperTradingAPI(AlpacaAPI):
    """Base Alpaca Paper API Class"""

    def __init__(self, endpoint):
        super().__init__(conf.ALPACA_PAPER_API_KEY_ID, conf.ALPACA_PAPER_API_SECRET_KEY, conf.ALPACA_PAPER_BASE_TRADING_URL, endpoint)

    def create_bracket_order(self, symbol, qty, entry, take, stop):
        headers = {"APCA-API-KEY-ID": self._API_KEY_ID, "APCA-API-SECRET-KEY": self._API_KEY}
        url = self._API_BASE_URL + self._ENDPOINT
        data = {
            "symbol": symbol,
            "qty": qty,
            "side": "buy",
            "type": "stop",
            "time_in_force": "day",
            "stop_price": entry,
            "order_class": "bracket",
            "take_profit": {
                "limit_price": take
            },
            "stop_loss": {
                "stop_price": stop
            }
        }

        response = requests.post(url, json=data, headers=headers)

        return json.loads(response.content)
