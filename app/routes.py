from app import app
from flask import render_template, url_for, request
import json
import subprocess
from urllib.parse import unquote
from app.models import v2rayConfig, AlchemyEncoder
from app import db
from app.v2rayControl.vmess2json import gen_client
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
    print(data)
    v2 = v2rayConfig(
        add=data['add'],
        aid=data['aid'],
        host=data['host'],
        id=data['id'],
        net=data['net'],
        path=data['path'],
        port=data['port'],
        ps=data['ps'],
        tls=data['tls'],
        type=data['type'],
        encrypt='auto',  # 默认为auto
        mux='off',  # 默认关闭
        status="off",  # 默认关闭
        sub=sub_url
    )
    return v2


'''
消息处理部分
'''


def set_message(code=200, url=""):
    if code == 200:
        return {
            "code": code,
            "status": "Success",
            "url": url
        }
    else:
        return {
            "code": code,
            "status": "Failure",
            "url": url
        }


'''
主界面路由部分
'''


@app.route('/', methods=["GET", "POST"])
@app.route('/index', methods=["GET", "POST"])
def index():
    page = request.args.get('page', 1, type=int)
    configs = v2rayConfig.query.order_by(v2rayConfig.status.desc()).paginate(page, app.config['PER_PAGE'], False)
    next_url = url_for('index', page=configs.next_num) \
        if configs.has_next else None
    prev_url = url_for('index', page=configs.prev_num) \
        if configs.has_prev else None
    return render_template('index.html', v2rayconfigs=configs.items, title="配置选择", next_url=next_url,
                           prev_url=prev_url)


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
    try:
        with open(app.config['V2RAY_ACCESS_LOG']) as f:
            content = f.read().split("\n")
            min_length = min(20, len(content))
            content = content[-min_length:]
            string = ""
            for i in range(min_length):
                string = string + content[i] + "<br>"
        return string
    except PermissionError as e:
        return " Permission denied "




@app.route('/get_error_log')
def get_error_log():
    try:
        with open(app.config['V2RAY_ERROR_LOG']) as f:
            content = f.read().split("\n")
            min_length = min(20, len(content))
            content = content[-min_length:]
            string = ""
            for i in range(min_length):
                string = string + content[i] + "<br>"
        return string
    except PermissionError as e:
        return " Permission denied "


'''
api部分，或许应该在封装到一起去，懒了
'''
re_word = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'


@app.route('/api/addSubscription', methods=["GET", "POST"])
def addSubscription():
    data = json.loads(request.get_data(as_text=True))
    print(data)
    if not re.findall(re_word, data['addr']):  # 检测订阅地址是否合法
        return set_message(400)
    sub = subscription(
        addr=data['addr'],
        remarks=data['remarks']
    )
    # 查找是否已存在这个订阅地址
    find = subscription.query.filter(subscription.addr == data['addr']).first()
    if find is not None:
        return set_message(400)
    print("1")
    db.session.add(sub)
    db.session.commit()
    return set_message(200)


@app.route('/api/deleteSub', methods=["GET", "POST"])
def deleteSub():
    data = request.get_data(as_text=True)
    num = data.split('=')[1]
    deleteConfig = subscription.query.filter(subscription.num == num).first()
    configs = v2rayConfig.query.filter(v2rayConfig.sub == deleteConfig.addr)
    for i in configs:
        db.session.delete(i)
    db.session.delete(deleteConfig)
    db.session.commit()

    return set_message(200)


@app.route('/api/editSubscription', methods=["GET", "POST"])
def editSubscription():
    data = json.loads(request.get_data(as_text=True))
    print(data)
    modifyConfig = subscription.query.filter(subscription.num == data['num']).first()
    if modifyConfig is None:
        return set_message(400)
    modifyConfig.addr = data['addr']
    modifyConfig.remarks = data['remarks']
    db.session.commit()
    return set_message(200)


