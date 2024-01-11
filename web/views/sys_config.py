from django.http import JsonResponse
from django.shortcuts import render


def sys_config_notify(request):
    return render(request, 'web/sys_config_notify.html')
def sys_config_template(request):
    return render(request, 'web/sys_config_template.html')

def sys_config_notify_switch(request):
    return JsonResponse({'status':1})