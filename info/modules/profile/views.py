from flask import g, jsonify
from flask import render_template
from flask import request

from info.utils.commons import user_login_data
from info.utils.response_code import RET
from . import profile_blu

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
    :return:
    """
    # 1第一次进入GET请求，直接渲染页面
    if request.method == "GET":
        return render_template("news/user_pic_info.html",user_info=g.user.to_dict())
    # 2获取参数
    # 3校验参数，为空校验




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
