# -*- coding: utf-8 -*-
# flake8: noqa
from qiniu import Auth, put_file, etag
import qiniu.config

# 需要填写你的 Access Key 和 Secret Key
from qiniu import put_data

access_key = 'Hn96PWs8U8QiSfVsmIlb__CrpTJrDRqbgeASN8Qx'
secret_key = 'chRHdO8n5XIBVxX7urzjIVgBUg8ws1KWUxFAolfu'
# 构建鉴权对象
q = Auth(access_key, secret_key)
# 要上传的空间
bucket_name = 'infomation'
# 上传到七牛后保存的文件名
key = None
# 生成上传 Token，可以指定过期时间等
token = q.upload_token(bucket_name, key, 3600)


# 要上传文件的本地路径
def image_storage(image_data):
    # localfile = './bbb.jpg'
    ret, info = put_data(token, key, image_data)
    if info.status_code == 200:
        return ret.get("key")
    else:
        return ""
    # print(info)
if __name__ == '__main__':
    with open('11.jpg','rb') as file:
        image_storage(file.read())