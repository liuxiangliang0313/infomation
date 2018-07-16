from flask import render_template, g, redirect, request, jsonify, current_app

from info import constants, db
from info.models import Category, News, User
from info.utils.commons import user_login_data
from info.utils.image_storage import image_storage
from info.utils.response_code import RET
from . import profile_blu


# 获取作者新闻列表
# 请求路径: /user/other_news_list
# 请求方式: GET
# 请求参数:p,user_id
# 返回值: errno,errmsg
@profile_blu.route('/other_news_list')
def other_news_list():
    """
    思路分析:
    1.获取参数
    2.校验参数,参数类型转换
    3.分页查询
    4.获取分页对象属性,总页数,当前页,对象列表
    5.对象列表转成字典列表
    6.参数拼接,返回响应
    :return:
    """
    # 1.获取参数
    page = request.args.get("p", 1)
    author_id = request.args.get("user_id")

    # 2.校验参数,参数类型转换
    if not author_id:
        return jsonify(errno=RET.NODATA, errmsg="参数不全")

    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    # 2.1获取作者对象
    try:
        author = User.query.get(author_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="作者查询失败")

    if not author:
        return jsonify(errno=RET.NODATA, errmsg="作者不存在")

    # 3.分页查询
    try:
        # News.query.filter(News.user_id == author_id).paginate(page,10,False)
        paginate = author.news_list.order_by(News.create_time.desc()).paginate(page, 2, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取新闻失败")

    # 4.获取分页对象属性,总页数,当前页,对象列表
    current_page = paginate.page
    total_page = paginate.pages
    items = paginate.items

    # 5.对象列表转成字典列表
    news_list = []
    for news in items:
        news_list.append(news.to_dict())

    # 6.参数拼接,返回响应
    data = {
        "current_page": current_page,
        "total_page": total_page,
        "news_list": news_list
    }
    return jsonify(errno=RET.OK, errmsg="获取成功", data=data)


# 获取作者详情信息
# 请求路径: /user/other
# 请求方式: GET
# 请求参数:id
# 返回值: 渲染other.html页面,字典data数据
@profile_blu.route('/other')
@user_login_data
def other_info():
    """
    思路分析:
    1.获取参数
    2.校验参数
    3.查询作者对象,判断作者是否存在
    4.拼接作者信息,渲染页面
    :return:
    """
    # 1.获取参数
    author_id = request.args.get("id")

    # 2.校验参数
    if not author_id:
        return jsonify(errno=RET.NODATA, errmsg="参数不全")

    # 3.查询作者对象,判断作者是否存在
    try:
        author = User.query.get(author_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="用户查询异常")

    if not author:
        return jsonify(errno=RET.NODATA, errmsg="作者不存在")

    # 判断用户是否关注过新闻的作者
    is_followed = False
    # 用户需要登录,并且新闻要有作者
    if g.user:
        # 用户必须要在作者的粉丝列表中
        if g.user in author.followers:
            is_followed = True

    # 4.拼接作者信息,渲染页面
    data = {
        "author_info": author.to_dict(),
        "is_followed": is_followed,
        "user_info": g.user.to_dict() if g.user else ""
    }
    return render_template('news/other.html', data=data)


# 获取我的关注列表
# 请求路径: /user/user_follow
# 请求方式: GET
# 请求参数:p
# 返回值: 渲染user_follow.html页面,字典data数据
@profile_blu.route('/user_follow')
@user_login_data
def user_follow():
    """
    思路分析:
    1.获取参数
    2.参数类型转换
    3.分页查询
    4.获取分页对象属性,总页数,当前页,对象列表
    5.将对象列表转成字典列表
    6.拼接参数,返回页面渲染
    :return:
    """
    # 1.获取参数
    page = request.args.get("p", 1)

    # 2.参数类型转换
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    # 3.分页查询
    try:
        paginate = g.user.followed.paginate(page, 4, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="用户查询失败")

    # 4.获取分页对象属性,总页数,当前页,对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    # 5.将对象列表转成字典列表
    user_list = []
    for user in items:
        user_list.append(user.to_dict())

    # 6.拼接参数,返回页面渲染
    data = {
        "totalPage": totalPage,
        "currentPage": currentPage,
        "user_list": user_list
    }
    return render_template('news/user_follow.html', data=data)


# 发布新闻展示
# 请求路径: /user/news_list
# 请求方式:GET
# 请求参数:p
# 返回值:GET渲染user_news_list.html页面
@profile_blu.route('/news_list')
@user_login_data
def news_list():
    """
    思路分析:
    1.获取请求参数
    2.参数类型转换
    3.分页查询
    4.获取到分页对象属性,总页数,当前页,对象列表
    5.将对象列表转成字典列表
    6.拼接数据返回
    :return:
    """
    # 1.获取请求参数
    page = request.args.get("p", 1)

    # 2.参数类型转换
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    # 3.分页查询
    try:
        # News.query.filter(News.user_id == g.user.id).all()
        paginate = g.user.news_list.order_by(News.create_time.desc()).paginate(page, 10, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询新闻失败")

    # 4.获取到分页对象属性,总页数,当前页,对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    # 5.将对象列表转成字典列表
    news_list = []
    for news in items:
        news_list.append(news.to_review_dict())

    # 6.拼接数据返回
    data = {
        "totalPage": totalPage,
        "currentPage": currentPage,
        "news_list": news_list
    }
    return render_template('news/user_news_list.html', data=data)


# 新闻发布
# 请求路径: /user/news_release
# 请求方式:GET,POST
# 请求参数:GET无, POST ,title, category_id,digest,index_image,content
# 返回值:GET请求,user_news_release.html, data分类列表字段数据, POST,errno,errmsg
@profile_blu.route('/news_release', methods=['GET', 'POST'])
@user_login_data
def news_release():
    """
    思路分析
    1.如果第一次进入,get请求,直接渲染页面
    2.获取参数
    3.校验参数
    4.图片上传
    5.创建新闻对象,设置属性
    6.更新到数据库
    7.返回响应
    :return:
    """
    # 1.如果第一次进入,get请求,直接渲染页面
    if request.method == "GET":

        # 查询分类信息
        try:
            categories = Category.query.all()
            categories.pop(0)  # 弹出最新分类
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="分类获取失败")

        # 将分类对象列表转成字典,渲染页面
        category_list = []
        for category in categories:
            category_list.append(category.to_dict())

        return render_template('news/user_news_release.html', categories=category_list)

    # 2.获取参数
    title = request.form.get("title")
    category_id = request.form.get("category_id")
    digest = request.form.get("digest")
    file_name = request.files.get("index_image")
    content = request.form.get("content")

    # 3.校验参数
    if not all([title, category_id, digest, file_name, content]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 4.图片上传
    try:
        # 读取图片为二进制流
        image_data = file_name.read()

        # 上传
        image_name = image_storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="七牛云异常")

    # 判断图片是否上传成功
    if not image_name:
        return jsonify(errno=RET.NODATA, errmsg="图片上传失败")

    # 5.创建新闻对象,设置属性
    news = News()
    news.title = title
    news.source = '个人发布'
    news.digest = digest
    news.content = content
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + image_name
    news.category_id = category_id
    news.user_id = g.user.id
    news.status = 1  # 1代表审核中

    # 6.更新到数据库
    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="发布新闻失败")

    # 7.返回响应
    return jsonify(errno=RET.OK, errmsg="发布成功")


