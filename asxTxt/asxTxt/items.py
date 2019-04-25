# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AsxTxtItem(scrapy.Item):
    # 文件名称
    file_name = scrapy.Field()
    # 文件链接
    file_url = scrapy.Field()
    # 文件保存路径
    file_path = scrapy.Field()
    # 文章发布的年份
    file_year = scrapy.Field()
    # pdf文章的时间公司名称pdf文章标题名asxcode封装，拼接格式为：公司名*pdf发布时间*pdf文章名*asxcode
    file_information = scrapy.Field()
    # 文件当前的请求链接
    # file_now = scrapy.Field()
    # 获取索引号
    # file_id = scrapy.Field()
