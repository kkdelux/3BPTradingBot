# 3BPTradingBot
Introductory Algorithmic Trading System using the Principles of Jared Wesley's 3 Bar Play Strategy


## 1. Pipeline for 15 minute 3BP
1. Load in top gainers
2. Scan for daily gap
3. Scan for 1st bar in 15 min timeframe
4. Scan for 2nd bar in 15 min timeframe
5. Determine entry point
6. Place order

## 2. Pipeline for 5 minute 3BP
1. If *1.3* or *1.4* fails, Scan for first bar in 5 min timeframe
2. Scan for 2nd bar in 5 min timeframe
3. Determine entry point
4. Place order
