# main.py

from sympy import evaluate
from trader.trade import *
from trader.evaluate import *
from data.daily_crawler import *

cash = 10000000
single_position = 200000
begin_date = '2021-01-01T16:00:00.000Z'
end_date = '2021-12-30T16:00:00.000Z' 
this_phase_codes = ['BTC/USDT', 'ETH/USDT', 'LUNA/USDT', 'TRX/USDT']

trade =  Trade(
            cash=cash, 
            single_position=single_position, 
            begin_date=begin_date, 
            end_date=end_date, 
            this_phase_codes=this_phase_codes
            )

df_profit = trade.backtest()
df_profit.index = df_profit.reset_index()['index'].str.replace('T16:00:00.000Z','')
df_profit.index = df_profit.reset_index()['index'].str.replace('2021-','')

evaluate = Evaluate(net_values=df_profit['net_value'])

print(df_profit)

# 计算最大回撤
drawdown = evaluate.compute_drawdown()

# 计算年化收益和夏普比率
annual_profit, sharpe_ratio = evaluate.compute_sharpe_ratio()

print('回测结果 %s - %s，年化收益： %7.3f%%, 最大回撤：%7.3f, 夏普比率：%4.2f' %
    (begin_date, end_date, annual_profit, drawdown, sharpe_ratio))

# 绘制收益曲线
df_profit.plot(title='Backtest Result', y=['profit'], kind='line')
plt.show()
