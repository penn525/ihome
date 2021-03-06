import re

from flask import current_app, request, session
from flask.json import jsonify
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash

from ihome import db, redis_store, constants
from ihome.api_1_0 import api
from ihome.models import User
from ihome.utils.response_code import RET


@api.route('/users', methods=['POST'])
def register():
    """
    用户注册
    :return:
    """
    # 1. 检查参数缺失
    req_dict = request.get_json()
    print(req_dict)
    mobile = req_dict.get('mobile')
    password = req_dict.get('password')
    password2 = req_dict.get('password2')
    sms_code = req_dict.get('sms_code')

    if not all([mobile, password, password2, sms_code]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    # 2. 业务处理
    # 检查手机号
    if not re.match(r'1[345789]\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号码格式错误')

    # 检查密码是否一致
    if password != password2:
        return jsonify(errno=RET.PWDERR, errmsg='两次密码不一致')

    # 检查短信验证码是否正确
    try:
        real_sms_code = int(redis_store.get(f'sms_code_{mobile}'))
    except Exception as e:
        return jsonify(errno=RET.DBERR, errmsg='读取真实手机验证码错误')

    if real_sms_code is None:
        return jsonify(errno=RET.NODATA, errmsg='短信验证码失效')

    # 删除短信验证码，防止重复利用
    try:
        redis_store.delete(f'sms_code_{mobile}')
    except Exception as e:
        current_app.logger.error(e)

    # print(real_sms_code, sms_code)
    if real_sms_code == sms_code:
        return jsonify(errno=RET.DATAERR, errmsg='短信验证码错误')

    # 3. 检查手机唯一性
    # try:
    #     user = User.query.filter_by(mobile=mobile).first()
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=RET.DATAEXIST, errmsg='手机已注册')

    # 4. 保存用户信息
    user = User(name=mobile, mobile=mobile)
    user.password = password

    try:
        db.session.add(user)
        db.session.commit()
    # 由于手机号码具有唯一性， 一旦重复插入就会报错， 利用此性质， 不需要进行查询
    # 会抛出 IntegrityError 异常，减少数据库操作
    except IntegrityError as e:
        db.session.rollback()
        # 手机号重复
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST, errmsg='手机已注册')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')

    # 保存登录状态到session中
    session['name'] = mobile
    session['mobile'] = mobile
    session['user_id'] = user.id

    return jsonify(errno=RET.OK, errmsg='注册成功')


@api.route('/session', methods=['POST'])
def login():
    """用户登录"""
    # 1. 获取参数
    req_dict = request.get_json()
    mobile = req_dict.get('mobile')
    password = req_dict.get('password')

    # 2. 检验参数
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')

    if not re.match(r'1[345789]\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号码格式不正确')

    # 检查用户重试登录次数, 限制ip, 而不是手机
    user_ip = request.remote_addr
    try:
        access_nums = redis_store.get(f'access_num_{user_ip}')
    except Exception as e:
        current_app.logger.error(e)
    else:
        if access_nums is not None and \
            int(access_nums) >= constants.LOGIN_ERROR_MAX_TIMES:
            return jsonify(errno=RET.IPERR, errmsg='登录次数过多，请稍后重试')

    # 3.查询用户是否存在
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取用户信息失败')

    if user is None or not check_password_hash(user.password_hash, password):
        try:
            redis_store.incr(f'access_num_{user_ip}')
            redis_store.expire(
                f'access_num_{user_ip}', 
                constants.LOGIN_ERROR_FORBID_TIME
            )
        except Exception as e:
            current_app.logger.error(e)
        return jsonify(errno=RET.USERERR, errmsg='用户名或密码错误')

    # 5. 保存到session
    session['name'] = user.name
    session['mobile'] = mobile
    session['user_id'] = user.id

    return jsonify(errno=RET.OK, errmsg='登录成功')


@api.route('/session', methods=['GET'])
def check_login():
    """检查用户登录状态"""
    name = session.get('name')
    if name is None:
        return jsonify(errno=RET.SESSIONERR, errmsg='false')
    return jsonify(errno=RET.OK, errmsg='true', data={'name': name})


@api.route('/session', methods=['DELETE'])
def logout():
    """用户登出"""
    csrf_token = session['csrf_token']
    session.clear()
    session['csrf_token'] = csrf_token
    return jsonify(errno=RET.OK, errmsg='OK')
