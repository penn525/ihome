import redis
from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

from config import config_map

db = SQLAlchemy()
redis_store = None

# 简单工厂模式
def create_app(config_name='product'):
    """
    创建flask的应用对象
    :param test_config: str 配置模式名字 
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

    # 注册蓝图
    from . import api_1_0
    app.register_blueprint(api_1_0.api, url_prefix='/api/v1.0')

    return app
