from app import app
from flask import render_template, redirect, url_for, request, jsonify
import json
import subprocess
from urllib.parse import unquote
from app.models import v2rayConfig, AlchemyEncoder
from app import db
from app.v2rayControl.config_generate import gen_client
from app.models import Parse, subscription
import re
import urllib

'''
获取v2ray运行状态
'''


def get_status():
    output = subprocess.Popen("service v2ray status | grep Active | awk '{print $2}'", shell=True,
                              stdout=subprocess.PIPE).communicate()[0].strip().decode('utf-8')
    if output == "active":
        return "on"
    else:
        return "off"


'''
运行v2ray
'''


def start():
    subprocess.Popen('service v2ray start', shell=True)
    return "OK"


'''
停止v2ray
'''


def stop():
    subprocess.Popen('service v2ray stop', shell=True)
    return "OK"


'''
重启v2ray
'''


def restart():
    subprocess.Popen('service v2ray restart', shell=True)
    return "OK"


'''
将vmess链接转为数据库的config格式
'''


def json2config(data, sub_url=""):
    ws = 'websocket' if data['net'] == 'ws' else data['net']
    tls = 'on' if data['tls'] == 'tls' else 'off'
    v2 = v2rayConfig(
        addr=data['add'],
        alterId=data['aid'],
        host=data['host'],
        uuid=data['id'],
        trans=ws,
        path=data['path'],
        port=data['port'],
        remarks=data['ps'],
        tls=tls,
        fake=data['type'],
        encrypt='auto',  # 默认为auto
        mux='off',  # 默认关闭
        status="off",  # 默认关闭
        sub=sub_url
    )
    return v2


'''
主界面路由部分
'''


@app.route('/')
@app.route('/index')
def index():
    configs = v2rayConfig.query.order_by(v2rayConfig.num)
    return render_template('index.html', v2rayconfigs=configs, title="配置选择")


@app.route('/config', methods=["GET"])
def config():
    num = request.args.get('num')
    editConfig = v2rayConfig.query.filter(v2rayConfig.num == num).first()
    return render_template('config.html', v2ray=editConfig, title="添加/修改连接")


@app.route('/subscription')
def Subscription():
    sub = subscription.query.order_by(subscription.num)
    return render_template('subscription.html', title="订阅管理", subscriptions=sub)


@app.route('/log')
def log():
    return render_template('log.html', title="运行日志")


@app.route('/get_access_log')
def get_access_log():
    with open(app.config['V2RAY_ACCESS_LOG']) as f:
        content = f.read().split("\n")
        min_length = min(20, len(content))
        content = content[-min_length:]
        string = ""
        for i in range(min_length):
            string = string + content[i] + "<br>"
    return string


@app.route('/get_error_log')
def get_error_log():
    with open(app.config['V2RAY_ERROR_LOG']) as f:
        content = f.read().split("\n")
        min_length = min(20, len(content))
        content = content[-min_length:]
        string = ""
        for i in range(min_length):
            string = string + content[i] + "<br>"
    return string


'''
api部分，或许应该在封装到一起去，懒了
'''
re_word = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'


@app.route('/api/addSubscription', methods=["GET", "POST"])
def addSubscription():
    data = json.loads(request.get_data(as_text=True))
    print(data)
    if not re.findall(re_word, data['addr']):  # 检测订阅地址是否合法
        return {
            "status": "Failure"
        }
    sub = subscription(
        addr=data['addr'],
        remarks=data['remarks']
    )
    db.session.add(sub)
    db.session.commit()
    return {
        "status": "Success"
    }


@app.route('/api/deleteSub', methods=["GET", "POST"])
def deleteSub():
    data = request.get_data(as_text=True)
    num = data.split('=')[1]
    print(num)
    deleteConfig = subscription.query.filter(subscription.num == num).first()
    configs = v2rayConfig.query.filter(v2rayConfig.sub == deleteConfig.addr)
    for i in configs:
        db.session.delete(i)
    db.session.delete(deleteConfig)
    db.session.commit()

    return "True"


@app.route('/api/editSubscription', methods=["GET", "POST"])
def editSubscription():
    data = json.loads(request.get_data(as_text=True))
    print(data)
    modifyConfig = subscription.query.filter(subscription.num == data['num']).first()
    if modifyConfig is None:
        return {
            "status": "Failure"
        }
    modifyConfig.addr = data['addr']
    modifyConfig.remarks = data['remarks']
    db.session.commit()
    return {
        "status": "Success"
    }


