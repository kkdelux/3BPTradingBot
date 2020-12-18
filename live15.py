# Live.py
# Main application file for running application in cloud on 15 min 3BP timeframe

import sys
# imports
import pytz
import datetime

import discriminators as ds
from api import AlpacaPaperDataAPI, AlpacaPaperTradingAPI
from populator import YahooPopulator

# setup

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
    "00:00": datetime.datetime.today().astimezone(eastern). replace(hour=0, minute=0, second=0, microsecond=0),
    "9:30": datetime.datetime.today().astimezone(eastern).replace(hour=9, minute=30, second=0, microsecond=0),
    "9:45": datetime.datetime.today().astimezone(eastern).replace(hour=9, minute=45, second=0, microsecond=0),
    "10:00": datetime.datetime.today().astimezone(eastern). replace(hour=10, minute=0, second=0, microsecond=0)
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

# Traded for the day?
traded = False
check_930 = False
check_945 = False
check_1000 = False
# main loop
# print(daily_bars_api.get_json({"symbols": ",".join(["AAPL", "TSLA"])}))
while (True):
    # update current time
    currenttime = datetime.datetime.now().astimezone(eastern)

    # determine if it is a new day
    if currenttime.day != prevtime.day:
        # new day
        today = datetime.datetime.today().astimezone(eastern)

        # update times
        times["00:00"] = datetime.datetime.today().astimezone(eastern). replace(hour=0, minute=0, second=0, microsecond=0)
        times["9:30"] = datetime.datetime.today().astimezone(eastern).replace(hour=9, minute=30, second=0, microsecond=0)
        times["9:45"] = datetime.datetime.today().astimezone(eastern).replace(hour=9, minute=45, second=0, microsecond=0)
        times["10:00"] = datetime.datetime.today().astimezone(eastern). replace(hour=10, minute=0, second=0, microsecond=0)

        # updated traded for the day
        traded = False
        # updated time checks for the day
        check_930 = False
        check_945 = False
        check_1000 = False

    # determine if the market is open today
    calendar_dt = today.strftime("%Y-%m-%d")
    is_open = calendar_api.get_json({"start": calendar_dt, "end": calendar_dt})[0]["date"] == calendar_dt

    if is_open and not traded:
        # if time is >= 9:30 AM New York time, collect premarket top gainers
        if currenttime >= times["9:30"] and currenttime < times["9:45"] and not check_930:
            print("Current Time greater than 9:30")
            # collect premarket top gainers
            tickers["Pre"] = populator.populate().get_tickers()

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

            check_930 = True


        # if time is >= 9:45 AM New York time, collect first 15 min bar from premarket top gainers
        # determine if any of the premarket gainers have a good first bar
        if currenttime >= times["9:45"] and currenttime < times["10:00"] and not check_945:
            print("Current Time greater than 9:45")
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
                            bars_swap.append(bar)

                    bars["1st"][ticker] = pd.DataFrame(bars_swap)
                    bars["1st"][ticker]["bs"] = bars["1st"][ticker]["h"] - bars["1st"][ticker]["l"]

                # determine if ticker has good first bar
                for ticker in tickers["1st"]:
                    if ds.has_good_1st_bar(bars["1st"][ticker]):
                        tickers["2nd"].append(ticker)

            check_945 = True

        # if time is >= 10:00 AM New York time, collect second 15 min bar from premarket top gainers
        # determine if any of the premarket gainers with a good first bar, have a good second bar
        if currenttime >= times["10:00"]:
            print("Current time greater than 10:00")
            sys.exit()
            # determine if tickers with good first bar have good second bar

            # get second bar
            # check to see if second bar is good
            for ticker in tickers["2nd"]:
                if ds.has_good_2nd_bar(bars["2nd"][ticker]):
                    # populate tickers["Ord"]
                    tickers["Ord"].append(ticker)

            check_1000 = True

        # if any have a good second bar, determine entry point
        if tickers["Ord"]:
            for ticker in tickers["Ord"]:
                # get balance
                balance = float(account_api.get_json()["cash"])
                # determine entry point
                high = bars["2nd"][ticker]["h"].tail(2).max()
                high_100 = int(high * 100)
                entry = (high_100 + (5 - (high_100 % 5))) / 100
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
                        "take"      : str(round(take, 2)),
                        "stop"      : str(round(stop, 2))
                    }
                    # place order
                    orders_api.create_bracket_order(order["symbol"], order["qty"], order["entry"], order["take"], order["stop"])

                    orders.append(order)

        # update traded
        traded = True

        # clear data structures
        tickers["Pre"] = tickers["Pre"].clear()
        tickers["1st"] = tickers["1st"].clear()
        tickers["2nd"] = tickers["2nd"].clear()
        tickers["Ord"] = tickers["Ord"].clear()

        bars["Pre"] = bars["Pre"].clear()
        bars["1st"] = bars["1st"].clear()
        bars["2nd"] = bars["2nd"].clear()

        orders.clear()
