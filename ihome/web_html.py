""" 用于开发模式浏览静态html文件的蓝图 """
from flask import Blueprint, current_app

html = Blueprint('web_html', __name__)


@html.route("/<re(r'.*'):html_file_name>")
def get_html(html_file_name):
    """ 提供静态文件访问 """
    if not html_file_name:
        html_file_name = 'index.html'
    
    if html_file_name != 'favicon.ico':
        html_file_name = 'html/' + html_file_name

    return current_app.send_static_file(html_file_name)
