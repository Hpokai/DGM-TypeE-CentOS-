#!/usr/bin/env python3
#coding=utf-8

from WebHMI.UserKey import UKeyOut
from WebHMI.LKeyCom import DeCrypComp
from WebHMI.TimeSync import time_sync
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.files import File
from WebHMI.models import Server, InitNetworkInfo, UpdatedNetworkInfo, OtherSettingsInfo
from pathlib import Path
from django.contrib import auth
from django.http import HttpResponseRedirect, JsonResponse, FileResponse
from django.core.files.storage import FileSystemStorage
from subprocess import check_output, CalledProcessError, run

import base64
import copy
import shutil
import zipfile

def validate_auth(request):
    serial_key = request.GET.get('skey', None)

    is_match = is_key_match(serial_key)
    save_compare_key_result(is_match)

    data = {
        'is_match': is_match
    }
    return JsonResponse(data)

def login(request):
    if request.user.is_authenticated:
        #return HttpResponseRedirect('/index/')
        return HttpResponseRedirect('/MainPage/')
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')

    user = auth.authenticate(username=username, password=password)

    if user is not None and user.is_active:
        auth.login(request, user)
        #return HttpResponseRedirect('/index/')
        return HttpResponseRedirect('/MainPage/')
    else:
        return render_to_response('login.html', locals())

def index(request):
    return render_to_response('index.html', locals())

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/login')

# Create your views here.
def keys_in_file():
    path = '/home/rp/.data_gather/WebSettings/web_OtherInfo.txt'
    if Path(path).exists():
        with open(path, 'r') as f:
            f_list = f.readlines()
            lkey = base64.b64decode(f_list[5].strip()).decode('UTF-8')
            print(lkey)
    return lkey

def is_key_match(lkey):
    ret = False
    print('lkey', lkey, len(lkey))
    result = DeCrypComp(lkey, len(lkey))
    print(result)
    if result == 'LicenseKeyOK!!':
        ret = True
    return ret

def save_compare_key_result(is_match):
    path = '/home/rp/.data_gather/WebSettings/web_au.ref'
    if Path(path).exists():
        with open(path, 'w') as f:
            f.write('{}\n'.format(is_match))

def get_compare_key_result():
    is_match = False
    path = '/home/rp/.data_gather/WebSettings/web_au.ref'
    if Path(path).exists():
        with open(path, 'r') as f:
            is_match = f.readline().strip()
            print('iskey: ', is_match)
    return is_match

def copy_log_to_dest(transfer_type):
    if transfer_type == 'SMB':
        print('delete smb dest file')
        dest_path = Path('/home/rp/.data_gather/DGMWebServer/media/smb_log')
        for x in dest_path.iterdir():
            print(x)
            x.unlink()

        print('copy smb file to dest')
        file_list = Path('/var/log').glob('dgmelog*')
        for src in file_list:
            print(src)
            shutil.copy(src, str(dest_path))

        print('zip smb files to a file')
        with zipfile.ZipFile('/home/rp/.data_gather/DGMWebServer/media/smb_log.zip', 'w') as zf:
            for x in dest_path.iterdir():
                print(x.name)
                zf.write(x, x.name)

    else:
        print('delete ftp dest file')
        dest_path = Path('/home/rp/.data_gather/DGMWebServer/media/ftp_log')
        for x in dest_path.iterdir():
            print(x)
            x.unlink()

        print('copy ftp file to dest')
        file_list = Path('/var/log').glob('xferlog*')
        for src in file_list:
            print(src)
            shutil.copy(src, str(dest_path))

        print('zip ftp files to a file')
        with zipfile.ZipFile('/home/rp/.data_gather/DGMWebServer/media/ftp_log.zip', 'w') as zf:
            for x in dest_path.iterdir():
                print(x.name)
                zf.write(x, x.name)

