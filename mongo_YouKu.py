import pymongo
from pymongo import MongoClient
from pymongo import IndexModel, ASCENDING, DESCENDING

import time
import hashlib
import sys

class MongoUrlManager:

    def __init__(self, mongo_ip='localhost', mongo_port=27017,
                    client=None, database_name='YouKu', table_name='动漫'):
        # 连接mongodb
        self.client = MongoClient(host=mongo_ip, port=mongo_port)
        self.db = self.client[database_name]
        self.table = self.db[table_name]
        # 为 mongodb 创建索引， 便于实现快速查询
        if self.table.count() is 0:
            self.table.create_index([("status", ASCENDING),])

    def enqueueUrl(self, url, depth, region=None, type=None):
        try:
            if self.table.find_one({'_id':hashlib.md5(url.encode('utf-8', 'ignore')).hexdigest()}):
                return None
            self.table.insert(
                {
                    '_id': hashlib.md5(url.encode('utf-8', 'ignore')).hexdigest(),
                    'url': url,
                    'depth': depth,
                    'region': region,
                    'type': type,
                    'status': "new",
                    'queue_time': time.strftime("%Y%m%d %H%M%S"),
                }
            )
        except Exception as e:
            print("lineNum {0}: {1}".format(str(sys._getframe().f_lineno), e))

    def enqueueItems(self, region, type, name, typeFinal="item"):
        try:
            if self.table.find_one({'_id': hashlib.md5(name.encode('utf-8', 'ignore')).hexdigest()}):
                return None
            self.table.insert(
                {
                    '_id': hashlib.md5(name.encode('utf-8', 'ignore')).hexdigest(),
                    'type': type,
                    'region': region,
                    'name': name,
                    'typeFinal': typeFinal,
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
            sort=[('depth',ASCENDING), ('queue_time', ASCENDING)],
        )
        if record:
            return record
        else:
            return None

    def finishUrl(self, url, error_flag="False"):
        record = {'status': 'done', 'done_time': time.strftime("%Y%m%d %H%M%S"), 'error_flag': error_flag}
        self.table.update({'_id': hashlib.md5(url.encode('utf-8', 'ignore')).hexdigest()}, {'$set': record},
                          upsert=False)

    def removeUrl(self, url):
        self.table.remove({'_id': hashlib.md5(url.encode('utf-8', 'ignore')).hexdigest()})

    def resetUrl(self, url):
        tmp = self.table.find_one({'_id': hashlib.md5(url.encode('utf-8')).hexdigest()})
        num = tmp['reset_num'] + 1
        record = {'status': 'new', 'queue_time':time.strftime("%Y%m%d %H%M%S"), 'reset_num':num}
        self.table.update({'_id': hashlib.md5(url.encode('utf-8', 'ignore')).hexdigest()}, {'$set': record},
                          upsert=False)

    def clear(self):
        self.table.drop()


def add_topic_items_2_mongo(index_s, index_e):
    base_topic_url = "https://wenda.autohome.com.cn/topic/detail/"
    mongo_mgr = MongoUrlManager()
    for serial_id in range(index_s, index_e+1):
        print(serial_id)
        url = base_topic_url + str(serial_id)
        mongo_mgr.enqueueUrl(url, serial_id)
        time.sleep(0.1)




if __name__ == "__main__":
    index_s = 82174
    index_e = 400000
    add_topic_items_2_mongo(index_s, index_e)


