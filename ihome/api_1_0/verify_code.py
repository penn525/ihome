from flask import current_app, make_response
from flask.json import jsonify

from ihome import constants, redis_store
from ihome.api_1_0 import api
from ihome.utils.captcha.captcha import captcha
from ihome.utils.response_code import RET


@api.route('/image_code/<image_code_id>')
def get_image_code(image_code_id):
    """ 
    获取图片验证码， 并将验证值保存到redis中
    :param image_code_id: 浏览器端带入的图片验证码编号
    :return 正常： 返回图片验证码， 异常：返回json
    """
    # 1. 业务处理逻辑

    # 2. 生成图片验证码
    # 名字， 真是文本， 图片二进制数据
    name, text, image_data = captcha.generate_captcha()

    # 3. 如果使用哈希表，只能同一设置过期时间，不合适
    # 将图片验证吗保存到redis中, 字符串
    try:
        redis_store.setex(
            f'image_code_{image_code_id}',
            constants.IMAGE_CODE_REDIS_EXPIRES,
            text
        )
    except Exception as e:
        current_app.logger.error(e)
        # 图片保存失败， 返回错误json
        return jsonify(error=RET.DBERR, errmsg='保存图片验证码失败！')

    # 4. 返回
    rsp = make_response(image_data)
    rsp.headers['Content-Type'] = 'image/jpg'
    return rsp