@app.route('/api/updateSub', methods=["GET", "POST"])
def updateSub():
    data = request.get_data(as_text=True)
    num = data.split('=')[1]
    updateConfig = subscription.query.filter(subscription.num == num).first()
    sub_url = updateConfig.addr
    print(sub_url)
    try:
        print("Reading from subscribe ...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
        req = urllib.request.Request(url=sub_url, headers=headers)
        with urllib.request.urlopen(req) as response:
            _subs = response.read()
            result = Parse.parse_subscription(_subs)
    except Exception as e:
        return set_message(400)
    if result is None:
        return set_message(400)
    print(result)
    need_stop = v2rayConfig.query.filter(v2rayConfig.status == "on").first()
    # 先停止服务
    if need_stop is not None:
        stop()
    old_sub = v2rayConfig.query.filter(v2rayConfig.sub == sub_url)
    for i in old_sub:
        db.session.delete(i)
    for i in result:
        v2 = json2config(i, sub_url)
        db.session.add(v2)
    db.session.commit()
    return set_message(200, url_for('index'))


@app.route('/api/generate_config', methods=['GET', 'POST'])
def generate_config():
    data = json.loads(request.get_data(as_text=True))
    print(data)
    # 修改部分
    if 'num' in data.keys():
        saveConfig = v2rayConfig.query.filter(v2rayConfig.num == data['num']).first()
        saveConfig.id = data['uuid']
        saveConfig.add = data['addr']
        saveConfig.port = data['port']
        saveConfig.aid = data['alterId']
        saveConfig.encrypt = data['encrypt']
        saveConfig.type = data['fake']
        saveConfig.path = data['path']
        saveConfig.tls = data['tls']
        saveConfig.mux = data['mux']
        saveConfig.ps = data['remarks']
        saveConfig.net = data['trans']
        saveConfig.host = data['host']
        saveConfig.status = data['status']
    else:
        # 手动添加部分
        v2 = v2rayConfig(
            id=data['uuid'],
            add=data['addr'],
            port=data['port'],
            aid=data['alterId'],
            encrypt=data['encrypt'],
            type=data['fake'],
            path=data['path'],
            tls=data['tls'],
            mux=data['mux'],
            status=data['status'],
            ps=data['remarks'],
            net=data['trans'],
            host=data['host']
        )
        db.session.add(v2)
    db.session.commit()
    return set_message(200, url_for('index'))


@app.route('/api/deleteById', methods=["GET", "POST"])
def deleteById():
    data = request.get_data(as_text=True)
    num = data.split('=')[1]
    deleteConfig = v2rayConfig.query.filter(v2rayConfig.num == num).first()
    db.session.delete(deleteConfig)
    db.session.commit()
    return set_message(200)


@app.route('/api/editById', methods=["GET", "POST"])
def editById():
    data = request.get_data(as_text=True)
    num = data.split('=')[1]
    return set_message(200, url_for('config', num=num))


@app.route('/api/start_service', methods=['POST', "GET"])
def start_service():
    try:
        data = request.get_data(as_text=True)
        num = data.split('=')[1]
        startConfig = v2rayConfig.query.filter(v2rayConfig.status == "on")
        for i in startConfig:
            i.status = "off"
        startConfig = v2rayConfig.query.filter(v2rayConfig.num == num).first()
        myjson = json.dumps(startConfig, cls=AlchemyEncoder)
        print(myjson)
        gen_client(json.loads(myjson))
        startConfig.status = "on"
        db.session.commit()
        restart()
        return set_message(200)
    except PermissionError as e:
        return set_message(400)


@app.route('/api/stop_service', methods=['POST', "GET"])
def stop_service():
    data = request.get_data(as_text=True)
    print(data)
    num = data.split('=')[1]
    stopConfig = v2rayConfig.query.filter(v2rayConfig.num == num).first()
    if stopConfig.status == "off":
        return set_message(400)
    stopConfig.status = "off"
    db.session.commit()
    stop()
    return set_message(200)


@app.route('/api/vmess2config', methods=["POST", "GET"])
def vmess2config():
    try:
        data = request.get_data(as_text=True)
        data = data.split('=')[1]
        data = unquote(data)
        data = Parse.parseVmess(data)
    except Exception as e:
        return set_message(400)
    v2 = json2config(data)
    db.session.add(v2)
    db.session.commit()
    return set_message(200)
