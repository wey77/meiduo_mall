import random

from rest_framework.views import APIView
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework import status

from meiduo.utils.exceptions import logger
from . import constants
from celery_tasks.sms.tasks import send_sms_code


#   GET /sms_codes/(?P<mobile>1[3-9]\d{9})/
class SMSCodeView(APIView):
    """
        获取短信验证码的视图
    """

    def get(self, request, mobile):
        # 链接到redis数据库
        redis_conn = get_redis_connection('verify_code')

        # 判断已为当前手机号发送验证码
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        # 如果短信发送标志存在则不产生新验证码
        if send_flag:
            return Response({'message': '频繁发送短信'}, status=status.HTTP_400_BAD_REQUEST)

        # 生成六位数字验证码
        sms_code = '%06d' % random.randint(0, 999999)
        logger.info(sms_code)

        # 创建数据库管道
        pl = redis_conn.pipeline()

        # 把当前手机号与短信验证码保存到redis数据库
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)

        # 将当前手机号标记为：已发短信验证码
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        pl.execute()

        # 使用容联云通讯发送短信验证码
        # CCP().send_template_sms(mobile, [sms_code, constants.YUNTONGXUN_EXPIRES], constants.YUNTONGXUN_TEMPLATE)
        # 通过异步任务发送短信验证码
        send_sms_code.delay(mobile, sms_code)

        # 返回数据
        return Response({'message': '0k'})
