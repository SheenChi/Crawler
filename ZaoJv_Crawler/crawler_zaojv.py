# coding:utf-8
import requests
from lxml import etree
import time
import hashlib
import os
import time
import random
import re

class Crawler_zaojv:
	def __init__(self, url, depth):
		self.url = url
		self.root_url = "http://zaojv.com"
		self.depth = depth
		self.html = None
		self.words_url = []
		self.contents = []
		ret = self.getHtmlTxt()
		if ret=="" or ret== None:
			print(self.url, "爬取失败...")

	def getHtmlTxt(self):
		try:
			all_agents = [
    					"Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
    					"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
    					"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
    					"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
    					"Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)"
					]
			user_agent = random.choice(all_agents)
			headers = {
				"User-Agent":user_agent
			}
			r = requests.get(self.url, headers=headers, timeout=30)
			if r.status_code != 200:
				return None
			self.html = r.text
			return r.text
	
		except Exception as e:
			print(e)
			return None

	def parseContent(self):
		self.pageSource = etree.HTML(self.html)
		if self.depth == 1:
			words_elems = self.pageSource.xpath('//div[@id="div_main_left"]//div[@id="div_content"]//div[@id="div_left"]//ul[@class="c1 ico2"]//li[@class="dotline"]//@href')
			words_elems = [self.root_url + word_tmp for word_tmp in words_elems]
			self.words_url = words_elems
			return len(self.words_url)
		else:
			try:
				self.title = self.pageSource.xpath('//div[@id="div_main_left"]//div[@class="viewbox"]//div[@class="title"]/h2//text()')[0]
				#print(self.title)
				contents_elems = self.pageSource.xpath('//div[@id="div_main_left"]//div[@class="viewbox"]//div[@id="content"]//div[@id="all"]//div[not(@id)]')
				for elem_tmp in contents_elems:
					text = elem_tmp.xpath('.//text()')
					retText = "".join(text)
					self.contents.append(retText)

				# 爬取下一页
				while True:
					next_elem_list = self.pageSource.xpath('//div[@id="div_main_left"]//div//a[contains(text(),"下一页")]')
					if len(next_elem_list) == 0:
						break
					self.url = self.root_url + "/" + next_elem_list[0].xpath('./@href')[0]
					ret = self.getHtmlTxt()
					if ret == "" or ret == None:
						for count in range(3):
							time.sleep(1)
							ret = self.getHtmlTxt()
							if ret != "" and ret != None:
								break
						if ret == "" or ret == None:
							print(self.url, "下一页爬取失败...")
							break
					self.pageSource = etree.HTML(self.html)
					contents_elems = self.pageSource.xpath('//div[@id="div_main_left"]//div[@class="viewbox"]//div[@id="content"]//div[@id="all"]//div[not(@id)]')
					for elem_tmp in contents_elems:
						text = elem_tmp.xpath('.//text()')
						retText = "".join(text)
						self.contents.append(retText)
				#print(self.contents)
			except Exception as e:
				print(e)
				print("current url: ", self.url)

			if len(self.contents):
				self.writeFile()
			return len(self.contents)


	def writeFile(self, dstDir="02_Zaojv_corpus"):
		try:
			fileName = self.title + ".txt"
			dstFile = os.path.join(dstDir, fileName)
			with open(dstFile, "w", encoding="utf-8") as fw:
				for content in self.contents:
					fw.write(content)
					fw.write("\n")
		except Exception as e:
			print(e)


if __name__ == "__main__":
	url_1 = "http://zaojv.com/word.html"
	url_2 = "http://zaojv.com/758979.html"
	url_2_next = "http://zaojv.com/758979_2.html"
	url_3 = "http://www.miaoqiyuan.cn/zaojv/an11/anshang.html"

	crawler = Crawler_zaojv(url_2, 2)
	crawler.parseContent()