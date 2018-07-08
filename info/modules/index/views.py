from info import redis_store
from info.models import User
from . import index_blue
import logging
from flask import current_app, render_template, session


@index_blue.route('/',methods=["GET",'POST'])
def hello_world():

    #获取用户编号
    user_id = session.get("user_id")

    #通过user_id取出用户对象
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    #拼接数据,渲染到页面中
    data = {
        # 如果user有值返回左边内容, 如果没有值返回右边内容
        "user_info": user.to_dict() if user else ""
    }

    return render_template('news/index.html',data=data)

#设置网站logo, 每个浏览器在访问主机的时候,都会自动向该网站发送一个,GET请求, 地址: /favicon.ico
#可以使用current_app.send_static_file('11.jpg'),自动去寻找static里面的资源
@index_blue.route('/favicon.ico')
def get_web_lofo():


    return current_app.send_static_file("news/favicon.ico")