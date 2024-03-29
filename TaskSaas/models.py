from django.db import models


# Create your models here.
class UserInfo(models.Model):
    id = models.BigAutoField(primary_key=True)
    username = models.CharField(verbose_name="用户名", max_length=32,unique=True)
    email = models.EmailField(verbose_name="邮箱", max_length=32,default='')
    # mobile_phone = models.CharField(verbose_name="手机号码", max_length=32)
    password = models.CharField(verbose_name="密码", max_length=32)

    REQUIRED_FIELDS=['password']
    USERNAME_FIELD='username'
    is_anonymous = False
    is_authenticated = True


