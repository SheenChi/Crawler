# coding=utf-8

from mongo_qczj import MongoUrlManager
from crawler_qczj import get_page_QAR
import re
import time

mongo_mgr = MongoUrlManager()

while True:
	record = mongo_mgr.dequeueUrl()
	if record == None:
		print("数据库为空， 程序退出")
		break
	url = record['url']
	crawler = get_page_QAR(url)
	ret = crawler.start()
	if ret == None:
		mongo_mgr.finishUrl(url,error_flag="True")
	else:
		mongo_mgr.finishUrl(url)

	time.sleep(0.2)


