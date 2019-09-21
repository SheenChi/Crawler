from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from lxml import etree
import time
import hashlib
import json
import os

class Crawler_YouKu:
    def __init__(self, url, max_click=300):
        self.url = url
        self.status_code = None
        self.max_click = max_click
        self.url_md5 = hashlib.md5(self.url.encode('utf-8', 'ignore')).hexdigest()
        self.usr_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'

        self.root_url = "https://list.youku.com"
        self.label_1_List = []
        self.label_2_List = []
        self.contents = []

        chrome_options = Options()
        chrome_options.add_argument('windows-size=1024x1200')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('blink-settings=imagesEnabled=false')
        # prefs = {"profile.managed_default_content_settings.images": 2}
        # chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get(url)
        self.driver.refresh()

    def get_label_1(self):
        html = etree.HTML(self.driver.page_source)
        label_elems = html.xpath('//div[@class="category_category_tag"]//dl')[2]
        for elem_tmp in label_elems.xpath('./dd//a')[1:]:
            href_tmp = elem_tmp.xpath('./@href')[0]
            text_tmp = elem_tmp.xpath('./text()')[0]
            self.label_1_List.append([self.root_url + href_tmp, text_tmp])

    def get_label_2(self):
        html = etree.HTML(self.driver.page_source)
        label_elems = html.xpath('//div[@class="category_category_tag"]//dl')[3]
        for elem_tmp in label_elems.xpath('./dd//a')[1:]:
            href_tmp = elem_tmp.xpath('./@href')[0]
            text_tmp = elem_tmp.xpath('./text()')[0]
            self.label_2_List.append([self.root_url + href_tmp, text_tmp])

    def get_movieName(self):
        #向下滚动滑轮，获取更多电影名称
        for i in range(self.max_click):
            try:
                js = "window.scrollTo(0, document.body.scrollHeight)"
                self.driver.execute_script(js)
            except Exception as e:
                print(e)
                break

        html = etree.HTML(self.driver.page_source)
        item_elems = html.xpath('//div[@class="videolist_container_inner"]//div[@class="g-col"]//div[@class="categorypack_info_list"]')
        for elem_tmp in item_elems:
            title = elem_tmp.xpath('.//a/@title')[0]
            #desc = elem_tmp.xpath('.//div[@class="categorypack_subtitle"]//text()')
            self.contents.append(title)

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


def test_get_label():
    url = "https://list.youku.com/category/show/c_96_a_中国香港_g_犯罪.html"
    url_2 = "https://list.youku.com/category/show/c_96_a_中国香港_g_动作.html?spm=a2ha1.12701310.app.5~5!2~5!2~5~5~DL!3~DD~A!17"
    crawler = Crawler_YouKu(url)
    crawler.get_movieName()
    print(crawler.contents)
    print(len(crawler.contents))




if __name__ == "__main__":
    test_get_label()
