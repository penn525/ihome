import os

from flask import request, session, g, jsonify, current_app
from alipay import AliPay, ISVAliPay

from ihome.api_1_0 import api
from ihome.models import Order
from ihome.utils.response_code import RET
from ihome.utils.common import login_required
from ihome import constants, db


@api.route('/orders/<int:order_id>/payment', methods=['POST'])
@login_required
def order_pay(order_id):
    """支付宝订单支付
    @param order_id: 订单编号
    """
    user_id = g.user_id

    # 创建支付宝对象
    alipay = AliPay(
        appid="2016101700707698",
        app_private_key_path=os.path.join(os.path.dirname(__file__),
                                        'keys/app_private_key.pem'),
        alipay_public_key_path=os.path.join(os.path.dirname(__file__),
                                            'keys/alipay_public_key.pem'),
        sign_type="RSA2",
        app_notify_url=None,
        debug=True
    )

    # 判断订单状态
    try:
        order = Order.query.filter(
            Order.id == order_id, Order.user_id == user_id, Order.status == "WAIT_PAYMENT").first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')

    if order is None:
        return jsonify(errno=RET.NODATA, errmsg='订单不存在')

    # 手机网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
    order_string = alipay.api_alipay_trade_wap_pay(
        out_trade_no=order.id,
        total_amount=str(order.amount/100.0),
        subject=f'爱家租房-{order.id}',
        timeout_express='15m',
        return_url="http://127.0.0.1:5000/payComplete.html",
        notify_url=None  # 可选, 不填则使用默认notify url
    )

    # 构建支付宝支付链接， 发送给用户
    pay_url = constants.ALIPAY_URL_PREFIX + order_string

    return jsonify(errno=RET.OK, errmsg='OK', data={'pay_url': pay_url})


@api.route('/order/payment', methods=['PUT'])
def save_order_payment_result():
    """保存订单支付结果"""

    data = request.form.to_dict()
    # sign 不能参与签名验证
    signature = data.pop("sign")

    # 创建支付宝对象
    alipay = AliPay(
        appid="2016101700707698",
        app_private_key_path=os.path.join(os.path.dirname(__file__),
                                        'keys/app_private_key.pem'),
        alipay_public_key_path=os.path.join(os.path.dirname(__file__),
                                            'keys/alipay_public_key.pem'),
        sign_type="RSA2",
        app_notify_url=None,
        debug=True
    )

    # verify
    success = alipay.verify(data, signature)
    if success:
        # 修改订单状态
        order_id = data.get('out_trade_no')
        trade_no = data.get('trade_no')
        try:
            Order.query.filter_by(id=order_id).update(
                {'status': 'WAIT_COMMENT', 'trade_no': trade_no})
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()

    return jsonify(errno=RET.OK, errmsg='OK')
