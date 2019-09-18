#!/bin/bash
#coding=utf-8


# 获取平台类型，mac还是linux平台
function get_platform_type()
{
    echo $(uname)
}

# 获取linux发行版名称
function get_linux_distro()
{
    if grep -Eq "Ubuntu" /etc/*-release; then
        echo "Ubuntu"
    elif grep -Eq "Deepin" /etc/*-release; then
        echo "Deepin"
    elif grep -Eq "LinuxMint" /etc/*-release; then
        echo "LinuxMint"
    elif grep -Eq "elementary" /etc/*-release; then
        echo "elementaryOS"
    elif grep -Eq "Debian" /etc/*-release; then
        echo "Debian"
    elif grep -Eq "CentOS" /etc/*-release; then
        echo "CentOS"
    elif grep -Eq "fedora" /etc/*-release; then
        echo "fedora"
    elif grep -Eq "openSUSE" /etc/*-release; then
        echo "openSUSE"
    elif grep -Eq "Arch Linux" /etc/*-release; then
        echo "ArchLinux"
    elif grep -Eq "ManjaroLinux" /etc/*-release; then
        echo "ManjaroLinux"
    else
        echo "Unknow"
    fi
}

function get_now_timestamp()
{
    cur_sec_and_ns=`date '+%s-%N'`
    echo ${cur_sec_and_ns%-*}
}


function install_others() {
    #安装依赖
    install_v2ray
    pip3 install -r requirements.txt
    pip3 install gunicorn

    #部署后台运行环境,以及开机自启
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
}


function install_v2ray() {
    echo "Do you need to install v2rayCore?(Y/N)"
    read choice
    if [ $choice == "Y" ]||[ $choice == "y" ];
    then
      bash <(curl -L -s https://install.direct/go.sh)
    fi
}

# 安装mac平台必要软件
function install_prepare_software_on_mac()
{
    brew install supervisor virtualenv
}

# 安装ubuntu必要软件
function install_prepare_software_on_ubuntu()
{
    sudo apt-get update
    sudo apt-get install -y supervisor virtualenv
}

# 安装debian必要软件
function install_prepare_software_on_debian()
{
    sudo apt-get update
    sudo apt-get install -y supervisor virtualenv
}

# 安装centos必要软件
function install_prepare_software_on_centos()
{
    sudo yum install -y supervisor virtualenv
}

# 安装fedora必要软件
function install_prepare_software_on_fedora()
{
    sudo dnf install -y supervisor virtualenv
}

# 安装archlinux必要软件
function install_prepare_software_on_archlinux()
{
    sudo pacman -S --noconfirm supervisor virtualenv
}

# 安装opensuse必要软件
function install_prepare_software_on_opensuse()
{
    sudo zypper install -y supervisor virtualenv
}

# 在ubuntu上安装v2rayClient
function install_v2rayClient_on_ubuntu()
{
    install_prepare_software_on_ubuntu
    install_others
}

# 在debian上安装v2rayClient
function install_v2rayClient_on_debian()
{
    install_prepare_software_on_debian
    install_others
}

# 在centos上安装v2rayClient
function install_v2rayClient_on_centos()
{
    install_prepare_software_on_centos
    install_others
}

# 在fedora上安装v2rayClient
function install_v2rayClient_on_fedora()
{
    install_prepare_software_on_fedora
    install_others
}

# 在archlinux上安装v2rayClient
function install_v2rayClient_on_archlinux()
{
    install_prepare_software_on_archlinux
    install_others
}

# 在opensuse上安装v2rayClient
function install_v2rayClient_on_opensuse()
{
    install_prepare_software_on_opensuse
    install_others
}


function install_v2rayClient_on_linux()
{
    distro=`get_linux_distro`
    echo "Linux distro: "${distro}

    if [ ${distro} == "Ubuntu" ]; then
        install_v2rayClient_on_ubuntu
    elif [ ${distro} == "Deepin" ]; then
        install_v2rayClient_on_ubuntu
    elif [ ${distro} == "LinuxMint" ]; then
        install_v2rayClient_on_ubuntu
    elif [ ${distro} == "elementaryOS" ]; then
        install_v2rayClient_on_ubuntu
    elif [ ${distro} == "Debian" ]; then
        install_v2rayClient_on_debian
    elif [ ${distro} == "CentOS" ]; then
        install_v2rayClient_on_centos
    elif [ ${distro} == "fedora" ]; then
        install_v2rayClient_on_fedora
    elif [ ${distro} == "openSUSE" ]; then
        install_v2rayClient_on_opensuse
    elif [ ${distro} == "ArchLinux" ]; then
        install_v2rayClient_on_archlinux
    elif [ ${distro} == "ManjaroLinux" ]; then
        install_v2rayClient_on_archlinux
    else
        echo "Not support linux distro: "${distro}
    fi
}

function main()
{
    begin=`get_now_timestamp`

    type=`get_platform_type`
    echo "Platform type: "${type}

    if [ ${type} == "Darwin" ]; then
        install_v2rayClient_on_mac
    elif [ ${type} == "Linux" ]; then
        install_v2rayClient_on_linux
    else
        echo "Not support platform type: "${type}
    fi

    end=`get_now_timestamp`
    second=`expr ${end} - ${begin}`
    min=`expr ${second} / 60`
    echo "It takes "${min}" minutes."
}

main


