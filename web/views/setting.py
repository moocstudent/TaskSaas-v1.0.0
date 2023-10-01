from django.shortcuts import render, redirect

from utils.tencent.cos import delete_bucket
from web import models


def setting(request, project_id):
    return render(request, 'web/setting.html')


def setting_delete(request, project_id):
    """删除项目"""
    if request.method == 'GET':
        return render(request, 'web/setting_delete.html')

    project_name = request.POST.get('project_name')
    password = request.POST.get('password')
    if not project_name or project_name != request.web.project.name:
        return render(request, 'web/setting_delete.html', {'error': "项目名称错误"})

    # 加密？
    if not password or password != request.user.password:
        return render(request, 'web/setting_delete.html', {'error': "密码错误"})

    # 删除项目(只有项目创建者才能删除）
    if request.web.user != request.web.project.creator:
        return render(request, 'web/setting_delete.html', {'error': "只有项目创建者才能删除项目"})

    # 删除桶里面所有文件
    # 删除桶
    delete_bucket(request.web.project.bucket,request.web.project.region)

    # 删除项目
    models.Project.objects.filter(id=request.web.project.id).delete()

    return redirect("project_list")
