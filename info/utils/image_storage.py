from qiniu import Auth, put_file, etag, put_data
import qiniu.config

# 需要填写你的 Access Key 和 Secret Key
access_key = 'Hn96PWs8U8QiSfVsmIlb__CrpTJrDRqbgeASN8Qx'
secret_key = 'chRHdO8n5XIBVxX7urzjIVgBUg8ws1KWUxFAolfu'

# 构建鉴权对象
q = Auth(access_key, secret_key)

# 要上传的空间
bucket_name = 'infomation'

# 上传到七牛后保存的文件名,如果不写由七牛云维护
# key = 'my-python-logo.png';
key = None

# 生成上传 Token，可以指定过期时间等
token = q.upload_token(bucket_name, key, 3600)


# 要上传文件的本地路径
def image_storage(image_data):
    # localfile = './111.jpg'
    # ret, info = put_file(token, key, localfile)

    ret, info = put_data(token, key, image_data)

    # 判断图片是否上传成功
    if info.status_code == 200:
        return ret.get("key")
    else:
        return ""

        # print(info)
        # print(ret)


# 测试
if __name__ == '__main__':
    # file = open('111.jpg','rb')
    # image_storage(file.read())

    with open("111.jpg", 'rb') as file:
        print(image_storage(file.read()))
