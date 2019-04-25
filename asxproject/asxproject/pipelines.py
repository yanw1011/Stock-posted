# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import scrapy
from scrapy.utils.project import get_project_settings
from scrapy.pipelines.files import FilesPipeline
from scrapy.exceptions import DropItem
import os
import shutil
class MyFilesPipeline(FilesPipeline):
    FILES_STORE = get_project_settings().get("FILES_STORE")
    def get_media_requests(self,item,info):
        file_url = item["file_url"]
        file_path2 = item["file_name"]      
        yield scrapy.Request(url=file_url, meta={'item': item,'file_name':file_path2})
    def item_completed(self,result,item,infor):
        file_paths = [x["path"] for ok, x in result if ok]
        if not file_paths:
            raise DropItem("Item contains no file")

        file_path = item["file_path"]
        # if os.path.exists(file_path) == False:
        #      os.makedirs(file_path)

        # os.chdir(file_path)
        # d = item['file_name']
        print('=====================================================')
        print(self.FILES_STORE + "/" + file_paths[0], file_path+"/" + item["file_name"] + ".pdf")
        print(file_paths)
        print(result)
        # down_filename = file_paths[0].split('/')[1]
        # print(self.FILES_STORE + "\\full\\" + item["file_name"] + ".pdf")
        # print(file_path)
        # print(file_path + "\\" + down_filename)
        # print(file_path + "\\" + item["file_name"] + ".pdf")
        # print(down_filename, item["file_name"], item["file_url"])
        # print(item['file_name']+'======='+dsfsda)
        # print(self.FILES_STORE + "\\" + d + ".pdf")
        print('888888888888888888888888888888888888888888888888888888888')
        # shutil.move(self.FILES_STORE + "\\" + file_paths[0], file_path + "\\" + item["file_name"] + ".pdf")
        # os.rename(file_path + "\\" + down_filename, file_path + "\\" + item["file_name"] + ".pdf")
        # os.rename(self.FILES_STORE + "\\" + file_paths[0], self.FILES_STORE + "\\" + item["file_name"] + ".pdf")
        # os.renames(self.FILES_STORE + "/" + file_paths[0], file_path+"/" + item["file_name"] + ".pdf")
        # shutil.move(self.FILES_STORE + "\\" + item["file_name"] + ".pdf", file_path)
        item["file_path"] = file_path
        return item

    def file_path(self, request, response=None, info=None):
        item = request.meta['item']
        file_name = request.meta['file_name']
        print('>>>>>>>>>>>>      file _ path >>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        print(file_name)
        print('\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\')
        return item['file_path'] + '/' + file_name + '.pdf'


