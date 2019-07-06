import urllib3
from bs4 import BeautifulSoup
from lxml import html
import xml
import requests
import re 
from urllib import request
import os
import json
import random
import time
import threading
import socket
http = urllib3.PoolManager()
headers = {
"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
"Accept-Encoding": "gzip, deflate",
"Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
"Cache-Control": "max-age=0",
"Connection": "keep-alive",
"Cookie": "UM_distinctid=16b7cf230ed4c6-0cd2791b0bfde6-e343166-1fa400-16b7cf230eebe6; CNZZDATA1257039673=283923358-1561169374-%7C1561859928; ASPSESSIONIDQCTBBDQS=ONBPONFDGAOLLFPFBFKFDNPF; 7Dw1Tw3Bh2Mvfr=; 7Dw1Tw3Bh2Mvu%5Fleixing=3; 7Dw1Tw3Bh2Mvu%5Fpw=c8534b0ccc48128b; 7Dw1Tw3Bh2Mvu%5Fusername=sdoshanxi865; 7Dw1Tw3Bh2Mvu%5Fid=89348",
"Host": "www.tujidao.com",
"Referer": "http://www.tujidao.com/u/?action=login",
"Upgrade-Insecure-Requests": 1,
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"  
}
socket.setdefaulttimeout(20)
# 目标网站地址
webUrl = "http://www.tujidao.com"
#文件下载地址
Path="F:\\图集岛\\"
#继承父类threading.Thread 并重写__init__方法和 run方法
class myThread(threading.Thread):
    def __init__(self,begNum,endNum):
        threading.Thread.__init__(self)
        self.begNum = begNum
        self.endNum = endNum
    def run(self):
            downAltals(self.begNum,self.endNum)
    def __del__(self):
             print("相册采集完成") 

# 获取分类名称 
def className(classId):
   url = webUrl +'/s/?id='+str(classId)
   try:
      r = http.request('Get',url,headers=headers)
      time.sleep(0.5)
   except IOError:
      print('', end="\r")
   soup = BeautifulSoup(r.data.decode("utf8"), "lxml")
   legend = soup.find('div',class_='hezi').find('legend').text#图集分类名称
   return legend
# 如果存在该图集 则返回图集名称 
def realClassid(classId):
   url = webUrl +'/s/?id='+str(classId)
   try:
      r = http.request('Get',url,headers=headers)
      time.sleep(0.5)
   except IOError:
      print('', end="\r")
   soup = BeautifulSoup(r.data.decode("utf8"), "lxml")
   legend = soup.find('div',class_='hezi').find('legend').text#图集分类名称
   if legend != "临时图集":
      if legend != "图集":
        return legend
   return False
#图片下载速度
def Schedule(blocknum,blocksize,totalsize):
    per = 100.0 * blocknum * blocksize / totalsize
    if per > 100 :
        per = 100
   # print('当前下载进度：%d'%per,end="\r")
#下载单张图片
def auto_down(url,filename):
   try:
       request.urlretrieve(url,filename)
   except IOError:
      count = 1
      while count <= 15:
         try:
               request.urlretrieve(url, filename)
               break
         except IOError:
               count += 1
      if count > 15:
         print('',end='\r')  
# 下载整个图片集
def imgDownLoad(imgUrl,localPath):
   try:
      r = http.request('Get',imgUrl,headers=headers)
      time.sleep(0.5)
   except IOError:
      print('', end="\r")
   try:
      soup = BeautifulSoup(r.data.decode("utf8"), "lxml")
   except:
      return
   else:
      for k in soup.find('div',id='kbox').find_all('img'):     
            imgUrl = k['data-src']
            downPath = localPath +"\\"+ imgUrl.split('//')[1].split('/')[4]
            auto_down(imgUrl,downPath)
      return

# 创建文件夹
def mkdir(path):
    path=path.strip() # 去除首位空格
    path=path.rstrip("\\") # 去除尾部 \ 符号
    isExists=os.path.exists(path) # 判断路径是否存在 存在 True 不存在   False
    # 判断结果
    if not isExists:
        os.makedirs(path) 
        return True
    else:
        return False

