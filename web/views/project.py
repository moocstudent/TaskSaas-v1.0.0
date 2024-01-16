import os

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

from TaskSaas.serializers.project_serializer import ProjectSerializer
from TaskSaasAPP import user_util
from web import models
from web.forms.project import ProjectModelForm
from web.models import UserInfo


def project_list(request):
    user = None
    if request.web.user:
        user = request.web.user

    """
    项目列表
    :param request:
    :return:
    """
    if request.method == 'GET':
        REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost----')
        print('REDIS_HOST>>>>>>>>', REDIS_HOST)
        if not user:
            user = UserInfo.objects.filter(id=request.GET.get('user_id')).first()
        """
        project-list页面展示
        从数据库获取两部分数据
        创建的：是否星标
        参与的：是否星标
        """
        project_dict = {'star': [], 'my': [], 'join': []}
        my_project_list = models.Project.objects.filter(creator=user)
        if my_project_list:
            for my_item in my_project_list:
                if my_item.star:
                    project_dict['star'].append({'value': my_item, 'type': 'my'})
                else:
                    project_dict['my'].append(my_item)

            join_project_list = models.ProjectUser.objects.filter(user=user)
            for join_item in join_project_list:
                if join_item.star:
                    project_dict['star'].append({'value': join_item.project, 'type': 'join'})
                else:
                    project_dict['join'].append(join_item.project)
        else:
            print('project list is empty')
            join_project_list = models.ProjectUser.objects.filter(user=user)
            for join_item in join_project_list:
                if join_item.star:
                    project_dict['star'].append({'value': join_item.project, 'type': 'join'})
                else:
                    project_dict['join'].append(join_item.project)
        form = ProjectModelForm(request,user=user)
        return render(request, 'web/project_list.html', {'form': form, 'project_dict': project_dict})

    if not user:
        user = UserInfo.objects.filter(id=request.POST.get('user_id')).first()

    form = ProjectModelForm(request, data=request.POST,user=user)
    if form.is_valid():
        name = form.cleaned_data['name']
        # 为项目创建一个桶&区域
        # bucket = "{}-{}-1302500499".format(request.web.user.mobile_phone, str(int(time.time())))
        # region = "ap-chengdu"
        # create_bucket(bucket, region)
        #
        # # 验证通过:项目名，颜色，描述+creater+COSbucketname+COSregion
        # form.instance.region = region
        # form.instance.bucket = bucket
        form.instance.creator = user
        instance = form.save()
        user_util.compute_forward_score(user=user, forward_score=2.00)
        # 创建项目时初始化问题类型
        issues_type_object = []
        for item in models.IssuesType.PROJECT_INIT_LIST:
            issues_type_object.append(models.IssuesType(project=instance, title=item))
        models.IssuesType.objects.bulk_create(issues_type_object)

        return JsonResponse({'status': True, })
    return JsonResponse({'status': False, 'error': form.errors})


def project_star(request, project_type, project_id):
    if project_type == 'my':
        models.Project.objects.filter(id=project_id, creator=request.web.user).update(star=True)
        return redirect('project_list')

    if project_type == 'join':
        models.ProjectUser.objects.filter(project_id=project_id, user=request.web.user).update(star=True)
        return redirect('project_list')

    return HttpResponse('请求错误')


def project_unstar(request, project_type, project_id):
    if project_type == 'my':
        models.Project.objects.filter(id=project_id, creator=request.web.user).update(star=False)
        return redirect('project_list')

    if project_type == 'join':
        models.ProjectUser.objects.filter(project_id=project_id, user=request.web.user).update(star=False)
        return redirect('project_list')

    return HttpResponse('请求错误')


def project_list_json(request):
    if request.method == 'GET':
        user_id = request.GET.get("user_id")
        """
        project-list页面展示
        从数据库获取两部分数据
        创建的：是否星标
        参与的：是否星标
        """
        project_dict = {'star': [], 'my': [], 'join': []}
        user = UserInfo.objects.filter(id=user_id).first()
        if not user:
            return JsonResponse({'status':0})
        my_project_list = models.Project.objects.filter(creator=user)

        if my_project_list:
            for my_item in (list(my_project_list)):
                if my_item.star:
                    project_dict['star'].append({'value': (ProjectSerializer(my_item).data), 'type': 'my'})
                else:
                    project_dict['my'].append(ProjectSerializer(my_item).data)

            join_project_list = models.ProjectUser.objects.filter(user=user)
            for join_item in (list(join_project_list)):
                if join_item.star:
                    project_dict['star'].append({'value': (ProjectSerializer(join_item.project).data), 'type': 'join'})
                else:
                    project_dict['join'].append(ProjectSerializer(join_item.project).data)
        else:
            print('project list is empty')
            join_project_list = models.ProjectUser.objects.filter(user=user)
            for join_item in (list(join_project_list)):
                if join_item.star:
                    project_dict['star'].append({'value': (ProjectSerializer(join_item.project).data), 'type': 'join'})
                else:
                    project_dict['join'].append(ProjectSerializer(join_item.project).data)
        return JsonResponse({'status': 1,'project_list':project_dict})
    return JsonResponse({'status':0})