from django.http import JsonResponse
from django.shortcuts import render

from web import models
from web.forms.issues import IssuesModelForm

from utils.pagination import Pagination


def issues(request, project_id):
    if request.method == 'GET':
        # 分页获取数据
        queryset = models.Issues.objects.filter(project_id=project_id)

        page_object = Pagination(
            current_page=request.GET.get('page'),
            all_count=queryset.count(),
            base_url=request.path_info,
            query_params=request.GET,
        )

        issues_object_list = queryset[page_object.start:page_object.end]

        form = IssuesModelForm(request)

        context = {
            'form': form,
            'issues_object_list': issues_object_list,
            'page_html': page_object.page_html()
        }
        return render(request, 'web/issues.html', context)

    form = IssuesModelForm(request, data=request.POST)
    if form.is_valid():
        form.instance.project = request.web.project
        form.instance.creator = request.web.user
        # 保存
        form.save()
        return JsonResponse({'status': True, })
    return JsonResponse({'status': False, 'error': form.errors})


def issues_detail(request, project_id, issues_id):
    """编辑问题"""

    issues_object = models.Issues.objects.filter(id=issues_id, project_id=project_id).first()

    form = IssuesModelForm(request, instance=issues_object)

    context = {
        'form': form,
    }
    return render(request, 'web/issues_detail.html', context)
