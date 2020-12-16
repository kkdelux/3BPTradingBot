# Application Entry Point

#imports
from populator import Populator
from scanner import AlpacaPaperDailyGapScanner, AlpacaPaper15Min1stBarScanner
import config as conf
#setup
fmp_gainers_populator = Populator("https://financialmodelingprep.com/api/v3/stock/gainers?apikey=", conf.FMP_API_SECRET_KEY)
alpaca_daily_gap_scanner = AlpacaPaperDailyGapScanner("/v1/bars/")
alpaca_15min_1st_bar_scanner = AlpacaPaper15Min1stBarScanner("/v1/bars/")

#run
tickers = fmp_gainers_populator.populate().get_tickers()
# print(tickers)

print("-----------------------------------------")
alpaca_daily_gap_scanner.set_tickers(tickers)
alpaca_daily_gap_scanner.scan()
print("-----------------------------------------")
alpaca_15min_1st_bar_scanner.set_tickers(alpaca_daily_gap_scanner.tickers)
alpaca_15min_1st_bar_scanner.set_data(alpaca_daily_gap_scanner.data)
alpaca_15min_1st_bar_scanner.filter_tickers()
data = alpaca_15min_1st_bar_scanner.scan()
print("-----------------------------------------")
for ticker in data.keys():
    if data[ticker]["has15Min1stBar"]:
        print(ticker)
