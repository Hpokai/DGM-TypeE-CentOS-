#!/usr/bin/env python3
#coding=utf-8

from subprocess import check_output, CalledProcessError
from pathlib import Path
import time
import os

path = '/home/rp/.data_gather/SysSettings/RerunProcess.sh'
if Path(path).exists():
    # os.system('{}'.format(path))

    try:
        ret = check_output(['{}'.format(path)])
    except CalledProcessError as err:
        print('CalledProcessError:', err)
