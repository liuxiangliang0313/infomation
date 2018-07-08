from . import passport_blue
from info.utils.captcha.captcha import captcha
#生成图片验证码
#请求路径:/passport/image_code
#请求方式:GET
#请求参数:随机字符串
#返回值: 图片验证码
@passport_blue.route('/image_code')
def get_image_code():

    #生成图片验证码
    name,text,image_data =  captcha.generate_captcha()

    #返回图片验证码
    return image_data

