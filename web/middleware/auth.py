import datetime

from django.http import FileResponse
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

from web import models


class Web(object):
    def __init__(self):
        self.user = None,
        self.price_policy = None
        self.project = None
        self.glory_wearing = None
        self.avatar_frame_wearing = None

class AuthMiddleWare(MiddlewareMixin):

    def process_request(self, request):
        """ 如果用户已登录，则request中赋值 """
        print('process_request ')
        request.web = Web()

        print('request.path_info ',request.path_info )
        if "/MP_verify" in request.path_info:
            file = open('/Users/tanghuijuan/PycharmProjects/TaskSaas/web/static/MP_verify_O7ZsD2KZoE5w9Usg.txt', 'rb')  # 打开文件
            response = FileResponse(file)  # 创建FileResponse对象
            return response
        user_id = request.session.get('user_id')
        user_object = models.UserInfo.objects.filter(id=user_id).first()
        request.web.user = user_object
        print('request session get user : ',request.web.user)

        # 白名单：没有登录都可以访问的URL
        """
        1. 获取当用户访问的URL
        2. 检查URL是否在白名单中，如果再则可以继续向后访问，如果不在则进行判断是否已登录
        """
        if request.path_info in settings.WHITE_REGEX_URL_LIST:
            return

        if request.path_info in settings.GREY_REGEX_URL_LIST:
            return

        # 检查用户是否已登录，已登录继续往后走；未登录则返回登录页面。
        if not request.web.user:
            return redirect('login')

        # 登录成功之后，访问后台管理时：获取当前用户所拥有的额度
        # 方式一：免费额度在交易记录中存储
        # 获取当前用户ID值最大（最近交易记录）
        _object = models.Transaction.objects.filter(user=user_object, status=2).order_by('-id').first()
        if _object:
            # 判断是否已过期
            current_datetime = datetime.datetime.now()
            if _object.end_datetime and _object.end_datetime < current_datetime:
                _object = models.Transaction.objects.filter(user=user_object, status=2, price_policy__category=1).first()

            request.web.price_policy = _object.price_policy

        # 方式二：免费额度存储到配置文件
        """
        _object = models.Transaction.objects.filter(user=user_object, status=2).order_by('-id').first()

        if not _object:
            # 没有购买
            request.price_policy = models.PricePolicy.objects.filter(category=1, title='个人免费版').first()
        else:
            # 付费版
            current_time = datetime.datetime.now()
            if _object.end_datetime and _object.end_datetime < current_time:
                # 过期
                request.price_policy = models.PricePolicy.objects.filter(category=1, title='个人免费版').first()
            else:
                request.price_policy = _object.price_policy
        """

    def process_view(self, request, view, args, kwargs):

        print('process_view' , request.path_info)

        # project_id 是我创建or我参与的

        project_id = request.GET.get('project_id')
        print('project_id at process_view ', project_id)
        if project_id:
            project_object = models.Project.objects.filter(id=project_id).first()
            if project_object:
                print('project_object at process_view ', project_object)
                # 是自己创建的项目，pass
                request.web.project = project_object
                return

        if request.path_info in settings.GREY_REGEX_URL_LIST:
            return
        # 判断URL是否以manage开头，如果是则判断项目ID是否是我的or我参与的
        if not request.path_info.startswith("/manage/"):
            return

        # project_id 是我创建or我参与的
        project_id = kwargs.get('project_id')
        # if not project_id:
        #     project_id = request.GET.get('project_id')



        # 是否自己创建
        project_object = models.Project.objects.filter(creator=request.web.user, id=project_id).first()
        if project_object:
            # 是自己创建的项目，pass
            request.web.project = project_object
            return

        # 是否自己参与
        project_user_object = models.ProjectUser.objects.filter(user=request.web.user, project_id=project_id).first()
        if project_user_object:
            # 是自己创建的项目，pass
            request.web.project = project_user_object.project
            return

        return redirect('project_list')
