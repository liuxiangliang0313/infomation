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
from info import create_app,db
from flask_migrate import Migrate,MigrateCommand
from flask_script import Manager


app = create_app("product")

#创建manager对象管理app
manager = Manager(app)
#使用Migrate关联app,db
Migrate(app,db)
#添加操作命令
manager.add_command("db",MigrateCommand)


@app.route('/',methods=["GET",'POST'])
def hello_world():

    #测试redis存储数据
    # redis_store.set("name","itcast")

    #使用session存储数据,以后专门用户存储用户登陆信息(比如:用户名,手机号)
    session["name"] = "banzhang"
    print(session.get("name"))

    return "helloworld100"

if __name__ == '__main__':
    manager.run()