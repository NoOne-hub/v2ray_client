#!/bin/bash
#coding=utf-8
pip3 uninstall -r requirements.txt
rm /etc/supervisor/conf.d/v2rayClient.conf
pip3 uninstall gunicorn
