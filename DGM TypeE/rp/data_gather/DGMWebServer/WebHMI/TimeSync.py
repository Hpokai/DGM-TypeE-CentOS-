#!/usr/bin/env python3
#coding=utf-8

import subprocess
import base64
from pathlib import Path

def check_local_time():
    #check local time
    try:
        output = subprocess.check_output(['date'])
    except subprocess.CalledProcessError:
        print('Exception handled')
    print('[Check local time] {}'.format(output.decode()))

def time_sync():
    check_local_time()

    #get remote time
    path = '/home/rp/.data_gather/WebSettings/web_FSDC.txt'
    if Path(path).exists():
        with open(path, 'r', encoding='UTF-8') as f:
            remote_server_name = base64.b64decode(f.readlines()[1].strip()).decode('UTF-8')

    print('[Remote server name] {}'.format(remote_server_name))

    try:
        remote_time = subprocess.check_output(['sudo', 'net', 'time', '-S', remote_server_name])
    except subprocess.CalledProcessError:
        print('Exception handled: remote server name [{}] error.'.format(remote_server_name))
    else:
        print('[Get remote time] {}'.format(remote_time.decode()))

        #set local time
        try:
            output = subprocess.check_output(['sudo', 'date', '-s', remote_time])
        except subprocess.CalledProcessError:
            print('Exception handled')
        else:
            print('[Set local time] {}'.format(output.decode()))

            check_local_time()

if __name__ == '__main__':
    time_sync()
