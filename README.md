# Design of digital currency backtest system based on breakout strategy of moving average

## Introduction
Our project is a digital currency backtesting system based on the moving average breakthrough strategy. In the strategy section, we use the moving average breakout strategy to generate trading signals, a buy signal when the closing price crosses the moving average, and a sell signal when the closing price crosses the moving average. Based on the MA10 strategy, we construct a backtesting system.

## Language Environment
* Python 3.9
* Modules: pandas, numpy, matplotlib.pyplot, pymongo, datetime.

## Files Description
* Folder "backtest": containing all the coding .py files;
  * Folder "data":
    1. database.py: construct a database in local MongoDB;
    2. daily_crawler: containing the class DailyCrowler, which captures the data from the exchange to local database.
  * Folder "trader":
    1. timing.py: containing the three MA10 strategies functions, which the execute the main strategy;
    2. trade.py: containing the class Trade, which contains the heart backtest(self), that automatically do the backtesting of the strategy;
    3. evaluate.py: containing the class Evaluate, which used to compute the drawdown, annual_profit, and the sharpe ratio.
* The File "main.py": run this file it will automatically do the backtesting of the strategy.


