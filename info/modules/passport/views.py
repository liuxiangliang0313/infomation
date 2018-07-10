from flask import request, current_app, jsonify, make_response, json, session
import random
from info import redis_store, constants, db
from info.libs.yuntongxun.sms import CCP
from info.models import User
from info.utils.response_code import RET
from . import passport_blue
from info.utils.captcha.captcha import captcha
import re


# 退出登陆
# 请求路径: /passport/logout
# 请求方式: DELETE
# 请求参数: 无
# 返回值: errno, errmsg
@passport_blue.route('/logout', methods=['DELETE'])
def logout():
    # 清除session信息
    session.pop("user_id", None)
    session.pop("nick_name", None)
    session.pop("mobile", None)

    return jsonify(errno=RET.OK, errmsg="退出成功")


# 登陆用户
# 请求路径: /passport/login
# 请求方式: POST
# 请求参数: mobile,password
# 返回值: errno, errmsg
@passport_blue.route('/login', methods=['POST'])
def login():
    """
    思路分析:
    1.获取参数
    2.校验参数
    3.根据手机号取出用户对象
    4.判断密码正确性
    5.将用户的登陆信息存到session
    6.返回响应
    :return: 
    """
    # 1.获取参数
    dict_data = request.get_json()
    mobile = dict_data.get("mobile")
    password = dict_data.get("password")

    # 2.校验参数
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 3.根据手机号取出用户对象
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询用户失败")

    # 判断用户是否存在
    if not user:
        return jsonify(errno=RET.NODATA, errmsg="该用户不存在")

    # 4.判断密码正确性
    if not user.check_passowrd(password):
        return jsonify(errno=RET.DATAERR, errmsg="密码输入错误")

    # 5.将用户的登陆信息存到session
    session["user_id"] = user.id
    session["nick_name"] = user.nick_name
    session["mobile"] = user.mobile

    # 6.返回响应
    return jsonify(errno=RET.OK, errmsg="登陆成功")


# 注册用户
# 请求路径: /passport/register
# 请求方式: POST
# 请求参数: mobile, sms_code,password
# 返回值: errno, errmsg
@passport_blue.route('/register', methods=['POST'])
def register():
    """
    1.获取参数
    2.校验参数,为空校验
    3.手机号格式校验
    4.根据手机号取出redis中的短信验证码
    5.判断短信验证码是否过期
    6.校验短信验证码是否正确
    7.创建用户对象
    8.设置用户对象的属性信息
    9.保存用户到数据库
    10.返回响应信息
    :return:
    """
    # 1.获取参数
    # json_data = request.data
    # dict_data = json.loads(json_data)

    # 上面获取方式可以写成一句话dict_data = request.get_json() 和  dict_data = request.json 都行
    dict_data = request.json
    mobile = dict_data.get("mobile")
    sms_code = dict_data.get("sms_code")
    password = dict_data.get("password")

    # 2.校验参数,为空校验
    if not all([mobile, sms_code, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 3.手机号格式校验
    if not re.match('1[345678]\\d{9}', mobile):
        return jsonify(errno=RET.DATAERR, errmsg="手机号格式有误")

    # 4.根据手机号取出redis中的短信验证码
    try:
        redis_sms_code = redis_store.get("sms_code:%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取短信验证码失败")

    # 5.判断短信验证码是否过期
    if not redis_sms_code:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码已过期")

    # 6.校验短信验证码是否正确
    if sms_code != redis_sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码填写错误")

    # 7.创建用户对象
    user = User()

    # 8.设置用户对象的属性信息
    user.nick_name = mobile
    user.mobile = mobile
    user.password = password

    # 9.保存用户到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="用户创建失败")

    # 10.返回响应信息
    return jsonify(errno=RET.OK, errmsg="注册成功")


# 发送短信验证码
# 请求路径:/passport/sms_code
# 请求方式:POST
# 请求参数:手机号,图片验证码,图片验证码编号
# 返回值:返回响应状态
@passport_blue.route('/sms_code', methods=['POST'])
def send_message():
    """
    思路分析:
    1.接收参数
    2.校验参数,为空校验
    3.校验手机号格式是否正确
    4.通过验证码编号,取出图片验证码A
    5.判断验证码A是否过期
    6.判断图片验证码是否正确
    7.调用CCP发送短信方法
    8.判断短信是否发送成功
    9.保存短信到redis中
    10.返回发送的状态
    :return:
    """

    # 1.接收参数
    json_data = request.data
    dict_data = json.loads(json_data)
    mobile = dict_data.get("mobile")
    image_code = dict_data.get("image_code")
    image_code_id = dict_data.get("image_code_id")

    # 2.校验参数,为空校验
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 3.校验手机号格式是否正确
    if not re.match('1[345678]\\d{9}', mobile):
        return jsonify(errno=RET.DATAERR, errmsg="手机号格式有误")

    # 4.通过验证码编号,取出图片验证码A
    try:
        redis_image_code = redis_store.get("image_code:%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="redis获取异常")

    # 5.判断验证码A是否过期
    if not redis_image_code:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码过期")

    # 6.判断图片验证码是否正确,忽略大小写
    if image_code.upper() != redis_image_code.upper():
        return jsonify(errno=RET.DATAERR, errmsg="图片填写错误")

    # 7.调用CCP发送短信方法
    sms_code = "%06d" % random.randint(0, 999999)  # 生成6位数的随机短信验证码
    current_app.logger.error("短信验证码是 = %s" % sms_code)
    # try:
    #     ccp = CCP()
    #     #发送短信,有效期5分钟
    #     result =  ccp.send_template_sms(mobile,[sms_code,constants.SMS_CODE_REDIS_EXPIRES/60],1)
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=RET.THIRDERR,errmsg="云通讯发送异常")
    #
    # # 8.判断短信是否发送成功
    # if result == -1:
    #     return jsonify(errno=RET.DATAERR,errmsg="短信发送失败")

    # 9.保存短信到redis中
    try:
        redis_store.set("sms_code:%s" % mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="短信验证码保存异常")

    # 10.返回发送的状态
    return jsonify(errno=RET.OK, errmsg="短信发送成功")


# 生成图片验证码
# 请求路径:/passport/image_code
# 请求方式:GET
# 请求参数:随机字符串
# 返回值: 图片验证码
@passport_blue.route('/image_code')
def get_image_code():
    # 1.获取参数
    cur_id = request.args.get("cur_id")
    pre_id = request.args.get("pre_id")

    # 生成图片验证码
    name, text, image_data = captcha.generate_captcha()

    try:
        # 保存图片验证码到redis
        redis_store.set("image_code:%s" % cur_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)

        # 判断是否有上一个图片验证编号
        if pre_id:
            redis_store.delete("image_code:%s" % pre_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="redis操作异常")

    # 返回图片验证码
    response = make_response(image_data)
    response.headers["Content-Type"] = "image/jpg"
    return response
