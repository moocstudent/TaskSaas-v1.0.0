from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from web import models
from web.forms.wiki import WikiModelForm

from utils.encrypt import uid
from utils.tencent.cos import upload_file


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

    return render(request, 'web/wiki.html', {'wiki_object': wiki_object})


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
def wiki_upload(request, project_id):
    """Markdown上传图片"""
    result = {
        'success': 0,
        'massage': None,
        'url': None,
    }

    image_object = request.FILES.get('editormd-image-file')

    if not image_object:
        result['massage'] = '文件不存在'
        return JsonResponse(result)

    bucket = request.web.project.bucket
    region = request.web.project.region
    ext = image_object.name.rsplit('.')[-1]
    key = "{}.{}".format(uid(request.web.user.mobile_phone), ext)

    file_url = upload_file(bucket, region, image_object, key)

    result['success'] = 1
    result['url'] = file_url

    return JsonResponse(result)
