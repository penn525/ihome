import redis


class Config():
    """ 配置信息 """
    SECRET_KEY = b'\xe2\x15%\xdc__\x8d&v6\xf7qi7\xc7\x00'

    # 数据库
    SQLALCHEMY_DATABASE_URI = 'mysql://root:root123@127.0.0.1:3306/ihome'
    SQLALCHEMY_TRACK_MODIFIFATIONS = True

    # redis
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # falsk-session配置
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.StrictRedis(REDIS_HOST, REDIS_PORT)
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = 24 * 60 * 60


class DevelopmentConfig(Config):
    """ 开发环境配置信息 """
    DEBUG = True


class ProductionConfig(Config):
    """ 生产环境配置信息 """
    pass


config_map = {
    'develop': DevelopmentConfig,
    'product': ProductionConfig
}
