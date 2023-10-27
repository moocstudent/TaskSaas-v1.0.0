import os
from datetime import datetime

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt

from TaskSaasAPP import settings
from TaskSaasAPP.file_util import get_file_type
from web import models
from web.forms.wiki import WikiModelForm

from utils.encrypt import uid
from utils.tencent.cos import upload_file
from web.models import FileRepository


def wiki(request, project_id):
    """
    wiki文档视图
    :param request:
    :param project_id:
    :return:
    """
    wiki_id = request.GET.get('wiki_id')
    if not wiki_id or not wiki_id.isdecimal():
        return render(request, 'web/wiki.html')
    # 展示具体文章
    wiki_object = models.Wiki.objects.filter(id=wiki_id, project_id=project_id).first()
    coll = models.Collect.objects.filter(wiki=wiki_object, creator=request.web.user).first()

    return render(request, 'web/wiki.html', {'wiki_object': wiki_object,'is_collected':coll})


def wiki_add(request, project_id):
    """wiki添加"""
    if request.method == 'GET':
        form = WikiModelForm(request)
        return render(request, 'web/wiki_form.html', {'form': form})

    form = WikiModelForm(request, data=request.POST)
    if form.is_valid():
        # 判断用户是否选择父文章
        if form.instance.parent:
            form.instance.depth = form.instance.parent.depth + 1
        else:
            form.instance.depth = 1

        form.instance.project = request.web.project
        form.save()
        url = reverse('wiki', kwargs={'project_id': project_id})
        return redirect(url)

    return render(request, 'web/wiki_form.html', {'form': form})


def wiki_catalog(request, project_id):
    """获取wiki目录"""

    # 获取当前项目的
    data = models.Wiki.objects.filter(project=request.web.project).values("id", "title", "parent_id").order_by('depth',
                                                                                                               'id')

    return JsonResponse({'status': True, 'data': list(data)})


def wiki_delete(request, project_id, wiki_id):
    """删除文章"""
    models.Wiki.objects.filter(project_id=project_id, id=wiki_id).delete()

    url = reverse('wiki', kwargs={'project_id': project_id})
    return redirect(url)


def wiki_edit(request, project_id, wiki_id):
    """编辑文章"""
    wiki_object = models.Wiki.objects.filter(project_id=project_id, id=wiki_id).first()
    if not wiki_object:
        url = reverse('wiki', kwargs={'project_id': project_id})
        return redirect(url)

    if request.method == 'GET':
        form = WikiModelForm(request, instance=wiki_object)
        return render(request, 'web/wiki_form.html', {'form': form})

    form = WikiModelForm(request, data=request.POST,
                         instance=wiki_object)
    if form.is_valid():
        if form.instance.parent:
            form.instance.depth = form.instance.parent.depth + 1
        else:
            form.instance.depth = 1
        form.save()
        url = reverse('wiki', kwargs={'project_id': project_id})
        preview_id = "{0}?wiki_id={1}".format(url, wiki_id)
        return redirect(preview_id)

    return render(request, 'web/wiki_form.html', {'form': form})


@csrf_exempt
@xframe_options_exempt
def wiki_upload(request, project_id):
    """Markdown上传图片"""
    result = {
        'success': 0,
        'massage': None,
        'url': None,
    }

    upload_file = request.FILES.get('editormd-image-file')


    if not upload_file:
        result['massage'] = '文件不存在'
        return JsonResponse(result)
    if upload_file:
        fix = datetime.now().strftime('%Y%m%d%H%M%S%f') + '1'
        ab_upload_path = os.path.join(settings.STATICFILES_DIRS[0] + '/uploads', fix + upload_file.name)
        f = open(ab_upload_path, 'wb')
        for i in upload_file.chunks():
            f.write(i)
        f.close()

        file_url = 'http://'+request.get_host().split(':')[0]+":"+request.get_port()+"/static/uploads/" + fix + upload_file.name
        file_path = "/static/uploads/" + fix + upload_file.name
        file_repository = FileRepository(name=upload_file.name, file=ab_upload_path, file_path=file_path,
                                         file_url=file_url,
                                         ab_file_path=ab_upload_path,
                                         file_size=upload_file.size, file_type=3,
                                         file_mime_type=get_file_type(upload_file),
                                         update_user=request.web.user, project_id=project_id, parent_id='')
        file_repository.save()
        result['success'] = 1
        result['url'] = file_url

        print('>>>',result['url'] )

        return JsonResponse(result)



