# daily_crawler.py

from pymongo import UpdateOne
from data import database
import ccxt
from datetime import datetime
import pandas as pd

"""
从ccxt获取日K数据，保存到本地的MongoDB数据库中
"""
huobi_exchange = ccxt.huobi()

DB_CONN = database.DB_CONN

class DailyCrawler:

    def __init__(self):
        """
        初始化
        """

        # 创建daily数据集
        self.daily = DB_CONN['daily']

    def save_data(self, code, df_daily, collection, extra_fields=None):
        """
        将从网上抓取的数据保存到本地MongoDB中

        :param code: 数字货币名称
        :param df_daily: 包含日线数据的DataFrame
        :param collection: 要保存的数据集
        :param extra_fields: 除了K线数据中保存的字段，需要额外保存的字段
        """

        # 数据更新的请求列表
        update_requests = []

        # 将DataFrame中的行情数据，生成更新数据的请求
        for df_index in df_daily.index:
            # 将DataFrame中的一行数据转dict
            doc = dict(df_daily.loc[df_index])
            # 设置数字货币名称
            doc['code'] = code

            # 如果指定了其他字段，则更新dict
            if extra_fields is not None:
                doc.update(extra_fields)

            # 生成一条数据库的更新请求
            update_requests.append(
                UpdateOne(
                    {'code': doc['code'], 'date': doc['date']},
                    {'$set': doc},
                    upsert=True)
            )

        # 如果写入的请求列表不为空，则保存都数据库中
        if len(update_requests) > 0:
            # 批量写入到数据库中，批量写入可以降低网络IO，提高速度
            update_result = collection.bulk_write(update_requests, ordered=False)
            print('保存日线数据，代码： %s, 插入：%4d条, 更新：%4d条' %
                  (code, update_result.upserted_count, update_result.modified_count),
                  flush=True)

    def crawl(self, begin_date=None, end_date=None):
        """
        :param begin_date: 开始日期
        :param end_date: 结束日期
        begin_date = '2021-10-05T00:00:00.000Z'
        end_date = '2021-10-30T00:00:00.000Z'
        """
        
        codes = ['BTC/USDT','ETH/USDT','LUNA/USDT','TRX/USDT']

        # 当前日期
        now = datetime.now().strftime('%Y-%m-%d') + 'T16:00:00.000Z'

        # 如果没有指定开始日期，则默认为当前日期
        if begin_date is None:
            begin_date = now

        # 如果没有指定结束日期，则默认为当前日期
        if end_date is None:
            end_date = now

        for code in codes:
            since = huobi_exchange.parse8601(begin_date) 
            end = huobi_exchange.parse8601(end_date)
            all_kline_data = []
            while since < end:
                while 1 :
                    # 存在获取时间的限制，需要取消这种限制
                    try:
                        kline_data = huobi_exchange.fetch_ohlcv(code, since=since, timeframe='1d',limit=2)
                        break
                    except:
                        pass
                print(huobi_exchange.iso8601(since))
                if len(kline_data):
                    # 更新获取时间
                    since = kline_data[len(kline_data) - 1][0]
                    all_kline_data += [kline_data[-1]]
                else:
                    break
            kline_data = pd.DataFrame(all_kline_data)
            kline_data.columns = ['date', 'Open', 'High', 'Low', 'Close', 'Vol']
            kline_data['date'] = kline_data['date'].apply(huobi_exchange.iso8601)
            df_daily = kline_data
            self.save_data(code, df_daily, self.daily)
    
#database.client.close()
# 抓取程序的入口函数
if __name__ == '__main__':
    dc = DailyCrawler()
    # 抓取指定日期范围的日行情
    # 这两个参数可以根据需求改变，时间范围越长，抓取时花费的时间就会越长
    dc.crawl('2021-01-01T00:00:00.000Z', '2021-12-31T00:00:00.000Z')
