## 本工具用于爬取汽车之家问答语料

#### 爬取网址：https://wenda.autohome.com.cn/topic/detail/

#### 本工具主要包含两个模块：
##### 1、数据库模块 mongo_qczj
    用于生成需要爬取的网页以及存储网页的爬取状态：未爬取、正在爬取、爬取完成
    
##### 2、网页解析模块 crawler_qczj
    通过模拟浏览器不断下拉获取问题的所有答案并写入文件中
