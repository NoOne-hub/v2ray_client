#!/bin/bash
#coding=utf-8

#安装依赖
pip3 install -r requirements.txt

#部署后台运行环境,以及开机自启
pip3 install gunicorn
sudo apt-get install supervisor -y
echo "[program:v2rayClient]
command=gunicorn -b localhost:8000 -w 4 v2rayClient:app
directory=$(pwd)
user=$USER
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true" > /etc/supervisor/conf.d/v2rayClient.conf

sudo supervisord -c /etc/supervisor/supervisord.conf
echo "接下来输入update,然后ctrl+d 退出"
sudo supervisorctl -c /etc/supervisor/supervisord.conf

echo -e "success"
echo -e "now you can open you web browser,open http://127.0.0.1:8000"
