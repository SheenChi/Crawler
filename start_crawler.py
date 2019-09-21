# coding=utf-8

from mongo_YouKu import MongoUrlManager
from crawler_YouKu import Crawler_YouKu
import time
import os

mongo_mgr = MongoUrlManager()

root_url = "https://list.youku.com/category/show/c_100.html"
mongo_mgr.enqueueUrl(root_url, 0)

while True:
	record = mongo_mgr.dequeueUrl()
	if record == None:
		print("数据库为空， 程序退出")
		break
	url = record['url']
	depth = record['depth']
	crawler = Crawler_YouKu(url)
	if depth == 0:
		crawler.get_label_1()
		for href, region in crawler.label_1_List:
			mongo_mgr.enqueueUrl(href, 1, region)
		mongo_mgr.finishUrl(url)
	elif depth == 1:
		region = record['region']
		crawler.get_label_2()
		for href, type in crawler.label_2_List:
			mongo_mgr.enqueueUrl(href, 2, region, type)
		mongo_mgr.finishUrl(url)
	elif depth == 2:
		region = record["region"]
		type = record["type"]
		fileTmp = region + "_" + type + ".txt"
		fileDir = os.path.join("优酷_Corpus", "动漫")
		if not os.path.exists(fileDir):
			os.makedirs(fileDir)
		fileName = os.path.join(fileDir, fileTmp)
		crawler.get_movieName()
		with open(fileName, "w", encoding="utf-8") as fw:
			for name in crawler.contents:
				fw.write(name + "\n")
				mongo_mgr.enqueueItems(region, type, name)

	crawler.close_driver()
	time.sleep(0.2)


