import json

from flask import current_app, g, request
from flask.json import jsonify

from ihome import constants, db, redis_store
from ihome.api_1_0 import api
from ihome.models import Area, House, Facility, HouseImage
from ihome.utils.common import login_required
from ihome.utils.response_code import RET
from ihome.utils.image_store import storage


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
            current_app.logger.info('hit area into redis')
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


@api.route('/house/info', methods=['POST'])
@login_required
def save_house_info():
    """保存新发布的房源信息， 包括该房源的设备信息"""
    # 1. 获取房源基本信息参数
    user_id = g.user_id
    house_data = request.get_json()

    title = house_data.get('title')
    price = house_data.get('price')
    area_id = house_data.get('area_id')
    address = house_data.get('address')
    room_count = house_data.get('room_count')
    acreage = house_data.get('acreage')
    unit = house_data.get('unit')
    capacity = house_data.get('capacity')
    beds = house_data.get('beds')
    deposit = house_data.get('deposit')
    min_days = house_data.get('min_days')
    max_days = house_data.get('max_days')

    # 2. 校验参数
    if not all(
            [title, price, area_id, address, room_count, acreage, unit,
             capacity, beds, deposit, min_days, max_days]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    try:
        price = int(float(price) * 100)
        deposit = int(float(deposit) * 100)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    # 3. 检查区域id是否存在
    try:
        area = Area.query.get(area_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')

    if area is None:
        return jsonify(errno=RET.NODATA, errmsg='区域信息错误')

    house = House(
        user_id=user_id,
        area_id=area_id,
        title=title,
        price=price,
        address=address,
        room_count=room_count,
        acreage=acreage,
        unit=unit,
        capacity=capacity,
        beds=beds,
        deposit=deposit,
        min_days=min_days,
        max_days=max_days
    )

    # 4. 校验是否有设备，若有设备，设备id是否存在
    facility_ids = house_data.get('facility')
    if facility_ids:
        try:
            facilities = Facility.query.filter(
                Facility.id.in_(facility_ids)).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='保存数据异常')

        if facilities:
            house.facilities = facilities

    # 5. 保存房源信息到数据库
    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存数据异常')

    return jsonify(errno=RET.OK, errmsg='OK', data={"house_id": house.id})


@api.route('/house/image', methods=['POST'])
@login_required
def save_house_image():
    """保存房屋图片"""
    # 1. 获取图片
    image_file = request.files.get('house_image')
    house_id = request.form.get('house_id')
    print(image_file, house_id)
    # 2. 校验参数
    if not all([house_id, image_file]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')

    if house is None:
        return jsonify(errno=RET.NODATA, errmsg='房屋信息错误')

    # 3. 上传图片
    image_data = image_file.read()
    try:
        file_name = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='上传图片失败')

    # 4. 保存url到数据库
    house_image = HouseImage(
        house_id=house.id,
        url=file_name
    )
    db.session.add(house_image)

    # 处理房屋主图片
    if not house.index_image_url:
        house.index_image_url = file_name
        # 如果不是主图片，house表没有变动，不需要添加到session
        db.session.add(house)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.err(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存图片数据异常')

    image_url = constants.QINIU_URL_DOMAIN + file_name
    return jsonify(errno=RET.OK, errmsg='OK', data={'image_url': image_url})


@api.route('/user/houses', methods=['GET'])
@login_required
def get_user_houses():
    """获取用户房源"""
    user_id = g.user_id
    try:
        houses = House.query.filter_by(user_id=user_id).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库查询异常')

    house_list = []
    for house in houses:
        house_list.append(house.to_basic_dict())

    # 将数据转换成json字符串
    # rsp_dict = dict(errno=RET.OK, errmsg='OK', data=house_list)
    # rsp_json = json.dumps(rsp_dict)
    # return rsp_json, 200, {'Content-Type': 'application/json'}

    return jsonify(errno=RET.OK, errmsg='OK', data={'houses': house_list})


@api.route('/houses/index', methods=['GET'])
def get_house_index():
    """获取主页幻灯片的基本房屋信息"""
    # 1. 尝试从 redis 数据库获取主页房
    houses = None
    try:
        houses = redis_store.get('home_page_data')
    except Exception as e:
        current_app.logger.error(e)

    if houses:
        current_app.logger.info('hit house index info redis')
        # return jsonify(errno=RET.OK, errmsg='OK', data={'houses': houses})
        return '{"errno": 0, "errmsg": "OK", "data": %s}' % (houses.decode()),            200, {'Content-Type': 'application/json'}

    # 2. 如果没有从 mysql 数据库查询获得， 并将查询的数据放入redis中
    try:
        houses = House.query.order_by(
            House.order_count.desc()).limit(
            constants.HOME_PAGE_MAX_HOUSE).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据失败')

    if not houses:
        return jsonify(errno=RET.NODATA, errmsg='查询无数据')

    # 把house对象转换成字符串，存入redis缓存
    # [<house1>, <house2>, ...]
    house_list = []
    for house in houses:
        if house.index_image_url:
            house_list.append(house.to_basic_dict())
    house_json = json.dumps(house_list)  # '[{}, {}, {}]'
    try:
        redis_store.setex('home_page_data',
                          constants.HOME_PAGE_REDIS_CACHE_EXPIRES, house_json)
    except Exception as e:
        current_app.logger.error(e)
    return '{"errno": 0, "errmsg": "OK", "data": %s}' % house_json, 200,                {'Content-Type': 'application/json'}
