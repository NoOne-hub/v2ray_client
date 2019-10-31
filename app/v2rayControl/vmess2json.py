import json
import base64
import pprint
import random
import hashlib
import urllib.request
import urllib.parse
from app import app
from app.models import Others

vmscheme = "vmess://"
ssscheme = "ss://"

TPL = {}
TPL["CLIENT"] = """
{
  "log": {
    "access": "",
    "error": "",
    "loglevel": "error"
  },
  "inbounds": [
  ],
  "outbounds": [
    {
      "protocol": "vmess",
      "settings": {
        "vnext": [
          {
            "address": "host.host",
            "port": 1234,
            "users": [
              {
                "email": "greenhand@v2ray.com",
                "id": "",
                "alterId": 0,
                "security": "auto"
              }
            ]
          }
        ]
      },
      "streamSettings": {
        "network": "tcp"
      },
      "mux": {
        "enabled": true
      },
      "tag": "proxy"
    },
    {
      "protocol": "freedom",
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
    }
}
"""

# tcpSettings
TPL["http"] = """
{
    "header": {
        "type": "http",
        "request": {
            "version": "1.1",
            "method": "GET",
            "path": [
                "/"
            ],
            "headers": {
                "Host": [
                    "www.cloudflare.com",
                    "www.amazon.com"
                ],
                "User-Agent": [
                    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0"
                ],
                "Accept": [
                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
                ],
                "Accept-language": [
                    "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4"
                ],
                "Accept-Encoding": [
                    "gzip, deflate, br"
                ],
                "Cache-Control": [
                    "no-cache"
                ],
                "Pragma": "no-cache"
            }
        }
    }
}
"""

# kcpSettings
TPL["kcp"] = """
{
    "mtu": 1350,
    "tti": 50,
    "uplinkCapacity": 12,
    "downlinkCapacity": 100,
    "congestion": false,
    "readBufferSize": 2,
    "writeBufferSize": 2,
    "header": {
        "type": "wechat-video"
    }
}
"""

# wsSettings
TPL["ws"] = """
{
    "connectionReuse": true,
    "path": "/path",
    "headers": {
        "Host": "host.host.host"
    }
}
"""

# httpSettings
TPL["h2"] = """
{
    "host": [
        "host.com"
    ],
    "path": "/host"
}
"""

TPL["quic"] = """
{
  "security": "none",
  "key": "",
  "header": {
    "type": "none"
  }
}
"""

TPL["in_socks"] = """
{
    "tag":"socks-in",
    "port": 10808,
    "listen": "::",
    "protocol": "socks",
    "settings": {
        "auth": "noauth",
        "udp": true,
        "ip": "127.0.0.1"
    }
}
"""

TPL["in_http"] = """
{
    "tag":"http-in",
    "port": 8123,
    "listen": "::",
    "protocol": "http"
}
"""

TPL["in_mt"] = """
{
    "tag": "mt-in",
    "port": 6666,
    "protocol": "mtproto",
    "settings": {
        "users": [
            {
                "secret": ""
            }
        ]
    }
}
"""

TPL["out_mt"] = """
{
    "tag": "mt-out",
    "protocol": "mtproto",
    "proxySettings": {
        "tag": "proxy"
    }
}
"""

TPL["in_dns"] = """
{
  "port": 53,
  "tag": "dns-in",
  "protocol": "dokodemo-door",
  "settings": {
    "address": "1.1.1.1",
    "port": 53,
    "network": "tcp,udp"
  }
}
"""

TPL["conf_dns"] = """
{
    "hosts": {
        "geosite:category-ads": "127.0.0.1",
        "domain:googleapis.cn": "googleapis.com"
    },
    "servers": [
        "1.0.0.1",
        {
            "address": "1.2.4.8",
            "domains": [
                "geosite:cn"
            ],
            "port": 53
        }
    ]
}
"""

TPL["in_tproxy"] = """
{
    "tag":"tproxy-in",
    "port": 1080,
    "protocol": "dokodemo-door",
    "settings": {
        "network": "tcp,udp",
        "followRedirect": true
    },
    "streamSettings": {
        "sockopt": {
            "tproxy":"tproxy"
        }
    },
    "sniffing": {
        "enabled": true,
        "destOverride": [
            "http",
            "tls"
        ]
    }
}
"""

TPL["in_api"] = """
{
    "tag": "api",
    "port": 10085,
    "listen": "127.0.0.1",
    "protocol": "dokodemo-door",
    "settings": {
        "address": "127.0.0.1"
    }
}
"""

TPL["out_ss"] = """
{
    "email": "user@ss",
    "address": "",
    "method": "",
    "ota": false,
    "password": "",
    "port": 0
}
"""

TPL["bpL"] = """
            [
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
                        "fe80::/10"
                    ],
                    "outboundTag": "direct"
                }
            ]
"""

