from django.http import JsonResponse
from django.shortcuts import render

from web import models
from web.forms.file import FileFolderModelForm
from utils.tencent.cos import delete_file, delete_file_list


def file(request, project_id):
    """文件列表 & 添加文件夹"""

    parent_object = None
    folder_id = request.GET.get('folder', "")

    if folder_id.isdecimal():
        parent_object = models.FileRepository.objects.filter(file_type=2, project=request.web.project,
                                                             id=folder_id).first()
    # GET查看页面
    if request.method == "GET":

        breadcrumb_list = []
        parent = parent_object
        while parent:
            breadcrumb_list.insert(0, {'id': parent.id, 'name': parent.name})
            parent = parent.parent

        # 获取当前页面所有的文件以及文件夹
        queryset = models.FileRepository.objects.filter(project=request.web.project)

        if parent_object:
            file_object_list = queryset.filter(parent=parent_object).order_by('-file_type')
        else:
            file_object_list = queryset.filter(parent__isnull=True).order_by('-file_type')

        form = FileFolderModelForm(request, parent_object)
        context = {
            'form': form,
            'file_object_list': file_object_list,
            'breadcrimb_list': breadcrumb_list
        }
        return render(request, "web/file.html", context)

    # 添加文件夹 & 修改文件夹
    fid = request.POST.get('fid', '')
    edit_object = None
    if fid.isdecimal():
        # 修改
        edit_object = models.FileRepository.objects.filter(file_type=2, project=request.web.project, id=fid).first()

    if edit_object:
        form = FileFolderModelForm(request, parent_object, data=request.POST, instance=edit_object)
    else:
        form = FileFolderModelForm(request, parent_object, data=request.POST)

    if form.is_valid():
        form.instance.project = request.web.project
        form.instance.file_type = 2
        form.instance.update_user = request.web.user
        form.instance.parent = parent_object
        form.save()
        return JsonResponse({'status': True})

    return JsonResponse({'status': False, 'error': form.errors})


def file_delete(request, project_id):
    """删除文件"""
    fid = request.GET.get('fid', '')

    # 删除数据库中的文件/文件夹(级联删除)
    if fid.isdecimal():
        delete_object = models.FileRepository.objects.filter(id=fid, project=request.web.project).first()

    if delete_object.file_type == 1:
        # 删除文件(数据库文件删除，cos文件删除，项目空间容量设置)

        # 删除文件时，项目空间容量设置
        request.web.project.user_space -= delete_object.file_size
        request.web.project.save()

        # cos中删除文件
        delete_file(request.web.project.bucket, request.web.project.region, delete_object.key)
        delete_object.delete()

        return JsonResponse({'status': True})

    # 删除文件夹下所有文件(数据库文件删除，cos文件删除，项目空间容量设置)
    total_size = 0
    folder_list = [delete_object, ]
    key_list = []
    for folder in folder_list:
        child_list = models.FileRepository.objects.filter(project=request.web.project, parent=folder).order_by(
            '-file_type')
        for child in child_list:
            if child.file_type == 2:
                folder_list.append(child)
            else:
                # 文件大小计算
                total_size += child.file_size

                # 放入文件列表
                key_list.append({"Key": child.key})

    if key_list:
        # 批量删除
        delete_file_list(request.web.project.bucket, request.web.project.region, key_list)

    if total_size:
        # 删除文件时，项目空间容量设置
        request.web.project.user_space -= total_size
        request.web.project.save()

    # 删除数据库文件
    delete_object.delete()
    return JsonResponse({'status': True})
