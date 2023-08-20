import pandas as pd

from datetime import datetime, timedelta
import ccxt
import pandas as pd
from retry import retry
import asyncio
import matplotlib.pyplot as plt
# Fetch OHLCV data from Binance
@retry(ccxt.NetworkError, tries=3, delay=2)
async def fetch_ohlcv(symbol, timeframe, limit=100):
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    return ohlcv





# Calculate liquidity levels
def calculate_liquidity_levels(ohlcv_df, marBuy, marSel, liqLen, liqMar):
    liquidity_levels_buy = []
    liquidity_levels_sell = []

    for i in range(liqLen, len(ohlcv_df)):
        high_price = ohlcv_df['high'].iloc[i]
        low_price = ohlcv_df['low'].iloc[i]

        if high_price > ohlcv_df['close'].iloc[i - liqLen:i].max() + marBuy * liqMar:
            liquidity_levels_buy.append((high_price, high_price + marBuy * liqMar))  # Changed this line

        if low_price < ohlcv_df['close'].iloc[i - liqLen:i].min() - marSel * liqMar:
            liquidity_levels_sell.append((low_price - marSel * liqMar, low_price))  # Changed this line

    return liquidity_levels_buy, liquidity_levels_sell


async def main():
    symbol = 'BTC/USDT'
    timeframe = '5m'
    limit = 100
    marBuy = 2.3
    marSel = 2.3
    liqLen = 7
    liqMar = 10 / 6.9  # You can replace this value with the desired calculation

    try:
        ohlcv = await fetch_ohlcv(symbol, timeframe, limit)
        ohlcv_df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

        buyside_liquidity_levels, sellside_liquidity_levels = calculate_liquidity_levels(ohlcv_df, marBuy, marSel, liqLen, liqMar)


        # Rest of your code for processing and printing the liquidity levels

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
        print('\n\n')

        return df


    except ccxt.NetworkError as e:
        print("Network error: Request timed out after multiple retries.", e)

# ... (your code for fetching and calculating liquidity levels)

async def update_plot():
    historical_data = pd.DataFrame(columns=['Timestamp', 'Buyside_Level_Start', 'Buyside_Level_Break',
                                            'Sellside_Level_Start', 'Sellside_Level_Break'])

    plt.ion()  # Turn on interactive mode for continuous updating


    while True:
        df = await main()  # Get the returned DataFrame from main()

        # Append new data to historical_data
        historical_data = pd.concat([historical_data, df])

        # Filter data within the current year
        current_year = datetime.now().year
        historical_data = historical_data[historical_data['Timestamp'].dt.year == current_year]

        # Clear the previous plot and create a new one
        plt.clf()

        # Plotting the liquidity levels
        plt.plot(historical_data['Timestamp'], historical_data['Buyside_Level_Start'], 'go', label='Buyside Start')
        plt.plot(historical_data['Timestamp'], historical_data['Buyside_Level_Break'], 'ro', label='Buyside Break')
        plt.plot(historical_data['Timestamp'], historical_data['Sellside_Level_Start'], 'bo', label='Sellside Start')
        plt.plot(historical_data['Timestamp'], historical_data['Sellside_Level_Break'], 'mo', label='Sellside Break')
        plt.xlabel('Timestamp')
        plt.ylabel('Price')
        plt.title('Liquidity Levels')
        plt.legend()
        plt.grid()
        plt.xticks(rotation=45)

        # Set custom x-axis tick intervals (e.g., every 1 day)
        interval = timedelta(days=1)
        plt.gca().xaxis.set_major_locator(plt.MultipleLocator(base=interval.days))

        plt.tight_layout()
        plt.pause(10)  # Pause for 10 sec for test purpose but use 5 minutes (300 sec) to pause before updating the plot with new data

if __name__ == "__main__":



    try:
           asyncio.run(update_plot())

    except KeyboardInterrupt:
            plt.ioff()  # Turn off interactive mode when done
            plt.show()  # Display the final plot



        # while True:
        #
        #         # asyncio.run(main())
        #         loop = asyncio.get_event_loop()
        #         df = loop.run_until_complete(main())  # Get the returned DataFrame from main()
        #
        #         # Plotting the liquidity levels
        #         plt.figure(figsize=(10, 6))
        #         plt.plot(df['Timestamp'], df['Buyside_Level_Start'], 'go', label='Buyside Start')
        #         plt.plot(df['Timestamp'], df['Buyside_Level_Break'], 'ro', label='Buyside Break')
        #         plt.plot(df['Timestamp'], df['Sellside_Level_Start'], 'bo', label='Sellside Start')
        #         plt.plot(df['Timestamp'], df['Sellside_Level_Break'], 'mo', label='Sellside Break')
        #         plt.xlabel('Timestamp')
        #         plt.ylabel('Price')
        #         plt.title('Liquidity Levels')
        #         plt.legend()
        #         plt.grid()
        #         plt.show()
        # #
        # while 1:
        #
        #     asyncio.run(main())
