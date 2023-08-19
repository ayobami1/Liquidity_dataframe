# Liquidity Calculation using Python

This repository contains Python code for calculating liquidity levels in the cryptocurrency market. The original liquidity calculation was implemented in Pine Script, and this repository showcases how the same concept is adapted to Python.

## Background

Liquidity levels play a crucial role in analyzing the cryptocurrency market. It helps traders identify potential price points where trading activity is likely to occur. The original code was written in Pine Script, a scripting language for creating custom technical analysis indicators and strategies on the TradingView platform.

This repository demonstrates how to perform liquidity calculation using Python, fetching OHLCV data from the Binance exchange API and implementing the same liquidity calculation strategy used in the Pine Script.

## Conversion from Pine Script to Python

The conversion from Pine Script to Python was done as follows:

1. **Fetching Data**: In Pine Script, we used the `request.security` function to fetch OHLCV data. In Python, the `fetch_ohlcv` function uses the CCXT library to fetch data from the Binance exchange.

2. **Calculate Liquidity Levels**: In Pine Script, the liquidity levels were calculated using moving averages (MA) and specific conditions. This concept was replicated in Python's `calculate_liquidity_levels` function. A volume threshold was introduced to filter levels based on trading volume.

3. **Main Loop**: In Pine Script, the code ran continuously on TradingView. In Python, the `main` function orchestrates the process within a loop to fetch, calculate, and print liquidity levels.

## Requirements and Dependencies

- Python 3.x
- CCXT library for fetching data from the Binance exchange
- Retry library for handling network errors
- loguru
- pandas


## Usage

1. Install required libraries using `pip install ccxt retry loguru pandas`.

2. Replace `symbol`, `timeframe`, and other parameters in the `main` function to match your requirements.

3. Run the script using `python liquidity_dataframe.py`.

## Notes

- Adjust `volume_threshold` to control the sensitivity of the liquidity calculation to trading volume.

- The code is intended for educational purposes and can be further optimized and customized based on specific trading strategies.

## Acknowledgments

- This code conversion was done by Ayocrypt.

- Original Pine Script code was provided by Lux Algo.
