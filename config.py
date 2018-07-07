import redis
import logging

#配置信息
class Config(object):

    #设置SECRET_KEY,DEBUG
    SECRET_KEY = "fjkdjfkd"
    DEBUG = True

    #数据库配置
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@127.0.0.1:3306/information12"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #配置redis
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    #配置session存储信息
    SESSION_TYPE = "redis" #指定存储类型
    SESSION_PERMANENT = False #需要过期
    SESSION_USE_SIGNER = True #需要签名存储
    SESSION_REDIS = redis.StrictRedis(REDIS_HOST,REDIS_PORT)
    PERMANENT_SESSION_LIFETIME = 3600*24*2 #设置session过期时间2天, 单位秒

    #默认的日志级别
    LEVEL = logging.DEBUG

#开发模式
class DevelopConfig(Config):
    pass

#生产模式(线上)
class ProductConfig(Config):
    #生产环境的数据库,可以配置
    #关闭调试模式
    DEBUG = False
    #生成环境日志级别
    LEVEL = logging.ERROR

#测试模式
class TestConfig(Config):
    #开启测试模式
    TESTING = True

#提供一个统一的入口
config_dict = {
    "develop":DevelopConfig,
    "product":ProductConfig,
    "test":TestConfig
}
