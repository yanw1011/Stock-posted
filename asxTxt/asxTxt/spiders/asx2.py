# -*- coding: utf-8 -*-
import scrapy
import xlrd
import requests
from bs4 import BeautifulSoup
import re
from scrapy import Spider
from scrapy.http import Request
from asxTxt.items import AsxTxtItem
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from scrapy.utils.project import get_project_settings

class Asx2Spider(scrapy.Spider):
    name = 'asx2'
    #allowed_domains = ['www.asx.com.au']
    #start_urls = ['http://www.asx.com.au/']
    #allowed_domains = ['httpbin.org']
    #start_urls = ['http://httpbin.org/get']
    url_lists = []
    row_num = 0
    col_num = 0
    base_url = "https://www.asx.com.au" 
    '''
    构建初次访问链接，对Excel中公司名进行遍历，遍历公司年份是1998—2018
    '''
    def start_requests(self):
        xlsx_path = 'F:\\test0407.xlsx'
        workbook = xlrd.open_workbook(xlsx_path)
        data_sheet = workbook.sheets()[0]
        self.row_num = data_sheet.nrows
        self.col_num = data_sheet.ncols
        for i in range(self.row_num):
            rowlist = []
            for j in range(self.col_num):
                rowlist.append(data_sheet.cell_value(i,j))
            self.url_lists.append(rowlist)
        # yield Request(url='https://www.asx.com.au/asx/statistics/announcements.do?by=asxCode&asxCode=NTD&timeframe=Y&year=2017', callback=self.parse_information, meta={'title': 'yang'})
        
        for uid in self.url_lists:
            for i in range(1998,2019):
                # yield Request(url = 'https://baidu.com',callback =self.parse_information)
                # yield Request(url = 'https://baidu.com',callback =lambda response, asxcode = uid[1]:self.parse_information(response,asxcode))
                yield Request(url='https://www.asx.com.au/asx/statistics/announcements.do?by=asxCode&asxCode=%s&timeframe=Y&year=%s'%(uid[1], i), callback=self.parse_information, meta={'title': uid[0],'asxcode':uid[1]})

    def parse_information(self, response):  
        
        # 初始化模型对象
        item = AsxTxtItem()
        selector = Selector(response)
        # links = selector.xpath('//*[@id="content"]/div/announcement_data/table/tbody/tr')
        allasxcode = selector.xpath('//*[@id="content"]/div/announcement_data/table/caption')
        if allasxcode:
            for i in allasxcode:
                # 序号是 allasxcode.index(i) + 1 asxcode是 i
                links = selector.xpath('//*[@id="content"]/div/announcement_data['+ str(allasxcode.index(i)+ 1)+']/table/tbody/tr')                          
                # //*[@id="content"]/div/announcement_data[1]/table/tbody/tr[1]/td[3]/a                                
                if links:
                    # 有公告
                    for link in links:               
                        # 获取文章标题
                        title = link.xpath('normalize-space(./td[3]/a/text())').extract_first()
                        if ('Disclosure Document' in title) or ('Prospectus' in title):
                        # if 'Prospectus' in title:
                            #获取网页中asxcode码
                            pdfasxcode = i.xpath('normalize-space(./text())').extract_first().split(" ")
                            #获取pdf文章时间
                            pdftime = link.xpath('normalize-space(./td[1]/text())').extract_first()
                            # 获取文章标题
                            # file_title = link.xpath('normalize-space(./td[3]/a/text())').extract_first()
                            # 获取跳转链接                    
                            middle_href = link.xpath('./td[3]/a/@href').extract_first()
                            # 获取发布年份
                            year = link.xpath('./td[1]/text()').extract_first().split('/')[2]
                            company_name = response.meta['title']
                            company_asxcode = response.meta['asxcode']
                            # item['file_now'] = re.findall('&asxCode=(.*?)&timeframe=',response.url)[0]
                            # item['file_id'] = response.meta['title']
                            # item['file_name'] = link.xpath('normalize-space(./td[3]/a/text())').extract_first()                  
                            item['file_path'] = re.sub(r'[\\/:*?"<>|\r\n\t]+', "_", company_name)
                            item['file_year'] = year
                            item['file_name'] = str(year)+ " "+ re.sub(r'[\\/:*?"<>|\r\n\t]+', "_", title)
                            # 拼接格式为：公司名##公司现有ascode##pdf发布时间##pdf文章名##asxcode
                            item['file_information'] = re.sub(r'[\\/:*?"<>|\r\n\t]+', "_", company_name)+'##'+re.sub(r'[\\/:*?"<>|\r\n\t]+', "_", company_asxcode) +'##'+str(pdftime)+'##'+str(year)+ " "+ re.sub(r'[\\/:*?"<>|\r\n\t]+', "_", title)+'##'+pdfasxcode[3]
                            pdf_data = requests.get(self.base_url + middle_href)
                            soup = BeautifulSoup(pdf_data.text, 'lxml')
                            pdf_url = soup.select('body > div > form > input[type="hidden"]')[0].get('value')
                            item['file_url'] = self.base_url + pdf_url
                            yield item
                            #yield Request(url=self.base_url + middle_href, callback=self.parse_url, meta={'item': item,'file_title':title})
                else:
                    # 没有公告
                    pass
    '''    
    def parse_url(self, response):
        selector = Selector(response)
        item = response.meta['item']
        file_dsf = response.meta['file_title']
        fin_href = selector.xpath('//*[@name="showAnnouncementPDFForm"]/input[3]/@value').extract_first()
        item['file_url'] = self.base_url + fin_href
        item['file_name'] = file_dsf
        yield item
    '''
if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())
    process.crawl('asx1')
    process.start()


'''
    def parse(self, response):
        self.logger.debug(response.text)
'''