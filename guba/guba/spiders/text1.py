# -*- coding: utf-8 -*-

import re
import scrapy
import requests
import datetime
from bs4 import BeautifulSoup
from guba.items import GubaItem


class Text1Spider(scrapy.Spider):
    name = 'text1'
    allowed_domains = ['guba.eastmoney.com']
    start_urls = ['http://guba.eastmoney.com/remenba.aspx?type=1&tab=1']

    url = 'http://guba.eastmoney.com{next}'
    base_url = 'http://guba.eastmoney.com/list,{stockcode},f_{pagenum}.html'

    def parse(self, response):
        '''
            实现对起始页的分析找到股票公司的股票代码，根据股票代码拼接出完整的股票请求链接
            发起请求由函数 parse_detail 对具体的吧内内容进行解析
        '''

        # 1、找到股票的代码
        ngblistul2s = response.css('.ngblistul2')
        hrefs = ngblistul2s.css('a::attr(href)').extract()
        # 2、遍历股票代码
        for href in hrefs:
            # 3、对股票代码进行正则匹配，并判断是否是6字开头的股票代码，是就处理
            if re.findall(r'[6][0-9]{5}', href):
                # 对不同股吧进行抓取的时候变量重置，page_num中记录的是抓取到吧内的第几页，
                # article_list存放的是['资讯', '公告', '研报']的内容
                page_num = 1
                article_list = []
                # 4、正则匹配，提取到股票代码
                stockcode = re.findall(r'[6][0-9]{5}', href)[0]
                # 5、根据股票代码拼接链接，发送请求，并传递参数。
                # 第一个参数拼接url 第二和参数为回调函数，第三个参数为要传递的参数，
                # dont_filter=True禁止scrapy运行去重机制，默认为False
                yield scrapy.Request(self.base_url.format(stockcode=stockcode, pagenum=1), callback=self.parse_detail,
                                     meta={'stockcode': stockcode, 'article_list': article_list, 'page_num': page_num},
                                     dont_filter=True)

    def parse_detail(self, response):
        '''
           对吧内页面进行解析
        '''

        # 存放的是今日帖子数量
        article_num = 0
        # 接收上级函数传递的参数
        stockcode = response.meta['stockcode']
        article_list = response.meta['article_list']
        page_num = response.meta['page_num']
        item = GubaItem()
        hifo_list = ['资讯', '公告', '研报']
        # 获取本地时间
        local_time = datetime.datetime.now().strftime('%Y-%m-%d')
        # 获取股票名称
        stockname = response.css('#stockname > a::text').extract_first()
        # 获取股票关注数和今日关注排名
        follow_num = response.css('.follow_num::text').extract_first()
        ran_num = response.css('.ran_num::text').extract_first()
        # 判断是否有帖子
        html_data = requests.get(response.url)
        soup = BeautifulSoup(html_data.text, 'lxml')
        has_data = soup.select('#articlelistnew > div.noarticle')

        item['crawl_date'] = local_time
        item['stock_ID'] = stockcode
        item['stock_name'] = stockname
        item['follow_num'] = follow_num
        item['ran_num'] = ran_num

        # 没有帖子的吧直接封装提交数据，有数据的贴吧继续进行进一步处理
        if has_data:
            item['today_article'] = '没有文章'
            item['article_num'] = 0
            yield item
        else:
            # 获取系统当前时间
            now_time = datetime.datetime.now().strftime('%m-%d')
            # 当前所有帖子的发表时间
            stock_times = response.css('.l5.a5::text').extract()[1:]
            # 记录最后一个帖子的时间
            late_times = stock_times[len(stock_times) - 1]
            # 循环遍历找到今天帖子数
            for stock_time in stock_times:
                if now_time in stock_time:
                    article_num = article_num + 1
            # 如果最后一个帖子的时间等于本地时间，则证明今日发帖量大于一页，则递归进行找到计算今日帖子的数量
            if now_time in late_times:
                # 页面数加 1
                page_num = page_num + 1
                yield scrapy.Request(self.base_url.format(stockcode=stockcode, pagenum=page_num),
                                     callback=self.parse_time,
                                     meta={'stockcode': stockcode, 'item': item, 'article_num': article_num,
                                           'page_num': page_num}, dont_filter=True)
            item['article_num'] = article_num

            # 找到['资讯', '公告', '研报']帖子对应的链接，进行请求，进一步获取数据
            hifos = response.css('.hinfo::text').extract()
            hifos_url = response.css('.hinfo+a::attr(href)').extract()
            for hifo, hifo_url in zip(hifos, hifos_url):
                if hifo in hifo_list:
                    # print(self.url.format(next=hifo_url))
                    yield scrapy.Request(self.url.format(next=hifo_url), callback=self.parse_article,
                                         meta={'article_type': hifo, 'item': item, 'article_list': article_list},
                                         dont_filter=True)

    def parse_article(self, response):
        '''
           对'资讯', '公告', '研报'，这些帖子进行进一步处理，获得进一步的数据，比如：文章标题，文章内容，文章发表时间等
        '''
        # 保存文章内容
        article_text = ''
        # 获得上级传来的参数
        item = response.meta['item']
        article_list = response.meta['article_list']
        article_type = response.meta['article_type']
        # 获得本地时间
        local_time = datetime.datetime.now().strftime('%Y-%m-%d')
        # 获得帖子的发表时间
        zwfbtime = response.css('.zwfbtime::text').extract_first()
        zwfbtime = re.findall(r'\d{4}-\d{1,2}-\d{1,2}', zwfbtime)[0]
        # 判断是否是今日发表的帖子，是就进行抓取处理，不是则跳过
        if local_time == zwfbtime:
            title = response.css('#zwconttbt::text').extract_first().strip()
            articles = response.css('p::text').extract()
            # 循环获取文章内容
            for article in articles:
                article_text = article_text + article.strip()
            content = {
                "article_type": article_type,
                "article_time": zwfbtime,
                "article_title": title,
                "article_text": article_text,
                'article_url': response.url
            }
            article_list.append(content)
        item['today_article'] = article_list
        yield item

    def parse_time(self, response):
        '''
            如果今日发帖量比较多则会进行到这一步，循环实现翻页计算今日的帖子数量
        '''
        # 获得上级传来的参数
        page_num = response.meta['page_num']
        article_num = response.meta['article_num']
        item = response.meta['item']
        stockcode = response.meta['stockcode']
        # 获取系统当前时间
        now_time = datetime.datetime.now().strftime('%m-%d')
        # ran_num = response.css('.articleh.normal_post .l3.a3 a::attr(title)').extract()
        stock_times = response.css('.l5.a5::text').extract()[1:]

        # 记录最后一个帖子的时间
        late_times = stock_times[len(stock_times) - 1]
        # 循环遍历找到今天帖子数
        for stock_time in stock_times:
            if now_time in stock_time:
                article_num = article_num + 1
        # 实现递归调用
        if now_time in late_times:
            page_num = page_num + 1
            yield scrapy.Request(self.base_url.format(stockcode=stockcode, pagenum=page_num), callback=self.parse_time,
                                 meta={'stockcode': stockcode, 'item': item, 'article_num': article_num,
                                       'page_num': page_num}, dont_filter=True)
        else:
            item['article_num'] = article_num
            yield item
