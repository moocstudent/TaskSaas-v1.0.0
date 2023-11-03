from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from web.models import UserInfo


class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # noinspection PyBroadException
        try:
            # 添加了一个手机验证，如果需要其他验证再加
            user = UserInfo.objects.get(Q(username=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None
