 #!/usr/bin/env python3
 #coding=utf-8

import RPi.GPIO as GPIO
import time
import os
import threading
import datetime
from pathlib import Path
from subprocess import check_output, CalledProcessError

def check_connection(dev):
    ret = False
    path = '/sys/class/net/{}'.format(dev)
    if Path(path).exists():
        try:
            operstate = check_output(['cat', '{}/operstate'.format(path)]).decode().strip()
        except CalledProcessError as err:
            operstate = 'down'
            print('CalledProcessError:', err)
        print('operstate = {}'.format(operstate))
        try:
            carrier = check_output(['cat', '{}/carrier'.format(path)]).decode().strip()
        except CalledProcessError as err:
            carrier = '0'
            print('CalledProcessError:', err)
        print('carrier = {}'.format(carrier))

        if operstate == 'up' and carrier == '1':
            ret = True

    return ret

def check_dataflow(dev):
    ret = False
    # for EQ
    if dev == 'eth0':
        print(dev)
        p = Path('/home/rp/.data_gather/Core/connectivity.pk')
        mt = p.stat().st_mtime
        td = datetime.datetime.now() - datetime.datetime.fromtimestamp(mt)
        print('{}:{} -> {}'.format(p.name, td, td.total_seconds()))
        if td.total_seconds() > 60*2:
            ret = False
            print('overtime')
        else:
            # print('non-block')
            ret = True

    # for IT
    else:
        print(dev)
        for p_iter in Path('/home/rp/TypeE').iterdir():
             if p_iter.is_file():
                mt = p_iter.stat().st_mtime
                td = datetime.datetime.now() - datetime.datetime.fromtimestamp(mt)
                print('{}:{} -> {}'.format(p_iter.name, td, td.total_seconds()))
                if td.total_seconds() > 60*2:
                    # print('overtime')
                    ret = False
                    break
        else:
            print('else')
            ret = True

    print('ret =', ret)
    return ret


def thread_job(dev, light_green, light_oragne):
    GPIO.setup(light_green, GPIO.OUT)
    GPIO.setup(light_oragne, GPIO.OUT)

    while 1:
        if check_connection(dev):
            if check_dataflow(dev):
                GPIO.output(light_green, GPIO.HIGH)
                time.sleep(1)
                GPIO.output(light_green, GPIO.LOW)
                GPIO.output(light_oragne, GPIO.HIGH)
                time.sleep(1)
                GPIO.output(light_oragne, GPIO.LOW)
            else:
                GPIO.output(light_green, GPIO.HIGH)
                GPIO.output(light_oragne, GPIO.HIGH)
                time.sleep(1)
        else:
            GPIO.output(light_green, GPIO.HIGH)
            GPIO.output(light_oragne, GPIO.HIGH)
            time.sleep(0.2)
            GPIO.output(light_green, GPIO.LOW)
            GPIO.output(light_oragne, GPIO.LOW)
            time.sleep(0.2)

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.cleanup()
    pin_dict = {'eq_green':23, 'eq_orange':24, 'it_green':16, 'it_orange':20}
    pin_list = [pin_dict['eq_green'], pin_dict['eq_orange'], pin_dict['it_green'], pin_dict['it_orange']]

    thread_eq = threading.Thread(target = thread_job, args = ('eth0', pin_dict['eq_green'], pin_dict['eq_orange']))
    thread_it = threading.Thread(target = thread_job, args = ('eth1', pin_dict['it_green'], pin_dict['it_orange']))

    thread_eq.start()
    thread_it.start()

    thread_eq.join()
    thread_it.join()
    # check_dataflow('eth1')
