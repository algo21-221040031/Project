# evaluate.py

import pandas as pd

class Evaluate:
    def __init__(self,net_values):
        self.net_values = net_values

    def compute_drawdown(self):
        """
        计算最大回撤
        :param net_values: 净值列表
        """
        # 最大回撤初始值设为0
        max_drawdown = 0
        size = len(self.net_values)
        index = 0
        # 双层循环找出最大回撤
        for net_value in self.net_values:
            # 计算从当前开始直到结束，和当前净值相比的最大回撤
            for sub_net_value in self.net_values[index:]:
                # 计算回撤
                drawdown = 1 - sub_net_value / net_value
                # 如果当前的回撤大于已经计算的最大回撤，则当前回撤作为最大回撤
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
            index += 1

        return max_drawdown


    def _compute_annual_profit(self, trading_days, net_value):
        """
        计算年化收益
        """

        annual_profit = 0
        # 交易日数大于0，才计算年化收益
        if trading_days > 0:
            # 计算年数
            years = trading_days / 365
            # 计算年化收益
            annual_profit = pow(net_value, 1 / years) - 1

        # 将年化收益转化为百分数，保留两位小数
        annual_profit = round(annual_profit * 100, 2)

        return annual_profit


    def compute_sharpe_ratio(self):
        """
        计算夏普比率
        :param net_values: 净值列表
        """

        # 总交易日数
        trading_days = len(self.net_values)
        # 所有收益的DataFrame
        profit_df = pd.DataFrame(columns={'profit'})
        # 收益之后，初始化为第一天的收益
        profit_df.loc[0] = {'profit': round((self.net_values[0] - 1) * 100, 2)}
        # 计算每天的收益
        for index in range(1, trading_days):
            # 计算每日的收益变化
            profit = (self.net_values[index] - self.net_values[index - 1]) / self.net_values[index - 1]
            profit = round(profit * 100, 2)
            profit_df.loc[index] = {'profit': profit}

        # 计算当日收益标准差
        profit_std = pow(profit_df.var()['profit'], 1 / 2)

        # 年化收益
        annual_profit = self._compute_annual_profit(trading_days, self.net_values[-1])

        # 夏普比率
        sharpe_ratio = (profit_df['profit'].mean() * 365 - 2.059) / (profit_std * pow(365, 1 / 2))

        return annual_profit, sharpe_ratio
