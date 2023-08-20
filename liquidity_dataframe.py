import pandas as pd
from datetime import datetime, timedelta
import ccxt
import pandas as pd
from retry import retry
import asyncio
import matplotlib.pyplot as plt
from loguru import logger as log

# Fetch OHLCV data from Binance
@retry(ccxt.NetworkError, tries=3, delay=2)
async def fetch_ohlcv(symbol, timeframe, limit=100):
    exchange = ccxt.binance() # Initialize the desired exchange class
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    return ohlcv

# Calculate liquidity levels with volume threshold
def calculate_liquidity_levels(ohlcv_df, marBuy, marSel, liqLen, liqMar, volume_threshold, use_volume):
    liquidity_levels_buy = []
    liquidity_levels_sell = []

    if use_volume:
        log.debug("Hey volume threshold condition Activated !\nMake sure you adjust to suit your Requirement set use_volume to False if only want to use Ma")
    else:
        log.debug(
            "Hey Moving Averages condition Activated !\nMake sure you adjust to suit your Requirement check example below and to use volume threshold set  use_volume to True")

    for i in range(liqLen, len(ohlcv_df)):
        high_price = ohlcv_df['high'].iloc[i]
        low_price = ohlcv_df['low'].iloc[i]

        # Calculate the moving average for the past liqLen days
        ma_buy = ohlcv_df['close'].iloc[i - liqLen:i].max() + marBuy * liqMar
        ma_sell = ohlcv_df['close'].iloc[i - liqLen:i].min() - marSel * liqMar

        # Adjust the moving average parameters here if needed
        # Example: ma_buy = ohlcv_df['close'].iloc[i - liqLen:i].mean() + marBuy * liqMar

        if use_volume:
            volume = ohlcv_df['volume'].iloc[i]


            if high_price > ma_buy and volume > volume_threshold:
                liquidity_levels_buy.append((high_price, high_price + marBuy * liqMar))

            if low_price < ma_sell and volume > volume_threshold:
                liquidity_levels_sell.append((low_price - marSel * liqMar, low_price))

        else:
            if high_price > ma_buy:
                liquidity_levels_buy.append((high_price, high_price + marBuy * liqMar))

            if low_price < ma_sell:
                liquidity_levels_sell.append((low_price - marSel * liqMar, low_price))

    return liquidity_levels_buy, liquidity_levels_sell



async def main():
    symbol = 'BTC/USDT'
    timeframe = '15m'
    limit = 100
    marBuy = 2.3
    marSel = 2.3
    liqLen = 7
    liqMar = 10 / 6.9  # You can replace this value with the desired calculation
    volume_threshold = 1000  # Set your desired volume threshold here
    use_volume = True


    try:
        ohlcv = await fetch_ohlcv(symbol, timeframe, limit)
        ohlcv_df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

        buyside_liquidity_levels, sellside_liquidity_levels = calculate_liquidity_levels(ohlcv_df, marBuy, marSel, liqLen, liqMar, volume_threshold, use_volume)

        

        df = pd.DataFrame(columns=['Timestamp', 'Buyside_Level_Start', 'Buyside_Level_Break', 'Sellside_Level_Start',
                                   'Sellside_Level_Break'])

        timestamp = pd.Timestamp.now()

        liquidity_data = []

        for start, break_level in buyside_liquidity_levels:
            liquidity_data.append({'Timestamp': timestamp,
                                   'Buyside_Level_Start': start,
                                   'Buyside_Level_Break': break_level,
                                   'Sellside_Level_Start': None,
                                   'Sellside_Level_Break': None})

        for start, break_level in sellside_liquidity_levels:
            liquidity_data.append({'Timestamp': timestamp,
                                   'Buyside_Level_Start': None,
                                   'Buyside_Level_Break': None,
                                   'Sellside_Level_Start': start,
                                   'Sellside_Level_Break': break_level})

        df = pd.DataFrame(liquidity_data)

        print(df)
        print('\n')

        return df

    except ccxt.NetworkError as e:
        print("Network error: Request timed out after multiple retries.", e)

if __name__ == "__main__":
    while True:
        asyncio.run(main())
