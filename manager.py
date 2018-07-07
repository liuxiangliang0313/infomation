"""
配置信息集成:
1.数据库配置
2.redis配置
3.session配置
4.csrf配置
5.迁移
6.日志记录

"""

from flask import Flask,session
from flask_session import Session #只是用来指定session存储数据的位置
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf import CSRFProtect

app = Flask(__name__)

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


#从类中加载配置信息到app
app.config.from_object(Config)

#创建SQLAlchemy对象,关联app
db = SQLAlchemy(app)

#创建redis对象
redis_store = redis.StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT,decode_responses=True)

#设置csrf对app进行保护
CSRFProtect(app)

#初始化Session
Session(app)

@app.route('/',methods=["GET",'POST'])
def hello_world():

    #测试redis存储数据
    # redis_store.set("name","itcast")

    #使用session存储数据,以后专门用户存储用户登陆信息(比如:用户名,手机号)
    session["name"] = "banzhang"
    print(session.get("name"))

    return "helloworld100"

if __name__ == '__main__':
    app.run()