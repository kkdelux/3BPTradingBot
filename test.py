# Unit testing for proper 3BPs base on sample 3BPs found in the wild

# imports
import unittest
import pytz
import datetime
import pandas as pd

import discriminators as ds
from api import AlpacaPaperDataAPI, AlpacaPaperTradingAPI

# Test on a solid 15 min 3BP -- CYBR on 12-18-2020 at Market Open
class CYBR_12_18_2020_Open(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Get time zone
        cls.eastern = pytz.timezone('America/New_York')
        cls.example_dt_945 = datetime.datetime.today().astimezone(cls.eastern).replace(
            year=2020, month=12, day=18, hour=9, minute=45, second=0, microsecond=0
        )
        cls.example_dt_1000 = datetime.datetime.today().astimezone(cls.eastern).replace(
            year=2020, month=12, day=18, hour=10, minute=0, second=0, microsecond=0
        )

        cls.example_next_day_dt = datetime.datetime.today().astimezone(cls.eastern).replace(
            year=2020, month=12, day=19, hour=0, minute=0, second=0, microsecond=0
        )

        cls.daily_bars_api  = AlpacaPaperDataAPI("/v1/bars/1D")
        cls.min15_bars_api  = AlpacaPaperDataAPI("/v1/bars/15Min")

        cls.dt_string_945 = cls.example_dt_945.strftime("%Y-%m-%dT%H:%M:%S-05:00")
        cls.dt_string_1000 = cls.example_dt_1000.strftime("%Y-%m-%dT%H:%M:%S-05:00")
        cls.next_day_dt_string = cls.example_next_day_dt.strftime("%Y-%m-%dT%H:%M:%S-05:00")

        cls.daily_bars = pd.DataFrame(cls.daily_bars_api.get_json({"symbols": "CYBR", "until": cls.next_day_dt_string})["CYBR"])

        # collect data for the first bar
        raw_data = cls.min15_bars_api.get_json({"symbols": "CYBR", "until": cls.dt_string_945})["CYBR"]
        bars_swap = []
        for bar in raw_data:
            dt = datetime.datetime.fromtimestamp(bar["t"]).astimezone(cls.eastern)

            if dt >= datetime.datetime.strptime("2020-12-18T00:00:00-05:00", "%Y-%m-%dT%H:%M:%S%z") and dt < datetime.datetime.strptime("2020-12-18T09:30:00-05:00", "%Y-%m-%dT%H:%M:%S%z"):
                continue
            bars_swap.append(bar)

        cls.first_bar_bars = pd.DataFrame(bars_swap)
        cls.first_bar_bars["bs"] = cls.first_bar_bars["h"] - cls.first_bar_bars["l"]

        # collect data for the second bar
        raw_data = cls.min15_bars_api.get_json({"symbols": "CYBR", "until": cls.dt_string_1000})["CYBR"]
        bars_swap = []
        for bar in raw_data:
            dt = datetime.datetime.fromtimestamp(bar["t"]).astimezone(cls.eastern)

            if dt >= datetime.datetime.strptime("2020-12-18T00:00:00-05:00", "%Y-%m-%dT%H:%M:%S%z") and dt < datetime.datetime.strptime("2020-12-18T09:30:00-05:00", "%Y-%m-%dT%H:%M:%S%z"):
                continue
            bars_swap.append(bar)
        cls.second_bar_bars = pd.DataFrame(bars_swap)
        cls.second_bar_bars["bs"] = cls.second_bar_bars["h"] - cls.second_bar_bars["l"]

    def test_daily_bars(self):
        self.assertTrue(not self.daily_bars.empty)

    def test_first_bar_bars(self):
        self.assertTrue(not self.first_bar_bars.empty)

    def test_second_bar_bars(self):
        self.assertTrue(not self.second_bar_bars.empty)

    def test_daily_gap(self):
        self.assertTrue(ds.has_gap(self.daily_bars))

    def test_good_first_bar(self):
        self.assertTrue(ds.has_igniting_bar(self.first_bar_bars))
        self.assertTrue(ds.has_wide_bar(self.first_bar_bars))
        self.assertTrue(ds.has_increased_volume(self.first_bar_bars))
        self.assertTrue(ds.has_positive_move(self.first_bar_bars))
        self.assertTrue(ds.has_good_1st_bar(self.first_bar_bars))

    def test_good_second_bar(self):
        self.assertTrue(ds.has_upper_50(self.second_bar_bars))
        self.assertTrue(ds.has_realtive_high(self.second_bar_bars))
        self.assertTrue(ds.has_good_2nd_bar(self.second_bar_bars))
