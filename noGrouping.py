# -*- coding: utf-8 -*-
"""
Created on 2018年4月28日

@author: Simba
"""


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


# # ftp上传多文件
# def uploadManyFiles(ftp, fileList):

def uploadFileTup(Tup):
    print "========"
    #print Tup
    print "%s-------%s" % (Tup, os.getpid())
    #ftpModule.uploadFile(Tup[0], Tup[1])



ftp = ftpModule.createFtpLink("47.104.253.105", "2121", "test", "test", "test", True)



def run():
    parameterList = sys.argv

    # 获得进程数
    numOfProcess = parameterList[1]

    filePathList = getImagesPathList(r"F:\newImages\newImages")

    pool = multiprocessing.Pool(processes=int(numOfProcess))
    # for i in range(100):
    #     pool.apply_async(ftpModule.uploadFile(), args=(ftp, ))
    print len(filePathList)

    countNum = 0
    tupList = []
    for i in filePathList:
        tup = (ftp, i)
        tupList.append(tup)

    for j in filePathList:



        pool.apply_async(uploadFileTup, args=(j,))
        # timeStr = str(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime()))
        # print "%s pid:%s--file: %s has been uploaded." % (timeStr, os.getpid(), i)
        # countNum = countNum + 1
    pool.close()
    pool.join()
    ftp.quit()
    print countNum




if __name__ == '__main__':
    # logService.initLogging()
    '''
    :param 脚本本身
    :param 进程数
    '''
    run()
    # logService.destoryLogging()