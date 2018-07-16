"""
配置信息集成:
1.数据库配置
2.redis配置
3.session配置
4.csrf配置
5.迁移
6.日志记录

"""
import datetime
import random

from flask import Flask, session, current_app
from info import create_app, db, models
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
import logging

# 调用工厂发方法,传入参数获取到应用程序对象
from info.models import User

app = create_app("develop")

# 创建manager对象管理app
manager = Manager(app)
# 使用Migrate关联app,db
Migrate(app, db)
# 添加操作命令
manager.add_command("db", MigrateCommand)


# 创建管理员,装饰器,用来通过调用方法,传递参数
@manager.option('-u', '--username', dest='username')
@manager.option('-p', '--password', dest='password')
def create_super_user(username, password):
    # 创建管理员对象
    admin = User()

    # 设置管理员属性
    admin.mobile = username
    admin.nick_name = username
    admin.password = password
    admin.is_admin = True

    # 添加到数据库
    try:
        db.session.add(admin)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return "管理员创建失败"

    return "管理员创建成功"


# 添加测试用户
@manager.option('-n', '--name', dest='name')
def add_test_users(name):
    # 用户列表容器
    user_list = []

    for num in range(0, 1000):
        # 创建用户对象
        user = User()

        # 设置属性
        user.mobile = "138%08d" % num
        user.nick_name = "138%08d" % num
        user.password_hash = "pbkdf2:sha256:50000$YYAGSAZY$2d2a6bdf9b3a142c14c5c15b62c93603caff7542afa5c80ec9f7e2a880efcf4b"
        # 近一个月用户登陆时间
        user.last_login = datetime.datetime.now() - datetime.timedelta(seconds=random.randint(0, 3600 * 24 * 31))
        # 添加到用户列表
        user_list.append(user)

    # 添加到数据库中
    try:
        db.session.add_all(user_list)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return "添加失败"

    return "添加成功"


if __name__ == '__main__':
    manager.run()
