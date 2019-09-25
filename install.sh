#!/bin/bash
#coding=utf-8

function get_now_timestamp()
{
    cur_sec_and_ns=`date '+%s-%N'`
    echo ${cur_sec_and_ns%-*}
}

function install_v2ray() {
    echo "Do you need to install v2rayCore?(Y/N)"
    read choice
    if [ $choice == "Y" ]||[ $choice == "y" ];
    then
      bash <(curl -L -s https://install.direct/go.sh)
    fi
}


function install_components() {
    #安装依赖
    install_v2ray
    pip3 install -r requirements.txt
    git clone https://github.com/Supervisor/supervisor
    cd supervisor && python setup.py install
    cd ..
    #部署后台运行环境,以及开机自启
    echo_supervisord_conf > config/supervisord.conf
    SHELL_FOLDER=$(cd "$(dirname "$0")";pwd)
    echo "[program:v2rayClient]
command=gunicorn -b localhost:8000 -w 4 v2rayClient:app
directory=$SHELL_FOLDER
user=$USER
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true" >> config/supervisord.conf
    supervisord -c config/supervisord.conf
    echo "接下来输入update,然后ctrl+d 退出"
    supervisorctl -c config/supervisord.conf
}




function main()
{

    command -v git >/dev/null 2>&1 || { echo >&2 "I require git but it's not installed.  Aborting."; exit 1; }
    command -v virtualenv >/dev/null 2>&1 || { echo >&2 "I require virtualenv but it's not installed.  Aborting."; exit 1; }
    begin=`get_now_timestamp`
    install_components
    end=`get_now_timestamp`
    second=`expr ${end} - ${begin}`
    min=`expr ${second} / 60`
    echo "It takes "${min}" minutes."
    echo -e "success"
    echo -e "now you can open you web browser,open http://127.0.0.1:8000"
}

main

