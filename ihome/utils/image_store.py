# -*- coding: utf-8 -*-
# flake8: noqa

import qiniu.config
from qiniu import Auth, etag, put_data, put_file

access_key = 'Qh0FF9JxAbVuKl8yyJfvfXRWzApevTRGsFDvyFzI'
secret_key = 'gG_njCcsHm2JOlHGaLzrzHhe7q7k8VERRhELL8Bi'


def storage(file_data):
    """
    存储图片到七牛服务器
    :param file_data: 文件二进制码
    :return:
    """
    q = Auth(access_key, secret_key)

    bucket_name = 'ihome-2019'

    # # 上传文件到七牛后， 七牛将文件名和文件大小回调给业务服务器。
    # policy = {
    #     'callbackUrl': 'http://your.domain.com/callback.php',
    #     'callbackBody': 'filename=$(fname)&filesize=$(fsize)'
    # }

    token = q.upload_token(bucket_name, None, 3600)

    # localfile = '../static/images/home01.jpg'
    # ret, info = put_file(token, None, localfile)

    ret, info = put_data(token, None, file_data)

    if info.status_code == 200:
        return ret.get('key')
    else:
        raise Exception('上传图片失败')


if __name__ == "__main__":
    with open('../static/images/home01.jpg', 'rb') as f:
        file_data = f.read()
        storage(file_data)
