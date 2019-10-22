from flask import current_app, g, request
from flask.json import jsonify

from ihome import constants, db
from ihome.api_1_0 import api
from ihome.models import User
from ihome.utils.common import login_required
from ihome.utils.image_store import storage
from ihome.utils.response_code import RET


@api.route('/users/avatar', methods=['POST'])
@login_required
def set_user_avatar():
    """
    设置用户头像
    参数： 图片（表单格式）， 用户id
    """
    # 1. 获取参数
    user_id = g.user.id
    image_file = request.files.get('avatar')

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
        g.user.update({'avatar_url': file_name})
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
