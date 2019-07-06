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
import threading
import socket
import time
import MySQLdb
mysqlHost = "localhost"
mysqlUser = "root"
mysqlPwd = "root"
mysqlTabel = "tujidao2"
http = urllib3.PoolManager()
headers = {
"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,\
   image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
"Accept-Encoding": "gzip, deflate",
"Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
"Cache-Control": "max-age=0",
"Connection": "keep-alive",
"Cookie": "UM_distinctid=16b7cf230ed4c6-0cd2791b0bfde6-e343166-1fa400-16b7cf230eebe6;\
          CNZZDATA1257039673=283923358-1561169374-%7C1561859928; \
          ASPSESSIONIDQCTBBDQS=ONBPONFDGAOLLFPFBFKFDNPF; 7Dw1Tw3Bh2Mvfr=; \
          7Dw1Tw3Bh2Mvu%5Fleixing=3; 7Dw1Tw3Bh2Mvu%5Fpw=c8534b0ccc48128b; \
          7Dw1Tw3Bh2Mvu%5Fusername=sdoshanxi865; 7Dw1Tw3Bh2Mvu%5Fid=89348",
"Host": "www.tujidao.com",
"Referer": "http://www.tujidao.com/u/?action=login",
"Upgrade-Insecure-Requests": 1,
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
   AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"  
}
# 目标网站地址
webUrl = "http://www.tujidao.com"

#继承父类threading.Thread 并重写__init__方法和 run方法
class myThread(threading.Thread):
    def __init__(self,functionName,begNum,endNum):
        threading.Thread.__init__(self)
        self.functionName = functionName
        self.begNum = begNum
        self.endNum = endNum
    def run(self):
         if self.functionName == "AltalsAndPhoto":
            AltalsAndPhoto(self.begNum,self.endNum)
         elif self.functionName == "GrilInfo":
            GrilInfo(self.begNum,self.endNum)
         elif self.functionName == "ClassInfo":
            ClassInfo(self.begNum,self.endNum)
         elif self.functionName == "OrgInfo":
            OrgInfo(self.begNum,self.endNum)
         else:
            print("抱歉！没有找到该多线程函数！") 
    def __del__(self):
         if self.functionName == "AltalsAndPhoto":
             print("图集信息采集完毕") 
         elif self.functionName == "GrilInfo":
             print("美女信息采集完毕") 
         elif self.functionName == "ClassInfo":
            print("图集分类采集完毕") 
         elif self.functionName == "OrgInfo":
             print("机构组织采集完毕") 
         else:
            print("抱歉！没有找到该多线程函数！") 

# 获取存在的图集名称 
def realClassid(classId):
   url = webUrl +'/s/?id='+str(classId)
   try:
      r = http.request('Get',url,headers=headers)
   except IOError:
      print('', end="\r")
   soup = BeautifulSoup(r.data.decode("utf8"), "lxml")
   legend = soup.find('div',class_='hezi').find('legend').text#图集分类名称
   if legend != "临时图集":
      if legend != "图集":
        return legend
   return False

# 图片下载速度
def Schedule(blocknum,blocksize,totalsize):
    per = 100.0 * blocknum * blocksize / totalsize
    if per > 100 :
        per = 100
   # print('当前下载进度：%d'%per,end="\r")

# 下载单张图片
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
   except IOError:
      print('', end="\r")
   soup = BeautifulSoup(r.data.decode("utf8"), "lxml")
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

# 获取图集分类总的分页数量
def altasClassPageCount(altasClassId):
   url = webUrl +'/s/?id='+str(altasClassId)
   try:
      r=http.request('Get',url,headers=headers)
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
   except IOError:
      print('', end="\r")
   soup = BeautifulSoup(r.data.decode("utf8"), "lxml")
   html = soup.find('div',class_='hezi')
   return html

# 获取传来的li的HTML信息，解析成json 
def pageAltasInfo(lihtml):
   p = lihtml.find_all('p')
   altasInfo = {
   #图集名称
   "altasName":p[3].a.text.replace('\\',' ').replace('\\',' ').\
               replace('/',' ').replace(':',' ').replace('*',' ').\
               replace('?',' ').replace('<',' ').replace('>',' ').\
               replace('|',' ').replace('"',' '), 
   "photoCount": lihtml.find('span').text, #图片数量
   "altasUrl":webUrl+p[3].a['href'], #图集地址
   "cover":lihtml.find('a').img['data-original'],#图集封面
   "organName":p[0].a.text,#图集发行机构名称
   "organUrl":webUrl+ p[0].a['href']
      }
   return altasInfo

