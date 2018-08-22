#!/usr/bin/env python3
#coding=utf-8

from subprocess import check_output, CalledProcessError
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

def get_ip_setting_state():
    try:
        is_init = check_output(['sudo', 'cat', '/home/rp/.data_gather/WebSettings/SystemSettings.txt']).decode().strip()
    except CalledProcessError:
        is_init = '1'
        print('Exception handled: is ip init error')
    # print('is_init = {}'.format(is_init))
    return is_init

def set_eth_ip(dev, eth_ip, eth_mask, eth_broad):
    is_exception = True
    # get old ip & mask
    try:
        old_eth = check_output(['ip', 'addr', 'show', dev]).decode().split(' ')
    except CalledProcessError as err:
        print('CalledProcessError:', err)
    else:
        try:
            old_eth = old_eth[old_eth.index('inet')+1]
        except:
            old_eth = None
        #print(old_eth)
    try:
        ret = check_output(['sudo', 'ip', 'addr', 'add', '{}/{}'.format(eth_ip, eth_mask), 'broadcast', eth_broad, 'dev', dev])
    except CalledProcessError as err:
        is_exception = False
        print('CalledProcessError:', err)
    else:
        if old_eth is not None:
            try:
                ret = check_output(['sudo', 'ip', 'addr', 'del', old_eth, 'dev', dev])
            except CalledProcessError as err:
                print('CalledProcessError:', err)
    return is_exception

def set_eth_gw(dev, eth_gateway):
    try:
        ret = check_output(['sudo', 'route', 'add', 'default', 'gw', eth_gateway, dev])
    except CalledProcessError as err:
        print('CalledProcessError:', err)


if __name__ == '__main__':
    item = ['eth0_ip', 'eth0_mask', 'eth1_ip', 'eth1_mask', 'eth1_gateway', 'eth0_broad', 'eth1_broad']
    network = dict().fromkeys(item)
    network_split = dict().fromkeys(item)

    is_init = get_ip_setting_state()
    if is_init == '1':
        path = '/home/rp/.data_gather/WebSettings/web_InitIPInfo.txt'
    else:
        path = '/home/rp/.data_gather/WebSettings/web_ChangedIPInfo.txt'

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

        # eth0 for EQ, eth1 for IT
        # eth0, eth1 = get_network_name()
        eth0, eth1 = 'eth0', 'eth1'

        is_set_eth0, is_set_eth1 = True, True

        while 1:
            #check eth0 up or down
            try:
                eth0_state = check_output(['sudo', 'cat', '/sys/class/net/{}/operstate'.format(eth0)]).decode().strip()
            except CalledProcessError:
                print('Exception handled: {} state is error'.format(eth0))
            else:
                print('eth0 state is {}'.format(eth0_state))
                if eth0_state == 'up':
                    print('up')
                    if not is_set_eth0:
                        is_set_eth0 = True
                else:
                    print('down')
                    if is_set_eth0:
                        is_set_eth0 = set_eth_ip(eth0, network['eth0_ip'], network['eth0_mask'], network['eth0_broad'])

            #check eth1 up or down
            try:
                eth1_state = check_output(['sudo', 'cat', '/sys/class/net/{}/operstate'.format(eth1)]).decode().strip()
            except CalledProcessError:
                print('Exception handled: {} state is error'.format(eth1))
            else:
                print('eth1 state is {}'.format(eth1_state))
                if eth1_state == 'up':
                    print('up')
                    if not is_set_eth1:
                        is_set_eth1 = True
                else:
                    print('down')
                    if is_set_eth1:
                        is_set_eth1 = set_eth_ip(eth1, network['eth1_ip'], network['eth1_mask'], network['eth1_broad'])
                        if is_init == '2':
                            set_eth_gw('eth1', network['eth1_gateway'])

            time.sleep(5)
