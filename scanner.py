# Scanner.py
# Base class for a scanner that scans a list of stocks to determine relevant information based on criteria

import config as conf
from utilities import get_json_parsed_data_with_headers
import datetime
import time
import pytz
import pandas as pd

import sys

from discriminators import DailyGapDiscriminator, Min151stBarDiscriminator

class Scanner:
    """Base Scanner Class"""

    def __init__(self, tickers=[], data={}):
        self.tickers    = tickers
        self.data = data

    def scan(self):
        pass

    def set_tickers(self, tickers):
        self.tickers = tickers

    def set_data(self, data):
        self.data = data

class AlpacaPaperScanner(Scanner):
    """Base Alpaca paper api scanner class"""

    _API_KEY        = conf.ALPACA_PAPER_API_SECRET_KEY
    _API_KEY_ID     = conf.ALPACA_PAPER_API_KEY_ID
    _API_BASE_URL   = conf.ALPACA_BASE_DATA_URL

    def __init__(self, endpoint, timeframe, tickers=[], data={}):
        self._ENDPOINT  = endpoint
        self._TIMEFRAME = timeframe
        super().__init__(tickers, data)

class AlpacaPaperDailyGapScanner(AlpacaPaperScanner):
    """Scanner subclass for scanning daily bars of some set of tickers"""

    def __init__(self, endpoint, tickers=[], data={}):
        super().__init__(endpoint, "1D", tickers, data)

    def scan(self):
        # create url string and headers dict
        url = self._API_BASE_URL + self._ENDPOINT + self._TIMEFRAME + "?limit=100&symbols=" + ",".join(self.tickers)
        headers = {"APCA-API-KEY-ID": self._API_KEY_ID, "APCA-API-SECRET-KEY": self._API_KEY}

        print(url)

        # get request
        data = get_json_parsed_data_with_headers(url, headers)
        dfs = {}

        # create data frame for all tickers
        for ticker in self.tickers:
            ticker_lst = []
            for bar in data[ticker]:
                bar_copy = dict(bar)

                try:
                    bar_copy["t"] = time.strftime("%b %d %Y", time.gmtime(bar["t"]))
                except:
                    print(ticker, bar, bar["t"])
                    sys.exit()

                bar_copy["ticker"] = ticker
                bar_copy["bs"] = bar_copy["h"] - bar_copy["l"]

                ticker_lst.append(bar_copy)

            dfs[ticker] = {"df": pd.DataFrame(ticker_lst)}

        # process data frame to see if ticker has a gap
        daily_gap_discriminator = DailyGapDiscriminator(self.tickers, dfs)

        self.data = daily_gap_discriminator.run()

        return dfs


class AlpacaPaper15Min1stBarScanner(AlpacaPaperScanner):
    """Scanner subclass for scanning 15 min bars of some set of tickers"""

    def __init__(self, endpoint, tickers=[], data={}):
        super().__init__(endpoint, "15Min", tickers, data)

    def filter_tickers(self):
        tickers_swap = []
        for ticker in self.tickers:
            if self.data[ticker]["hasDailyGap"]:
                tickers_swap.append(ticker)

        self.tickers = tickers_swap

    def scan(self):
        until = datetime.datetime.today().strftime("%Y-%m-%d")

        # create url string and headers dict
        url = self._API_BASE_URL + self._ENDPOINT + self._TIMEFRAME + "?until="+ until +"T09:45:00-05:00&symbols=" + ",".join(self.tickers)
        headers = {"APCA-API-KEY-ID": self._API_KEY_ID, "APCA-API-SECRET-KEY": self._API_KEY}

        # print(url)

        # get request
        data = get_json_parsed_data_with_headers(url, headers)
        dfs = {}

        eastern = pytz.timezone('America/New_York')
        today = datetime.date.today()

        # create data frame for all tickers
        for ticker in self.tickers:
            ticker_lst = []
            for bar in data[ticker]:
                date = datetime.date.fromtimestamp(bar["t"])

                dt = datetime.datetime.fromtimestamp(bar["t"]).astimezone(eastern)
                market_open = datetime.datetime.today().astimezone(eastern).replace(hour=9, minute=29)

                if date == today and dt < market_open:
                    continue

                bar["t"] = dt.strftime("%b %d %Y %I:%M %Z")


                bar_copy = dict(bar)
                bar_copy["ticker"] = ticker
                bar_copy["bs"] = bar_copy["h"] - bar_copy["l"]

                ticker_lst.append(bar_copy)

            dfs[ticker] = {"df": pd.DataFrame(ticker_lst)}

        min15_1st_bar_discriminator = Min151stBarDiscriminator(self.tickers, dfs)

        self.data = min15_1st_bar_discriminator.run()

        return self.data
