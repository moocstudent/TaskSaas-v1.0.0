import time

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

from web import models
from web.forms.project import ProjectModelForm
from utils.tencent.cos import create_bucket


def project_list(request):
    """
    项目列表
    :param request:
    :return:
    """
    if request.method == 'GET':
        """
        project-list页面展示
        从数据库获取两部分数据
        创建的：是否星标
        参与的：是否星标
        """
        project_dict = {'star': [], 'my': [], 'join': []}

        my_project_list = models.Project.objects.filter(creator=request.web.user)
        if my_project_list:
            for my_item in my_project_list:
                if my_item.star:
                    project_dict['star'].append({'value': my_item, 'type': 'my'})
                else:
                    project_dict['my'].append(my_item)

            join_project_list = models.ProjectUser.objects.filter(user=request.web.user)
            for join_item in join_project_list:
                if join_item.star:
                    project_dict['star'].append({'value': join_item.project, 'type': 'join'})
                else:
                    project_dict['join'].append(join_item.project)
        else:
            print('project list is empty')
            join_project_list = models.ProjectUser.objects.filter(user=request.web.user)
            for join_item in join_project_list:
                if join_item.star:
                    project_dict['star'].append({'value': join_item.project, 'type': 'join'})
                else:
                    project_dict['join'].append(join_item.project)
        form = ProjectModelForm(request)
        return render(request, 'web/project_list.html', {'form': form, 'project_dict': project_dict})

    form = ProjectModelForm(request, data=request.POST)
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
        form.instance.creator = request.web.user
        instance = form.save()

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