#  获取该图集下所有的图片标签
def trueAltalsUrl(altalsId):
   url = webUrl +'/a/?id='+str(altalsId)
   try:
      r = http.request('Get',url,headers=headers)
   except IOError:
      print('', end="\r")
   try:      
      soup = BeautifulSoup(r.data.decode("utf8"), "lxml")
   except:
      return
   else:
      html = soup.find('div',class_='tuji')
      if not html:
         return
      altalsName = html.find('h1').text.replace('\\',' ').replace('\\',' ').\
                   replace('/',' ').replace(':',' ').replace('*',' ').replace('?',' ').\
                   replace('<',' ').replace('>',' ').replace('|',' ').replace('"',' ')
      p = html.find_all('p')
      orgid = str(p[0].a['href']).replace('/x/?id=','')
      altalsCount = str(p[2].text.replace('图片数量：','').replace('P',''))   
      models = []
      classs = []
      grilIds = ''
      classIds=''
      for m in p[1].find_all('a'):
          h = m['href'].replace('/t/?id=','')
          models.append(h)
      for c in p[3].find_all('a'):
          h = c['href'].replace('/s/?id=','')
          classs.append(h)
      for m in models:
         grilIds += m +','
      for c in classs:
         classIds += c +','
      grilIds = grilIds.rstrip(',')
      classIds = classIds.rstrip(',')
      if not grilIds:
         grilIds = '-1'
      try:
         saveAltals(altalsId,orgid,classIds,grilIds,altalsName,altalsCount)
         try:
            imgHtml = soup.find('div',id='kbox').find_all('img')
            imgs=[]
            for k in imgHtml:
               imgUrl = k['data-src']
               imgs.append(imgUrl)        
            return imgs
         except IOError:
             return False  
      except IOError:
         return False

#  在数据库中建立要用到的5张表
def CreateTabel():
    # 图集信息表
   altalsTabelExist ="DROP TABLE IF EXISTS `altals`;"
   altalsTabel = """CREATE TABLE `altals`  (
                     `id` int(11) NOT NULL,
                     `orgid` int(11) NULL DEFAULT NULL,
                     `cids` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
                     `grilIds` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '-1：为不知名美女',
                     `name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
                     `count` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
                     PRIMARY KEY (`id`) USING BTREE) ENGINE = MyISAM AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;
                  """
   # 图片信息表
   photoTabelExist ="DROP TABLE IF EXISTS `photo`;"
   photoTabel="""CREATE TABLE `photo`  (
                  `id` int(11) NOT NULL AUTO_INCREMENT,
                  `aid` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
                  `name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
                  `url` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
                  PRIMARY KEY (`id`) USING BTREE) ENGINE = MyISAM AUTO_INCREMENT = 8049 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;
               """
   # 组织信息表
   orgnationTabelExist ="DROP TABLE IF EXISTS `orgnation`;"
   orgnationTabel=""" CREATE TABLE `orgnation`  (
                     `id` int(11) NOT NULL,
                     `orgName` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '机构名称',
                     PRIMARY KEY (`id`) USING BTREE) ENGINE = MyISAM AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;
                  """
   # 美女信息表
   girlTabelExist ="DROP TABLE IF EXISTS `girl`;"
   girlTabel="""CREATE TABLE `girl`  (
               `id` int(11) NOT NULL,
               `grilName` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '美女姓名',
               PRIMARY KEY (`id`) USING BTREE) ENGINE = MyISAM AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;
            """
   # 图集分类信息表
   classTabelExist ="DROP TABLE IF EXISTS `class`;"
   classTabel="""CREATE TABLE `class`  (
                  `id` int(11) NOT NULL,
                  `className` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
                  PRIMARY KEY (`id`) USING BTREE) ENGINE = MyISAM AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;
               """
   mySqlTablesExist= [altalsTabelExist,photoTabelExist,orgnationTabelExist,girlTabelExist,classTabelExist]
   mySqlTables = [altalsTabel,photoTabel,orgnationTabel,girlTabel,classTabel]
   for sql in mySqlTablesExist:
      db = MySQLdb.connect(mysqlHost,mysqlUser,mysqlPwd,mysqlTabel,use_unicode=1, charset='utf8')
      cursor = db.cursor() 
      try:
            cursor.execute(sql)
      except:
            db.rollback() 
            return
      db.close()
   for sql in mySqlTables:
      db = MySQLdb.connect(mysqlHost,mysqlUser,mysqlPwd,mysqlTabel,use_unicode=1, charset='utf8')
      cursor = db.cursor()
      try:     
            cursor.execute(sql)  
            db.commit()  
      except:  
            db.rollback()
      db.close() 

