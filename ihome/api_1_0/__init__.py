from flask import Blueprint


api = Blueprint('api_1_0', __name__)

# 导入蓝图的视图
from ihome.api_1_0 import (demo, verify_code, passport,
                           profile, houses, orders, pay)