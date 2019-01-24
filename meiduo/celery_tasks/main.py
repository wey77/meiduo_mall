from celery import Celery


# 创建celery对象
celery_app = Celery('meiduo')  # 给定一个名称，无实际意义

# 加载celery配置
celery_app.config_from_object("celery_tasks.config")

# 注册celery异步任务
celery_app.autodiscover_tasks(["celery_tasks.sms"])  # 传入一个异步任务文件所在包，异步任务名字必须为stasks

