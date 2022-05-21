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

## Class Description
* dailycrowler: This class gives other classes an interface for providing market data to the remaining components with the system, which connects the exchange and the local MongoDB;
* trade: This class generates the trading signal and finish the execution, and gets data from class DailyCrawler and calls the function from Timing;
* evaluate: This class measures the performance of the strategy.

## Result Analysis
* The net value is:
  <div align=left>
  <img src="https://user-images.githubusercontent.com/101002984/169658215-0870d05f-7a0c-490b-9bc9-e39dbc177983.png" />
  </div>
* The performance matrix is:
  -------- | :-----------:
 Date Interval      | 20210101-2021-1230  
  -------- | :-----------:
 Annual yield rate     | 26.160%
  -------- | :-----------:
Maximum Drawdown    | 0.033
  -------- | :-----------:
 Sharpe Ratio| 1.97
