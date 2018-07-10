"""
配置信息集成:
1.数据库配置
2.redis配置
3.session配置
4.csrf配置
5.迁移
6.日志记录

"""
from flask import Flask, session, current_app
from info import create_app, db, models
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
import logging

# 调用工厂发方法,传入参数获取到应用程序对象
app = create_app("develop")

# 创建manager对象管理app
manager = Manager(app)

# 使用Migrate关联app,db
Migrate(app, db)
# 添加操作命令

manager.add_command("db", MigrateCommand)

if __name__ == '__main__':
    manager.run()
