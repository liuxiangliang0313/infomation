"""
配置信息集成:
1.数据库配置
2.redis配置
3.session配置
4.csrf配置
5.迁移
6.日志记录

"""
from flask import Flask,session,current_app
from info import create_app,db
from flask_migrate import Migrate,MigrateCommand
from flask_script import Manager
import logging


app = create_app("develop")

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
    # session["name"] = "banzhang"
    # print(session.get("name"))

    #如果使用print打印,在真实环境中,不需要输出, 但是有可能很多文件里面都写了print,如果驱逐是特别麻烦
    # print('jkfjdkfjkd')

    #使用日志文件对象输出
    logging.debug("调试内容")
    logging.info("详细信息")
    logging.warning("警告信息")
    logging.error("错误信息")

    #上面的输出内容,还可以使用current_app来输出,在控制台打印效果有下划线, 但是写入到文件一样
    current_app.logger.debug("调试内容++")
    current_app.logger.info("调试内容++")
    current_app.logger.warning("调试内容++")
    current_app.logger.error("调试内容++")


    return "helloworld100"

if __name__ == '__main__':
    manager.run()