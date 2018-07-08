from flask import request, current_app, jsonify, make_response

from info import redis_store, constants
from info.utils.response_code import RET
from . import passport_blue
from info.utils.captcha.captcha import captcha
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

