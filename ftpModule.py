# -*- coding: utf-8 -*-
"""
Created on 2018年4月24日

@author: Simba
"""


import ftplib
import os
import time
import config.config as CONFIG


# 创建ftp链接，设置属性
def createFtpLink(ip, port, ftpDir, user, passwd, passiveVal):
    f = ftplib.FTP()
    f.connect(ip, port)
    f.login(user, passwd)
    f.set_pasv(passiveVal)
    f.cwd(ftpDir)
    #f.timeout = CONFIG.FTP_TIMEOUT
    return f


# 上传文件
def uploadFile(ftp, filePath):
    timeStr = str(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime()))
    print "%s pid:%s--file: %s has been uploaded." % (timeStr, os.getpid(), filePath)
    file_handler = open(filePath, "rb")
    ftp.storbinary("STOR %s" % os.path.basename(filePath), file_handler)
    file_handler.close()


#
