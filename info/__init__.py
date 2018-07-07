from flask_session import Session #只是用来指定session存储数据的位置
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf import CSRFProtect
from config import config_dict
from flask  import Flask

#抽取工厂方法,根据参数生产不同环境下的app
def create_app(config_name):
    app = Flask(__name__)

    #根据config_name获取到配置对象
    config = config_dict.get(config_name)

    #从类中加载配置信息到app
    app.config.from_object(config)

    #创建SQLAlchemy对象,关联app
    db = SQLAlchemy(app)

    #创建redis对象
    redis_store = redis.StrictRedis(host=config.REDIS_HOST,port=config.REDIS_PORT,decode_responses=True)

    #设置csrf对app进行保护
    CSRFProtect(app)

    #初始化Session
    Session(app)

    return app