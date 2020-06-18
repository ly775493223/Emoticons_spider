
import requests
from urllib import request
from lxml import etree
import  os
import re
from queue import Queue
import threading

class Producer(threading.Thread):
    headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'
        }
    def __init__(self,page_queue,img_queue,*args,**kwargs):
        super(Producer,self).__init__(*args,**kwargs)
        self.page_queue = page_queue
        self.img_queue = img_queue

    def run(self):
        while True:
            if self.page_queue.empty():
                break
            url = self.page_queue.get()
            self.parse_page(url)

    def parse_page(self,url):
        response = requests.get(url,headers=self.headers)
        text = response.text
        html = etree.HTML(text)
        imgs = html.xpath('//div[@class="random_picture"]//img[@class!="gif"]')
        for img in imgs:
            img_url = img.get('data-original')
            alt = img.get('alt')
            alt = re.sub(r'[\/,，\.!！\?？~&$*@#\|]','',alt)
            suffix = os.path.splitext(img_url)[1]
            file_name = alt + suffix
            self.img_queue.put((img_url,file_name))

class Consumer(threading.Thread):
    def __init__(self,page_queue,img_queue,*args,**kwargs):
        super(Consumer,self).__init__(*args,**kwargs)
        self.page_queue = page_queue
        self.img_queue = img_queue

    def run(self):
        while True:
            if self.img_queue.empty() and self.page_queue.empty():
                break
            img_url,filename = self.img_queue.get()
            request.urlretrieve(img_url,'表情包/'+filename)
            print("%s  下载完成"%filename)

def main():
    page_queue = Queue(1000)
    img_queue = Queue(100000)
    for i in range(1,1001):
        url = 'https://www.doutula.com/photo/list/?page=%d'%i
        page_queue.put(url)

    for i in range(10):
        t = Producer(page_queue,img_queue)
        t.start()
    for i in range(10):
        t = Consumer(page_queue,img_queue)
        t.start()

if __name__ == '__main__':
    main()

