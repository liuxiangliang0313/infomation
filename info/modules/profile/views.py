from flask import current_app
from flask import g, jsonify
from flask import render_template
from flask import request

from info import constants
from info.constants import USER_COLLECTION_MAX_NEWS
from info.utils.commons import user_login_data
from info.utils.image_storage import image_storage
from info.utils.response_code import RET
from . import profile_blu


# 获取新闻收藏列表
# 请求路径: /user/ collection
# 请求方式:GET
# 请求参数:p(页数)
# 返回值: user_collection.html页面
@profile_blu.route('/collection')
@user_login_data
def collection():
    """
    1获取参数
    2转换参数类型
    3分页查询，得到分页对象
    4获取分页对象属性，总页数，当前页，对象列表
    5将对象列表转成字典列表
    6拼接数据，返回页面
    :return:
    """
    # 1获取参数
    page = request.args.get("p",1)

    # 2转换参数类型
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    # 3分页查询，得到分页对象
    try:
        paginate = g.user.collection_news.paginate(page, constants.USER_COLLECTION_MAX_NEWS,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询新闻失败")

    # 4获取分页对象属性，总页数，当前页，对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    # 5将对象列表转成字典列表
    news_list = []
    for news in items:
        news_list.append(news.to_dict())

    # 6拼接数据，返回页面
    data = {
        "totalPage":totalPage,
        "currentPage":currentPage,
        "news_list":news_list
    }
    return render_template("news/user_collection.html",data=data)


# 获取/设置用户密码
# 请求路径: /user/pass_info
# 请求方式:GET,POST
# 请求参数:GET无, POST有参数,old_password, new_password
# 返回值:GET请求: user_pass_info.html页面,data字典数据, POST请求: errno, errmsg
@profile_blu.route('/pass_info', methods=['GET', 'POST'])
@user_login_data
def pass_info():
    """
    1第一次进入GET请求，直接返回页面
    2获取参数
    3校验参数，旧密码正确性
    4修改新密码
    5返回响应
    :return:
    """
    # 1第一次进入GET请求，直接返回页面
    if request.method == "GET":
        return render_template("news/user_pass_info.html")

    # 2获取参数
    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")

    # 3校验参数，旧密码正确性
    if not all([old_password, new_password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    if not g.user.check_passowrd(old_password):
        return jsonify(errno=RET.DATAERR, errmsg="旧密码不正确")

    # 4修改新密码
    g.user.password = new_password

    # 5返回响应
    return jsonify(errno=RET.OK, errmsg="密码修改成功")


# 用户头像获取/设置
# 请求路径: /user/pic_info
# 请求方式:GET,POST
# 请求参数:无, POST有参数,avatar
# 返回值:GET请求: user_pci_info.html页面,data字典数据, POST请求: errno, errmsg,avatar_url
@profile_blu.route('/pic_info', methods=['GET', 'POST'])
@user_login_data
def pic_info():
    """
    1第一次进入GET请求，直接渲染页面
    2获取参数
    3校验参数，为空校验
    4上传图片
    5判断图片是否上传成功
    6设置用户图像
    7返回响应
    :return:
    """
    # 1第一次进入GET请求，直接渲染页面
    if request.method == "GET":
        return render_template("news/user_pic_info.html", user_info=g.user.to_dict())
    # 2获取参数
    file = request.files.get("avatar")

    # 3校验参数，为空校验
    if not file:
        return jsonify(errno=RET.NODATA, errmsg="图片不能为空")

    # 4上传图片
    try:
        # 读取图片为二进制流
        image_data = file.read()
        # 调用方法上传
        image_name = image_storage(image_data)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="图片上传失败")

    # 5判断图片是否上传成功
    if not image_name:
        return jsonify(errno=RET.DATAERR, errmsg="上传失败")

    # 6设置用户图像
    g.user.avatar_url = image_name

    # 7返回响应
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
    """
    1判断如果第一次进入，使用GET请求，直接返回页面即可
    2获取参数
    3校验参数，为空校验
    4更新用户信息
    5返回响应
    :return:
    """
    # 1判断如果第一次进入，使用GET请求，直接返回页面即可
    if request.method == "GET":
        return render_template('news/user_base_info.html', user_info=g.user.to_dict() if g.user else "")

    # 2获取参数
    nick_name = request.json.get("nick_name")
    signature = request.json.get("signature")
    gender = request.json.get("gender")

    # 3校验参数，为空校验
    if not all([nick_name, signature, gender]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    if not gender in ["MAN", "WOMAN"]:
        return jsonify(errno=RET.DATAERR, errmsg="性别异常")

    # 4更新用户信息
    g.user.signature = signature
    g.user.nick_name = nick_name
    g.user.gender = gender

    # 5返回响应
    return jsonify(errno=RET.OK, errmsg="修改成功")


# 展示个人中心页面
@profile_blu.route('/info')
@user_login_data
def user_info():
    # 判断用户是否登陆
    if not g.user:
        return render_template('/')

    # 拼接数据返回页面
    data = {
        "user_info": g.user.to_dict()
    }
    return render_template("news/user.html", data=data)
