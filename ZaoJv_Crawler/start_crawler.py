# coding=utf-8

from mongo_zaojv import MongoUrlManager
from crawler_zaojv import Crawler_zaojv
import re
import time

mongo_mgr = MongoUrlManager()

# 设置爬虫起始页
root_url = "http://www.miaoqiyuan.cn/zaojv/word-a.html"
# 向数据库中添加一级网页
first_url = "http://zaojv.com/word_{}.html"
"""
for page in range(1,1046):
	url_tmp = first_url.format(page)
	mongo_mgr.enqueueUrl(url_tmp, 1)
	time.sleep(0.1)
"""

while True:
	record = mongo_mgr.dequeueUrl()
	if record == None:
		print("数据库为空， 程序退出")
		break
	url = record['url']
	depth = record['depth']
	reset_num = record['reset_num']
	crawler = Crawler_zaojv(url, depth)
	if (crawler.html == None) or (crawler.html == ""):
		if reset_num < 3:
			mongo_mgr.resetUrl(url)
		else:
			mongo_mgr.finishUrl(url, error_flag=True)
		time.sleep(1)
		continue
	retLen = crawler.parseContent()
	if retLen == 0:
		if reset_num < 3:
			mongo_mgr.resetUrl(url)
		else:
			mongo_mgr.finishUrl(url, error_flag=True)
		time.sleep(1)
		continue

	mongo_mgr.finishUrl(url)
	if depth == 1:
		for url_tmp in crawler.words_url:
			mongo_mgr.enqueueUrl(url_tmp, depth+1)

	time.sleep(0.5)


