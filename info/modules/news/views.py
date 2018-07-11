from flask import current_app
from flask import g
from flask import render_template
from flask import session

from info.models import User
from info.utils.commons import user_login_data
from . import news_blu


# 新闻详情展示
@news_blu.route('/<int:news_id>')
@user_login_data
def new_details(news_id):

    # # 获取用户编号
    # user_id = session.get("user_id")
    #
    # # 查询用户对象
    # user = None
    # try:
    #     user = User.query.get(user_id)
    # except Exception as e:
    #     current_app.logger.error(e)
    # 拼接数据，渲染到页面
    data = {
        "user_info":g.user.to_dict() if g.user else ""
    }

    return render_template("news/detail.html",data=data)
