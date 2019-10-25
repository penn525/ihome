from flask import current_app, g, request, session
from flask.json import jsonify
from sqlalchemy.exc import IntegrityError

from ihome import constants, db
from ihome.api_1_0 import api
from ihome.models import User
from ihome.utils.common import login_required
from ihome.utils.image_store import storage
from ihome.utils.response_code import RET


@api.route('/user/avatar', methods=['POST'])
@login_required
def set_user_avatar():
    """
    设置用户头像
    参数： 图片（表单格式）， 用户id
    """
    # 1. 获取参数
    user_id = g.user_id
    image_file = request.files.get('avatar')

    if user_id is None:
        return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')

    if image_file is None:
        return jsonify(errno=RET.PARAMERR, errmsg='没有选择图片')
    # 2. 上传图片
    try:
        image_data = image_file.read()
        file_name = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='上传头像失败')

    # 3. 更新数据库用户信息
    try:
        User.query.filter_by(id=user_id).update({'avatar_url': file_name})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存图片信息失败')

    # 4. 设置用户头像 avatar_url
    return jsonify(
        errno=RET.OK,
        errmsg='上传头像成功',
        data={'avatar_url': constants.QINIU_URL_DOMAIN+file_name}
    )


@api.route('/user/name', methods=['PUT'])
@login_required
def set_user_name():
    """设置用户名称"""
    # 1. 校验参数完整性
    user_id = g.user_id

    if user_id is None:
        return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')

    name = request.get_json().get('name')

    try:
        user = User.query.get(user_id)
    except Exception as e:
        pass
    if name is None:
        return jsonify(errno=RET.PARAMERR, errmsg='请填写用户名')

    # 2. 保存用户数据
    try:
        # 2） 查询的 BaseQuery 对象的 update 方法进行保存
        User.query.filter_by(id=user_id).update({'name': name})
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST, errmsg='用户名已存在，请重新设置')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存用户名失败')
    session['name'] = name
    g.name = name
    return jsonify(errno=RET.OK, errmsg='保存成功', data={'name': name})


@api.route('/user', methods=['GET'])
@login_required
def get_user_profile():
    """获取用户信息"""
    user_id = g.user_id

    if user_id is None:
        return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')

    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取用户信息失败')

    if user.avatar_url is None:
        avatar_url = ''
    else:
        avatar_url = constants.QINIU_URL_DOMAIN + user.avatar_url

    user_info = {
        "name": user.name,
        "mobile": user.mobile,
        "avatar_url": avatar_url,
        "real_name": user.real_name,
        "id_card": user.id_card
    }

    return jsonify(
        errno=RET.OK,
        errmsg='获取用户信息成功',
        data={'user': user_info}
    )


@api.route('/user/auth', methods=['PUT'])
@login_required
def user_auth():
    """用户实名认证, 只能更改一次"""
    req_json = request.get_json()
    user_id = g.user_id
    real_name = req_json.get('real_name')
    id_card = req_json.get('id_card')

    if not all([real_name, id_card]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    if user_id is None:
        return jsonify(errno=RET.SESSIONERR, errmsg='获取用户信息失败')

    try:
        User.query.filter_by(id=user_id, real_name=None, id_card=None).update(
            {'real_name': real_name, 'id_card': id_card})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库操作失败')

    data = {'real_name': real_name, 'id_card': id_card}
    return jsonify(errno=RET.OK, errmsg='实名认证成功', data=data)


@api.route('/user/auth', methods=['GET'])
@login_required
def get_user_auth():
    """查询用户认证信息"""
    user_id = g.user_id

    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库操作失败')

    real_name = user.real_name
    id_card = user.id_card

    if not all([real_name, id_card]):
        return jsonify(errno=RET.DATAERR, errmsg='未进行实名认证')

    return jsonify(
        errno=RET.OK,
        errmsg='获取认证信息成功',
        data={
            'real_name': real_name,
            'id_card': id_card
        }
    )
