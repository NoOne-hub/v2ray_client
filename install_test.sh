#!/usr/bin/env bash
#coding=utf-8
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

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
if [ ${OS} == Ubuntu ] || [ ${OS} == Debian || [ ${OS} == LinuxMint || [ ${OS} == elementaryOS [ ${OS} == Deepin ];then
	apt-get update -y
	apt-get install git unzip supervisor curl python3 python3-pip -y
	pip3 install -r requirements.txt
	pip3 install gunicorn
fi
#Manjaro&&Arch_Linux
if [ ${OS} == ManjaroLinux ] || [ ${OS} == Arch Linux ];then
	pacman -Sy
	pacman -S --noconfirm git unzip supervisor curl python3 python3-pip
	pip3 install -r requirements.txt
	pip3 install gunicorn
fi
#CentOS
if [ ${OS} == CentOS ];then
	yum update -y
	yum install git unzip supervisor curl python3 python3-pip -y
	pip3 install -r requirements.txt
	pip3 install gunicorn
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

# supervisor配置
rm -rf /etc/supervisor
mkdir -p /etc/supervisor
mkdir -p /etc/supervisor/conf.d
touch /etc/supervisor/supervisord.conf
cat>>/etc/supervisor/supervisord.conf<<EOF
[unix_http_server]
file=/var/run/supervisor.sock   ; (the path to the socket file)
chmod=0700                       ; sockef file mode (default 0700)

[supervisord]
logfile=/var/log/supervisor/supervisord.log ; (main log file;default \$CWD/supervisord.log)
pidfile=/var/run/supervisord.pid ; (supervisord pidfile;default supervisord.pid)
childlogdir=/var/log/supervisor            ; ('AUTO' child log dir, default \$TEMP)

; the below section must remain in the config file for RPC
; (supervisorctl/web interface) to work, additional interfaces may be
; added by defining them in separate rpcinterface: sections
[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[supervisorctl]
serverurl=unix:///var/run/supervisor.sock ; use a unix:// URL  for a unix socket

; The [include] section can just contain the \"files\" setting.  This
; setting can list multiple files (separated by whitespace or
; newlines).  It can also contain wildcards.  The filenames are
; interpreted as relative to this file.  Included files *cannot*
; include files themselves.

[include]
files = /etc/supervisor/conf.d/*.conf"
EOF

# 安装v2ray
curl -L -s https://install.direct/go.sh | bash


#部署后台运行环境,以及开机自启
rm -rf /etc/supervisor/conf.d/v2rayClient.conf
touch /etc/supervisor/conf.d/v2rayClient.conf
cat>>/etc/supervisor/conf.d/v2rayClient.conf<<EOF
[program:v2ray.fun]
command=/usr/local/V2ray.Fun/start.sh run
stdout_logfile=/var/log/v2ray.fun
autostart=true
autorestart=true
startsecs=5
priority=1
stopasgroup=true
killasgroup=true
EOF

#关闭supervisor
unlink /run/supervisor.sock
unlink /run/supervisor.sock

supervisord -c /etc/supervisor/supervisord.conf
echo "接下来输入update,然后ctrl+d 退出"
supervisorctl -c /etc/supervisor/supervisord.conf
echo -e "now you can open you web browser,open http://127.0.0.1:8000"
