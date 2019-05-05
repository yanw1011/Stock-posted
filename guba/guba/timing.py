import datetime
import time
import os
if __name__ == "__main__":
    while True:
        print('现在的时间是：')
        now = datetime.datetime.now()
        print(now.month, '月', now.day, '号', now.hour, '点', now.minute, '分')
        if now.hour == 23 and now.minute == 0:
            print("开始执行了")
            os.system("scrapy crawl text1")
        #休眠60秒检测一次
        time.sleep(60)

