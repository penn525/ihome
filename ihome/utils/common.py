from functools import wraps

from flask import g, make_response, session
from flask.json import jsonify
from flask_wtf import csrf
from werkzeug.routing import BaseConverter


class ReConverter(BaseConverter):
    """ 自定义re转换器 """

    def __init__(self, url_map, regex):
        super().__init__(url_map)
        # 保存正则表达式
        self.regex = regex


def login_required(view):
    """
    登录状态检查装饰器,并保存用户状态
    :param view: 视图函数
    :return 未登录: 返回session错误； 已登录: 返回被装饰的视图函数
    """
    @wraps(view)
    def view_wrapper(*args, **kwargs):
        from ihome.models import User
        from ihome.utils.response_code import RET
        g.user = None
        user_id = session.get('user_id')
        if user_id is None:
            return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')
        try:
            g.user = User.query.get(user_id)
        except Exception as e:
            return jsonify(errno=RET.DBERR, errmsg='读取用户信息异常')
        return view(*args, **kwargs)

    return view_wrapper


def csrf_wrap(view):
    """ csrf保护装饰器，第一次访问时，对rsp添加csrf_token """
    @wraps(view)
    def view_wrapper(*args, **kwargs):
        rsp = view(*args, **kwargs)
        rsp.set_cookie('csrf_token', csrf.generate_csrf())
        # print(rsp)
        return make_response(rsp)

    return view_wrapper
