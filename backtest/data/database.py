#  database.py

from pymongo import MongoClient

# 指定数据库的连接，quant_01是数据库名
#DB_CONN = MongoClient('mongodb://127.0.0.1:27017').quant_01
client = MongoClient('mongodb://localhost:27017/')

#with client:
DB_CONN = client.quant_01
