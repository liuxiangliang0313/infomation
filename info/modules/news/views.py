from flask import abort
from flask import current_app, jsonify
from flask import g
from flask import render_template
from flask import request
from flask import session

from info import constants, db
from info.models import User, News, Comment, CommentLike
from info.utils.commons import user_login_data
from info.utils.response_code import RET
from . import news_blu


# 点赞/取消点赞
# 请求路径: /news/comment_like
# 请求方式: POST
# 请求参数:news_id,comment_id,action,g.user
# 返回值: errno,errmsg
# 参数解释:
@news_blu.route('/comment_like', methods=['POST'])
@user_login_data
def user_comment_like():
    """
    1判断用户是否登陆
    2获取参数
    3校验参数，为空校验，类型校验
    4根据评论编号查询评论对象
    5判断评论对象是否存在
    6根据操作类型，点赞，取消
    7返回响应
    :return:
    """
    # 1判断用户是否登陆
    if not g.user:
        return jsonify(errno=RET.NODATA, errmsg="该用户未登录")

    # 2获取参数
    comment_id = request.json.get("comment_id")
    action = request.json.get("action")

    # 3校验参数，为空校验，类型校验
    if not all([comment_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    if not action in ["add", "remove"]:
        return jsonify(errno=RET.DATAERR, errmsg="操作类型有误")

    # 4根据评论编号查询评论对象
    try:
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="评论查询失败")

    # 5判断评论对象是否存在
    if not comment:
        return jsonify(errno=RET.NODATA, errmsg="该评论不存在")

    # 6根据操作类型，点赞，取消
    try:
        if action == "add":
            # 查询用户是否有对该评论点过赞
            comment_like = CommentLike.query.filter(CommentLike.comment_id == comment_id,
                                                    CommentLike.user_id == g.user.id).first()
            if not comment_like:
                # 创建点赞对象，设置属性值
                comment_like = CommentLike()
                comment_like.comment_id = comment_id
                comment_like.user_id = g.user.id
                # 将当前点赞数量+1
                comment.like_count += 1
                # 添加到数据库
                db.session.add(comment_like)
                db.session.commit()
        else:
            # 查询用户是否有对该评论点过赞
            comment_like = CommentLike.query.filter(CommentLike.comment_id == comment_id,
                                                    CommentLike.user_id == g.user.id).first()
            if comment_like:
                # 从数据库删除
                db.session.delete(comment_like)
                # 将当前评论点赞数量-1
                comment.like_count -= 1
                db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="操作失败")

    # 7返回响应
    return jsonify(errno=RET.OK, errmsg="点赞成功")


# 评论/回复评论
# 请求路径: /news/news_comment
# 请求方式: POST
# 请求参数:news_id,comment,parent_id
# 返回值: errno,errmsg,评论字典
@news_blu.route('/news_comment', methods=['POST'])
@user_login_data
def news_comment():
    """
    1判断用户是否登陆
    2获取参数
    3校验参数，为空校验
    4根据编号取出新闻对象，并判断是否存在/
    5创建评论对象，设置评论对象属性
    6添加评论对象到数据库
    7返回响应
    :return:
    """

    # 1判断用户是否登陆
    if not g.user:
        return jsonify(errno=RET.NODATA, errmsg="该用户未登录")

    # 2获取参数
    news_id = request.json.get("news_id")
    content = request.json.get("comment")
    parent_id = request.json.get("parent_id")

    # 3校验参数，为空校验
    if not all([news_id, content]):
        return jsonify(errno=RET.NODATA, errmsg="参数不全")

    # 4根据编号取出新闻对象，并判断是否存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="新闻查询失败")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="该新闻不存在")

    # 5创建评论对象，设置评论对象属性
    comment = Comment()
    comment.user_id = g.user.id
    comment.news_id = news.id
    comment.content = content

    if parent_id:
        comment.parent_id = parent_id

    # 6添加评论对象到数据库
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="添加评论失败")

    # 7返回响应
    return jsonify(errno=RET.OK, errmsg="评论成功", data=comment.to_dict())


# 收藏/取消收藏
# 请求路径: /news/news_collect
# 请求方式: POST
# 请求参数:news_id,action, g.user
# 返回值: errno,errmsg
@news_blu.route('/news_collect', methods=["POST"])
@user_login_data
def news_collect():
    """
    1判断用户是否登陆
    2取出参数
    3校验参数，为空校验，参数类型校验
    4根据编号查询新闻是否存在
    5根据操作类型，收藏，取消收藏
    6返回响应
    :return:
    """
    # 1判断用户是否登陆
    if not g.user:
        return jsonify(errno=RET.NODATA, errmsg="该用户未登录")

    # 2取出参数
    news_id = request.json.get("news_id")
    action = request.json.get("action")

    # 3校验参数，为空校验，参数类型校验
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")
    if not action in ["collect", "cancel_collect"]:
        return jsonify(errno=RET.DATAERR, errmsg="类型有误")

    # 4根据编号查询新闻是否存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="新闻查询异常")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="该新闻不存在")

    # 5根据操作类型，收藏，取消收藏
    try:
        if action == "collect":
            g.user.collection_news.append(news)
        else:
            g.user.collection_news.remove(news)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="操作失败")

    # 6返回响应
    return jsonify(errno=RET.OK, errmsg="操作成功")


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

    # 根据编号，获取新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="新闻查询失败")
    # 判断新闻是否存在
    if not news:
        abort(404)

    # 将新闻点击量家+1
    news.clicks += 1

    # 查询热门新闻列表，取前10条
    try:
        news_items = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="热门新闻查询失败")

    # 将新闻对象列表转成字典列表
    clicks_news_list = []
    for item in news_items:
        clicks_news_list.append(item.to_dict())

    # 判断用户是否有收藏该新闻
    is_collected = False
    # 如果用户登录，并且该新闻在用户收藏列表中，说明已收藏
    if g.user and news in g.user.collection_news:
        is_collected = True

    # 获取该新闻的所有评论内容
    try:
        comments = Comment.query.filter(Comment.news_id == news.id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取评论失败")

    # 记录点赞过的评论编号
    my_comment_like_ids = []
    if g.user:
        # 获取当前新闻到所有评论列表编号
        comment_ids = [comm.id for comm in comments]

        # 获取到当前新闻所有的评论的所有赞对象列表
        # 条件1：找到当前新闻的所有赞
        # 条件2：过滤出了某个人
        comment_like_list = CommentLike.query.filter(CommentLike.comment_id.in_(comment_ids),
                                                     CommentLike.user_id == g.user.id).all()

        # 获取到用户对当前新闻，点赞过的评论编号
        my_comment_like_ids = [comment_like.comment_id for comment_like in comment_like_list]

    # 将评论对象列表转成字典列表
    comment_list = []
    for comment in comments:
        comm_dict = comment.to_dict()
        # 假设对每条评论都没有点过赞
        comm_dict["is_like"] = False
        # 判断用户是否有点赞
        if g.user and comment.id in my_comment_like_ids:
            comm_dict["is_like"] = True

        comment_list.append(comm_dict)

    # 拼接数据，渲染到页面
    data = {
        "user_info": g.user.to_dict() if g.user else "",
        "news": news.to_dict(),
        "clicks_news_list": clicks_news_list,
        "is_collected": is_collected,
        "comments": comment_list
    }

    return render_template("news/detail.html", data=data)
