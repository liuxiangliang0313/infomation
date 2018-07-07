from . import index_blue
import logging
from  flask import current_app

@index_blue.route('/',methods=["GET",'POST'])
def hello_world():

    #测试redis存储数据
    # redis_store.set("name","itcast")

    #使用session存储数据,以后专门用户存储用户登陆信息(比如:用户名,手机号)
    # session["name"] = "banzhang"
    # print(session.get("name"))

    #如果使用print打印,在真实环境中,不需要输出, 但是有可能很多文件里面都写了print,如果驱逐是特别麻烦
    # print('jkfjdkfjkd')

    #使用日志文件对象输出
    logging.debug("调试内容")
    logging.info("详细信息")
    logging.warning("警告信息")
    logging.error("错误信息")

    #上面的输出内容,还可以使用current_app来输出,在控制台打印效果有下划线, 但是写入到文件一样
    # current_app.logger.debug("调试内容++")
    # current_app.logger.info("调试内容++")
    # current_app.logger.warning("调试内容++")
    # current_app.logger.error("调试内容++")


    return "helloworld100"