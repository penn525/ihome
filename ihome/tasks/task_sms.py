from celery import Celery

from ihome.libs.cloudcommunication.sms import CCP


celery_app = Celery('ihome', broker='redis://127.0.0.1:6379/1')


@celery_app.task
def send_sms(to, datas, expire, temp_id):
    """发送短信的celery异步任务"""
    ccp = CCP()
    status = ccp.send_template_sms(to, [datas, expire], temp_id)
