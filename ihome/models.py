from datetime import datetime

from werkzeug.security import generate_password_hash

from ihome import db, constants


class BaseModel(object):
    """模型基类，为每个模型补充创建时间与更新时间"""

    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now)


class User(BaseModel, db.Model):
    """用户"""

    __tablename__ = "ih_user_profile"

    id = db.Column(db.Integer, primary_key=True)  # 用户编号
    name = db.Column(db.String(32), unique=True, nullable=False)  # 用户暱称
    password_hash = db.Column(db.String(128), nullable=False)  # 加密的密码
    mobile = db.Column(db.String(11), unique=True, nullable=False)  # 手机号
    real_name = db.Column(db.String(32))  # 真实姓名
    id_card = db.Column(db.String(20))  # 身份证号
    avatar_url = db.Column(db.String(128))  # 用户头像路径
    houses = db.relationship("House", backref="user")  # 用户发布的房屋
    orders = db.relationship("Order", backref="user")  # 用户下的订单

    @property
    def password(self):
        # return self.password_hash
        raise AttributeError('改属性只能设置，不能读取')

    @password.setter
    def password(self, origin_password):
        self.password_hash = generate_password_hash(origin_password)

    def __repr__(self):
        return f'<User: {self.name}>'


class Area(BaseModel, db.Model):
    """城区"""

    __tablename__ = "ih_area_info"

    id = db.Column(db.Integer, primary_key=True)  # 区域编号
    name = db.Column(db.String(32), nullable=False)  # 区域名字
    houses = db.relationship("House", backref="area")  # 区域的房屋

    def __repr__(self):
        return f'<Area: {self.name}>'

    def to_dict(self):
        return {
            'aid': self.id,
            'aname': self.name
        }


# 房屋设施表，建立房屋与设施的多对多关系, 联合主键
house_facility = db.Table(
    "ih_house_facility",
    db.Column("house_id", db.Integer, db.ForeignKey(
        "ih_house_info.id"), primary_key=True),  # 房屋编号
    db.Column("facility_id", db.Integer, db.ForeignKey(
        "ih_facility_info.id"), primary_key=True)  # 设施编号
)


