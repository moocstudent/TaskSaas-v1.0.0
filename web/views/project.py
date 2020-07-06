from django.http import JsonResponse
from django.shortcuts import render
from web.forms.project import ProjectModelForm


def project_list(request):
    """
    项目列表
    :param request:
    :return:
    """
    if request.method == 'GET':
        form = ProjectModelForm(request)
        return render(request, 'web/project_list.html', {'form': form})
    form = ProjectModelForm(request, data=request.POST)
    if form.is_valid():
        # 验证通过:项目名，颜色，描述+creater
        form.instance.creator = request.web.user
        form.save()
        return JsonResponse({'status': True, })
    return JsonResponse({'status': False, 'error': form.errors})
