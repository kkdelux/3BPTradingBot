# Application Entry Point

#imports
from populator import Populator, YahooPopulator
from scanner import AlpacaPaperDailyGapScanner, AlpacaPaper15Min1stBarScanner
import config as conf
from utilities import get_json_parsed_data_with_headers
#setup
fmp_gainers_populator = Populator("https://financialmodelingprep.com/api/v3/stock/gainers?apikey=", conf.FMP_API_SECRET_KEY)
yahoo_gainers_populator = YahooPopulator()
alpaca_daily_gap_scanner = AlpacaPaperDailyGapScanner("/v1/bars/")
alpaca_15min_1st_bar_scanner = AlpacaPaper15Min1stBarScanner("/v1/bars/")

#run
# print(get_json_parsed_data_with_headers(conf.ALPACA_BASE_DATA_URL + "/v1/bars/" + "1D" + "?limit=100&symbols=ARGGY", {"APCA-API-KEY-ID": conf.ALPACA_PAPER_API_KEY_ID, "APCA-API-SECRET-KEY": conf.ALPACA_PAPER_API_SECRET_KEY}))
tickers = fmp_gainers_populator.populate().get_tickers()
tickers = yahoo_gainers_populator.populate().get_tickers()
print(len(tickers), tickers)
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