#  保存相册信息到数据库
def saveAltals(id,orgid,cids,grilIds,name,count): 
      sql = "INSERT INTO `altals` (`id`,`orgid`,`cids`,`grilIds`,`name`,`count`)\
             VALUES (%i,%i,'%s','%s','%s','%s')"%(int(id),int(orgid),cids,grilIds,name,count)
      db = MySQLdb.connect(mysqlHost,mysqlUser,mysqlPwd,mysqlTabel,use_unicode=1, charset='utf8')
      cursor = db.cursor()
      try:     
         cursor.execute(sql)  
         db.commit()  
      except:  
         db.rollback()
      db.close()  

#  保存图片信息到数据库
def savePhotos(aid,name,url): 
      sql = "INSERT INTO `photo` (`aid`,`name`,`url`) VALUES (%i,'%s','%s')"%(int(aid),name,url)
      db = MySQLdb.connect(mysqlHost,mysqlUser,mysqlPwd,mysqlTabel,use_unicode=1, charset='utf8')
      cursor = db.cursor()
      try:     
         cursor.execute(sql)  
         db.commit()  
      except:  
         db.rollback()
      db.close()  

# 判断是为美女姓名
def realgrilid(grilId):
   url = webUrl +'/t/?id='+str(grilId)
   r = http.request('Get',url,headers=headers)
   soup = BeautifulSoup(r.data.decode("utf8"), "lxml")
   legend = soup.find('div',class_='hezi').find('legend').text#图集分类名称
   if legend != "临时图集":
      if legend != "图集":
         legend =str(legend).lstrip('图集')
         return legend
   return False

# 获取美女姓名 
def getGrilName(grilid):
   url = webUrl +'/t/?id='+str(grilid)
   try:
      r = http.request('Get',url,headers=headers)
   except IOError:
      print('', end="\r")
   soup = BeautifulSoup(r.data.decode("utf8"), "lxml")
   legend = soup.find('div',class_='hezi').find('legend').text#图集分类名称
   return legend

# 添加美女名称到数据库
def AddGrilName(id,classname): 
      sql = "INSERT INTO `girl` (`id`,`grilName`) VALUES (%i,'%s')"%(int(id),classname)
      db = MySQLdb.connect(mysqlHost,mysqlUser,mysqlPwd,mysqlTabel,use_unicode=1, charset='utf8')
      cursor = db.cursor()
      try:  
         cursor.execute(sql)  
         db.commit()  
      except:  
         db.rollback()  
      db.close()

# 获取图集分类名称 
def className(classId):
   url = webUrl +'/s/?id='+str(classId)
   try:
      r = http.request('Get',url,headers=headers)
      time.sleep(0.1)
   except IOError:
      print('')
   soup = BeautifulSoup(r.data.decode("utf8"), "lxml")
   legend = soup.find('div',class_='hezi').find('legend').text#图集分类名称
   return legend

# 添加图集分类 
def AddAltalsClass(id,classname): 
      sql = "INSERT INTO `class` (`id`,`className`) VALUES (%i,'%s')"%(int(id),classname)
      db = MySQLdb.connect(mysqlHost,mysqlUser,mysqlPwd,mysqlTabel,use_unicode=1, charset='utf8')
      cursor = db.cursor()
      try:  
         cursor.execute(sql)  
         db.commit()  
      except:  
         db.rollback()  
      db.close()

# 获取图集所属机构名称
def getOrgName(orgid):
   url = webUrl +'/x/?id='+str(orgid)
   try:
      r = http.request('Get',url,headers=headers)
   except IOError:
      print('', end="\r")
   soup = BeautifulSoup(r.data.decode("utf8"), "lxml")
   legend = soup.find('div',class_='hezi').find('legend').text#图集分类名称
   if legend !='图集':
      if legend !='临时 图集':
         return legend.replace(' 图集','').replace('图集','')
   return False

# 添加机构信息添加到数据库
def AddorglName(id,orgName): 
      sql = "INSERT INTO `orgnation` (`id`,`orgName`) VALUES (%i,'%s')"%(int(id),orgName)
      db = MySQLdb.connect(mysqlHost,mysqlUser,mysqlPwd,mysqlTabel,use_unicode=1, charset='utf8')
      cursor = db.cursor()
      try:  
         cursor.execute(sql)  
         db.commit()  
      except:  
         db.rollback() 
      db.close()

# 多线程函数——采集图集信息（altals表）  和  图集对应图片信息（photo表）
def AltalsAndPhoto(begin,end):
   for num in range(begin,end): 
      res = trueAltalsUrl(num)#获取图集下的所有图片标签
      if res:
         for img in res:
            imgname = img.split('/a/1/')[1].split('/')[1]
            savePhotos(num,imgname,img)#将图片信息存入到数据库中

