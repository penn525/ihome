import json

from flask import current_app, g, request
from flask.json import jsonify

from ihome import constants, db, redis_store
from ihome.api_1_0 import api
from ihome.models import Area
from ihome.utils.common import login_required
from ihome.utils.response_code import RET


@api.route('/areas', methods=['GET'])
def get_areas():
    """查询全部区域
    由于区域访问频繁，但是更新不频繁，所以可以放入redis缓存
    """
    try:
        rsp_json = redis_store.get('area_info')
    except Exception as e:
        current_app.logger.error(e)
    else:
        if rsp_json is not None:
            current_app.logger.info('hit redis')
            return rsp_json, 200, {'Content-Type': 'application/json'}

    try:
        areas = Area.query.all()
    except Exception as e:
        current_app.logger.err(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库查询异常')

    areas_list = []
    for area in areas:
        areas_list.append(area.to_dict())

    # 将数据转换成json字符串
    rsp_dict = dict(errno=RET.OK, errmsg='OK', data=areas_list)
    rsp_json = json.dumps(rsp_dict)

    try:
        redis_store.setex(
            'area_info',
            constants.AREA_INFO_REDIS_CACHE_EXPIRES,
            rsp_json
        )
    except Exception as e:
        current_app.logger.error(e)

    return rsp_json, 200, {'Content-Type': 'application/json'}
