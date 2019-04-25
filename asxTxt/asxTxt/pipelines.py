# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
class AsxtxtPipeline(object): 
#     def open_spider(self,spider):
#         self.file = open('items2.txt', 'w')
 
#     def close_spider(self,spider):
#         self.file.close()
 
# #item在后期使用的时候还要转换回来，他存在的意义只是防止出错导致程序中止
#     def process_item(self, item, spider):
#         try:
#             res=dict(item)
#             line=res['file_name']
#             self.file.write(line.encode('utf-8')+'\n')
#         except:
#             pass
    def __init__(self):
        self.filename = open("asxtxt.txt",'w',encoding='utf-8')
        self.filename1 = open("asxjson.json",'w',encoding='utf-8')
    def process_item(self,item,spider):        
        text2 = item["file_information"]
        text3 = json.dumps(dict(item),ensure_ascii=False)+",\n"
        self.filename.write(text2+'\n')
        self.filename1.write(text3)
    def close_spider(self,spider):
        self.filename.close()
        self.filename1.close()
