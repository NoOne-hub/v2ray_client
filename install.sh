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

function ReadMeFirst() {
    echo "Do you have read README.md?(Y/N)"
    read choice
    if [ $choice != "Y" ]||[ $choice != "y" ];
    then
      echo "Read it first!!!Change the config second!"
      exit 1;
    fi
}

function write_config() {
cat >> config/supervisord.conf << EOF
[program:v2rayClient]
command=gunicorn -b 0.0.0.0:8000 -w 4 v2rayClient:app
directory=$1
user=$USER
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
EOF
}

function start_on_linux() {
cat >> /etc/rc.local << EOF
source $1/venv/bin/activate
supervisord -c $1/config/supervisord.conf
supervisorctl -c $1/config/supervisord.conf
EOF
chmod +x /etc/rc.local
}

function install_components() {
    #切换到虚拟环境

    #安装依赖
    install_v2ray
    source venv/bin/activate
    #部署后台运行环境
    echo_supervisord_conf > config/supervisord.conf
    SHELL_FOLDER=$(cd "$(dirname "$0")";pwd)
    sudo kill -9 $(ps -aux|grep supervisor| awk '{print$2}')
    write_config $SHELL_FOLDER
    supervisord -c config/supervisord.conf
    echo "接下来ctrl+d 退出"
    supervisorctl -c config/supervisord.conf
    if [ $? -ne 0 ]; then
      echo "执行出错，请检查是否root运行"
    else
      # 开机启动
      start_on_linux $SHELL_FOLDER
    fi
}




function main()
{
    #command -v git >/dev/null 2>&1 || { echo >&2 "I require git but it's not installed.  Aborting."; exit 1; }
    #command -v virtualenv >/dev/null 2>&1 || { echo >&2 "I require virtualenv but it's not installed.  Aborting."; exit 1; }
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

