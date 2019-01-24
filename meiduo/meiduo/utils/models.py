from django.db import models


class BaseModel(models.Model):
    """模型类的基类"""
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    update_time = models.DateTimeField(verbose_name="更新时间", auto_now=True)

    class Meta:
        abstract = True  # 表明该模型类是抽象的,不会在迁移的时候在数据库中创建表
