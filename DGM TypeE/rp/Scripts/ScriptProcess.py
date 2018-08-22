#!/usr/bin/env python3
#coding=utf-8

from subprocess import check_output, CalledProcessError
from pathlib import Path
import time
import os

# before main program, time sync first.
path = '/home/rp/.data_gather/DGMWebServer/WebHMI/TimeSync.pyc'
if Path(path).exists():
    try:
        ret = check_output(['python3', path])
    except CalledProcessError:
        print('Exception handled: is ip init error')

time.sleep(0.5)
# run main program
path = '/home/rp/.data_gather/Core/process.pyc'
if Path(path).exists():
    try:
        ret = check_output(['python3', path])
    except CalledProcessError:
        print('Exception handled: is ip init error')
