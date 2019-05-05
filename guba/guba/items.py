# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GubaItem(scrapy.Item):

    #抓取日期
    crawl_date = scrapy.Field()
    #股吧代号
    stock_ID = scrapy.Field()
    #股吧吧名
    stock_name = scrapy.Field()
    #follow_num关注数
    follow_num = scrapy.Field()
    #浏览排名
    ran_num = scrapy.Field()
    #存放公告 研报 咨询内容
    today_article = scrapy.Field()
    #文章数目
    article_num = scrapy.Field()