# 获取我的收藏新闻
# 请求路径: /user/collection
# 请求方式:GET
# 请求参数:p(页数)
# 返回值: user_collection.html页面
@profile_blu.route('/collection')
@user_login_data
def collection():
    """
    思路分析:
    1.获取参数
    2.转换参数类型
    3.分页查询,得到分页对象
    4.获取分页对象中属性,总页数,当前页,对象列表
    5.将对象列表转成字典列表
    6.拼接数据,返回页面
    :return:
    """
    # 1.获取参数
    page = request.args.get("p", 1)

    # 2.转换参数类型
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    # 3.分页查询,得到分页对象
    try:
        paginate = g.user.collection_news.paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询新闻失败")

    # 4.获取分页对象中属性,总页数,当前页,对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    # 5.将对象列表转成字典列表
    news_list = []
    for news in items:
        news_list.append(news.to_dict())

    # 6.拼接数据,返回页面
    data = {
        "totalPage": totalPage,
        "currentPage": currentPage,
        "news_list": news_list
    }
    return render_template('news/user_collection.html', data=data)


# 设置用户密码
# 请求路径: /user/pass_info
# 请求方式:GET,POST
# 请求参数:GET无, POST有参数,old_password, new_password
# 返回值:GET请求: user_pass_info.html页面,data字典数据, POST请求: errno, errmsg
@profile_blu.route('/pass_info', methods=['GET', 'POST'])
@user_login_data
def pass_info():
    """
    思路分析:
    1.第一次进来get请求,直接返回页面
    2.获取参数
    3.校验参数,旧密码正确性
    4.修改用户新密码
    5.返回响应
    :return:
    """
    # 1.第一次进来get请求,直接返回页面
    if request.method == "GET":
        return render_template('news/user_pass_info.html')

    # 2.获取参数
    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")

    # 3.校验参数,旧密码正确性
    if not all([old_password, new_password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    if not g.user.check_passowrd(old_password):
        return jsonify(errno=RET.DATAERR, errmsg="旧密码不正确")

    # 4.修改用户新密码
    g.user.password = new_password

    # 5.返回响应
    return jsonify(errno=RET.OK, errmsg="修改成功")


# 用户头像获取/设置
# 请求路径: /user/pic_info
# 请求方式:GET,POST
# 请求参数:无, POST有参数,avatar
# 返回值:GET请求: user_pci_info.html页面,data字典数据, POST请求: errno, errmsg,avatar_url
@profile_blu.route('/pic_info', methods=['GET', 'POST'])
@user_login_data
def pic_info():
    # 1.如果第一次进入,get请求,直接渲染页面
    if request.method == "GET":
        return render_template('news/user_pic_info.html', user_info=g.user.to_dict())

    # 2.获取参数
    file = request.files.get("avatar")

    # 3.校验参数
    if not file:
        return jsonify(errno=RET.NODATA, errmsg="图片不能为空")

    # 4.上传图片
    try:
        # 读取图片为二进制
        image_data = file.read()

        # 调用方法上传
        image_name = image_storage(image_data)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="七牛云上传失败")

    # 5.判断图片是否上传成功
    if not image_name:
        return jsonify(errno=RET.DATAERR, errmsg="上传失败")

    # 6.设置图像给用户
    g.user.avatar_url = image_name

    # 7.返回响应
    data = {
        "avatar_url": constants.QINIU_DOMIN_PREFIX + image_name
    }
    return jsonify(errno=RET.OK, errmsg="上传成功", data=data)


# 基本资料展示
# 请求路径: /user/base_info
# 请求方式:GET,POST
# 请求参数:POST请求有参数,nick_name,signature,gender
# 返回值:errno,errmsg
@profile_blu.route('/base_info', methods=["GET", "POST"])
@user_login_data
def base_info():
    # 1.如果是第一次进来,GET请求,直接返回页面即可
    if request.method == "GET":
        return render_template('news/user_base_info.html', user_info=g.user.to_dict() if g.user else "")

    # 2.获取参数
    nick_name = request.json.get("nick_name")
    signature = request.json.get("signature")
    gender = request.json.get("gender")

    # 3.校验参数,为空校验
    if not all([nick_name, signature, gender]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    if not gender in ["MAN", "WOMAN"]:
        return jsonify(errno=RET.DATAERR, errmsg="性别异常")

    # 4.更新用户信息
    g.user.signature = signature
    g.user.nick_name = nick_name
    g.user.gender = gender

    # 5.返回响应
    return jsonify(errno=RET.OK, errmsg="修改成功")


# 展示个人中心页面
@profile_blu.route('/info')
@user_login_data
def user_info():
    # 判断用户是否登陆
    if not g.user:
        return redirect('/')

    # 拼接数据返回页面
    data = {
        "user_info": g.user.to_dict()
    }

    return render_template('news/user.html', data=data)
