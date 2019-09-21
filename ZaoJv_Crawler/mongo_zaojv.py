import pymongo
from pymongo import MongoClient
from pymongo import IndexModel, ASCENDING, DESCENDING

import time
import hashlib
import sys

class MongoUrlManager:

    def __init__(self, mongo_ip='localhost', mongo_port=27017,
                    client=None, database_name='Zaojv', table_name='zaojv_items'):
        # 连接mongodb
        self.client = MongoClient(host=mongo_ip, port=mongo_port)
        self.db = self.client[database_name]
        self.table = self.db[table_name]
        # 为 mongodb 创建索引， 便于实现快速查询
        if self.table.count() is 0:
            self.table.create_index([("status", ASCENDING), ("reset_num", ASCENDING)])

    def enqueueUrl(self, url, depth):
        try:
            if self.table.find_one({'_id':hashlib.md5(url.encode('utf-8', 'ignore')).hexdigest()}):
                return None
            self.table.insert(
                {
                    '_id': hashlib.md5(url.encode('utf-8', 'ignore')).hexdigest(),
                    'url': url,
                    "depth": depth,
                    'status': "new",
                    'reset_num': 0,
                    'queue_time': time.strftime("%Y%m%d %H%M%S"),
                }
            )
        except Exception as e:
            print("lineNum {0}: {1}".format(str(sys._getframe().f_lineno), e))

    def dequeueUrl(self):
        record = self.table.find_one_and_update(
            {'status': 'new'},
            {'$set': {'status': 'downloading'}},
            upsert=False,
            returnNewDocument=False,
            sort=[("depth", DESCENDING),('queue_time', ASCENDING)],
        )
        if record:
            return record
        else:
            return None

    def finishUrl(self, url, error_flag=False):
        if error_flag == False:
            record = {'status': 'done', 'done_time': time.strftime("%Y%m%d %H%M%S")}
        else:
            record = {'status': 'done', 'done_time': time.strftime("%Y%m%d %H%M%S"), 'error_flag': 'True'}

        self.table.update({'_id': hashlib.md5(url.encode('utf-8', 'ignore')).hexdigest()}, {'$set': record},
                          upsert=False)

    def resetUrl(self, url):
        tmp = self.table.find_one({'_id': hashlib.md5(url.encode('utf-8')).hexdigest()})
        num = tmp['reset_num'] + 1
        record = {'status': 'new', 'queue_time':time.strftime("%Y%m%d %H%M%S"), 'reset_num':num}
        self.table.update({'_id': hashlib.md5(url.encode('utf-8', 'ignore')).hexdigest()}, {'$set': record},
                          upsert=False)

    def clear(self):
        self.table.drop()



