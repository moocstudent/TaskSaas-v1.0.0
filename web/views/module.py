import json

from django.http import JsonResponse
from django.shortcuts import render
from django.template.defaulttags import csrf_token
from rest_framework.viewsets import ModelViewSet

from web import models
from web.models import Module

# todo
class ModuleView(ModelViewSet):
    queryset = Module.objects.all()
    ordering = ("-created_at", "id")
    def list(self, request, *args, **kwargs):
        module_list = models.Module.objects.filter(project_id=kwargs['project_id'])
        context = {
            'list': module_list
        }
        return render(request, 'web/setting_module.html', context)
    def destroy(self, request, *args, **kwargs):
        pass


def setting_module(request, project_id):
    if request.method == 'GET':
        module_list = models.Module.objects.filter(project_id=project_id)
        context = {
            'list': module_list
        }
        return render(request, 'web/setting_module.html', context)
    elif request.method == 'POST' and request.POST.get("title"):
        title = request.POST.get("title")
        module = Module(title=title, project_id=project_id)
        module.save()
        module_list = models.Module.objects.filter(project_id=project_id)
        context = {
            'list': module_list
        }
        return render(request, 'web/setting_module.html', context)
    elif request.method == 'POST' and request.POST.get("id"):
        models.Module.objects.filter(id=request.POST.get("id")).delete()
        module_list = models.Module.objects.filter(project_id=project_id)
        context = {
            'list': module_list
        }
        return render(request, 'web/setting_module.html', context)
    else:
        print('else')
        id = request.POST.get('id')
        print(id)
        module_list = models.Module.objects.filter(project_id=project_id)
        context = {
            'list': module_list
        }
        return render(request, 'web/setting_module.html', context)


#
# def module(request, project_id):
#     if request.method == 'GET':
#         module_list = models.Module.objects.filter(project_id=project_id)
#         module_list_json = json.dumps(list(module_list.values_list("id", "title")))
#         return HttpResponse({'status': 1, 'data': module_list_json})
#     elif request.method == 'POST' and request.POST.get("title"):
#         title = request.POST.get("title")
#         print(title)
#         module = Module(title=title, project_id=project_id)
#         module.save()
#         return HttpResponse({'status': 1})
#     elif request.method == 'POST' and request.POST.get("id"):
#         del_id = request.POST.get("id")
#         models.Module.objects.filter(id=del_id).delete()
#         return HttpResponse({'status': 1})
#     else:
#         return HttpResponse({'status': 0})
def setting_module_del(request,project_id):
    id = request.POST.get('id')
    print(id)
    models.Module.objects.filter(project_id=project_id,id=id).delete()
    return JsonResponse({'status':1})