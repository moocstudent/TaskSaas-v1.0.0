# 开源多人任务管理平台改造升级 TASK SAAS

#### 介绍
此项目基于Python Django框架搭建的集‘概览’，‘问题’，‘统计’，‘文件’，‘文档’模块于一体的任务管理Saas平台,集成了腾讯云的SMS短信模块 & 对象存储模块，帮助解决项目管理者进行任务管理的问题。

#### 安装教程

##### 1.  虚拟环境配置

##### 2.  下载依赖第三方库

使用pip3安装： pip3 install -r requirements.txt

如果你没有pip，使用如下方式安装：

- OS X / Linux 电脑，终端下执行:


```
curl http://peak.telecommunity.com/dist/ez_setup.py | python
curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python
```

- Windows电脑：

下载 http://peak.telecommunity.com/dist/ez_setup.py 和 https://raw.github.com/pypa/pip/master/contrib/get-pip.py 这两个文件，双击运行。

##### 3.  settings配置
```
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

# 自己的短信模板相关配置
TENCENT_SMS_APP_ID = 00000000  # 应用ID
TENCENT_SMS_APP_KEY = "0000000000000"  # 应用Key
TENCENT_SMS_SIGN = "短信签名"  # 腾讯云创建签名时填写的签名内容（使用公众号的话这个值一般是公众号全称或简称）

TENCENT_SMS_TEMPLATES = {
    'register': 645735,
    'login': 645736,
}
# Django-redis配置
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://0.0.0.0:6379",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 1000,
                "encoding": "utf-8"
            },
            # "PASSWORD": '0'
        }
    }
}

# 登录白名单：无需登录就能访问的页面
WHITE_REGEX_URL_LIST = [
    '/register/',
    '/send/sms/',
    '/login/sms/',
    '/login/',
    '/image/code/',
    '/index/',
]

# COS文件存储相关ID/KEY
SECRET_ID = '替换为用户的 secretId'  # 替换为用户的 secretId
SECRET_KEY = '替换为用户的 secretKey'  # 替换为用户的 secretKey
REGION = 'ap-chengdu'

try:
    from .local_settings import *
except ImportError:
    pass
```

#### 模块说明
##### 项目文件夹
```
[
('form', '自定义表单'), 
('middleware', '中间件'), 
('static', '静态文件'), #js,css,plugin插件,image
('templatetags', '主要放置simple_tag'),
('view', '视图函数'),
]
```

##### view视图
```
[
('account', '用户信息'), 
('dashboard', '概览页面'),
('file', '文件上传页面'),  
('home', 'index主页'),
('issues', '问题页面'),
('project', '项目'),
('setting', '设置页面'),
('wiki', '文档页面'),
]
```


### 更新
todo https://www.django-rest-framework.org/




