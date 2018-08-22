 #!/usr/bin/env python3
#coding=utf-8

import time
import os

from pathlib import Path
from subprocess import check_output, CalledProcessError, run

if __name__ == '__main__':
    files_path_dict = {
        'HotplugIpSetting.pyc': '/home/rp/Scripts/',
        'RerunProcess.pyc': '/home/rp/Scripts',
        'ResetSys.pyc': '/home/rp/Scripts',
        'ScriptProcess.pyc': '/home/rp/Scripts',
        'ScriptWeb.pyc': '/home/rp/Scripts',
        'process.pyc': '/home/rp/.data_gather/Core',
        'TimeSync.pyc': '/home/rp/.data_gather/DGMWebServer/WebHMI',
        'upgrade.pyc': '/home/rp/.data_gather/DGMWebServer/WebHMI',
        'views.py': '/home/rp/.data_gather/DGMWebServer/WebHMI',
        'ipaddresschange.pyc': '/home/rp/.data_gather/SysSettings',
        'ipaddressinit.pyc': '/home/rp/.data_gather/SysSettings',
        'pypyc.pyc': '/home/rp/.data_gather'
    }

    p = Path('/home/rp/.data_gather/DGMWebServer/media/unzip')
    file_list = p.glob('*.*')

    for x in file_list:
        name = str(x).split('/')[-1]
        print(name)
        print(files_path_dict[name])
        try:
            run(['mv', '-f', x, files_path_dict[name]])
        except CalledProcessError as err:
            print('CalledProcessError:', err)

    run(['reboot'])
