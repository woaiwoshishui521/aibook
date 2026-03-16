"""
Django settings for aibook project.
自动根据环境加载对应的配置
"""
import os

ENV = os.environ.get('DJANGO_ENV', 'local')

if ENV == 'production':
    from .production import *
elif ENV == 'test':
    from .test import *
else:
    from .local import *