def delete_temp_file(request):
    print('delete_temp_file')

    p = Path('/home/rp/TypeE')
    for x in p.iterdir():
        if x.is_file():
            print('file', x)
            x.unlink()

    print('Delete Done')
    return HttpResponseRedirect('/MainPage')

def smbconnection(request):
    cell_title = ('User ID :', 'IP Address :', 'Domain Name :', 'Password :', 'Server Name :', 'Client Name :', 'Folder Name :')
    fs = Server.objects.get(type='File Server')
    dc = Server.objects.get(type='Data Center')
    uni = UpdatedNetworkInfo.objects.get(type='Updated Network Info')
    osi = OtherSettingsInfo.objects.get(type='Other Settings Info')
    ipchangeflag = 0

    eq_info = dict().fromkeys(['user', 'ip_address', 'domain_name', 'password', 'server_name', 'client_name', 'folder_name'])
    net_info = dict().fromkeys(['ip', 'mask', 'gateway'])

    other_info = dict().fromkeys(['update_min', 'update_sec', 'account_id', 'account_pw', 'auth_product', 'auth_serial', 'auth_result'])

    osi.auth_product = UKeyOut()
    print(osi.auth_product)
    save_compare_key_result(is_key_match(keys_in_file()))

    if request.method == 'POST' and 'Upload_submit' in request.POST:
        try:
            myfile = request.FILES['myfile']
        except:
            print('No file: myfile.')
        else:
            fss = FileSystemStorage()
            if myfile.name == 'UpgradeDGME.tar':
                fn = fss.save(myfile.name, myfile)
                print('filename: ', fn)
                upload_file_url = fss.url(fn)
                path = '/home/rp/.data_gather/DGMWebServer/media/UpgradeDGME.tar'
                if Path(path).exists():
                    unzip_path = '/home/rp/.data_gather/DGMWebServer/media/unzip/'
                    if not Path(unzip_path).exists():
                        try:
                            run(['mkdir', unzip_path])
                        except CalledProcessError as err:
                            print('CalledProcessError:', err)
                    try:
                        ret = check_output(['tar', '-xvf', path, '-C', unzip_path]).decode()
                    except CalledProcessError as err:
                        print('CalledProcessError:', err)
                    else:
                        print('tar:\n{}'.format(ret))
                        try:
                            run(['rm', '-r', path])
                        except CalledProcessError as err:
                            print('CalledProcessError:', err)

                        path = '/home/rp/.data_gather/DGMWebServer/WebHMI/upgrade.py'
                        if Path(path).exists():
                            try:
                                run(['python3', path])
                            except CalledProcessError as err:
                                print('CalledProcessError:', err)

    if request.method == 'POST' and 'Save_submit' in request.POST:
        fs_eq_info = copy.deepcopy(eq_info)
        dc_eq_info = copy.deepcopy(eq_info)

        fs_eq_info.update({
            'user': request.POST['userfs'],
            'ip_address': request.POST['ipaddressfs'],
            'domain_name': request.POST['domainnamefs'],
            'password': request.POST['passwordfs'],
            'server_name': request.POST['servernamefs'],
            'client_name': '',
            'folder_name': request.POST['foldernamefs']
        })
        dc_eq_info.update({
            'user': request.POST['userdc'],
            'ip_address': '',
            'domain_name': '',
            'password': request.POST['passworddc'],
            'server_name': '',
            'client_name': '',
            'folder_name': '/'
        })

        eth_net_info = copy.deepcopy(net_info)
        wlan_net_info = copy.deepcopy(net_info)

        eth_net_info.update({
            'ip': request.POST['ethipaddresslm'],
            'mask': request.POST['ethmasklm'],
            'gateway': '0'
        })
        wlan_net_info.update({
            'ip': request.POST['wlanipaddresslm'],
            'mask': request.POST['wlanmasklm'],
            'gateway': request.POST['wlangatewaylm']
        })

        other_info.update({
            'update_min': request.POST['updaterateminute'],
            'update_sec': request.POST['updateratesecond'],
            'account_id': request.POST['accountid'],
            'account_pw': request.POST['accountpw'],
            'auth_product': request.POST['authorizationproductkey'],
            'auth_serial': request.POST['authorizationserialkey'],
            'auth_result': '' #get_compare_key_result()
        })

        print('auth_serial',other_info['auth_serial'])
        other_info['auth_result'] = is_key_match(other_info['auth_serial'])
        print('auth_result',other_info['auth_result'])

        fs.user_name = fs_eq_info['user']
        fs.ip_address = fs_eq_info['ip_address']
        fs.domain_name = fs_eq_info['domain_name']
        fs.password = fs_eq_info['password']
        fs.server_name = fs_eq_info['server_name']
        fs.client_name = fs_eq_info['client_name']
        fs.folder_name = fs_eq_info['folder_name']
        fs.save()

        dc.user_name = dc_eq_info['user']
        dc.ip_address = dc_eq_info['ip_address']
        dc.domain_name = dc_eq_info['domain_name']
        dc.password = dc_eq_info['password']
        dc.server_name = dc_eq_info['server_name']
        dc.client_name = dc_eq_info['client_name']
        dc.folder_name = dc_eq_info['folder_name']
        dc.save()

        if uni.eth_ip_address != eth_net_info['ip'] or uni.eth_mask != eth_net_info['mask'] or \
                uni.wlan_ip_address != wlan_net_info['ip'] or uni.wlan_mask != wlan_net_info['mask']:
            ipchangeflag = 1

        uni.eth_ip_address = eth_net_info['ip']
        uni.eth_mask = eth_net_info['mask']
        uni.wlan_ip_address = wlan_net_info['ip']
        uni.wlan_mask = wlan_net_info['mask']
        uni.wlan_gateway = wlan_net_info['gateway']
        uni.save()

        if ipchangeflag == 1:
            path = '/home/rp/.data_gather/WebSettings/SystemSettings.txt'
            if Path(path).exists():
                 with open(path, 'w') as f:
                     f.write('2\n')

        osi.uprating_rate_min = other_info['update_min']
        osi.uprating_rate_sec = other_info['update_sec']
        osi.account_id = other_info['account_id']
        osi.account_pw = other_info['account_pw']
        osi.auth_product = other_info['auth_product']
        osi.auth_serial = other_info['auth_serial']
        osi.auth_result = other_info['auth_result']
        osi.save()
        ### ChangedIPInfo ###
        path = '/home/rp/.data_gather/WebSettings/web_ChangedIPInfo.txt'
        if Path(path).exists():
            with open(path, 'w') as f:
                str_seq = list()
                str_seq.append('{}\n'.format(base64.b64encode(uni.eth_ip_address.encode()).decode('UTF-8')))
                str_seq.append('{}\n'.format(base64.b64encode(uni.eth_mask.encode()).decode('UTF-8')))
                str_seq.append('{}\n'.format(base64.b64encode(uni.wlan_ip_address.encode()).decode('UTF-8')))
                str_seq.append('{}\n'.format(base64.b64encode(uni.wlan_mask.encode()).decode('UTF-8')))
                str_seq.append('{}\n'.format(base64.b64encode(uni.wlan_gateway.encode()).decode('UTF-8')))
                f.writelines(str_seq)

        ### InitIPInfo ###
        path = '/home/rp/.data_gather/WebSettings/web_InitIPInfo.txt'
        if Path(path).exists():
            with open(path, 'w') as f:
                str_seq = list()
                str_seq.append('{}\n'.format(base64.b64encode(b'192.168.0.5').decode('UTF-8')))
                str_seq.append('{}\n'.format(base64.b64encode(b'255.255.255.0').decode('UTF-8')))
                str_seq.append('{}\n'.format(base64.b64encode(b'192.167.0.5').decode('UTF-8')))
                str_seq.append('{}\n'.format(base64.b64encode(b'255.255.255.0').decode('UTF-8')))
                f.writelines(str_seq)

        ### OtherInfo ###
        path = '/home/rp/.data_gather/WebSettings/web_OtherInfo.txt'
        if Path(path).exists():
            with open(path, 'w') as f:
                str_seq = list()
                str_seq.append('{}\n'.format(base64.b64encode(osi.uprating_rate_min.encode()).decode('UTF-8')))
                str_seq.append('{}\n'.format(base64.b64encode(osi.uprating_rate_sec.encode()).decode('UTF-8')))
                str_seq.append('{}\n'.format(base64.b64encode(osi.account_id.encode()).decode('UTF-8')))
                str_seq.append('{}\n'.format(base64.b64encode(osi.account_pw.encode()).decode('UTF-8')))
                str_seq.append('{}\n'.format(base64.b64encode(osi.auth_product.encode()).decode('UTF-8')))
                str_seq.append('{}\n'.format(base64.b64encode(osi.auth_serial.encode()).decode('UTF-8')))
                #str_seq.append('{}\n'.format(base64.b64encode(osi.auth_result.encode()).decode('UTF-8')))
                f.writelines(str_seq)

        save_compare_key_result(osi.auth_result)

        ### Information of FS and DC ###
        path = '/home/rp/.data_gather/WebSettings/web_FSDC.txt'
        if Path(path).exists():
            with open(path, 'w') as f:
                str_seq = list()
                ## fs
                str_seq.append('{}\n'.format(base64.b64encode(fs.user_name.encode()).decode('UTF-8')))
                str_seq.append('{}\n'.format(base64.b64encode(fs.ip_address.encode()).decode('UTF-8')))
                str_seq.append('{}\n'.format(base64.b64encode(fs.domain_name.encode()).decode('UTF-8')))
                str_seq.append('{}\n'.format(base64.b64encode(fs.password.encode()).decode('UTF-8')))
                str_seq.append('{}\n'.format(base64.b64encode(fs.server_name.encode()).decode('UTF-8')))
                str_seq.append('{}\n'.format(base64.b64encode(fs.client_name.encode()).decode('UTF-8')))
                str_seq.append('{}\n'.format(base64.b64encode(fs.folder_name.encode()).decode('UTF-8')))
                ## dc
                str_seq.append('{}\n'.format(base64.b64encode(dc.user_name.encode()).decode('UTF-8')))
                str_seq.append('{}\n'.format(base64.b64encode(dc.ip_address.encode()).decode('UTF-8')))
                str_seq.append('{}\n'.format(base64.b64encode(dc.domain_name.encode()).decode('UTF-8')))
                str_seq.append('{}\n'.format(base64.b64encode(dc.password.encode()).decode('UTF-8')))
                str_seq.append('{}\n'.format(base64.b64encode(dc.server_name.encode()).decode('UTF-8')))
                str_seq.append('{}\n'.format(base64.b64encode(dc.client_name.encode()).decode('UTF-8')))
                str_seq.append('{}\n'.format(base64.b64encode(dc.folder_name.encode()).decode('UTF-8')))
                f.writelines(str_seq)

        time_sync()

    if request.method == 'POST' and 'LoadSMBlog_submit' in request.POST:
        copy_log_to_dest('SMB')
        file = open('/home/rp/.data_gather/DGMWebServer/media/smb_log.zip','rb')
        response = FileResponse(file)
        response['Content-Type']='application/octet-stream'
        response['Content-Disposition']='attachment;filename="smb_log.zip"'
        return response
    if request.method == 'POST' and 'LoadFTPlog_submit' in request.POST:
        copy_log_to_dest('FTP')
        file = open('/home/rp/.data_gather/DGMWebServer/media/ftp_log.zip','rb')
        response = FileResponse(file)
        response['Content-Type']='application/octet-stream'
        response['Content-Disposition']='attachment;filename="ftp_log.zip"'
        return response

    return render_to_response('MainPage.html', locals())
