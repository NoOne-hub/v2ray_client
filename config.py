import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    V2RAY_PATH = "/etc/v2ray/config.json"
    LOCALDNS = "8.8.8.8"
    INBOUNDS = "socks:10808,http:10809"
    V2RAY_ERROR_LOG = "/var/log/v2ray/error.log"
    V2RAY_ACCESS_LOG = "/var/log/v2ray/access.log"
    PER_PAGE = 13