# 多线程函数——采集美女姓名（gril表）
def GrilInfo(begin,end):
  for num in range(begin,end): 
   grilName =str(getGrilName(num)).replace('图集','') 
   AddGrilName(num,grilName)

# 多线程函数——采集图集分类信息（class表） 
def ClassInfo(begin,end):
   for num in range(begin,end):
      res = realClassid(num)
      if res !=False:
         res =res.replace('图集','') 
         AddAltalsClass(num,res)
# 多线程函数——采集平台机构信息(orgnation)
def OrgInfo(begin,end):
   for num in range(begin,end): 
      orgName =getOrgName(num)
      if  orgName:
         AddorglName(num,orgName)
     

#程序入口
#  1.图集范围：   经过对网站的分析，发现图集的id编号是在 299——28200这个区间内存在数据
#  2.机构范围：   经过对网站的分析，发现机构的id编号是在 1——100这个区间内存在数据
#  3.分类范围：   经过对网站的分析，发现分类的id编号是在 1——210这个区间内存在数据
#  4.美女范围：   经过对网站的分析，发现分类的id编号是在 1——5130这个区间内存在数据
if __name__ == '__main__':

   # 开始编号 与 结束编号
   altalsBegNum = 299 
   altalsEndNum = 28200 
   orgBegNum = 1
   orgEndNum = 100     
   classBegNum = 1
   classEndNum = 210   
   grilBegNum = 1  
   grilEndNum = 5130

   # 需要开启的线程数量
   altalsThread = 50
   orgThread = 10      
   classThread = 50   
   grilThread = 50      
   
   # 数据间隔  与 结尾余数
   altalsGap = int(( altalsEndNum - altalsBegNum )/altalsThread) 
   altalsGapRemainder = int(( altalsEndNum - altalsBegNum )%altalsThread) 
   orgGap = int(( orgEndNum - orgBegNum )/orgThread)
   orgGapRemainder = int(( orgEndNum - orgBegNum )%orgThread)      
   classGap = int(( classEndNum - classBegNum)/classThread)
   classGapRemainder = int(( classEndNum - classBegNum)%classThread)  
   grilGap = int(( grilEndNum - grilBegNum)/grilThread)
   grilGapRemainder = int(( grilEndNum - grilBegNum)%grilThread)     

   print ('图集采集线程数：',altalsThread,'\n数据间隔：',altalsGap,'\n余数：',altalsGapRemainder)
   print('\n')
   print ('机构采集线程数：',orgThread,'\n数据间隔：',orgGap,'\n余数：',orgGapRemainder)
   print('\n')
   print ('分类采集线程数：',classThread,'\n数据间隔：',classGap,'\n 余数：',classGapRemainder)
   print('\n')
   print ('美女采集线程数：',grilThread,'\n数据间隔：',grilGap,'\n余数：',grilGapRemainder)
   print('\n')

   CreateTabel()   #首先创建数据库
   threads = []
   for num in range(0,altalsThread):
      theThread = myThread('AltalsAndPhoto',altalsBegNum + num*altalsGap, altalsBegNum + (num+1)*altalsGap)
      theThread.start() # 开启新线程
      threads.append(theThread)# 添加线程到线程列表
   if not altalsGapRemainder == 0:
      theThread = myThread('AltalsAndPhoto', altalsEndNum - altalsGapRemainder, altalsEndNum )
      theThread.start()
      threads.append(theThread)

   for num in range(0,altalsThread):
      theThread = myThread('GrilInfo',grilBegNum + num*grilGap, grilBegNum + (num+1)*grilGap )
      theThread.start() 
      threads.append(theThread)
   if not altalsGapRemainder == 0:
      theThread = myThread('GrilInfo',grilEndNum - grilGapRemainder, grilEndNum )
      theThread.start()
      threads.append(theThread)

   for num in range(0,altalsThread):
      theThread = myThread('ClassInfo',classBegNum + num*classGap, classBegNum + (num+1)*classGap)
      theThread.start() 
      threads.append(theThread)
   if not altalsGapRemainder == 0:
      theThread = myThread('ClassInfo', classEndNum - classGapRemainder, classEndNum)
      theThread.start()
      threads.append(theThread)
   
   for num in range(0,altalsThread):
      theThread = myThread('OrgInfo',orgBegNum + num*orgGap, orgBegNum + (num+1)*orgGap)
      theThread.start() 
      threads.append(theThread)
   if not altalsGapRemainder == 0:
      theThread = myThread('OrgInfo', orgEndNum - orgGapRemainder, orgEndNum  )
      theThread.start()
      threads.append(theThread)

   print('所有线程启动完毕')
   # 等待所有线程完成
   for t in threads:
      t.join()
   print ("所有任务已完成")
  