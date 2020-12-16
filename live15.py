# Live.py
# Main application file for running application in cloud on 15 min 3BP timeframe

# imports
import pytz
import datetime

from api import AlpacaPaperDataAPI, AlpacaPaperTradingAPI
# setup

## APIs

# Alpaca
daily_bars_api = AlpacaPaperDataAPI("/v1/bars/1D")
min15_bars_api = AlpacaPaperDataAPI("/v1/bars/15Min")
calendar_api = AlpacaPaperTradingAPI("/v2/calendar")

eastern = pytz.timezone('America/New_York')
today = datetime.datetime.today().astimezone(eastern)

currenttime = datetime.datetime.now().astimezone(eastern)
prevtime = datetime.datetime.now().astimezone(eastern)
# main loop
while (True):
    # update current time
    currenttime = datetime.datetime.now().astimezone(eastern)

    # determine if it is a new day
    if currenttime.day != prevtime.day:
        # new day
        today = datetime.datetime.today().astimezone(eastern)

    # determine if the market is open today
    calendar_dt = today.strftime("%Y-%m-%d")
    is_open = calendar_api.get_json({"start": calendar_dt, "end": calendar_dt})[0]["date"] == calendar_dt

    if is_open:
        # if time is >= 9:30 AM New York time, collect premarket top gainers

        # if time is >= 9:45 AM New York time, collect first 15 min bar from premarket top gainers
        # determine if any of the premarket gainers have a good first bar

        # if time is >= 10:00 AM New York time, collect second 15 min bar from premarket top gainers
        # determine if any of the premarket gainers with a good first bar, have a good second bar

        # if any have a good second bar, determine entry point

        # place orders
