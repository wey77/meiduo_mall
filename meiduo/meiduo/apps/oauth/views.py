from rest_framework.views import APIView
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
import logging

from rest_framework_jwt.settings import api_settings

from .models import QQAuthUser

logger = logging.getLogger("django")


class QQAuthURLView(APIView):
    """qq登录视图"""

    def get(self, request):
        # 获取url位置参数：next
        next = request.query_params.get("next")
        if not next:
            next = '/'
        # 创建OAuthQQ对象
        auth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                       client_secret=settings.QQ_CLIENT_SECRET,
                       redirect_uri=settings.QQ_REDIRECT_URI,
                       state=next)
        # 获取登录url
        login_url = auth.get_qq_url()
        return Response({"login_url": login_url})


# url(r'^qq/user/$', views.QQAuthUserView.as_view()),
class QQAuthUserView(APIView):
    def get(self, request):
        # 获取到url中的位置参数：code
        code = request.query_params.get("code")
        if not code:
            return Response({"message": "code缺失"}, status=status.HTTP_400_BAD_REQUEST)
        # 创建OAuthQQ对象
        auth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                       client_secret=settings.QQ_CLIENT_SECRET,
                       redirect_uri=settings.QQ_REDIRECT_URI,
                       )
        try:
            # 获取到access_token
            access_token = auth.get_access_token(code)
            # 获取到openid
            openid = auth.get_open_id(access_token)
        except Exception as error:
            logger(error)
            return Response({"message": "qq服务器异常"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        # 根据openid验证用户是否存在
        try:
            auth_model = QQAuthUser.objects.get(openid=openid)
        except QQAuthUser.DoseNotExist:
            pass
        else:
            # 如果openid已绑定美多商城⽤用户，直接⽣生成JWT token，并返回
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            # 获取oauth_user关联的user
            user = auth_model.user
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            return Response({
                'token': token,
                'user_id': user.id,
                'username': user.username
            })
