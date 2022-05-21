# Design of digital currency backtest system based on breakout strategy of moving average

## Introduction
Our project is a digital currency backtesting system based on the moving average breakthrough strategy. In the strategy section, we use the moving average breakout strategy to generate trading signals, a buy signal when the closing price crosses the moving average, and a sell signal when the closing price crosses the moving average. Based on the MA10 strategy, we construct a backtesting system.

## Language Environment
* Python 3.9
* Modules: pandas, numpy, matplotlib.pyplot, pymongo, datetime.

## Files Description
* Folder "backtest": containing all the coding .py files;
  * Folder "data":
    1. database.py: construct a database in local MongoDB
* Folder "data": containing all the data required, the price of stock option of JP Morgan;
* Folder "result": containing the output figures.
