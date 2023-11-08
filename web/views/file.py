import json
import os.path
from datetime import datetime

from django.http import JsonResponse, FileResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from TaskSaasAPP import settings
from TaskSaasAPP.file_util import get_file_type
from utils.tencent.cos import credential
from web import models
from web.forms.file import FileFolderModelForm, FileModelForm
from web.models import FileRepository, UserInfo


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
        queryset = models.FileRepository.objects.filter(project=request.web.project,file_type__in=(1,2))

        if parent_object:
            file_object_list = queryset.filter(parent=parent_object).order_by('-file_type')
        else:
            file_object_list = queryset.filter(parent__isnull=True).order_by('-file_type')

        for fobj in file_object_list:
            coll = models.Collect.objects.filter(file=fobj, creator=request.web.user).first()
            if coll:
                fobj.is_collected = True
        form = FileFolderModelForm(request, parent_object)
        context = {
            'form': form,
            'file_object_list': file_object_list,
            'breadcrimb_list': breadcrumb_list,
            'folder_object': parent_object
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
            # request.web.project.user_space -= delete_object.file_size
            # request.web.project.save()

            # cos中删除文件
            # delete_file(request.web.project.bucket, request.web.project.region, delete_object.key)
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

    # if key_list:
        # 批量删除
        # delete_file_list(request.web.project.bucket, request.web.project.region, key_list)
        # for k in key_list:



    # if total_size:
    #     # 删除文件时，项目空间容量设置
    #     request.web.project.user_space -= total_size
    #     request.web.project.save()

    # 删除数据库文件
    delete_object.delete()
    return JsonResponse({'status': True})


@csrf_exempt
def cos_credential(request, project_id):
    """
    获取COS临时凭证
    :param request:
    :param project_id:
    :return:
    """
    per_file_limit = request.web.price_policy.per_file_size * 1024 * 1024
    total_file_limit = request.web.price_policy.project_space * 1024 * 1024 * 1024
    total_size = 0

    # 获取要上传的每个文件以及文件的大小
    file_list = json.loads(request.body.decode('utf-8'))
    for item in file_list:
        # 字节转换
        if item['size'] > per_file_limit:
            return JsonResponse({'status': False,
                                 'error': '单文件超出限制(最大{}M)，文件:{}'.format(request.web.price_policy.per_file_size,
                                                                        item['name'])})

        total_size += item['size']

    if total_size + request.web.project.user_space > total_file_limit:
        return JsonResponse({'status': False,
                             'error': '该项目已超出文件限制(最大{}M)!'.format(request.web.price_policy.project_space)})

    # 做容量限制
    data_dict = credential(request.web.project.bucket, request.web.project.region)
    return JsonResponse({'status': True, 'data': data_dict})



def uploadfile_common(request):
    upload_file = request.FILES['file']
    print('upload_file',upload_file)
    openid = request.POST.get('openid')
    user_id = request.POST.get('user_id')
    print('openid',openid)
    print('post body ',request.POST)
    if not user_id:
        # select user by openid ,if not exist then return false
        return JsonResponse({'status':False,'msg':'用户id未传送'})
    user = UserInfo.objects.filter(id=user_id).first()
    if not user:
        return JsonResponse({'status':False,'msg':'不存在的用户'})
    if upload_file:
        fix = datetime.now().strftime('%Y%m%d%H%M%S%f') + '1'
        ab_upload_path = os.path.join(settings.STATICFILES_DIRS[0]+'/uploads',fix+upload_file.name)
        f = open(ab_upload_path, 'wb')
        for i in upload_file.chunks():
            f.write(i)
        f.close()
        file_url = "http://localhost:3000/static/uploads/"+fix+upload_file.name
        file_path = "/static/uploads/"+fix+upload_file.name
        file_repository = FileRepository(name=upload_file.name, file=ab_upload_path,file_path=file_path,file_url=file_url,
                                         ab_file_path=ab_upload_path,
                                         file_size=upload_file.size,file_type=1,file_mime_type=get_file_type(upload_file),
                                         update_user=user)
        file_repository.save()
    # 项目的已使用空间更新
    # request.web.project.user_space += data_dict['file_size']
    # request.web.project.save()

        result = {
            'id': file_repository.id,
            'name': file_repository.name,
            'file_size': file_repository.file_size,
            'username': file_repository.update_user.username,
            'datetime': file_repository.update_datetime.strftime('%Y年%m月%d日 %H:%M'),
            'file_type': file_repository.get_file_type_display(),
            'download_url': reverse('file_download',
                                    kwargs={'file_id': file_repository.id})
        }
        return JsonResponse({'status': True, 'data': result})

# @csrf_exempt
def upload_file(request,project_id):
    upload_file = request.FILES['file']
    parent_id = request.POST.get('parent_id')
    print('upload_file',upload_file)
    print(request.POST)

    if upload_file:
        fix = datetime.now().strftime('%Y%m%d%H%M%S%f') + '1'
        ab_upload_path = os.path.join(settings.STATICFILES_DIRS[0]+'/uploads',fix+upload_file.name)
        f = open(ab_upload_path, 'wb')
        for i in upload_file.chunks():
            f.write(i)
        f.close()
        file_url = "http://localhost:3000/static/uploads/"+fix+upload_file.name
        file_path = "/static/uploads/"+fix+upload_file.name
        file_repository = FileRepository(name=upload_file.name, file=ab_upload_path,file_path=file_path,file_url=file_url,
                                         ab_file_path=ab_upload_path,
                                         file_size=upload_file.size,file_type=1,file_mime_type=get_file_type(upload_file),
                                         update_user=request.web.user,project_id=project_id,parent_id=parent_id)
        file_repository.save()

    # 项目的已使用空间更新
    # request.web.project.user_space += data_dict['file_size']
    # request.web.project.save()

        result = {
            'id': file_repository.id,
            'name': file_repository.name,
            'file_size': file_repository.file_size,
            'username': file_repository.update_user.username,
            'datetime': file_repository.update_datetime.strftime('%Y年%m月%d日 %H:%M'),
            'file_type': file_repository.get_file_type_display(),
            'download_url': reverse('file_download',
                                    kwargs={'project_id': request.web.project.id, 'file_id': file_repository.id})
        }

        return JsonResponse({'status': True, 'data': result})

    # return JsonResponse({'status': False, 'data': "文件错误"})


@csrf_exempt
def file_post(request, project_id):
    """
    上传成功的文件传到数据库
    :param request:
    :param project_id:

    name: fileName,
    key: key,
    file_size: fileSize,
    parent: CURRENT_FOLDER_ID,
    etag: data.ETag,
    file_path: data.Location
    """

    form = FileModelForm(request, data=request.POST)
    if form.is_valid():
        # 校验通过
        data_dict = form.cleaned_data
        data_dict.update({'project': request.web.project, 'file_type': 1, 'update_user': request.web.user})
        instance = models.FileRepository.objects.create(**data_dict)

        # 项目的已使用空间更新
        request.web.project.user_space += data_dict['file_size']
        request.web.project.save()

        result = {
            'id': instance.id,
            'name': instance.name,
            'file_size': instance.file_size,
            'username': instance.update_user.username,
            'datetime': instance.update_datetime.strftime('%Y年%m月%d日 %H:%M'),
            'file_type': instance.get_file_type_display(),
            'download_url': reverse('file_download',
                                    kwargs={'project_id': request.web.project.id, 'file_id': instance.id})
        }

        return JsonResponse({'status': True, 'data': result})

    return JsonResponse({'status': False, 'data': "文件错误"})


def file_download(request, project_id, file_id):
    """下载文件"""
    # 文件内容
    # 响应头
    # with open('xxx.jpg', mode='rb') as f:
    #     data = f.read()

    file_object = models.FileRepository.objects.filter(project_id=project_id, id=file_id).first()
    ab_file_path = file_object.ab_file_path
    file_name = file_object.name
    file_url = file_object.file_url
    content_type = file_object.file_mime_type

    if ab_file_path and content_type:
        file = open(ab_file_path, 'rb')  # 打开文件
        response = FileResponse(file)  # 创建FileResponse对象
        return response
        # with open(ab_file_path, 'rb') as fh:
        #     response = HttpResponse(fh.read(), content_type=content_type)
        #     response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_url)
        #     return response



