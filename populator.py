# Populator.py
# Base class for an object that populates a stock list based on a specific aggregator

from utilities import get_json_parsed_data, get_json_parsed_data_with_headers_and_params
import config as conf
import requests
import sys

class Populator:
    """Base Populator Class"""

    def __init__(self, endpoint, api_key):
        self._ENDPOINT = endpoint
        self._API_KEY = api_key
        self.tickers = []

    def populate(self):
        """
        Populate ``self.tickers`` with data from provided endpoint.
        Parameters
        ----------
        None
        Returns
        -------
        Populator
        """
        url = self._ENDPOINT + self._API_KEY
        # print(url)
        data = get_json_parsed_data(self._ENDPOINT + self._API_KEY)

        for entry in data["mostGainerStock"]:
            self.tickers.append(entry["ticker"])

        return self

    def get_tickers(self):
        """
        Getter for ``self.tickers``.
        Parameters
        ----------
        None
        Returns
        -------
        list
        """
        return self.tickers


class YahooPopulator(Populator):
    """Populator class for Yahoo Finance Top Gainers"""

    def __init__(self):
        super().__init__("https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/v2/get-movers", conf.YAHOO_RAPIDAPI_KEY)
        self._API_HOST = conf.YAHOO_RAPIDAPI_HOST

    def populate(self):

        url = self._ENDPOINT

        headers = {
        'x-rapidapi-key': self._API_KEY,
        'x-rapidapi-host': self._API_HOST
        }

        for i in range(10): # Change to higher number in production
            querydict = {"region":"US","lang":"en-US","start":str(i*6),"count":"6"}

            data = get_json_parsed_data_with_headers_and_params(url, querydict, headers)
            try:
                quotes = data["finance"]["result"][0]["quotes"]
            except:
                print(data)
                sys.exit()

            temp_tickers = []
            for quote in quotes:
                if "-" in quote["symbol"]:
                    continue
                if "." in quote["symbol"]:
                    continue
                if quote["fullExchangeName"] != "Other OTC":
                    self.tickers.append(quote["symbol"])

        return self

    def reset(self):

        self.tickers = []

        return self
