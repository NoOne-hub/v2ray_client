#!/bin/bash
#coding=utf-8


pip3 uninstall -r requirements.txt
rm /etc/supervisor/conf.d/v2rayClient.conf
pip3 uninstall gunicorn
echo -e "接下来删除下载下来的文件夹即可，还有卸载supervisor"