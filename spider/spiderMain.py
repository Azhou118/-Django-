import json
import time
import csv
from distutils.command.install_egg_info import install_egg_info
from ipaddress import summarize_address_range
from xml.etree.ElementPath import xpath_tokenizer

import django
import pandas as pd
import os
import requests
from lxml import etree
import re
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doubantushu.settings')
django.setup()
from myApp.models import BookList


class spider(object):
    def __init__(self, tag, page):
        self.tag = tag
        self.page = page
        self.bookId = 0
        self.spiderUrl = 'https://book.douban.com/tag/%s?start=%s&#39&#39'
        self.headers = {
            'HOST': 'book.douban.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            'Referer': 'https://book.douban.com/tag/&#39&#39'
        }
        # self.proxies={
        #     'http': 'http://67.43.228.251:7365&#39;,
        #     'https': 'http://67.43.228.251:7365&#39;    # 如果代理支持 HTTPS
        # }

    def main(self):
        while True:
            time.sleep(4.0)#防止被封
            resq = requests.get(self.spiderUrl % (self.tag, self.page * 20), headers=self.headers)
            print('爬取页面为：' + self.spiderUrl % (self.tag, self.page * 20))
            # print(resq.text)
            respXpath = etree.HTML(resq.text)
            li_list = respXpath.xpath('//ul[@class="subject-list"]/li/div[2]/h2/a')
            # print(li_list)
            detailLinks = [x.xpath('@href')[0] for x in li_list]
            # print(detailLinks)

            for i in detailLinks:
                time.sleep(random.uniform(1, 3))#防止被封
                try:
                    print('正在爬取的详情地址为' + i)
                    respDetail = requests.get(i, headers=self.headers)
                    respDetailXpath = etree.HTML(respDetail.text)
                    # title
                    title = respDetailXpath.xpath('//span[@property="v:itemreviewed"]/text()')[0]
                    # cover
                    cover = respDetailXpath.xpath('//img[@rel="v:photo"]/@src')[0]
                    # info
                    info = respDetailXpath.xpath('//div[@id="info"]')[0]
                    # author
                    author = info.xpath('./span[1]/a/text()')[0]

                    # press
                    press = info.xpath('./a/text()')[0]
                    # year
                    year = re.search('\d{4}-\d{1,2}', "".join(respDetailXpath.xpath('//div[@id="info"]/text()'))).group()
                    # pageNum
                    regex = re.compile(r"\d{4}-\d{1,2}")
                    pageNum = re.search('\d{3}',
                                        regex.sub('', "".join(respDetailXpath.xpath('//div[@id="info"]/text()')))).group()
                    # price
                    try:
                        price = re.search(r'\d+(\.\d+)?', "".join(respDetailXpath.xpath(
                            '//span[contains(text(), "定价")]/following-sibling::text()')).strip()).group()
                    except:
                        price = random.randint(1, 1000)
                    # rate
                    rate = respDetailXpath.xpath('//strong[@property="v:average"]/text()')[0].strip()

                    # starList
                    starList = json.dumps(
                        [float(x.text.replace('%', '')) for x in respDetailXpath.xpath('//span[@class="rating_per"]')])

                    # summary
                    summary = ""
                    for s in [x.text for x in
                              respDetailXpath.xpath('//div[@id="link-report"]/span[@class="short"]/div[@class="intro"]/p')]:
                        if s: summary += s

                    # detailLink
                    detailLink = i
                    createTime = time.localtime(time.time())
                    # comment_len
                    comment_len = re.search('\d+',
                                            respDetailXpath.xpath('//div[@class="mod-hd"]//span[@class="pl"]/a/text()')[
                                                0]).group()
                    # print(detailLink,createTime,comment_len)

                    # commentlist
                    commentList = []
                    for c in respDetailXpath.xpath('//ul/li[@class="comment-item"]'):
                        try:
                            userName = c.xpath('.//h3/span[@class="comment-info"]/a[1]/text()')[0]
                            star = int(int(re.search('\d+', c.xpath('.//h3/span[@class="comment-info"]/span[1]/@class')[
                                0]).group()) / 10)
                            userId = random.randint(1, 100)
                            createTime = c.xpath('.//h3/span[@class="comment-info"]/a[2]/text()')[0][:10]
                            content = c.xpath('.//p[@class="comment-content"]/span/text()')[0]
                            commentList.append({
                                'userName': userName,
                                'star': star,
                                'bookId': self.bookId,
                                'userId': userId,
                                'createTime': createTime,
                                'content': content
                            })
                        except:
                            continue

                    commentList = json.dumps(commentList)
                    # print(commentList)
                    self.save_to_csv([
                        self.bookId,
                        self.tag,
                        title,
                        cover,
                        author,
                        press,
                        year,
                        pageNum,
                        price,
                        rate,
                        starList,
                        summary,
                        detailLink,
                        createTime,
                        comment_len,
                        commentList

                    ])
                    self.bookId += 1

                except:
                    continue

            self.page += 1
        self.main()

        # break

    def save_to_csv(self, rowData):
        with open('./temp.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(rowData)

    def init(self):
        if not os.path.exists('./temp.csv'):
            with open('./temp.csv', 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["bookId", "tag", "title", "cover", "author", "press", "year", "pageNum", "price", "rate",
                     "starList", "summary", "detailLink",
                     "createTime", "comment_len", "commentList"])

    def clearData(self):
        df = pd.read_csv('./temp.csv')
        df.dropna(inplace=True)
        df.drop_duplicates(inplace=True)
        print("总数据条数为%d" % df.shape[0])
        return df.values

    def save_to_sql(self):
        data = self.clearData()
        for book in data:
                print(book[0])
                BookList.objects.create(
                    bookId=book[0],
                    tag=book[1],
                    title=book[2],
                    cover=book[3],
                    author=book[4],
                    press=book[5],
                    year=book[6],
                    pageNum=book[7],
                    price=book[8],
                    rate=book[9],
                    starList=book[10],
                    summary=book[11],
                    detailLink=book[12],
                    createTime=book[13],
                    comment_len=book[14],
                    commentList=book[15]
                )


import json
import time
import csv
from distutils.command.install_egg_info import install_egg_info
from ipaddress import summarize_address_range
from xml.etree.ElementPath import xpath_tokenizer

import django
import pandas as pd
import os
import requests
from lxml import etree
import re
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doubantushu.settings')
django.setup()
from myApp.models import BookList


class spider(object):
    def __init__(self, tag, page):
        self.tag = tag
        self.page = page
        self.bookId = 0
        self.spiderUrl = 'https://book.douban.com/tag/%s?start=%s&#39&#39'
        self.headers = {
            'HOST': 'book.douban.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            'Referer': 'https://book.douban.com/tag/&#39&#39'
        }
        # self.proxies={
        #     'http': 'http://67.43.228.251:7365&#39;,
        #     'https': 'http://67.43.228.251:7365&#39;    # 如果代理支持 HTTPS
        # }

    def main(self):
        while True:
            time.sleep(4.0)#防止被封
            resq = requests.get(self.spiderUrl % (self.tag, self.page * 20), headers=self.headers)
            print('爬取页面为：' + self.spiderUrl % (self.tag, self.page * 20))
            # print(resq.text)
            respXpath = etree.HTML(resq.text)
            li_list = respXpath.xpath('//ul[@class="subject-list"]/li/div[2]/h2/a')
            # print(li_list)
            detailLinks = [x.xpath('@href')[0] for x in li_list]
            # print(detailLinks)

            for i in detailLinks:
                time.sleep(random.uniform(1, 3))#防止被封
                try:
                    print('正在爬取的详情地址为' + i)
                    respDetail = requests.get(i, headers=self.headers)
                    respDetailXpath = etree.HTML(respDetail.text)
                    # title
                    title = respDetailXpath.xpath('//span[@property="v:itemreviewed"]/text()')[0]
                    # cover
                    cover = respDetailXpath.xpath('//img[@rel="v:photo"]/@src')[0]
                    # info
                    info = respDetailXpath.xpath('//div[@id="info"]')[0]
                    # author
                    author = info.xpath('./span[1]/a/text()')[0]

                    # press
                    press = info.xpath('./a/text()')[0]
                    # year
                    year = re.search('\d{4}-\d{1,2}', "".join(respDetailXpath.xpath('//div[@id="info"]/text()'))).group()
                    # pageNum
                    regex = re.compile(r"\d{4}-\d{1,2}")
                    pageNum = re.search('\d{3}',
                                        regex.sub('', "".join(respDetailXpath.xpath('//div[@id="info"]/text()')))).group()
                    # price
                    try:
                        price = re.search(r'\d+(\.\d+)?', "".join(respDetailXpath.xpath(
                            '//span[contains(text(), "定价")]/following-sibling::text()')).strip()).group()
                    except:
                        price = random.randint(1, 1000)
                    # rate
                    rate = respDetailXpath.xpath('//strong[@property="v:average"]/text()')[0].strip()

                    # starList
                    starList = json.dumps(
                        [float(x.text.replace('%', '')) for x in respDetailXpath.xpath('//span[@class="rating_per"]')])

                    # summary
                    summary = ""
                    for s in [x.text for x in
                              respDetailXpath.xpath('//div[@id="link-report"]/span[@class="short"]/div[@class="intro"]/p')]:
                        if s: summary += s

                    # detailLink
                    detailLink = i
                    createTime = time.localtime(time.time())
                    # comment_len
                    comment_len = re.search('\d+',
                                            respDetailXpath.xpath('//div[@class="mod-hd"]//span[@class="pl"]/a/text()')[
                                                0]).group()
                    # print(detailLink,createTime,comment_len)

                    # commentlist
                    commentList = []
                    for c in respDetailXpath.xpath('//ul/li[@class="comment-item"]'):
                        try:
                            userName = c.xpath('.//h3/span[@class="comment-info"]/a[1]/text()')[0]
                            star = int(int(re.search('\d+', c.xpath('.//h3/span[@class="comment-info"]/span[1]/@class')[
                                0]).group()) / 10)
                            userId = random.randint(1, 100)
                            createTime = c.xpath('.//h3/span[@class="comment-info"]/a[2]/text()')[0][:10]
                            content = c.xpath('.//p[@class="comment-content"]/span/text()')[0]
                            commentList.append({
                                'userName': userName,
                                'star': star,
                                'bookId': self.bookId,
                                'userId': userId,
                                'createTime': createTime,
                                'content': content
                            })
                        except:
                            continue

                    commentList = json.dumps(commentList)
                    # print(commentList)
                    self.save_to_csv([
                        self.bookId,
                        self.tag,
                        title,
                        cover,
                        author,
                        press,
                        year,
                        pageNum,
                        price,
                        rate,
                        starList,
                        summary,
                        detailLink,
                        createTime,
                        comment_len,
                        commentList

                    ])
                    self.bookId += 1

                except:
                    continue

            self.page += 1
        self.main()

        # break

    def save_to_csv(self, rowData):
        with open('./temp.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(rowData)

    def init(self):
        if not os.path.exists('./temp.csv'):
            with open('./temp.csv', 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["bookId", "tag", "title", "cover", "author", "press", "year", "pageNum", "price", "rate",
                     "starList", "summary", "detailLink",
                     "createTime", "comment_len", "commentList"])

    def clearData(self):
        df = pd.read_csv('./temp.csv')
        df.dropna(inplace=True)
        df.drop_duplicates(inplace=True)
        print("总数据条数为%d" % df.shape[0])
        return df.values

    def save_to_sql(self):
        data = self.clearData()
        for book in data:
                print(book[0])
                BookList.objects.create(
                    bookId=book[0],
                    tag=book[1],
                    title=book[2],
                    cover=book[3],
                    author=book[4],
                    press=book[5],
                    year=book[6],
                    pageNum=book[7],
                    price=book[8],
                    rate=book[9],
                    starList=book[10],
                    summary=book[11],
                    detailLink=book[12],
                    createTime=book[13],
                    comment_len=book[14],
                    commentList=book[15]
                )


if __name__ == '__main__':
    spider_obj = spider('科幻', 0)
    # spider_obj.main()#爬取数据
    # spider_obj.init()#初始化csv
    spider_obj.save_to_sql()#将数据保存到数据库，务必爬完所需要的所有书籍信息后再运行这个，
    #现在数据还没爬完，等爬完后,把数据库表全删了,再重新用另一个项目生成，记得把两个项目的migrations文件都删了，重新生成.然后两个项目都要运行那两个东西。
    #目前数据库已经删除，需要重新注册用户,才能打开网页