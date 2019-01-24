from celery_tasks.sms.yuntongxun.sms import CCP
from celery_tasks.sms.yuntongxun import constants
from celery_tasks.main import celery_app


@celery_app.task(name='sms_code')
def send_sms_code(mobile, sms_code):
    """
    发送短信验证码的异步任务函数
    :param mobile:
    :param sms_code:
    :return:
    """
    # CCP().send_template_sms(mobile, [sms_code, constants.YUNTONGXUN_EXPIRES], constants.YUNTONGXUN_TEMPLATE)
