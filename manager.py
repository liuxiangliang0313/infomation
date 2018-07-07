"""
配置信息集成:
1.数据库配置
2.redis配置
3.session配置
4.csrf配置
5.迁移
6.日志记录

"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis

app = Flask(__name__)

#配置信息
class Config(object):
    #数据库配置
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@127.0.0.1:3306/information12"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #配置redis
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

#从类中加载配置信息到app
app.config.from_object(Config)

#创建SQLAlchemy对象,关联app
db = SQLAlchemy(app)

#创建redis对象
redis_store = redis.StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT,decode_responses=True)

@app.route('/')
def hello_world():

    #测试redis存储数据
    redis_store.set("name","itcast")

    return "helloworld100"

if __name__ == '__main__':
    app.run(debug=True)