TPL["bpA"] = """
            [
                {
                    "type": "chinasites",
                    "outboundTag": "direct"
                },
                {
                    "type": "chinaip",
                    "outboundTag": "direct"
                }
            ]
"""

TPL["bpLAA"] = """
            [
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
"""

TPL["all"] = """
[]
"""

def parseLink(link):
    if link.startswith(ssscheme):
        return parseSs(link)
    elif link.startswith(vmscheme):
        return parseVmess(link)
    else:
        print("ERROR: This script supports only vmess://(N/NG) and ss:// links")
        return None


def parseSs(sslink):
    RETOBJ = {
        "v": "2",
        "ps": "",
        "add": "",
        "port": "",
        "id": "",
        "aid": "",
        "net": "shadowsocks",
        "type": "",
        "host": "",
        "path": "",
        "tls": ""
    }
    if sslink.startswith(ssscheme):
        info = sslink[len(ssscheme):]

        if info.rfind("#") > 0:
            info, _ps = info.split("#", 2)
            RETOBJ["ps"] = urllib.parse.unquote(_ps)

        if info.find("@") < 0:
            # old style link
            # paddings
            blen = len(info)
            if blen % 4 > 0:
                info += "=" * (4 - blen % 4)

            info = base64.b64decode(info).decode()

            atidx = info.rfind("@")
            method, password = info[:atidx].split(":", 2)
            addr, port = info[atidx + 1:].split(":", 2)
        else:
            atidx = info.rfind("@")
            addr, port = info[atidx + 1:].split(":", 2)

            info = info[:atidx]
            blen = len(info)
            if blen % 4 > 0:
                info += "=" * (4 - blen % 4)

            info = base64.b64decode(info).decode()
            method, password = info.split(":", 2)

        RETOBJ["add"] = addr
        RETOBJ["port"] = port
        RETOBJ["aid"] = method
        RETOBJ["id"] = password
        return RETOBJ


def parseVmess(vmesslink):
    """
    return:
{
  "v": "2",
  "ps": "remark",
  "add": "4.3.2.1",
  "port": "1024",
  "id": "xxx",
  "aid": "64",
  "net": "tcp",
  "type": "none",
  "host": "",
  "path": "",
  "tls": ""
}
    """
    if vmesslink.startswith(vmscheme):
        bs = vmesslink[len(vmscheme):]
        # paddings
        blen = len(bs)
        if blen % 4 > 0:
            bs += "=" * (4 - blen % 4)

        vms = base64.b64decode(bs).decode()
        return json.loads(vms)
    else:
        raise Exception("vmess link invalid")


def load_TPL(stype):
    s = TPL[stype]
    return json.loads(s)


def fill_basic(_c, _v):
    _outbound = _c["outbounds"][0]
    _vnext = _outbound["settings"]["vnext"][0]

    _vnext["address"] = _v["add"]
    _vnext["port"] = int(_v["port"])
    _vnext["users"][0]["id"] = _v["id"]
    _vnext["users"][0]["alterId"] = int(_v["aid"])

    _outbound["streamSettings"]["network"] = _v["net"]

    if _v["tls"] == "tls":
        _outbound["streamSettings"]["security"] = "tls"

    return _c


def fill_shadowsocks(_c, _v):
    _ss = load_TPL("out_ss")
    _ss["email"] = _v["ps"] + "@ss"
    _ss["address"] = _v["add"]
    _ss["port"] = int(_v["port"])
    _ss["method"] = _v["aid"]
    _ss["password"] = _v["id"]

    _outbound = _c["outbounds"][0]
    _outbound["protocol"] = "shadowsocks"
    _outbound["settings"]["servers"] = [_ss]

    del _outbound["settings"]["vnext"]
    del _outbound["streamSettings"]
    del _outbound["mux"]

    return _c


def fill_tcp_http(_c, _v):
    tcps = load_TPL("http")
    tcps["header"]["type"] = _v["type"]
    if _v["host"] != "":
        # multiple host
        tcps["header"]["request"]["headers"]["Host"] = _v["host"].split(",")

    if _v["path"] != "":
        tcps["header"]["request"]["path"] = [_v["path"]]

    _c["outbounds"][0]["streamSettings"]["tcpSettings"] = tcps
    return _c


def fill_kcp(_c, _v):
    kcps = load_TPL("kcp")
    kcps["header"]["type"] = _v["type"]
    _c["outbounds"][0]["streamSettings"]["kcpSettings"] = kcps
    return _c


def fill_ws(_c, _v):
    wss = load_TPL("ws")
    wss["path"] = _v["path"]
    wss["headers"]["Host"] = _v["host"]
    _c["outbounds"][0]["streamSettings"]["wsSettings"] = wss
    return _c


