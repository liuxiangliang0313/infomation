# 公用内容写在此处

# 过滤器，过滤热门新闻颜色

from functools import wraps

from flask import current_app
from flask import g
from flask import session


def news_class_filter(index):
    if index == 1:
        return 'first'
    elif index == 2:
        return 'second'
    elif index == 3:
        return 'third'
    else:
        ""


# 登陆装饰器，用来封装用户登录的数据
def user_login_data(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):

        # 获取用户编号
        user_id = session.get("user_id")

        # 查询用户对象
        from info.models import User
        user = None
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

        # 将用户对象添加到g对象
        g.user = user

        return view_func(*args, **kwargs)

    return wrapper
