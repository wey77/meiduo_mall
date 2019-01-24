from django.contrib.auth.backends import ModelBackend
import re

from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    """重写jwt返回值"""
    return {
        "token": token,
        "user_id": user.id,
        "username": user.username
    }


def get_user_by_account(account):
    """实现手机号和用户名多方式登录"""
    if re.match(r"^1[3-9]\d{9}$", account):
        try:
            user = User.objects.get(mobile=account)
        except User.DoseNotExist:
            return None
    else:
        try:
            user = User.objects.get(username=account)
        except User.DoseNotExist:
            return None
    return user


class UsernameMobileAuthBackend(ModelBackend):
    """重写django认证类中authenticate"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        # 用户数据返回
        user = get_user_by_account(username)
        if user and user.check_password(password):
            return user
        return None