#获取图集分类总的分页数量
def altasClassPageCount(altasClassId):
   url = webUrl +'/s/?id='+str(altasClassId)
   try:
      r=http.request('Get',url,headers=headers)
      time.sleep(0.5)
   except IOError:
      print('', end="\r")
   soup = BeautifulSoup(r.data.decode("utf8"), "lxml")
   pagenum = soup.find('div',class_='text-c').find('a').text
   pagenum = int(re.findall(r"\d+\.?\d*", pagenum)[0])
   allPageCount = int(pagenum/20)+2
   return allPageCount

# 获取当前分类下 指定页面的 div中的内容
def pageAltasHtml(classId,pageNum):
   url = webUrl +'/s/?id='+str(classId)+'&page=' +str(pageNum)
   try:
      r = http.request('Get',url,headers=headers)
      time.sleep(0.5)
   except IOError:
      print('', end="\r")
   soup = BeautifulSoup(r.data.decode("utf8"), "lxml")
   html = soup.find('div',class_='hezi')
   return html

#根据传来的li的HTML信息，解析成json 
def pageAltasInfo(lihtml):
   p = lihtml.find_all('p')
   altasInfo = {
   #图集名称
   "altasName":p[3].a.text.replace('\\',' ').replace('\\',' ').replace('/',' ').replace(':',' ').replace('*',' ').replace('?',' ').replace('<',' ').replace('>',' ').replace('|',' ').replace('"',' '), 
   "photoCount": lihtml.find('span').text, #图片数量
   "altasUrl":webUrl+p[3].a['href'], #图集地址
   "cover":lihtml.find('a').img['data-original'],#图集封面
   "organName":p[0].a.text,#图集发行机构名称
   "organUrl":webUrl+ p[0].a['href']
      }
   return altasInfo
# 多线程函数——下载图片 
def downAltals(begNum,endNum):
   for num in range(begNum.endNum): 
      res = realClassid(num)
      if res != False:
         #图集分类名称
         altasClassName = className(num)
         #图集分类文件路径
         filePath = Path + altasClassName
         #创建分类文件夹
         mkdir(filePath)
         #该分类的页面分页数量+1
         pageCount = altasClassPageCount(num)
         #获取该分类下所有图集信息
         for i in range(1,pageCount):
            pageAltasHtml(num,i)
            pagehtml =pageAltasHtml(num,i)
            for j in pagehtml.find_all('li'):
               pageAltasInfo(j)
               altasInfoJson =json.loads(str(pageAltasInfo(j)).replace('\'','"'))
               altasName = altasInfoJson['altasName']
               #创建分类文件夹内的图集文件夹
               altasFilePath = filePath + "\\"+altasName.rstrip()# rstrip去除文件结尾的空格
               mkdir(altasFilePath)
               #下载封面
               coverUrl = altasInfoJson['cover'] 
               coverPath = altasFilePath+"\\"+'cover.jpg'
               auto_down(coverUrl,coverPath)   
               #下载整个图集
               altasUrl =  altasInfoJson['altasUrl']
               imgDownLoad(altasUrl,altasFilePath)     
               print("已完成第：",str(altusCount)+"个相册", end="\r")
               altusCount+=1
# 程序入口
if __name__ == '__main__':
   beginNum = 0
   endNum= 204
   theardNum =50
   Gap = int(( endNum - beginNum )/theardNum) 
   GapRemainder = int(( endNum - beginNum )%theardNum) 
   threads = []
   for num in range(0,theardNum):
      theThread = myThread(beginNum + num*Gap, beginNum + (num+1)*Gap)
      theThread.start() 
      threads.append(theThread)
   if not GapRemainder == 0:
      theThread = myThread( endNum - GapRemainder, endNum  )
      theThread.start()
      threads.append(theThread)
   print('所有线程启动完毕')
   # 等待所有线程完成
   for t in threads:
      t.join()
   print ("所有任务已完成")
  

