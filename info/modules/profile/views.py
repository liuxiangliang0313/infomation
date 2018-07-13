from flask import render_template

from info.utils.commons import user_login_data
from . import profile_blu


# 展示个人中心页面
@profile_blu.route('/info', methods=['GET', 'POST'])
@user_login_data
def user_info():
    return render_template("news/user.html",data={})
