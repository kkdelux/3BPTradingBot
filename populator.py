# Populator.py
# Base class for an object that populates a stock list based on a specific aggregator

from utilities import get_json_parsed_data

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
