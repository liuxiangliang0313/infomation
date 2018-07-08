from flask import request, current_app, jsonify, make_response, json
import random
from info import redis_store, constants
from info.libs.yuntongxun.sms import CCP
from info.utils.response_code import RET
from . import passport_blue
from info.utils.captcha.captcha import captcha
import re

#发送短信验证码
#请求路径:/passport/sms_code
#请求方式:POST
#请求参数:手机号,图片验证码,图片验证码编号
#返回值:返回响应状态
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
    if not all([mobile,image_code,image_code_id]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不完整")

    # 3.校验手机号格式是否正确
    if not re.match('1[345678]\\d{9}',mobile):
        return jsonify(errno=RET.DATAERR,errmsg="手机号格式有误")

    # 4.通过验证码编号,取出图片验证码A
    try:
        redis_image_code = redis_store.get("image_code:%s"%image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="redis获取异常")

    # 5.判断验证码A是否过期
    if not redis_image_code:
        return jsonify(errno=RET.NODATA,errmsg="图片验证码过期")

    # 6.判断图片验证码是否正确,忽略大小写
    if image_code.upper() != redis_image_code.upper():
        return jsonify(errno=RET.DATAERR,errmsg="图片填写错误")

    # 7.调用CCP发送短信方法
    sms_code = "%06d"%random.randint(0,999999) #生成6位数的随机短信验证码
    current_app.logger.error("短信验证码是 = %s"% sms_code )
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
        redis_store.set("sms_code:%s"%mobile,sms_code,constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="短信验证码保存异常")
    
    # 10.返回发送的状态
    return jsonify(errno=RET.OK,errmsg="短信发送成功")



#生成图片验证码
#请求路径:/passport/image_code
#请求方式:GET
#请求参数:随机字符串
#返回值: 图片验证码
@passport_blue.route('/image_code')
def get_image_code():

    #1.获取参数
    cur_id = request.args.get("cur_id")
    pre_id = request.args.get("pre_id")

    #生成图片验证码
    name,text,image_data =  captcha.generate_captcha()

    try:
        #保存图片验证码到redis
        redis_store.set("image_code:%s"%cur_id,text,constants.IMAGE_CODE_REDIS_EXPIRES)

        #判断是否有上一个图片验证编号
        if pre_id:
            redis_store.delete("image_code:%s"%pre_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="redis操作异常")

    #返回图片验证码
    response = make_response(image_data)
    response.headers["Content-Type"] = "image/jpg"
    return response

