from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from lxml import etree
import time
import hashlib
import json
import os

class get_page_QAR:
    def __init__(self, url, max_click=100):
        self.url = url
        self.status_code = None
        self.links = []
        self.answers = []
        self.max_click = max_click
        self.url_md5 = hashlib.md5(self.url.encode('utf-8', 'ignore')).hexdigest()
        self.usr_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'

        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.customHeaders.user-agent"] = self.usr_agent
        self.driver = webdriver.PhantomJS(
                                          service_args=['--ignore-ssl-errors=true',
                                                        '--load-images=false', ],
                                          desired_capabilities=dcap)

        self.driver.set_window_size(1024, 1200)

    def get_QA(self):
        #首先获取回答数，根据回答数确定向下翻页次数
        html = etree.HTML(self.driver.page_source)
        answer_num = html.xpath('//span[@class="card-record-right"]//p[@class="card-record-count"]/text()')[0]
        self.scrol_num = int(int(answer_num) / 8) + 1
        #print(self.scrol_num)
        for i in range(self.scrol_num):
            try:
                #time.sleep(0.2)
                js = "window.scrollTo(0, document.body.scrollHeight)"
                self.driver.execute_script(js)
            except Exception as e:
                print(e)
                break
        #print("scroll %d times..." % i)
        html = etree.HTML(self.driver.page_source)
        self.title = html.xpath('//div//h1[@class="card-title"]/text()')[0]
        description_list = html.xpath('//div[@class="content example"]//p/text()')
        if len(description_list):
            self.description = description_list[0]
        else:
            self.description = None
            #print("description is None")
            #print(self.url)
        tagList = html.xpath('//ul[@class="card-tag-list"]//li//a//text()')
        if len(tagList):
            self.tag = tagList[0]
        else:
            self.tag = "其他"
        answer_elems = html.xpath('//div[@class="card-reply-wrap"]')
        for answer_tmp in answer_elems:
            answer = ""
            answer_list = answer_tmp.xpath('.//div[@ahe-role="text"]//text()')
            answer = "\n".join(answer_list)
            self.answers.append(answer)

    def writeFile(self):
        fileName = self.url_md5 + ".txt"
        fileDir = os.path.join("汽车之家_Corpus", self.tag)
        if not os.path.exists(fileDir):
            os.makedirs(fileDir)
        dstFile = os.path.join(fileDir, fileName)
        with open(dstFile, "w", encoding="utf-8") as fw:
            print("=========title=========", file=fw)
            print(self.title, file=fw)
            if self.description != None:
                print("=========description========", file=fw)
                print(self.description, file=fw)
            print("==========answer===========", file=fw)
            for ans in self.answers:
                print(ans, file=fw)
                print("======================", file=fw)

    def getResponseStatus(self):
        har = json.loads(self.driver.get_log('har')[0]['message'])
        return har['log']['entries'][0]['response']["status"]
        #return (har['log']['entries'][0]['response']["status"], str(har['log']['entries'][0]['response']["statusText"]))


    def start(self):
        self.driver.get(self.url)
        #判断网页重定向
        time.sleep(0.2)
        if self.driver.current_url == "https://wenda.autohome.com.cn/":
            print("重定向....")
            print("---------------------------")
            self.close_driver()
            return None
        self.status_code = self.getResponseStatus()
        if self.status_code != 200:
            print("{0} 状态码：{1}".format(self.driver.current_url, self.status_code))
            self.close_driver()
            return None
        self.get_QA()
        self.writeFile()
        self.close_driver()

        return True

    def close_driver(self):
        try:
            self.driver.close()
            self.driver.quit()
        except Exception as e:
            print(e)
            print("dirver already closed!")


def test_get_page_QAR():
    url = "https://wenda.autohome.com.cn/topic/detail/397518"
    url_error = "https://wenda.autohome.com.cn/topic/detail/1000000"
    url_redirect = "https://wenda.autohome.com.cn/topic/detail/10100"
    crawler = get_page_QAR(url)
    crawler.start()




if __name__ == "__main__":
    test_get_page_QAR()
