from info import redis_store, constants
from info.models import User, News, Category
from info.utils.commons import user_login_data
from info.utils.response_code import RET
from . import index_blue
import logging
from flask import current_app, render_template, session, jsonify, request, g


# 获取首页新闻列表数据
# 请求路径: /newslist
# 请求方式: GET
# 请求参数: cid,page,per_page
# 返回值: data数据
@index_blue.route('/newslist')
def news_list():
    """
    思路分析:
    1.获取参数
    2.转换参数类型
    3.查询数据库
    4.获取到分页对象中的内容
    5.将对象列表,转成字典列表
    6.返回响应,携带数据
    :return:
    """
    # 1.获取参数
    cid = request.args.get("cid", 1)
    page = request.args.get("page", 1)
    per_page = request.args.get("per_page", 10)

    # 2.转换参数类型
    try:
        page = int(page)

        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
        per_page = 10

    # 3.查询数据库
    try:

        # 判断分类编号是否不等于1
        filters = [News.status == '0']
        if cid != "1":
            filters.append(News.category_id == cid)

        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询新闻失败")

    # 4.获取到分页对象中的内容
    currentPage = paginate.page
    totalPage = paginate.pages
    items = paginate.items

    # 5.将对象列表,转成字典列表
    news_list = []
    for news in items:
        news_list.append(news.to_dict())

    # 6.返回响应,携带数据
    return jsonify(errno=RET.OK, errmsg="查询成功", totalPage=totalPage, currentPage=currentPage, newsList=news_list)


@index_blue.route('/', methods=["GET", 'POST'])
@user_login_data
def show_index_page():
    # 获取用户编号
    # user_id = session.get("user_id")
    #
    # #通过user_id取出用户对象
    # user = None
    # if user_id:
    #     try:
    #         user = User.query.get(user_id)
    #     except Exception as e:
    #         current_app.logger.error(e)

    # 查询数据库中,前十条新闻,按照点击量
    try:
        news_items = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询新闻失败")

    # 将新闻对象列表,转成字典列表
    clicks_news_list = []
    for item in news_items:
        clicks_news_list.append(item.to_dict())

    # 查询分类列表
    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="分类信息查询失败")

    # 将分类对象列表转成,字典列表
    category_list = []
    for category in categories:
        category_list.append(category.to_dict())

    # 拼接数据,渲染到页面中
    data = {
        # 如果user有值返回左边内容, 如果没有值返回右边内容
        "user_info": g.user.to_dict() if g.user else "",
        "clicks_news_list": clicks_news_list,
        "categories": category_list
    }

    return render_template('news/index.html', data=data)


# 设置网站logo, 每个浏览器在访问主机的时候,都会自动向该网站发送一个,GET请求, 地址: /favicon.ico
# 可以使用current_app.send_static_file('111.jpg'),自动去寻找static里面的资源
@index_blue.route('/favicon.ico')
def get_web_lofo():
    return current_app.send_static_file("news/favicon.ico")
