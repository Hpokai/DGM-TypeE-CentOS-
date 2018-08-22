#!/usr/bin/env python3
#coding=utf-8

import py_compile

from pathlib import Path

# 1
path = '/home/rp/.data_gather/Core/process.py'
if Path(path).exists():
    py_compile.compile(path, '/home/rp/.data_gather/Core/process.pyc')

# 2
path = '/home/rp/Scripts/RerunProcess.py'
if Path(path).exists():
    py_compile.compile(path, '/home/rp/Scripts/RerunProcess.pyc')

# 3
path = '/home/rp/Scripts/ResetSys.py'
if Path(path).exists():
    py_compile.compile(path, '/home/rp/Scripts/ResetSys.pyc')

# 4
path = '/home/rp/Scripts/ScriptProcess.py'
if Path(path).exists():
    py_compile.compile(path, '/home/rp/Scripts/ScriptProcess.pyc')

# 5
path = '/home/rp/Scripts/ScriptWeb.py'
if Path(path).exists():
    py_compile.compile(path, '/home/rp/Scripts/ScriptWeb.pyc')

# 6
path = '/home/rp/.data_gather/SysSettings/ipaddresschange.py'
if Path(path).exists():
    py_compile.compile(path, '/home/rp/.data_gather/SysSettings/ipaddresschange.pyc')

# 7
path = '/home/rp/.data_gather/SysSettings/ipaddressinit.py'
if Path(path).exists():
    py_compile.compile(path, '/home/rp/.data_gather/SysSettings/ipaddressinit.pyc')

# 8
path = '/home/rp/.data_gather/DGMWebServer/WebHMI/TimeSync.py'
if Path(path).exists():
    py_compile.compile(path, '/home/rp/.data_gather/DGMWebServer/WebHMI/TimeSync.pyc')

# 9
path = '/home/rp/Scripts/HotplugIpSetting.py'
if Path(path).exists():
    py_compile.compile(path, '/home/rp/Scripts/HotplugIpSetting.pyc')

# 10
path = '/home/rp/.data_gather/pypyc.py'
if Path(path).exists():
    py_compile.compile(path, '/home/rp/.data_gather/pypyc.pyc')
