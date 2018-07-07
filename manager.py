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


app = Flask(__name__)

#配置信息
class Config(object):
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@127.0.0.1:3306/information12"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

#从类中加载配置信息到app
app.config.from_object(Config)

#创建SQLAlchemy对象,关联app
db = SQLAlchemy(app)

@app.route('/')
def hello_world():

    return "helloworld100"

if __name__ == '__main__':
    app.run(debug=True)