def fill_h2(_c, _v):
    h2s = load_TPL("h2")
    h2s["path"] = _v["path"]
    h2s["host"] = [_v["host"]]
    _c["outbounds"][0]["streamSettings"]["httpSettings"] = h2s
    return _c


def fill_quic(_c, _v):
    quics = load_TPL("quic")
    quics["header"]["type"] = _v["type"]
    quics["security"] = _v["host"]
    quics["key"] = _v["path"]
    _c["outbounds"][0]["streamSettings"]["quicSettings"] = quics
    return _c

def fill_strategy(_c, _v):
    routing = load_TPL("routing")
    routing["domainStrategy"] = _v["test"]
    _c[""]


def vmess2client(_t, _v):
    _net = _v["net"]
    _type = _v["type"]

    if _net == "shadowsocks":
        return fill_shadowsocks(_t, _v)

    _c = fill_basic(_t, _v)

    if _net == "kcp":
        return fill_kcp(_c, _v)
    elif _net == "ws":
        return fill_ws(_c, _v)
    elif _net == "h2":
        return fill_h2(_c, _v)
    elif _net == "quic":
        return fill_quic(_c, _v)
    elif _net == "tcp":
        if _type == "http":
            return fill_tcp_http(_c, _v)
        return _c
    else:
        pprint.pprint(_v)
        raise Exception("this link seem invalid to the script, please report to dev.")


def fill_inbounds(_c, _v="socks:10808,http:10809"):
    _ins = _v.split(",")
    for _in in _ins:
        _proto, _port = _in.split(":", maxsplit=1)
        _tplKey = "in_" + _proto
        if _tplKey in TPL:
            _inobj = load_TPL(_tplKey)

            if _proto == "dns":
                _c["dns"] = load_TPL("conf_dns")
                _c["routing"]["rules"].insert(0, {
                    "type": "field",
                    "inboundTag": ["dns-in"],
                    "outboundTag": "dns-out"
                })
                _c["outbounds"].append({
                    "protocol": "dns",
                    "tag": "dns-out"
                })

            elif _proto == "api":
                _c["api"] = {
                    "tag": "api",
                    "services": ["HandlerService", "LoggerService", "StatsService"]
                }
                _c["stats"] = {}
                _c["policy"] = {
                    "levels": {"0": {"statsUserUplink": True, "statsUserDownlink": True}},
                    "system": {"statsInboundUplink": True, "statsInboundDownlink": True}
                }
                _c["routing"]["rules"].insert(0, {
                    "type": "field",
                    "inboundTag": ["api"],
                    "outboundTag": "api"
                })

            elif _proto == "mt":
                mtinfo = _port.split(":", maxsplit=1)
                if len(mtinfo) == 2:
                    _port, _secret = mtinfo
                else:
                    _secret = hashlib.md5(str(random.random()).encode()).hexdigest()

                _inobj["settings"]["users"][0]["secret"] = _secret
                _c["outbounds"].append(load_TPL("out_mt"))
                _c["routing"]["rules"].insert(0, {
                    "type": "field",
                    "inboundTag": ["mt-in"],
                    "outboundTag": "mt-out"
                })

            _inobj["port"] = int(_port)
            _c["inbounds"].append(_inobj)
        else:
            print("Error Inbound: " + _in)

    return _c


def fill_dns(_c, localdns=""):
    if localdns != "":
        dns = {
            "address": localdns,
            "port": 53,
            "domains": ["geosite:cn"]
        }
        ## 当某个 DNS 服务器指定的域名列表匹配了当前要查询的域名，V2Ray 会优先使用这个 
        ## DNS 服务器进行查询，否则按从上往下的顺序进行查询。
        ## 
        _c["dns"]["servers"].insert(1, dns)

        ## 若要使 DNS 服务生效，需要配置路由功能中的 domainStrategy。
        _c["routing"]["domainStrategy"] = "IPOnDemand"

    return _c

def fill_domainStrategy(_c, type):
    _c["routing"]["domainStrategy"] = type
    return _c

def fill_rules(_c, type):
    rules = load_TPL(type)
    _c["routing"]['rules'] = rules
    return _c


def gen_client(vc):
    Others.get_all()
    cc = vmess2client(load_TPL("CLIENT"), vc)
    cc = fill_dns(cc, Others.get_all()['LOCALDNS'])
    cc = fill_inbounds(cc, Others.get_all()['INBOUNDS'])
    cc = fill_domainStrategy(cc, Others.get_all()['DOMAINSTRATEGY'])
    cc = fill_rules(cc, Others.get_all()['RULES'])
    cc['log']['access'] = Others.get_all()['V2RAY_ACCESS_LOG']
    cc['log']['error'] = Others.get_all()['V2RAY_ERROR_LOG']
    with open(Others.get_all()['V2RAY_PATH'], "w+") as f:
        json.dump(cc, f, indent=2)
