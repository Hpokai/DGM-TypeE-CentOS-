#!/usr/bin/env python3
#coding=utf-8

import os
import sys
import time
import base64
import subprocess
import logging
import datetime

from smb.SMBConnection import SMBConnection
from smb.base import SMBTimeout, NotConnectedError
from pathlib import Path
from subprocess import run, CalledProcessError


class CInfo:
    def __init__(self):
        self.item = ['ID', 'IP', 'DOMIN', 'PASSWORD', 'SERVER', 'CLIENT', 'FOLDER']
        self.single_machine = dict()
        self.center_server = dict()

        if not self.load_setting():
            raise IOError

    def load_setting(self):
        ret = False

        path = '/home/rp/.data_gather/WebSettings/web_FSDC.txt'
        if Path(path).exists():
            with open(path, 'r') as file:
                for i, f in enumerate(file):
                    if i < len(self.item):
                        self.single_machine.setdefault(self.item[i], base64.b64decode(f).decode('UTF-8'))
                    else:
                        self.center_server.setdefault(self.item[i-len(self.item)], base64.b64decode(f).decode('UTF-8'))
                ret = True

        return ret

class CSamba:
    def __str__(self):
        return 'CSamba: Modularize Samba connection.'

    def __init__(self):
        self.isConnect = False
        self.handle = None

    def connect(self, s_ip, s_id, password, client_name, server_name, domain):
        is_connect = False
        self.handle = SMBConnection(s_id, password, client_name, server_name, domain, use_ntlm_v2=True)
        try:
            is_connect = self.handle.connect(s_ip, 139)
        except:
            print('handle connect error')

        return is_connect

    def append_log(self, f_name, byte):
        with open('/var/log/dgmelog', 'a') as f:
            f.write('[{0:^24}] [{1:<15}]: [{2:>8}] bytes downloaded.\n'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f_name, byte))

    def download(self, folder):
        ret = True
        local_path = '/home/rp/TypeE'

        try:
            file_list = self.handle.listPath(folder, '/')
        except:
            ret = False
            print('list path error')
        else:
            for file in file_list:
                if not file.isDirectory:
                    local_filename = '{}/{}'.format(local_path, file.filename)
                    remote_filename = '/{}'.format(file.filename)

                    try:
                        is_exists = Path(local_filename).exists()
                    except:
                        print('Path file exists error')
                    else:
                        if is_exists:
                            #check local file size
                            f_size = Path(local_filename).stat().st_size
                            print('f_size = ', f_size)

                            if f_size > 0:
                            # print('{} exist.'.format(file.filename))
                                try:
                                    self.handle.deleteFiles(folder, remote_filename)
                                except:
                                    print('delete error(exists)')
                            else:
                                with open(local_filename, 'wb') as f:
                                    try:
                                        file_attr, file_size = self.handle.retrieveFile(folder, remote_filename, f)
                                        print('====Download Finished====\n{}\n{}'.format(file_attr, file_size))
                                    except:
                                        ret = False
                                        print('remote error')
                                        break
                                    else:
                                        self.append_log(file.filename, file_size)

                                #check local file size
                                try:
                                    f_size = Path(local_filename).stat().st_size
                                except FileNotFoundError as e:
                                    print('FileNotFoundError:', e)
                                else:
                                    if f_size > 0:
                                        try:
                                            self.handle.deleteFiles(folder, remote_filename)
                                        except:
                                            print('delete error')
                                    else:
                                        f_size = Path(local_filename).unlink()
                        else:
                            with open(local_filename, 'wb') as f:
                                try:
                                    file_attr, file_size = self.handle.retrieveFile(folder, remote_filename, f)
                                    print('====Download Finished====\n{}\n{}'.format(file_attr, file_size))
                                except:
                                    ret = False
                                    print('remote error')
                                    break
                                else:
                                    self.append_log(file.filename, file_size)

                            #check local file size
                            try:
                                f_size = Path(local_filename).stat().st_size
                            except FileNotFoundError as e:
                                print('FileNotFoundError:', e)
                            else:
                                if f_size > 0:
                                    try:
                                        self.handle.deleteFiles(folder, remote_filename)
                                    except:
                                        print('delete error')
                                else:
                                    f_size = Path(local_filename).unlink()

                        run(['touch', '/home/rp/.data_gather/Core/connectivity.pk'])

        return ret

    def close(self):
        self.handle.close()

def get_period_time():
    minute = 1
    second = 0
    path = '/home/rp/.data_gather/WebSettings/web_OtherInfo.txt'
    if Path(path).exists():
        with open(path, 'r', encoding='UTF-8') as f:
            minute = base64.b64decode(f.readline().strip()).decode('UTF-8')
            second = base64.b64decode(f.readline().strip()).decode('UTF-8')
            #print('{}:{}'.format(minute, second))

    period_time = int(minute)*60 + int(second)
    return period_time

if __name__ == '__main__':
    isConnectSMB = 0
    auth = False

    period_time = get_period_time()

    path = '/home/rp/.data_gather/Core/log'

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        handlers=[logging.FileHandler('{}/{}.log'.format(path, time.strftime('%Y%m%d_%H%M%S', time.localtime())), 'w', 'utf-8')]
                        )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s'))
    logging.getLogger('').addHandler(console)

    # get authentication
    path = '/home/rp/.data_gather/WebSettings/web_au.ref'
    if Path(path).exists():
        with open(path, 'r', encoding='UTF-8') as f:
            if f.readline()[0:-1] == 'True':
                auth = True

    auth = True
    while 1:
        if not auth:
            logging.info('[auth] NOT Authorized...')
        else:
            logging.info('[auth] Authorized...')
            try:
                # print('[Init][{}] Load Settings...'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))
                logging.info('[Init] Load Settings...')
                info = CInfo()
            except IOError:
                # print('[Init][{}] Except:  Load setting Error!...'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))
                logging.info('[Init] Except:  Load setting Error!...')
            else:
                # print('[Init][{}] Connect to Controller with SMB...'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))
                logging.info('[Init] Connect to Controller with SMB...')
                csmb = CSamba()
                try:
                    ret = csmb.connect(
                        info.single_machine['IP'],
                        info.single_machine['ID'],
                        info.single_machine['PASSWORD'],
                        info.single_machine['CLIENT'],
                        info.single_machine['SERVER'],
                        info.single_machine['DOMIN']
                    )
                except OSError:
                    print('disconnect!')
                    logging.info('[Init] SMB Client DISconnect!')
                except NotConnectedError:
                    print('NotConnectedError!')
                    logging.info('[Init] SMB Client NotConnectedError!')
                else:
                    if ret:
                        isConnectSMB = 1
                        # print('connect!')
                        logging.info('[Init] SMB Client Connected!')
                    else:
                        isConnectSMB = 0
                        logging.info('[Init] SMB Client DISConnected!')

                while isConnectSMB:
                    try:
                        # print('[SMB][{}] Start to download file...'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))
                        logging.info('[SMB] Start to download file...')
                        if csmb.download(info.single_machine['FOLDER']):
                            # print('done!')
                            logging.info('[SMB] File Downloaded!!')
                        else:
                            isConnectSMB = 0
                    except SMBTimeout:
                        isConnectSMB = 0
                        # print('SMBTimeout!')
                        logging.info('[SMB] SMB Connect Timeout')
                    time.sleep(period_time)

                csmb.close()
                del csmb
                del info

        time.sleep(5)
