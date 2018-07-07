from info import redis_store
from . import index_blue
import logging
from  flask import current_app,render_template

@index_blue.route('/',methods=["GET",'POST'])
def hello_world():

    return render_template('news/index.html')

#设置网站logo, 每个浏览器在访问主机的时候,都会自动向该网站发送一个,GET请求, 地址: /favicon.ico
#可以使用current_app.send_static_file('11.jpg'),自动去寻找static里面的资源
@index_blue.route('/favicon.ico')
def get_web_lofo():


    return current_app.send_static_file("news/favicon.ico")