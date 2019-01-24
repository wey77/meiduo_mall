from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from . import serializers


class UserView(CreateAPIView):
    """注册用户视图"""
    serializer_class = serializers.CreateUserSerializer


class UsernameCountView(APIView):
    """验证用户名是否存在试图"""
    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        data = {
            "count": count,
            "username": username
        }
        return Response(data)


class MobileCountView(APIView):
    """判断用户手机号是否已存在"""
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        data = {
            "count": count,
            "mobile": mobile
        }
        return Response(data)



