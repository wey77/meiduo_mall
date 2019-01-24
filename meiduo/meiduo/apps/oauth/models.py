from django.db import models

from meiduo.utils.models import BaseModel
from users.models import User


class QQAuthUser(BaseModel):
    user = models.ForeignKey(User, verbose_name="openid关联的用户对象", on_delete=models.CASCADE)
    openid = models.CharField(verbose_name="用户的openid", db_index=True, max_length=64)

    class Meta:
        db_table = "db_qq_auth"
        verbose_name = "用户QQ数据"
        verbose_name_plural = verbose_name