class House(BaseModel, db.Model):
    """房屋信息"""

    __tablename__ = "ih_house_info"

    id = db.Column(db.Integer, primary_key=True)  # 房屋编号
    user_id = db.Column(db.Integer, db.ForeignKey(
        "ih_user_profile.id"), nullable=False)  # 房屋主人的用户编号
    area_id = db.Column(db.Integer, db.ForeignKey(
        "ih_area_info.id"), nullable=False)  # 归属地的区域编号
    title = db.Column(db.String(64), nullable=False)  # 标题
    price = db.Column(db.Integer, default=0)  # 单价，单位：分
    address = db.Column(db.String(512), default="")  # 地址
    room_count = db.Column(db.Integer, default=1)  # 房间数目
    acreage = db.Column(db.Integer, default=0)  # 房屋面积
    unit = db.Column(db.String(32), default="")  # 房屋单元， 如几室几厅
    capacity = db.Column(db.Integer, default=1)  # 房屋容纳的人数
    beds = db.Column(db.String(64), default="")  # 房屋床铺的配置
    deposit = db.Column(db.Integer, default=0)  # 房屋押金
    min_days = db.Column(db.Integer, default=1)  # 最少入住天数
    max_days = db.Column(db.Integer, default=0)  # 最多入住天数，0表示不限制
    order_count = db.Column(db.Integer, default=0)  # 预订完成的该房屋的订单数
    index_image_url = db.Column(db.String(256), default="")  # 房屋主图片的路径
    facilities = db.relationship("Facility", secondary=house_facility)  # 房屋的设施
    images = db.relationship("HouseImage")  # 房屋的图片
    orders = db.relationship("Order", backref="house")  # 房屋的订单

    def __repr__(self):
        return f'<House: {self.title}>'

    def to_basic_dict(self):
        return {
            'id': self.id,
            'user_avatar': constants.QINIU_URL_DOMAIN + self.user.avatar_url if self.user.avatar_url else "",
            'area_name': self.area.name,
            'address': self.address,
            'title': self.title,
            'room_count': self.room_count,
            'order_count': self.order_count,
            'price': '%.2f' % (self.price/100),
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S'),
            'index_image_url': constants.QINIU_URL_DOMAIN + self.index_image_url if self.index_image_url else ""
        }

    def to_full_dict(self):
        house_dict = {
            'hid': self.id,
            'uid': self.user_id,
            'uname': self.user.name,
            'user_avatar': constants.QINIU_URL_DOMAIN + self.user.avatar_url if self.user.avatar_url else "",
            'title': self.title,
            'price': '%.2f' % (self.price/100),
            'address': self.address,
            'room_count': self.room_count,
            'acreage': self.acreage,
            'unit': self.unit,
            'capacity': self.capacity,
            'beds': self.beds,
            'deposit': '%.2f' % (self.deposit/100),
            'min_days': self.min_days,
            'max_days': self.max_days,
        }
        # 获取房屋图片url
        image_urls = []
        for image in self.images:
            image_urls.append(constants.QINIU_URL_DOMAIN + image.url)
        house_dict['image_urls'] = image_urls

        # 设备信息
        facilities = []
        for facility in self.facilities:
            facilities.append(facility.id)
        house_dict['facilities'] = facilities

        # 评论信息
        # 订单完成，且评论不为空的最新20跳评论
        comments = []
        orders = Order.query.filter(Order.house_id == self.id,
                                    Order.status == 'COMPLETE',
                                    Order.comment != None).order_by(
            Order.create_time.desc()).limit(constants.HOUSE_DETAIL_COMMENTS_DISPLAY_COUNT)
        for order in orders:
            comment = {
                'user_name': order.user.name if order.user.name != order.user.mobile else '匿名用户',
                'comment': order.comment,
                'ctime': order.update_time.strftime('%Y-%m-%d %H:%M:%S')
            }
            comments.append(comment)
        house_dict['comments'] = comments

        return house_dict


class Facility(BaseModel, db.Model):
    """设施信息"""

    __tablename__ = "ih_facility_info"

    id = db.Column(db.Integer, primary_key=True)  # 设施编号
    name = db.Column(db.String(32), nullable=False)  # 设施名字


class HouseImage(BaseModel, db.Model):
    """房屋图片"""

    __tablename__ = "ih_house_image"

    id = db.Column(db.Integer, primary_key=True)
    house_id = db.Column(db.Integer, db.ForeignKey(
        "ih_house_info.id"), nullable=False)  # 房屋编号
    url = db.Column(db.String(256), nullable=False)  # 图片的路径


class Order(BaseModel, db.Model):
    """订单"""

    __tablename__ = "ih_order_info"

    id = db.Column(db.Integer, primary_key=True)  # 订单编号
    user_id = db.Column(db.Integer, db.ForeignKey(
        "ih_user_profile.id"), nullable=False)  # 下订单的用户编号
    house_id = db.Column(db.Integer, db.ForeignKey(
        "ih_house_info.id"), nullable=False)  # 预订的房间编号
    begin_date = db.Column(db.DateTime, nullable=False)  # 预订的起始时间
    end_date = db.Column(db.DateTime, nullable=False)  # 预订的结束时间
    days = db.Column(db.Integer, nullable=False)  # 预订的总天数
    house_price = db.Column(db.Integer, nullable=False)  # 房屋的单价
    amount = db.Column(db.Integer, nullable=False)  # 订单的总金额
    status = db.Column(  # 订单的状态
        db.Enum(
            "WAIT_ACCEPT",  # 待接单,
            "WAIT_PAYMENT",  # 待支付
            "PAID",  # 已支付
            "WAIT_COMMENT",  # 待评价
            "COMPLETE",  # 已完成
            "CANCELED",  # 已取消
            "REJECTED"  # 已拒单
        ),
        default="WAIT_ACCEPT", index=True)
    comment = db.Column(db.Text)  # 订单的评论信息或者拒单原因
