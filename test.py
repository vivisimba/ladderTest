# -*- coding: utf-8 -*-
"""
Created on 2018/4/28

@author: Simba
"""


import os
import pickle

import multiprocessing
import time
import ftpModule

def check(num):
    print num/0


def some():
    pool = multiprocessing.Pool(processes=3)

    for i in range(10,20):
        pool.apply_async(check, (i,))

# "47.105.36.177", "21", "ftpuser", "aivivi"

ftp = ftpModule.createFtpLink("47.105.36.177", "21", "aaa", "ftpuser", "aivivi", True,)
ftp.quit()