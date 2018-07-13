from flask import g
from flask import render_template

from info.utils.commons import user_login_data
from . import profile_blu


# 基本资料展示
# 请求路径: /user/base_info
# 请求方式:GET,POST
# 请求参数:POST请求有参数,nick_name,signature,gender
# 返回值:errno,errmsg
@profile_blu.route('/base_info')
@user_login_data
def base_info():
    return render_template('news/user_base_info.html',user_info=g.user.to_dict() if g.user else "")


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
