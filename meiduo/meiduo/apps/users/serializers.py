import re

from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from users.models import User


class CreateUserSerializer(serializers.ModelSerializer):
    """注册时的序列化器"""
    # 将原始模型类中没有的字段在此处定义
    password2 = serializers.CharField(label="二次密码", write_only=True)
    sms_code = serializers.CharField(label="短信验证码", write_only=True)
    allow = serializers.CharField(label="协议同意", write_only=True)
    token = serializers.CharField(label="状态保持", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "password", "password2", "sms_code", "mobile", "allow", "token"]
        extra_kwargs = {
            "username": {
                "min_length": 5,
                "max_length": 20,
                "error_messages": {
                    "min_length": "账号不能少于5位",
                    "max_length": "账号不能多于20位"
                }
            },
            "password": {
                "write_only": True,
                "min_length": 8,
                "max_length": 20,
                "error_messages": {
                    "min_length": "账号不能少于8位",
                    "max_length": "账号不能多于20位"
                }
            }
        }

    def validated_password(self, password):
        if not re.match(r"^1[3-9]\d{9}$", password):
            raise serializers.ValidationError("手机号格式错误")
        return password

    def validate_allow(self, allow):
        if allow != "true":
            raise serializers.ValidationError("请先同意协议")
        return allow

    def validate(self, attrs):
        # 验证密码是否符合格式
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError("两次密码不一致")
        # 判断短信验证码是否正确
        redis_conn = get_redis_connection("verify_code")
        real_sms_code = redis_conn.get("sms_%s" % attrs["mobile"])
        if real_sms_code is None:
            raise serializers.ValidationError("短信验证码失效")
        if real_sms_code.decode() != attrs["sms_code"]:
            return serializers.ValidationError("短信验证码错误")
        return attrs

    def create(self, validated_data):
        """创建用户"""
        # 去除不需要的数据
        del validated_data["password2"]
        del validated_data["sms_code"]
        del validated_data["allow"]
        user = User(**validated_data)
        # 使用django认证加密方法对密码进行加密
        user.set_password(validated_data["password"])
        user.save()

        # 生成jwt token
        # 获取payload处理函数
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        # 将对象编码处理
        payload = jwt_payload_handler(user)
        # 获取token处理函数
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        # 将payload处理并拼接成token
        token = jwt_encode_handler(payload)
        # 将token绑定到user对象中，让token通过序列化返出去
        user.token = token

        return user
