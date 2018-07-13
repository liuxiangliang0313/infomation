from flask import g
from flask import render_template

from info.utils.commons import user_login_data
from . import profile_blu


# 展示个人中心页面
@profile_blu.route('/info', methods=['GET', 'POST'])
@user_login_data
def user_info():

    # 判断用户是否登陆
    if not g.user:
        return render_template('/')

    # 拼接数据返回页面
    data = {
        g.user.to_dict() if g.user else ""
    }
    return render_template("news/user.html", data=data)
