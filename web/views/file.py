from django.http import JsonResponse
from django.shortcuts import render

from web import models
from web.forms.file import FileFolderModelForm


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
