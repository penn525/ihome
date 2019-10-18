import logging

from flask import current_app

from . import api


@api.route('/index')
def index():
    # logging.info('info info')
    # logging.warn('warn info')
    # current_app.logger.debug('debug info')
    # current_app.logger.error('error info')
    return 'index page'
