from app import db
from sqlalchemy.ext.declarative import DeclarativeMeta
import base64
import urllib
import json


class Others:

    @staticmethod
    def get_all():
        with open("config/v2ray/others.json") as v2ray_config:
            json_content = json.load(v2ray_config)
        return json_content

    @staticmethod
    def set_info(type, aim):
        exist = ["DOMAINSTRATEGY", "RULES", "V2RAY_PATH", "LOCALDNS", "INBOUNDS", "V2RAY_ERROR_LOG", "V2RAY_ACCESS_LOG"]
        if type not in exist:
            return False
        print(type)
        print(aim)
        with open("config/v2ray/others.json") as v2ray_config:
            json_content = json.load(v2ray_config)
            json_content[type] = aim

        with open('config/v2ray/others.json', "w") as f:
            f.write(json.dumps(json_content, indent=2))
        return True


class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data)  # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)


class Parse:
    vmscheme = "vmess://"
    ssscheme = "ss://"

    @staticmethod
    def parseLink(link):
        if link.startswith(Parse.ssscheme):
            return Parse.parseSs(link)
        elif link.startswith(Parse.vmscheme):
            return Parse.parseVmess(link)
        else:
            print("ERROR: unsupported line: " + link)
            return None

    @staticmethod
    def item2link(item):
        if item["net"] == "shadowsocks":
            auth = base64.b64encode("{method}:{password}".format(**item).encode()).decode()
            addr = "{add}:{port}".format(**item)
            sslink = "ss://{}@{}#{}".format(auth, addr, urllib.parse.quote(item["ps"]))
            return sslink
        else:
            return "vmess://{}".format(base64.b64encode(json.dumps(item).encode()).decode())

    @staticmethod
    def parseSs(sslink):
        if sslink.startswith(Parse.ssscheme):
            ps = ""
            info = sslink[len(Parse.ssscheme):]

            if info.rfind("#") > 0:
                info, ps = info.split("#", 2)
                ps = urllib.parse.unquote(ps)

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

            return dict(net="shadowsocks", add=addr, port=port, method=method, password=password, ps=ps)

    @staticmethod
    def parseVmess(vmesslink):
        if vmesslink.startswith(Parse.vmscheme):
            bs = vmesslink[len(Parse.vmscheme):]
            # paddings
            blen = len(bs)
            if blen % 4 > 0:
                bs += "=" * (4 - blen % 4)
            vms = base64.b64decode(bs).decode()
            return json.loads(vms)
        else:
            raise Exception("vmess link invalid")

    @staticmethod
    def parse_subscription(lines):
        lines = base64.b64decode(lines + b'=' * (-len(lines) % 4)).decode().splitlines()
        temp = [line for line in lines]
        result = [Parse.parseLink(line) for line in temp]
        return result


class v2rayConfig(db.Model):
    num = db.Column(db.Integer, primary_key=True)
    add = db.Column(db.String(100))
    host = db.Column(db.String(100))
    id = db.Column(db.String(100))
    aid = db.Column(db.Integer)
    type = db.Column(db.String(100))
    net = db.Column(db.String(100))
    path = db.Column(db.String(100))
    ps = db.Column(db.String(100))
    tls = db.Column(db.String(20))
    port = db.Column(db.Integer)
    encrypt = db.Column(db.String(100))
    mux = db.Column(db.String(20))
    status = db.Column(db.String(20))
    sub = db.Column(db.String(200))


class subscription(db.Model):
    num = db.Column(db.Integer, primary_key=True)
    addr = db.Column(db.String(100))
    remarks = db.Column(db.String(100))
