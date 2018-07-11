from info import redis_store
from info.models import User, News, Category
from info.utils.response_code import RET
from . import index_blue
import logging
from flask import current_app, render_template, session, jsonify


@index_blue.route('/', methods=["GET", 'POST'])
def show_index_page():
    # 获取用户编号
    user_id = session.get("user_id")

    # 通过user_id取出用户对象
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    # 查询数据库中，前十条新闻，按照点击量
    try:
        news_items = News.query.order_by(News.clicks.desc()).limit(10)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="查询新闻失败")

    # 将新闻对象列表，转换成字典列表
    clicks_news_list = []
    for item in news_items:
        clicks_news_list.append(item.to_dict())

    # 查询分类列表
    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="分类信息查询失败")

    # 将分类对象列表转成字典列表
    category_list =[]
    for category in categories:
        category_list.append(category.to_dict())

    # 拼接数据,渲染到页面中
    data = {
        # 如果user有值返回左边内容, 如果没有值返回右边内容
        "user_info": user.to_dict() if user else "",
        "clicks_news_list":clicks_news_list,
        "categories":category_list
    }

    return render_template('news/index.html', data=data)


# 设置网站logo, 每个浏览器在访问主机的时候,都会自动向该网站发送一个,GET请求, 地址: /favicon.ico
# 可以使用current_app.send_static_file('11.jpg'),自动去寻找static里面的资源
@index_blue.route('/favicon.ico')
def get_web_lofo():
    return current_app.send_static_file("news/favicon.ico")
