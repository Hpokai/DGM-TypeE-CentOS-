#!/usr/bin/env python3
#coding=utf-8

import RPi.GPIO as GPIO
import time
import os
from pathlib import Path

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN)
while 1:
    while GPIO.input(11):
        print('gpio 11: High.')
        time.sleep(0.5)

    cnt = 0
    while not GPIO.input(11):
        print('gpio 11: Low.')
        time.sleep(1)
        cnt += 1
        print('cnt = {}'.format(cnt))
        if cnt > 2:
            #do something before reboot
            print('reboot!')
            path = '/home/rp/.data_gather/WebSettings/SystemSettings.txt'
            if Path(path).exists():
                with open(path, 'w') as f:
                    f.write('1\n')

            time.sleep(0.5)
            os.system('sudo reboot')
            break

    time.sleep(1)
    print('gpio END')
