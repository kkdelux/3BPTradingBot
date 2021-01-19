# Live.py
# Main application file for running application in cloud on 15 min 3BP timeframe
# With a small change from original file in that we are checking top gainers at 9:45
# instead of market open to try to identify symbols with good first bars at a higher rate

import sys
# imports
import logging
logging.basicConfig(filename='live15.log', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %H:%M:%S %z', level=logging.DEBUG)

import time
import pytz
import datetime

import pandas as pd

import discriminators as ds
from api import AlpacaPaperDataAPI, AlpacaPaperTradingAPI
from populator import YahooPopulator

# setup
logging.info("Starting Live Trading Application at " + __file__)

## APIs

# Alpaca
daily_bars_api  = AlpacaPaperDataAPI("/v1/bars/1D")
min15_bars_api  = AlpacaPaperDataAPI("/v1/bars/15Min")
calendar_api    = AlpacaPaperTradingAPI("/v2/calendar")
orders_api      = AlpacaPaperTradingAPI("/v2/orders")
account_api     = AlpacaPaperTradingAPI("/v2/account")

# Populator
populator = YahooPopulator()

## Globals
# Risk/Reward
rr = 2 # for every 1 risk try for 2 reward
# Size of each order compared to account balance
order_size = 0.05 # Order should be 5% of remaining account balance

# Times
eastern = pytz.timezone('America/New_York')
today = datetime.datetime.today().astimezone(eastern)
times = {
    "00:00": datetime.datetime.today().astimezone(eastern).replace(hour=0, minute=0, second=0, microsecond=0),
    "9:30": datetime.datetime.today().astimezone(eastern).replace(hour=9, minute=30, second=0, microsecond=0),
    "9:45": datetime.datetime.today().astimezone(eastern).replace(hour=9, minute=45, second=0, microsecond=0),
    "10:00": datetime.datetime.today().astimezone(eastern).replace(hour=10, minute=0, second=0, microsecond=0)
}

currenttime = datetime.datetime.now().astimezone(eastern)
prevtime = datetime.datetime.now().astimezone(eastern)

# Tickers data structure
tickers = {
    "Pre": [],      # Premarket top tickers
    "1st": [],      # Tickers that have a gap
    "2nd": [],      # Tickers that have a good first bar
    "Ord": []       # Tickers that have a good second bar
}

# Bars data structure
# each entry has the form
# bars["XXX"] = {
#     "YYYY"  : DataFrame of bars,
#     "ZZZZ"  : DataFrame of bars,
#     ...
# }
bars = {
    "Pre": {},      # bars dataframe for each ticker in premarket
    "1st": {},      # bars dataframe for each ticker that attempts first bar check
    "2nd": {}       # bars dataframe for each ticker that attempts second bar check
}

# Order data structure
# Holds array of tickers and entry points
# entrys in array should have the form
# {
#     "symbol"    : "XXXX",
#     "qty"       :  number,
#     "entry"     : "number string",
#     "take"      : "number string"
#     "stop"      : "number string",
# }
orders = []

# is market open today
calendar_dt = today.strftime("%Y-%m-%d")
is_open = calendar_api.get_json({"start": calendar_dt, "end": calendar_dt})[0]["date"] == calendar_dt

# Traded for the day?
traded = False
check_930 = False
check_945 = False
check_1000 = False
ordered = False
# main loop
logging.info("DateTime Event -- Today is: " + today.strftime("%Y-%m-%d") + " Market is: " + ("Open" if is_open else "Closed"))
logging.info("DateTime Event -- 9:30 is at: " + times["9:30"].strftime("%Y %m %d %H:%M:%S %z"))

while (True):
    # update current time
    currenttime = datetime.datetime.now().astimezone(eastern)

    # determine if it is a new day
    if currenttime.day != prevtime.day:
        # new day
        today = datetime.datetime.today().astimezone(eastern)


        # update times
        times["00:00"] = datetime.datetime.today().astimezone(eastern).replace(hour=0, minute=0, second=0, microsecond=0)
        times["9:30"] = datetime.datetime.today().astimezone(eastern).replace(hour=9, minute=30, second=0, microsecond=0)
        times["9:45"] = datetime.datetime.today().astimezone(eastern).replace(hour=9, minute=45, second=0, microsecond=0)
        times["10:00"] = datetime.datetime.today().astimezone(eastern).replace(hour=10, minute=0, second=0, microsecond=0)

        # updated traded for the day
        traded = False
        # updated time checks for the day
        check_930 = False
        check_945 = False
        check_1000 = False
        ordered = False

        # determine if the market is open today
        calendar_dt = today.strftime("%Y-%m-%d")
        is_open = calendar_api.get_json({"start": calendar_dt, "end": calendar_dt})[0]["date"] == calendar_dt

        logging.info("DateTime Event -- Today is: " + today.strftime("%Y-%m-%d") + " Market is: " + ("Open" if is_open else "Closed"))

    if is_open and not traded:
        # if time is >= 9:30 AM New York time, collect premarket top gainers
        if (currenttime >= times["9:45"]) and (currenttime < times["10:00"]) and (not check_930):
            logging.debug("DateTime Event -- Getting Daily Gainers")
            # collect premarket top gainers
            tickers["Pre"] = populator.populate().get_tickers()
            populator.reset()

            logging.info("Intraday Event -- Found " + str(len(tickers["Pre"])) + " pre-market gainers")
            print("Premarket Tickers:")
            print(tickers["Pre"])

            # scan for gaps
            raw_data = daily_bars_api.get_json({"symbols": ",".join(tickers["Pre"])})

            for ticker in tickers["Pre"]:
                # convert bars to a data frame
                bars["Pre"][ticker] = pd.DataFrame(raw_data[ticker])

            for ticker in tickers["Pre"]:
                # check if bar has a gap
                if ds.has_gap(bars["Pre"][ticker]):
                    # if gap append to tickers["1st"] for the next check
                    tickers["1st"].append(ticker)

            logging.info("Intraday Event -- Found " + str(len(tickers["1st"])) + " pre-market gainers with gaps")

            tickers["Pre"] = []
            bars["Pre"] = []

            check_930 = True


        # if time is >= 9:45 AM New York time, collect first 15 min bar from premarket top gainers
        # determine if any of the premarket gainers have a good first bar
        if currenttime >= times["9:45"] and currenttime < times["10:00"] and (not check_945) and check_930:
            logging.debug("DateTime Event -- Processing Symbols with good gaps")
            # determine if any of the premarket tickers have a good first bar
            if tickers["1st"]:
                # collect 15 min bars
                raw_data = min15_bars_api.get_json({"symbols": ",".join(tickers["1st"])})

                for ticker in tickers["1st"]:
                    bars_swap = []
                    for bar in raw_data[ticker]:
                        dt = datetime.datetime.fromtimestamp(bar["t"]).astimezone(eastern)
                        # remove premarket bars
                        if dt >= times["00:00"] and dt < times["9:30"]:
                            continue
                        bars_swap.append(bar)

                    bars["1st"][ticker] = pd.DataFrame(bars_swap)
                    bars["1st"][ticker]["bs"] = bars["1st"][ticker]["h"] - bars["1st"][ticker]["l"]

                # determine if ticker has good first bar
                for ticker in tickers["1st"]:
                    if ds.has_good_1st_bar(bars["1st"][ticker]):
                        tickers["2nd"].append(ticker)

                logging.info("Intraday Event -- Found " + str(len(tickers["2nd"])) + " symbols with a good 1st bar")

            tickers["1st"] = []
            bars["1st"] = []

            check_945 = True

        # if time is >= 10:00 AM New York time, collect second 15 min bar from premarket top gainers
        # determine if any of the premarket gainers with a good first bar, have a good second bar
        if currenttime >= times["10:00"] and (not check_1000) and check_945:
            logging.debug("DateTime Event -- Processing Symbols with a good first bar")
            # determine if tickers with good first bar have good second bar
            if tickers["2nd"]:
                # collect second 15 min bar
                raw_data = min15_bars_api.get_json({"symbols": ",".join(tickers["2nd"])})

                for ticker in tickers["2nd"]:
                    bars_swap = []
                    for bar in raw_data[ticker]:
                        dt = datetime.datetime.fromtimestamp(bar["t"]).astimezone(eastern)
                        # remove premarket bars
                        if dt >= times["00:00"] and dt < times["9:30"]:
                            continue
                        bars_swap.append(bar)

                    bars["2nd"][ticker] = pd.DataFrame(bars_swap)
                    bars["2nd"][ticker]["bs"] = bars["2nd"][ticker]["h"] - bars["2nd"][ticker]["l"]

                # check to see if second bar is good
                for ticker in tickers["2nd"]:
                    if ds.has_good_2nd_bar(bars["2nd"][ticker]):
                        # populate tickers["Ord"]
                        tickers["Ord"].append(ticker)

                logging.info("Intraday Event -- Found " + str(len(tickers["Ord"])) + " symbols with a good 2nd bar")

            tickers["2nd"] = []

            check_1000 = True

        # if any have a good second bar, determine entry point
        if tickers["Ord"]:
            logging.debug("DateTime Event -- Processing Symbols with a good second bar")
            for ticker in tickers["Ord"]:
                # get balance
                balance = float(account_api.get_json()["cash"])
                # determine entry point
                entry = bars["2nd"][ticker]["h"].tail(2).max()
                # high_100 = int(high * 100)
                # entry = (high_100 + (5 - (high_100 % 5))) / 100
                # determine stop
                stop = bars["2nd"][ticker]["l"].iloc[-1]
                # determine take profit
                take = entry + (rr * (entry - stop))
                # determine quantity
                qty = int((balance * order_size) / entry)

                if qty > 1:
                    order = {
                        "symbol"    : ticker,
                        "qty"       : qty,
                        "entry"     : str(round(entry, 2)),
                        "limit"     : str(round(entry*1.01, 2)),
                        "take"      : str(round(take, 2)),
                        "stop"      : str(round(stop, 2))
                    }
                    # place order
                    orders_api.create_bracket_order(order["symbol"], order["qty"], order["entry"], order["limit"], order["take"], order["stop"])

                    logging.info("Intraday Event -- Order placed for " + order["symbol"] + " x" + str(order["qty"]))

                    orders.append(order)

            tickers["Ord"] = []
            bars["2nd"] = []

            ordered = True

        # update traded
        if check_930 and check_945 and check_1000 and ordered:
            traded = True
            orders = []

        if check_930:
            bars["Pre"] = {}
        if check_945:
            bars["1st"] = {}
        if check_1000 and ordered:
            bars["2nd"] = {}


    # update prev time
    prevtime = currenttime
