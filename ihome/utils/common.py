from werkzeug.routing import BaseConverter
from functools import wraps
from flask import make_response
from flask_wtf import csrf


class ReConverter(BaseConverter):
    """ 自定义re转换器 """

    def __init__(self, url_map, regex):
        super().__init__(url_map)
        # 保存正则表达式
        self.regex = regex


def csrf_wrap(view):
    """ csrf保护装饰器，第一次访问时，对rsp添加csrf_token """
    @wraps(view)
    def view_wrapper(*args, **kwargs):
        rsp = view(*args, **kwargs)
        rsp.set_cookie('csrf_token', csrf.generate_csrf())
        print(rsp)
        return make_response(rsp)

    return view_wrapper
