from flask import Blueprint


api = Blueprint('api_1_0', __name__)

from ihome.api_1_0 import demo
