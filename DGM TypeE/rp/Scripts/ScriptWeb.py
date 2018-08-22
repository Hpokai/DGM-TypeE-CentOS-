#!/usr/bin/env python3
#coding=utf-8

from subprocess import check_output, CalledProcessError
from pathlib import Path
import time
import os

state = '1'

try:
    state = check_output(['sudo', 'cat', '/home/rp/.data_gather/WebSettings/SystemSettings.txt']).decode().strip()
except CalledProcessError:
    print('Exception handled: is ip init error')

print('state ', state)

if state == '2':
    print('2: change')
    path = '/home/rp/.data_gather/SysSettings/ipaddresschange.pyc'
    if Path(path).exists():
        try:
            ret = check_output(['python3', path])
        except CalledProcessError:
            print('Exception handled: is ip init error')
else:   #state is '1' or others:
    print('1: init')
    path = '/home/rp/.data_gather/SysSettings/ipaddressinit.pyc'
    if Path(path).exists():
        try:
            ret = check_output(['python3', path])
        except CalledProcessError:
            print('Exception handled: is ip init error')
