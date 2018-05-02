# -*- coding: utf-8 -*-
'''
Created on 2018年4月24日

@author: Simba
'''

import os
import logService.logService as logService
import logging
import ftpModule
import multiprocessing
import time
import exception.myException as MYEXCEPTION
import math
import sys
import datetime
import config.config as CONFIG
import tokenBucket


# 获得所有图片的绝对路径列表
def getImagesPathList(imagesDir):
    imagesList = os.listdir(imagesDir)
    imagePathList = []
    logging.info("Start to get imagePathList.")
    for i in imagesList:
        imagePathList.append(os.path.join(imagesDir, i))
    logging.info("Get imagePathList completed.")
    return imagePathList


# 将列表分为m份
def chunks(arr, m):
    n = int(math.ceil(len(arr) / float(m)))
    return [arr[i:i + n] for i in range(0, len(arr), n)]


# ftp上传文件
def uploadFileByFtp(iTup):
    # ip, port, ftpDir, user, passwd, passiveVal, fileList
    count = 0
    firstTime = datetime.datetime.now()
    ftp = ftpModule.createFtpLink(iTup[0], iTup[1], iTup[2], iTup[3], iTup[4], iTup[5])
    # logService.initLogging()
    pidCount = 0
    for i in iTup[6]:
        nowtime = datetime.datetime.now()
        if 100 <= (nowtime - firstTime).seconds:
            ftp.quit()
            ftp = ftpModule.createFtpLink(iTup[0], iTup[1], iTup[2], iTup[3], iTup[4], iTup[5])
            firstTime = datetime.datetime.now()
            count += 1

        ftpModule.uploadFile(ftp, i)
        timeStr = str(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime()))
        print "%s pid:%s--file: %s has been uploaded." % (timeStr, os.getpid(), i)
        infoStr = "%s pid:%s--file: %s has been uploaded." % (timeStr, os.getpid(), i)
        logging.info(infoStr)
        pidCount = pidCount + 1
    ftp.quit()
    countDic = {}
    countDic["reconnectNum"] = count
    countDic["uploadNum"] = pidCount
    return countDic
    # logService.destoryLogging()


# 不重连
def newUploadFileByFtp(iTup):
    # ip, port, ftpDir, user, passwd, passiveVal, fileList
    ftp = ftpModule.createFtpLink(iTup[0], iTup[1], iTup[2], iTup[3], iTup[4], iTup[5])
    # logService.initLogging()
    uploadCount = 0
    discardCount = 0
    # 限流，如果令牌桶中有令牌，则上传图片，如果没有，则丢弃图片
    # 每秒往桶中存放3个令牌
    token = tokenBucket.TokenBucket(3, 100000)
    token._current_amount = 1000
    for i in iTup[6]:
        if token.consume(1):
            ftpModule.uploadFile(ftp, i)
            timeStr = str(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime()))
            print "%s pid:%s--file: %s has been uploaded." % (timeStr, os.getpid(), i)
            infoStr = "%s pid:%s--file: %s has been uploaded." % (timeStr, os.getpid(), i)
            logging.info(infoStr)
            uploadCount = uploadCount + 1
        else:
            discardCount = discardCount + 1
            print time.time()
    ftp.quit()
    countDic = {}
    countDic["uploadNum"] = uploadCount
    countDic["discardNum"] = discardCount
    return countDic


# 检查ftp连接状态
def checkFtpStatus(ftp):
    if ftp.voidcmd("NOOP") == "200 OK":
        return True
    else:
        return False


# 子进程异常处理
def errInfo(e):
    raise

def bucketUploadFileByFtp(iTup):
    # ip, port, ftpDir, user, passwd, passiveVal, fileList
    #ftp = ftpModule.createFtpLink(iTup[0], iTup[1], iTup[2], iTup[3], iTup[4], iTup[5])
    # logService.initLogging()
    uploadCount = 0
    # 限流，如果令牌桶中有令牌，则上传图片，如果没有，则空循环
    # 每秒往桶中存放3个令牌
    token = tokenBucket.TokenBucket(3, 100000)
    token._current_amount = 1
    index = 0

    try:
        while index < len(iTup[6]):
            if token.consume(1):
                ftp = ftpModule.createFtpLink(iTup[0], iTup[1], iTup[2], iTup[3], iTup[4], iTup[5])
                ftpModule.uploadFile(ftp, iTup[6][index])
                timeStr = str(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime()))
                print "%s pid:%s--file: %s has been uploaded." % (timeStr, os.getpid(), iTup[6][index])
                uploadCount = uploadCount + 1
                index = index + 1
                ftp.quit()
        #ftp.quit()
    except Exception, e:
        raise MYEXCEPTION.MyException(e)
    countDic = {}
    nameStr = "pid:" + str(os.getpid)
    countDic[nameStr] = uploadCount
    return countDic


#
def run():
    parameterList = sys.argv

    # 获得进程数
    numOfPiece = parameterList[1]

    originalFilePathList = getImagesPathList(r"/home/ubuntu/simba/newImages/newImages")
    #originalFilePathList = getImagesPathList(r"/opt/ladder/simba/images/newImages")
    #originalFilePathList = getImagesPathList(r"F:\newImages\newImages")

    superFilePathList = chunks(originalFilePathList, numOfPiece)

    imagesCount = 0
    for i in superFilePathList:
        imagesCount = imagesCount + len(i)



    pool = multiprocessing.Pool(processes=int(numOfPiece))
    paraList = []
    for i in superFilePathList:
        iTup = ("47.104.253.105", "2121", "test", "test", "test", True, i)
        #iTup = ("47.105.36.177", "21", "aaa", "ftpuser", "aivivi", True, i)
        paraList.append(iTup)

    startTime = time.time()
    resultList = []
    try:
        for i in paraList:

            #resultList.append(pool.apply_async(uploadFileByFtp, args=(i,)))
            resultList.append(pool.apply_async(bucketUploadFileByFtp, args=(i,)))
            #pool.apply_async(newUploadFileByFtp, args=(i,))
        # resultList.append(pool.map(bucketUploadFileByFtp, paraList))
    except Exception, e:
        # raise MYEXCEPTION.MyException(e)
        print e
    finally:
        pool.close()
        pool.join()
        endTime = time.time()
        print "end"
        print startTime
        print endTime
    print "original number: %d" % imagesCount

    resInfo = []

    for i in resultList:
        info = i.get()
        resInfo.append(info)
    for j in resInfo:
        print j



if __name__ == '__main__':
    # logService.initLogging()
    '''
    :param 脚本本身
    :param 进程数
    '''
    run()
    # logService.destoryLogging()