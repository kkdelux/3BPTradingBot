# Discriminators to be used with scanners to filter out stocks

import sys

class Discriminator:
    """Base Discriminator Class"""

    def __init__(self, title, tickers, dataframes):
        self.title = title
        self.tickers = tickers
        self.dfs = dataframes

    def run(self):
        pass

class DailyGapDiscriminator(Discriminator):
    """Discriminator to determine if stock has a wide daily gap"""

    def __init__(self, tickers, dataframes):
        super().__init__("hasDailyGap", tickers, dataframes)

    def run(self):
        for ticker in self.tickers:
            try:
                mean_high = self.dfs[ticker]["df"]["h"][:-1].mean()
            except:
                print(ticker, self.dfs[ticker])
                sys.exit()
            standard_deviation = self.dfs[ticker]["df"]["h"][:-1].std()

            # determine if price is abnormally high
            if self.dfs[ticker]["df"]["h"].iloc[-1] - mean_high > 1.25 * standard_deviation:
                self.dfs[ticker][self.title] = True
            else:
                self.dfs[ticker][self.title] = False

        return self.dfs

class Min151stBarDiscriminator(Discriminator):
    """Discriminator to determine if stock has a first igniting bar"""

    def __init__(self, tickers, dataframes):
        super().__init__("has15Min1stBar", tickers, dataframes)

    def run(self):
        for ticker in self.tickers:
            mean_bar_size = self.dfs[ticker]["df"]["bs"][:-1].mean()
            std_bar_size = self.dfs[ticker]["df"]["bs"][:-1].std()

            mean_volume = self.dfs[ticker]["df"]["v"][:-1].mean()
            std_volume = self.dfs[ticker]["df"]["v"][:-1].std()

            last_bar = self.dfs[ticker]["df"].iloc[-1]

            # use Donchian Channel n=20 to find decent resistance
            donchian_high = self.dfs[ticker]["df"]["h"].tail(41)[:-1].max()
            donchian_low = self.dfs[ticker]["df"]["l"].tail(41)[:-1].min()
            donchian_channel_size = donchian_high - donchian_low

            # print(ticker+":")
            # print("Channel Size", donchian_channel_size, "High", donchian_high, "Low", donchian_low)
            # print("Bar Size", self.dfs[ticker]["df"]["bs"].iloc[-1])

            # 3 step process to determine if bar is a proper 1st bar
            # 1. First bar of move
            first_bar = False
            # 2. Wide range bar (abnormally large)
            wr_bar = False
            # 3. Increased volume
            inc_volume = False
            # 4. (extra) should be bullish direction since not shorting
            positive = False

            # determine if first bar of move
            # move happens in 2 ways
            # a. moves above the resistance
            if last_bar['h'] > donchian_high + (donchian_channel_size * 0.5):
                first_bar = True
            # b. turns a pivot

            # determine if bar size is abnormally large
            if self.dfs[ticker]["df"]["bs"].iloc[-1] > 2 * mean_bar_size:
                wr_bar = True

            # determine if bar has increased volume
            if last_bar["v"] - mean_volume > 1.5 * std_volume:
                inc_volume = True

            # determine if bar is positive
            if last_bar["c"] > last_bar["o"]:
                positive = True

            if first_bar and wr_bar and inc_volume and positive:
                self.dfs[ticker][self.title] = True
            else:
                self.dfs[ticker][self.title] = False


        return self.dfs
