from django.contrib.auth import base_user
from django.http import HttpResponse
from django.shortcuts import render, redirect

from utils import encrypt
from utils.tencent.cos import delete_bucket
from web import models


def setting(request,project_id):
    return render(request, 'web/setting.html')

def sys_setting(request):
    return HttpResponse('主题颜色 / 密码 / 布局偏好 (现在并没有功能实现)')

def setting_common_spider(request,project_id):
    status = request.POST.get('status')

def setting_common(request,project_id):
    return render(request,'web/setting_common.html')

def setting_delete(request, project_id):
    """删除项目"""
    if request.method == 'GET':
        return render(request, 'web/setting_delete.html')

    project_name = request.POST.get('project_name')
    password = request.POST.get('password')
    if not project_name or project_name != request.web.project.name:
        return render(request, 'web/setting_delete.html', {'error': "项目名称错误"})
    if password is None:
        return render(request, 'web/setting_delete.html', {'error': "密码错误"})
    else:
        print('md5 password:{} request.web.user.password:{}'.format(encrypt.md5(password),request.web.user.password))
        if not (encrypt.md5(password) == request.web.user.password):
            return render(request, 'web/setting_delete.html', {'error': "密码错误"})

    # 删除项目(只有项目创建者才能删除）
    if request.web.user != request.web.project.creator:
        return render(request, 'web/setting_delete.html', {'error': "只有项目创建者才能删除项目"})

    # 删除桶里面所有文件
    # 删除桶
    # try:
    #     delete_bucket(request.web.project.bucket,request.web.project.region)
    # except:
    #     print('delete bucket error ',project_id)
    #     pass
    if str(project_id) == str(request.web.project.id):
         # 删除项目
        models.Project.objects.filter(id=request.web.project.id).delete()
    else:
        return render(request, 'web/setting_delete.html', {'error': "项目错误"})

    return redirect("project_list")
