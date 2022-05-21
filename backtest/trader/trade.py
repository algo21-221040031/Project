# trade.py

from pymongo import DESCENDING
import pandas as pd
import matplotlib.pyplot as plt
from data.database import DB_CONN
from trader.timing import is_k_up_break_ma10, is_k_down_break_ma10
import ccxt

class Trade:

    def __init__(
        self, 
        cash=1E7, 
        single_position=2E5, begin_date='2021-01-01T16:00:00Z', end_date='2021-12-30T16:00:00Z',
        this_phase_codes = ['BTC/USDT','ETH/USDT','LUNA/USDT','TRX/USDT'],
        slippage = 0.001
        ):

        self.cash = cash
        self.single_position = single_position
        self.begin_date = begin_date
        self.end_date = end_date
        self.this_phase_codes = this_phase_codes
        self.slippage = slippage
    
    def _get_trading_dates(self,begin_date, end_date):
        # 从火币交易所获取交易日期；
        huobi_exchange = ccxt.huobi()
        days = []
        while begin_date < end_date:
            days.append(begin_date)
            begin_date = huobi_exchange.iso8601(huobi_exchange.parse8601(begin_date) + 60*1000*60*24)
        return days  

    def backtest(self):

        cash = self.cash

        # 时间为key的净值、收益；
        df_profit = pd.DataFrame(columns=['net_value', 'profit'])

        # 获取回测开始日期和结束之间的所有交易日，并且是按照正序排列
        all_dates = self._get_trading_dates(self.begin_date, self.end_date)
        # 待卖的数字货币简称集合
        to_be_sold_codes = set()
        # 待买的数字货币简称集合
        to_be_bought_codes = set()
        # 持仓货币dict，key是数字货币简称，value是一个dict，
        # 三个字段分别为：cost - 持仓成本，volume - 持仓数量，last_value：前一天的市值
        holding_code_dict = dict()

        # 在交易日的顺序，一天天完成信号检测
        for _date in all_dates:
            print('Backtest at %s.' % _date)

            # 当期持仓货币的代码列表
            before_sell_holding_codes = list(holding_code_dict.keys())

            """
            卖出的逻辑处理：
            卖出价格是当日的开盘价，卖出的数量就是持仓币种的数量，卖出后获得的资金累加到账户的可用现金上
            """

            print('待卖币种池：', to_be_sold_codes, flush=True)
            # 如果有待卖货币，则继续处理
            if len(to_be_sold_codes) > 0:
                # 从daily数据集中查询所有待卖数字货币的开盘价
                sell_daily_cursor = DB_CONN['daily'].find(
                    {'code': {'$in': list(to_be_sold_codes)}, 'date': _date},
                    projection={'Open': True, 'code': True}
                )

                # 一个货币一个货币处理
                for sell_daily in sell_daily_cursor:
                    # 待卖货币的简称
                    code = sell_daily['code']
                    # 如果货币在持仓币池里
                    if code in before_sell_holding_codes:
                        # 获取持仓货币
                        holding_stock = holding_code_dict[code]
                        # 获取持仓数量
                        holding_volume = holding_stock['volume']
                        # 卖出价格为当日开盘价
                        sell_price = sell_daily['Open'] * (1-self.slippage)
                        # 卖出获得金额为持仓量乘以卖出价格
                        sell_amount = holding_volume * sell_price
                        # 卖出得到的资金加到账户的可用现金上
                        cash += sell_amount
                        # 获取该只货币的持仓成本
                        cost = holding_stock['cost']
                        # 计算持仓的收益
                        single_profit = (sell_amount - cost) * 100 / cost
                        print('卖出 %s, %6d, %6.2f, %8.2f, %4.2f' %
                            (code, holding_volume, sell_price, sell_amount, single_profit))

                        # 删除该货币的持仓信息
                        del holding_code_dict[code]
                        to_be_sold_codes.remove(code)

            print('卖出后，现金: %10.2f' % cash)

            """
            买入的逻辑处理：
            买入的价格是当日的开盘价，每只数字货币可买入的金额为20万，如果可用现金少于20万，就不再买入了
            """
            print('待买币种池：', to_be_bought_codes, flush=True)
            
            # 如果待买货币集合不为空，则执行买入操作
            if len(to_be_bought_codes) > 0:
                # 获取所有待买入货币的开盘价
                buy_daily_cursor = DB_CONN['daily'].find(
                    {'code': {'$in': list(to_be_bought_codes)}, 'date': _date},
                    projection={'code': True, 'Open': True}
                )

                # 处理所有待买入货币
                for buy_daily in buy_daily_cursor:
                    # 判断可用资金是否够用
                    if cash > self.single_position:
                        # 获取买入价格
                        buy_price = buy_daily['Open'] * (1+self.slippage)
                        # 获取货币简称
                        code = buy_daily['code']
                        # 获取可买的数量，数量必须为正手数
                        volume = self.single_position / buy_price
                        # 买入花费的成本为买入价格乘以实际的可买入数量
                        buy_amount = buy_price * volume
                        # 从现金中减去本次花费的成本
                        cash -= buy_amount
                        # 增加持仓币
                        holding_code_dict[code] = {
                            'volume': volume,         # 持仓量
                            'cost': buy_amount,       # 持仓成本
                            'last_value': buy_amount  # 初始前一日的市值为持仓成本
                        }

                        print('买入 %s, %6d, %6.2f, %8.2f' % (code, volume, buy_price, buy_amount))

            print('买入后，现金: %10.2f' % cash)

            # 持仓币种简称列表
            holding_codes = list(holding_code_dict.keys())

            # 检查是否有需要第二天卖出的货币
            for holding_code in holding_codes:
                if is_k_down_break_ma10(holding_code, _date):
                    to_be_sold_codes.add(holding_code)

            # 检查是否有需要第二天买入的货币
            to_be_bought_codes.clear()
            #if this_phase_codes is not None:
            for _code in self.this_phase_codes:
                if _code not in holding_codes and is_k_up_break_ma10(_code, _date):
                    to_be_bought_codes.add(_code)

            # 计算总资产
            total_value = 0

            # 获取所有持仓货币的当日收盘价
            holding_daily_cursor = DB_CONN['daily'].find(
                {'code': {'$in': holding_codes}, 'date': _date},
                projection={'Close': True, 'code': True}
            )

            # 计算所有持仓货币的总市值
            for holding_daily in holding_daily_cursor:
                code = holding_daily['code']
                holding_stock = holding_code_dict[code]
                
                # 单只持仓的市值等于收盘价乘以持仓量
                value = holding_daily['Close'] * holding_stock['volume']
                
                # 总市值等于所有持仓币种市值的累加之和
                total_value += value

                # 计算单个货币的持仓收益
                profit = (value - holding_stock['cost']) * 100 / holding_stock['cost']
                
                # 计算单个货币的单日收益
                one_day_profit = (value - holding_stock['last_value']) * 100 / holding_stock['last_value']
                
                # 更新前一日市值
                holding_stock['last_value'] = value
                print('持仓: %s, %10.2f, %4.2f, %4.2f' %
                    (code, value, profit, one_day_profit))

            # 总资产等于总市值加上总现金
            total_capital = total_value + cash
            print('收盘后，现金: %10.2f, 总资产: %10.2f' % (cash, total_capital))
            
            # 将当日的净值、收益和沪深300的涨跌幅放入DataFrame
            df_profit.loc[_date] = {
                'net_value': round(total_capital / self.cash, 2),
                'profit': round(100 * (total_capital - self.cash) / self.cash, 2)
            }
        return df_profit

if __name__ == "__main__":
    Trade().backtest()
