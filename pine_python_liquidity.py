import asyncio
import asyncio
import pandas as pd
import numpy as np
import talib
import ccxt
from loguru import logger as log

from retry import retry

# np.random.seed(0)
# ohlcv_data = np.random.rand(100, 4)

# Fetch OHLCV data from Binance
@retry(ccxt.NetworkError, tries=3, delay=2)
async def fetch_ohlcv(symbol, timeframe, limit=100):
    exchange = ccxt.binance() # Initialize the desired exchange class
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    return ohlcv

def calculate_liquidity_levels(ohlcv_df, marBuy, marSel, liqLen, liqMar, volume_threshold, use_volume):
    liquidity_levels_buy = []
    liquidity_levels_sell = []

    #get the ATR
    atr = talib.ATR(ohlcv_df['high'], ohlcv_df['low'], ohlcv_df['close'], timeperiod=14)

    for i in range(liqLen, len(ohlcv_df)):
        high_price = ohlcv_df['high'].iloc[i]
        low_price = ohlcv_df['low'].iloc[i]

        #get the pivot high and low
        pivot_high = ohlcv_df['high'].iloc[i - liqLen:i].max()
        pivot_low = ohlcv_df['low'].iloc[i - liqLen:i].min()

        # Calculate liquidity margin adjustment
        liquidity_margin = atr.iloc[i] / liqMar

        if use_volume:
            volume = ohlcv_df['volume'].iloc[i]

            if high_price > pivot_high + marBuy * liquidity_margin and volume > volume_threshold:
                liquidity_levels_buy.append((high_price, high_price + marBuy * liquidity_margin))

            if low_price < pivot_low - marSel * liquidity_margin and volume > volume_threshold:
                liquidity_levels_sell.append((low_price - marSel * liquidity_margin, low_price))

        else:
            if high_price > pivot_high + marBuy * liquidity_margin:
                liquidity_levels_buy.append((high_price, high_price + marBuy * liquidity_margin))

            if low_price < pivot_low - marSel * liquidity_margin:
                liquidity_levels_sell.append((low_price - marSel * liquidity_margin, low_price))

    return liquidity_levels_buy, liquidity_levels_sell

async def main():
    symbol = 'BTC/USDT'
    timeframe = '15m'
    limit = 1000
    marBuy = 2.3
    marSel = 2.3
    liqLen = 7
    liqMar = 10 / 6.9
    volume_threshold = 1000
    use_volume = False

    try:
        ohlcv = await fetch_ohlcv(symbol, timeframe, limit)
        ohlcv_df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])


        buyside_liquidity_levels, sellside_liquidity_levels = calculate_liquidity_levels(ohlcv_df, marBuy, marSel, liqLen, liqMar, volume_threshold, use_volume)

        print(buyside_liquidity_levels, sellside_liquidity_levels)


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

        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        print(df)
        print('\n')

        return df

    except ccxt.NetworkError as e:
        print("Network error: Request timed out after multiple retries.", e)



if __name__ == "__main__":
    while True:
        asyncio.run(main())

