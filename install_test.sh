#!/usr/bin/env bash
#coding=utf-8

#检查root权限
[ $(id -u) != "0" ] && { echo "${CFAILURE}Error: You must be root to run this script${CEND}"; exit 1; }

#获取系统名称
    if grep -Eq "Ubuntu" /etc/*-release; then
        echo "Ubuntu"
        OS=Ubuntu
    elif grep -Eq "Deepin" /etc/*-release; then
        echo "Deepin"
        OS=Deepin
    elif grep -Eq "LinuxMint" /etc/*-release; then
        echo "LinuxMint"
        OS=LinuxMint
    elif grep -Eq "elementary" /etc/*-release; then
        echo "elementaryOS"
        OS=elementaryOS
    elif grep -Eq "Debian" /etc/*-release; then
        echo "Debian"
        OS=Debian
    elif grep -Eq "CentOS" /etc/*-release; then
        echo "CentOS"
        OS=CentOS
    elif grep -Eq "fedora" /etc/*-release; then
        echo "fedora"
        OS=fedora
    elif grep -Eq "openSUSE" /etc/*-release; then
        echo "openSUSE"
        OS=openSUSE
    elif grep -Eq "Arch Linux" /etc/*-release; then
        echo "ArchLinux"
        OS=ArchLinux
    elif grep -Eq "ManjaroLinux" /etc/*-release; then
        echo "ManjaroLinux"
        OS=ManjaroLinux
      elif grep -Eq "Mac" /System/Library/CoreServices/SystemVersion.plist; then
        echo "Mac"
        OS=Mac
    else
        echo "Unknow"
        echo "${CFAILURE}Does not support this OS, Please contact the author! ${CEND}"
        kill -9 $$
fi

#安装依赖包
#Ubuntu
if [ ${OS} == Ubuntu ] || [ ${OS} == Debian ] || [ ${OS} == LinuxMint ] || [ ${OS} == elementaryOS ] || [ ${OS} == Deepin ];then
    apt-get update -y
    apt-get install git unzip supervisor curl python3 python3-pip -y
    pip3 install -r requirements.txt
    pip3 install gunicorn
fi
#Manjaro&&Arch_Linux
if [ ${OS} == ManjaroLinux ] || [ ${OS} == ArchLinux ];then
    pacman -Sy
    pacman -S --noconfirm git unzip supervisor curl python3 python3-pip
    pip3 install -r requirements.txt
    pip3 install gunicorn
fi
#CentOS
if [ ${OS} == CentOS ];then

    yum install git unzip curl python3 python3-pip -y
    pip3 install -r requirements.txt
    pip3 install gunicorn
    pip3 install supervisor
fi
#openSUSE
if [ ${OS} == openSUSE ];then
    zypper install git unzip supervisor curl python3 python3-pip -y
    pip3 install -r requirements.txt
    pip3 install gunicorn
fi
#fedora
if [ ${OS} == fedora ];then
    dnf install git unzip supervisor curl python3 python3-pip -y
    pip3 install -r requirements.txt
    pip3 install gunicorn
fi
#Mac
if [ ${OS} == Mac ];then
    pip3 install git unzip supervisor curl python3 python3-pip -y
    pip3 install -r requirements.txt
    pip3 install gunicorn
fi

# 安装v2ray
curl -L -s https://install.direct/go.sh | bash

# supervisord.conf配置
rm -rf /etc/supervisor
mkdir -p /etc/supervisor
mkdir -p /etc/supervisor/conf.d
touch /etc/supervisor/supervisord.conf
echo_supervisord_conf > /etc/supervisor/supervisord.conf
cat>>/etc/supervisor/supervisord.conf<<EOF
[include]
files = /etc/supervisor/conf.d/*.conf
EOF

# v2rayClient.conf配置
rm -rf /etc/supervisor/conf.d/v2rayClient.conf
touch /etc/supervisor/conf.d/v2rayClient.conf
cat>>/etc/supervisor/conf.d/v2rayClient.conf<<EOF
[program:v2rayClient]
command=gunicorn -b 0.0.0.0:8000 -w 4 v2rayClient:app
directory=$(pwd)
user=$USER
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
EOF

#日志
touch /var/log/v2ray/error.log
chmod -R 777 /var/log/v2ray/error.log
touch /var/log/v2ray/access.log
chmod -R 777 /var/log/v2ray/access.log

#关闭supervisor
unlink /run/supervisor.sock
pkill -9 supervisord

supervisord -c /etc/supervisor/supervisord.conf
echo "接下来输入【update】然后【ctrl+d】退出"
supervisorctl -c /etc/supervisor/supervisord.conf
echo -e "now you can open you web browser,open http://127.0.0.1:8000"
