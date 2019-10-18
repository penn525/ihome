import logging
import os
from logging.handlers import RotatingFileHandler

import redis
from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

from config import config_map
from ihome.utils.common import ReConverter

db = SQLAlchemy()
redis_store = None

# 日志配置
logging.basicConfig(level=logging.DEBUG)
file_log_handler = RotatingFileHandler(
    'logs/log', maxBytes=1024*1024*100, backupCount=10)
formatter = logging.Formatter(
    '%(levelname)s %(filename)s:%(lineno)d %(message)s')
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app实用的）添加日志记录器
logging.getLogger().addHandler(file_log_handler)


def create_app(config_name='product'):
    """
    创建flask的应用对象
    :param config_name: str 配置模式名字
    （'develop'- 开发者模式， 'product'- 生产者模式）
    :return app: flask应用对象
    """
    app = Flask(__name__)
    app.config.from_object(config_map.get(config_name))

    # 注册数据库
    db.init_app(app)

    # 开启 csrf 保护
    CSRFProtect(app)

    # flask-session
    Session(app)

    global redis_store
    redis_store = redis.StrictRedis(
        host=app.config.get('REDIS_HOST'),
        port=app.config.get('REDIS_PORT')
    )

    # 将自定义转换器类,添加到默认的转换列表中
    app.url_map.converters['re'] = ReConverter

    # 注册蓝图
    from . import api_1_0  # 延迟加载，解决循环导包
    app.register_blueprint(api_1_0.api, url_prefix='/api/v1.0')

    from ihome.web_html import html
    app.register_blueprint(html)

    # 日志文件夹
    try:
        os.makedirs('logs')
    except:
        pass

    return app
