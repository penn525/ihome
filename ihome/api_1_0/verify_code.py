from random import randint

from flask import current_app, make_response, request
from flask.json import jsonify

from ihome import constants, db, redis_store
from ihome.api_1_0 import api
from ihome.models import User
from ihome.tasks.task_sms import send_sms
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
        return jsonify(errno=RET.DBERR, errmsg='保存图片验证码失败！')

    # 4. 返回
    rsp = make_response(image_data)
    rsp.headers['Content-Type'] = 'image/jpg'
    return rsp


@api.route('/sms_code/<re(r"1[345789]\d{9}"):mobile_num>')
def get_sms_code(mobile_num):
    """
    验证图片验证码， 再发送手机短信验证码
    :param mobile_num 手机号码
    :return sms_code 手机验证码
    """
    # 1. 验证图片验证码
    image_code = request.args.get('image_code')
    image_code_id = request.args.get('image_code_id')

    # 检验参数完整性
    if not all([image_code_id, image_code]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    # 检验参数正确性
    try:
        real_image_code = redis_store.get(f'image_code_{image_code_id}')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='redis数据库异常')

    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg='图片验证码失效')

    # 删除redis中图片验证码，防止用户多次尝试, 生产环境开启
    try:
        redis_store.delete(f'image_code_{image_code_id}')
    except Exception as e:
        current_app.logger.error(e)

    if real_image_code.lower() == image_code.lower():
        return jsonify(errno=RET.DATAERR, errmsg='图片验证失败')

    # 验证手机是否在一分钟内已发送验证码，限制一分钟内只能发送一次
    try:
        send_flag = redis_store.get(f'send_sms_code_{mobile_num}')
    except Exception as e:
        current_app.logger.error(e)
    else:
        if send_flag:
            return jsonify(errno=RET.REQERR, errmsg='请求过于频繁，请60秒后重试')

    # 2. 验证手机是否以注册
    try:
        user = User.query.filter_by(mobile=mobile_num).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')
    else:
        if user is not None:
            return jsonify(errno=RET.DATAEXIST, errmsg='手机已注册，请直接登录')

    # 3. 验证通过，保存到redis中
    sms_code = '%06d' % randint(0, 999999)

    try:
        redis_store.setex(
            f'sms_code_{mobile_num}',
            constants.SMS_CODE_REDIS_EXPIRES,
            sms_code
        )
        # 保存手机发送短信验证码的记录，限制60秒内重复发送
        redis_store.setex(
            f'send_sms_code_{mobile_num}',
            constants.SEND_SMS_CODE_INTERVAL,
            1
        )
    except Exception as e:
        return jsonify(errno=RET.DBERR, errmsg='redis数据库异常')

    # 4. 发送手机验证码
    # try:
    #     status = ccp.send_template_sms(
    #         mobile_num,
    #         [sms_code, str(constants.SMS_CODE_REDIS_EXPIRES//60)],
    #         1
    #     )
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=RET.THIRDERR, errmsg='短信发送异常')

    # celery 发布异步任务
    send_sms.delay(mobile_num, sms_code, str(
        constants.SMS_CODE_REDIS_EXPIRES//60), 1)

    return jsonify(errno=RET.OK, errmsg='短信发送成功')