@app.route('/api/updateSub', methods=["GET", "POST"])
def updateSub():
    data = request.get_data(as_text=True)
    num = data.split('=')[1]
    updateConfig = subscription.query.filter(subscription.num == num).first()
    sub_url = updateConfig.addr
    try:
        print("Reading from subscribe ...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
        req = urllib.request.Request(url=sub_url, headers=headers)
        with urllib.request.urlopen(req) as response:
            _subs = response.read()
            result = Parse.parse_subscription(_subs)
    except Exception as e:
        return {
            "status": "Failure"
        }
    if result is None:
        return {
            "status": "Failure"
        }
    print(result)
    old_sub = v2rayConfig.query.filter(v2rayConfig.sub == sub_url)
    for i in old_sub:
        db.session.delete(i)
    print("1")
    for i in result:
        v2 = json2config(i, sub_url)
        db.session.add(v2)
    db.session.commit()
    return {
        "status": "Success",
        "url": url_for('index')
    }


@app.route('/api/generate_config', methods=['GET', 'POST'])
def generate_config():
    data = json.loads(request.get_data(as_text=True))
    print(data)
    # 修改部分
    saveConfig = v2rayConfig.query.filter(v2rayConfig.num == data['num']).first()
    print(saveConfig.num)
    if saveConfig is not None:
        saveConfig.uuid = data['uuid']
        saveConfig.addr = data['addr']
        saveConfig.port = data['port']
        saveConfig.alterId = data['alterId']
        saveConfig.encrypt = data['encrypt']
        saveConfig.fake = data['fake']
        saveConfig.path = data['path']
        saveConfig.tls = data['tls']
        saveConfig.mux = data['mux']
        saveConfig.status = data['status']
        saveConfig.remarks = data['remarks']
        saveConfig.trans = data['trans']
        saveConfig.host = data['host']
    else:
        # 手动添加部分
        v2 = v2rayConfig(
            uuid=data['uuid'],
            addr=data['addr'],
            port=data['port'],
            alterId=data['alterId'],
            encrypt=data['encrypt'],
            fake=data['fake'],
            path=data['path'],
            tls=data['tls'],
            mux=data['mux'],
            status=data['status'],
            remarks=data['remarks'],
            trans=data['trans'],
            host=data['host']
        )
        db.session.add(v2)
    db.session.commit()
    return {
        "addr": url_for('index')
    }


@app.route('/api/deleteById', methods=["GET", "POST"])
def deleteById():
    data = request.get_data(as_text=True)
    num = data.split('=')[1]
    deleteConfig = v2rayConfig.query.filter(v2rayConfig.num == num).first()
    db.session.delete(deleteConfig)
    db.session.commit()
    return "True"


@app.route('/api/editById', methods=["GET", "POST"])
def editById():
    data = request.get_data(as_text=True)
    num = data.split('=')[1]
    return url_for('config', num=num)


@app.route('/api/start_service', methods=['POST', "GET"])
def start_service():
    data = request.get_data(as_text=True)
    num = data.split('=')[1]
    startConfig = v2rayConfig.query.filter(v2rayConfig.status == "on")
    for i in startConfig:
        i.status = "off"
    startConfig = v2rayConfig.query.filter(v2rayConfig.num == num).first()
    myjson = json.dumps(startConfig, cls=AlchemyEncoder)
    gen_client(json.loads(myjson))
    startConfig.status = "on"
    db.session.commit()
    restart()
    return "OK"


@app.route('/api/stop_service', methods=['POST', "GET"])
def stop_service():
    data = request.get_data(as_text=True)
    print(data)
    num = data.split('=')[1]
    stopConfig = v2rayConfig.query.filter(v2rayConfig.num == num).first()
    if stopConfig.status == "off":
        return "Failure"
    stopConfig.status = "off"
    db.session.commit()
    stop()
    return "OK"


@app.route('/api/vmess2config', methods=["POST", "GET"])
def vmess2config():
    try:
        data = request.get_data(as_text=True)
        data = data.split('=')[1]
        data = unquote(data)
        data = Parse.parseVmess(data)
    except Exception as e:
        return "Failure"
    v2 = json2config(data)
    db.session.add(v2)
    db.session.commit()
    return "OK"
