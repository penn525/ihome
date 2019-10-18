""" 用于开发模式浏览静态html文件的蓝图 """
from flask import Blueprint, current_app, make_response

from ihome.utils.common import csrf_wrap


html = Blueprint('web_html', __name__)


@html.route("/<re(r'.*'):html_file_name>")
@csrf_wrap
def get_html(html_file_name):
    """ 提供静态文件访问 """
    if not html_file_name:
        html_file_name = 'index.html'

    if html_file_name != 'favicon.ico':
        html_file_name = 'html/' + html_file_name

    # 前后端分离后，给rsp添加csrf的cookie
    # rsp = make_response(current_app.send_static_file(html_file_name))
    # rsp.set_cookie('csrf_token', csrf.generate_csrf())
    # return rsp

    return current_app.send_static_file(html_file_name)
