#!/usr/bin/env python3
#coding=utf-8

from subprocess import call, check_output, CalledProcessError
from pathlib import Path
import base64
import os
import time

def get_network_name():
    eth0 = ''
    eth1 = ''
    for lsdir in os.listdir('/sys/class/net/'):
        try:
            lsdir.index('enx')
        except ValueError:
            pass
        else:
            try:
                lsdir.index('enxb827eb')
            except ValueError:
                eth1 = lsdir
            else:
                eth0 = lsdir
    return (eth0, eth1)

if __name__ == '__main__':
    item = ['eth0_ip', 'eth0_mask', 'eth1_ip', 'eth1_mask', 'eth0_broad', 'eth1_broad']
    network = dict().fromkeys(item)
    network_split = dict().fromkeys(item)

    path = '/home/rp/.data_gather/WebSettings/web_InitIPInfo.txt'
    if Path(path).exists():
        with open(path, 'r', encoding='UTF-8') as f:
            for index, data in enumerate(f.readlines()):
                network[item[index]] = base64.b64decode(data.strip()).decode('UTF-8')

        for key, value in network.items():
            try:
                network_split[key] = value.split('.')
            except AttributeError:
                network_split[key] = list()

        #set broadcast
        for i, key in enumerate(zip(network_split['eth0_mask'], network_split['eth1_mask'])):
            if key[0] == '0':
                network_split['eth0_broad'].append('255')
            else:
                network_split['eth0_broad'].append(network_split['eth0_ip'][i])
            if key[1] == '0':
                network_split['eth1_broad'].append('255')
            else:
                network_split['eth1_broad'].append(network_split['eth1_ip'][i])

        network['eth0_broad'] = '.'.join(network_split['eth0_broad'])
        network['eth1_broad'] = '.'.join(network_split['eth1_broad'])

        # eth0, eth1 = get_network_name()   # for ubuntu new eth named rule

        # get old ip & mask
        try:
            old_eth0 = check_output(['ip', 'addr', 'show', 'eth0']).decode().split(' ')
        except CalledProcessError as err:
            print('CalledProcessError:', err)
        else:
            old_eth0 = old_eth0[old_eth0.index('inet')+1]
            # print(old_eth0)
        try:
            old_eth1 = check_output(['ip', 'addr', 'show', 'eth1']).decode().split(' ')
        except CalledProcessError as err:
            print('CalledProcessError:', err)
        else:
            old_eth1 = old_eth1[old_eth1.index('inet')+1]
            # print(old_eth1)

        #ip addr add 192.168.0.77/24 broadcast 192.168.0.255 dev eth0
        try:
            ret = check_output(['sudo', 'ip', 'addr', 'add', '{}/{}'.format(network['eth0_ip'],
                                network['eth0_mask']), 'broadcast', network['eth0_broad'], 'dev', 'eth0'])
        except CalledProcessError as err:
            print('CalledProcessError:', err)
        else:
            try:
                ret = check_output(['sudo', 'ip', 'addr', 'del', old_eth0, 'dev', 'eth0'])
            except CalledProcessError as err:
                print('CalledProcessError:', err)

        try:
            ret = check_output(['sudo', 'ip', 'addr', 'add', '{}/{}'.format(network['eth1_ip'],
                                network['eth1_mask']), 'broadcast', network['eth1_broad'], 'dev', 'eth1'])
        except CalledProcessError as err:
            print('CalledProcessError:', err)
        else:
            try:
                ret = check_output(['sudo', 'ip', 'addr', 'del', old_eth1, 'dev', 'eth1'])
            except CalledProcessError as err:
                print('CalledProcessError:', err)

        # especially, gateway needs to be deleted.
        try:
            ret = check_output(['sudo', 'route', 'del', 'default'])
        except CalledProcessError as err:
            print('CalledProcessError:', err)

        path = '/home/rp/.data_gather/DGMWebServer/manage.py'
        if Path(path).exists():
            try:
                ret = check_output(['python3', path, 'runserver', '{}:80'.format(network['eth0_ip'])])
            except CalledProcessError as err:
                print('CalledProcessError:', err)
