#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
from app import app


def gen_client(data):
    client_raw = """
        {
        "log": {
             "access": "/var/log/v2ray/access.log",
             "error": "/var/log/v2ray/error.log",
             "loglevel": "info"
        },
  "inbounds": [
    {
      "port": 10808,
      "protocol": "socks",
      "settings": {
        "auth": "noauth",
        "udp": true,
        "userLevel": 8
      },
      "sniffing": {
        "destOverride": [
          "http",
          "tls"
        ],
        "enabled": false
      },
      "tag": "socks"
    },
    {
      "port": 10809,
      "protocol": "http",
      "settings": {
        "userLevel": 8
      },
      "tag": "http"
    }
  ],
        "outbound": {
            "protocol": "vmess",
            "settings": {
                "vnext": [
                    {
                        "address": "",
                        "port": 39885,
                        "users": [
                            {
                                "id": "475161c6-837c-4318-a6bd-e7d414697de5",
                                "alterId": 100,
                                "security": "auto"
                            }
                        ]
                    }
                ]
            },
            "streamSettings": {
                "network": "ws"
            },
            "mux": {
                "enabled": false
            }
        },
        "inboundDetour": null,
        "outboundDetour": [
            {
                "protocol": "freedom",
                "settings": {},
                "tag": "direct"
            }
        ],
        "dns": {
            "servers": [
                "8.8.8.8",
                "8.8.4.4",
                "localhost"
            ]
        },
        "routing": {
            "strategy": "rules",
            "settings": {
                "domainStrategy": "IPIfNonMatch",
                "rules": [
                    {
                        "type": "field",
                        "ip": [
                            "0.0.0.0/8",
                            "10.0.0.0/8",
                            "100.64.0.0/10",
                            "127.0.0.0/8",
                            "169.254.0.0/16",
                            "172.16.0.0/12",
                            "192.0.0.0/24",
                            "192.0.2.0/24",
                            "192.168.0.0/16",
                            "198.18.0.0/15",
                            "198.51.100.0/24",
                            "203.0.113.0/24",
                            "::1/128",
                            "fc00::/7",
                            "fe80::/10",
                            "geoip:cn"
                        ],
                        "domain": [
                            "geosite:cn"
                        ],
                        "outboundTag": "direct"
                    },
                    {
                        "type": "chinasites",
                        "outboundTag": "direct"
                    },
                    {
                        "type": "chinaip",
                        "outboundTag": "direct"
                    }
                ]
            }
        }
    }
        """

    cLient_mkcp = json.loads("""
    {
                "mtu": 1350,
                "tti": 50,
                "uplinkCapacity": 20,
                "downlinkCapacity": 100,
                "congestion": false,
                "readBufferSize": 2,
                "writeBufferSize": 2,
                "header": {
                    "type": "none"
                }
    }
    """)

    cLient_ws = json.loads("""
    {
        "connectionReuse": true,
        "headers": {
        "Host": "",
        "path": ""
        }
    }
    """)

    cLient_tls = json.loads("""
    {
        "allowInsecure": true,
        "serverName": ""
    }
    """)
    client = json.loads(client_raw)

    if data['mux'] == "on":
        client['outbound']['mux']['enabled'] = True
    elif data['mux'] == "off":
        client['outbound']['mux']['enabled'] = False

    client['outbound']['settings']['vnext'][0]['users'][0]['alterId'] = data['alterId']
    client['outbound']['settings']['vnext'][0]['address'] = data['addr']
    client['outbound']['settings']['vnext'][0]['port'] = int(data['port'])
    client['outbound']['settings']['vnext'][0]['users'][0]['id'] = data['uuid']
    client['outbound']['settings']['vnext'][0]['users'][0]['security'] = data[
        'encrypt']
    client['outbound']['settings']['vnext'][0]['users'][0]['alterId'] = data['alterId']

    if data['trans'] == "websocket":
        client['outbound']['streamSettings']['network'] = "ws"
        cLient_ws['headers']['Host'] = data['host']
        cLient_ws['headers']['path'] = data['path']
        client['outbound']['streamSettings']['wssettings'] = cLient_ws

    elif data['trans'].startswith("mkcp"):
        if data['trans'] == "mkcp-srtp":
            cLient_mkcp['header']['type'] = "srtp"
        elif data['trans'] == "mkcp-utp":
            cLient_mkcp['header']['type'] = "utp"
        elif data['trans'] == "mkcp-wechat":
            cLient_mkcp['header']['type'] = "wechat-video"

        client['outbound']['streamSettings']['network'] = "kcp"
        client['outbound']['streamSettings']['kcpSettings'] = cLient_mkcp

    elif data['trans'] == "tcp":
        client['outbound']['streamSettings']['network'] = "tcp"

    if data['tls'] == "on":
        client['outbound']['streamSettings']['security'] = "tls"
        cLient_tls['serverName'] = data['host']
        client['outbound']['streamSettings']['tlssettings'] = cLient_tls

    print(json.dumps(client, indent=2))
    with open(app.config['V2RAY_PATH'], "w") as f:
        f.write(json.dumps(client, indent=2))
