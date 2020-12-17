# Discriminators to be used to determine if a stocks bars have a specific quality

def has_gap(bars_df):
    mean_high   = bars_df["h"][:-1].mean()
    std_high    = bars_df["h"][:-1].std()

    if bars_df["h"].iloc[-1] - mean_high > 1.25 * std_high:
        return True
    return False

def has_igniting_bar(bars_df):
    # use donchian channel until pivots are necessary
    donchian_high = bars_df["h"].tail(41)[:-1].max()
    donchian_low = bars_df["l"].tail(41)[:-1].min()
    donchian_gap = donchian_high - donchian_low

    if bars_df["h"].iloc[-1] > donchian_high + (donchian_channel_size * 0.5):
        return True
    return False

def has_wide_bar(bars_df):
    mean_bar_size = bars_df["bs"][:-1].mean()

    if bars_df["bs"].iloc[-1] > 2 * mean_bar_size:
        return True
    return False

def has_increased_volume(bars_df):
    mean_volume = bars_df["v"][:-1].mean()
    std_volume = bars_df["v"][:-1].std()

    if bars_df["v"].iloc[-1] - mean_volume > 1.5 * std_volume:
        return True
    return False

def has_positive_move(bars_df):
    if bars_df["c"].iloc[-1] > bars_df["o"].iloc[-1]:
        return True
    return False

def has_good_1st_bar(bars_df):
    if has_igniting_bar(bars_df) and has_wide_bar(bars_df) and has_increased_volume(bars_df) and has_positive_move(bars_df):
        return True
    return False
